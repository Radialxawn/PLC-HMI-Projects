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

const Q = { region: 'Q', single: { name: 'QW', name_bit: 'QX', type: 'Word', type_bit: 'Bit' }, double: { name: 'QD', type: 'DWord' } };
const M = { region: 'M', single: { name: 'MW', name_bit: 'MX', type: 'Word', type_bit: 'Bit' }, double: { name: 'MD', type: 'DWord' } };
const Auto = new AutoClass();

const BOOL = 'BOOL';
const INT = 'INT';
const DINT = 'DINT';
const UINT = 'UINT';
const UDINT = 'UDINT';

let name__tag = {};
let region_used = { Q: [], M: [] };
let error = '';

region_used.Q = [];
region_used.M = [];
for (var i = 0; i < 2048; i++) {
   let q_byte = Array(8).fill(false);
   region_used.Q.push(q_byte);
   let m_byte = Array(8).fill(false);
   region_used.M.push(m_byte);
}

function any_bit_used(_byte_) {
   for (var i = 0; i < _byte_.length; i++) {
      if (_byte_[i] == true) {
         return true;
      }
   }
   return false;
}

function byte_count_get(_type_) {
   return [DINT, UDINT].includes(_type_) ? 4 : 2;
}

function tag_add_boolean_auto(_region_) {
   for (var i = Auto.begin; i < _region_.length; i++) {
      let byte = _region_[i];
      for (var j = 0; j < byte.length; j++) {
         if (byte[j] == false) {
            return [i, j];
         }
      }
   }
   error += `Region limit reach\n`;
}

function tag_add_integer_auto(_region_, _type_) {
   let size = byte_count_get(_type_);
   let i_begin = Auto.begin * size;
   let i_end = _region_.length - size;
   for (var i = i_begin; i < i_end; i += size) {
      let free = true;
      for (var j = 0; j < size; j++) {
         if (any_bit_used(_region_[i + j])) {
            free = false;
         }
      }
      if (free) {
         return [i / size, 0];
      }
   }
   error += `Region limit reach\n`;
}

function tag_add(_name_, _register_, _type_, _address_) {
   let region = region_used[_register_.region];
   // add
   if (_type_ == BOOL) {
      if (_address_ == Auto) {
         _address_ = tag_add_boolean_auto(region);
      }
   } else {
      if (_address_ == Auto) {
         _address_ = tag_add_integer_auto(region, _type_);
      } else if (typeof _address_ === 'number') {
         _address_ = [_address_, 0];
      } else {
         error += `Error define -> ${_name_}\n`;
         return;
      }
   }
   // check
   if (_name_ in name__tag) {
      error += `Dupplicated -> ${_name_}\n`;
      return;
   } else {
      let address = { main: _address_[0], sub: _address_[1]};
      let tag = { register: _register_, address: address, type: _type_ };
      if (_type_ == BOOL) {
         let byte = region[address.main];
         if (byte[address.sub] == true) {
            error += `Overlap region -> ${_name_}\n`;
            return;
         } else {
            byte[address.sub] = true;
         }
      } else {
         let size = byte_count_get(_type_);
         let i_begin = address.main * size;
         let i_end = i_begin + size;
         for (var i = i_begin; i < i_end; i++) {
            let byte = region[i];
            if (any_bit_used(byte)) {
               error += `Overlap region -> ${_name_}\n`;
               return;
            } else {
               byte.fill(true);
            }
         }
      }
      name__tag[_name_] = tag;
   }
}

function hmi_csv_build() {
   let result = 'Sn,LabelName,DeviceAlias,RegName,RegisterTypes,StationNo,IsUseStationNoIndex,MainAddress,SubAddress,BlockAddress,IsUseBlockAddressIndex,UseWordAsBit,StationAddressDeviceAlias,StationAddressRegName,StationAddressRegisterTypes,StationAddressStationNo,StationAddressMainAddress,StationAddressBlockAddress,BlockAddressDeviceAlias,BlockAddressRegName,BlockAddressRegisterTypes,BlockAddressStationNo,BlockAddressMainAddress,BlockAddressBlockAddress,PlcId,StationAddressPlcId,BlockAddressPlcId,Version';
   for (let [k, v] of Object.entries(name__tag)) {
      let reg = ([BOOL, INT, UINT].includes(v.type)) ? v.register.single : v.register.double;
      let n = v.type == BOOL ? reg.name_bit : reg.name;
      let t = v.type == BOOL ? reg.type_bit : reg.type;
      result += '\n';
      result += `0,${k},PLC:[Ethernet PLC:Leadshine MC_Ethernet],${n},${t},1,False,${v.address.main},${v.address.sub},0,False,False,,,,,,,,,,,,,8205,,,1`;
   }
   return result;
}

