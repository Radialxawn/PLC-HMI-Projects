import re
import sys
from pathlib import Path
from core.data import Data
from data.face import Face
from core.helper import Helper
import matplotlib.pyplot as pyplot
from screen.screen_load import ScreenLoad

machine = ScreenLoad.config_machine_load()

def testa():
    data = Data(
        _address_ip_='192.168.2.3', _address_port_=4840,
        _xml_path_windows_=Path(f'../MC500/MC500.Device.Application.xml'),
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
    print('Name count:', len(name__value))

def testc():
    a = {'a'}
    b = {'b'}
    ab(a, b)

def ab(*params):
    for param in params:
        print(param)

def testd(_name_, _index_):
    path = Helper.path_get('CNC') / f'{_name_}.cnc'
    gcode = None
    try:
        gcode = Helper.gcode_read(path)
    except Exception as error:
        print(error)
        return
    Helper.cnc_preview_image_generate(
        _gcode_=gcode,
        _index_=_index_,
    )
    image, pixel_per_mm = Helper.cnc_preview_image_get(_index_=_index_, _image_=True)
    print(image, 'pixel_per_mm', pixel_per_mm)

def teste():
    path = Path('D:/Download')
    first = []
    for i in range(8):
        pf = path / f'custom_{i}.cnc'
        j = 0
        with pf.open(mode='r') as file:
            for l in file:
                if i == 0:
                    first.append(l)
                else:
                    if first[j] != l:
                        raise Exception('Test failed')
                j += 1

parameters = sys.argv[1:]
parameter_count = len(parameters)
if parameter_count > 0:
    match parameters[0]:
        case 'a':
            testa()
        case 'b':
            testb()
        case 'c':
            testc()
        case 'd':
            if parameter_count > 2 and int(parameters[2]) in range(machine.shape_custom_count):
                testd(parameters[1], parameters[2])
            else:
                print('No name and index')
        case 'e':
            teste()
