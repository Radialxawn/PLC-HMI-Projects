from kivy.uix.screenmanager import Screen

class PopupConfirm(Screen):
    def __init__(self, _instance_, _confirm_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._confirm_ = _confirm_

    def _confirm(self):
        self._confirm_()
        self._instance_.dismiss()

    def _cancel(self):
        self._instance_.dismiss()