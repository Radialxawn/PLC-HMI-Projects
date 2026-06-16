import sys
from core.data import Data
from data.face import Face

def testa():
    data = Data(
        _address_ip_='192.168.2.3', _address_port_=4840,
        _xml_path_windows_=r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml',
        _tag_head_='ns=4;s=|var|LS'
    )
    data.create()
    for k, v in data._name__block.items():
        print(f'Name: {k}, ID: {v.id}, Type: {v.type}')
    print(len(data._name__block), 'tags')
    bridge_names = data._download_get_bridge_names()
    for o in bridge_names:
        print(o)

def testb():
    face = Face(0, 3, 10)
    name__value = face.name__value()
    for name in name__value:
        print(name, name__value[name])

def testc():
    s = 'zs[0]'
    array = s.split('[')
    print(array, array[1][:-1])
    s = 'wtf'
    array = s.split('[')
    print(array)

parameters = sys.argv[1:]
if len(parameters) > 0:
    match parameters[0]:
        case 'a':
            testa()
        case 'b':
            testb()
        case 'c':
            testc()