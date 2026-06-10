from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

class ScreenSettingAdvanced(Screen):
    def __init__(self, **kvargs):
        super(ScreenSettingAdvanced, self).__init__(**kvargs)
        t = Button(
            text="Click Me!", 
            size_hint=(None, None), 
            size=(200, 100),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(t)