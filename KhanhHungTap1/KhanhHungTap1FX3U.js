const fs = require('node:fs');

function print(data) {
   console.log(data);
}

const PLC = 'PLC', M = 'M', D = 'D', Self = 'Self', LB = 'LB', LW = 'LW', RW = 'RW', $M = '$M', $ = '$';
const BOOL = 'BOOL', INT = 'INT', DINT = 'DINT', X = 'X', Y = 'Y', TC = 'TC';
const XAxis = 'XX', YAxis = 'YY', ZAxis = 'ZZ', AAxis = 'AA';
const Auto = -1, NoUse = -2;

class ARRAY {
   type = '';
   length = 1;
   constructor(_type_, _length_) {
      this.type = _type_;
      this.length = _length_;
   }
   toString() { return `ARRAY [0..${this.length - 1}] OF ${this.type}`; }
}

const ControllerType = Object.freeze({
   FX3U: 'FX3U',
   Weintek: 'Weintek',
   Delta: 'Delta'
});

class Controller {
   type = '';
   path = '';
   csv = '';
   encoding = '';
   tags = {};
   devices_used = {};
   error = '';

   constructor(_type_) {
      this.type = _type_
      var is_plc = false;
      var project_name = __dirname.split('\\').pop();
      switch (_type_) {
         case ControllerType.FX3U:
            is_plc = true;
            this.csv += `${project_name}\n`;
			   this.csv += `"Class"	"Label Name"	"Data Type"	"Constant"	"Device"	"Address"	"Comment"	"Remark"	"Relation with System Label"	"System Label Name"	"Attribute"\n`;
            this.encoding = 'UTF16LE';
            this.devices_used[X] = [];
            this.devices_used[Y] = [];
            for (var i = 0; i < 32; i++) {
               var to_ignore = [i * 10 + 8, i * 10 + 9];
               this.devices_used[X].push(...to_ignore);
               this.devices_used[Y].push(...to_ignore);
            }
            break;
         case ControllerType.Weintek:
            this.csv_data = '';
            this.encoding = 'UTF16LE';
            break;
         case ControllerType.Delta:
            this.csv += 'Define Name,Type,Address,Description\n';
            break;
      }
      if (is_plc) {
         this.path = `${__dirname}\\${project_name}.tags.PLC.csv`;
      } else {
         this.path = `${__dirname}\\${project_name}.tags.HMI.csv`;
      }
   }

   tag_add(_name_, _type_, _device_name_, _device_index_) {
      if (_device_index_ == NoUse) {
         return;
      }
      if (_device_index_ == Auto) {
         _device_index_ = this._auto_index(_device_name_);
      }
      if (this.tags.hasOwnProperty(_name_)) {
         this.error += `${this.type} already has ${_name_}\n`;
      }
      switch (this.type) {
         case ControllerType.FX3U:
            let count = 1;
            if (_type_ instanceof ARRAY) {
               if (_type_.type == DINT) {
                  count = 2;
               }
               for (var i = 0; i < _type_.length * count; i++) {
                  this._tag_check(_device_name_, _device_index_ + i);
               }
            } else {
               if (_type_ == DINT) {
                  count = 2;
               }
               for (var i = 0; i < count; i++) {
                  this._tag_check(_device_name_, _device_index_ + i);
               }
            }
            this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_ };
            this.csv += `"VAR_GLOBAL"	"${_name_}"	"${_type_}"	""	"${_device_name_}${_device_index_}"	""	""	""	""	""	""\n`;
            return this.tags[_name_];
         case ControllerType.Weintek:
            this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_ };
            this.csv += `${_name_},${_type_},${_device_name_},${_device_index_}\n`;
            this._tag_check(_device_name_, _device_index_);
            break;
         case ControllerType.Delta:
            var device_type = function (_device_name_) {
               if (_device_name_ == D || _device_name_ == '$' || _device_name_ == '$M') {
                  return 'WORD';
               }
               return 'BIT';
            }
            this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_ };
            if (_type_ == Self) {
               this.csv += `${_name_},${device_type(_device_name_)},${_device_name_}${_device_index_},\n`;
            } else {
               this.csv += `${_name_},${device_type(_device_name_)},{${_type_}}0@${_device_name_}${_device_index_},\n`;
            }
            this._tag_check(_device_name_, _device_index_);
            break;
      }
   }

   _tag_check(_device_name_, _device_index_) {
      if (this.devices_used.hasOwnProperty(_device_name_) == false) {
         this.devices_used[_device_name_] = [];
      }
      if (this.devices_used[_device_name_].includes(_device_index_)) {
         this.error += `${this.type} overlap device ${_name_}${_device_index_}\n`;
      }
      this.devices_used[_device_name_].push(_device_index_);
   }

   _auto_index(_device_name_) {
      if (this.devices_used.hasOwnProperty(_device_name_) == false) {
         this.devices_used[_device_name_] = [];
      }
      for (var i = 0; i < 256; i++) {
         if (this.devices_used[_device_name_].includes(i)) {
            continue;
         }
         return i;
      }
      return 0;
   }

   save() {
      fs.writeFile(this.path, this.csv, { encoding: this.encoding }, err => {
         if (err) {
            print(err);
         } else {
            print(`Save to ${this.path} done`);
         }
      });
   }

   get_table(_device_name_) {
      let table = [];
      for (const [k, v] of Object.entries(this.tags)) {
         if (v.device_name == _device_name_) {
            table.push({ name: v.name, device: `${v.device_name}${v.device_index}` });
         }
      }
      return table;
   }
}

const plc = new Controller(ControllerType.FX3U);