function plc_txt_build() {
   let result = '';
   for (let [k, v] of Object.entries(name__tag)) {
      let reg = ([BOOL, INT, UINT].includes(v.type)) ? v.register.single : v.register.double;
      let r = ``;
      if (v.type == BOOL) {
         r += `${reg.name_bit}${v.address.main}.${v.address.sub}`;
      } else {
         r += `${reg.name}${v.address.main}`;
      }
      result += result.length > 0 ? '\n' : '';
      result += `\t_${k} AT %${r}: ${v.type};`;
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
tag_add('PLCReady', M, BOOL, Auto);
tag_add('HMIReady', M, BOOL, Auto);
tag_add('On', M, BOOL, Auto);
tag_add('Off', M, BOOL, Auto);
tag_add('Home', M, BOOL, Auto);
tag_add('SettingApply', M, BOOL, Auto);
tag_add('OverloadResolved', M, BOOL, Auto);
for (var k of ['Jog']) {
   tag_add(`${k}N`, M, BOOL, Auto);
   tag_add(`${k}P`, M, BOOL, Auto);
   tag_add(`${k}MicronPerSec`, M, UINT, Auto);
}
//setting
tag_add(`HomeTorque`, M, UDINT, Auto);
tag_add(`AccelRpm`, M, UINT, Auto);
tag_add(`DecelRpm`, M, UINT, Auto);
for (var k of ['Tap']) {
   tag_add(`${k}Begin`, M, UDINT, Auto);
   tag_add(`${k}Depth`, M, UDINT, Auto);
   tag_add(`${k}PeckDepth`, M, UDINT, Auto);
   tag_add(`${k}Pitch`, M, UINT, Auto);
   tag_add(`${k}Rpm`, M, UINT, Auto);
   tag_add(`${k}TorqueMax`, M, UDINT, Auto);
}
for (var k of ['FoilExtract']) {
   tag_add(`${k}`, M, BOOL, Auto);
   for (var a of ['Top', 'Bot']) {
      for (var b of ['N', 'P']) {
         tag_add(`${k}${a}${b}Delay`, M, UINT, Auto);
      }
   }
}
for (var k of ['FoilClamp']) {
   tag_add(`${k}`, M, BOOL, Auto);
   for (var a of ['N', 'P']) {
      tag_add(`${k}${a}Delay`, M, UINT, Auto);
   }
}
for (var k of ['AirBurst']) {
   tag_add(`${k}`, M, BOOL, Auto);
   tag_add(`${k}Delay`, M, UINT, Auto);
}
//view
for (var k of ['View']) {
   for (var a of ['Linear', 'Rotary']) {
      tag_add(`${k}${a}Position`, M, DINT, Auto);
      tag_add(`${k}${a}Torque`, M, DINT, Auto);
   }
   tag_add(`${k}TapEnd`, M, UDINT, Auto);
   tag_add(`${k}TapPeckEnd`, M, UDINT, Auto);
   tag_add(`${k}FoilExtract`, M, BOOL, Auto);
   tag_add(`${k}AirBurst`, M, BOOL, Auto);
   tag_add(`${k}CycleTime`, M, UDINT, Auto);
   tag_add(`${k}Overload`, M, BOOL, Auto);
   tag_add(`${k}Ready`, M, BOOL, Auto);
   tag_add(`${k}CanChangeMode`, M, BOOL, Auto);
   tag_add(`${k}LinearPositionMax`, M, UDINT, Auto);
   tag_add(`${k}Auto`, M, BOOL, Auto);
   tag_add(`${k}AutoActive`, M, BOOL, Auto);
   tag_add(`${k}RotaryTorqueMaxN`, M, DINT, Auto);
   tag_add(`${k}RotaryTorqueMaxP`, M, DINT, Auto);
   tag_add(`${k}Air`, M, BOOL, Auto);
   tag_add(`${k}StateMain`, M, UINT, Auto);
   tag_add(`${k}StateWork`, M, UINT, Auto);
   tag_add(`${k}StateGear`, M, UINT, Auto);
}
/////GENERATE

if (error == '') {
   save(path_get('hmi', 'csv'), hmi_csv_build());
   save(path_get('plc', 'txt'), plc_txt_build());
} else {
   print(error);
}