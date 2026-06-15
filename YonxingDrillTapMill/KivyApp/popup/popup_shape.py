import re
from kivy.app import App
from core.draw import Draw
from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from data.shape import Shape
from kivy.utils import get_color_from_hex as clhex

class PopupShape(Screen):
    def __init__(self, _instance_, _shape_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._shape_ = _shape_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(5e-3)
        self._generate()
        self._shape_id_changed = True
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        self._sp__widget = {}
        for k in vars(self._shape_):
            self._sp__widget[k] = []
        self._sp__name = {
            'x':  'x',
            'y':  'y',
            'va': 'a',
            'vb': 'b',
            'vc': 'c',
            'vd': 'd',
            've': 'e',
        }
        shape_id_selector = self.ids.shape_id_selector
        values = []
        for shape_name in Shape.name__data:
            values.append(shape_name)
            shape_id_selector.values = values
        self.ids.shape_property.width = 180
        for sp in self._sp__name:
            obox = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            olabel = Label(
                text=self._sp__name[sp].upper(),
                size_hint_x=None,
                width=30
            )
            obox.add_widget(olabel)
            oinput = self._generate_input(sp, self._shape_[sp], obox)
            self._sp__widget[sp].append(olabel)
            self._sp__widget[sp].append(oinput)
            self.ids.shape_property.add_widget(obox)
            if sp == 'y':
                self.ids.shape_property.add_widget(Widget())
        self.ids.shape_property.add_widget(Widget())
    
    def _generate_input(self, _sp_, _value_, _parent_):
        ip = TextInput(
            halign='center',
            input_filter=self._on_text_input_filter,
            multiline=False
        )
        ip.sp = _sp_
        ip.text = str(_value_*1e-3)
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
        if value != self._shape_[_instance_.sp]:
            self._shape_[_instance_.sp] = value
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)
    
    def _on_shape_id_selector(self, _instance_):
        if self._ignore_shape_id_selector:
            return
        self._shape_.id = Shape.name__data[_instance_.text]['id']
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
        self._shape_.limit()
        with area.canvas:
            Color(rgba=clhex("#ff5656ff"))
            self._draw.shape(
                _shape_=self._shape_,
                _position_=[cx, cy],
            )
        active_sp = []
        for name in Shape.name__data:
            data = Shape.name__data[name]
            if data['id'] == self._shape_.id:
                active_sp = data['sp']
                break
        if self._shape_id_changed:
            for sp in self._sp__widget:
                opacity = 1 if sp in active_sp else 0
                wg = self._sp__widget[sp]
                for e in wg:
                    e.opacity = opacity
        self._ignore_shape_id_selector = True
        self.ids.shape_id_selector.text = self.ids.shape_id_selector.values[self._shape_['id']]
        self._ignore_shape_id_selector = False
        self._shape_id_changed = False

    def _apply(self):
        self._apply_()
        self._instance_.dismiss()
    
    def _delete(self):
        self._delete_(self._shape_)
        self._instance_.dismiss()

    def _cancel(self):
        self._instance_.dismiss()