from kivy.uix.popup import Popup

class PopupConfirm(Popup):
    def set_data(self, _confirm_, _dismiss_, _password_):
        self._confirm_ = _confirm_
        self._dismiss_ = _dismiss_
        self._password_ = _password_
        if _password_ == None:
            self._widget_remove(self.ids.password)
        return self

    def _widget_remove(self, _instance_):
        if _instance_.parent:
            _instance_.parent.remove_widget(_instance_)

    def _confirm(self):
        if self._password_ != None:
            password = self.ids.password
            if password.text != self._password_:
                password.text = ''
                password.hint_text = 'SAI MẬT KHẨU'
                return
        self._confirm_()
        self.dismiss()

    def _cancel(self):
        self.dismiss()
    
    def on_dismiss(self):
        self._dismiss_()
        return super().on_dismiss()