import time
import json
from pathlib import Path
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

class ScreenLoad(Screen):
    def __init__(self, **kvargs):
        super(ScreenLoad, self).__init__(**kvargs)
        self._first_load = True
    
    def on_enter(self, *args):
        self.skip = False
        threading.Thread(target=self._perform_heavy_task, daemon=True).start()

    def _config_machine_load(self):
        path = Path(Path(__file__).resolve().parent.parent, 'config/machine.json')
        if not path.exists():
            raise Exception('No machine config')
        with path.open(mode='r') as file:
            return json.load(file)

    def _perform_heavy_task(self):
        app = App.get_running_app()
        if self._first_load:
            self._first_load = False
            app.data.create()
            app.auto_connect_start()
            app.machine = self._config_machine_load()
        for i in range(100):
            if self.skip:
                break
            time.sleep(0.01)
            Clock.schedule_once(lambda _, p=i+1: self._update_progress(p))
        Clock.schedule_once(self._transition_to_main)

    def _update_progress(self, _value_):
        self.ids.progress_bar.value = _value_
        self.ids.loading_label.text = f"{_value_}%"

    def _transition_to_main(self, _dt_):
        self.manager.current = "home"
    
    def _skip(self):
        self.skip = True