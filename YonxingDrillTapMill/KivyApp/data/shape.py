class Shape(object):
    name__id = {
        'NONE':     0,
        'DRILL':    1,
        'TAP':      2,
        'CIRCLE':   3,
        'RECT':     4,
        'CAPSULE':  5,
        'RECT-R':   6,
        'ELLIPSE':  7,
        'LOCKA':    8,
        'LOCKA-F':  9,
        'LOCKB':    10,
        'LOCKB-F':  11,
        'CNC-1':    12,
        'CNC-2':    13,
        'CNC-3':    14,
        'CNC-4':    15,
        'CNC-5':    16,
        'CNC-6':    17,
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

    def contain(self, _lx_, _ly_, _indicator_radius_):
        dx = _lx_ - self.x
        dy = _ly_ - self.y
        dsq = dx*dx + dy*dy
        match self.id:
            case 0: # none
                return False
            case 1: # drill
                return False
            case 2: # tap
                return False
            case 3: # circle
                r = self.va * 0.5
                return dsq < r*r
        return dsq < _indicator_radius_*_indicator_radius_