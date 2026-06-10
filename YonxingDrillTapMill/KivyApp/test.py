from _data import Data

data = Data(
    _address_ip_='192.168.2.3', _address_port_=4840,
    _xml_path_windows_=r'D:/Github/PLC-HMI-Projects/YonxingDrillTapMill/MC500/MC500.Device.Application.xml',
    _tag_head_='ns=4;s=|var|LS'
)
data.create()
for k, v in data.name__block.items():
    print(f'Name: {k}, ID: {v.id}, Type: {v.type}')
print(len(data.name__block), 'tags')