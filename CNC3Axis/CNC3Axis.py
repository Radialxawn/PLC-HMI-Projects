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

R, LS = 3, 0.07 # Bit radius, length step
FSM, FS = 20, 4 # Feed speed max, feed speed

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

def _run_code_test_limit(location, xyzStep):
   for i in range(48):
      interpolation.line((234, 86, 0), FSM)
      interpolation.line((0, 0, 0), FSM)
      
def _run_code_test_circle(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   interpolation.line((-39 - R, 0, 0), FSM)
   interpolation.arc((0, 0, 0), (-39 - R, 0, 0), True, LS, FS)
   interpolation.arc((0, 0, 0), (-39 - R, 0, 0), False, LS, FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()

def _run_code_test_fixture_D1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kxs = [ 0, -13.5, -13.5, -2,  -2,   2,  0]
   kys = [32,    32,    23, 23, 5.5, 5.5, 32]
   interpolation.line((kxs[0], kys[0], 0), FS)
   for iz in _get_range(h, h + 17, zStep):
      for x, y in zip(kxs, kys):
         interpolation.line((x, y, iz), FS)
   interpolation.line((x, y, 0), FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()

def _run_code_test(location, xyzStep):
   #_run_code_test_limit(location, xyzStep)
   #_run_code_test_circle(location, xyzStep)
   _run_code_test_fixture_D1(location, xyzStep)

def _run_code_mill_A1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kx, ky = -0.1, -11
   for sign in [1, -1]:
      for i, iz in enumerate(_get_range(h, h + 21, zStep)):
         if i == 0:
            interpolation.line((kx, 0, iz), FS)
         interpolation.line((kx, sign * (ky + 4), iz), FS)
         interpolation.line((kx, sign * ky, iz), FS)
         interpolation.line((-kx, sign * ky, iz), FS)
         interpolation.line((-kx, sign * (ky + 4), iz), FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()

def _run_code_mill_B1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   o = 0.5
   #4Hole
   interpolation.line((-5, -20, 0), FS)
   for iz in _get_range(h, h + 5, zStep):
      interpolation.line((-5, -20, iz), FS)
      #
      interpolation.line((-5, -18, iz), FS)
      interpolation.arc((-5, -13, iz), (-9, -13, iz), True, LS, FS)
      interpolation.line((-9, -10.5, iz), FS)
      interpolation.line((-11.5, -10.5, iz), FS)
      interpolation.arc((-11.5, -6.5, iz), (-15.5, -6.5, iz), True, LS, FS)
      interpolation.line((-15.5 - o, -6.5, iz), FS) # offset
      #
      interpolation.line((-15.5 - o, 6.5, iz), FS) # offset
      interpolation.line((-15.5, 6.5, iz), FS)
      interpolation.arc((-11.5, 6.5, iz), (-11.5, 10.5, iz), True, LS, FS)
      interpolation.line((-9, 10.5, iz), FS)
      interpolation.line((-9, 13, iz), FS)
      interpolation.arc((-5, 13, iz), (-5, 18, iz), True, LS, FS)
      #
      interpolation.line((-5, 18 + o, iz), FS) # offset
      interpolation.line((5, 18 + o, iz), FS) # offset
      interpolation.line((5, 18, iz), FS)
      interpolation.arc((5, 13, iz), (9, 13, iz), True, LS, FS)
      interpolation.line((9, 10.5, iz), FS)
      interpolation.line((11.5, 10.5, iz), FS)
      interpolation.arc((11.5, 6.5, iz), (15.5, 6.5, iz), True, LS, FS)
      interpolation.line((15.5 + o, 6.5, iz), FS) # offset
      #
      interpolation.line((15.5 + o, -6.5, iz), FS) # offset
      interpolation.line((15.5, -6.5, iz), FS)
      interpolation.arc((11.5, -6.5, iz), (11.5, -10.5, iz), True, LS, FS)
      interpolation.line((9, -10.5, iz), FS)
      interpolation.line((9, -13, iz), FS)
      interpolation.arc((5, -13, iz), (5, -18, iz), True, LS, FS)
      interpolation.line((5, -18 - o, iz), FS) # offset
      #
      interpolation.line((-5, -18 - o, iz), FS) # offset
      interpolation.line((-5, -20, iz), FS)
   interpolation.line((-5, -20, 0), FS)
   interpolation.line((0, 0, 0), FS)
   interpolation.local_end()

def _run_code_mill_D1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kxs = [-1.5,  -1.5,   1.5,  1.5]
   kys = [-3.5, 26, 26, -3.5]
   first = False
   for iz in _get_range(h, h + 22, zStep):
     for x, y in zip(kxs, kys):
         if not first:
            interpolation.line((x, y, 0), FS)
            first = True
         interpolation.line((x, y, iz), FS)
   interpolation.line((0, 0, 0), FS)
   interpolation.local_end()

def _run_code_AB_top_carve(h, xyzStep):
   xStep, yStep, zStep = xyzStep[0], xyzStep[1], xyzStep[2]
   #Top
   kx, ky = -35, -17.5
   for iz in _get_range(h, h + 4, zStep):
      interpolation.line((kx, ky, 0), FSM)
      left = True
      factor = math.cos(math.asin(1 - (iz / 17)))
      for iy in _get_range(-17 * factor - R, 17 * factor - R, yStep):
         ix = left and -kx or kx
         interpolation.line((-ix, iy, iz), FS)
         interpolation.line((ix, iy, iz), FS)
         left = not left
      interpolation.line((left and -kx or kx, iy, iz), FS)
   interpolation.line((0, 0, 0), FSM)
   #Carve
   kxs = [-35.0396, -20.6396, 11.5718, 16.768]
   kys = [-17, -8, -8, -17]
   def _carve(sign):
      interpolation.line((kxs[0], sign * kys[0], h + 3), FSM)
      for iz in _get_range(h + 4, h + 5, zStep):
         factor = math.cos(math.asin(1 - (iz / 17)))
         for iy in _get_range(17 * factor - 7, 0, yStep):
            interpolation.line((kxs[0], sign * kys[0], iz), FSM)
            interpolation.line((kxs[1], sign * (kys[1] - iy), iz), FS)
            interpolation.line((kxs[2], sign * (kys[2] - iy), iz), FS)
            interpolation.line((kxs[3], sign * kys[3], iz), FS)
      interpolation.line((kxs[3], sign * kys[3], 0), FS)
   _carve(1)
   interpolation.line((0, 0, 0), FSM)
   _carve(-1)
   interpolation.line((0, 0, 0), FSM)
   #Fillet
   for sign in [1, -1]:
      for i, ix in enumerate(_get_range(-0.5, 2, xStep)):
         if i == 0:
            interpolation.line((-25.5 + ix, sign * (8.5 + R), 0), FSM)
         interpolation.line((-25.5 + ix, sign * (8.5 + R), 5.5), FS)
         interpolation.line((-25.5 + ix, sign * (7.5 + R), 5.5), FS)
         interpolation.arc((-25.5 + ix + sign * 1, sign * (7.5 + R), 5.5), (-25.5 + ix + sign * 1, sign* (7.5 + R) - 1, 5.5), sign < 0, LS, FS, 'yz')
         interpolation.line((-25.5 + ix, sign * (5.5 + R), 4), FS)
         interpolation.line((-25.5 + ix, sign * (8.5 + R), 4), FS)
      interpolation.line((0, 0, 0), FSM)

def _run_code_mill_AB1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   _run_code_AB_top_carve(h, xyzStep)
   interpolation.local_end()

def _run_code_mill_AB2(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   _run_code_AB_top_carve(h, xyzStep)
   #SideA
   kxs = [26.2135, 17.9714, -30.2575, -33.2574]
   kys = [-21, -18, -18, -21]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(10.1, 25, zStep):
      for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((kxs[3], kys[3], 0), FS)
   interpolation.line((0, 0, 0), FSM)
   #SideB
   kxs = [-34, -34, 34, 34]
   kys = [21, 18, 18, 21]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(10.1, 25, zStep):
      for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((kxs[3], kys[3], 0), FS)
   interpolation.line((0, 0, 0), FSM)
   #
   interpolation.local_end()

def _run_code_cut_A2(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0] - 16.5, location[1] - 12.5, 0), FSM)
   interpolation.local_start()
   interpolation.line((0, -2, 0), FS)
   for iz in _get_range(h + 25.75, h + 26.25, zStep):
      for i, iy in enumerate(_get_range(0, 4, yStep)):
         interpolation.line((0, -2, iz), FS)
         interpolation.line((0, iy, iz), FS)
         interpolation.line((33, iy, iz), FS)
         interpolation.line((33, -2, iz), FS)
   interpolation.line((0, -2, 0), FS)
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
      _run_code_test,         (117, 43, 1),        (1, 1, 0.4),
      _run_code_mill_A1,      (6.1, 16.4, 1),        (1, 1, 0.4),
      _run_code_mill_B1,      (214.05, 20.675, 1),        (1, 3, 0.4),
      _run_code_mill_D1,      (228.55, 56.3, 1),        (1, 1, 0.4),
      _run_code_mill_AB1,     (117, 43, 0.5),      (0.2, 3, 0.4),
      _run_code_mill_AB2,     (117, 43, 0.5),      (0.2, 3, 0.4),
      _run_code_cut_A2,       (117, 43, 1.5),      (1, 1, 1),
   ]
   print('-Export data')
   timeMinutesTotal = 0
   for i in range(0, len(fs), 3):
      interpolation.refresh()
      function, center, xyzStep = fs[i], fs[i + 1], fs[i + 2]
      function(center, xyzStep)
      function_name = function.__name__[10:]
      print(function_name)
      _export_data(function_name)
      timeMinutes = interpolation.check()
      if not 'test' in function_name:
         timeMinutesTotal += timeMinutes
   print('-Export data done: Total time: %s minutes' % ('{:.2f}'.format(timeMinutesTotal)))

def _export_data(file_name):
   locations, speeds = interpolation.get_data()
   def fx(value):
      return int(round(value * 1000))
   byte_arr = []
   byte_arr += _int_to_dword(len(locations))
   byte_arr += _int_to_dword(len(locations))
   byte_arr += _int_to_word(3)
   byte_arr += _int_to_word(4)
   byte_arr += _int_to_word(5)
   byte_arr += _int_to_word(6)
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
   with open(('C:\EBpro\emfile\%s.emi' % file_name), 'wb') as binary_file:
      binary_file.write(immutable_bytes)

def animate(target, timeFactor):
   print('-Animate')
   interpolation.refresh()
   #_run_code_test((37, 10, 1),              (1, 1, 1))
   #_run_code_mill_A1((180, 67, 1),           (1, 1, 1))
   _run_code_mill_B1((137, 64, 1),           (1, 3, 1))
   #_run_code_mill_D1((102, 50, 1),           (1, 1, 1))
   #_run_code_mill_AB1((167.5, 23, 0.5),      (0.2, 3, 1))
   #_run_code_mill_AB2((96.5, 23, 0.5),       (0.2, 3, 1))
   #_run_code_cut_A2((22, 76, 1.5),           (1, 1, 1))
   interpolation.check()
   locations, frames = interpolation.animate(target, timeFactor)
   for fcurve in target.animation_data.action.fcurves:
      for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
   print('-Animate done')