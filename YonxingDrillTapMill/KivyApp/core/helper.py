from kivy.app import App
from pathlib import Path
from core.gcode import GCode
from PIL import Image, ImageDraw
from PIL.PngImagePlugin import PngInfo
from popup.popup_error import PopupError
from kivy.core.image import Image as CoreImage
from popup.popup_confirm import PopupConfirm
from popup.popup_login import PopupLogin
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

    def show_popup_confirm(self, _message_, _confirm_):
        name = 'confirm'
        if self._popup_is_active(name):
            return
        popup = PopupConfirm().set_data(
            _confirm_=_confirm_,
            _dismiss_=lambda: self._popup_dismiss(name)
        )
        popup.ids['message'].text = _message_
        popup.open()
        self._popup_activate(name, popup)

    def show_popup_login(self, _password_, _screen_):
        name = 'login'
        if self._popup_is_active(name):
            return
        popup = PopupLogin().set_data(
            _password_=_password_,  
            _screen_=_screen_,
            _dismiss_=lambda: self._popup_dismiss(name)
        )
        popup.open()
        self._popup_activate(name, popup)
    
    def show_popup_error(self, _message_, _acknowledge_):
        name = 'error'
        if self._popup_is_active(name):
            return
        popup = PopupError().set_data(
            _acknowledge_=_acknowledge_,
            _dismiss_=lambda: self._popup_dismiss(name)
        )
        popup.ids.message.text = _message_
        popup.open()
        self._popup_activate(name, popup)

    @staticmethod
    def path_get(_folder_: str):
        folder = f'Desktop/{_folder_}'
        rootpath = Path.home() / folder
        if not rootpath.exists():
            rootpath.mkdir(parents=True, exist_ok=True)
        return rootpath
    
    @staticmethod
    def gcode_read(_source_path_: Path):
        if not _source_path_.is_file():
            raise Exception('KHÔNG TỒN TẠI TỆP [%s]' % (_source_path_.stem))
        gcode = GCode().read(_source_path_)
        gcode.parse()
        gcode.combine()
        gcode.check(0.1)
        return gcode
    
    @staticmethod
    def cnc_preview_path_get(_index_: int):
        return Helper.path_get('CNC') / f'cnc_{_index_}.png'
    
    @staticmethod
    def cnc_preview_image_get(_index_: int, _image_: bool):
        path = Helper.cnc_preview_path_get(_index_)
        if not path.exists():
            return None, None
        if not _image_:
            return True, True
        image = Image.open(path)
        try:
            pixel_per_mm = float(image.text.get('pixel_per_mm'))
            CoreImage(str(path)).remove_from_cache()
            return CoreImage(str(path)), pixel_per_mm
        except:
            CoreImage(str(path)).remove_from_cache()
            return CoreImage(str(path)), None
        finally:
            image.close()

    @staticmethod
    def cnc_preview_image_generate(_gcode_: GCode, _index_: int):
        size_half = 256
        image_size = size_half * 2
        tool_diameter = 6.0
        pixel_per_mm = image_size / (max(1,
            abs(_gcode_.checked.bound_min[0])+tool_diameter*2,
            abs(_gcode_.checked.bound_min[1])+tool_diameter*2,
            abs(_gcode_.checked.bound_max[0])+tool_diameter*2,
            abs(_gcode_.checked.bound_max[1])+tool_diameter*2,
        )*2)
        depth_factor = 256 / max(1, abs(_gcode_.checked.bound_min[2]))
        image = np.zeros((image_size, image_size, 2), dtype=np.uint8)
        image_tmp = image.copy()
        lx, ly, lz = size_half, size_half, 0
        lw = round(max(1, tool_diameter * pixel_per_mm))
        for point in _gcode_.checked.points:
            x, y, z = point
            x = round(size_half + x * pixel_per_mm)
            y = round(size_half - y * pixel_per_mm)
            z = round(max(-255, min(z * depth_factor, 0)))
            image_tmp[:] = 0
            cv2.line(image_tmp, (lx, ly), (x, y), (abs(z), 255), lw)
            image = cv2.max(image, image_tmp)
            lx, ly, lz = x, y, z
        image[:, :, 0] = 255 - image[:, :, 0] # invert the first channel
        image_final = np.zeros((image_size, image_size, 4), dtype=np.uint8)
        image_final[:, :, 2] = image[:, :, 0] # copy first channel to red channel, cv2 use BGRA instead of RGBA
        image_final[:, :, 3] = image[:, :, 1] # copy second channel to alpha channel
        path = Helper.cnc_preview_path_get(_index_)
        cv2.imwrite(path, image_final)
        image_source = Image.open(path)
        metadata = PngInfo()
        metadata.add_text('pixel_per_mm', f'{pixel_per_mm:.8f}')
        image_source.save(path, pnginfo=metadata)
    
    @staticmethod
    def cnc_preview_image_remove(_index_: int):
        path = Helper.cnc_preview_path_get(_index_)
        path.unlink(missing_ok=True)