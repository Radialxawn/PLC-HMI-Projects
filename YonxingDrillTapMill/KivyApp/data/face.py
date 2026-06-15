from data.shape import Shape

class Face(object):
    def __init__(self, _index_, _z_count_, _shape_count_):
        self._index_ = _index_
        self.ox = 0
        self.oy = 0
        self.oz = 0
        self.z = [0]*_z_count_
        self.zs = [0]*_z_count_
        self.tool_d = 0
        self.depth = 0
        self.feed = 0
        self.index__shape = {}
        for i in range(_shape_count_):
            self.index__shape[i] = Shape()

    def __getitem__(self, _key_):
        return getattr(self, _key_)

    def __setitem__(self, _key_, _value_):
        if _key_ in self.__dict__:
            setattr(self, _key_, _value_)
        else:
            raise Exception(f'No {_key_} in this class')

    def from_json(self):
        return

    def name__value(self):
        head = f'hmi.face[{self._index_}]'
        kv = vars(self)
        n__v = {}
        for k in kv:
            v = kv[k]
            if k == 'z' or k == 'zs':
                for i, iv in enumerate(v):
                    n__v[f'{head}.{k}[{i}]'] = iv
            elif k == 'index__shape':
                for index in v:
                    s_kv = vars(v[index])
                    for s_k in s_kv:
                        s_v = s_kv[s_k]
                        n__v[f'{head}.shape[{index}].{s_k}'] = s_v
            elif k[0] != '_':
                n__v[f'{head}.{k}'] = v
        return n__v