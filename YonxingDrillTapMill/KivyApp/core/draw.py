from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from kivy.utils import get_color_from_hex as clhex
from kivy.core.image import Image as CoreImage
from core.helper import Helper
from data.shape import Shape
import numpy as np

class Draw(object):
    def __init__(self, _ppm_, _ppm_range_):
        self._pixel_per_micro = _ppm_
        self._ppm_range = _ppm_range_
        self._offset_pixel = [0, 0]

    @property
    def pixel_per_micro(self):
        return self._pixel_per_micro

    @pixel_per_micro.setter
    def pixel_per_micro(self, _value_):
        self._pixel_per_micro = max(self._ppm_range[0], min(_value_, self._ppm_range[1]))

    @property
    def offset_pixel(self):
        return self._offset_pixel.copy()
    
    @offset_pixel.setter
    def offset_pixel(self, _value_):
        self._offset_pixel[0] = _value_[0]
        self._offset_pixel[1] = _value_[1]
    
    def pixel_to_micro(self, *_params_):
        result = list(_params_)
        for i, v in enumerate(result):
            result[i] = v / self._pixel_per_micro
        return result

    def micro_to_pixel(self, *_params_):
        result = list(_params_)
        for i, v in enumerate(result):
            result[i] = v * self._pixel_per_micro
        return result

    def micro_to_pixel_offset(self, _x_, _y_):
        return _x_ * self._pixel_per_micro + self._offset_pixel[0], _y_ * self._pixel_per_micro + self._offset_pixel[1]
    
    def touch_pos_to_center_of_widget(self, _widget_, _touch_pos_):
        wgpos = _widget_.pos
        wgsize = _widget_.size
        dxp = _touch_pos_[0] - wgpos[0]
        dyp = _touch_pos_[1] - wgpos[1]
        inside = 0 < dxp < wgsize[0] and 0 < dyp < wgsize[1]
        dxp -= wgsize[0] * 0.5 + self._offset_pixel[0]
        dyp -= wgsize[1] * 0.5 + self._offset_pixel[1]
        return dxp, dyp, inside

    def axis(self, _area_, _pos_pixel_, _max_x_pixel_=None, _width_=1):
        pos = [_pos_pixel_[0]+self._offset_pixel[0], _pos_pixel_[1]+self._offset_pixel[1]]
        Color(rgba=clhex("#ff5656ff"))
        Rectangle(pos=pos, size=[_area_.size[0], _width_])
        Color(rgba=clhex("#56ff64ff"))
        Rectangle(pos=pos, size=[_width_, _area_.size[1]])
        if _max_x_pixel_ != None:
            Color(rgba=clhex("#000000ff"))
            Rectangle(pos=[pos[0]+_max_x_pixel_, pos[1]-_area_.size[1]*0.5], size=[_width_, _area_.size[1]])

    def shape(self, _shape_, _pos_micro_, _color_):
        Color(rgba=_color_)
        sa, sb, sc, sd, se = self.micro_to_pixel(_shape_.va, _shape_.vb, _shape_.vc, _shape_.vd, _shape_.ve)
        px, py = self.micro_to_pixel(_pos_micro_[0], _pos_micro_[1])
        poff = self.offset_pixel 
        px += poff[0]
        py += poff[1]
        match _shape_.id:
            case 1: # drill
                texture = CoreImage('texture/drill.png').texture
                sa, = self.micro_to_pixel(Shape.shape_name__data['drill']['view_micro'])
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case 2: # tap
                texture = CoreImage('texture/tap.png').texture
                sa, = self.micro_to_pixel(Shape.shape_name__data['tap']['view_micro'])
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case 3: # circle
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
            case 4: # circles
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(0, 0, 0, 1)
                abh = max(sa, sb)
                se = max(1, se*2)
                for i in np.arange(se, abh, se):
                    sai = i * sa / abh
                    sbi = i * sb / abh
                    Line(ellipse=(px-sai*0.5, py-sbi*0.5, sai, sbi), width=1)
            case 5: # rect
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 2
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
            case 6: # rects
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
                Color(0, 0, 0, 1)
                abh = max(sa, sb)
                se = max(1, se*2)
                for i in np.arange(se, abh, se):
                    sai = i * sa / abh
                    sbi = i * sb / abh
                    sci = sc * sai / sa
                    Line(rounded_rectangle=(px-sai*0.5, py-sbi*0.5, sai, sbi, sci), width=1)
            case 7: # locka
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px+(sa-2*sc)*0.5, py-sc*0.5], size=[sc, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px+(sa-2*sc)*0.5, py-sc*0.5], size=[sc, sc])
            case 8: # lockaf
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px-sa*0.5, py-sc*0.5], size=[sc, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px-sa*0.5, py-sc*0.5], size=[sc, sc])
            case 9: # lockb
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                sd -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
            case 10: # lockbf
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5+(sc-sb)*0.5], size=[sd, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                sd -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5+(sc-sb)*0.5], size=[sd, sc])
        scid = Shape.get_custom_id(_shape_.id)
        if scid >= 0:
            image, pixel_per_mm = Helper.cnc_preview_image_get(_index_=scid, _image_=True)
            sa, = self.micro_to_pixel(Shape.shape_name__data['custom_0']['view_micro'])
            if image != None:
                if pixel_per_mm != None:
                    sa, = self.micro_to_pixel(image.width * 1e3 / pixel_per_mm)
                Rectangle(texture=image.texture, pos=(px-sa*0.5, py-sa*0.5), size=(sa, sa))
            Line(rectangle=(px-sa*0.5, py-sa*0.5, sa, sa), width=1)
    
    def face(self, _face_, _pos_micro_, _color_):
        px, py = _pos_micro_[0], _pos_micro_[1]
        Color(rgba=clhex("#000000ff"))
        pxp, pyp, wp = self.micro_to_pixel(px, py, 50_000)
        poff = self.offset_pixel
        pxp += poff[0]
        pyp += poff[1]
        zpl = 0
        for z, zs in zip(_face_.z, _face_.zs):
            if z == 0 and zs == 0:
                continue
            zp, zsp = self.micro_to_pixel(z, zs)
            if zsp > 0:
                for i in np.arange(zpl, zp, zsp):
                    Rectangle(pos=[pxp-wp, pyp-i], size=[wp, 1])
                Rectangle(pos=[pxp-wp, pyp-zp], size=[wp, 1])
            else:
                Rectangle(pos=[pxp-wp, pyp-zp], size=[wp, 1])
            zpl = zp
        for shape in _face_.shape:
            self.shape(shape, [px + shape.x,  py + shape.y], _color_=_color_)