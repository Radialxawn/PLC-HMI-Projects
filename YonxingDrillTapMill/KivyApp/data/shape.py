from enum import Enum
from kivy.app import App
from core.helper import Helper

class ShapeID(Enum):
    NONE    = 0
    FACEX   = 1
    FACEY   = 2
    DRILL   = 3
    TAP     = 4
    CIRCLE  = 5
    CIRCLES = 6
    RECT    = 7
    RECTS   = 8
    LOCKA   = 9
    LOCKAF  = 10
    LOCKB   = 11
    LOCKBF  = 12
    CT0     = 13
    CT1     = 14
    CT2     = 15
    CT3     = 16
    CT4     = 17
    CT5     = 18
    CT6     = 19
    CT7     = 20

class Shape(object):
    property__data = {
        'x':     {'label': ' X', 'factor': -1e-3},
        'y':     {'label': ' Y', 'factor': -1e-3},
        '0':     None,
        'va':    {'label': ' A', 'factor': 1e-3},
        'vb':    {'label': ' B', 'factor': 1e-3},
        'vc':    {'label': ' C', 'factor': 1e-3},
        'vd':    {'label': ' D', 'factor': 1e-3},
        've':    {'label': ' E', 'factor': 1e-3},
        'vmode': {'label': 'MODE', 'state_text': ['NGHỊCH', 'THUẬN']},
    }

    shape_id__data = {
        ShapeID.NONE:    {'label': '...',      'property__data': {}},
        ShapeID.FACEX:   {'label': 'MẶT X',    'property__data': {'x': None, 'y': None, 'va': None, 'vb': None,             've': 'BƯỚC', 'vmode': None}},
        ShapeID.FACEY:   {'label': 'MẶT Y',    'property__data': {'x': None, 'y': None, 'va': None, 'vb': None,             've': 'BƯỚC', 'vmode': None}},
        ShapeID.DRILL:   {'label': 'KHOAN',    'property__data': {'x': None, 'y': None, 'va': ' Z', 'vb': ' F', 'vc': ' R', 've': 'BƯỚC'}, 'view_micro': 100_000},
        ShapeID.TAP:     {'label': 'TARO',     'property__data': {'x': None, 'y': None, 'va': ' Z', 'vb': ' RPM',           've': 'BƯỚC'}, 'view_micro': 100_000},
        ShapeID.CIRCLE:  {'label': 'TRÒN',     'property__data': {'x': None, 'y': None, 'va': None, 'vb': None,                           'vmode': None}},
        ShapeID.CIRCLES: {'label': 'TRÒN ĐẶC', 'property__data': {'x': None, 'y': None, 'va': None, 'vb': None,             've': 'BƯỚC', 'vmode': None}},
        ShapeID.RECT:    {'label': 'HỘP',      'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None,               'vmode': None}},
        ShapeID.RECTS:   {'label': 'HỘP ĐẶC',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 've': 'BƯỚC', 'vmode': None}},
        ShapeID.LOCKA:   {'label': 'KHOÁ 1A',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None,               'vmode': None}},
        ShapeID.LOCKAF:  {'label': 'KHOÁ 1B',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None,               'vmode': None}},
        ShapeID.LOCKB:   {'label': 'KHOÁ 2A',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 'vd': None,   'vmode': None}},
        ShapeID.LOCKBF:  {'label': 'KHOÁ 2B',  'property__data': {'x': None, 'y': None, 'va': None, 'vb': None, 'vc': None, 'vd': None,   'vmode': None}},
        # custom
        ShapeID.CT0: {'label': 'CNC 1',   'property__data': {'x': None, 'y': None,}, 'view_micro': 100_000},
        ShapeID.CT1: {'label': 'CNC 2',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT2: {'label': 'CNC 3',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT3: {'label': 'CNC 4',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT4: {'label': 'CNC 5',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT5: {'label': 'CNC 6',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT6: {'label': 'CNC 7',   'property__data': {'x': None, 'y': None,}},
        ShapeID.CT7: {'label': 'CNC 8',   'property__data': {'x': None, 'y': None,}},
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
        self.vmode = 0
    
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
            case ShapeID.DRILL.value:
                self.vc = max(0, min(self.vc, 5_000))
                self.ve = max(100, min(self.ve, self.va))
            case ShapeID.TAP.value:
                self.ve = max(100, min(self.ve, self.va))
            case ShapeID.FACEX.value:
                self.ve = max(100, min(self.ve, self.vb*0.5))
            case ShapeID.FACEY.value:
                self.ve = max(100, min(self.ve, self.va*0.5))
            case ShapeID.CIRCLE.value:
                if self.va < self.vb:
                    self.va = int(max(self.vb*0.25, self.va))
                elif self.vb < self.va:
                    self.vb = int(max(self.va*0.25, self.vb))
            case ShapeID.CIRCLES.value:
                if self.va < self.vb:
                    self.va = int(max(self.vb*0.25, self.va))
                elif self.vb < self.va:
                    self.vb = int(max(self.va*0.25, self.vb))
                self.ve = min(self.ve, max(self.va, self.vb)*0.5)
            case ShapeID.RECT.value:
                self.vc = int(min(self.va*0.5, self.vb*0.5, self.vc))
            case ShapeID.RECTS.value:
                self.vc = int(min(self.va*0.5, self.vb*0.5, self.vc))
                self.ve = min(self.ve, max(self.va, self.vb)*0.5)
            case ShapeID.LOCKA.value:
                self.vb = int(min(self.va, self.vb))
            case ShapeID.LOCKAF.value:
                self.vb = int(min(self.va, self.vb))
            case ShapeID.LOCKB.value:
                self.vb = int(min(self.va, self.vb))
            case ShapeID.LOCKBF.value:
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
            case ShapeID.NONE.value:
                return False
            case ShapeID.FACEX.value:
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, 0)
            case ShapeID.FACEY.value:
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, 0)
            case ShapeID.DRILL.value:
                sa = Shape.shape_id__data[ShapeID.DRILL]['view_micro']
                return Shape._inside_local_circle(dx, dy, sa*0.5)
            case ShapeID.TAP.value:
                sa = Shape.shape_id__data[ShapeID.TAP]['view_micro']
                return Shape._inside_local_circle(dx, dy, sa*0.5)
            case ShapeID.CIRCLE.value:
                return Shape._inside_local_ellipse(dx, dy, self.va, self.vb)
            case ShapeID.CIRCLES.value:
                return Shape._inside_local_ellipse(dx, dy, self.va, self.vb)
            case ShapeID.RECT.value:
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, 0)
            case ShapeID.RECTS.value:
                return Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vc)
            case ShapeID.LOCKA.value:
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx-(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case ShapeID.LOCKAF.value:
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_circle = Shape._inside_local_circle(dx+(self.va-self.vc)*0.5, dy, self.vc*0.5)
                return inside_capsule or inside_circle
            case ShapeID.LOCKB.value:
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy+ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
            case ShapeID.LOCKBF.value:
                ky = (self.vc - self.vb) * 0.5
                inside_capsule = Shape._inside_local_rect_r(dx, dy, self.va, self.vb, self.vb*0.5)
                inside_rect = Shape._inside_local_rect_r(dx, dy-ky, self.vd, self.vc, 0)
                return inside_capsule or inside_rect
        sa = Shape.shape_id__data[ShapeID.CT0]['view_micro']
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
        base_i_max = ShapeID.CT0.value - 1
        if _id_ > base_i_max:
            _id_ -= base_i_max + 1
            return _id_
        return -1

    def default(self):
        match self.id:
            case ShapeID.FACEX.value:
                self.va, self.vb, self.ve = 50_000, 25_000, 5_000
            case ShapeID.FACEY.value:
                self.va, self.vb, self.ve = 25_000, 50_000, 5_000
            case ShapeID.DRILL.value:
                self.va, self.vb, self.vc, self.ve = 10_000, 600_000, 0, 10_000
            case ShapeID.TAP.value:
                self.va, self.vb, self.ve = 10_000, 900_000, 10_000
            case ShapeID.CIRCLE.value:
                self.va, self.vb = 50_000, 50_000
            case ShapeID.CIRCLES.value:
                self.va, self.vb, self.ve = 50_000, 50_000, 5_000
            case ShapeID.RECT.value:
                self.va, self.vb, self.vc = 50_000, 50_000, 5_000
            case ShapeID.RECTS.value:
                self.va, self.vb, self.vc, self.ve = 50_000, 50_000, 5_000, 5_000
            case ShapeID.LOCKA.value:
                self.va, self.vb, self.vc = 80_000, 20_000, 35_000
            case ShapeID.LOCKAF.value:
                self.va, self.vb, self.vc = 80_000, 20_000, 35_000
            case ShapeID.LOCKB.value:
                self.va, self.vb, self.vc, self.vd = 80_000, 20_000, 30_000, 35_000
            case ShapeID.LOCKBF.value:
                self.va, self.vb, self.vc, self.vd = 80_000, 20_000, 30_000, 35_000