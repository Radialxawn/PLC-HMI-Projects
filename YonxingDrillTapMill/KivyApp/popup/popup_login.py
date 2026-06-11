from kivy.app import App
from kivy.uix.screenmanager import Screen

class PopupLogin(Screen):
    def __init__(self, _instance_, _password_, _screen_, **kwargs):
        super().__init__(**kwargs)
        self._instance = _instance_
        self._password = _password_
        self._screen = _screen_

    def on_cancel(self):
        self._instance.dismiss()

    def on_confirm(self, _input_):
        if _input_.text == self._password:
            App.get_running_app().root.current = self._screen
            self._instance.dismiss()
        else:
            _input_.text = ''
            _input_.hint_text = 'SAI MẬT KHẨU'