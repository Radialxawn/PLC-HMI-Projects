import time
import json
import threading
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from types import SimpleNamespace
from kivy.uix.screenmanager import Screen

class ScreenLoad(Screen):
    def __init__(self, **kvargs):
        super(ScreenLoad, self).__init__(**kvargs)
        self._first_load = True
    
    def on_enter(self, *args):
        self.skip = False
        threading.Thread(target=self._perform_heavy_task, daemon=True).start()

    @staticmethod
    def config_machine_load():
        path = Path(Path(__file__).resolve().parent.parent, 'config/_machine.json')
        if not path.exists():
            raise Exception('No machine config')
        with path.open(mode='r') as file:
            machine = json.load(file)
            return SimpleNamespace(**machine)

    def _perform_heavy_task(self):
        app = App.get_running_app()
        if self._first_load:
            self._first_load = False
            app.data.create()
            app.auto_connect_start()
            app.machine = ScreenLoad.config_machine_load()
        while app.data.connect_state() != 100:
            if self.skip:
                break
            time.sleep(0.5)
        state_key = 'hmi.view_state[0]'
        app.data.block_active({state_key})
        state = 0
        while state != 100:
            if self.skip:
                break
            state = app.data.get(state_key)
            state = 0 if state == None else state
            Clock.schedule_once(lambda _: self._update_progress(state))
            time.sleep(0.1)
        Clock.schedule_once(self._transition_to_main)

    def _update_progress(self, _value_):
        self.ids.progress_bar.value = _value_
        self.ids.loading_label.text = f"{_value_}%"

    def _transition_to_main(self, _dt_):
        self.manager.current = "home"
    
    def _skip(self):
        self.skip = True