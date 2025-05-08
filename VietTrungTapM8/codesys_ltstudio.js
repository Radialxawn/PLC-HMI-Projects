const fs = require('node:fs');

function print(data) {
   console.log(data);
}

class AutoClass {
   constructor() {
      this.begin = 0;
   }
   begin_set(_value_) {
      this.begin = _value_;
      return this;
   }
}

const I_8bit = { name: 'I_8bit', region: 'I_8bit', type: 'Bit'};
const QW = { name: 'QW', region: 'Q', type: 'Word', size: 1};
const QD = { name: 'QD', region: 'Q', type: 'DWord', size: 2 };
const MW = { name: 'MW', region: 'M', type: 'Word', size: 1 };
const MD = { name: 'MD', region: 'M', type: 'DWord', size: 2 };
const Auto = new AutoClass();

const T_INTEGER = 'T_INTEGER';
const T_UINTEGER = 'T_UINTEGER';
const BOOL = 'BOOL';
const INT = 'INT';
const DINT = 'DINT';
const UINT = 'UINT';
const UDINT = 'UDINT';

let name__tag = {};
let region_used = { Q: [], M: [], I_8bit: [] };
let error = '';

region_used.Q = Array(1024).fill(false);
region_used.M = Array(1024).fill(false);
region_used.I_8bit = [];
for (var i = 0; i < 1024; i++) {
   let region_byte = Array(8).fill(false);
   region_used.I_8bit.push(region_byte);
}

function tag_add(_name_, _register_, _address_, _plc_type_) {
   let region = region_used[_register_.region];
   if (region == region_used.Q || region == region_used.M) {
      if (_address_ == Auto) {
         let found = false;
         let i_begin = Auto.begin * _register_.size;
         for (var i = i_begin; i < region.length - _register_.size; i += _register_.size) {
            let free = true;
            for (var s = 0; s < _register_.size; s++) {
               if (region[i + s] == true) {
                  free = false;
               }
            }
            if (free) {
               _address_ = [i / _register_.size, 0];
               found = true;
               break;
            }
         }
         if (!found) {
            error += `Region limit reach -> ${_name_}\n`;
            return;
         }
      } else if (typeof _address_ === 'number') {
         _address_ = [_address_, 0];
      } else {
         error += `Error define -> ${_name_}\n`;
         return;
      }
   } else if (region == region_used.I_8bit) {
      if (_address_ == Auto) {
         let found = false;
         for (var i = Auto.begin; i < region.length; i++) {
            let region_byte = region[i];
            for (var j = 0; j < region_byte.length; j++) {
               if (region_byte[j] == false) {
                  _address_ = [i, j];
                  found = true;
                  break;
               }
            }
            if (found) {
               break;
            }
         }
         if (!found) {
            error += `Region limit reach -> ${_name_}\n`;
            return;
         }
      } else if (!(Array.isArray(_address_) && _address_.length == 2 && 0 <= _address_[1] && _address_[1] <= 7)) {
         error += `Error define -> ${_name_}\n`;
         return;
      }
   }
   if (_name_ in name__tag) {
      error += `Dupplicated -> ${_name_}\n`;
      return;
   } else {
      let address = { main: _address_[0], sub: _address_[1] };
      let tag = { register: _register_, address: address, plc_type: _plc_type_ };
      if (region == region_used.Q || region == region_used.M) {
         let i_begin = address.main * _register_.size;
         let i_end = i_begin + _register_.size;
         for (var i = i_begin; i < i_end; i++) {
            if (region[i] == true) {
               error += `Overlap region -> ${_name_}\n`;
               return;
            } else {
               region[i] = true;
            }
         }
      } else if (region == region_used.I_8bit) {
         let region_byte = region[address.main];
         if (region_byte[address.sub] == true) {
            error += `Overlap region -> ${_name_}\n`;
            return;
         } else {
            region_byte[address.sub] = true;
         }
      }
      name__tag[_name_] = tag;
   }
}

function hmi_csv_build() {
   let result = 'Sn,LabelName,DeviceAlias,RegName,RegisterTypes,StationNo,IsUseStationNoIndex,MainAddress,SubAddress,BlockAddress,IsUseBlockAddressIndex,UseWordAsBit,StationAddressDeviceAlias,StationAddressRegName,StationAddressRegisterTypes,StationAddressStationNo,StationAddressMainAddress,StationAddressBlockAddress,BlockAddressDeviceAlias,BlockAddressRegName,BlockAddressRegisterTypes,BlockAddressStationNo,BlockAddressMainAddress,BlockAddressBlockAddress,PlcId,StationAddressPlcId,BlockAddressPlcId,Version';
   result += '\n';
   for (let [k, v] of Object.entries(name__tag)) {
      result += `0,${k},PLC:[Ethernet PLC:Leadshine MC_Ethernet],${v.register.name},${v.register.type},1,False,${v.address.main},${v.address.sub},0,False,False,,,,,,,,,,,,,8205,,,1`;
      result += '\n';
   }
   return result;
}

function plc_txt_build() {
   let result = '';
   let hmi_map_plc = { QW: 'QW', QD: 'QD', MW: 'MW', MD: 'MD', I_8bit: 'QX' };
   for (let [k, v] of Object.entries(name__tag)) {
      let region = region_used[v.register.region];
      let r = '';
      let n = hmi_map_plc[v.register.name];
      if (region == region_used.Q || region == region_used.M) {
         r = `${n}${v.address.main}`;
         let single = v.register.size == 1;
         if (v.plc_type == T_INTEGER) {
            v.plc_type = single ? INT : DINT;
         } else if (v.plc_type == T_UINTEGER) {
            v.plc_type = single ? UINT : UDINT;
         }
      } else if (region == region_used.I_8bit) {
         r = `${n}${v.address.main}.${v.address.sub}`;
         v.plc_type = BOOL;
      }
      result += `\t_${k} AT %${r}: ${v.plc_type};`;
      result += '\n';
   }
   return result;
}

function path_get(_name_, _extension_) {
   var project_name = __dirname.split('\\').pop();
   return `${__dirname}\\${project_name}.${_name_}.${_extension_}`;
}

function save(_path_, _data_) {
   fs.writeFile(_path_, _data_, { encoding: 'UTF8' }, err => {
      if (err) {
         print(err);
      } else {
         print(`Save to ${_path_} done`);
      }
   });
}

/////GENERATE
tag_add('Start', I_8bit, [0, 0]);
tag_add('Stop', I_8bit, [0, 1]);
tag_add('Damn', I_8bit, Auto);
tag_add('Suck', I_8bit, Auto);
tag_add('Holy', I_8bit, Auto.begin_set(10));
tag_add('Yo', I_8bit, Auto.begin_set(20));
tag_add('Output', QW, 0, T_UINTEGER);
tag_add('A', QD, Auto.begin_set(20), T_INTEGER);
tag_add('B', QD, Auto, T_INTEGER);
tag_add('C', MD, Auto, T_INTEGER);
tag_add('D', MD, Auto, T_INTEGER);
/////GENERATE

if (error == '') {
   save(path_get('hmi', 'csv'), hmi_csv_build());
   save(path_get('plc', 'txt'), plc_txt_build());
} else {
   print(error);
}