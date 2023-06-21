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

R, LS = 3, 0.05 # Bit radius, length step
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
      #interpolation.line((-15.5 - o, -6.5, iz), FS) # offset
      #
      #interpolation.line((-15.5 - o, 6.5, iz), FS) # offset
      interpolation.line((-15.5, 6.5, iz), FS)
      interpolation.arc((-11.5, 6.5, iz), (-11.5, 10.5, iz), True, LS, FS)
      interpolation.line((-9, 10.5, iz), FS)
      interpolation.line((-9, 13, iz), FS)
      interpolation.arc((-5, 13, iz), (-5, 18, iz), True, LS, FS)
      #
      #interpolation.line((-5, 18 + o, iz), FS) # offset
      #interpolation.line((5, 18 + o, iz), FS) # offset
      interpolation.line((5, 18, iz), FS)
      interpolation.arc((5, 13, iz), (9, 13, iz), True, LS, FS)
      interpolation.line((9, 10.5, iz), FS)
      interpolation.line((11.5, 10.5, iz), FS)
      interpolation.arc((11.5, 6.5, iz), (15.5, 6.5, iz), True, LS, FS)
      #interpolation.line((15.5 + o, 6.5, iz), FS) # offset
      #
      #interpolation.line((15.5 + o, -6.5, iz), FS) # offset
      interpolation.line((15.5, -6.5, iz), FS)
      interpolation.arc((11.5, -6.5, iz), (11.5, -10.5, iz), True, LS, FS)
      interpolation.line((9, -10.5, iz), FS)
      interpolation.line((9, -13, iz), FS)
      interpolation.arc((5, -13, iz), (5, -18, iz), True, LS, FS)
      #interpolation.line((5, -18 - o, iz), FS) # offset
      #
      #interpolation.line((-5, -18 - o, iz), FS) # offset
      interpolation.line((-5, -18, iz), FS)
      interpolation.line((-5, -20, iz), FS)
   #Out face
   kxs = [-10, -15.5, -15.5, -10, 10, 15.5, 15.5,  10, -10]
   kys = [-18,   -13,    13,  18, 18,   13,  -13, -18, -18]
   kfs = [FSM,   FSM,    FS, FSM, FS,  FSM,   FS, FSM,  FS]
   interpolation.line((kxs[0], kys[0], iz), FS)
   for iz in _get_range(h + 5.1, h + 11.5, zStep):
     for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((x, y, 0), FS)
   #
   interpolation.line((0, 0, 0), FS)
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_D1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kxs = [ 1.5, 1.5, -1.5, -1.5]
   kys = [-3.5,  26,   26, -3.5]
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
   foilRadius = 16.5
   up = True
   sy = 7
   ey = 65
   firstZ = True
   for iz in _get_range(h, h + 4, zStep):
      id = foilRadius - (iz - h)
      iw = 2 * math.sin(math.acos(id / foilRadius)) * foilRadius
      iw = max(0, iw - R * 2)
      kxs = []
      kys = []
      for ix in _get_range(-iw, iw, xStep):
         kxs.append(ix)
         kys.append(up and sy or ey)
         kxs.append(ix)
         kys.append(up and ey or sy)
         up = not up
      for ix, iy in zip(kxs, kys):
         if firstZ:
            interpolation.line((ix, iy, 0), FSM)
            firstZ = False
         interpolation.line((ix, iy, iz), FS)
   interpolation.line((ix, iy, 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #Carve
   kxs = [-17,-11.6901,      -8,      -8,     -17]
   kys = [4,   3.99282, 9.89692, 41.5718, 46.6807]
   kos = [0,         1,       1,       1,       0]
   def _carve(sign):
      if sign == -1:
         kxs.reverse()
         kys.reverse()
         kos.reverse()
      interpolation.line((sign * kxs[0], kys[0], h + 3), FSM)
      for iz in _get_range(h + 4, h + 5, zStep):
         for ox in [3, 0]:
            for ix, iy, io in zip(kxs, kys, kos):
               fx = sign * (ix - ox * io)
               interpolation.line((fx, iy, iz), FSM)
      interpolation.line((fx, iy, 0), FS)
   _carve(1)
   interpolation.line((0, 0, 0), FSM)
   _carve(-1)
   interpolation.line((0, 0, 0), FSM)
   #Fillet
   for sign in [1, -1]:
      interpolation.line((sign * -11.1, 5, 0), FSM)
      interpolation.line((sign * -11.1, 5, h + 5), FSM)
      interpolation.line((sign * -9.6, 5, h + 3.5), FS)
      interpolation.line((sign * -11, 5, h + 5), FS)
      interpolation.line((sign * -10.6, 5, h + 5), FS)
      interpolation.arc((sign * -9.6, 5, h + 5), (sign * -9.6, 3.9, h + 5), sign < 0, LS, FS, 'xz')
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
   kxs = [     21,      18, 18, 21]
   kys = [56.2135, 47.9714,  8,  8]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(10.1, 25, zStep):
      for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((kxs[3], kys[3], 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #SideB
   kxs = [-21, -18, -18, -21]
   kys = [  8,   8,  62,  62]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(10.1, 25, zStep):
      for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((kxs[3], kys[3], 0), FSM)
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
      _run_code_mill_B1,      (214.03, 20.59, 1),        (1, 3, 0.4),
      _run_code_mill_D1,      (228.55, 56.3, 1),        (1, 1, 0.4),
      _run_code_mill_AB1,     (117, 43, 1),      (5, 1, 0.4),
      _run_code_mill_AB2,     (117, 43, 1),      (5, 1, 0.4),
      _run_code_cut_A2,       (117, 43, 1),      (1, 1, 1),
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
   #_run_code_mill_A1((6, 16, 1),           (1, 1, 1))
   #_run_code_mill_B1((214, 20, 1),           (1, 3, 1))
   #_run_code_mill_D1((228, 56, 1),           (1, 1, 1))
   #_run_code_mill_AB1((154, 12, 1),      (5, 1, 1))
   _run_code_mill_AB2((100, 12, 1),       (5, 1, 1))
   #_run_code_cut_A2((22, 76, 1),           (1, 1, 1))
   interpolation.check()
   locations, frames = interpolation.animate(target, timeFactor)
   for fcurve in target.animation_data.action.fcurves:
      for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
   print('-Animate done')