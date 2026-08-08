from kivy.app import App
from pathlib import Path
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo
from kivy.core.image import Image as CoreImage
from popup.popup_confirm import PopupConfirm
import numpy as np
import cv2

class Helper(object):
    def __init__(self, **kvargs):
        self._name__popup = {
            'confirm': None,
            'login': None,
            'error': None,
        }

    def save_accept(self):
        app = App.get_running_app()
        app.data.set('hmi.cfsh.accept', True)
    
    def save_decline(self):
        app = App.get_running_app()
        app.data.set('hmi.cfsh.decline', True)
    
    def save_need_check(self):
        app = App.get_running_app()
        app.data.set('hmi.cfsh.need_check', True)
    
    def home(self, _value_):
        app = App.get_running_app()
        app.data.set('hmi.home', _value_)
    
    def _popup_is_active(self, _name_: str):
        return self._name__popup[_name_] != None
    
    def _popup_activate(self, _name_: str, _popup_):
        self._name__popup[_name_] = _popup_

    def _popup_dismiss(self, _name_: str):
        self._name__popup[_name_] = None

    def show_popup_confirm(self, _message_, _confirm_, _password_=None):
        name = 'confirm'
        if self._popup_is_active(name):
            return
        popup = PopupConfirm().set_data(
            _confirm_=_confirm_,
            _dismiss_=lambda: self._popup_dismiss(name),
            _message_=_message_,
            _password_=_password_,
        )
        popup.open()
        self._popup_activate(name, popup)