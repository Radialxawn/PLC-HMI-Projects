from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from popup.popup_progress import PopupProgress
from popup.popup_file import PopupFile
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from core.ui import UITextInputInteger
from kivy.utils import get_color_from_hex as clhex

class ScreenCNC(Screen):
    def __init__(self, **kvargs):
        super(ScreenCNC, self).__init__(**kvargs)
        self._first_load = True
        self._cnc_id = -1
        self._cnc_id_selector_active = False
    
    def on_pre_enter(self, *args):
        if self._first_load:
            self._first_load = False
            self._name__hash = {
                'hmi.cnc_id',
                'hmi.cnc_feed',
                'hmi.view_cnc_micro[0]',
                'hmi.view_cnc_micro[1]',
                'hmi.view_cnc_micro[2]',
                'hmi.view_can_run',
            }
            self._name__index, self._name__input, self._name__value = self._generate()
    
    def _generate(self):
        cnc_id_selector = self.ids.cnc_id_selector
        name__index = {}
        values = []
        for i in range(6):
            button = self.ids[f'cnc_{i}']
            button.text = f'CNC {i+1}'
            button.cnc_index = i
            values.append(button.text)
            name__index[button.text] = i
        cnc_id_selector.values = values
        cnc_id_selector.text = values[0]
        #
        name__input, name__value = {}, {}
        name__data = {
            'hmi.cnc_feed': {'label': 'TỐC ĐỘ (mm/min)', 'factor': 1},
        }
        self.ids.cnc_property.width = 180
        for name in name__data:
            data = name__data[name]
            label = Label(
                text=data['label'],
                size_hint_x=None,
                size_hint_y=None,
                halign='left',
                valign='center',
                height=40,
                width=180
            )
            label.bind(size=label.setter('text_size'))
            input = UITextInputInteger(
                size_hint_y=None,
                height=40,
                halign='center',
                multiline=False
            ).data_set(
                _key_=name,
                _factor_=data['factor'],
                _validate_=self._on_text_input_validate,
                _focus_=None
            )
            name__input[input.v_key] = input
            name__value[input.v_key] = None
            self.ids.cnc_property.add_widget(label)
            self.ids.cnc_property.add_widget(input)
        self.ids.cnc_property.add_widget(Widget())
        return name__index, name__input, name__value

    def on_enter(self, *args):
        self._cnc_id_selector_active = True
        app = App.get_running_app()
        app.data.block_active(self._name__hash)
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_leave(self, *args):
        self._cnc_id_selector_active = False
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _on_text_input_validate(self, _instance_, _value_):
        app = App.get_running_app()
        app.data.set(_instance_.v_key, _value_)

    def _value_update(self, _dt_):
        app = App.get_running_app()
        for name in self._name__input:
            input = self._name__input[name]
            if input.focus:
                continue
            block = app.data.block(name)
            value = self._name__value[name]
            if value == block.value:
                continue
            self._name__value[name] = block.value
            input.v_value_set(block.value)
        view_can_run = app.data.get('hmi.view_can_run')
        self.ids.cnc_run.disabled = not view_can_run
        cnc_id = app.data.get('hmi.cnc_id')
        if cnc_id != self._cnc_id:
            self._cnc_id = cnc_id
            for i in range(6):
                color = clhex("#6AA145") if cnc_id == i else clhex("#5F5F5F")
                self.ids[f'cnc_{i}'].background_color = color
    
    def _on_cnc_id_selector(self, _instance_):
        if not self._cnc_id_selector_active:
            return
        app = App.get_running_app()
        app.data.set('hmi.cnc_id', self._name__index[_instance_.text])

    def _cnc_download(self, _instance_):
        self._download_cnc_index = _instance_.cnc_index
        popup = PopupFile(
            title='CHỌN TỆP CNC',
        ).set_data(
            _folder_='CNC',
            _filter_=['*.cnc'],
            _select_=lambda p: self._cnc_download_confirm(p, _instance_.cnc_index),
            _deletable_=False
        )
        popup.open()
    
    def _cnc_download_confirm(self, _source_path_, _cnc_index_):
        app = App.get_running_app()
        app.m_show_popup_confirm(
            _message_=f'TẢI TỆP [{_source_path_.stem}] XUỐNG PLC [CNC {_cnc_index_+1}]?',
            _confirm_=lambda : self._cnc_download_start(_source_path_)
        )
    
    def _cnc_download_start(self, _source_path_):
        app = App.get_running_app()
        popup = PopupProgress().set_data(
            _cancel_=app.data.download_cancel
        )
        popup.open()
        self._popup_progress = popup
        app.data.download_start(
            _source_path_=_source_path_,
            _destination_index_=self._download_cnc_index,
            _progress_=self._cnc_download_progress
        )
    
    def _cnc_download_progress(self, _value_):
        self._popup_progress.progress(_value_)
    
    def _cnc_run(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.cnc_run', _value_)