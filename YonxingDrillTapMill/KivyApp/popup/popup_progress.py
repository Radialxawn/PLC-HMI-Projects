from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex as clhex

class PopupProgress(Popup):
    def set_data(self, _cancel_):
        self._cancel_ = _cancel_
        self.ids.bar.value = 0
        self.ids.cancel.disabled = False
        self.ids.state.opacity = 0.0
        return self

    def _cancel(self):
        self._cancel_()
        self.dismiss()
    
    def progress(self, _value_):
        self.ids.bar.value = _value_
        if _value_ == 101:
            self.ids.cancel.disabled = True
            self.ids.state.opacity = 1.0
            self.ids.state.text = 'XONG'
            self.ids.state.color = clhex('#95fe54ff')
            Clock.schedule_once(lambda _: self.dismiss(), 1.0)
        if _value_ == -1:
            self.ids.state.opacity = 1.0
            self.ids.state.text = 'THẤT BẠI'
            self.ids.state.color = clhex("#fe5454ff")