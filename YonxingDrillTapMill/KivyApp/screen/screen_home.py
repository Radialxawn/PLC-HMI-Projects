import re
import json
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from popup.popup_file import PopupFile
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle

class ScreenHome(Screen):
    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        for i in range(6):
            button = self.ids[f'face_{i}']
            button.text = f'MẶT {i+1}'
            button.face_index = i
        for i in range(6):
            button = self.ids[f'cnc_{i}']
            button.text = f'CNC {i+1}'
            button.cnc_index = i
        self._first_load = True
        # test
        with self.canvas:
            Color(0.2, 0.6, 1, 1)
            self.rect = RoundedRectangle(pos=(5, 120), size=(200, 100), radius=[20])

    def on_touch_down(self, touch):
        print(self.ids.area.pos)
        self.rect.pos = (touch.x, touch.y)
        self.rect.size = (150, 75)
    
    def on_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._generate()

    def _generate(self):
        count__property = {
            1: [
                'ox',
                'oy',
                'oz',
                'tool_d',
                'depth',
                'feed',
            ],
            2: [
                'z',
                'zs',
            ],
            10: [
                's_id',
                's_x',
                's_y',
                's_va',
                's_vb',
                's_vc',
                's_vd',
                's_ve',
            ]
        }
        app = App.get_running_app()
        self._index__face = {}
        for i in range(6):
            face = {}
            for count in count__property:
                if count == 1:
                    for p in count__property[count]:
                        name = f'hmi.faces[{i}].{p}'
                        block = app.data.name__block[name]
                        face[name] = block.value
                else:
                    for p in count__property[count]:
                        for j in range(count):
                            name = f'hmi.faces[{i}].{p}[{j}]'
                            block = app.data.name__block[name]
                            face[name] = block.value
            self._index__face[i] = face

    def _file_name_filter(self, _substring_, _from_undo_):
        pattern = re.compile(r'[^a-zA-Z0-9_-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered

    def _profile_load(self, _path_):
        self.ids.profile_name.text = _path_.stem

    def _profile_load_select(self):
        popup = Popup(
            title='CHỌN TỆP CẤU HÌNH',
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.content = PopupFile(popup, _folder_='PROFILE', _filter_=['*.profile'], _select_=self._profile_load)
        popup.open()

    def _profile_save_confirm(self):
        app = App.get_running_app()
        for i in self._index__face:
            face = self._index__face[i]
            for name in face:
                block = app.data.name__block[name]
                if block.type == ua.VariantType.Boolean:
                    face[name] = block.value == 1
                else:
                    face[name] = block.value
        profile_name = self.ids.profile_name.text.strip()
        if profile_name == '':
            return
        path = Path(PopupFile.path_get('PROFILE'), profile_name)
        path_full = f'{str(path)}.profile'
        with open(path_full, 'w', encoding='utf-8') as file:
            json.dump(self._index__face, file, indent=3)

    def _profile_save(self):
        profile_name = self.ids.profile_name.text.strip()
        if profile_name == '':
            return
        directory = PopupFile.path_get('PROFILE')
        files = [f for f in directory.glob('*.profile')]
        message = 'LƯU TỆP MỚI?'
        for file in files:
            if profile_name == file.stem:
                message = f'ĐÃ TỒN TẠI [{profile_name}]\nTHAY THẾ?'
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_=message,
            _confirm_=self._profile_save_confirm)

    def _select_face(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
    
    def _download_cnc_select(self, _instance_):
        popup = Popup(
            title='CHỌN TỆP CNC',
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        self.cnc_index = _instance_.cnc_index
        popup.content = PopupFile(popup, _folder_='CNC', _filter_=['*.cnc'], _select_=self._download_cnc)
        popup.open()
    
    def _download_cnc(self, _source_path_):
        app = App.get_running_app()
        app.data.download_start(
            _source_path_=_source_path_,
            _destination_index_=self.cnc_index,
            _progress_=self._download_cnc_bar
        )

    def _download_cnc_bar(self, _value_):
        self.ids.cnc_bar.value = _value_
        if _value_ == 100:
            self.ids.cnc_state.opacity = 1.0
        else:
            self.ids.cnc_state.opacity = 0.0