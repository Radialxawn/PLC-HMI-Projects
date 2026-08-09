import shutil
import socket
import platform
from asyncua import ua
from pathlib import Path
from kivy.clock import Clock
from asyncua.sync import Client
from types import SimpleNamespace
import xml.etree.ElementTree as ET

class DataBlock(object):
    stype__uatype = {
        'T_BOOL': ua.VariantType.Boolean,
        'T_INT': ua.VariantType.Int16,
        'T_UINT': ua.VariantType.UInt16,
        'T_DINT': ua.VariantType.Int32,
        'T_UDINT': ua.VariantType.UInt32,
        'T_STRING': ua.VariantType.String,
        'T_STRING_GVL_c_line_size_': ua.VariantType.String,
    }

    def __init__(self, _id_, _type_):
        self.id = _id_
        self.type = _type_
        self.node = {}
        self.value = None
        self.active = False

    @staticmethod
    def _clamp(_value_, _a_, _b_):
        if _value_ < _a_:
            return _a_
        elif _value_ > _b_:
            return _b_
        return _value_

    def get_ua_value(self, _value_):
        match self.type:
            case ua.VariantType.Int16:
                _value_ = int(DataBlock._clamp(_value_, -32768, 32767))
            case ua.VariantType.UInt16:
                _value_ = int(DataBlock._clamp(_value_, 0, 65535))
            case ua.VariantType.Int32:
                _value_ = int(DataBlock._clamp(_value_, -2147483648, 2147483647))
            case ua.VariantType.UInt32:
                _value_ = int(DataBlock._clamp(_value_, 0, 4294967295))
        return ua.Variant(_value_, self.type)

