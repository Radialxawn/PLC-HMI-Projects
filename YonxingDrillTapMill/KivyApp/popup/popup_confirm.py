from kivy.uix.popup import Popup

class PopupConfirm(Popup):
    def set_data(self, _confirm_):
        self._confirm_ = _confirm_
        return self

    def _confirm(self):
        self._confirm_()
        self.dismiss()

    def _cancel(self):
        self.dismiss()