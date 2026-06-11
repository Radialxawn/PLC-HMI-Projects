from kivy.uix.boxlayout import BoxLayout
from pathlib import Path

class PopupFile(BoxLayout):
    def __init__(self, _instance_, _callback_, **kwargs):
        super().__init__(**kwargs)
        self._instance = _instance_
        self._callback = _callback_
        cnc_path = Path.home() / 'Desktop/CNC'
        if not cnc_path.exists():
            cnc_path.mkdir(parents=True, exist_ok=True)
        self.ids.chooser.rootpath = str(cnc_path)
        self.ids.warn.opacity = 0.0
        self.ids.ok.disabled = True

    def _select(self, *args):
        paths = args[1]
        is_file = len(paths) > 0
        self.ids.ok.disabled = not is_file
        if is_file:
            self._select_path = paths[0]
            size_mb = Path(self._select_path).stat().st_size / (1024 * 1024)
            if size_mb >= 1.0:
                self.ids.ok.disabled = True
                self.ids.warn.opacity = 1.0
                self.ids.warn.text = f'TỆP PHẢI NHỎ HƠN 1MB'
    
    def _confirm(self):
        self._callback(self._select_path)
        self._instance.dismiss()