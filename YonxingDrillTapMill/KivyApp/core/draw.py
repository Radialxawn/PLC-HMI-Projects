from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from kivy.utils import get_color_from_hex as clhex
from kivy.core.image import Image as CoreImage
from data.shape import Shape

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
    
    def pixel_to_micro(self, _x_, _y_):
        return _x_ / self._pixel_per_micro, _y_ / self._pixel_per_micro

    def micro_to_pixel(self, _x_, _y_):
        ppm = self._pixel_per_micro
        return ppm * _x_ + self._offset_pixel[0], ppm * _y_ + self._offset_pixel[1]
    
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

    def shape(self, _shape_, _pos_micro_):
        sid = _shape_.id
        ppm = self._pixel_per_micro
        sa = _shape_.va * ppm
        sb = _shape_.vb * ppm
        sc = _shape_.vc * ppm
        sd = _shape_.vd * ppm
        se = _shape_.ve * ppm
        px, py = self.micro_to_pixel(_pos_micro_[0], _pos_micro_[1])
        match sid:
            case 1: # drill
                texture = CoreImage('texture/drill.png').texture
                sa = Shape.shape_name__data['drill']['view_micro'] * ppm
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case 2: # tap
                texture = CoreImage('texture/tap.png').texture
                sa = Shape.shape_name__data['tap']['view_micro'] * ppm
                Rectangle(texture=texture, pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case 3: # circle
                Ellipse(pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
            case 4: # rect
                Rectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
            case 5: # capsule
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
            case 6: # rectr
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
            case 7: # ellipse
                Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
            case 8: # locka
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px+(sa-2*sc)*0.5, py-sc*0.5], size=[sc, sc])
            case 9: # lockaf
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Ellipse(pos=[px-sa*0.5, py-sc*0.5], size=[sc, sc])
            case 10: # lockb
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
            case 11: # lockbf
                RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                Rectangle(pos=[px-sd*0.5, py-sc*0.5+(sc-sb)*0.5], size=[sd, sc])
        scid = -1
        if sid > 11:
            scid = sid - 11 - 1
        if scid >= 0:
            Line(rectangle=(px-sa*0.5, py-sa*0.5, sa, sa), width=2)
    
    def face(self, _face_, _position_, _color_):
        px, py = _position_[0], _position_[1]
        Color(rgba=clhex("#000000ff"))
        pxp, pyp = self.micro_to_pixel(px, py)
        Rectangle(pos=[pxp, pyp], size=[50, 1])
        Rectangle(pos=[pxp, pyp], size=[1, 50])
        for i, iz in enumerate(_face_.z):
            _, izp = self.micro_to_pixel(0, py - iz)
            Rectangle(pos=[pxp, izp], size=[50, 1])
        Color(rgba=_color_)
        for shape in _face_.shape:
            self.shape(shape, [px + shape.x,  py + shape.y])