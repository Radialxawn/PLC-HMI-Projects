from pathlib import Path
from core.gcode import GCode
from kivy.core.image import Image as CoreImage
from PIL.PngImagePlugin import PngInfo
from PIL import Image, ImageDraw

class Helper(object):
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
            return CoreImage(str(path)), pixel_per_mm
        except:
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
        image = Image.new('RGBA', (image_size, image_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        lx, ly, lz = size_half, size_half, 0
        lw = round(max(1, tool_diameter * pixel_per_mm))
        for point in _gcode_.checked.points:
            x, y, z = point
            x = round(size_half + x * pixel_per_mm)
            y = round(size_half - y * pixel_per_mm)
            z = round(max(-255, min(z * depth_factor, 0)))
            draw.line((lx, ly, x, y), fill=(abs(z), 0, 0, 255), width=lw)
            lx, ly, lz = x, y, z
        path = Helper.cnc_preview_path_get(_index_)
        metadata = PngInfo()
        metadata.add_text('pixel_per_mm', f'{pixel_per_mm:.8f}')
        image.save(path, pnginfo=metadata)
    
    @staticmethod
    def cnc_preview_image_remove(_index_: int):
        path = Helper.cnc_preview_path_get(_index_)
        path.unlink(missing_ok=True)