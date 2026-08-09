import json
import kivy.utils
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from core.ui import UITextInputInteger
from kivy.uix.label import Label
from core.ui import UIBoolInput

class ScreenHome(Screen):
    axis_list = [
        {'name': 'DC-z',  'index': 0,  'label': ''},
        {'name': 'D-x',   'index': 1,  'label': ''},
        {'name': 'D-z',   'index': 2,  'label': ''},
        {'name': 'DT-z',  'index': 3,  'label': ''},
        {'name': 'DB-z',  'index': 4,  'label': ''},
        {'name': 'C-y',   'index': 5,  'label': ''},
        {'name': 'T-z',   'index': 6,  'label': ''},
        {'name': 'C-a',   'index': 7,  'label': ''},
        {'name': 'D-a',   'index': 8,  'label': ''},
        {'name': 'DT-a',  'index': 9,  'label': ''},
        {'name': 'DB-a',  'index': 10, 'label': ''},
        {'name': 'T-a',   'index': 11, 'label': ''},
    ]

    axis_stat = [
        None,
        {'name': 'max_rpm',                        'label': 'Max RPM',               'factor': 1},
        {'name': 'gear_num',                       'label': 'Gear num',              'factor': 1},
        {'name': 'gear_den',                       'label': 'Gear den',              'factor': 1},
        {'name': 'gear_dir',                       'label': 'Gear dir',              'factor': 1},
        {'name': 'home_torque_mNm',                'label': 'Home torque',           'factor': 1e-3},
        {'name': 'home_encoder_value',             'label': 'Home encoder',          'factor': 1},
        {'name': 'max_micro',                      'label': 'Max travel',            'factor': 1e-3},
        {'name': 'overload_hold_torque_factor',    'label': 'Hold torque factor',    'factor': 1e-3},
        {'name': 'overload_hold_torque_time_msec', 'label': 'Hold torque time',      'factor': 1e-3},
        {'name': 'overload_instant_torque_factor', 'label': 'Instant torque factor', 'factor': 1e-3},
        {'name': 'ramp_time_msec',                 'label': 'Ramp time',             'factor': 1e-3},
        {'name': 'jerk_factor',                    'label': 'Jerk',                  'factor': 1},
    ]

    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        self._first_load = True

    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._process_name__hash = {
                'hmi.cfsh.need',
                'hmi.cfsh.need_check',
                'hmi.cfsh.accept',
                'hmi.cfsh.decline',
                'hmi.view_can_home',
                'hmi.home',
            }
            self._axis_label__data, self._axis_name__input, self._axis_name__value = self._generate()
            self._config_name__hash = self._generate_config_name__hash()

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._process_name__hash, self._axis_name__input, self._config_name__hash)
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
        for label in self._axis_label__data:
            data = self._axis_label__data[label]
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
        need = app.data.get('hmi.cfsh.need')
        self.ids['hmi.cfsh.accept'].disabled = not need
        self.ids['hmi.cfsh.decline'].disabled = not need
        self.ids['hmi.cf.home_encoder_value_recorded'].state = (
            'down' if app.data.get('hmi.cf.home_encoder_value_recorded') else 'normal')
        self.ids['hmi.home'].disabled = not app.data.get('hmi.view_can_home')
        self._value_update_axis()

    def _value_update_axis(self):
        app = App.get_running_app()
        for name in self._axis_name__input:
            input = self._axis_name__input[name]
            if input.focus:
                continue
            block = app.data.block(name)
            value = self._axis_name__value[name]
            if value == block.value:
                continue
            self._axis_name__value[name] = block.value
            if block.type == ua.VariantType.Boolean:
                input.v_value_set(block.value == 1)
            else:
                input.v_value_set(block.value)

    def _generate_config_name__hash(self):
        result = set()
        app = App.get_running_app()
        all_name = app.data.all_name_get()
        for name in all_name:
            if '.cf.' in name:
                result.add(name)
        return result

    def _generate(self):
        app = App.get_running_app()
        axis_label__data, axis_name__input, axis_name__value = {}, {}, {}
        axis_type__color = {
            'x': kivy.utils.get_color_from_hex('#ff4444ff'),
            'y': kivy.utils.get_color_from_hex('#95fe54ff'),
            'z': kivy.utils.get_color_from_hex('#526fffff'),
            'a': kivy.utils.get_color_from_hex('#fff644ff'),
        }
        grid = self.ids.grid
        grid.cols = len(ScreenHome.axis_stat)
        grid.rows = len(ScreenHome.axis_list) + 1
        #
        for stat in ScreenHome.axis_stat:
            if stat == None:
                grid.add_widget(Label(
                    text='Servo'
                ))
            else:
                label = Label()
                labelv = stat['label']
                labeld = [' | ' + labelv, 3, 10]
                if len(labelv) <= labeld[2]:
                    label.text = labelv
                    labeld[2] = 0
                axis_label__data[label] = labeld
                grid.add_widget(label)
        #
        for axis in ScreenHome.axis_list:
            for stat in ScreenHome.axis_stat:
                if stat == None:
                    grid.add_widget(Label(
                        text=axis['name'],
                        color=axis_type__color[axis['name'][-1]],
                    ))
                else:
                    input = None
                    name = 'hmi.cf.%s[%d]' % (stat['name'], axis['index'])
                    if app.data.block(name).type == ua.VariantType.Boolean:
                        input = UIBoolInput().data_set(
                            _key_=name,
                            _validate_=self._on_bool_input_validate,
                            _state_text_=['NGHỊCH', 'THUẬN'],
                        )
                    else:
                        input = UITextInputInteger(
                            halign='center',
                            multiline=False
                        ).data_set(
                            _key_=name,
                            _factor_=stat['factor'],
                            _validate_=self._on_text_input_validate,
                            _focus_=None,
                        )
                    axis_name__input[name] = input
                    axis_name__value[name] = None
                    grid.add_widget(input)
        return axis_label__data, axis_name__input, axis_name__value
    
    def _on_bool_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)
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
    
    def _config_path(self, _type_):
        return Path(Path(__file__).resolve().parent.parent, f'config/{_type_}.json')

    def _config_axis_load_confirm(self):
        app = App.get_running_app()
        for t in ['axis', 'machine']:
            config = {}
            path = self._config_path(t)
            if not path.exists():
                print(f'{path} does not exist')
                return
            with path.open(mode='r') as file:
                config = json.load(file)
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
        app = App.get_running_app()
        machine = set()
        for k in self._config_name__hash:
            if k not in self._axis_name__input:
                machine.add(k)
        for t in [['axis', self._axis_name__input], ['machine', machine]]:
            config = {}
            for name in t[1]:
                block = app.data.block(name)
                if block.type == ua.VariantType.Boolean:
                    config[name] = block.value == 1
                else:
                    config[name] = block.value
            with open(self._config_path(t[0]), 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=3)

    def _config_axis_save(self):
        app = App.get_running_app()
        app.helper.show_popup_confirm(
            _message_='LƯU DỮ LIỆU VÀO HMI?',
            _confirm_=self._config_axis_save_confirm
        )