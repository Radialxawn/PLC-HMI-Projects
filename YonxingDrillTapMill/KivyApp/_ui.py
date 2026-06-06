import functools
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class UI(object):
    def __init__(self, _layout_):
        self.layout = _layout_
    
    def create(self):
        self.connect = Button(
            text='Connect',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(0, 0)
            )
        self.connect.bind(on_press=self.layout.button_connect)
        self.layout.add_widget(self.connect)
        #
        self.disconnect = Button(
            text='Disconnect',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(200, 0)
            )
        self.disconnect.bind(on_press=self.layout.button_disconnect)
        self.layout.add_widget(self.disconnect)
        #
        self.data = Label(
            font_size=16,
            size_hint=(1, 1),
            )
        self.layout.add_widget(self.data)
        #
        self.button_machine_run = Button(
            text='Run',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(0, 50)
            )
        self.button_machine_run.bind(on_press=functools.partial(self.layout.button_machine_run, True))
        self.button_machine_run.bind(on_release=functools.partial(self.layout.button_machine_run, False))
        self.layout.add_widget(self.button_machine_run)
        #
        self.button_machine_stop = Button(
            text='Stop',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(200, 50)
            )
        self.button_machine_stop.bind(on_press=functools.partial(self.layout.button_machine_stop, True))
        self.button_machine_stop.bind(on_release=functools.partial(self.layout.button_machine_stop, False))
        self.layout.add_widget(self.button_machine_stop)
        #
        self.button_download = Button(
            text='Download',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(400, 0)
            )
        self.button_download.bind(on_press=self.layout.button_download)
        self.layout.add_widget(self.button_download)