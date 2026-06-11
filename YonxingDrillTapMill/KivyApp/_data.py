import os
import shutil
import socket
import platform
import subprocess
from asyncua import ua
from pathlib import Path
from kivy.clock import Clock
from asyncua.sync import Client
import xml.etree.ElementTree as ET

class DataBlock(object):
    def __init__(self, _id_, _type_):
        self.id = _id_
        self.type = _type_
        self.node = {}
        self.change = 0
        self.value = None
        self.get = False

class Data(object):
    def __init__(self, _address_ip_, _address_port_, _xml_path_windows_, _tag_head_):
        self.address_ip = _address_ip_
        self.address_port = _address_port_
        self.xml_path_windows = _xml_path_windows_
        self.tag_head = _tag_head_
        self.name__block = {}
        self.id__block = {}
        self.client = None
        self._connect_state = 0
    
    def _reset(self):
        self.client = None
        self._connect_state = 0

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
            'T_STRING_255_': ua.VariantType.String,
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
    
    def _get_all_start(self):
        self._get_all_done = True
        self._get_all_index = 0
        self._get_all_clock = Clock.schedule_interval(self._get_all, self._get_all_interval)
    
    def _get_all_stop(self):
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
        id__node = self.id__node(ids)
        node__value = self.node__value(id__node.values())
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
        if self._connect_state == 100:
            block = self.name__block[_name_]
            block.node.set_value(ua.Variant(_value_, block.type))
    
    def get(self, _name_):
        if self._connect_state == 100:
            block = self.name__block[_name_]
            return block.value
        return None

    def block(self, _name_) -> DataBlock:
        return self.name__block[_name_]

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
        return self._is_ip_active(self.address_ip, self.address_port, 0.1)

    def connect_state(self):
        return self._connect_state

    def connect(self, _interval_, _step_):
        if not self.can_connect():
            print(f'Cannot connect to {self.address_ip}')
            return
        self._connect_state = 10
        address = 'opc.tcp://%s:%d' % (self.address_ip, self.address_port)
        self.client = Client(address)
        self.client.connect()
        self.client.load_data_type_definitions()
        self.client.load_enums()
        self.client.load_type_definitions()
        self._connect_state = 100
        self._get_all_interval = _interval_
        self._get_all_step = _step_
        self._get_all_start()
        print('Connected')

    def disconnect(self):
        if self._connect_state != 100:
            return
        self._get_all_stop()
        self._connect_state = 90
        if self.can_connect():
            self.client.disconnect()
        self._reset()
        print("Disconnected")

    def id__node(self, _ids_):
        if self._connect_state == 100:
            nodes = [self.client.get_node(id) for id in _ids_]
            return dict(zip(_ids_, nodes))
        return None
    
    def node__value(self, _nodes_):
        if self._connect_state == 100:
            values = self.client.read_values(_nodes_)
            return dict(zip(_nodes_, values))
        return None

    #################
    # DATA DOWNLOAD #
    #################

    def _download_read_file(self, _path_):
        path = Path(_path_)
        if not path.is_file():
            print('File does not exist: %s' % (_path_))
            return []
        combine = ''
        with path.open(mode='r') as file:
            index = 0
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    combine += f'N{index} {line}\r\n'
                    index += 1
        chunk_size = 255
        result = [
            combine[i : i + chunk_size]
            for i in range(0, len(combine), chunk_size)
        ]
        return result

    def _download_get_bridge_ids(self):
        return [self.name__block[n].id for n in self.name__block if n[:3] == 'fst']

    def download_start(self, _source_path_, _destination_index_, _progress_):
        if self._connect_state != 100:
            print('Not connected')
            return
        if hasattr(self, '_download_process_clock'):
            print('File downloading')
            return
        if not hasattr(self, '_dl'):
            self._dl = {
                'line_index': 0,
                'progress': _progress_,
            }
        dl = self._dl
        dl['index'] = _destination_index_
        dl['lines'] = self._download_read_file(_source_path_)
        if len(dl['lines']) == 0:
            return
        dl['bridge_ids'] = self._download_get_bridge_ids()
        self._get_all_stop()
        dl['state'] = 1
        self._download_process_clock = Clock.schedule_interval(self._download_process, 0.001)

    def _download_process(self, _):
        dl = self._dl
        line_count = len(dl['lines'])
        id__node = self.id__node(dl['bridge_ids'])
        node__value = self.node__value(id__node.values())
        for id in id__node:
            node = id__node[id]
            value = node__value[node]
            block = self.id__block[id]
            block.node = node
            block.value = value
        match dl['state']:
            case 1:
                if self.get('fst.state') == 10:
                    self.set('fst.index', dl['index'])
                    dl['line_index'] = 0
                    dl['state'] += 1
            case 2:
                if self.get('fst.index') == dl['index']:
                    dl['state'] += 1
            case 3:
                self.set('fst.begin', True)
                dl['state'] = 11
            ##########
            case 11:
                if self.get('fst.state') == 21:
                    if dl['line_index'] >= line_count:
                        dl['state'] = 99
                    else:
                        self.set('fst.line', dl['lines'][dl['line_index']])
                        dl['state'] += 1
            case 12:
                if self.get('fst.line') == dl['lines'][dl['line_index']]:
                    dl['line_index'] += 1
                    dl['state'] += 1
            case 13:
                if self.get('fst.state') == 30:
                    dl['progress'](dl['line_index'] * 100 / line_count)
                    self.set('fst.next', True)
                    dl['state'] = 11
            ##########
            case 99:
                if self.get('fst.state') == 10:
                    dl['state'] += 1
            case 100:
                Clock.unschedule(self._download_process_clock)
                delattr(self, '_download_process_clock')
                dl['state'] = 0
                dl['progress'](100)
                self._get_all_start()

    def stop(self):
        if hasattr(self, '_download_index_clock'):
            Clock.unschedule(self._download_index_clock)
            delattr(self, '_download_index_clock')
        if hasattr(self, '_download_line_clock'):
            Clock.unschedule(self._download_line_clock)
            delattr(self, '_download_line_clock')