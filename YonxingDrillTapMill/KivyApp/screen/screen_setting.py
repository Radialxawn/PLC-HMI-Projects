from asyncua import ua
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from core.ui import UI, UITextInputInteger

class ScreenSetting(Screen):
    name__data = {
        'left': None,
        '0': 0,
        '1': 0,
        'hmi.cf.rapid_micro_per_sec':  {'namev': 'TỐC ĐỘ TỊNH TIẾN (mm/s)', 'factor': 1e-3},
        'hmi.cf.tap_micro_per_rev[0]': {'namev': 'BƯỚC REN TARO ĐỨNG',      'factor': 1e-3},
        'hmi.cf.tap_micro_per_rev[1]': {'namev': 'BƯỚC REN TARO NGHIÊNG',   'factor': 1e-3},
        '2': 0,
        'hmi.cf.tool_z_ox_micro[0]':   {'namev': 'X DAO ĐỨNG',              'factor': 1e-3},
        'hmi.cf.tool_z_oy_micro[0]':   {'namev': 'Y DAO ĐỨNG',              'factor': 1e-3},
        'hmi.cf.tool_z_base_micro[0]': {'namev': 'Z CHUẨN DAO ĐỨNG',        'factor': 1e-3},
        'hmi.cf.tool_z_micro[0]':      {'namev': 'Z DAO ĐỨNG',              'factor': 1e-3},
        '3': 0,
        'hmi.cf.tool_z_ox_micro[1]':   {'namev': 'X DAO NGANG',             'factor': 1e-3},
        'hmi.cf.tool_z_oy_micro[1]':   {'namev': 'X DAO NGANG',             'factor': 1e-3},
        'hmi.cf.tool_z_base_micro[1]': {'namev': 'Z CHUẨN DAO NGANG',       'factor': 1e-3},
        'hmi.cf.tool_z_micro[1]':      {'namev': 'Z DAO NGANG',             'factor': 1e-3},
        '4': 0,
        'right': None,
        '100': 0,
        '101': 0,
        'hmi.cf.air_burst_delay_msec[0]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 1', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[1]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 2', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[2]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 3', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[3]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 4', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[4]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 5', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[5]': {'namev': 'THỜI GIAN XỊT KHÍ MẶT 6', 'factor': 1e-3},
        '102': 0,
        '103': 0,
        '104': 0,
        '105': 0,
        '106': 0,
        '107': 0,
        '108': 0,
        '109': 0,
    }

    def __init__(self, **kvargs):
        super(ScreenSetting, self).__init__(**kvargs)
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__hash = {
                'hmi.cfsh.need',
                'hmi.cfsh.need_check',
                'hmi.cfsh.accept',
                'hmi.cfsh.decline',
                'hmi.view_can_home',
                'hmi.home',
            }
            self._name__input, self._name__value = self._generate()

    def _generate(self):
        name__input, name__value = {}, {}
        side = None
        for name in ScreenSetting.name__data:
            data = ScreenSetting.name__data[name]
            if data == None:
                match name:
                    case 'left':
                        side = self.ids.left
                    case 'right':
                        side = self.ids.right
                continue
            if data == 0:
                side.add_widget(Widget())
                continue
            box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,
            )
            label = Label(
                text=data['namev'],
                halign='left',
                valign='center'
            )
            label.bind(size=label.setter('text_size'))
            box.add_widget(label)
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
            box.add_widget(input)
            side.add_widget(box)
        return name__input, name__value

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__hash, self._name__input)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.2)

    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')

    def _on_text_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)
        app.m_save_need_check()

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
            else:
                input.v_value_set(block.value)
        need = app.data.get('hmi.cfsh.need')
        self.ids['hmi.cfsh.accept'].disabled = not need
        self.ids['hmi.cfsh.decline'].disabled = not need
        self.ids['hmi.home'].disabled = not app.data.get('hmi.view_can_home')