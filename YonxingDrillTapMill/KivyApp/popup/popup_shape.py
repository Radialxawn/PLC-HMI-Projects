import re
from kivy.app import App
from core.draw import Draw
from core.mouse import Mouse
from kivy.graphics import Color
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from core.ui import UITextInputInteger
from kivy.uix.widget import Widget
from data.shape import ShapeID
from kivy.uix.label import Label
from core.ui import UIBoolInput
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
        property__input = {}
        shape_id_selector = self.ids.shape_id_selector
        #
        rule = self._rule_
        shape_ids = [ShapeID.NONE]
        for shape_id in Shape.shape_id__data:
            add = ('shape_include' in rule and shape_id in rule['shape_include'] or
                   'shape_exclude' in rule and shape_id not in rule['shape_exclude'])
            if add and shape_id not in shape_ids:
                shape_ids.append(shape_id)
        shape_id_selector.values = [Shape.shape_id__data[id]['label'] for id in shape_ids]
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
            input = None
            if 'factor' in data:
                input = UITextInputInteger(
                    halign='center',
                    multiline=False
                ).data_set(
                    _key_=property,
                    _factor_=data['factor'],
                    _validate_=self._on_text_input_validate,
                    _focus_=None,
                )
            elif 'state_text' in data:
                input = UIBoolInput().data_set(
                    _key_=property,
                    _validate_=self._on_bool_input_validate,
                    _state_text_=data['state_text'],
                )
            input.v_value_set(self._shape_edit[property])
            input.v_label = label
            box.add_widget(label)
            box.add_widget(input)
            property__input[property] = input
            self.ids.shape_property.add_widget(box)
        self.ids.shape_property.add_widget(Widget())
        return property__input

    def _on_bool_input_validate(self, _instance_, _value_):
        if _value_ != self._shape_edit[_instance_.v_key]:
            self._shape_edit[_instance_.v_key] = _value_
            self._update_canvas()

    def _on_text_input_validate(self, _instance_, _value_):
        if _value_ != self._shape_edit[_instance_.v_key]:
            self._shape_edit[_instance_.v_key] = _value_
            self._shape_edit_limit()
            self._update_canvas()
    
    def _shape_edit_limit(self):
        self._shape_edit.limit()
        for property in Shape.property__data:
            if Shape.property__data[property] == None:
                continue
            self._property__input[property].v_value_set(self._shape_edit[property])

    def _on_shape_id_selector(self, _instance_):
        if self._ignore_shape_id_selector:
            return
        self._shape_edit.id = self._label_to_id(_instance_.text).value
        self._shape_edit.default()
        self._shape_edit_limit()
        self._shape_id_changed = True
        self._update_canvas()

    def _update_canvas(self, *args):
        area = self.ids.area
        area.canvas.clear()
        self._draw.offset_pixel = [area.center_x, area.center_y]
        with area.canvas:
            self._draw.axis(area, [0, 0], None, 2)
            self._draw.shape(
                _shape_=self._shape_edit,
                _pos_micro_=[0, 0],
                _color_=clhex("#ff5656ff")
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
        for shape_id in Shape.shape_id__data:
            data = Shape.shape_id__data[shape_id]
            if data['label'] == _value_:
                return shape_id
        return None

    def _id_to_label(self, _value_):
        for shape_id in Shape.shape_id__data:
            data = Shape.shape_id__data[shape_id]
            if shape_id.value == _value_:
                return data['label']
        return None

    def _id_to_data(self, _value_):
        for shape_id in Shape.shape_id__data:
            data = Shape.shape_id__data[shape_id]
            if shape_id.value == _value_:
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