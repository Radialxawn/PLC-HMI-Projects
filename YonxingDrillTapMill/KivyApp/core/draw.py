from kivy.graphics import Color, Line, Rectangle, Ellipse, RoundedRectangle

class Draw(object):
    def __init__(self, _pixel_per_micro_):
        self._pixel_per_micro_ = _pixel_per_micro_
        self._offset_x = 0
        self._offset_y = 0
    
    def set(self, _pixel_per_micro_, _offset_x_, _offset_y_):
        self._pixel_per_micro_ = _pixel_per_micro_
        self._offset_x = _offset_x_
        self._offset_y = _offset_y_
    
    def pixel_to_micro(self, _x_, _y_):
        return _x_ / self._pixel_per_micro_, _y_ / self._pixel_per_micro_

    def shape(self, _area_, _shape_, _position_):
        sid = _shape_.id
        x, y, va, vb, vc, vd, ve = 'x', 'y', 'va', 'vb', 'vc', 'vd', 've'
        sa = _shape_[va] * self._pixel_per_micro_
        sb = _shape_[vb] * self._pixel_per_micro_
        sc = _shape_[vc] * self._pixel_per_micro_
        sd = _shape_[vd] * self._pixel_per_micro_
        se = _shape_[ve] * self._pixel_per_micro_
        px = _position_[0] * self._pixel_per_micro_
        py = _position_[1] * self._pixel_per_micro_
        bound = min(_area_.size)
        bound = max(0, bound - 10)
        if bound == 0.0:
            return []
        active_sp = []
        with _area_.canvas:
            match sid:
                case 1: # drill
                    active_sp = [x, y, va, vb, vc]
                case 2: # tap
                    active_sp = [x, y, va, vb, vc]
                case 3: # circle
                    Color(1, 0, 0, 1)
                    Ellipse(pos=[px-sa*0.5, py-sa*0.5], size=[sa, sa])
                    active_sp = [x, y, va]
                case 4: # rect
                    Color(1, 0, 0, 1)
                    Rectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                    active_sp = [x, y, va, vb]
                case 5: # capsule
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    active_sp = [x, y, va, vb]
                case 6: # rectr
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sc])
                    active_sp = [x, y, va, vb, vc]
                case 7: # ellipse
                    Color(1, 0, 0, 1)
                    Ellipse(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb])
                    active_sp = [x, y, va, vb]
                case 8: # locka
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Ellipse(pos=[px-sc*0.5+(sa-sc)*0.5, py-sc*0.5], size=[sc, sc])
                    active_sp = [x, y, va, vb, vc]
                case 9: # lockaf
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Ellipse(pos=[px-sc*0.5-(sa-sc)*0.5, py-sc*0.5], size=[sc, sc])
                    active_sp = [x, y, va, vb, vc]
                case 10: # lockb
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Rectangle(pos=[px-sd*0.5, py-sc*0.5-(sc-sb)*0.5], size=[sd, sc])
                    active_sp = [x, y, va, vb, vc, vd]
                case 11: # lockbf
                    Color(1, 0, 0, 1)
                    RoundedRectangle(pos=[px-sa*0.5, py-sb*0.5], size=[sa, sb], radius=[sb*0.5])
                    Rectangle(pos=[px-sd*0.5, py-sc*0.5+(sc-sb)*0.5], size=[sd, sc])
                    active_sp = [x, y, va, vb, vc, vd]
            scid = -1
            if sid > 11:
                scid = sid - 11 - 1
            if scid >= 0:
                Color(1, 0, 0, 1)
                Line(rectangle=(px-bound*0.5, py-bound*0.5, bound, bound), width=2)
        return active_sp