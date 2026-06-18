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
from kivy.app import App
from core.data import Data
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup
from core.launcher import Launcher
from kivy.core.window import Window
from screen.screen_io import ScreenIO
from screen.screen_home import ScreenHome
from screen.screen_setting import ScreenSetting
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from screen.screen_setting_axis import ScreenSettingAxis
from popup.popup_confirm import PopupConfirm
from screen.screen_load import ScreenLoad
from popup.popup_login import PopupLogin
from popup.popup_error import PopupError

Builder.load_file('style.kv')
Builder.load_file('screen/screen_load.kv')
Builder.load_file('screen/screen_home.kv')
Builder.load_file('screen/screen_io.kv')
Builder.load_file('screen/screen_setting.kv')
Builder.load_file('screen/screen_setting_axis.kv')
Builder.load_file('popup/popup_confirm.kv')
Builder.load_file('popup/popup_file.kv')
Builder.load_file('popup/popup_login.kv')
Builder.load_file('popup/popup_progress.kv')
Builder.load_file('popup/popup_face.kv')
Builder.load_file('popup/popup_shape.kv')
Builder.load_file('popup/popup_error.kv')

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
            _xml_path_windows_=r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml',
            _tag_head_='ns=4;s=|var|LS'
        )
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(ScreenLoad(name='load'))
        sm.add_widget(ScreenHome(name='home'))
        sm.add_widget(ScreenIO(name='io'))
        sm.add_widget(ScreenSetting(name='setting'))
        sm.add_widget(ScreenSettingAxis(name='setting_axis'))
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

    def m_save_accept(self):
        self.data.set('hmi.cfsh.accept', True)
    
    def m_save_decline(self):
        self.data.set('hmi.cfsh.decline', True)
    
    def m_save_need_check(self):
        self.data.set('hmi.cfsh.need_check', True)
    
    def m_run(self, _value_):
        self.data.set('hmi.run', _value_)
    
    def m_stop(self, _value_):
        self.data.set('hmi.stop', _value_)

    def m_home(self):
        self.data.set('hmi.home', True)
    
    def m_face_run(self, _value_):
        self.data.set('hmi.face_run', _value_)
    
    def m_face_to_org(self, _value_):
        self.data.set('hmi.face_to_org', _value_)

    def m_run_pump_toggle(self):
        name = 'hmi.run_pump'
        value = self.data.get(name)
        self.data.set(name, not value)
    
    def m_show_popup_confirm(self, _message_, _confirm_):
        popup = Popup(
            title="XÁC NHẬN",
            size_hint=(None, None),
            size=(480, 240),
            auto_dismiss=False
        )
        popup.content = PopupConfirm(
            _instance_=popup,
            _confirm_=_confirm_
        )
        popup.content.ids['message'].text = _message_
        popup.open()
    
    def m_show_popup_login(self, _password_, _screen_):
        popup = Popup(
            title="ĐĂNG NHẬP",
            size_hint=(None, None),
            size=(480, 240),
            auto_dismiss=False
        )
        popup.content = PopupLogin(
            _instance_=popup,
            _password_=_password_,
            _screen_=_screen_
        )
        popup.open()
    
    def m_show_popup_error(self, _message_, _acknowledge_):
        popup = Popup(
            title="LỖI",
            size_hint=(None, None),
            size=(480, 240),
            auto_dismiss=False
        )
        popup.content = PopupError(
            _instance_=popup,
            _acknowledge_=_acknowledge_
        )
        popup.content.ids['message'].text = _message_
        popup.open()

if __name__ == '__main__':
    Main().run()