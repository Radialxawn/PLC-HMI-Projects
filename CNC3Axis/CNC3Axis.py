import os
import sys
import bpy
import math
import mathutils
import importlib

dir = r'D:\Github\Blender-Data\Projects\Interpolation'
if not dir in sys.path:
   sys.path.append(dir)

import interpolation
importlib.reload(interpolation)

LS = 0.05 # length step
R6 = 6/2 # bit radius
FSM, FS6, FS25 = 20, 5, 3 # feed speed: max, d6mm end mill, d16mm end mill, d25mm-2mm cutter

def _get_range(a, b, step):
   if a == b:
      return [a]
   step = step < 0 and -step or step
   increase = a < b
   result = []
   i = a
   count, count_max = 0, 1024
   while True:
      result.append(i)
      if increase:
         i += step
         if i >= b:
            break
      else:
         i -= step
         if i <= b:
            break
      count += 1
      if (count == count_max):
         print('_get_range overflow', 'a = %s, b = %s, step = %s, increase = %s' % (a, b, step, increase))
         return []
   result.append(b)
   return result

def _run_code_test_limit():
   for _ in range(48):
      interpolation.line((234, 86, 0), FSM)
      interpolation.line((0, 0, 0), FSM)

def _run_code_test(location):
   _run_code_test_limit()

def _run_code_mill_A1(location):
   h, zStep = location[2], 0.4
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kx, ky = -0.3, -11
   depth = 21
   for sign in [1, -1]:
      for i, iz in enumerate(_get_range(h, h + depth, zStep)):
         if i == 0:
            interpolation.line((kx, 0, iz), FSM)
         interpolation.line((kx, sign * (ky + 4), iz), FS6)
         interpolation.line((kx, sign * ky, iz), FS6)
         interpolation.line((-kx, sign * ky, iz), FS6)
         interpolation.line((-kx, sign * (ky + 4), iz), FS6)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((100, 0, 0), FSM)

