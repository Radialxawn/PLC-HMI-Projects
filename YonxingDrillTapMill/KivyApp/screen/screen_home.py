import kivy.utils
import tkinter as tk
from tkinter import filedialog
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from popup.popup_file import PopupFile

class ScreenHome(Screen):
    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        for i in range(6):
            button = self.ids[f'face_{i}']
            button.text = f'FACE-{i+1}'
            button.face_index = i
        for i in range(6):
            button = self.ids[f'cnc_{i}']
            button.text = f'CNC-{i+1}'
            button.cnc_index = i
    
    def _select_face(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)
    
    def _download_cnc_select(self, _instance_):
        popup = Popup(
            title='CHỌN TỆP CNC',
            size_hint=(0.8, 0.8),
            auto_dismiss=True
        )
        self.cnc_index = _instance_.cnc_index
        popup.content = PopupFile(popup, _folder_='CNC', _filter_=['*.cnc'], _callback_=self._download_cnc)
        popup.open()
    
    def _download_cnc(self, _source_path_):
        app = App.get_running_app()
        app.data.download_start(
            _source_path_=_source_path_,
            _destination_index_=self.cnc_index,
            _progress_=self._download_cnc_bar
        )

    def _download_cnc_bar(self, _value_):
        self.ids.cnc_bar.value = _value_
        if _value_ == 100:
            self.ids.cnc_state.opacity = 1.0
        else:
            self.ids.cnc_state.opacity = 0.0