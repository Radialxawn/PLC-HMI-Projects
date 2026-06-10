from kivy.uix.screenmanager import Screen

class PopupConfirm(Screen):
    def __init__(self, _instance_, _confirm_, **kwargs):
        super().__init__(**kwargs)
        self.instance = _instance_
        self.confirm = _confirm_

    def on_confirm(self):
        self.confirm()
        self.instance.dismiss()

    def on_cancel(self):
        self.instance.dismiss()