def _run_code_mill_B1R(location): # out of working range
   h, zStep = location[2], 0.4
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_B1(location):
   h, zStep = location[2], 0.4
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   ox = 0.05
   oy = 0.05
   #4Hole
   interpolation.line((-5 - ox, -20 - oy, 0), FS6)
   kzs = _get_range(h, h + 5, zStep)
   kzs.append(h + 4.95)
   lastIndex = len(kzs) - 1
   for i, iz in enumerate(kzs):
      if i == lastIndex:
         ox = 0.05
         oy = 0.05
      interpolation.line((-5 - ox, -20 - oy, iz), FS6)
      #
      interpolation.line((-5 - ox, -18 - oy, iz), FS6)
      interpolation.arc((-5 - ox, -13 - oy, iz), (-9 - ox, -13 - oy, iz), True, LS, FS6)
      interpolation.line((-9 - ox, -10.5 - oy, iz), FS6)
      interpolation.line((-11.5 - ox, -10.5 - oy, iz), FS6)
      interpolation.arc((-11.5 - ox, -6.5 - oy, iz), (-15.5 - ox, -6.5 - oy, iz), True, LS, FS6)
      #
      interpolation.line((-15.5 - ox, 6.5 + oy, iz), FS6)
      interpolation.arc((-11.5 - ox, 6.5 + oy, iz), (-11.5 - ox, 10.5 + oy, iz), True, LS, FS6)
      interpolation.line((-9 - ox, 10.5 + oy, iz), FS6)
      interpolation.line((-9 - ox, 13 + oy, iz), FS6)
      interpolation.arc((-5 - ox, 13 + oy, iz), (-5 - ox, 18 + oy, iz), True, LS, FS6)
      #
      interpolation.line((5 + ox, 18 + oy, iz), FS6)
      interpolation.arc((5 + ox, 13 + oy, iz), (9 + ox, 13 + oy, iz), True, LS, FS6)
      interpolation.line((9 + ox, 10.5 + oy, iz), FS6)
      interpolation.line((11.5 + ox, 10.5 + oy, iz), FS6)
      interpolation.arc((11.5 + ox, 6.5 + oy, iz), (15.5 + ox, 6.5 + oy, iz), True, LS, FS6)
      #
      interpolation.line((15.5 + ox, -6.5 - oy, iz), FS6)
      interpolation.arc((11.5 + ox, -6.5 - oy, iz), (11.5 + ox, -10.5 - oy, iz), True, LS, FS6)
      interpolation.line((9 + ox, -10.5 - oy, iz), FS6)
      interpolation.line((9 + ox, -13 - oy, iz), FS6)
      interpolation.arc((5 + ox, -13 - oy, iz), (5 + ox, -18 - oy, iz), True, LS, FS6)
      #
      interpolation.line((-5 - ox, -18 - oy, iz), FS6)
      interpolation.line((-5 - ox, -20 - oy, iz), FS6)
   #Out face
   ox = 0.05
   oy = 0.05
   kxs = [-10, -15.5, -15.5, -10, 10, 15.5, 15.5,  10, -10]
   kys = [-18,   -13,    13,  18, 18,   13,  -13, -18, -18]
   kfs = [FSM,   FSM,    FS6, FSM, FS6,  FSM,   FS6, FSM,  FS6]
   final = False
   interpolation.line((kxs[0], kys[0], iz), FS6)
   for iz in _get_range(h + 5.1, h + 11.9, zStep):
      if (iz >= h + 10.5) and not final:
         kxs.reverse()
         kys.reverse()
         kfs = [FS6, FS6,    FSM, FS6, FSM,  FS6,   FSM, FS6,  FSM]
         final = True
      for x, y, f in zip(kxs, kys, kfs):
         dx = x < 0 and -ox or ox
         dy = y < 0 and -oy or oy
         interpolation.line((x + dx, y + dy, iz), f)
   kxs.reverse()
   kys.reverse()
   kfs = [FSM,   FSM,    FS6, FSM, FS6,  FSM,   FS6, FSM,  FS6]
   for x, y, f in zip(kxs, kys, kfs):
      dx = x < 0 and -ox or ox
      dy = y < 0 and -oy or oy
      interpolation.line((x + dx, y + dy, iz), f)
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_D1(location):
   h, zStep = location[2], 0.4
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   #
   kx = (9.5 - R6 * 2) / 2
   kxs = [kx,   kx, -kx,  -kx]
   kys = [-3.5, 26,  26, -3.5]
   #   
   interpolation.line((kxs[0], kys[0], 0), FS6)
   for iz in _get_range(h + 0.1, h + 20, zStep):
      for x, y in zip(kxs, kys):
         interpolation.line((x, y, iz), FS6)
   interpolation.line((0, 0, 0), FS6)
   #
   for _ in range(2):
      interpolation.line((kxs[0], kys[0], 0), FS6)
      for iz in _get_range(h + 5, h + 21, zStep * 10):
         for x, y in zip(kxs, kys):
            interpolation.line((x, y, iz), FS6)
   interpolation.line((0, 0, 0), FS6)
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_AB_top(h, flipY):
   xStepMax, zStep = 5, 0.4
   foilRadius = 16.5
   sy = 12 * (flipY and -1 or 1)
   ey = 60 * (flipY and -1 or 1)
   kzs = _get_range(h + 0.3, h + 4, zStep)
   lastIndex = len(kzs) - 1
   xSign, ySign = 1, 1
   for i, iz in enumerate(kzs):
      iw = math.sin(math.acos((foilRadius - (iz - h)) / foilRadius)) * foilRadius * 2
      count = math.ceil(iw / xStepMax)
      xStep = min((iw + 1) / count, xStepMax)
      if i == lastIndex:
         sy = 1
      x = xSign * (-iw / 2 - R6 - 1)
      y = ySign == 1 and sy or ey
      interpolation.line((x, y, iz - 2 * zStep), FSM)
      interpolation.line((x, y, iz), FS6)
      x = xSign * (-iw / 2 - R6 - xStep)
      j = 0
      for _ in range(count * 2):
         x += xSign * xStep
         y = ySign == 1 and sy or ey
         interpolation.line((x, y, iz), FS6)
         j += 1
         ySign *= -1
         if j > count:
            break
         else:
            interpolation.line((x + xSign * xStep, y, iz), FS6)
      xSign *= -1
      ySign *= -1
   interpolation.line((x, y, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_AB_carve(h, flipY):
   kxs = [-17, -10, -10,     -17,      -8,      -8, -11.9981, -17]
   kys = [  4,  10,  40, 46.6807, 41.5718, 9.89692,        2,   4]
   def _carve(signX, signY):
      interpolation.line((signX * kxs[0], signY * kys[0], 0), FSM)
      for iz in _get_range(h + 4.3, h + 5, 0.3):
         for ix, iy in zip(kxs, kys):
            fx = signX * ix
            fy = signY * iy
            interpolation.line((fx, fy, iz), FS6)
      interpolation.line((fx, fy, 0), FSM)
   _carve(1, flipY and -1 or 1)
   _carve(-1, flipY and -1 or 1)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_AB1(location):
   h, zStep = location[2], 0.4
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   _run_code_AB_top(h, False)
   _run_code_AB_carve(h, False)
   #
   #SideA
   ox = -0.2
   kxs = [  19.8, 18 + ox, 18 + ox, 20]
   kys = [53.466, 47.9714,    10.8, 11]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(h + 10, h + 25, zStep):
      for x, y in zip(kxs, kys):
         interpolation.line((x, y, iz), FS6)
      kxs.reverse()
      kys.reverse()
   interpolation.line((x, y, 0), FSM)
   #SideB
   ox = -0.2
   kxs = [-20, -18 - ox, -18 - ox, -20]
   kys = [ 11, 10.8,     62,  62]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(h + 10, h + 25, zStep):
      for x, y in zip(kxs, kys):
         interpolation.line((x, y, iz), FS6)
      kxs.reverse()
      kys.reverse()
   interpolation.line((x, y, 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_AB2(location):
   h = location[2]
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   _run_code_AB_top(h, True)
   _run_code_AB_carve(h, True)
   #
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_cut_A2(location):
   h, yStep = location[2], 0.4
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   interpolation.line((0, -2, 0), FS25)
   iz = h + 26.5
   for i, iy in enumerate(_get_range(0, 4, yStep)):
      interpolation.line((-17, -2, iz), FSM)
      interpolation.line((-17, iy, iz), FSM)
      interpolation.line((17, iy, iz), FS25)
      interpolation.line((17, -2, iz), FSM)
   interpolation.line((0, -2, 0), FS25)
   interpolation.local_end()

def set_data(target):
   _constraint = target.constraints['Limit Location']
   max_x = getattr(_constraint, 'max_x')
   max_y = getattr(_constraint, 'max_y')
   max_z = getattr(_constraint, 'max_z')
   interpolation.set_data(mathutils.Vector((max_x, max_y, max_z)))
   print('Bounds', max_x, max_y, max_z)

def _int_to_word(value):
  value += value < 0 and 65536 or 0
  a = value % 256
  b = (value - a) / 256
  return [int(a), int(b)]

def _int_to_dword(value):
  value += value < 0 and 4294967296 or 0
  a = (value - (value % 16777216)) / 16777216
  value -= a * 16777216
  b = (value - (value % 65536)) / 65536
  value -= b * 65536
  c = (value - (value % 256)) / 256
  value -= c * 256
  return [int(value), int(c), int(b), int(a)]

def export_data():
   fs = [
      _run_code_test,         (117, 43, 1),        (0, 0),
      _run_code_mill_A1,      (5.8, 16.9, 1),      (0, 14),
      _run_code_mill_B1,      (213.89, 21.12, 1),  (0, 0),
      _run_code_mill_D1,      (228.3, 56.9, 1),    (0, 0),
      _run_code_mill_AB1,     (156.43, 20.2, 1),   (0, 14),
      _run_code_mill_AB2,     (91.5, 81.2, 1),     (0, -14),
      _run_code_cut_A2,       (20, 60, 1),         (0, 10),
   ]
   print('-Export data')
   timeMinutesTotal = 0
   for i in range(0, len(fs), 3):
      interpolation.refresh()
      function, center, setZOffset = fs[i], fs[i + 1], fs[i + 2]
      function(center)
      function_name = function.__name__[10:]
      print(function_name)
      _export_data(function_name, center, setZOffset)
      timeMinutes = interpolation.check()
      if not 'test' in function_name:
         timeMinutesTotal += timeMinutes
   print('-Export data done: Total time: %s minutes' % ('{:.2f}'.format(timeMinutesTotal)))

def _export_data(file_name, center, setZOffset):
   locations, speeds = interpolation.get_data()
   def fx(value):
      return int(round(value * 1000))
   
   centerX = fx(center[0])
   centerY = fx(center[1])
   centerIndex = 1
   for i, (l, s) in enumerate(zip(locations, speeds)):
      if i < 1:
         continue
      if fx(l.x) == centerX and fx(l.y) == centerY:
         centerIndex = i
         break
   byte_arr = []
   byte_arr += _int_to_dword(len(locations))
   byte_arr += _int_to_dword(len(locations))
   byte_arr += _int_to_word(centerIndex)
   byte_arr += _int_to_word(fx(setZOffset[0]))
   byte_arr += _int_to_word(fx(setZOffset[1]))
   byte_arr += _int_to_word(0)
   for i, (l, s) in enumerate(zip(locations, speeds)):
      if i < 1:
         continue
      byte_arr += _int_to_dword(fx(l.x))
      byte_arr += _int_to_dword(fx(l.y))
      byte_arr += _int_to_word(fx(l.z))
      byte_arr += _int_to_word(fx(s.x))
      byte_arr += _int_to_word(fx(s.y))
      byte_arr += _int_to_word(fx(s.z))
   some_bytes = bytearray(byte_arr)
   immutable_bytes = bytes(some_bytes)
   with open('C:\EBpro\emfile\%s.emi' % (file_name), 'wb') as binary_file:
      binary_file.write(immutable_bytes)
   if (os.path.exists('F:')):
      with open('F:\%s.emi' % (file_name), 'wb') as binary_file:
         binary_file.write(immutable_bytes)

def animate(target, timeFactor):
   print('-Animate')
   interpolation.refresh()
   #_run_code_test((37, 10, 1))
   #_run_code_mill_A1((6, 16, 1))
   #
   #_run_code_mill_B1((214, 20, 1))
   #
   #_run_code_mill_D1((228, 56, 1))
   #
   #_run_code_mill_AB1((154, 12, 1))
   #
   _run_code_mill_AB2((97, 73, 1))
   #
   #_run_code_cut_A2((22, 63.5, 1))
   interpolation.check()
   locations, frames = interpolation.animate(target, timeFactor)
   for fcurve in target.animation_data.action.fcurves:
      for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
   print('-Animate done')