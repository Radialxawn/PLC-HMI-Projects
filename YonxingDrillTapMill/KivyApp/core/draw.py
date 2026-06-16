from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle
from kivy.utils import get_color_from_hex as clhex

class Draw(object):
    def __init__(self, _pixel_per_micro_):
        self._pixel_per_micro = _pixel_per_micro_
        self._offset_pixel = [0, 0]

    @property
    def pixel_per_micro(self):
        return self._pixel_per_micro

    @pixel_per_micro.setter
    def pixel_per_micro(self, _value_):
        self._pixel_per_micro = max(0.5e-3, min(_value_, 5e-3))

    @property
    def offset_pixel(self):
        return self._offset_pixel.copy()
    
    @offset_pixel.setter
    def offset_pixel(self, _value_):
        self._offset_pixel[0] = _value_[0]
        self._offset_pixel[1] = _value_[1]
    
    def pixel_to_micro(self, _x_, _y_):
        return _x_ / self._pixel_per_micro, _y_ / self._pixel_per_micro

    def axis(self, _area_, _position_):
        pos = [_position_[0]+self._offset_pixel[0], _position_[1]+self._offset_pixel[1]]
        Color(rgba=clhex("#ff5656ff"))
        Rectangle(pos=pos, size=[_area_.size[0], 1])
        Color(rgba=clhex("#56ff64ff"))
        Rectangle(pos=pos, size=[1, _area_.size[1]])

    def shape(self, _shape_, _position_):
        sid = _shape_.id
        ppm = self._pixel_per_micro
        sa = _shape_.va * ppm
        sb = _shape_.vb * ppm
        sc = _shape_.vc * ppm
        sd = _shape_.vd * ppm
        se = _shape_.ve * ppm
        px = _position_[0] * ppm + self._offset_pixel[0]
        py = _position_[1] * ppm + self._offset_pixel[1]
        match sid:
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
    
    def face(self, _face_, _position_):
        for shape in _face_.shape:
            px = _position_[0] + shape.x
            py = _position_[1] + shape.y
            self.shape(shape, [px,  py])