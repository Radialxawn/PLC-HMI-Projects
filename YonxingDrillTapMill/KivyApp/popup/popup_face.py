import re
from kivy.app import App
from kivy.uix.screenmanager import Screen
from popup.popup_shape import PopupShape
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from core.draw import Draw
from kivy.graphics import Color, StencilPush, StencilUse, StencilUnUse, Rectangle, Ellipse

class PopupFace(Screen):
    def __init__(self, _instance_, _face_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._face_ = _face_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(1e-3)
        self._generate()
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        self._fp__name = {
            'ox':     'x',
            'oy':     'y',
            'oz':     'z',
            'tool_d': 'đường kính dao',
            'depth':  'độ sâu',
            'feed':   'tốc độ',
        }
        self.ids.face_property.add_widget(Widget())
        self.ids.face_property.width = 320
        for fp in self._fp__name:
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            olabel = Label(
                text=self._fp__name[fp].upper(),
                size_hint_x=None,
                width=160
            )
            oinput = TextInput(
                hint_text='...',
                halign='center',
                input_filter=self._on_text_input_filter,
                multiline=False
            )
            oinput.fp = fp
            oinput.bind(on_text_validate=self._on_text_input_validate)
            oinput.bind(focus=self._on_text_input_focus)
            obox.add_widget(olabel)
            obox.add_widget(oinput)
            self.ids.face_property.add_widget(obox)
        self.ids.face_property.add_widget(Widget())
    
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
        if value != self._face_[_instance_.fp]:
            self._face_[_instance_.fp] = value
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)

    def _update_canvas(self, *args):
        print('update face')

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
        area_pos = [a + b for a, b in zip(self.pos, self.ids.area.pos)]
        area_size = self.ids.area.size
        dx = touch.pos[0] - area_pos[0]
        dy = touch.pos[1] - area_pos[1]
        inside = 0 < dx < area_size[0] and 0 < dy < area_size[1]
        if inside:
            if touch.button == 'scrollup':
                self._draw.set(1e-3, 0, 0)
                self._shape_apply()
            elif touch.button == 'scrolldown':
                self._draw.set(5e-3, 0, 0)
                self._shape_apply()
            elif touch.button == 'left':
                self._shape_select(dx, dy)
        else:
            super().on_touch_down(touch)

    def _shape_apply(self):
        area = self.ids.area
        area.canvas.clear()
        with area.canvas:
            StencilPush()
            Color(1, 1, 1, 1)
            Ellipse(pos=(100, 100), size=(200, 200))
            StencilUse()
            Color(1, 0, 0, 1)
            Rectangle(pos=[area.center_x, area.center_y], size=[area.size[0]*0.5, 1])
            Color(0, 1, 0, 1)
            Rectangle(pos=[area.center_x, area.center_y], size=[1, area.size[1]*0.5])
        cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
        for index in self._face_.index__shape:
            shape = self._face_.index__shape[index]
            px, py = cx + shape.x, cy + shape.y
            self._draw.shape(
                _area_=area,
                _shape_=shape,
                _position_=[px, py],
            )
        with area.canvas:
            StencilUnUse()

    def _shape_delete(self, _shape_):
        _shape_.id = 0
        self._shape_apply()

    def _shape_select(self, _lx_, _ly_):
        area = self.ids.area
        dxp, dyp = _lx_ - area.size[0] * 0.5, _ly_ - area.size[1] * 0.5
        dx, dy = self._draw.pixel_to_micro(dxp, dyp)
        shape_index = -1
        shape_index_free = -1
        for index in self._face_.index__shape:
            shape = self._face_.index__shape[index]
            if shape.id > 0:
                if shape.contain(dx, dy, 10):
                    shape_index = index
                    break
            else:
                if shape_index_free == -1:
                    shape_index_free = index
        if shape_index == -1 and shape_index_free != -1:
            shape_index = shape_index_free
        if shape_index != -1:
            self._shape_open(self._face_.index__shape[shape_index])
    
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