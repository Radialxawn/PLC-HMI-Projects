from kivy.app import App
from kivy.uix.screenmanager import Screen

class PopupLogin(Screen):
    def __init__(self, _instance_, _password_, _screen_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._password_ = _password_
        self._screen_ = _screen_

    def _cancel(self):
        self._instance_.dismiss()

    def _confirm(self, _input_):
        if _input_.text == self._password_:
            App.get_running_app().root.current = self._screen_
            self._instance_.dismiss()
        else:
            _input_.text = ''
            _input_.hint_text = 'SAI MẬT KHẨU'