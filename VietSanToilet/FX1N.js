const { match } = require('node:assert');
const fs = require('node:fs');
const { exec } = require('child_process');

function print(data) {
   console.log(data);
}

function copy_to_clipboard(text) {
   const platform = process.platform;
   if (platform === 'win32') {
      const proc = exec('clip');
      proc.stdin.write(text);
      proc.stdin.end();
   } else if (platform === 'darwin') {
      const proc = exec('pbcopy');
      proc.stdin.write(text);
      proc.stdin.end();
   } else if (platform === 'linux') {
      const proc = exec('xclip -selection clipboard');
      proc.stdin.write(text);
      proc.stdin.end();
   } else {
      console.error('Unsupported operating system');
   }
}

const PLC = 'PLC', M = 'M', D = 'D', Self = 'Self', LB = 'LB', LW = 'LW', RW = 'RW', $M = '$M', $ = '$';
const BOOL = 'BOOL', INT = 'INT', DINT = 'DINT', X = 'X', Y = 'Y', TC = 'TC';
const XAxis = 'XX', YAxis = 'YY', ZAxis = 'ZZ', AAxis = 'AA';
const Auto = -1, NoUse = -2, Internal = -3;

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
   FX: 'FX',
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
         case ControllerType.FX:
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

   tag_add(_name_, _type_, _device_name_, _device_index_, _flag_='') {
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
         case ControllerType.FX:
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
            this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_, flag: _flag_ };
            this.csv += `"VAR_GLOBAL"	"${_name_}"	"${_type_}"	""	"${_device_name_}${_device_index_}"	""	""	""	""	""	""\n`;
            return this.tags[_name_];
         case ControllerType.Weintek:
            if (_type_ instanceof ARRAY) {
               for (var i = 0; i < _type_.length; i++) {
                  this.tag_add(`${_name_}${i}`, _type_.type, _device_name_, _device_index_ + i);
               }
            } else {
               var device_type = function (_device_type_) {
                  if (_device_type_ == 'INT') {
                     return '16-bit Unsigned'
                  } else if (_device_type_ == 'DINT') {
                     return '32-bit Unsigned'
                  } else {
                     return 'Undesignated'
                  }
               }
               this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_, flag: _flag_ };
               this.csv += `${_name_},PLC,${_device_name_},${_device_index_},,${device_type(_type_)}\n`;
               this._tag_check(_device_name_, _device_index_);
            }
            break;
         case ControllerType.Delta:
            var device_type = function (_device_name_) {
               if (_device_name_ == D || _device_name_ == '$' || _device_name_ == '$M') {
                  return 'WORD';
               }
               return 'BIT';
            }
            this.tags[_name_] = { name: _name_, type: _type_, device_name: _device_name_, device_index: _device_index_, flag: _flag_ };
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
         this.error += `${this.type} overlap device ${_device_name_}${_device_index_}\n`;
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

const plc = new Controller('FX');
const hmi = new Controller('Weintek');

