import json
import kivy.utils
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from core.ui import UITextInputInteger
from kivy.uix.label import Label

class ScreenSettingAxis(Screen):
    axis_name__data = {
        'R-x':     {'index': 0,  'label': 'PHẢI: X'},
        'RM-V-y':  {'index': 2,  'label': 'PHẢI: Y ĐỨNG'},
        'RM-V-z':  {'index': 1,  'label': 'PHẢI: Z ĐỨNG'},
        'RM-H-y':  {'index': 3,  'label': 'PHẢI: Y NGANG'},
        'RM-H-z':  {'index': 4,  'label': 'PHẢI: Z NGANG'},
        'L-x':     {'index': 5,  'label': 'TRÁI: X'},
        'LDT-V-y': {'index': 7,  'label': 'TRÁI: Y'},
        'LD-V-z':  {'index': 6,  'label': 'TRÁI: KHOAN Z ĐỨNG'},
        'LD-L-z':  {'index': 10, 'label': 'TRÁI: KHOAN Z NGHIÊNG'},
        'LT-V-z':  {'index': 8,  'label': 'TRÁI: TARO Z ĐỨNG'},
        'LT-V-a':  {'index': 9,  'label': 'TRÁI: TARO XOAY ĐỨNG'},
        'LT-L-z':  {'index': 11, 'label': 'TRÁI: TARO Z NGHIÊNG'},
        'LT-L-a':  {'index': 12, 'label': 'TRÁI: TARO XOAY NGHIÊNG'},
    }

    property__data = {
        'max_rpm':                        {'label': 'Max RPM',               'factor': 1},
        'gear_num':                       {'label': 'Gear num',              'factor': 1},
        'gear_den':                       {'label': 'Gear den',              'factor': 1},
        'gear_dir':                       {'label': 'Gear dir',              'factor': 1},
        'home_torque_mNm':                {'label': 'Home torque',           'factor': 1e-3},
        'home_encoder_value':             {'label': 'Home encoder',          'factor': 1},
        'max_micro':                      {'label': 'Max travel',            'factor': 1e-3},
        'overload_hold_torque_factor':    {'label': 'Hold torque factor',    'factor': 1e-3},
        'overload_hold_torque_time_msec': {'label': 'Hold torque time',      'factor': 1e-3},
        'overload_instant_torque_factor': {'label': 'Instant torque factor', 'factor': 1e-3},
        'ramp_time_msec':                 {'label': 'Ramp time',             'factor': 1e-3},
        'jerk_factor':                    {'label': 'Jerk',                  'factor': 1},
    }

    def __init__(self, **kvargs):
        super(ScreenSettingAxis, self).__init__(**kvargs)
        self._first_load = True

    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__hash = {
                'hmi.cfsh.need',
                'hmi.cfsh.need_check',
                'hmi.cfsh.accept',
                'hmi.cfsh.decline',
                'hmi.cf.home_encoder_value_recorded',
                'hmi.view_can_home',
                'hmi.home',
            }
            self._label__data, self._name__input, self._name__value = self._generate()

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__hash, self._name__input)
        if not hasattr(self, '_value_update_clock'):
            self._label_scroll_clock = Clock.schedule_interval(self._label_scroll, 0.2)
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.2)

    def on_leave(self, *args):
        if hasattr(self, '_label_scroll_clock'):
            Clock.unschedule(self._label_scroll_clock)
            delattr(self, '_label_scroll_clock')
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _label_scroll(self, _dt_):
        for label in self._label__data:
            data = self._label__data[label]
            text = data[0]
            index = data[1]
            count = data[2]
            if count <= 0:
                continue
            tl = len(text)
            if tl > count:
                index = (index + 1) % tl
                data[1] = index
                tc = text[index:index+count]
                tcl = len(tc)
                ih = max(0, count - tcl)
                if tcl < count:
                    tc += text[:ih]
                label.text = tc
    
    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._name__input:
            input = self._name__input[name]
            if input.focus:
                continue
            block = app.data.block(name)
            value = self._name__value[name]
            if value == block.value:
                continue
            self._name__value[name] = block.value
            if block.type == ua.VariantType.Boolean:
                value = block.value == 1
                input.state = 'down' if value else 'normal'
                input.text = 'THUẬN' if value else 'NGHỊCH'
            else:
                input.v_value_set(block.value)
        need = app.data.get('hmi.cfsh.need')
        self.ids['hmi.cfsh.accept'].disabled = not need
        self.ids['hmi.cfsh.decline'].disabled = not need
        self.ids['hmi.cf.home_encoder_value_recorded'].state = (
            'down' if app.data.get('hmi.cf.home_encoder_value_recorded') else 'normal')
        self.ids['hmi.home'].disabled = not app.data.get('hmi.view_can_home')

    def _generate(self):
        app = App.get_running_app()
        axis_name_array = []
        axis_index_array = []
        label__data, name__input, name__value = {}, {}, {}
        for name in ScreenSettingAxis.axis_name__data:
            data = ScreenSettingAxis.axis_name__data[name]
            axis_name_array.append(name)
            axis_index_array.append(data['index'])
        property_array = []
        for property in ScreenSettingAxis.property__data:
            property_array.append(property)
        axis_type__color = {
            'x': kivy.utils.get_color_from_hex('#ff4444ff'),
            'y': kivy.utils.get_color_from_hex('#95fe54ff'),
            'z': kivy.utils.get_color_from_hex('#526fffff'),
            'a': kivy.utils.get_color_from_hex('#fff644ff'),
        }
        grid = self.ids.grid
        grid.cols = len(ScreenSettingAxis.property__data) + 1
        grid.rows = len(axis_name_array) + 1
        grid.add_widget(Label(
            text='Servo'
        ))
        for property in ScreenSettingAxis.property__data:
            label = Label()
            labelv = ScreenSettingAxis.property__data[property]['label']
            labeld = [' | ' + labelv, 3, 10]
            if len(labelv) <= labeld[2]:
                label.text = labelv
                labeld[2] = 0
            label__data[label] = labeld
            grid.add_widget(label)
        for i in range(grid.cols):
            for j in range(grid.rows - 1):
                if j == 0:
                    grid.add_widget(Label(
                        text=axis_name_array[i],
                        color=axis_type__color[axis_name_array[i][-1]]
                    ))
                else:
                    input = None
                    property = property_array[j - 1]
                    data = ScreenSettingAxis.property__data[property]
                    name = 'hmi.cf.%s[%d]' % (property, axis_index_array[i])
                    if app.data.block(name).type == ua.VariantType.Boolean:
                        input = ToggleButton()
                        input.focus = False
                        input.name = name
                        input.bind(on_press=self._on_toggle_press)
                    else:
                        input = UITextInputInteger(
                            halign='center',
                            multiline=False
                        ).data_set(
                            _key_=name,
                            _factor_=data['factor'],
                            _validate_=self._on_text_input_validate,
                            _focus_=None
                        )
                    name__input[name] = input
                    name__value[name] = None
                    grid.add_widget(input)
        return label__data, name__input, name__value
    
    def _on_toggle_press(self, _instance_):
        app = App.get_running_app()
        value = _instance_.state == 'down'
        app.data.set(_instance_.name, value)
        app.helper.save_need_check()
        
    def _on_text_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)
        app.helper.save_need_check()
    
    def _on_home_recorded_reset(self):
        app = App.get_running_app()
        app.helper.show_popup_confirm(
            _message_='RESET GỐC ENCODER?',
            _confirm_=self._on_home_recorded_reset_confirm
        )

    def _on_home_recorded_reset_confirm(self):
        app = App.get_running_app()
        app.data.set('hmi.cf.home_encoder_value_recorded', False)
        app.helper.save_need_check()
    
    def _config_axis_path(self):
        return Path(Path(__file__).resolve().parent.parent, 'config/axis.json')

    def _config_axis_load_confirm(self):
        config = {}
        app = App.get_running_app()
        path = self._config_axis_path()
        if not path.exists():
            print(f'{path} does not exist')
            return
        with path.open(mode='r') as file:
            config = json.load(file)
        names, values = [], []
        for name in config:
            value = config[name]
            if value == None:
                continue
            app.data.set(name, value)
        app.helper.save_need_check()

    def _config_axis_load(self):
        app = App.get_running_app()
        app.helper.show_popup_confirm(
            _message_='LẤY DỮ LIỆU TRÊN HMI?',
            _confirm_=self._config_axis_load_confirm
        )
    
    def _config_axis_save_confirm(self):
        config = {}
        app = App.get_running_app()
        for name in self._name__input:
            block = app.data.block(name)
            if block.type == ua.VariantType.Boolean:
                config[name] = block.value == 1
            else:
                config[name] = block.value
        with open(self._config_axis_path(), 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=3)

    def _config_axis_save(self):
        app = App.get_running_app()
        app.helper.show_popup_confirm(
            _message_='LƯU DỮ LIỆU VÀO HMI?',
            _confirm_=self._config_axis_save_confirm
        )