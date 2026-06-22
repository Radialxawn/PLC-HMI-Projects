import re
import sys
from pathlib import Path
from core.data import Data
from data.face import Face
from core.gcode import GCode
import matplotlib.pyplot as plt

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
    print('Name count:', len(name__value))

def testc():
    a = {'a'}
    b = {'b'}
    ab(a, b)

def ab(*params):
    for param in params:
        print(param)

def testd():
    path = Path(r'C:/Users/Admin/Desktop/CNC/test.cnc')
    gcode = GCode().read(path)
    print('raw:')
    for line in gcode.raw:
        print(line)
    print('parsed:')
    gcode.parse()
    for line in gcode.parsed:
        print(line)
    points = []
    try:
        points = gcode.linear(0.1)
    except:
        print('Error')
        return
    xs, ys = [], []
    for point in points:
        print(point)
        xs.append(point[0])
        ys.append(point[1])
    plt.plot(xs, ys)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

parameters = sys.argv[1:]
if len(parameters) > 0:
    match parameters[0]:
        case 'a':
            testa()
        case 'b':
            testb()
        case 'c':
            testc()
        case 'd':
            testd()