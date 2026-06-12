from kivy.uix.boxlayout import BoxLayout
from pathlib import Path

class PopupFile(BoxLayout):
    def __init__(self, _instance_, _folder_, _filter_, _callback_, **kwargs):
        super().__init__(**kwargs)
        self._instance = _instance_
        self._callback = _callback_
        folder = f'Desktop/{_folder_}'
        rootpath = Path.home() / folder
        if not rootpath.exists():
            rootpath.mkdir(parents=True, exist_ok=True)
        self.ids.chooser.rootpath = str(rootpath)
        self.ids.chooser.filters = _filter_
        self.ids.warn.opacity = 0.0
        self.ids.ok.disabled = True
        self.ids.warn.text = f'TỆP PHẢI NHỎ HƠN 1MB'

    def _select(self, *args):
        paths = args[1]
        is_file = len(paths) > 0
        if is_file:
            self._select_path = paths[0]
            size_mb = Path(self._select_path).stat().st_size / (1024 * 1024)
            if size_mb >= 1.0:
                self.ids.ok.disabled = True
                self.ids.warn.opacity = 1.0
            else:
                self.ids.ok.disabled = False
                self.ids.warn.opacity = 0.0
        else:
            self.ids.ok.disabled = True
            self.ids.warn.opacity = 0.0
    
    def _confirm(self):
        self._callback(self._select_path)
        self._instance.dismiss()