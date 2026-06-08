import functools
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class UI(object):
    def __init__(self, _layout_):
        self.layout = _layout_
        self.name__button = {}
    
    def create(self):
        btn = Button(
            text='Connect',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(0, 0)
            )
        btn.bind(on_press=self.layout.button_connect)
        self.layout.add_widget(btn)
        self.name__button['self.connect'] = btn
        #
        btn = Button(
            text='Disconnect',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(200, 0)
            )
        btn.bind(on_press=self.layout.button_disconnect)
        self.layout.add_widget(btn)
        self.name__button['self.disconnect'] = btn
        #
        self.data = Label(
            font_size=16,
            size_hint=(1, 1),
            )
        self.layout.add_widget(self.data)
        #
        btn = Button(
            text='Run',
            font_size=32,
            size_hint=(None, None),
            size=(100, 50),
            pos=(0, 50)
            )
        btn.bind(on_press=functools.partial(self.layout.button_machine_run, True))
        btn.bind(on_release=functools.partial(self.layout.button_machine_run, False))
        self.layout.add_widget(btn)
        self.name__button['hmi.run'] = btn
        #
        btn = Button(
            text='Stop',
            font_size=32,
            size_hint=(None, None),
            size=(100, 50),
            pos=(100, 50)
            )
        btn.bind(on_press=functools.partial(self.layout.button_machine_stop, True))
        btn.bind(on_release=functools.partial(self.layout.button_machine_stop, False))
        self.layout.add_widget(btn)
        self.name__button['hmi.stop'] = btn
        #
        btn = Button(
            text='Home',
            font_size=32,
            size_hint=(None, None),
            size=(100, 50),
            pos=(200, 50)
            )
        btn.bind(on_press=functools.partial(self.layout.button_machine_home, True))
        btn.bind(on_release=functools.partial(self.layout.button_machine_home, False))
        self.layout.add_widget(btn)
        self.name__button['hmi.home'] = btn
        #
        self.button_face_indexs = []
        for i in range(6):
            btn = Button(
                text=f'Face {i}',
                font_size=32,
                size_hint=(None, None),
                size=(100, 50),
                pos=(i * 100, 100)
                )
            btn.bind(on_press=functools.partial(self.layout.button_machine_face, i))
            self.button_face_indexs.append(btn)
            self.layout.add_widget(btn)
        #
        btn = Button(
            text='Download',
            font_size=32,
            size_hint=(None, None),
            size=(200, 50),
            pos=(400, 0)
            )
        btn.bind(on_press=self.layout.button_download)
        self.layout.add_widget(btn)
        self.name__button['self.download'] = btn