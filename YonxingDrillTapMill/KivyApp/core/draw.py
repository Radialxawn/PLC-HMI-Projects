from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from kivy.utils import get_color_from_hex as clhex
from kivy.core.image import Image as CoreImage
from core.helper import Helper
from data.shape import Shape
from data.shape import ShapeID
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
            case ShapeID.FACEX.value:
                Rectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(0, 0, 0, 1)
                se = max(1, se)
                sai = -sa * 0.5 * (1 - 2 * int(_shape_.vmode))
                Line(ellipse=(px+sai-se*0.5, py-sb*0.5-se*0.5, se, se), width=1)
                points = []
                for sbi in np.arange(-sb*0.5, sb*0.5, se):
                    points.append([px+sai, py+sbi])
                    points.append([px-sai, py+sbi])
                    sai = -sai
                Line(points=points, width=1)
            case ShapeID.FACEY.value:
                Rectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(0, 0, 0, 1)
                se = max(1, se)
                sbi = -sb * 0.5 * (1 - 2 * int(_shape_.vmode))
                Line(ellipse=(px-sa*0.5-se*0.5, py+sbi-se*0.5, se, se), width=1)
                points = []
                for sai in np.arange(-sa*0.5, sa*0.5, se):
                    points.append([px+sai, py+sbi])
                    points.append([px+sai, py-sbi])
                    sbi = -sbi
                Line(points=points, width=1)
            case ShapeID.DRILL.value:
                texture = CoreImage('texture/drill.png').texture
                sa, = self.micro_to_pixel(Shape.shape_id__data[ShapeID.DRILL]['view_micro'])
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case ShapeID.TAP.value:
                texture = CoreImage('texture/tap.png').texture
                sa, = self.micro_to_pixel(Shape.shape_id__data[ShapeID.TAP]['view_micro'])
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case ShapeID.CIRCLE.value:
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
            case ShapeID.CIRCLES.value:
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                Color(0, 0, 0, 1)
                abh = max(sa, sb)
                se = max(1, se*2)
                for i in np.arange(se, abh, se):
                    sai = i * sa / abh
                    sbi = i * sb / abh
                    Line(ellipse=(px-sai*0.5, py-sbi*0.5, sai, sbi), width=1)
            case ShapeID.RECT.value:
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 2
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
            case ShapeID.RECTS.value:
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
                Color(0, 0, 0, 1)
                abh = max(sa, sb)
                se = max(1, se*2)
                for i in np.arange(se, abh, se):
                    sai = i * sa / abh
                    sbi = i * sb / abh
                    sci = sc * sai / sa
                    Line(rounded_rectangle=(px-sai*0.5, py-sbi*0.5, sai, sbi, sci), width=1)
            case ShapeID.LOCKA.value:
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px+(sa-2*sc)*0.5, py-sc*0.5], size=[sc, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px+(sa-2*sc)*0.5, py-sc*0.5], size=[sc, sc])
            case ShapeID.LOCKAF.value:
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px-sa*0.5, py-sc*0.5], size=[sc, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px-sa*0.5, py-sc*0.5], size=[sc, sc])
            case ShapeID.LOCKB.value:
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
                Color(1, 1, 1, 1)
                sa -= 4
                sb -= 4
                sc -= 4
                sd -= 4
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
            case ShapeID.LOCKBF.value:
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
            sa, = self.micro_to_pixel(Shape.shape_id__data[ShapeID.CT0]['view_micro'])
            if image != None:
                if pixel_per_mm != None:
                    sa, = self.micro_to_pixel(image.width * 1e3 / pixel_per_mm)
                Rectangle(texture=image.texture, pos=(px-sa*0.5, py-sa*0.5), size=(sa, sa))
            Line(rectangle=(px-sa*0.5, py-sa*0.5, sa, sa), width=1)
    
    def face(self, _face_, _pos_micro_, _color_):
        px, py = _pos_micro_[0], _pos_micro_[1]
        pxp, pyp, wp, ws = self.micro_to_pixel(px, py, 25_000, 10_000)
        poff = self.offset_pixel
        pxp += poff[0]
        pyp += poff[1]
        zl = 0
        for z, zs in zip(_face_.z, _face_.zs):
            if z < zl:
                continue
            single = zs == 0
            if single:
                zs = _face_.depth
            zp, zsp, zpl = self.micro_to_pixel(z, zs, zl)
            if single:
                Color(rgba=clhex("#000000ff"))
                Rectangle(pos=[pxp-wp*2, pyp-zp], size=[wp-ws, 1])
                Color(rgba=clhex("#ff0000ff"))
                Line(points=[pxp-wp-ws, pyp-zp, pxp-wp, pyp-zp-zsp], width=1)
                Rectangle(pos=[pxp-wp, pyp-zp-zsp], size=[wp, 1])
                zl += zs
            else:
                for i in np.arange(zpl, zp, zsp):
                    Color(rgba=clhex("#000000ff"))
                    Rectangle(pos=[pxp-wp*2, pyp-i], size=[wp-ws, 1])
                    Color(rgba=clhex("#ff0000ff"))
                    Line(points=[pxp-wp-ws, pyp-i, pxp-wp, pyp-min(i+zsp, zp)], width=1)
                    Rectangle(pos=[pxp-wp, pyp-min(i+zsp, zp)], size=[wp, 1])
                zl = z
        for shape in _face_.shape:
            self.shape(shape, [px + shape.x,  py + shape.y], _color_=_color_)