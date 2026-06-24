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
from kivy.utils import get_color_from_hex as clhex

class ScreenSetting(Screen):
    name__data = {
        'left': None,
        '1': 0,
        'hmi.cf.rapid_micro_per_sec':  {'label': 'TỐC ĐỘ TỊNH TIẾN (mm/s)', 'type': 'rw', 'factor': 1e-3},
        'hmi.cf.tap_micro_per_rev[0]': {'label': 'BƯỚC REN TARO ĐỨNG',      'type': 'rw', 'factor': 1e-3},
        'hmi.cf.tap_micro_per_rev[1]': {'label': 'BƯỚC REN TARO NGHIÊNG',   'type': 'rw', 'factor': 1e-3},
        '2': 0,
        'hmi.cf.tool_z_ox_micro[0]':   {'label': 'X CẢM BIẾN DAO ĐỨNG',     'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_oy_micro[0]':   {'label': 'Y CẢM BIẾN DAO ĐỨNG',     'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_base_micro[0]': {'label': 'Z DAO ĐỨNG CHUẨN',        'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_micro[0]':      {'label': 'Z DAO ĐỨNG',              'type': 'ro', 'factor': -1e-3},
        '3': 0,
        'hmi.cf.tool_z_ox_micro[1]':   {'label': 'X CẢM BIẾN DAO NGANG',    'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_oy_micro[1]':   {'label': 'Y CẢM BIẾN DAO NGANG',    'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_base_micro[1]': {'label': 'Z DAO NGANG CHUẨN',       'type': 'rw', 'factor': -1e-3},
        'hmi.cf.tool_z_micro[1]':      {'label': 'Z DAO NGANG',             'type': 'ro', 'factor': -1e-3},
        '4': 0,
        'right': None,
        '101': 0,
        'hmi.cf.air_burst_delay_msec[0]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 1', 'type': 'rw', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[1]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 2', 'type': 'rw', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[2]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 3', 'type': 'rw', 'factor': 1e-3},
        '102': 0,
        'hmi.cf.air_burst_delay_msec[3]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 4', 'type': 'rw', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[4]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 5', 'type': 'rw', 'factor': 1e-3},
        'hmi.cf.air_burst_delay_msec[5]': {'label': 'THỜI GIAN XỊT KHÍ MẶT 6', 'type': 'rw', 'factor': 1e-3},
        '103': 0,
        '104': 0,
        'hmi.view_axis_tmp_micro[0]': {'label': 'VỊ TRÍ TRỤC X MẶT {}', 'type': 'ro', 'factor': -1e-3},
        'hmi.view_axis_tmp_micro[1]': {'label': 'VỊ TRÍ TRỤC Y MẶT {}', 'type': 'ro', 'factor': -1e-3},
        '105': 0,
        '106': 0,
        '107': 0,
    }

    def __init__(self, **kvargs):
        super(ScreenSetting, self).__init__(**kvargs)
        self._face_index = -1
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            app = App.get_running_app()
            for i in range(len(app.machine.index__face)):
                button = self.ids[f'face_{i}']
                button.text = f'MẶT {i+1}'
                button.face_index = i
            self._name__hash = {
                'hmi.cfsh.need',
                'hmi.cfsh.need_check',
                'hmi.cfsh.accept',
                'hmi.cfsh.decline',
                'hmi.view_can_home',
                'hmi.home',
                'hmi.face_index',
                'hmi.run_tool_setter',
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
                orientation='horizontal'
            )
            label = Label(
                text=data['label'],
                halign='left',
                valign='center'
            )
            label.bind(size=label.setter('text_size'))
            input = UITextInputInteger(
                halign='center',
                multiline=False
            ).data_set(
                _key_=name,
                _factor_=data['factor'],
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            input.disabled = data['type'] == 'ro'
            input.v_label = label
            name__input[name] = input
            name__value[name] = None
            box.add_widget(label)
            box.add_widget(input)
            side.add_widget(box)
        return name__input, name__value

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__hash, self._name__input)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')

    def _on_text_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)
        app.helper.save_need_check()

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
        face_index = app.data.get('hmi.face_index')
        if face_index != None and face_index != self._face_index:
            self._face_index = face_index
            for i in range(len(app.machine.index__face)):
                color = clhex("#6AA145") if face_index == i else clhex("#5F5F5F")
                self.ids[f'face_{i}'].background_color = color
            for i in range(2):
                name = f'hmi.view_axis_tmp_micro[{i}]'
                data = ScreenSetting.name__data[name]
                self._name__input[name].v_label.text = data['label'].format(face_index + 1)
    
    def _face_select(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
    
    def _run_tool_setter(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.run_tool_setter', _value_)