class Data(object):
    DOWNLOAD_CHUNK_SIZE = 4095

    def __init__(self, _address_ip_, _address_port_, _xml_path_windows_, _tag_head_):
        self._address_ip_ = _address_ip_
        self._address_port_ = _address_port_
        self._xml_path_windows_ = _xml_path_windows_
        self._tag_head_ = _tag_head_
        self._names = []
        self._name__block = {}
        self._id__block = {}
        self._client = None
        self._connect_state = 0
    
    def _reset(self):
        self._client = None
        self._connect_state = 0

    def create(self):
        if platform.system() == 'Windows':
            shutil.copy(self._xml_path_windows_, r'./tags.xml')
        tags_path = Path(Path(__file__).resolve().parent.parent, 'tags.xml')
        tree = ET.parse(tags_path)
        root = tree.getroot()
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
        head_part = [self._tag_head_] + [''] * 5
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
            self._create_generate(node, elms, utype__elms, ids, types)
        # apply process
        self.ids = ids
        head = '.'.join(item for item in head_part if item)
        for id, type in zip(ids, types):
            name = id[len(head)+1:]
            self._id__block[id] = DataBlock(id, type)
            self._name__block[name] = self._id__block[id]
            self._names.append(name)
    
    def _create_generate(self, _node_, _elms_, _utype__elms_, _ids_, _types_):
        for e in _elms_:
            sname = e['iecname']
            stype = e['type']
            if stype in DataBlock.stype__uatype: # simple type
                if sname[0] == '[': # array element
                    name = '%s%s' % (_node_, sname)
                else:
                    name = '%s.%s' % (_node_, sname)
                tp = DataBlock.stype__uatype[stype]
                _ids_.append(name)
                _types_.append(tp)
            elif stype in _utype__elms_: # user define type
                elms = _utype__elms_[stype]
                dot = '' if sname[0] == '[' else '.'
                self._create_generate('%s%s%s' % (_node_, dot, sname), elms, _utype__elms_, _ids_, _types_)
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
                self._create_generate('%s.%s' % (_node_, sname), elms, _utype__elms_, _ids_, _types_)
    
    def get_all_start(self):
        if hasattr(self, '_get_all_clock'):
            return
        print('Data get all start')
        self._get_all_done = True
        self._get_all_index = 0
        self._get_all_clock = Clock.schedule_interval(self._get_all, self._get_all_interval)
    
    def get_all_stop(self):
        if hasattr(self, '_get_all_clock'):
            Clock.unschedule(self._get_all_clock)
            delattr(self, '_get_all_clock')
            print('Data get all stop')

    def _get_all(self, _dt_):
        if not self._get_all_done:
            return
        self._get_all_done = False
        names = []
        count = len(self._names)
        for i in range(count):
            ioff = (i + self._get_all_index) % count
            name = self._names[ioff]
            block = self._name__block[name]
            if block.active:
                names.append(name)
                if len(names) >= self._get_all_step:
                    break
        self._get_all_index = (self._get_all_index + self._get_all_step) % count
        self.gets(names)
        self._get_all_done = True
    
    def get(self, _name_): # get local data
        if self._connect_state == 100:
            block = self._name__block[_name_]
            return block.value
        return None
    
    def gets(self, _names_): # get ua nodes
        if self._connect_state == 100:
            nodes = []
            for name in _names_:
                block = self._name__block[name]
                nodes.append(self._client.get_node(block.id))
            if len(nodes) > 0:
                values = self._client.read_values(nodes)
            for i, node in enumerate(nodes):
                block = self._name__block[_names_[i]]
                block.node = node
                block.value = values[i]

    def set(self, _name_, _value_): # set ua node
        if self._connect_state == 100:
            block = self._name__block[_name_]
            block.node.set_value(block.get_ua_value(_value_))
    
    def sets(self, _name__value_): # set ua nodes
        if self._connect_state == 100:
            nodes = []
            values = []
            for name in _name__value_:
                block = self._name__block[name]
                nodes.append(self._client.get_node(block.id))
                values.append(block.get_ua_value(_name__value_[name]))
            self._client.write_values(nodes, values)

    def all(self, _name__value_):
        for name in _name__value_:
            block = self._name__block[name]
            if _name__value_[name] != block.value:
                return False
        return True

    def block(self, _name_) -> DataBlock:
        return self._name__block[_name_]

    def block_active(self, *_name__hash_):
        for name in self._name__block:
            inside = False
            for name__hash in _name__hash_:
                inside = inside or name in name__hash
            self._name__block[name].active = inside

    def all_name_get(self):
        return list(self._name__block)

    ###################
    # DATA CONNECTION #
    ###################

    def _is_ip_active(self, _ip_, _port_, _timeout_):
        address_family = socket.AF_INET6 if ":" in _ip_ else socket.AF_INET
        with socket.socket(address_family, socket.SOCK_STREAM) as s:
            s.settimeout(_timeout_)
            try:
                result = s.connect_ex((_ip_, _port_))
                return result == 0
            except socket.error:
                return False
    
    def can_connect(self):
        return self._is_ip_active(self._address_ip_, self._address_port_, 0.1)

    def connect_state(self):
        return self._connect_state

    def connect(self, _interval_, _step_):
        if not self.can_connect():
            print(f'Cannot connect to {self._address_ip_}')
            return
        self._connect_state = 10
        address = 'opc.tcp://%s:%d' % (self._address_ip_, self._address_port_)
        self._client = Client(address)
        self._client.connect()
        self._client.load_data_type_definitions()
        self._client.load_enums()
        self._client.load_type_definitions()
        self._connect_state = 100
        self._get_all_interval = _interval_
        self._get_all_step = _step_
        self.get_all_start()
        print('Connected')

    def disconnect(self):
        if self._connect_state != 100:
            return
        self.get_all_stop()
        self._connect_state = 90
        if self.can_connect():
            self._client.disconnect()
        self._reset()
        print("Disconnected")

    #################
    # DATA DOWNLOAD #
    #################
    def _download_get_bridge_names(self):
        return [n for n in self._name__block if n[:3] == 'fst']

    def download_start(self, _index_, _chunks_, _progress_):
        if hasattr(self, '_download_process_clock'):
            print('File downloading')
            return
        if self._connect_state != 100:
            print('Not connected')
            return
        self._dl = SimpleNamespace(
            index=_index_,
            chunks=_chunks_,
            progress=_progress_,
            bridge_names=self._download_get_bridge_names(),
            chunk_index=0,
            cancel=False,
            state=1
        )
        self.get_all_stop()
        self.gets(self._dl.bridge_names)
        self._download_process_clock = Clock.schedule_interval(self._download_process, 0.001)

    def _download_process(self, _):
        dl = self._dl
        line_count = len(dl.chunks)
        for name in dl.bridge_names:
            self.block(name).value = None
        if dl.cancel:
            dl.state = 100
        match dl.state:
            case 1:
                self.gets(['fst.state'])
                if self.get('fst.state') == 10:
                    self.set('fst.index', dl.index)
                    dl.chunk_index = 0
                    dl.state += 1
            case 2:
                self.gets(['fst.index'])
                if self.get('fst.index') == dl.index:
                    dl.state += 1
            case 3:
                self.set('fst.begin', True)
                dl.state = 11
            ##########
            case 11:
                self.gets(['fst.state'])
                if self.get('fst.state') == 21:
                    if dl.chunk_index >= line_count:
                        dl.state = 99
                    else:
                        self.block('fst.line').value = None
                        self.set('fst.line', dl.chunks[dl.chunk_index])
                        dl.state += 1
            case 12:
                self.gets(['fst.line'])
                if self.get('fst.line') == dl.chunks[dl.chunk_index]:
                    self.set('fst.lbegin', True)
                    dl.state += 1
            case 13:
                self.gets(['fst.state'])
                if self.get('fst.state') == 30:
                    dl.chunk_index += 1
                    dl.progress(dl.chunk_index * 100 / line_count)
                    self.set('fst.lnext', True)
                    dl.state = 11
            ##########
            case 99:
                self.gets(['fst.state'])
                if self.get('fst.state') == 10:
                    dl.state += 1
            case 100:
                Clock.unschedule(self._download_process_clock)
                delattr(self, '_download_process_clock')
                dl.state = 0
                if dl.cancel:
                    dl.progress(-1)
                else:
                    dl.progress(101)
                self.get_all_start()
    
    def download_cancel(self):
        if hasattr(self, '_dl'):
            self._dl.cancel = True