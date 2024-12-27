const { match } = require('node:assert');
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
         this.path = `${__dirname}\\${project_name}.tag.PLC.csv`;
      } else {
         this.path = `${__dirname}\\${project_name}.tag.HMI.csv`;
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
            table[v.name] = { device: `${v.device_name}${v.device_index}` };
         }
      }
      return table;
   }
}

const plc = new Controller('FX3U');

/////GENERATE
function plc_generate_axis(_name_) {
   let lb = function (n) { return `${_name_}${n}`; }
   let xyz = function (x, y, z) { return _name_ == XAxis ? x : _name_ == YAxis ? y : z; }
   let xyz_name = function (x, y, z) { return _name_ == XAxis ? x : _name_ == YAxis ? y : z; }
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
   plc.tag_add(lb(xyz_name('PPR', 'PPM', 'PPR')), DINT, D, Auto);
   plc.tag_add(lb('TarR'), BOOL, M, Auto);
   plc.tag_add(lb('TarRSkip'), INT, D, Auto, false);
   plc.tag_add(lb('On'), BOOL, M, xyz(Auto, Auto, NoUse));
   plc.tag_add(lb('Run'), BOOL, M, Auto);
   plc.tag_add(lb('Direction'), BOOL, M, Auto);
   plc.tag_add(lb('MinI'), BOOL, X, xyz(0, NoUse, NoUse));
   plc.tag_add(lb('MaxI'), BOOL, X, xyz(NoUse, NoUse, NoUse));
   plc.tag_add(lb('Ready'), BOOL, M, xyz(Auto, Auto, NoUse));
   plc.tag_add(lb('ReadyI'), BOOL, X, xyz(4, 5, 6));
   plc.tag_add(lb('PulseO'), BOOL, Y, xyz(0, 1, 2));
   plc.tag_add(lb('DirectionO'), BOOL, Y, xyz(4, 5, 6));
   plc.tag_add(lb('OnO'), BOOL, Y, xyz(10, 11, 12));
   plc.tag_add(lb('InTorqueI'), BOOL, X, xyz(10, 11, 12));
   plc.tag_add(lb('InTorqueIEdge'), BOOL, M, Auto);
   plc.tag_add(lb('OverTorque'), BOOL, M, Auto);
}

plc_generate_axis(XAxis);
plc_generate_axis(YAxis);
plc_generate_axis(ZAxis);
for (k of ['Run', 'AxisSpin', 'AxisTap', 'FoilExtract', 'FoilClamp', 'FoilSupply']) {
   plc.tag_add(`${k}State`, INT, D, Auto);
   plc.tag_add(`${k}StateNext`, BOOL, M, Auto);
}
const blocks = [
   ['FoilExtractDrop', ['N', 'P'], []],
   ['FoilClamp', ['N', 'P'], ['P']],
   ['FoilSupply', [], []],
];
for (const block of blocks) {
   var k = block[0];
   var s = block[1];
   var i = block[2];
   for (a of s) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, Auto);
   }
   for (a of i) {
      plc.tag_add(`${k}${a}I`, BOOL, X, Auto);
   }
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
for (k of ['WorkFeed']) {
   plc.tag_add(`${k}Spin`, DINT, D, Auto);
   plc.tag_add(`${k}TapTravelFast`, DINT, D, Auto);
   plc.tag_add(`${k}TapSpinDown`, DINT, D, Auto);
   plc.tag_add(`${k}TapSpinUp`, DINT, D, Auto);
}
for (k of ['FoilFull']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}I`, BOOL, X, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
}
plc.tag_add(`SpinArray`, new ARRAY(DINT, 8), D, Auto);
plc.tag_add(`SpinArrayIndex`, INT, D, Auto);
for (k of ['AirReady', 'Run', 'RunStop']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}I`, BOOL, X, Auto);
}
for (k of ['Setting']) {
   plc.tag_add(`${k}TapPitch`, DINT, D, Auto);
   plc.tag_add(`${k}TapPitchI`, BOOL, X, Auto);
   plc.tag_add(`${k}FoilSupplyI`, BOOL, X, Auto);
   plc.tag_add(`${k}TapSpinSpeedI`, BOOL, X, Auto);
   plc.tag_add(`${k}TapTravelLengthIObsolete`, BOOL, X, Auto);
   plc.tag_add(`${k}TapTravelBegin`, DINT, D, Auto);
   plc.tag_add(`${k}TapTravelBeginOffset`, DINT, D, Auto);
   plc.tag_add(`${k}TapTravelFast`, DINT, D, Auto);
   plc.tag_add(`${k}TapTravelEnd`, DINT, D, Auto);
}

