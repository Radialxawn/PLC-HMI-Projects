from kivy.uix.boxlayout import BoxLayout
from pathlib import Path

class PopupFile(BoxLayout):
    def __init__(self, _callback_, **kwargs):
        super().__init__(**kwargs)
        cnc_path = Path.home() / 'Desktop/CNC'
        if not cnc_path.exists():
            cnc_path.mkdir(parents=True, exist_ok=True)
        self.ids.chooser.rootpath = str(cnc_path)
        self._callback = _callback_

    def _select(self, *args):
        paths = args[1]
        if len(paths) <= 0:
            return
        self._callback(paths[0])