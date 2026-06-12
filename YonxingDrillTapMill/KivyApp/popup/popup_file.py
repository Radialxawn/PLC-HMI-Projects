from kivy.uix.boxlayout import BoxLayout
from pathlib import Path

class PopupFile(BoxLayout):
    def __init__(self, _instance_, _folder_, _filter_, _select_, **kwargs):
        super().__init__(**kwargs)
        self._instance_ = _instance_
        self._select_ = _select_
        self.ids.chooser.rootpath = str(PopupFile.path_get(_folder_))
        self.ids.chooser.filters = _filter_
        self.ids.warn.opacity = 0.0
        self.ids.ok.disabled = True
        self.ids.warn.text = f'TỆP PHẢI NHỎ HƠN 1MB'

    @staticmethod
    def path_get(_folder_):
        folder = f'Desktop/{_folder_}'
        rootpath = Path.home() / folder
        if not rootpath.exists():
            rootpath.mkdir(parents=True, exist_ok=True)
        return rootpath

    def _select(self, *args):
        paths = args[1]
        is_file = len(paths) > 0
        if is_file:
            self._select_path = Path(paths[0])
            size_mb = self._select_path.stat().st_size / (1024 * 1024)
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
        self._select_(self._select_path)
        self._instance_.dismiss()
    
    def _cancel(self):
        self._instance_.dismiss()