from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex as clhex

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
    
    def progress(self, _value_):
        self.ids.bar.value = _value_
        if _value_ == 101:
            self.ids.cancel.disabled = True
            self.ids.state.opacity = 1.0
            self.ids.state.text = 'XONG'
            self.ids.state.color = clhex('#95fe54ff')
            Clock.schedule_once(lambda _: self._instance_.dismiss(), 1.0)
        if _value_ == -1:
            self.ids.state.opacity = 1.0
            self.ids.state.text = 'THẤT BẠI'
            self.ids.state.color = clhex("#fe5454ff")