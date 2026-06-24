from kivy.uix.popup import Popup

class PopupConfirm(Popup):
    def set_data(self, _confirm_, _dismiss_):
        self._confirm_ = _confirm_
        self._dismiss_ = _dismiss_
        return self

    def _confirm(self):
        self._confirm_()
        self.dismiss()

    def _cancel(self):
        self.dismiss()
    
    def on_dismiss(self):
        self._dismiss_()
        return super().on_dismiss()