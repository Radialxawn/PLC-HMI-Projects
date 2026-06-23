import re
from kivy.uix.textinput import TextInput

class UITextInputInteger(TextInput):
    def data_set(self, _key_, _factor_, _validate_, _focus_) -> TextInput:
        self.v_key = _key_
        self._v_factor = abs(_factor_)
        self._v_validate = _validate_
        self._v_focus = _focus_
        self._v_value = 0
        negative = _factor_ < 0
        if self._v_factor == 1:
            if negative:
                self._v_pattern = re.compile(r'[^0-9-]')
            else:
                self._v_pattern = re.compile(r'[^0-9]')
        else:
            if negative:
                self._v_pattern = re.compile(r'[^0-9.-]')
            else:
                self._v_pattern = re.compile(r'[^0-9.]')
        match self._v_factor:
            case 1e-3:
                self._v_format = '{:.3f}'
            case 1e-2:
                self._v_format = '{:.2f}'
            case 1e-1:
                self._v_format = '{:.1f}'
            case 1:
                self._v_format = '{:.0f}'
        self.bind(on_text_validate=self._v_on_validate)
        self.bind(focus=self._v_on_focus)
        return self
    
    def _v_on_validate(self, _instance_):
        self._v_value = self._v_parse(_instance_.text)
        if self._v_validate != None:
            self._v_validate(_instance_, self.v_value_get())
    
    def _v_on_focus(self, _instance_, _value_):
        if self._v_focus != None:
            self._v_focus(_instance_, _value_)
        if not _value_:
            self.text = self._v_format.format(self._v_value)
    
    def _v_parse(self, _string_):
        try:
            value = float(_string_)
            return value
        except (ValueError, TypeError):
            self.text = str(self._v_value)
            return self._v_value

    def v_value_set(self, _value_):
        if _value_ != None:
            self._v_value = _value_ * self._v_factor
            self.text = self._v_format.format(self._v_value)
        else:
            self.text = ''
    
    def v_value_get(self):
        return round(self._v_value / self._v_factor)

    def insert_text(self, _substring_, from_undo=False):
        filtered = re.sub(self._v_pattern, '', _substring_)
        return super(UITextInputInteger, self).insert_text(filtered, from_undo=from_undo)

class UI():
    @staticmethod
    def filter_file_name(_substring_, _from_undo_):
        pattern = re.compile(r'[^a-zA-Z0-9_-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered