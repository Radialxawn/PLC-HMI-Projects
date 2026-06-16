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
from kivy.utils import get_color_from_hex as clhex

class PopupShape(Screen):
    def __init__(self, _instance_, _shape_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._shape_ = _shape_
        self._shape_edit = Shape().copy(_shape_)
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(5e-3, [1e-3, 10e-3])
        self._mouse = Mouse()
        self._generate()
        self._shape_id_changed = True
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)

    def _generate(self):
        self._sp__widget = {}
        for k in vars(self._shape_edit):
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
        datas = []
        for data in Shape.name__data.values():    
            datas.append(data)
        datas.sort(key=lambda s: s['id'])
        shape_id_selector.values = [d['namev'] for d in datas]
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
            oinput = self._generate_input(sp, self._shape_edit[sp], obox)
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
        if value != self._shape_edit[_instance_.sp]:
            self._shape_edit[_instance_.sp] = value
            self._update_canvas()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
        if not _value_:
            self._on_text_input_validate(_instance_)
    
    def _on_shape_id_selector(self, _instance_):
        if self._ignore_shape_id_selector:
            return
        for name in Shape.name__data:
            data = Shape.name__data[name]
            if _instance_.text == data['namev']:
                self._shape_edit.id = data['id']
                break
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
        self._shape_edit.limit()
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y])
            Color(rgba=clhex("#ff5656ff"))
            self._draw.shape(
                _shape_=self._shape_edit,
                _pos_micro_=[cx, cy],
            )
        active_sp = []
        for name in Shape.name__data:
            data = Shape.name__data[name]
            if data['id'] == self._shape_edit.id:
                active_sp = data['sp']
                break
        if self._shape_id_changed:
            for sp in self._sp__widget:
                opacity = 1 if sp in active_sp else 0
                wg = self._sp__widget[sp]
                for e in wg:
                    e.opacity = opacity
        self._ignore_shape_id_selector = True
        self.ids.shape_id_selector.text = self.ids.shape_id_selector.values[self._shape_edit['id']]
        self._ignore_shape_id_selector = False
        self._shape_id_changed = False

    def _apply(self):
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