plc.tag_add(`TapMoveToTravelBegin`, BOOL, M, Auto);
plc.tag_add(`TapCount`, DINT, D, Auto);
plc.tag_add(`TapCountAtSupplyEnd`, DINT, D, Auto);
plc.tag_add(`TapCountResetOrigin`, DINT, D, Auto);
for (k of ['Stop']) {
   plc.tag_add(`${k}Tap`, BOOL, M, Auto);
   plc.tag_add(`${k}TapTimer`, BOOL, TC, Auto);
   plc.tag_add(`${k}Clamp`, BOOL, M, Auto);
   plc.tag_add(`${k}ClampPLS`, BOOL, M, Auto);
   plc.tag_add(`${k}ClampTimer`, BOOL, TC, Auto);
}
for (k of ['XXOff']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
}
for (k of ['Alert']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
for (k of ['ErrorReset']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}Timer`, BOOL, TC, Auto);
   plc.tag_add(`${k}O`, BOOL, Y, Auto);
}
for (k of ['Overload']) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
}
for (k of ['Setting']) {
   plc.tag_add(`${k}TapPitchO`, BOOL, Y, Auto);
}
/////GENERATE

if (plc.error == '') {
   plc.save();
   //
   var input = plc.get_table(X);
   input.XXReadyI.xinje1 = 'SO1';
   input.XXMinI.xinje1 = 'SO2';
   input.XXInTorqueI.xinje1 = 'SO3';
   //
   input.YYReadyI.xinje2 = 'SO1';
   input.YYInTorqueI.xinje2 = 'SO3';
   //
   input.AirReadyI.sensor = 'NPN';
   input.FoilClampPI.sensor = 'NPN';
   input.FoilFullI.sensor = 'NPN';
   //
   input.ZZReadyI.fatek = 'CN1-19';
   input.ZZInTorqueI.fatek = 'CN1-17';
   //
   input.RunI.panel = 'NO';
   input.RunStopI.panel = 'NC';
   input.SettingTapPitchI.panel = "NO";
   input.SettingTapSpinSpeedI.panel = "NO";
   input.SettingFoilSupplyI.panel = "NO";
   input.SettingTapTravelLengthIObsolete.panel = "NO";
   var output = plc.get_table(Y);
   output.XXPulseO.xinje1 = 'P-';
   output.XXDirectionO.xinje1 = 'D-';
   output.XXOnO.xinje1 = 'SI1';
   output.ErrorResetO.xinje1 = 'SI2';
   //
   output.YYPulseO.xinje2 = 'P-';
   output.YYDirectionO.xinje2 = 'D-';
   output.YYOnO.xinje2 = 'SI1';
   output.ErrorResetO.xinje2 = 'SI2';
   //
   output.ZZPulseO.fatek = 'CN1-27';
   output.ZZDirectionO.fatek = 'CN1-31,11';
   output.ZZOnO.fatek = 'CN1-4';
   output.ErrorResetO.fatek = 'CN1-5';
   //
   output.FoilExtractDropO.relay = 'NO';
   output.FoilClampO.relay = 'NO';
   output.FoilSupplyO.relay = 'NO';
   output.AlertO.relay = 'NO';
   //
   output.SettingTapPitchO.panel = 'NO';
   //
   console.table(input);
   console.table(output);
   print(`Input used: ${Object.keys(input).length}, Output used: ${Object.keys(output).length}`);
} else {
   print(plc.error);
}