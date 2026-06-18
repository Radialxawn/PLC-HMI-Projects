from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

class ScreenIO(Screen):
    def __init__(self, **kvargs):
        super(ScreenIO, self).__init__(**kvargs)
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__toggle = self._generate()

    def _generate(self):
        name__toggle = {}
        input = [
            'TAY QUAY PHA A',
            'TAY QUAY PHA B',
            'CHẠY',
            'DỪNG',
            'TỐC ĐỘ JOG X1',
            'TỐC ĐỘ JOG X10',
            'TỐC ĐỘ JOG X100',
            'TRỤC JOG X',
            'TRỤC JOG Y',
            'TRỤC JOG Z',
            'TRỤC JOG A',
            'TRỤC JOG B',
            'TRỤC JOG C',
            'SO DAO QUÁ HÀNH TRÌNH',
            'SO DAO SPINDLE 1',
            'SO DAO SPINDLE 2',
        ]
        for i in range(16):
            toggle = self._generate_toggle(input[i], f'I-{i:02}', self.ids.input)
            name__toggle[f'hmi.view_input[{i}]'] = toggle
        output = [
            '[KHÔNG SỬ DỤNG]',
            'SPINDLE 1',
            'SPINDLE 2',
            'BƠM TẢN NHIỆT',
            'PHUN KHÍ SPINDLE 1',
            'PHUN KHÍ SPINDLE 2',
            'KHOÁ TRỤC Z 1',
            'KHOÁ TRỤC Z 2',
            'SPINDLE 3',
            'SPINDLE 4',
            'KHOÁ TRỤC Z 3',
            'KHOÁ TRỤC Z 5',
            'PHUN KHÍ SPINDLE 3',
            'PHUN KHÍ SPINDLE 4',
            'PHUN KHÍ TARO 5',
            'PHUN KHÍ TARO 6',
        ]
        for i in range(16):
            toggle = self._generate_toggle(output[i], f'Q-{i:02}', self.ids.output)
            name__toggle[f'hmi.view_output[{i}]'] = toggle
        return name__toggle
    
    def _generate_toggle(self, _namev_, _bit_, _parent_):
        box = BoxLayout(
            orientation='horizontal',
            spacing=5
        )
        toggle = ToggleButton(
            text=_bit_,
            size_hint_x = 0.2
        )
        label = Label(
            text=_namev_,
            halign='left',
            valign='center'
        )
        label.bind(size=label.setter('text_size'))
        box.add_widget(toggle)
        box.add_widget(Widget(size_hint_x=0.05))
        box.add_widget(label)
        _parent_.add_widget(box)
        return toggle

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__toggle)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.05)
    
    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')

    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._name__toggle:
            toggle = self._name__toggle[name]
            block = app.data.block(name)
            value = block.value == True
            toggle.state = 'down' if value else 'normal'