import re
import json
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from kivy.graphics import Color, Rectangle
from popup.popup_shape import PopupShape
from popup.popup_file import PopupFile
from popup.popup_face import PopupFace
from kivy.uix.popup import Popup
from data.face import Face
from core.draw import Draw
from kivy.utils import get_color_from_hex as clhex

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
        self._draw = Draw(1e-3)
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
            self.ids.area_top.bind(pos=self._update_canvas_area_top, size=self._update_canvas_area_top)
            self.ids.area_front.bind(pos=self._update_canvas_area_front, size=self._update_canvas_area_front)
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

    def _update_canvas_area_top(self, *args):
        self._profile_draw(
            _area_=self.ids.area_top,
            _area_padding_x_=50,
            _face_indexs_=[4, 2, 0],
            _tool_ox_micro_=[0, 300_000, 1660_000],
            _axis_dir_x_=[1, 1, -1],
            _colors_=[
                clhex("#ff5656ff"),
                clhex("#ffff56ff"),
                clhex("#61ff56ff"),
            ]
        )

    def _update_canvas_area_front(self, *args):
        self._profile_draw(
            _area_=self.ids.area_front,
            _area_padding_x_=50,
            _face_indexs_=[5, 3, 1],
            _tool_ox_micro_=[0, 300_000, 1660_000],
            _axis_dir_x_=[1, 1, -1],
            _colors_=[
                clhex("#56f1ffff"),
                clhex("#b956ffff"),
                clhex("#ff56cfff"),
            ]
        )

    def _profile_draw(self, _area_, _area_padding_x_, _face_indexs_, _tool_ox_micro_, _axis_dir_x_, _colors_):
        self._draw.pixel_per_micro = (_area_.size[0] - _area_padding_x_ * 2) / _tool_ox_micro_[-1]
        _area_.canvas.clear()
        with _area_.canvas:
            self._draw.axis(_area_, [_area_padding_x_, _area_.center_y])
            for i, index in enumerate(_face_indexs_):
                Color(rgba=_colors_[i])
                face = self._index__face[index]
                x, y = self._draw.pixel_to_micro(_area_.pos[0]+_area_padding_x_, _area_.center_y)
                x += _tool_ox_micro_[i]
                x += face.ox * _axis_dir_x_[i]
                self._draw.face(face, [x, y])

    def _face_select(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
        app.data.block_active(self._name__hash)
        face = self._index__face[face_index]
        for name in face.name__value(face_index):
            app.data.block(name).active = True
        if app.data.get('hmi.face_index') == face_index or app.launcher.offline:
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
        self._update_canvas_area_top()
        self._update_canvas_area_front()

    def _face_delete(self):
        for shape in self._face.shape:
            shape.id = 0
        self._face_apply()