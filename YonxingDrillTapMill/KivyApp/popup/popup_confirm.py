from kivy.uix.screenmanager import Screen

class PopupConfirm(Screen):
    def __init__(self, _instance_, _confirm_, **kwargs):
        super().__init__(**kwargs)
        self._instance = _instance_
        self._confirm = _confirm_

    def _confirm(self):
        self._confirm()
        self._instance.dismiss()

    def _cancel(self):
        self._instance.dismiss()