import re
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from popup.popup_shape import PopupShape
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from core.mouse import Mouse
from core.draw import Draw
from kivy.utils import get_color_from_hex as clhex

class PopupFace(Screen):
    def __init__(self, _instance_, _face_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._face_ = _face_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(1e-3, [0.5e-3, 5e-3])
        self._mouse = Mouse()
        self._generate()
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        fp__name = {
            'ox':     'x',
            'oy':     'y',
            'oz':     'z',
            'tool_d': 'đk dao',
            'depth':  'độ sâu',
            'feed':   'tốc độ',
        }
        self.ids.face_property.add_widget(Widget())
        self.ids.face_property.width = 320
        for fp in fp__name:
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            olabel = Label(
                text=fp__name[fp].upper(),
                size_hint_x=None,
                width=90
            )
            obox.add_widget(olabel)
            self._generate_input(fp, self._face_[fp], obox)
            self.ids.face_property.add_widget(obox)
        self.ids.face_property.add_widget(Widget())
        for i in range(len(self._face_.z)):
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                spacing=5,
                height=40,
            )
            olabel = Label(
                text=f'Z{i+1}',
                size_hint_x=None,
                width=30
            )
            obox.add_widget(olabel)
            self._generate_input(f'z[{i}]', self._face_.z[i], obox)
            self._generate_input(f'zs[{i}]', self._face_.zs[i], obox)
            self.ids.face_property.add_widget(obox)
        self.ids.face_property.add_widget(Widget())

    def _generate_input(self, _fp_, _value_, _parent_):
        ip = TextInput(
            halign='center',
            input_filter=self._on_text_input_filter,
            multiline=False
        )
        ip.fp = _fp_
        ip.text = f'{(_value_*1e-3):.3f}'
        ip.bind(on_text_validate=self._on_text_input_validate)
        ip.bind(focus=self._on_text_input_focus)
        _parent_.add_widget(ip)
        return ip
    
    def _on_text_input_filter(self, _substring_, _from_undo_):
        pattern = re.compile(r'[^0-9.]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered

    def _on_text_input_validate(self, _instance_):
        value = 0
        try:
            value = int(float(_instance_.text)*1e3)
        except (ValueError, TypeError):
            _instance_.text = ''
        changed = False
        array = _instance_.fp.split('[')
        if len(array) > 1:
            self._face_[array[0]][int(array[1][:-1])] = value
            changed = True
        elif value != self._face_[_instance_.fp]:
            self._face_[_instance_.fp] = value
            changed = True
        if changed:
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)

    def _update_canvas(self, *args):
        self._face_update()

    def _apply(self):
        self._apply_()
        self._instance_.dismiss()
    
    def _delete(self):
        self._delete_()
        self._instance_.dismiss()

    def _cancel(self):
        self._instance_.dismiss()
    
    ##############
    # SHAPE EDIT #
    ##############

    def on_touch_down(self, touch):
        self._mouse.down_time_sec = Clock.get_time()
        dxp, dyp, inside = self._draw.touch_pos_to_center_of_widget(self, self.ids.area, touch.pos)
        if inside:
            changed = False
            match touch.button:
                case 'scrollup':
                    self._draw.pixel_per_micro *= 0.9
                    changed = True
                case 'scrolldown':
                    self._draw.pixel_per_micro *= 1.1
                    changed = True
                case 'left':
                    dx, dy = self._draw.pixel_to_micro(dxp, dyp)
                    shape = self._shape_select(dx, dy)
                    if shape != None:
                        self._mouse.selected_object = shape
                        self._mouse.selected_object_pos = [dx, dy]
                        self._mouse.drag = True
                        self._mouse.drag_begin[0] = touch.pos[0]
                        self._mouse.drag_begin[1] = touch.pos[1]
                        self._mouse.drag_offset = [shape.x, shape.y]
                case 'right':
                    self._mouse.drag = True
                    self._mouse.drag_begin[0] = touch.pos[0]
                    self._mouse.drag_begin[1] = touch.pos[1]
                    self._mouse.drag_offset = self._draw.offset_pixel
            if changed:
                self._face_update()
        else:
            return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self._mouse.drag == True:
            match touch.button:
                case 'left':
                    shape = self._mouse.selected_object
                    if shape != None and shape.id > 0:
                        dxp = touch.pos[0] - self._mouse.drag_begin[0]
                        dyp = touch.pos[1] - self._mouse.drag_begin[1]
                        dx, dy = self._draw.pixel_to_micro(dxp, dyp)
                        offset = self._mouse.drag_offset
                        shape.x = max(0, offset[0] + dx)
                        shape.y = offset[1] + dy
                        self._face_update()
                case 'right':
                    dxp = touch.pos[0] - self._mouse.drag_begin[0] + self._mouse.drag_offset[0]
                    dyp = touch.pos[1] - self._mouse.drag_begin[1] + self._mouse.drag_offset[1]
                    self._draw.offset_pixel = [dxp, dyp]
                    self._face_update()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        match touch.button:
            case 'left':
                shape = self._mouse.selected_object
                if Clock.get_time() - self._mouse.down_time_sec < 0.2:
                    if shape != None:
                        if shape.id == 0:
                            pos = self._mouse.selected_object_pos
                            shape.x = max(0, pos[0])
                            shape.y = pos[1]
                        self._shape_open(shape)
        self._mouse.drag = False
        self._mouse.selected_object = None
        return super().on_touch_up(touch)

    def _face_update(self):
        area = self.ids.area
        area.canvas.clear()
        self._face_.shape.sort(key=lambda s: (s.id == 0, s.x)) # sort using x value and push id = 0 object to the back
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y])
            cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
            for i, shape in enumerate(self._face_.shape):
                px, py = cx + shape.x, cy + shape.y
                Color((i+1)/len(self._face_.shape), 0, 0, 1)
                self._draw.shape(
                    _shape_=shape,
                    _pos_micro_=[px, py],
                )

    def _shape_delete(self, _shape_):
        _shape_.id = 0
        self._face_update()

    def _shape_select(self, _dx_, _dy_):
        shape_index = -1
        shape_index_free = -1
        for i, shape in enumerate(self._face_.shape):
            if shape.id > 0:
                if shape.contain(_dx_, _dy_, 10):
                    shape_index = i
                    break
            else:
                if shape_index_free == -1:
                    shape_index_free = i
        if shape_index == -1 and shape_index_free != -1:
            shape_index = shape_index_free
        if shape_index != -1:
            return self._face_.shape[shape_index]
        return None
    
    def _shape_open(self, _shape_):
        _shape_.limit()
        popup = Popup(
            title='BIÊN DẠNG',
            size_hint=(0.8, 0.8),
            auto_dismiss=False,
        )
        popup.content = PopupShape(
            _instance_=popup,
            _shape_=_shape_,
            _apply_=self._face_update,
            _delete_=self._shape_delete
            )
        popup.open()