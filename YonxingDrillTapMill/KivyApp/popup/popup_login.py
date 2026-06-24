from kivy.app import App
from kivy.uix.popup import Popup

class PopupLogin(Popup):
    def set_data(self, _password_, _screen_, _dismiss_):
        self._password_ = _password_
        self._screen_ = _screen_
        self._dismiss_ = _dismiss_
        return self

    def _cancel(self):
        self.dismiss()

    def _confirm(self, _input_):
        if _input_.text == self._password_:
            App.get_running_app().root.current = self._screen_
            self.dismiss()
        else:
            _input_.text = ''
            _input_.hint_text = 'SAI MẬT KHẨU'
    
    def _password_on_text(self, _input_):
        if _input_.text == self._password_:
            App.get_running_app().root.current = self._screen_
            self.dismiss()
    
    def on_dismiss(self):
        self._dismiss_()
        return super().on_dismiss()