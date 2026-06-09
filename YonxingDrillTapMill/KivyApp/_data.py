import os
import platform
import shutil
from asyncua import ua
from kivy.clock import Clock
import xml.etree.ElementTree as ET

class DataBlock(object):
    def __init__(self, _id_, _type_):
        self.id = _id_
        self.type = _type_
        self.node = {}
        self.change = 0
        self.value = None

class Data(object):
    def __init__(self, _uac_, _address_, _xml_path_windows_, _tag_head_):
        self.uac = _uac_
        self.address = _address_
        self.xml_path_windows = _xml_path_windows_
        self.tag_head = _tag_head_
        self.name__block = {}
        self.id__block = {}

    def create(self):
        current_os = platform.system()
        if current_os == 'Windows':
            shutil.copy(self.xml_path_windows, r'./tags.xml')
        path = os.path.dirname(os.path.abspath(__file__)) + '/tags.xml'
        tree = ET.parse(path)
        root = tree.getroot()
        stype__uatype = {
            'T_BOOL': ua.VariantType.Boolean,
            'T_INT': ua.VariantType.Int16,
            'T_UINT': ua.VariantType.UInt16,
            'T_DINT': ua.VariantType.Int32,
            'T_UDINT': ua.VariantType.UInt32,
            'T_STRING': ua.VariantType.String,
        }
        # user type process
        utype_last = ''
        utype__elms = {}
        level = -1
        last_is_leaf = False
        for e in root.iter():
            if 'TypeUserDef' in e.tag:
                for esub in e.iter():
                    d = esub.attrib
                    if d == {}:
                        continue
                    is_leaf = 'type' in d
                    if last_is_leaf:
                        if not is_leaf:
                            level -= 1
                    else:
                        level += 1
                    last_is_leaf = is_leaf
                    if is_leaf:
                        utype__elms[utype_last].append(d)
                    else:
                        utype_last = d['name']
                        if utype_last not in utype__elms:
                            utype__elms[utype_last] = []
        # node process
        head_part = [self.tag_head] + [''] * 5
        node__utype = {}
        level = 0
        last_is_leaf = False
        for e in root.iter():
            if 'NodeList' in e.tag:
                for esub in e.iter():
                    d = esub.attrib
                    if d == {}:
                        continue
                    is_leaf = 'type' in d
                    if last_is_leaf:
                        if not is_leaf:
                            level -= 1
                    else:
                        level += 1
                    last_is_leaf = is_leaf
                    if is_leaf:
                        head = '.'.join(item for item in head_part if item) + '.' + d['name']
                        node__utype[head] = d['type']
                    else:
                        head_part[level] = d['name']
        # generate process
        ids = []
        types = []
        for node, utype in node__utype.items():
            elms = utype__elms[utype]
            self._create_generate(node, elms, stype__uatype, utype__elms, ids, types)
        # apply process
        self.ids = ids
        head = '.'.join(item for item in head_part if item)
        for id, type in zip(ids, types):
            name = id[len(head)+1:]
            self.id__block[id] = DataBlock(id, type)
            self.name__block[name] = self.id__block[id]
    
    def _create_generate(self, _node_, _elms_, _stype__uatype_, _utype__elms_, _ids_, _types_):
        for e in _elms_:
            sname = e['iecname']
            stype = e['type']
            if stype in _stype__uatype_: # simple type
                if sname[0] == '[': # array element
                    name = '%s%s' % (_node_, sname)
                else:
                    name = '%s.%s' % (_node_, sname)
                tp = _stype__uatype_[stype]
                _ids_.append(name)
                _types_.append(tp)
            elif stype in _utype__elms_: # user define type
                elms = _utype__elms_[stype]
                self._create_generate('%s.%s' % (_node_, sname), elms, _stype__uatype_, _utype__elms_, _ids_, _types_)
            else: # array type
                name = '%s.%s' % (_node_, sname)
                part = stype.split('__')
                elms = []
                for i in range(int(part[1]), int(part[2]) + 1):
                    e = {
                        'iecname': '[%s]' % (i),
                        'type': 'T_%s' % (part[3][3:])
                    }
                    elms.append(e)
                self._create_generate('%s.%s' % (_node_, sname), elms, _stype__uatype_, _utype__elms_, _ids_, _types_)
    
    def start(self, _dt_, _step_):
        self._get_all_done = True
        self._get_all_index = 0
        self._get_all_step = _step_
        self._get_all_clock = Clock.schedule_interval(self._get_all, _dt_)
    
    def stop(self):
        if hasattr(self, '_get_all_clock'):
            Clock.unschedule(self._get_all_clock)
            delattr(self, '_get_all_clock')

    def _get_all(self, _dt_):
        if not self._get_all_done:
            return
        self._get_all_done = False
        si = self._get_all_index
        se = si + self._get_all_step
        count = len(self.ids)
        if se > count:
            self._get_all_index = 0
        else:
            self._get_all_index += self._get_all_step
        ids = self.ids[si:se]
        id__node = self.uac.id__node(ids)
        node__value = self.uac.node__value(id__node.values())
        for id in id__node:
            node = id__node[id]
            value = node__value[node]
            block = self.id__block[id]
            block.node = node
            block.value = value
            self._change_check(id, value)
        self._get_all_done = True

    def _change_check(self, _id_, _value_):
        block = self.id__block[_id_]
        if _value_ != block.value:
            block.change += 1
    
    def set(self, _name_, _value_):
        block = self.name__block[_name_]
        block.node.set_value(ua.Variant(_value_, block.type))
    
    def get(self, _name_):
        block = self.name__block[_name_]
        return block.value

    def block(self, _name_) -> DataBlock:
        return self.name__block[_name_]