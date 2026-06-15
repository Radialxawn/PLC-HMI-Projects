from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle

class Draw(object):
    def __init__(self, _pixel_per_micro_):
        self._pixel_per_micro = _pixel_per_micro_
        self._offset_x = 0
        self._offset_y = 0

    @property
    def pixel_per_micro(self):
        return self._pixel_per_micro

    @pixel_per_micro.setter
    def pixel_per_micro(self, value):
        self._pixel_per_micro = max(1e-3, min(value, 5e-3))
    
    def pixel_to_micro(self, _x_, _y_):
        return _x_ / self._pixel_per_micro, _y_ / self._pixel_per_micro

    def shape(self, _shape_, _position_):
        sid = _shape_.id
        ppm = self._pixel_per_micro
        sa = _shape_.va * ppm
        sb = _shape_.vb * ppm
        sc = _shape_.vc * ppm
        sd = _shape_.vd * ppm
        se = _shape_.ve * ppm
        px = _position_[0] * ppm
        py = _position_[1] * ppm
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