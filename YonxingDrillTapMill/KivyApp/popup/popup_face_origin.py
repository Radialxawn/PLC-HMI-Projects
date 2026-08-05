from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex as clhex

class PopupFaceOrigin(Popup):
    def set_data(self, _face_edit_):
        self._face_edit = _face_edit_
        self._generate()
        return self

    def _generate(self):
        return

    def on_open(self, *args):
        if not hasattr(self, '_value_update_clock'):
            self._value_update_clock = Clock.schedule_interval(self._value_update, 0.1)

    def on_dismiss(self, *args):
        if hasattr(self, '_value_update_clock'):
            Clock.unschedule(self._value_update_clock)
            delattr(self, '_value_update_clock')
    
    def _face_to_org(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.face_to_org', _value_)
    
    def _face_run(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.face_run', _value_)
    
    def _face_org_set(self, _instance_):
        app = App.get_running_app()
        bid = _instance_.id
        for property in self._face_org_set_property__data:
            input = self._property__input[property]
            if not hasattr(input, 'v_name_view') or input.disabled:
                continue
            if bid == 'all' or (bid in self._face_org_set_property__data and bid == property):
                input_view = self._name__input_view[input.v_name_view]
                value = app.data.get(input_view.v_key)
                if value != None:
                    input.v_value_set(value)
                    self._on_text_input_validate(input, input.v_value_get())

    def _value_update(self, _dt_):
        return
        app = App.get_running_app()
        for name in self._name__input_view:
            input_view = self._name__input_view[name]
            block = app.data.block(name)
            if input_view.v_value_last == block.value:
                continue
            input_view.v_value_last = block.value
            input_view.v_value_set(block.value)
            input_view_local = input_view.v_local
            if input_view_local != None:
                delta = block.value - self._face_edit[input_view_local.v_key]
                input_view_local.v_value_set(delta)
        view_can_run = app.data.get('hmi.view_can_run')
        self.ids.face_run.disabled = not view_can_run
        self.ids.face_to_org.disabled = not view_can_run 

    def _update_canvas(self, *args):
        self._face_draw()

    def _apply(self):
        self.dismiss()

    def _cancel(self):
        self.dismiss()