import re
import json
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from kivy.core.image import Image as CoreImage
from popup.popup_file import PopupFile
from popup.popup_face import PopupFace
from kivy.graphics import Rectangle
from kivy.uix.popup import Popup
from data.face import Face
from core.draw import Draw
from core.ui import UI
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
        self._draw = Draw(1e-3, [0.1e-3, 5e-3])
        self.ids.profile_name.input_filter = UI.filter_file_name
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._generate()
            self._name__hash = {
                'hmi.face_index',
                'hmi.run',
                'hmi.stop',
                'hmi.view_can_run',
                'hmi.view_can_stop',
                'hmi.view_work_ing',
            }
            self.ids.area_top.bind(pos=self._update_canvas_area_top, size=self._update_canvas_area_top)
            self.ids.area_front.bind(pos=self._update_canvas_area_front, size=self._update_canvas_area_front)
        app = App.get_running_app()
        app.data.block_active(self._name__hash)
    
    def _generate(self):
        self._index__face = {}
        self._index__face_cog = {}
        for i in range(6):
            self._index__face[i] = Face(i, _z_count_=3, _shape_count_=10)
            self._index__face_cog[i] = None
    
    def on_enter(self, *args):
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _value_update(self, _dt_):
        app = App.get_running_app()
        print('_value_update')

    #################
    # LOAD AND SAVE #
    #################

    def _profile_load(self):
        popup = Popup(
            title='CHỌN TỆP CẤU HÌNH',
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.content = PopupFile(
            _instance_=popup,
            _folder_='PROFILE',
            _filter_=['*.profile'],
            _select_=self._profile_load_start,
            _deletable_=True
        )
        popup.open()

    def _profile_load_start(self, _path_):
        save_data = {}
        with _path_.open(mode='r') as file:
            save_data = json.load(file)
        try:
            for index in self._index__face:
                face = self._index__face[index]
                face.from_json(save_data[str(index)])
        except:
            app = App.get_running_app()
            app.m_show_popup_error(
                _message_='TỆP BỊ LỖI',
                _acknowledge_=None)
            return
        self.ids.profile_name.text = _path_.stem
        self._face_apply()
    
    def _profile_save(self):
        profile_name = self.ids.profile_name.text.strip()
        if profile_name == '':
            return
        directory = PopupFile.path_get('PROFILE')
        files = [f for f in directory.glob('*.profile')]
        message = 'LƯU TỆP MỚI?'
        for file in files:
            if profile_name == file.stem:
                message = f'ĐÃ TỒN TẠI [{profile_name}]\nGHI ĐÈ?'
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_=message,
            _confirm_=self._profile_save_start
        )

    def _profile_save_start(self):
        profile_name = self.ids.profile_name.text.strip()
        if profile_name == '':
            return
        path = Path(PopupFile.path_get('PROFILE'), profile_name)
        save_data = {}
        for index in self._index__face:
            face = self._index__face[index]
            face.limit()
            save_data[index] = face.to_json()
        path_full = f'{str(path)}.profile'
        with open(path_full, 'w', encoding='utf-8') as file:
            json.dump(save_data, file, indent=3)
    
    def _profile_download(self):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_=f'TẢI CẤU HÌNH XUỐNG PLC?',
            _confirm_=self._profile_download_start
        )
    
    def _profile_download_start(self):
        if hasattr(self, '_profile_download_clock'):
            return
        app = App.get_running_app()
        popup = Popup(
            title='TẢI XUỐNG',
            size_hint=(0.6, 0.6),
            auto_dismiss=False
        )
        popup.content = PopupProgress(
            _instance_=popup,
            _cancel_=lambda : print('Profile download cancel')
        )
        popup.open()
        self._popup_progress = popup
        self._profile_download_face_index = 0
        self._profile_download_progress_clock = Clock.schedule_interval(self._profile_download_progress, 0.1)

    def _profile_download_progress(self, _dt_):
        app = App.get_running_app()
        index, count = self._profile_download_face_index, len(self._index__face)
        face = self._index__face[index]
        name__value = face.name__value()
        app.data.sets(list(name__value.keys()), list(name__value.values()))
        self._popup_progress.content.progress(100 * index / count)
        self._profile_download_face_index = (index + 1) % count
        if self._profile_download_face_index == 0:
            if hasattr(self, '_profile_download_progress_clock'):
                Clock.unschedule(self._profile_download_progress_clock)
                delattr(self, '_profile_download_progress_clock')
            self._popup_progress.content.progress(101)

    def _cnc_download(self, _instance_):
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
            _select_=lambda p: self._cnc_download_confirm(p, _instance_.cnc_index),
            _deletable_=False
        )
        popup.open()
    
    def _cnc_download_confirm(self, _source_path_, _cnc_index_):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_=f'TẢI TỆP [{_source_path_.stem}] XUỐNG PLC [CNC {_cnc_index_+1}]?',
            _confirm_=lambda : self._cnc_download_start(_source_path_)
        )
    
    def _cnc_download_start(self, _source_path_):
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
        self._popup_progress = popup
        app.data.download_start(
            _source_path_=_source_path_,
            _destination_index_=self._download_cnc_index,
            _progress_=self._cnc_download_progress
        )
    
    def _cnc_download_progress(self, _value_):
        self._popup_progress.content.progress(_value_)
    
    #############
    # FACE EDIT #
    #############

    def _update_canvas_area_top(self, *args):
        self._profile_draw(
            _area_=self.ids.area_top,
            _area_padding_x_=50,
            _face_indexs_=[4, 2, 0],
            _colors_=[
                clhex("#8a2d2dff"),
                clhex("#909033ff"),
                clhex("#36942fff"),
            ]
        )

    def _update_canvas_area_front(self, *args):
        self._profile_draw(
            _area_=self.ids.area_front,
            _area_padding_x_=50,
            _face_indexs_=[5, 3, 1],
            _colors_=[
                clhex("#33858dff"),
                clhex("#6a3094ff"),
                clhex("#8c2e71ff"),
            ]
        )

    def _profile_draw(self, _area_, _area_padding_x_, _face_indexs_, _colors_):
        app = App.get_running_app()
        active_width_pixel = _area_.size[0] - _area_padding_x_ * 2
        x_max_micro = 0
        for fi in _face_indexs_:
            face = self._index__face[fi]
            machine_face = app.machine['index__face'][str(fi)]
            x_max_micro = max(x_max_micro, machine_face['x'])
        self._draw.pixel_per_micro = active_width_pixel / x_max_micro
        _area_.canvas.clear()
        with _area_.canvas:
            self._draw.axis(_area_, [_area_padding_x_, _area_.center_y], active_width_pixel, 2)
            for i, fi in enumerate(_face_indexs_):
                machine_face = app.machine['index__face'][str(fi)]
                Color(rgba=_colors_[i])
                face = self._index__face[fi]
                x, y = self._draw.pixel_to_micro(_area_.pos[0]+_area_padding_x_, _area_.center_y)
                x += machine_face['x']
                y += machine_face['y']
                x += face.ox * machine_face['dir_x']
                y += face.oy * machine_face['dir_y']
                self._draw.face(face, [x, y])
        if self._index__face_cog[_face_indexs_[0]] == None:
            cog_texture = CoreImage('texture/cog.png').texture
            with _area_.canvas.after:
                for fi in _face_indexs_:
                    Color(1, 1, 1, 1)
                    cog = Rectangle(texture=cog_texture, pos=(_area_.center_x - 8, _area_.center_y - 8), size=(16, 16))
                    self._index__face_cog[fi] = cog

    def _face_select(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
        app.data.block_active(self._name__hash)
        face = self._index__face[face_index]
        for name in face.name__value():
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