import logging
from _data import Data
from _download import Download
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from screen.screen_load import ScreenLoad
from screen.screen_home import ScreenHome
from screen.screen_setting import ScreenSetting
from screen.screen_io import ScreenIO
from screen.screen_setting_advanced import ScreenSettingAdvanced

Builder.load_file('screen/screen_load.kv')
Builder.load_file('screen/screen_home.kv')
Builder.load_file('screen/screen_io.kv')
Builder.load_file('screen/screen_setting.kv')
Builder.load_file('screen/screen_setting_advanced.kv')

class Main(App):
    def build(self):
        self._log_mode()
        self.data = Data(
            _address_ip_='192.168.2.3', _address_port_=4840,
            _xml_path_windows_=r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml',
            _tag_head_='ns=4;s=|var|LS'
        )
        self.download = Download(self.data)
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(ScreenLoad(name='load'))
        sm.add_widget(ScreenHome(name='home'))
        sm.add_widget(ScreenIO(name='io'))
        sm.add_widget(ScreenSetting(name='setting'))
        sm.add_widget(ScreenSettingAdvanced(name='setting_advanced'))
        return sm

    def _log_mode(self):
        for k in logging.root.manager.loggerDict:
            if 'asyncua' in k:
                logger = logging.getLogger(k)
                logger.setLevel(level=logging.CRITICAL)

    def on_stop(self):
        self.data.disconnect()
    
    def save_accept(self):
        print('Save accept')
    
    def save_decline(self):
        print('Save decline')

if __name__ == '__main__':
    Main().run()