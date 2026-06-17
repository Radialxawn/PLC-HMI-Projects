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
            self._name__hash = {
                'hmi.cfsh.need',
                'hmi.cfsh.need_check',
                'hmi.cfsh.accept',
                'hmi.cfsh.decline',
            }
        app = App.get_running_app()
        app.data.block_active(self._name__hash)

    def on_enter(self, *args):
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.2)

    def on_leave(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')

    def _value_update(self, _dt_):
        app = App.get_running_app()