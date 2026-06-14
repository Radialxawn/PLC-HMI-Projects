from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

class ScreenSetting(Screen):
    def __init__(self, **kvargs):
        super(ScreenSetting, self).__init__(**kvargs)
        self._first_load = True
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            name__hash = {}
            name__hash['hmi.cfsh.need'] = False
            name__hash['hmi.cfsh.need_check'] = False
            name__hash['hmi.cfsh.accept'] = False
            name__hash['hmi.cfsh.decline'] = False
            self._name__hash = name__hash
        app = App.get_running_app()
        for name in app.data.name__block:
            app.data.name__block[name].active = name in self._name__hash

    def on_enter(self, *args):
        return

    def on_leave(self, *args):
        return