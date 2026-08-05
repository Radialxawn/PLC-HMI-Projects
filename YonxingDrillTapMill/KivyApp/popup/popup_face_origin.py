from kivy.app import App
from data.face import Face
from kivy.uix.popup import Popup
from types import SimpleNamespace
from kivy.utils import get_color_from_hex as clhex

class PopupFaceOrigin(Popup):
    def set_data(self, _name__input_view_, _set_):
        self._name__input_view = _name__input_view_
        self._set_ = _set_
        button__edge_data = {}
        for id in [['edge_xn', 0], ['edge_xp', 0], ['edge_yn', 1], ['edge_yp', 1], ['edge_z', 2]]:
            k = self.ids[id[0]]
            v = SimpleNamespace(
                id=id[0],
                axis=id[1],
                position=[0, 0, 0],
                active=False,
            )
            k.bind(on_press=self._edge_press)
            button__edge_data[k] = v
        self._button__edge_data = button__edge_data
        return self

    def _edge_press(self, _instance_):
        app = App.get_running_app()
        edge_data = self._button__edge_data[_instance_]
        edge_data.active = not edge_data.active
        edge_data.position = [
            app.data.get(Face.property__data['ox']['name_view']),
            app.data.get(Face.property__data['oy']['name_view']),
            app.data.get(Face.property__data['oz']['name_view']),
        ]
        color = clhex("#6AA145") if edge_data.active else clhex("#5F5F5F")
        _instance_.background_color = color

    def _set(self):
        ps = [[], [], []]
        position = None
        for button in self._button__edge_data:
            v = self._button__edge_data[button]
            if v.active:
                ps[v.axis].append(v.position[v.axis])
        for i, p in enumerate(ps):
            if len(p) > 0:
                if position == None:
                    position = [None, None, None]
                position[i] = round(sum(p)/len(p))
        self._set_(position)
        self.dismiss()

    def _cancel(self):
        self.dismiss()