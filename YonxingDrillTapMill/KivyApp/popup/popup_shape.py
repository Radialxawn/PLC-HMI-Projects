import re
from kivy.app import App
from core.draw import Draw
from core.mouse import Mouse
from kivy.graphics import Color
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from core.ui import UITextInputInteger
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from data.shape import Shape
from kivy.utils import get_color_from_hex as clhex

class PopupShape(Popup):
    def set_data(self, _shape_, _rule_, _apply_, _delete_):
        _shape_.limit()
        self._shape_ = _shape_
        self._shape_edit = _shape_.clone()
        self._rule_ = _rule_
        self._apply_ = _apply_
        self._delete_ = _delete_
        self._draw = Draw(5e-3, [1e-3, 10e-3])
        self._mouse = Mouse()
        self._property__input = self._generate()
        self._shape_id_changed = True
        self.ids.area.bind(pos=self._update_canvas, size=self._update_canvas)
        return self

    def _generate(self):
        key__input = {}
        shape_id_selector = self.ids.shape_id_selector
        #
        rule = self._rule_
        shape_names = ['none']
        for shape_name in Shape.shape_name__data:
            add = ('shape_include' in rule and shape_name in rule['shape_include'] or
                   'shape_exclude' in rule and shape_name not in rule['shape_exclude'])
            if add and shape_name not in shape_names:
                shape_names.append(shape_name)
        shape_id_selector.values = [Shape.shape_name__data[sn]['label'] for sn in shape_names]
        #
        self.ids.shape_property.width = 180
        for property in Shape.property__data:
            data = Shape.property__data[property]
            if data == None:
                self.ids.shape_property.add_widget(Widget())
                continue
            box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=35,
            )
            label = Label(
                size_hint_x=None,
                halign='left',
                valign='center',
                width=60
            )
            label.bind(size=label.setter('text_size'))
            input = UITextInputInteger(
                halign='center',
                multiline=False
            ).data_set(
                _key_=property,
                _factor_=data['factor'],
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            input.v_value_set(self._shape_edit[property])
            input.v_label = label
            box.add_widget(label)
            box.add_widget(input)
            key__input[property] = input
            self.ids.shape_property.add_widget(box)
        self.ids.shape_property.add_widget(Widget())
        return key__input

    def _on_text_input_validate(self, _instance_, _value_):
        if _value_ != self._shape_edit[_instance_.v_key]:
            self._shape_edit[_instance_.v_key] = _value_
            self._update_canvas()

    def _on_shape_id_selector(self, _instance_):
        if self._ignore_shape_id_selector:
            return
        self._shape_edit.id = self._label_to_id(_instance_.text)
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        self._draw.offset_pixel = [area.center_x, area.center_y]
        with area.canvas:
            self._draw.axis(area, [0, 0], None, 2)
            Color(rgba=clhex("#ff5656ff"))
            self._draw.shape(
                _shape_=self._shape_edit,
                _pos_micro_=[0, 0],
            )
        data = self._id_to_data(self._shape_edit.id)
        if self._shape_id_changed:
            property__data = data['property__data']
            for property in self._property__input:
                inside = property in property__data
                opacity = 1 if inside else 0
                input = self._property__input[property]
                input.opacity = opacity
                input.v_label.opacity = opacity
                if inside:
                    label = property__data[property]
                    if label == None:
                        label = Shape.property__data[property]['label']
                    input.v_label.text = label
        self._ignore_shape_id_selector = True
        self.ids.shape_id_selector.text = self._id_to_label(self._shape_edit.id)
        self._ignore_shape_id_selector = False
        self._shape_id_changed = False
    
    def _label_to_id(self, _value_):
        for shape_name in Shape.shape_name__data:
            data = Shape.shape_name__data[shape_name]
            if data['label'] == _value_:
                return data['id']
        return None

    def _id_to_label(self, _value_):
        for shape_name in Shape.shape_name__data:
            data = Shape.shape_name__data[shape_name]
            if data['id'] == _value_:
                return data['label']
        return None

    def _id_to_data(self, _value_):
        for shape_name in Shape.shape_name__data:
            data = Shape.shape_name__data[shape_name]
            if data['id'] == _value_:
                return data
        return None

    def _apply(self):
        self._shape_edit.limit()
        self._shape_.copy(self._shape_edit)
        self._apply_()
        self.dismiss()
    
    def _delete(self):
        self._delete_(self._shape_)
        self.dismiss()

    def _cancel(self):
        self.dismiss()
    
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
            if changed:
                self._update_canvas()
        else:
            return super().on_touch_down(touch)