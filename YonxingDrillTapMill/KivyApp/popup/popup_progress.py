from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

class PopupProgress(Screen):
    def __init__(self, _instance_, _cancel_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._cancel_ = _cancel_
        self.ids.bar.value = 0
        self.ids.cancel.disabled = False
        self.ids.state.opacity = 0.0

    def _cancel(self):
        self._cancel_()
        self._instance_.dismiss()
    
    def update(self, _value_):
        self.ids.bar.value = _value_
        if _value_ == 101:
            self.ids.cancel.disabled = True
            self.ids.state.opacity = 1.0
            Clock.schedule_once(lambda _: self._instance_.dismiss(), 0.5)