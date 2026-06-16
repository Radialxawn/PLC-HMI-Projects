import re
from kivy.app import App
from kivy.uix.label import Label
from popup.popup_shape import PopupShape
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from core.draw import Draw
from kivy.utils import get_color_from_hex as clhex

class PopupFace(Screen):
    def __init__(self, _instance_, _face_, _apply_, _delete_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._face_ = _face_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(1e-3)
        self._drag = {
            'active': False,
            'begin': [0, 0],
            'offset': [0, 0],
        }
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
        self._shape_apply()

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
            changed = False
            match touch.button:
                case 'scrollup':
                    self._draw.pixel_per_micro -= 1e-4
                    changed = True
                case 'scrolldown':
                    self._draw.pixel_per_micro += 1e-4
                    changed = True
                case 'left':
                    self._shape_select(dx, dy)
                case 'right':
                    self._drag['active'] = True
                    self._drag['begin'][0] = touch.pos[0]
                    self._drag['begin'][1] = touch.pos[1]
                    self._drag['offset'] = self._draw.offset_pixel
            if changed:
                self._shape_apply()
        else:
            return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self._drag['active'] == True:
            match touch.button:
                case 'right':
                    dx = touch.pos[0] - self._drag['begin'][0] + self._drag['offset'][0]
                    dy = touch.pos[1] - self._drag['begin'][1] + self._drag['offset'][1]
                    self._draw.offset_pixel = [dx, dy]
                    self._shape_apply()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self._drag['active'] = False
        return super().on_touch_up(touch)

    def _shape_apply(self):
        area = self.ids.area
        area.canvas.clear()
        self._face_.shape.sort(key=lambda s: s.x)
        with area.canvas:
            self._draw.axis(area, [area.center_x, area.center_y])
            cx, cy = self._draw.pixel_to_micro(area.center_x, area.center_y)
            for i, shape in enumerate(self._face_.shape):
                px, py = cx + shape.x, cy + shape.y
                Color((i+1)/len(self._face_.shape), 0, 0, 1)
                self._draw.shape(
                    _shape_=shape,
                    _position_=[px, py],
                )

    def _shape_delete(self, _shape_):
        _shape_.id = 0
        self._shape_apply()

    def _shape_select(self, _lx_, _ly_):
        area = self.ids.area
        offsetp = self._draw.offset_pixel
        dxp, dyp = _lx_ - area.size[0] * 0.5 - offsetp[0], _ly_ - area.size[1] * 0.5 - offsetp[1]
        dx, dy = self._draw.pixel_to_micro(dxp, dyp)
        shape_index = -1
        shape_index_free = -1
        for i, shape in enumerate(self._face_.shape):
            if shape.id > 0:
                if shape.contain(dx, dy, 10):
                    shape_index = i
                    break
            else:
                if shape_index_free == -1:
                    shape_index_free = i
        if shape_index == -1 and shape_index_free != -1:
            shape_index = shape_index_free
        if shape_index != -1:
            self._shape_open(self._face_.shape[shape_index])
    
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