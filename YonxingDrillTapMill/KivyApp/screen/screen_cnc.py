import numpy as np
from kivy.app import App
from core.draw import Draw
from kivy.clock import Clock
from core.ui import UITextInputInteger
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from popup.popup_file import PopupFile
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from core.data import Data
from core.mouse import Mouse
from core.helper import Helper
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle
from kivy.utils import get_color_from_hex as clhex

class ScreenCNC(Screen):
    def __init__(self, **kvargs):
        super(ScreenCNC, self).__init__(**kvargs)
        self._draw = Draw(2e-3, [1e-3, 10e-3])
        self._mouse = Mouse()
        self._first_load = True
        self._cnc_id_selector_active = False
        self._cnc_id = None
        self._work_state = None
        self._line_points = []
        self._cog = None
        self._depth = None
        self.ids.cnc_error.opacity = 0
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__hash = {
                'hmi.cnc_id',
                'hmi.cnc_run',
                'hmi.cnc_feed',
                'hmi.view_cnc_error',
                'hmi.view_cnc_micro[0]',
                'hmi.view_cnc_micro[1]',
                'hmi.view_cnc_micro[2]',
                'hmi.view_state[1]',
                'hmi.view_can_run',
            }
            self._name__index, self._name__input, self._name__value = self._generate()
    
    def _generate(self):
        app = App.get_running_app()
        cnc_id_selector = self.ids.cnc_id_selector
        name__index = {}
        values = []
        for i in range(app.machine.shape_custom_count):
            button = self.ids[f'cnc_{i}']
            button.text = f'CNC {i+1}'
            button.cnc_index = i
            values.append(button.text)
            name__index[button.text] = i
        cnc_id_selector.values = values
        cnc_id_selector.text = values[0]
        #
        name__input, name__value = {}, {}
        name__data = {
            'hmi.cnc_feed': {'label': 'TỐC ĐỘ (mm/min)', 'factor': 1},
        }
        self.ids.left.width = 180
        self.ids.cnc_preview.height = 180
        for name in name__data:
            data = name__data[name]
            label = Label(
                text=data['label'],
                size_hint_x=None,
                size_hint_y=None,
                halign='left',
                valign='center',
                height=40,
                width=self.ids.left.width
            )
            label.bind(size=label.setter('text_size'))
            input = UITextInputInteger(
                size_hint_y=None,
                height=40,
                halign='center',
                multiline=False
            ).data_set(
                _key_=name,
                _factor_=data['factor'],
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            name__input[input.v_key] = input
            name__value[input.v_key] = None
            self.ids.cnc_property.add_widget(label)
            self.ids.cnc_property.add_widget(input)
        self.ids.cnc_property.add_widget(Widget())
        return name__index, name__input, name__value

    def on_enter(self, *args):
        self._cnc_id_selector_active = True
        app = App.get_running_app()
        app.data.block_active(self._name__hash)
        self._cnc_id = None
        self._work_state = None
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.05)

    def on_leave(self, *args):
        self._cnc_id_selector_active = False
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _on_text_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)

    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._name__input:
            input = self._name__input[name]
            if input.focus:
                continue
            block = app.data.block(name)
            value = self._name__value[name]
            if value == block.value:
                continue
            self._name__value[name] = block.value
            input.v_value_set(block.value)
        work_state = app.data.get('hmi.view_state[1]')
        if work_state != None and self._work_state != work_state:
            self._work_state = work_state
            self.ids.cnc_run.background_color = clhex("#6AA145") if work_state > 500 else clhex("#5F5F5F")
            self.ids.cnc_run.disabled = work_state < 100
            for i in range(app.machine.shape_custom_count):
                self.ids[f'cnc_{i}'].disabled = work_state > 100
        cnc_id = app.data.get('hmi.cnc_id')
        if cnc_id != self._cnc_id:
            self._cnc_id = cnc_id
            for i in range(app.machine.shape_custom_count):
                color = clhex("#6AA145") if cnc_id == i else clhex("#5F5F5F")
                self.ids[f'cnc_{i}'].background_color = color
            self._redraw_preview()
        self.ids.cnc_error.opacity = 1 if app.data.get('hmi.view_cnc_error') else 0
        self._line_update()
    
    def _update_canvas(self, *args):
        self._redraw_path(True)
        self._redraw_preview()
    
    def _redraw_preview(self):
        image, _ = Helper.cnc_preview_image_get(_index_=self._cnc_id, _image_=True)
        prv = self.ids.cnc_preview
        prv.canvas.clear()
        with prv.canvas:
            if image != None:
                Rectangle(texture=image.texture, pos=prv.pos, size=prv.size)

    def _redraw_path(self, _canvas_):
        area = self.ids.area
        area.canvas.clear()
        if _canvas_:
            self._draw.offset_pixel = [area.center_x, area.center_y]
        with area.canvas:
            self._draw.axis(area, [0, 0], None, 2)
            Color(rgba=clhex("#41bc41"))
            self._line = Line(points=self._line_points_to_pixel(), width=2)
            Color(rgba=clhex("#4145bc"))
            self._draw_depth(area)
            Color(rgba=clhex("#ffffff"))
            xp, yp = self._draw.micro_to_pixel_offset(0, 0)
            cog_texture = CoreImage('texture/cog.png').texture
            self._cog = Rectangle(texture=cog_texture, pos=[xp-8, yp-8], size=(16, 16))
    
    def _draw_depth(self, _area_):
        cx, cy = _area_.center_x, _area_.center_y
        sx, sy = _area_.pos[0] + 5, _area_.pos[1] + 5
        self._depth = Rectangle(pos=[sx, cy-1], size=[30, 2])
        self._depth_z = 0
        #
        l = _area_.height - 10
        lh = l * 0.5
        lh_micro, = self._draw.pixel_to_micro(lh)
        Rectangle(pos=[sx+35, sy], size=[2, l])
        #
        draw_sub = self._draw.pixel_per_micro > 3e-3
        for i, y in enumerate(np.arange(0, -lh_micro, -10_000)):
            xp, yp = self._draw.micro_to_pixel(5_000, y)
            sxi = sx + 35
            yp += cy - 1
            Rectangle(pos=[sxi, yp], size=[xp, 2])
            if draw_sub:
                for j in range(1_000, 10_000, 1_000):
                    Rectangle(pos=[sxi, yp-j*self._draw.pixel_per_micro+0.5], size=[xp*0.5, 1])
            label = CoreLabel(text=f'{i*10:03}', font_size=12)
            label.refresh()
            texture = label.texture
            Rectangle(texture=texture, pos=(sxi+xp+5, yp-texture.size[1]*0.5), size=texture.size)

    def on_touch_down(self, touch):
        _, _, inside = self._draw.touch_pos_to_center_of_widget(self.ids.area, touch.pos)
        if inside:
            changed = False
            match touch.button:
                case 'scrollup':
                    self._draw.pixel_per_micro *= 0.9
                    changed = True
                case 'scrolldown':
                    self._draw.pixel_per_micro *= 1.1
                    changed = True
                case 'right':
                    self._mouse.drag = True
                    self._mouse.drag_begin[0] = touch.pos[0]
                    self._mouse.drag_begin[1] = touch.pos[1]
                    self._mouse.drag_offset = self._draw.offset_pixel
            if changed:
                self._redraw_path(False)
        else:
            return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._mouse.drag == True:
            match touch.button:
                case 'right':
                    dxp = touch.pos[0] - self._mouse.drag_begin[0] + self._mouse.drag_offset[0]
                    dyp = touch.pos[1] - self._mouse.drag_begin[1] + self._mouse.drag_offset[1]
                    self._draw.offset_pixel = [dxp, dyp]
                    self._redraw_path(False)
            return True
        return super().on_touch_down(touch)

    def _line_update(self):
        app = App.get_running_app()
        x = app.data.get('hmi.view_cnc_micro[0]')
        y = app.data.get('hmi.view_cnc_micro[1]')
        count = len(self._line_points)
        add = False
        if count == 0:
            add = True
            x, y = 0, 0
        else:
            lx, ly = self._line_points[-1]
            add = x != None and y != None and (x != lx or y != ly)
        if add:
            self._line_points.append([x, y])
        if count > 1500:
            self._line_points.pop(0)
        if add and self._cog != None:
            xp, yp = self._draw.micro_to_pixel_offset(x, y)
            s = self._cog.size
            self._cog.pos = [xp - s[0]*0.5, yp - s[1]*0.5]
            self._line.points = self._line_points_to_pixel()
        z = app.data.get('hmi.view_cnc_micro[2]')
        if z != None and self._depth != None and self._depth_z != z:
            zp, = self._draw.micro_to_pixel(z)
            s, p = list(self._depth.size), list(self._depth.pos)
            s[1] = abs(zp) + 2
            self._depth.size = s
            p[1] = self.ids.area.center_y + zp - 1
            self._depth.pos = p
            self._depth_z = z

    def _clear(self):
        self._line_points = []
        self._line.points = self._line_points
    
    def _line_points_to_pixel(self):
        points = []
        poff = self._draw.offset_pixel
        for point in self._line_points:
            xp, yp = self._draw.micro_to_pixel(point[0], point[1])
            points.append([xp + poff[0], yp + poff[1]])
        return points
    
    def _on_cnc_id_selector(self, _instance_):
        if not self._cnc_id_selector_active:
            return
        app = App.get_running_app()
        app.data.set('hmi.cnc_id', self._name__index[_instance_.text])

    def _cnc_download(self, _instance_):
        popup = PopupFile(
            title='CHỌN TỆP CNC',
        ).set_data(
            _folder_='CNC',
            _filter_=['*.cnc'],
            _select_=lambda p: self._cnc_download_confirm(p, _instance_.cnc_index),
            _deletable_=False
        )
        popup.open()
    
    def _cnc_download_confirm(self, _source_path_, _cnc_index_):
        app = App.get_running_app()
        try:
            self._download_cnc_gcode = Helper.gcode_read(_source_path_)
        except Exception as error:
            app.helper.show_popup_error(
                _message_=str(error),
                _acknowledge_=None)
            return
        self._download_cnc_index = _cnc_index_
        self._download_cnc_chunks = self._download_cnc_gcode.chunks(Data.DOWNLOAD_CHUNK_SIZE)
        app.helper.show_popup_confirm(
            _message_=f'TẢI TỆP [{_source_path_.stem}] XUỐNG PLC [CNC {_cnc_index_+1}]?',
            _confirm_=self._cnc_download_start
        )
    
    def _cnc_download_start(self):
        app = App.get_running_app()
        Helper.cnc_preview_image_remove(self._download_cnc_index)
        popup = PopupProgress().set_data(
            _cancel_=app.data.download_cancel
        )
        popup.open()
        self._popup_progress = popup
        app.data.download_start(
            _index_=self._download_cnc_index,
            _chunks_=self._download_cnc_chunks,
            _progress_=self._cnc_download_progress
        )
    
    def _cnc_download_progress(self, _value_):
        self._popup_progress.progress(_value_)
        match _value_:
            case 101:
                Helper.cnc_preview_image_generate(
                    _gcode_=self._download_cnc_gcode,
                    _index_=self._download_cnc_index,
                )
                self._redraw_preview()
    
    def _cnc_run(self, _value_):
        self._line_points = []
        app = App.get_running_app()
        app.data.set('hmi.cnc_run', _value_)