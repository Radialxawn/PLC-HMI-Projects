class Shape(object):
    name__data = {
        'NONE':     {'id': 0,  'sp': []},
        'DRILL':    {'id': 1,  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'TAP':      {'id': 2,  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'CIRCLE':   {'id': 3,  'sp': ['x', 'y', 'va']},
        'RECT':     {'id': 4,  'sp': ['x', 'y', 'va', 'vb']},
        'CAPSULE':  {'id': 5,  'sp': ['x', 'y', 'va', 'vb']},
        'RECT-R':   {'id': 6,  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'ELLIPSE':  {'id': 7,  'sp': ['x', 'y', 'va', 'vb']},
        'LOCKA':    {'id': 8,  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'LOCKA-F':  {'id': 9,  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'LOCKB':    {'id': 10, 'sp': ['x', 'y', 'va', 'vb', 'vc', 'vd']},
        'LOCKB-F':  {'id': 11, 'sp': ['x', 'y', 'va', 'vb', 'vc', 'vd']},
        'CNC-1':    {'id': 12, 'sp': ['x', 'y']},
        'CNC-2':    {'id': 13, 'sp': ['x', 'y']},
        'CNC-3':    {'id': 14, 'sp': ['x', 'y']},
        'CNC-4':    {'id': 15, 'sp': ['x', 'y']},
        'CNC-5':    {'id': 16, 'sp': ['x', 'y']},
        'CNC-6':    {'id': 17, 'sp': ['x', 'y']},
    }

    def __init__(self):
        self.id = 0
        self.x = 0
        self.y = 0
        self.va = 0
        self.vb = 0
        self.vc = 0
        self.vd = 0
        self.ve = 0

    def __getitem__(self, _key_):
        return getattr(self, _key_)

    def __setitem__(self, _key_, _value_):
        if _key_ in self.__dict__:
            setattr(self, _key_, _value_)
        else:
            raise Exception(f'No {_key_} in this class')
    
    def limit(self):
        match self.id:
            case 5: # capsule
                self.vb = int(min(self.va, self.vb))
            case 6: # rectr
                self.vc = int(min(self.va*0.5, self.vb*0.5, self.vc))
            case 8: # locka
                self.vb = int(min(self.va, self.vb))
            case 9: # lockaf
                self.vb = int(min(self.va, self.vb))
            case 10: # lockb
                self.vb = int(min(self.va, self.vb))
            case 11: # lockbf
                self.vb = int(min(self.va, self.vb))

    def contain(self, _lx_, _ly_, _r_):
        dx = _lx_ - self.x
        dy = _ly_ - self.y
        match self.id:
            case 0: # none
                return False
            case 1: # drill
                return False
            case 2: # tap
                return False
            case 3: # circle
                return Shape._inside_local_circle(dx, dy, self.va*0.5)
            case 4: # rect
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, 0)
            case 5: # capsule
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
            case 6: # rectr
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vc)
            case 7: # ellipse
                if self.va == 0 or self.vb == 0:
                    return False
                a = self.va * 0.5
                b = self.vb * 0.5
                return dx*dx/(a*a) + dy*dy/(b*b) <= 1.0
            case 8: # locka
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx-(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case 9: # lockaf
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx+(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case 10: # lockb
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy+ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
            case 11: # lockbf
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy-ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
        return (dx*dx + dy*dy) < _r_*_r_

    @staticmethod
    def _inside_local_circle(_px_, _py_, _r_):
        return  (_px_ * _px_ + _py_ * _py_) < (_r_ * _r_)

    @staticmethod
    def _inside_local_rect_r(_px_, _py_, _w_, _h_, _r_):
        hw, hh = _w_ * 0.5, _h_ * 0.5
        dx, dy = abs(_px_), abs(_py_)
        if dx > hw or dy > hh:
            return False
        inner_w = hw - _r_
        inner_h = hh - _r_
        if dx <= inner_w or dy <= inner_h:
            return True
        tx = dx - inner_w
        ty = dy - inner_h
        return (tx * tx + ty * ty) <= (_r_ * _r_)
