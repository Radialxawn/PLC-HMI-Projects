import time
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

class ScreenLoad(Screen):
    def __init__(self, **kvargs):
        super(ScreenLoad, self).__init__(**kvargs)
    
    def on_enter(self, *args):
        threading.Thread(target=self.perform_heavy_task, daemon=True).start()

    def perform_heavy_task(self):
        app = App.get_running_app()
        app.data.create()
        for i in range(100):
            time.sleep(0.001)
            Clock.schedule_once(lambda dt, p=i+1: self.update_progress(p))
        Clock.schedule_once(self.transition_to_main)

    def update_progress(self, _value_):
        self.ids.progress_bar.value = _value_
        self.ids.loading_label.text = f"{_value_}%"

    def transition_to_main(self, dt):
        self.manager.current = "home"