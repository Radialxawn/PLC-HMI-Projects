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
from data.face import Face
from core.ui import UI
from kivy.utils import get_color_from_hex as clhex

class PopupFace(Screen):
    def __init__(self, _instance_, _face_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        _face_.limit()
        self._face_ = _face_
        self._face_edit = _face_.clone()
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(1e-3, [0.5e-3, 10e-3])
        self._mouse = Mouse()
        self._generate()
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        self.ids.face_property.add_widget(Widget())
        self.ids.face_property.width = 320
        for key in Face.key__data:
            data = Face.key__data[key]
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            olabel = Label(
                text=data['namev'],
                size_hint_x=None,
                width=180
            )
            obox.add_widget(olabel)
            UI.generate_text_input_number(self, key, data['factor'], self._face_edit[key], obox)
            self.ids.face_property.add_widget(obox)
        self.ids.face_property.add_widget(Widget())
        for i in range(len(self._face_edit.z)):
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
            UI.generate_text_input_number(self, f'z[{i}]', 1e-3, self._face_edit.z[i], obox)
            UI.generate_text_input_number(self, f'zs[{i}]', 1e-3, self._face_edit.zs[i], obox)
            self.ids.face_property.add_widget(obox)
        self.ids.face_property.add_widget(Widget())

    def _on_text_input_validate(self, _instance_):
        value = 0
        try:
            value = int(float(_instance_.text)/_instance_.v_factor)
        except (ValueError, TypeError):
            _instance_.text = ''
        changed = False
        array = _instance_.v_key.split('[')
        if len(array) > 1:
            self._face_edit[array[0]][int(array[1][:-1])] = value
            changed = True
        elif value != self._face_edit[_instance_.v_key]:
            self._face_edit[_instance_.v_key] = value
            changed = True
        if changed:
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)

    def _update_canvas(self, *args):
        self._face_draw()

    def _apply(self):
        self._face_edit.limit()
        self._face_.copy(self._face_edit)
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
                self._face_draw()
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
                        shape.x = offset[0] + dx
                        shape.y = offset[1] + dy
                        self._face_draw()
                case 'right':
                    dxp = touch.pos[0] - self._mouse.drag_begin[0] + self._mouse.drag_offset[0]
                    dyp = touch.pos[1] - self._mouse.drag_begin[1] + self._mouse.drag_offset[1]
                    self._draw.offset_pixel = [dxp, dyp]
                    self._face_draw()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        match touch.button:
            case 'left':
                shape = self._mouse.selected_object
                if Clock.get_time() - self._mouse.down_time_sec < 0.2:
                    if shape != None:
                        if shape.id == 0:
                            pos = self._mouse.selected_object_pos
                            shape.x = pos[0]
                            shape.y = pos[1]
                        self._shape_open(shape)
        self._mouse.drag = False
        self._mouse.selected_object = None
        return super().on_touch_up(touch)
    
    def _face_draw(self):
        area = self.ids.area
        area.canvas.clear()
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y], None, 2)
            cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
            for i, shape in enumerate(self._face_edit.shape):
                px, py = cx + shape.x, cy + shape.y
                Color((i+1)/len(self._face_edit.shape), 0, 0, 1)
                self._draw.shape(
                    _shape_=shape,
                    _pos_micro_=[px, py],
                )

    def _shape_apply(self):
        self._face_edit.shape.sort(key=lambda s: (s.id == 0, s.x)) # sort using x value and push id = 0 object to the back
        self._face_draw()

    def _shape_delete(self, _shape_):
        _shape_.id = 0
        self._shape_apply()
        self._face_draw()

    def _shape_select(self, _dx_, _dy_):
        shape_index = -1
        shape_index_free = -1
        for i, shape in enumerate(self._face_edit.shape):
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
            return self._face_edit.shape[shape_index]
        return None
    
    def _shape_open(self, _shape_):
        popup = Popup(
            title='BIÊN DẠNG',
            size_hint=(0.8, 0.8),
            auto_dismiss=False,
        )
        popup.content = PopupShape(
            _instance_=popup,
            _shape_=_shape_,
            _apply_=self._shape_apply,
            _delete_=self._shape_delete
            )
        popup.open()