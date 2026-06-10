import kivy.utils
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

class ScreenHome(Screen):
    def __init__(self, **kvargs):
        super(ScreenHome, self).__init__(**kvargs)
        for i in range(6):
            button = self.ids[f'face_{i}']
            button.text = f'FACE-{i}'
            button.face_index = i
    
    def _select_face(self, _instance_):
        app = App.get_running_app()
        face_index = _instance_.face_index
        app.data.set('hmi.face_index', face_index)