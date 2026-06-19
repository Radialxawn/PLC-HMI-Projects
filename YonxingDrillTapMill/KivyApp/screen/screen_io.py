from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
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
            self._name__button, self._name_view__toggle, self._io_name__toggle = self._generate()

    def _generate(self):
        name__button_data = {
            '0': None,
            '1': None,
            '2': None,
            'hmi.run_pump':          {'label': 'BƠM'},
            'hmi.run_spindles[0]':   {'label': 'SPINDLE 1'},
            'hmi.run_spindles[1]':   {'label': 'SPINDLE 2'},
            'hmi.run_spindles[2]':   {'label': 'SPINDLE 3'},
            'hmi.run_spindles[3]':   {'label': 'SPINDLE 4'},
            'hmi.run_air_bursts[0]': {'label': 'XỊT KHÍ 1'},
            'hmi.run_air_bursts[1]': {'label': 'XỊT KHÍ 2'},
            'hmi.run_air_bursts[2]': {'label': 'XỊT KHÍ 3'},
            'hmi.run_air_bursts[3]': {'label': 'XỊT KHÍ 4'},
            'hmi.run_air_bursts[4]': {'label': 'XỊT KHÍ 5'},
            'hmi.run_air_bursts[5]': {'label': 'XỊT KHÍ 6'},
            '3': None,
            '4': None,
        }
        name__button = {}
        name_view__toggle = {}
        for name in name__button_data:
            button_data = name__button_data[name]
            if button_data == None:
                self.ids.process.add_widget(Widget())
                continue
            button, toggle = self._generate_button(name, name.replace('hmi.', 'hmi.view_'), button_data['label'], self.ids.process)
            name__button[name] = button
            name_view__toggle[button.name_view] = toggle
        io_name__toggle = {}
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
            io_name__toggle[f'hmi.view_input[{i}]'] = toggle
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
            io_name__toggle[f'hmi.view_output[{i}]'] = toggle
        return name__button, name_view__toggle, io_name__toggle
    
    def _generate_toggle(self, _label_, _bit_, _parent_):
        box = BoxLayout(
            orientation='horizontal',
            spacing=5
        )
        toggle = ToggleButton(
            text=_bit_,
            size_hint_x = 0.2
        )
        label = Label(
            text=_label_,
            halign='left',
            valign='center'
        )
        label.bind(size=label.setter('text_size'))
        box.add_widget(toggle)
        box.add_widget(Widget(size_hint_x=0.05))
        box.add_widget(label)
        _parent_.add_widget(box)
        return toggle

    def _generate_button(self, _name_, _name_view_, _label_, _parent_):
        box = BoxLayout(
            orientation='horizontal',
            spacing=5
        )
        button = Button(
            size_hint_x = 0.5
        )
        button.name = _name_
        button.name_view = _name_view_
        button.bind(on_press=self._on_button_press)
        button.bind(on_release=self._on_button_release)
        toggle = ToggleButton(
            size_hint_x = 0.1
        )
        label = Label(
            text=_label_,
            halign='left',
            valign='center'
        )
        label.bind(size=label.setter('text_size'))
        box.add_widget(button)
        box.add_widget(toggle)
        box.add_widget(Widget(size_hint_x=0.05))
        box.add_widget(label)
        _parent_.add_widget(box)
        return button, toggle

    def _on_button_press(self, _instance_):
        app = App.get_running_app()
        app.data.set(_instance_.name, True)
    
    def _on_button_release(self, _instance_):
        app = App.get_running_app()
        app.data.set(_instance_.name, False)

    def on_enter(self, *args):
        app = App.get_running_app()
        app.data.block_active(self._name__button, self._name_view__toggle, self._io_name__toggle)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.05)
    
    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')

    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._io_name__toggle:
            toggle = self._io_name__toggle[name]
            block = app.data.block(name)
            value = block.value == True
            toggle.state = 'down' if value else 'normal'
        for name in self._name_view__toggle:
            toggle = self._name_view__toggle[name]
            block = app.data.block(name)
            value = block.value == True
            toggle.state = 'down' if value else 'normal'