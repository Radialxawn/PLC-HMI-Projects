from kivy.uix.popup import Popup

class PopupError(Popup):
    def set_data(self, _acknowledge_):
        self._acknowledge_ = _acknowledge_
        self.ids.acknowledge.opacity = 0 if _acknowledge_ == None else 1
        self.ids.acknowledge.disabled = _acknowledge_ == None
        return self

    def _acknowledge(self):
        self._acknowledge_()
        self.dismiss()

    def _exit(self):
        self.dismiss()