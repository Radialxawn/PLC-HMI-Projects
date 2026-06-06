from _data import Data

data = Data({}, 'opc.tcp://192.168.2.3:4840')
data.create(r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml', 'ns=4;s=|var|LS')
for k, v in data.name__block.items():
    print(f'Name: {k}, ID: {v.id}, Type: {v.type}')
print(len(data.name__block), 'tags')