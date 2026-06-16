from kivy.uix.screenmanager import Screen

class PopupError(Screen):
    def __init__(self, _instance_, _acknowledge_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._acknowledge_ = _acknowledge_
        self.ids.acknowledge.opacity = 0 if _acknowledge_ == None else 1
        self.ids.acknowledge.disabled = _acknowledge_ == None

    def _acknowledge(self):
        self._acknowledge_()
        self._instance_.dismiss()

    def _exit(self):
        self._instance_.dismiss()