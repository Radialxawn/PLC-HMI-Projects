from kivy.clock import Clock

class Data(object):
    def __init__(self, _uac_):
        self.address = 'opc.tcp://192.168.2.3:4840'
        self.nms = []
        self.ids = []
        self.nm__id = {}
        self.id__no = {}
        self.no__vl = {}
        self.no__change = {}
        self._uac = _uac_
        self._get_done = False
    
    def start(self, _dt_):
        self._get_done = True
        self._get_clock = Clock.schedule_interval(self._get, _dt_)
    
    def stop(self):
        if hasattr(self, '_get_clock'):
            Clock.unschedule(self._get_clock)
            delattr(self, '_get_clock')

    def _get(self, _dt_):
        if not self._get_done:
            return
        self._get_done = False
        id__no = self._uac.get_id__node(self.ids)
        no__vl = self._uac.get_node__value(id__no.values())
        for k, v in no__vl.items():
            self._check(k, v)
        self.id__no = id__no
        self.no__vl = no__vl
        self._get_done = True

    def _check(self, _node_, _value_):
        if _node_ in self.no__vl:
            value_last = self.no__vl[_node_]
            if _value_ != value_last:
                if _node_ not in self.no__change:
                    self.no__change[_node_] = 1
                else:
                    self.no__change[_node_] += 1
    
    def set(self, _id_head_, _names_):
        self.nms = _names_
        self.ids = [(_id_head_ + n) for n in _names_]
        self.nm__id = dict(zip(_names_, self.ids))
    
    def node(self, _name_):
        id = self.nm__id[_name_]
        return self.id__no[id]

    def value(self, _name_):
        no = self.node(_name_)
        return self.no__vl[no]

    def change(self, _name_):
        no = self.node(_name_)
        return self.no__change[no]