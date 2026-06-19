class Shape(object):
    key__data = {
        'x':  {'label': 'X', 'factor': -1e-3},
        'y':  {'label': 'Y', 'factor': -1e-3},
        '0': None,
        'va': {'label': 'A', 'factor': 1e-3},
        'vb': {'label': 'B', 'factor': 1e-3},
        'vc': {'label': 'C', 'factor': 1e-3},
        'vd': {'label': 'D', 'factor': 1e-3},
        've': {'label': 'E', 'factor': 1e-3},
    }

    shape_name__data = {
        'none':     {'id': 0,  'label': '...',     'sp': []},
        'drill':    {'id': 1,  'label': 'KHOAN',   'sp': ['x', 'y', 'va', 'vb']},
        'tap':      {'id': 2,  'label': 'TARO',    'sp': ['x', 'y', 'va', 'vb']},
        'circle':   {'id': 3,  'label': 'TRÒN',    'sp': ['x', 'y', 'va']},
        'rect':     {'id': 4,  'label': 'HỘP',     'sp': ['x', 'y', 'va', 'vb']},
        'capsule':  {'id': 5,  'label': 'NANG',    'sp': ['x', 'y', 'va', 'vb']},
        'rectr':    {'id': 6,  'label': 'HỘP BO',  'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'ellipse':  {'id': 7,  'label': 'BẦU DỤC', 'sp': ['x', 'y', 'va', 'vb']},
        'locka':    {'id': 8,  'label': 'KHOÁ 1A', 'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'lockaf':   {'id': 9,  'label': 'KHOÁ 1B', 'sp': ['x', 'y', 'va', 'vb', 'vc']},
        'lockb':    {'id': 10, 'label': 'KHOÁ 2A', 'sp': ['x', 'y', 'va', 'vb', 'vc', 'vd']},
        'lockbf':   {'id': 11, 'label': 'KHOÁ 2B', 'sp': ['x', 'y', 'va', 'vb', 'vc', 'vd']},
        'custom_0': {'id': 12, 'label': 'CNC 1',   'sp': ['x', 'y']},
        'custom_1': {'id': 13, 'label': 'CNC 2',   'sp': ['x', 'y']},
        'custom_2': {'id': 14, 'label': 'CNC 3',   'sp': ['x', 'y']},
        'custom_3': {'id': 15, 'label': 'CNC 4',   'sp': ['x', 'y']},
        'custom_4': {'id': 16, 'label': 'CNC 5',   'sp': ['x', 'y']},
        'custom_5': {'id': 17, 'label': 'CNC 6',   'sp': ['x', 'y']},
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

    def clone(self):
        return Shape().copy(self)

    def copy(self, _target_):
        kv = vars(self)
        for k in kv:
            kv[k] = _target_[k]
        return self
    
    def to_json(self):
        result = {}
        kv = vars(self)
        for k in kv:
            result[k] = int(kv[k])
        return result

    def from_json(self, _value_):
        kv = vars(self)
        for k in kv:
            kv[k] = _value_[k]
    
    def limit(self):
        self.va = max(2_000, self.va)
        self.vb = max(2_000, self.vb)
        self.vc = max(2_000, self.vc)
        self.vd = max(2_000, self.vd)
        self.ve = max(2_000, self.ve)
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
                return Shape._inside_local_circle(dx, dy, self.va*0.5)
            case 2: # tap
                return Shape._inside_local_circle(dx, dy, self.va*0.5)
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
