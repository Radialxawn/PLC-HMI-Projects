from data.shape import Shape

class Face(object):
    def __init__(self, _index_, _z_count_, _shape_count_):
        self._index = _index_
        self.ox = 0
        self.oy = 0
        self.oz = 0
        self.z = [0]*_z_count_
        self.zs = [0]*_z_count_
        self.tool_d = 0
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