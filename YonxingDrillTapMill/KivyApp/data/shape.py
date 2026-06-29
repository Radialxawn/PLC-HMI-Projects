from kivy.app import App
from core.helper import Helper

class Shape(object):
    property__data = {
        'x':  {'label': ' X', 'factor': -1e-3},
        'y':  {'label': ' Y', 'factor': -1e-3},
        '0': None,
        'va': {'label': ' A', 'factor': 1e-3},
        'vb': {'label': ' B', 'factor': 1e-3},
        'vc': {'label': ' C', 'factor': 1e-3},
        'vd': {'label': ' D', 'factor': 1e-3},
        've': {'label': ' E', 'factor': 1e-3},
    }

    shape_name__data = {
        'none':     {'id': 0,  'label': '...',     'property__data': {}},
        'drill':    {'id': 1,  'label': 'KHOAN',   'property__data': {'x': None, 'y': None,
                'va': ' Z',
                'vb': ' F'
            },
            'view_micro': 100_000
        },
        'tap':      {'id': 2,  'label': 'TARO',    'property__data': {'x': None, 'y': None,
                'va': ' Z',
                'vb': ' RPM'
            },
            'view_micro': 100_000
        },
        'circle':   {'id': 3,  'label': 'TRÒN',     'property__data': {'x': None, 'y': None, 'va': None, 'vb': None}},
        'circles':  {'id': 4,  'label': 'TRÒN ĐẶC', 'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 've': 'BƯỚC'}},
        'rect':     {'id': 5,  'label': 'HỘP',      'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None}},
        'rects':    {'id': 6,  'label': 'HỘP ĐẶC',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 've': 'BƯỚC'}},
        'locka':    {'id': 7,  'label': 'KHOÁ 1A',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None}},
        'lockaf':   {'id': 8,  'label': 'KHOÁ 1B',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None}},
        'lockb':    {'id': 9,  'label': 'KHOÁ 2A',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 'vd': None}},
        'lockbf':   {'id': 10, 'label': 'KHOÁ 2B',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 'vd': None}},
        # custom
        'custom_0': {'id': 11, 'label': 'CNC 1',   'property__data': {'x': None, 'y': None,
            },
            'view_micro': 100_000
        },
        'custom_1': {'id': 12, 'label': 'CNC 2',   'property__data': {'x': None, 'y': None,}},
        'custom_2': {'id': 13, 'label': 'CNC 3',   'property__data': {'x': None, 'y': None,}},
        'custom_3': {'id': 14, 'label': 'CNC 4',   'property__data': {'x': None, 'y': None,}},
        'custom_4': {'id': 15, 'label': 'CNC 5',   'property__data': {'x': None, 'y': None,}},
        'custom_5': {'id': 16, 'label': 'CNC 6',   'property__data': {'x': None, 'y': None,}},
        'custom_6': {'id': 17, 'label': 'CNC 7',   'property__data': {'x': None, 'y': None,}},
        'custom_7': {'id': 18, 'label': 'CNC 8',   'property__data': {'x': None, 'y': None,}},
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
        self.va = max(1_000, self.va)
        self.vb = max(1_000, self.vb)
        self.vc = max(0, self.vc)
        self.vd = max(0, self.vd)
        self.ve = max(0, self.ve)
        match self.id:
            case 3: # circle
                if self.va < self.vb:
                    self.va = int(max(self.vb*0.25, self.va))
                elif self.vb < self.va:
                    self.vb = int(max(self.va*0.25, self.vb))
            case 4: # circles
                if self.va < self.vb:
                    self.va = int(max(self.vb*0.25, self.va))
                elif self.vb < self.va:
                    self.vb = int(max(self.va*0.25, self.vb))
                self.ve = min(self.ve, max(self.va, self.vb)*0.5)
            case 5: # rect
                self.vc = int(min(self.va*0.5, self.vb*0.5, self.vc))
            case 6: # rects
                self.vc = int(min(self.va*0.5, self.vb*0.5, self.vc))
                self.ve = min(self.ve, max(self.va, self.vb)*0.5)
            case 7: # locka
                self.vb = int(min(self.va, self.vb))
            case 8: # lockaf
                self.vb = int(min(self.va, self.vb))
            case 9: # lockb
                self.vb = int(min(self.va, self.vb))
            case 10: # lockbf
                self.vb = int(min(self.va, self.vb))
        scid = Shape.get_custom_id(self.id)
        if scid >= 0:
            image, _ = Helper.cnc_preview_image_get(_index_=scid, _image_=False)
            if image == None:
                self.id = 0

    def contain(self, _lx_, _ly_, _r_):
        dx = _lx_ - self.x
        dy = _ly_ - self.y
        match self.id:
            case 0:
                return False
            case 1: # drill
                sa = Shape.shape_name__data['drill']['view_micro']
                return Shape._inside_local_circle(dx, dy, sa*0.5)
            case 2: # tap
                sa = Shape.shape_name__data['tap']['view_micro']
                return Shape._inside_local_circle(dx, dy, sa*0.5)
            case 3: # circle
                return Shape._inside_local_ellipse(dx, dy, self.va, self.vb)
            case 4: # circles
                return Shape._inside_local_ellipse(dx, dy, self.va, self.vb)
            case 5: # rect
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vc)
            case 6: # rects
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vc)
            case 7: # locka
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx-(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case 8: # lockaf
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx+(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case 9: # lockb
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy+ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
            case 10: # lockbf
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy-ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
        sa = Shape.shape_name__data['custom_0']['view_micro']
        return Shape._inside_local_rect_r(dx, dy, sa, sa, 0)

    @staticmethod
    def _inside_local_circle(_dx_, _dy_, _r_):
        return  (_dx_ * _dx_ + _dy_ * _dy_) < (_r_ * _r_)

    @staticmethod
    def _inside_local_ellipse(_dx_, _dy_, _a_, _b_):
        if _a_ == 0 or _b_ == 0:
            return False
        a = _a_ * 0.5
        b = _b_ * 0.5
        return _dx_*_dx_/(a*a) + _dy_*_dy_/(b*b) <= 1.0

    @staticmethod
    def _inside_local_rect_r(_dx_, _dy_, _w_, _h_, _r_):
        hw, hh = _w_ * 0.5, _h_ * 0.5
        dx, dy = abs(_dx_), abs(_dy_)
        if dx > hw or dy > hh:
            return False
        inner_w = hw - _r_
        inner_h = hh - _r_
        if dx <= inner_w or dy <= inner_h:
            return True
        tx = dx - inner_w
        ty = dy - inner_h
        return (tx * tx + ty * ty) <= (_r_ * _r_)

    @staticmethod
    def get_custom_id(_id_):
        base_i_max = 10
        if _id_ > base_i_max:
            _id_ -= base_i_max + 1
            return _id_
        return -1
        
