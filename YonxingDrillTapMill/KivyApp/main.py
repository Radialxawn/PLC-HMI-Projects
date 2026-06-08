from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from screen.screen_home import ScreenHome
from screen.screen_setting import ScreenSetting

Builder.load_file('main.kv')

class MainWindow(App):
    def on_stop(self):
        return
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreenHome(name='home'))
        sm.add_widget(ScreenSetting(name='setting'))
        return sm

if __name__ == '__main__':
    MainWindow().run()