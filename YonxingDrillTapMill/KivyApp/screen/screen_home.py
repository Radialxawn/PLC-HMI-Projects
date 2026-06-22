import json
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from popup.popup_file import PopupFile
from popup.popup_face import PopupFace
from data.face import Face
from core.draw import Draw
from core.ui import UI
from core.helper import Helper
from types import SimpleNamespace
from kivy.utils import get_color_from_hex as clhex

class ScreenHome(Screen):
    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        for i in range(6):
            button = self.ids[f'face_{i}']
            button.text = f'MẶT {i+1}'
            button.face_index = i
        self._draw = Draw(1e-3, [0.1e-3, 5e-3])
        self.ids.profile_name.input_filter = UI.filter_file_name
        self._face_index = -1
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__hash = {
                'hmi.face_index',
                'hmi.face_ready',
                'hmi.run',
                'hmi.stop',
                'hmi.face_run',
                'hmi.face_to_org',
                'hmi.view_can_run',
                'hmi.view_can_stop',
                'hmi.view_work_ing',
                'hmi.view_run_pump',
                'hmi.view_axis_tmp_micro[0]',
                'hmi.view_axis_tmp_micro[1]',
                'hmi.view_axis_tmp_micro[2]',
                'hmi.view_tool_offset_micro[0]',
                'hmi.view_tool_offset_micro[1]',
            }
            self._index__face, self._index__face_cog = self._generate()
            self.ids.area_top.bind(pos=self._update_canvas_area_top, size=self._update_canvas_area_top)
            self.ids.area_front.bind(pos=self._update_canvas_area_front, size=self._update_canvas_area_front)
    
    def _generate(self):
        index__face = {}
        index__face_cog = {}
        for i in range(6):
            index__face[i] = Face(i, _z_count_=3, _shape_count_=10)
            index__face_cog[i] = None
        return index__face, index__face_cog
    
    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__hash)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _value_update(self, _dt_):
        app = App.get_running_app()
        self.ids.stop.disabled = not app.data.get('hmi.view_can_stop')
        view_can_run = app.data.get('hmi.view_can_run')
        self.ids.run.disabled = not view_can_run
        face_index = app.data.get('hmi.face_index')
        if face_index != self._face_index:
            self._face_index = face_index
            for i in range(6):
                color = clhex("#6AA145") if face_index == i else clhex("#5F5F5F")
                self.ids[f'face_{i}'].background_color = color
    
    def _run(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.run', _value_)
    
    def _stop(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.stop', _value_)

    #################
    # LOAD AND SAVE #
    #################

    def _profile_load(self):
        popup = PopupFile(
            title='CHỌN TỆP CẤU HÌNH',
        ).set_data(
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
        directory = Helper.path_get('PROFILE')
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
        path = Path(Helper.path_get('PROFILE'), profile_name)
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
        chunk_array = []
        chunk_size = 15
        counter = 0
        for index in self._index__face:
            name__value = self._index__face[index].name__value()
            for name in name__value:
                block = app.data.block(name)
                block.active = True
                block.value = None
                if counter >= chunk_size:
                    counter = 0
                if counter == 0:
                    chunk_array.append({})
                chunk_array[-1][name] = name__value[name]
                counter += 1
        popup = PopupProgress().set_data(
            _cancel_=self._profile_download_cancel
        )
        popup.open()
        self._popup_progress = popup
        pdd = {
            'state': 0,
            'send_count': 0,
            'send_count_max': len(chunk_array) * 5,
            'index': 0,
            'chunk_array': chunk_array,
            'count': len(chunk_array),
            'match': [False] * len(chunk_array),
        }
        self._profile_download_data = SimpleNamespace(**pdd)
        self._profile_download_progress_clock = Clock.schedule_interval(self._profile_download_progress, 0.1)

    def _profile_download_cancel(self):
        self._profile_download_data.state = 11

    def _profile_download_progress(self, _dt_):
        app = App.get_running_app()
        ppc = self._popup_progress
        pdd = self._profile_download_data
        match pdd.state:
            case 0:
                app.data.block('hmi.face_ready').value = None
                app.data.set('hmi.face_ready', False)
                ppc.progress(10)
                pdd.state += 1
            case 1:
                if app.data.get('hmi.face_ready') == False:
                    ppc.progress(20)
                    pdd.state += 1
            case 2:
                if pdd.send_count >= pdd.send_count_max:
                    pdd.state = 11
                else:
                    si = -1
                    for i in range(pdd.count):
                        if pdd.match[i] == False:
                            si = i
                            break
                    if si == -1:
                        pdd.state = 11
                    else:
                        pdd.index = si
                        name__value = pdd.chunk_array[pdd.index]
                        app.data.sets(name__value)
                        pdd.send_count += 1
                        pdd.state += 1
            case 3:
                for i, chunk in enumerate(pdd.chunk_array):
                    pdd.match[i] = app.data.all(chunk)
                ppc.progress(100 * pdd.send_count / pdd.count)
                pdd.state = 2
            case 11:
                if all(pdd.match):
                    ppc.progress(30)
                    pdd.state = 21
                else:
                    ppc.progress(-1)
                    pdd.state = 100
            case 21:
                ppc.progress(40)
                app.data.set('hmi.face_ready', True)
                pdd.state += 1
            case 22:
                if app.data.get('hmi.face_ready') == True:
                    ppc.progress(101)
                    pdd.state = 100
            case 100:
                if hasattr(self, '_profile_download_progress_clock'):
                    Clock.unschedule(self._profile_download_progress_clock)
                    delattr(self, '_profile_download_progress_clock')
                app.data.block_active(self._name__hash)
    
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
                face = self._index__face[fi]
                x, y = self._draw.pixel_to_micro(_area_.pos[0] + _area_padding_x_ - _area_.parent.padding[0], _area_.center_y)
                x += machine_face['x']
                y += machine_face['y']
                x += face.ox
                y += face.oy
                self._draw.face(_face_=face, _position_=[x, y], _color_=_colors_[i])
        return
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
        name = 'hmi.face_index'
        app.data.set(name, face_index)
        if app.data.get(name) == face_index or app.launcher.offline:
            self._face_open(face_index)

    def _face_open(self, _index_):
        self._face = self._index__face[_index_]
        popup = PopupFace(
            title=f'MẶT {_index_+1}',
        ).set_data(
            _face_=self._face,
            _rule_=Face.index__rule[_index_],
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