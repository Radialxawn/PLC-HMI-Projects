import re
from kivy.app import App
from core.draw import Draw
from core.mouse import Mouse
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from data.shape import Shape
from core.ui import UI
from kivy.utils import get_color_from_hex as clhex

class PopupShape(Screen):
    def __init__(self, _instance_, _shape_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        _shape_.limit()
        self._shape_ = _shape_
        self._shape_edit = _shape_.clone()
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(5e-3, [1e-3, 10e-3])
        self._mouse = Mouse()
        self._generate()
        self._shape_id_changed = True
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        self._key__widget = {}
        for k in vars(self._shape_edit):
            self._key__widget[k] = []
        shape_id_selector = self.ids.shape_id_selector
        datas = []
        for data in Shape.shape_name__data.values():    
            datas.append(data)
        datas.sort(key=lambda s: s['id'])
        shape_id_selector.values = [d['namev'] for d in datas]
        self.ids.shape_property.width = 180
        for key in Shape.key__data:
            data = Shape.key__data[key]
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            olabel = Label(
                text=data['namev'],
                size_hint_x=None,
                width=30
            )
            obox.add_widget(olabel)
            oinput = UI.generate_text_input_number(self, key, data['factor'], self._shape_edit[key], obox)
            self._key__widget[key].append(olabel)
            self._key__widget[key].append(oinput)
            self.ids.shape_property.add_widget(obox)
            if key == 'y':
                self.ids.shape_property.add_widget(Widget())
        self.ids.shape_property.add_widget(Widget())

    def _on_text_input_validate(self, _instance_):
        value = 0
        try:
            value = int(float(_instance_.text)/_instance_.v_factor)
        except (ValueError, TypeError):
            _instance_.text = ''
        if value != self._shape_edit[_instance_.v_key]:
            self._shape_edit[_instance_.v_key] = value
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)
    
    def _on_shape_id_selector(self, _instance_):
        if self._ignore_shape_id_selector:
            return
        for name in Shape.shape_name__data:
            data = Shape.shape_name__data[name]
            if _instance_.text == data['namev']:
                self._shape_edit.id = data['id']
                break
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y], None, 2)
            Color(rgba=clhex("#ff5656ff"))
            self._draw.shape(
                _shape_=self._shape_edit,
                _pos_micro_=[cx, cy],
            )
        active_sp = []
        for name in Shape.shape_name__data:
            data = Shape.shape_name__data[name]
            if data['id'] == self._shape_edit.id:
                active_sp = data['sp']
                break
        if self._shape_id_changed:
            for sp in self._key__widget:
                opacity = 1 if sp in active_sp else 0
                wg = self._key__widget[sp]
                for e in wg:
                    e.opacity = opacity
        self._ignore_shape_id_selector = True
        self.ids.shape_id_selector.text = self.ids.shape_id_selector.values[self._shape_edit['id']]
        self._ignore_shape_id_selector = False
        self._shape_id_changed = False

    def _apply(self):
        self._shape_edit.limit()
        self._shape_.copy(self._shape_edit)
        self._apply_()
        self._instance_.dismiss()
    
    def _delete(self):
        self._delete_(self._shape_)
        self._instance_.dismiss()

    def _cancel(self):
        self._instance_.dismiss()
    
    def on_touch_down(self, touch):
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
            if changed:
                self._update_canvas()
        else:
            return super().on_touch_down(touch)