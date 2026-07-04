from data.shape import Shape

class Face(object):
    property__data = {
        'ox':            {'label': ' GỐC X',           'factor': -1e-3, 'name_view': 'hmi.view_axis_tmp_micro[0]', 'local': True},
        'oy':            {'label': ' GỐC Y',           'factor': -1e-3, 'name_view': 'hmi.view_axis_tmp_micro[1]', 'local': True},
        'oz':            {'label': ' GỐC Z',           'factor': -1e-3, 'name_view': 'hmi.view_axis_tmp_micro[2]', 'local': True},
        'tool_diameter': {'label': ' ĐƯỜNG KÍNH DAO',  'factor': 1e-3},
        'tool_offset':   {'label': ' DAO LỆCH CHUẨN',  'factor': -1e-3,  'name_view': 'hmi.view_tool_offset_micro[{}]'},
        'depth':         {'label': ' ĐỘ SÂU MẶC ĐỊNH', 'factor': 1e-3},
        'feed':          {'label': ' TỐC ĐỘ (mm/min)', 'factor': 1},
    }

    index__rule = {
        0: {'property_exclude': [],                    'shape_exclude': ['tap']},
        1: {'property_exclude': [],                    'shape_exclude': ['tap']},
        2: {'property_exclude': ['tool_offset'],       'shape_exclude': ['tap']},
        3: {'property_exclude': ['oy', 'tool_diameter', 'tool_offset'], 'shape_include': ['drill']},
        4: {'property_exclude': ['tool_diameter','tool_offset'],        'shape_include': ['tap']},
        5: {'property_exclude': ['oy', 'tool_diameter', 'tool_offset'], 'shape_include': ['tap']},
    }

    def __init__(self, _index_, _z_count_, _shape_count_):
        self._index = _index_
        self.ox = 0
        self.oy = 0
        self.oz = 0
        self.z = [0]*_z_count_
        self.zs = [0]*_z_count_
        self.tool_diameter = 0
        self.tool_offset = 0
        self.depth = 0
        self.feed = 0
        self.shape = []
        for _ in range(_shape_count_):
            self.shape.append(Shape())

    def __getitem__(self, _key_):
        return getattr(self, _key_)

    def __setitem__(self, _key_, _value_):
        if _key_ in self.__dict__:
            setattr(self, _key_, _value_)
        else:
            raise Exception(f'No {_key_} in this class')
    
    def clone(self):
        return Face(self._index, len(self.z), len(self.shape)).copy(self)

    def copy(self, _target_):
        kv = vars(self)
        for k in kv:
            vt = _target_[k]
            if k == 'z' or k == 'zs':
                for i, vti in enumerate(vt):
                    kv[k][i] = vti
            elif k == 'shape':
                for i, vti in enumerate(vt):
                    kv[k][i].copy(vti)
            else:
                kv[k] = vt
        return self

    def to_json(self):
        result = {}
        kv = vars(self)
        for k in kv:
            v = kv[k]
            if k == 'z' or k == 'zs':
                result[k] = []
                for vi in v:
                    result[k].append(int(vi))
            elif k == 'shape':
                result[k] = []
                for vi in v:
                    result[k].append(vi.to_json())
            else:
                result[k] = int(v)
        return result

    def from_json(self, _value_):
        kv = vars(self)
        for k in kv:
            v = _value_[k]
            if k == 'z' or k == 'zs':
                for i, vi in enumerate(v):
                    kv[k][i] = vi
            elif k == 'shape':
                for i, vi in enumerate(v):
                    kv[k][i].from_json(vi)
            else:
                kv[k] = v

    def limit(self):
        for i, v in enumerate(self.z):
            self.z[i] = max(0, v)
        for i, v in enumerate(self.zs):
            self.zs[i] = min(self.z[i], v)
        self.tool_diameter = max(0, self.tool_diameter)
        self.depth = max(0, self.depth)
        self.feed = max(1, self.feed)
        for shape in self.shape:
            shape.limit()

    def name__value(self):
        head = f'hmi.face[{self._index}]'
        kv = vars(self)
        n__v = {}
        for k in kv:
            v = kv[k]
            if k == 'z' or k == 'zs':
                for i, iv in enumerate(v):
                    n__v[f'{head}.{k}[{i}]'] = iv
            elif k == 'shape':
                for index, value in enumerate(v):
                    s_kv = vars(value)
                    for s_k in s_kv:
                        s_v = s_kv[s_k]
                        n__v[f'{head}.shape[{index}].{s_k}'] = s_v
            elif k[0] != '_':
                n__v[f'{head}.{k}'] = v
        return n__v

    def index_get(self):
        return self._index