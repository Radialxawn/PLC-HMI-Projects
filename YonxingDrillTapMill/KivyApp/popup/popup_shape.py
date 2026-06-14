import re
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from kivy.graphics import PushMatrix, PopMatrix, Scale
from kivy.graphics.transformation import Matrix
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

class PopupShape(Screen):
    def __init__(self, _instance_, _shape_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._shape_ = _shape_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._generate()
        self._shape_id_changed = True
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)
    
    def on_enter(self, *args):
        return

    def _generate(self):
        self._shape_name__shape_id = {
            'NONE':     0,
            'DRILL':    1,
            'TAP':      2,
            'CIRCLE':   3,
            'RECT':     4,
            'CAPSULE':  5,
            'RECT-R':    6,
            'ELLIPSE':  7,
            'LOCKA':    8,
            'LOCKA-F':  9,
            'LOCKB':    10,
            'LOCKB-F':  11,
            'CNC-1':    12,
            'CNC-2':    13,
            'CNC-3':    14,
            'CNC-4':    15,
            'CNC-5':    16,
            'CNC-6':    17,
        }
        self._shape_id__shape_name = {value: key for key, value in self._shape_name__shape_id.items()}
        if len(self._shape_name__shape_id) != len(self._shape_id__shape_name):
            raise Exception('Swap k, v failed')
        self._sp__widget = {
            'x':  [],
            'y':  [],
            'va': [],
            'vb': [],
            'vc': [],
            'vd': [],
            've': [],
        }
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
        for shape_name in self._shape_name__shape_id:
            values.append(shape_name)
            shape_id_selector.values = values
        for sp in self._sp__widget:
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
            oinput = TextInput(
                hint_text='...',
                halign='center',
                input_filter=self._on_text_input_filter,
                multiline=False
            )
            oinput.sp = sp
            oinput.bind(on_text_validate=self._on_text_input_validate)
            oinput.bind(focus=self._on_text_input_focus)
            obox.add_widget(olabel)
            obox.add_widget(oinput)
            self._sp__widget[sp].append(olabel)
            self._sp__widget[sp].append(oinput)
            self.ids.shape_property.add_widget(obox)
            if sp == 'y':
                self.ids.shape_property.add_widget(Widget())
        self.ids.shape_property.add_widget(Widget())
    
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
        self._shape_['id'] = self._shape_name__shape_id[_instance_.text]
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        active_sp = PopupShape.draw_shape(
            _area_=area,
            _shape_=self._shape_,
            _position_=[area.center_x, area.center_y],
            _scale_=5e-3,
            _indicator_=None
        )
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
    
    @staticmethod
    def draw_shape(_area_, _shape_, _position_, _scale_, _indicator_):
        sid = _shape_['id']
        x, y, va, vb, vc, vd, ve = 'x', 'y', 'va', 'vb', 'vc', 'vd', 've'
        sa = _shape_[va] * _scale_
        sb = _shape_[vb] * _scale_
        sc = _shape_[vc] * _scale_
        sd = _shape_[vd] * _scale_
        se = _shape_[ve] * _scale_
        bound = min(_area_.size)
        bound = max(0, bound - 10)
        if bound == 0.0:
            return []
        active_sp = []
        with _area_.canvas:
            match sid:
                case 1: # drill
                    active_sp = [x, y, va, vb, vc]
                case 2: # tap
                    active_sp = [x, y, va, vb, vc]
                case 3: # circle
                    Color(1, 0, 0, 1)
                    Ellipse(pos=[_position_[0]-sa*0.5, _position_[1]-sa*0.5], size=[sa, sa])
                    active_sp = [x, y, va]
                case 4: # rect
                    Color(1, 0, 0, 1)
                    Rectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb])
                    active_sp = [x, y, va, vb]
                case 5: # capsule
                    Color(1, 0, 0, 1)
                    sb = min(sa, sb)
                    _shape_[vb] = sb
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    active_sp = [x, y, va, vb]
                case 6: # rectr
                    Color(1, 0, 0, 1)
                    sc = int(min(sc, sb*0.5))
                    _shape_[vc] = sc
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sc])
                    active_sp = [x, y, va, vb, vc]
                case 7: # ellipse
                    Color(1, 0, 0, 1)
                    Ellipse(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb])
                    active_sp = [x, y, va, vb]
                case 8: # locka
                    Color(1, 0, 0, 1)
                    sb = int(min(sa, sb))
                    _shape_[vb] = sb
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Ellipse(pos=[_position_[0]-sc*0.5+(sa-sc)*0.5, _position_[1]-sc*0.5], size=[sc, sc])
                    active_sp = [x, y, va, vb, vc]
                case 9: # lockaf
                    Color(1, 0, 0, 1)
                    sb = int(min(sa, sb))
                    _shape_[vb] = sb
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Ellipse(pos=[_position_[0]-sc*0.5-(sa-sc)*0.5, _position_[1]-sc*0.5], size=[sc, sc])
                    active_sp = [x, y, va, vb, vc]
                case 10: # lockb
                    Color(1, 0, 0, 1)
                    sb = int(min(sa, sb))
                    _shape_[vb] = sb
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Rectangle(pos=[_position_[0]-sd*0.5, _position_[1]-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
                    active_sp = [x, y, va, vb, vc, vd]
                case 11: # lockbf
                    Color(1, 0, 0, 1)
                    sb = int(min(sa, sb))
                    _shape_[vb] = sb
                    RoundedRectangle(pos=[_position_[0]-sa*0.5, _position_[1]-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Rectangle(pos=[_position_[0]-sd*0.5, _position_[1]-sc*0.5+(sc-sb)*0.5], size=[sd, sc])
                    active_sp = [x, y, va, vb, vc, vd]
            scid = -1
            if sid > 11:
                scid = sid - 11 - 1
            if scid >= 0:
                Color(1, 0, 0, 1)
                Line(rectangle=(_position_[0]-bound*0.5, _position_[1]-bound*0.5, bound, bound), width=2)
            if _indicator_:
                Color(0, 0, 1, 1)
                r = _indicator_['radius']
                Ellipse(pos=[_position_[0]-r, _position_[1]-r], size=[r*2, r*2])
        return active_sp

    def _apply(self):
        self._apply_()
        self._instance_.dismiss()
    
    def _delete(self):
        self._delete_()
        self._instance_.dismiss()

    def _cancel(self):
        self._instance_.dismiss()