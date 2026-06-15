import re
import json
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from popup.popup_shape import PopupShape
from popup.popup_file import PopupFile
from popup.popup_face import PopupFace
from kivy.uix.popup import Popup
from data.face import Face

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
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._generate()
            name__hash = {}
            name__hash['hmi.face_index'] = False
            name__hash['hmi.run'] = False
            name__hash['hmi.stop'] = False
            self._name__hash = name__hash
        app = App.get_running_app()
        app.data.block_active(self._name__hash)
    
    def _generate(self):
        self._index__face = {}
        for i in range(6):
            face = Face(_z_count_=3, _shape_count_=10)
            self._index__face[i] = face

    #################
    # LOAD AND SAVE #
    #################

    def _file_name_filter(self, _substring_, _from_undo_):
        pattern = re.compile(r'[^a-zA-Z0-9_-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered

    def _profile_load(self, _path_):
        index__face = {}
        with _path_.open(mode='r') as file:
            index__face = json.load(file)
        self._index__face = index__face
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
                block = app.data.block(name)
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
    
    def _download_cnc_select(self, _instance_):
        popup = Popup(
            title='CHỌN TỆP CNC',
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        self._download_cnc_index = _instance_.cnc_index
        popup.content = PopupFile(
            _instance_=popup,
            _folder_='CNC',
            _filter_=['*.cnc'],
            _select_=self._download_cnc
        )
        popup.open()
    
    def _download_cnc(self, _source_path_):
        app = App.get_running_app()
        popup = Popup(
            title='TẢI XUỐNG',
            size_hint=(0.6, 0.6),
            auto_dismiss=False
        )
        popup.content = PopupProgress(
            _instance_=popup,
            _cancel_=app.data.download_cancel
        )
        popup.open()
        self._download_cnc_popup = popup
        app.data.download_start(
            _source_path_=_source_path_,
            _destination_index_=self._download_cnc_index,
            _progress_=self._download_cnc_progress
        )
    
    def _download_cnc_progress(self, _value_):
        self._download_cnc_popup.content.progress(_value_)
    
    #############
    # FACE EDIT #
    #############

    def _profile_draw(self):
        print('draw profile')

    def _face_select(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
        app.data.block_active(self._name__hash)
        face = self._index__face[face_index]
        for name in face.name__value(face_index):
            app.data.block(name).active = True
        if app.data.get('hmi.face_index') == face_index or app.offline:
            self._face_open(face_index)

    def _face_open(self, _index_):
        popup = Popup(
            title=f'MẶT {_index_+1}',
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
        )
        self._face = self._index__face[_index_]
        for i, shape in enumerate(self._face.shape):
            shape.id = 3
            shape.x = (i * 20) * 1e3
            shape.va = (10 + i * 5) * 1e3
        popup.content = PopupFace(
            _instance_=popup,
            _face_=self._face,
            _apply_=self._face_apply,
            _delete_=self._face_delete
            )
        popup.open()
    
    def _face_apply(self):
        print('face apply:', self._face)
        self._profile_draw()

    def _face_delete(self):
        print('face delete')