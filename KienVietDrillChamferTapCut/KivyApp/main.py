# fucking corsair mouse slow down the fucking program load process
from kivy.config import Config
Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '540')
Config.set('graphics', 'minimum_width', '960')
Config.set('graphics', 'minimum_height', '540')
Config.set('graphics', 'multisamples', '4')
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', '0')
import sys
import logging
import platform
from pathlib import Path
from kivy.app import App
from core.data import Data
from kivy.clock import Clock
from kivy.lang import Builder
from core.launcher import Launcher
from kivy.core.window import Window
from screen.screen_home import ScreenHome
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from screen.screen_load import ScreenLoad
from core.helper import Helper

Builder.load_file('screen/screen_load.kv')
Builder.load_file('screen/screen_home.kv')
Builder.load_file('popup/popup_confirm.kv')

class Main(App):
    def build(self):
        self.launcher = Launcher()
        parameters = sys.argv[1:]
        if len(parameters) > 0:
            match parameters[0]:
                case 'offline':
                    self.launcher.offline = True
                    print('Run offline mode')
        self._log_mode()
        self.data = Data(
            _address_ip_='192.168.2.3', _address_port_=4840,
            _xml_path_windows_=Path(f'../MC500/MC500.Device.Application.xml'),
            _tag_head_='ns=4;s=|var|LS'
        )
        self.helper = Helper()
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(ScreenLoad(name='load'))
        sm.add_widget(ScreenHome(name='home'))
        return sm

    def _log_mode(self):
        for k in logging.root.manager.loggerDict:
            if 'asyncua' in k:
                logger = logging.getLogger(k)
                logger.setLevel(level=logging.CRITICAL)

    def on_start(self):
        if platform.system() == 'Linux':
            Window.maximize()

    def on_stop(self):
        self.data.disconnect()
    
    def auto_connect_start(self):
        self._auto_connect_clock = Clock.schedule_interval(self._auto_connect, 0.5)

    def _auto_connect(self, _dt_):
        if self.data.can_connect():
            if self.data.connect_state() == 0:
                self.data.connect(0.010, 32)
        else:
            if self.data.connect_state() == 100:
                self.data.disconnect()

if __name__ == '__main__':
    Main().run()