/////GENERATE
for ([k, v] of Object.entries({'MainRun':1, 'MainStop':2, 'CoverRun':6, 'SpinRun':5, 'FlushRun':15, 'CleanRun':7})) {
   plc.tag_add(`${k}`, BOOL, M, Auto);
   plc.tag_add(`${k}I`, BOOL, X, v);
}
plc.tag_add(`Mode`, INT, D, Auto);
for ([k, v] of Object.entries({'ModeManual':3, 'ModeAuto':4})) {
   plc.tag_add(`${k}I`, BOOL, X, v);
}
for (k of ['Main', 'Cover', 'Spin', 'Flush', 'Clean']) {
   plc.tag_add(`${k}State`, INT, D, Auto);
   plc.tag_add(`${k}StateNext`, BOOL, M, Auto);
}
var delay = 128;
for (k of ['Cover']) {
   plc.tag_add(`${k}Pos`, INT, D, Auto);
   for (a of ['Unlock']) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}O`, BOOL, Y, 5);
      for (b of ['N', 'P']) {
         plc.tag_add(`${k}${a}${b}`, BOOL, M, Auto);
         plc.tag_add(`${k}${a}${b}Timer`, BOOL, TC, Auto);
         plc.tag_add(`${k}${a}${b}TimerDelay`, INT, D, delay++);
      }
   }
   for ([a, v] of Object.entries({'N':[11, 6], 'P':[-1, 7]})) {
      if (v[0] != -1) {
         plc.tag_add(`${k}${a}I`, BOOL, X, v[0]);
      }
      plc.tag_add(`${k}${a}O`, BOOL, Y, v[1]);
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, delay++);
   }
   for (a of ['Fail']) {
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, delay++);
   }
}
for (k of ['Spin']) {
   plc.tag_add(`${k}Pos`, INT, D, Auto);
   for (a of ['Unlock', 'Block']) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      for (b of ['N', 'P']) {
         plc.tag_add(`${k}${a}${b}`, BOOL, M, Auto);
         plc.tag_add(`${k}${a}${b}Timer`, BOOL, TC, Auto);
         plc.tag_add(`${k}${a}${b}TimerDelay`, INT, D, delay++);
      }
   }
   plc.tag_add(`${k}UnlockLO`, BOOL, Y, 3);
   plc.tag_add(`${k}UnlockRO`, BOOL, Y, 4);
   plc.tag_add(`${k}BlockO`, BOOL, Y, 16);
   for ([a, v] of Object.entries({'P':[10, 0]})) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}I`, BOOL, X, v[0]);
      plc.tag_add(`${k}${a}O`, BOOL, Y, v[1]);
   }
   for (a of ['Block']) {
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, delay++);
   }
   for (a of ['Fail']) {
      plc.tag_add(`${k}${a}Timer`, BOOL, TC, Auto);
      plc.tag_add(`${k}${a}TimerDelay`, INT, D, delay++);
   }
}
for (k of ['Flush']) {
   for ([a, v] of Object.entries({'Engage':10, 'Tank':11})) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}O`, BOOL, Y, v);
      for (b of ['N', 'P']) {
         plc.tag_add(`${k}${a}${b}`, BOOL, M, Auto);
         plc.tag_add(`${k}${a}${b}Timer`, BOOL, TC, Auto);
         plc.tag_add(`${k}${a}${b}TimerDelay`, INT, D, delay++);
      }
   }
}
for (k of ['Clean']) {
   for (a of ['Pump']) {
      plc.tag_add(`${k}${a}Pos`, INT, D, Auto);
      plc.tag_add(`${k}${a}O`, BOOL, Y, 1);
      plc.tag_add(`${k}${a}DirectionO`, BOOL, Y, 12);
   }
   for ([a, v] of Object.entries({'LowA':12, 'LowB':13, 'LowC':14})) {
      plc.tag_add(`${k}${a}I`, BOOL, X, v);
   }
   plc.tag_add(`${k}Type`, INT, D, Auto);
   for ([a, v] of Object.entries({'TypeA':13, 'TypeB':14, 'TypeC':15})) {
      plc.tag_add(`${k}${a}O`, BOOL, Y, v);
   }
   for ([a, v] of Object.entries({'Spreader':2})) {
      plc.tag_add(`${k}${a}`, BOOL, M, Auto);
      plc.tag_add(`${k}${a}O`, BOOL, Y, v);
   }
   stage = 5
   plc.tag_add(`${k}SprayTimer`, new ARRAY(BOOL, stage), TC, Auto);
   plc.tag_add(`${k}SprayTimerDelay`, new ARRAY(INT, stage), D, delay++);
   delay += stage - 1;
   plc.tag_add(`${k}SoakTimer`, new ARRAY(BOOL, stage), TC, Auto);
   plc.tag_add(`${k}SoakTimerDelay`, new ARRAY(INT, stage), D, delay++);
   delay += stage - 1;
}
for (k of ['Problem']) {
   plc.tag_add(`${k}Exist`, BOOL, M, Auto);
   plc.tag_add(`${k}ExistO`, BOOL, Y, 17);
   plc.tag_add(`${k}Index`, INT, D, Auto);
   plc.tag_add(`${k}`, new ARRAY(BOOL, 8), M, 600);
}
for (k of ['Time']) {
   plc.tag_add(`${k}SetEnable`, BOOL, M, Auto);
   plc.tag_add(`${k}SetTrigger`, BOOL, M, Auto);
   plc.tag_add(`${k}Buffer`, new ARRAY(INT, 7), D, Auto, Internal);
   for ([a, v] of Object.entries({'Year':8018, 'Month':8017, 'Day':8016, 'Hour':8015, 'Min':8014, 'Sec':8013, 'OfWeek':8019})) {
      plc.tag_add(`${k}${a}In`, INT, D, v, Internal);
      plc.tag_add(`${k}${a}`, INT, D, Auto);
   }
}
for (k of ['Process']) {
   plc.tag_add(`${k}DoorI`, BOOL, X, 16);
   plc.tag_add(`${k}HumanI`, BOOL, X, 17);
   plc.tag_add(`${k}HumanCount`, INT, D, delay++);
   plc.tag_add(`${k}HumanCountTimer`, BOOL, TC, Auto);
   plc.tag_add(`${k}HumanCountTimerDelay`, INT, D, delay++);
   plc.tag_add(`${k}FlushCount`, INT, D, delay++);
   plc.tag_add(`${k}Count`, INT, D, delay++);
   plc.tag_add(`${k}CountTarget`, INT, D, delay++);
}
for (k of ['Decode']) {
   plc.tag_add(`${k}CleanType`, new ARRAY(BOOL, 2**2), M, Auto, Internal);
}
/////GENERATE

if (plc.error == '') {
   plc.save();
   for (const [k, v] of Object.entries(plc.tags)) {
      if (v.device_name != TC && v.flag != Internal) {
         hmi.tag_add(v.name, v.type, v.device_name, v.device_index);
      }
   }
   hmi.save();
   for (var k of ['X', 'Y', 'D', 'TC']) {
      tb = plc.get_table(k);
      print(`${k} count = ${Object.keys(tb).length}`);
      console.table(tb);
   }
} else {
   print(plc.error);
}

i = 0, state = 500, text = '';
text += `(*start*)\n`;
text += `SET(M${state+=1}, fTmp);\n`;
text += `SET(fTmp, CleanSpreader);\n`;
text += `SET(fTmp, CleanStateNext);\n`;
text += `RST(fTmp, fTmp);\n`;
for (k of [[1, 0], [1, 1], [1, 2], [1, 0], [2, 0]]) {
   text += `(*${i}*)\n`;
   text += `(*spray*)\n`;
   text += `SET(M${state+=1}, fTmp);\n`;
   text += `MOV(fTmp, ${k[0]}, CleanPumpPos);\n`;
   text += `MOV(fTmp, ${k[1]}, CleanType);\n`;
   text += `SET(fTmp, CleanStateNext);\n`;
   text += `RST(fTmp, fTmp);\n`;
   text += `(*spray done -> soak*)\n`;
   text += `OUT_T(M${state+=1}, CleanSprayTimer[${i}], CleanSprayTimerDelay[${i}]);\n`;
   text += `SET(M${state} AND CleanSprayTimer[${i}], fTmp);\n`;
   text += `RST(fTmp, CleanPumpPos);\n`;
   text += `SET(fTmp, CleanStateNext);\n`;
   text += `RST(fTmp, fTmp);\n`;
   text += `(*soak done*)\n`;
   text += `OUT_T(M${state+=1}, CleanSoakTimer[${i}], CleanSoakTimerDelay[${i}]);\n`;
   text += `SET(M${state} AND CleanSoakTimer[${i}], fTmp);\n`;
   text += `SET(fTmp, CleanStateNext);\n`;
   text += `RST(fTmp, fTmp);\n`;
   i++;
}
text += `(*done*)\n`;
text += `SET(M${state+=1}, fTmp);\n`;
text += `RST(fTmp, CleanPumpPos);\n`;
text += `RST(fTmp, CleanType);\n`;
text += `RST(fTmp, CleanSpreader);\n`;
text += `RST(fTmp, CleanState);\n`;
text += `RST(fTmp, fTmp);\n`;
copy_to_clipboard(text);
print('Text copied to clipboard!');