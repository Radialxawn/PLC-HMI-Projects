import re
from kivy.uix.textinput import TextInput

class UI():
    @staticmethod
    def generate_text_input_number(_self_, _key_, _factor_, _value_, _parent_):
        ip = TextInput(
            halign='center',
            multiline=False
        )
        ip.v_key = _key_
        ip.v_factor = _factor_
        match _factor_:
            case 1e-1:
                ip.input_filter=UI.filter_float
                ip.text = f'{(_value_*1e-1):.1f}'
            case 1e-2:
                ip.input_filter=UI.filter_float
                ip.text = f'{(_value_*1e-2):.2f}'
            case 1e-3:
                ip.input_filter=UI.filter_float
                ip.text = f'{(_value_*1e-3):.3f}'
            case _:
                ip.input_filter=UI.filter_int
                ip.text = f'{_value_}'
        ip.bind(on_text_validate=_self_._on_text_input_validate)
        ip.bind(focus=_self_._on_text_input_focus)
        _parent_.add_widget(ip)
        return ip
    
    @staticmethod
    def filter_int(_substring_, _from_undo_):
        pattern = re.compile(r'[^0-9-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered

    @staticmethod
    def filter_float(_substring_, _from_undo_):
        pattern = re.compile(r'[^0-9.-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered

    @staticmethod
    def filter_file_name(_substring_, _from_undo_):
        pattern = re.compile(r'[^a-zA-Z0-9_-]')
        filtered = re.sub(pattern, '', _substring_)
        return filtered