import json
import kivy.utils
from asyncua import ua
from kivy.app import App
from pathlib import Path
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

class ScreenSettingAdvanced(Screen):
    def __init__(self, **kvargs):
        super(ScreenSettingAdvanced, self).__init__(**kvargs)
        self._axiss_name__index = {
            'R-x':     0,
            'RM-V-y':  2,
            'RM-V-z':  1,
            'RM-H-y':  3,
            'RM-H-z':  4,
            'L-x':     5,
            'LDT-V-y': 7,
            'LD-V-z':  6,
            'LD-L-z':  10,
            'LT-V-z':  8,
            'LT-V-a':  9,
            'LT-L-z':  11,
            'LT-L-a':  12,
        }
        self._axis_propertys = [
            'max_rpm',
            'gear_num',
            'gear_den',
            'gear_dir',
            'home_torque_mNm',
            'home_encoder_value',
            'max_micro',
            'overload_hold_torque_factor',
            'overload_hold_torque_time_msec',
            'overload_instant_torque_factor',
            'ramp_time_msec',
            'jerk_factor',
        ]
        self._grid_draw_done = False

    def on_pre_enter(self, *args):
        if not self._grid_draw_done:
            self._label__data = {}
            self._name__input = {}
            self._grid_draw()
            self._grid_draw_done = True

    def on_enter(self, *args):
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
            if input.is_focus:
                continue
            block = app.data.name__block[name]
            if block.type == ua.VariantType.Boolean:
                value = block.value == 1
                input.state = 'down' if value else 'normal'
                input.text = 'THUẬN' if value else 'NGHỊCH'
            else:
                input.text = f'{block.value}' if block.value != None else ''
        need = app.data.name__block['hmi.cfsh.need'].value
        self.ids['hmi.cfsh.accept'].disabled = not need
        self.ids['hmi.cfsh.decline'].disabled = not need
        self.ids['hmi.cf.home_encoder_value_recorded'].state = (
            'down' if app.data.name__block['hmi.cf.home_encoder_value_recorded'].value else 'normal')
        self.ids['hmi.home'].disabled = not app.data.name__block['hmi.view_can_home'].value

    def _grid_draw(self):
        app = App.get_running_app()
        axiss_name = []
        axiss_index = []
        for name in self._axiss_name__index:
            axiss_name.append(name)
            axiss_index.append(self._axiss_name__index[name])
        axis_color = {
            'x': kivy.utils.get_color_from_hex('#ff4444ff'),
            'y': kivy.utils.get_color_from_hex('#95fe54ff'),
            'z': kivy.utils.get_color_from_hex('#526fffff'),
            'a': kivy.utils.get_color_from_hex('#fff644ff'),
        }
        grid = self.ids['grid']
        grid.cols = len(self._axis_propertys) + 1
        grid.rows = len(axiss_name) + 1
        grid.add_widget(Label(
            text='Servo'
        ))
        for p in self._axis_propertys:
            label = Label()
            data = [' | ' + p, 3, 10]
            if len(p) <= data[2]:
                label.text = p
                data[2] = 0
            self._label__data[label] = data
            grid.add_widget(label)
        for i in range(grid.cols):
            for j in range(grid.rows - 1):
                if j == 0:
                    grid.add_widget(Label(
                        text=axiss_name[i],
                        color=axis_color[axiss_name[i][-1]]
                    ))
                else:
                    oinput = None
                    name = 'hmi.cf.%s[%d]' % (self._axis_propertys[j - 1], axiss_index[i])
                    value_type = app.data.name__block[name].type
                    if value_type == ua.VariantType.Boolean:
                        oinput = ToggleButton(
                            text='...',
                            state='normal'
                        )
                        oinput.bind(on_press=self._on_toggle_press)
                    else:
                        oinput = TextInput(
                            hint_text='...',
                            halign='center',
                            input_filter='int',
                            multiline=False
                        )
                        oinput.bind(on_text_validate=self._on_text_input_validate)
                        oinput.bind(focus=self._on_text_input_focus)
                    oinput.name = name
                    oinput.is_focus = False
                    self._name__input[name] = oinput
                    grid.add_widget(oinput)
    
    def _on_toggle_press(self, _instance_):
        app = App.get_running_app()
        value = _instance_.state == 'down'
        app.data.set(_instance_.name, value)
        app.m_save_need_check()
        
    def _on_text_input_validate(self, _instance_):
        app = App.get_running_app()
        app.data.set(_instance_.name, int(_instance_.text))
        app.m_save_need_check()
    
    def _on_text_input_focus(self, _instance_, _value_):
        _instance_.is_focus = _value_
    
    def _on_home_recorded_reset(self):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_='RESET GỐC ENCODER?',
            _confirm_=self._on_home_recorded_reset_confirm)

    def _on_home_recorded_reset_confirm(self):
        app = App.get_running_app()
        app.data.set('hmi.cf.home_encoder_value_recorded', False)
        app.m_save_need_check()
    
    def _config_path(self):
        return Path(Path(__file__).resolve().parent.parent, 'config.json')

    def _config_load_confirm(self):
        config = {}
        app = App.get_running_app()
        path = self._config_path()
        if not path.exists():
            return
        with path.open(mode='r') as file:
            config = json.load(file)
        for name in config:
            value = config[name]
            if value == None:
                continue
            app.data.set(name, value)
        app.m_save_need_check()

    def _config_load(self):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_='LẤY DỮ LIỆU TRÊN HMI?',
            _confirm_=self._config_load_confirm)
    
    def _config_save_confirm(self):
        config = {}
        app = App.get_running_app()
        for name in self._name__input:
            block = app.data.name__block[name]
            if block.type == ua.VariantType.Boolean:
                config[name] = block.value == 1
            else:
                config[name] = block.value
        with open(self._config_path(), 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=3)

    def _config_save(self):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_='LƯU DỮ LIỆU VÀO HMI?',
            _confirm_=self._config_save_confirm)