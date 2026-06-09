from kivy.config import Config
Config.set('kivy', 'log_level', 'warning')
from _data import Data
from _uaclient import UaClient
from _download import Download
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
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

class MainWindow(App):
    def build(self):
        app = App.get_running_app()
        app.uac = UaClient()
        app.data = Data(
            _uac_=app.uac,
            _address_='opc.tcp://192.168.2.3:4840',
            _xml_path_windows_=r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml',
            _tag_head_='ns=4;s=|var|LS'
        )
        app.download = Download(self.uac, self.data)
        app.connect = self.connect
        app.disconnect = self.disconnect
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(ScreenLoad(name='load'))
        sm.add_widget(ScreenHome(name='home'))
        sm.add_widget(ScreenIO(name='io'))
        sm.add_widget(ScreenSetting(name='setting'))
        sm.add_widget(ScreenSettingAdvanced(name='setting_advanced'))
        return sm

    def connect(self, _uri_):
        app = App.get_running_app()
        uri = _uri_.strip()
        try:
            app.uac.connect(uri)
        except Exception as ex:
            print(ex)
            raise
    
    def disconnect(self):
        app = App.get_running_app()
        try:
            app.uac.disconnect()
        except Exception as ex:
            print(ex)
            raise

    def on_stop(self):
        app = App.get_running_app()
        app.disconnect()

if __name__ == '__main__':
    MainWindow().run()