/////GENERATE
function plc_generate_axis(_name_) {
   let lb = function (n) { return `${_name_}${n}`; }
   let xyz = function (x, y, z) { return _name_ == XAxis ? x : _name_ == YAxis ? y : z; }
   plc.tag_add(lb('LimitN'), BOOL, M, xyz(8344, 8354, 8364));
   plc.tag_add(lb('LimitP'), BOOL, M, xyz(8343, 8353, 8363));
   plc.tag_add(lb('Busy'), BOOL, M, xyz(8340, 8350, 8360));
   plc.tag_add(lb('InterruptInverse'), BOOL, M, xyz(8347, 8357, 8367));
   plc.tag_add(lb('Pos'), DINT, D, xyz(8340, 8350, 8360));
   plc.tag_add(lb('AccelTime'), INT, D, xyz(8348, 8358, 8368));
   plc.tag_add(lb('DecelTime'), INT, D, xyz(8349, 8359, 8369));
   plc.tag_add(lb('PosView'), DINT, D, Auto);
   plc.tag_add(lb('TarPos'), DINT, D, Auto);
   plc.tag_add(lb('Feed'), DINT, D, Auto);
   plc.tag_add(lb('TarR'), BOOL, M, Auto);
   plc.tag_add(lb('TarRSkip'), INT, D, Auto);
   plc.tag_add(lb('On'), BOOL, M, Auto);
   plc.tag_add(lb('Run'), BOOL, M, Auto);
   plc.tag_add(lb('Direction'), BOOL, M, Auto);
   //plc.tag_add(lb('OverTorque'), BOOL, M, Auto);
   //Input
   plc.tag_add(lb('MinI'), BOOL, X, xyz(0, 1, NoUse));
   plc.tag_add(lb('MaxI'), BOOL, X, xyz(NoUse, NoUse, NoUse));
   plc.tag_add(lb('ReadyI'), BOOL, X, xyz(4, 5, NoUse));
   plc.tag_add(lb('InTorqueI'), BOOL, X, xyz(2, 3, NoUse));
   plc.tag_add(lb('InTorqueIEdge'), BOOL, M, Auto);
   //Output
   plc.tag_add(lb('PulseO'), BOOL, Y, xyz(0, 1, NoUse));
   plc.tag_add(lb('DirectionO'), BOOL, Y, xyz(4, 5, NoUse));
   plc.tag_add(lb('OnO'), BOOL, Y, xyz(2, 3, NoUse));
}

plc_generate_axis(XAxis);
plc_generate_axis(YAxis);
for (k of ['Run', 'RunStop']) {
   plc.tag_add(`${k}`, BOOL, M, Auto).sync = true;
   plc.tag_add(`${k}I`, BOOL, X, Auto).sync = true;
}
for (k of ['Run', 'AxisSpin', 'AxisTap', 'FoilExtract', 'FoilClamp', 'FoilSupply']) {
   plc.tag_add(`${k}State`, INT, D, Auto).sync = true;
   plc.tag_add(`${k}StateNext`, BOOL, M, Auto).sync = true;
}
for (k of ['FoilClamp', 'FoilSupply']) {
   for (a of ['N', 'P']) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, Auto);
   }
   for (a of ['P']) {
      if (k == 'FoilClamp') {
         plc.tag_add(`${k}${a}I`, BOOL, X, Auto);
      }
   }
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
for (k of ['Overload']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}I`, BOOL, X, Auto);
}
for (k of ['WorkFeed']) {
   plc.tag_add(`${k}Spin`, DINT, D, Auto);
   plc.tag_add(`${k}TapDown`, DINT, D, Auto);
   plc.tag_add(`${k}TapUp`, DINT, D, Auto);
}
for (k of ['FoilFull']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}I`, BOOL, X, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
}
plc.tag_add(`SpinArray`, new ARRAY(DINT, 6), D, Auto);
plc.tag_add(`SpinArrayIndex`, INT, D, Auto);
for (k of ['SpinTest']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
   plc.tag_add(`${k}TimerDelay`, INT, D, Auto);
}
for (k of ['Setting']) {
   plc.tag_add(`${k}TapBegin`, DINT, D, Auto);
   plc.tag_add(`${k}FoilSupplyI`, BOOL, X, Auto);
   plc.tag_add(`${k}TapSpeed1I`, BOOL, X, Auto);
   plc.tag_add(`${k}TapSpeed2I`, BOOL, X, Auto);
}
for (k of ['Air']) {
   plc.tag_add(`${k}Ready`, BOOL, M, Auto);
   plc.tag_add(`${k}ReadyI`, BOOL, X, Auto);
}
plc.tag_add(`TapCount`, DINT, D, Auto);
plc.tag_add(`TapCountAtSupplyEnd`, DINT, D, Auto);
for (k of ['Stop']) {
   plc.tag_add(`${k}Tap`, BOOL, M, Auto);
   plc.tag_add(`${k}TapTimer`, BOOL, TC, Auto);
   plc.tag_add(`${k}Clamp`, BOOL, M, Auto);
   plc.tag_add(`${k}ClampPLS`, BOOL, M, Auto);
   plc.tag_add(`${k}ClampTimer`, BOOL, TC, Auto);
}
for (k of ['FoilSupply']) {
   plc.tag_add(`${k}PTimeoutTimer`, BOOL, TC, Auto);
   plc.tag_add(`${k}PTimeoutTimerDelay`, INT, D, Auto);
}
for (k of ['XXOff']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
}
for (k of ['ErrorReset']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
for (k of ['Alert']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
/////GENERATE

if (plc.error == '') {
   plc.save();
   console.table(plc.get_table(X));
   console.table(plc.get_table(Y));
} else {
   print(plc.error);
}