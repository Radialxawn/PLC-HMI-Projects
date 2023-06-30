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
FSM, FS = 20, 5 # Feed speed max, feed speed

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

def _run_code_test(location, xyzStep):
   _run_code_test_limit(location, xyzStep)
   #_run_code_test_circle(location, xyzStep)

def _run_code_mill_A1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kx, ky = -0.3, -11
   depth = 21
   #depth = 10
   for sign in [1, -1]:
      for i, iz in enumerate(_get_range(h, h + depth, zStep)):
         if i == 0:
            interpolation.line((kx, 0, iz), FSM)
         interpolation.line((kx, sign * (ky + 4), iz), FS)
         interpolation.line((kx, sign * ky, iz), FS)
         interpolation.line((-kx, sign * ky, iz), FS)
         interpolation.line((-kx, sign * (ky + 4), iz), FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((100, 0, 0), FSM)

def _run_code_mill_B1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   ox = 0.05
   oy = 0.05
   #4Hole
   interpolation.line((-5 - ox, -20 - oy, 0), FS)
   kzs = _get_range(h, h + 5, zStep)
   kzs.append(h + 4.95)
   lastIndex = len(kzs) - 1
   for i, iz in enumerate(kzs):
      '''
      if i == lastIndex:
         ox = 0
         oy = 0
      '''
      interpolation.line((-5 - ox, -20 - oy, iz), FS)
      #
      interpolation.line((-5 - ox, -18 - oy, iz), FS)
      interpolation.arc((-5 - ox, -13 - oy, iz), (-9 - ox, -13 - oy, iz), True, LS, FS)
      interpolation.line((-9 - ox, -10.5 - oy, iz), FS)
      interpolation.line((-11.5 - ox, -10.5 - oy, iz), FS)
      interpolation.arc((-11.5 - ox, -6.5 - oy, iz), (-15.5 - ox, -6.5 - oy, iz), True, LS, FS)
      #
      interpolation.line((-15.5 - ox, 6.5 + oy, iz), FS)
      interpolation.arc((-11.5 - ox, 6.5 + oy, iz), (-11.5 - ox, 10.5 + oy, iz), True, LS, FS)
      interpolation.line((-9 - ox, 10.5 + oy, iz), FS)
      interpolation.line((-9 - ox, 13 + oy, iz), FS)
      interpolation.arc((-5 - ox, 13 + oy, iz), (-5 - ox, 18 + oy, iz), True, LS, FS)
      #
      interpolation.line((5 + ox, 18 + oy, iz), FS)
      interpolation.arc((5 + ox, 13 + oy, iz), (9 + ox, 13 + oy, iz), True, LS, FS)
      interpolation.line((9 + ox, 10.5 + oy, iz), FS)
      interpolation.line((11.5 + ox, 10.5 + oy, iz), FS)
      interpolation.arc((11.5 + ox, 6.5 + oy, iz), (15.5 + ox, 6.5 + oy, iz), True, LS, FS)
      #
      interpolation.line((15.5 + ox, -6.5 - oy, iz), FS)
      interpolation.arc((11.5 + ox, -6.5 - oy, iz), (11.5 + ox, -10.5 - oy, iz), True, LS, FS)
      interpolation.line((9 + ox, -10.5 - oy, iz), FS)
      interpolation.line((9 + ox, -13 - oy, iz), FS)
      interpolation.arc((5 + ox, -13 - oy, iz), (5 + ox, -18 - oy, iz), True, LS, FS)
      #
      interpolation.line((-5 - ox, -18 - oy, iz), FS)
      interpolation.line((-5 - ox, -20 - oy, iz), FS)
   #Out face
   ox = 0.05
   oy = 0.05
   kxs = [-10, -15.5, -15.5, -10, 10, 15.5, 15.5,  10, -10]
   kys = [-18,   -13,    13,  18, 18,   13,  -13, -18, -18]
   kfs = [FSM,   FSM,    FS, FSM, FS,  FSM,   FS, FSM,  FS]
   final = False
   interpolation.line((kxs[0], kys[0], iz), FS)
   for iz in _get_range(h + 5.1, h + 11.9, zStep):
      if (iz >= h + 10.5) and not final:
         kxs.reverse()
         kys.reverse()
         kfs = [FS, FS,    FSM, FS, FSM,  FS,   FSM, FS,  FSM]
         final = True
      for x, y, f in zip(kxs, kys, kfs):
         dx = x < 0 and -ox or ox
         dy = y < 0 and -oy or oy
         interpolation.line((x + dx, y + dy, iz), f)
   kxs.reverse()
   kys.reverse()
   kfs = [FSM,   FSM,    FS, FSM, FS,  FSM,   FS, FSM,  FS]
   for x, y, f in zip(kxs, kys, kfs):
      dx = x < 0 and -ox or ox
      dy = y < 0 and -oy or oy
      interpolation.line((x, y, iz), f)
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_mill_D1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], 0, 0), FSM)
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   #
   kx = (9.5 - R * 2) / 2
   kxs = [kx,   kx, -kx,  -kx]
   kys = [-3.5, 26,  26, -3.5]
   #   
   interpolation.line((kxs[0], kys[0], 0), FS)
   for iz in _get_range(h + 0.1, h + 20, zStep):
      for x, y in zip(kxs, kys):
         interpolation.line((x, y, iz), FS)
   interpolation.line((0, 0, 0), FS)
   #
   for _ in range(2):
      interpolation.line((kxs[0], kys[0], 0), FS)
      for iz in _get_range(h + 5, h + 21, zStep * 10):
         for x, y in zip(kxs, kys):
            interpolation.line((x, y, iz), FS)
   interpolation.line((0, 0, 0), FS)
   #
   interpolation.local_end()
   x, y, z = interpolation.get_location()
   interpolation.line((x, 0, 0), FSM)
   interpolation.line((0, 0, 0), FSM)

def _run_code_AB_top_carve(h, xyzStep):
   xStep, yStep, zStep = xyzStep[0], xyzStep[1], xyzStep[2]
   #Top
   foilRadius = 16.5
   up = True
   sy = 7
   ey = 65
   firstZ = True
   kzs = _get_range(h + 0.3, h + 4, zStep)
   lastIndex = len(kzs) - 1
   for i, iz in enumerate(kzs):
      if i == lastIndex:
         sy = 1
         firstZ = True
      id = foilRadius - (iz - h)
      iw = math.sin(math.acos(id / foilRadius)) * foilRadius
      iw = max(0, iw - R * 0.7)
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
      for iz in _get_range(h + 4.1, h + 5, zStep):
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
   kxs = [     21,      18,   18,   21]
   kys = [56.2135, 47.9714, 10.8, 10.8]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(11, 25, zStep * 2):
      for x, y, f in zip(kxs, kys, kfs):
         interpolation.line((x, y, iz), f)
   interpolation.line((kxs[3], kys[3], 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #SideB
   kxs = [ -21,  -18, -18, -21]
   kys = [10.8, 10.8,  62,  62]
   kfs = [FSM, FS, FS, FS]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(11, 25, zStep * 2):
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
      _run_code_test,         (117, 43, 1),       (1, 1, 0.4), (0, 0),
      _run_code_mill_A1,      (5.8, 16.9, 1),     (1, 1, 0.4), (0, 14),
      _run_code_mill_B1,      (213.89, 21.12, 1), (1, 3, 0.4), (0, 0),
      _run_code_mill_D1,      (228.3, 56.9, 1),   (1, 1, 0.4), (0, 0),
      _run_code_mill_AB1,     (117, 43, 1),       (5, 1, 0.4), (0, 0),
      _run_code_mill_AB2,     (117, 43, 1),       (5, 1, 0.4), (0, 0),
      _run_code_cut_A2,       (117, 43, 1),       (1, 1, 1),   (0, 0),
   ]
   print('-Export data')
   timeMinutesTotal = 0
   for i in range(0, len(fs), 4):
      interpolation.refresh()
      function, center, xyzStep, setZOffset = fs[i], fs[i + 1], fs[i + 2], fs[i + 3]
      function(center, xyzStep)
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
   #_run_code_test((37, 10, 1),              (1, 1, 0.4))
   #_run_code_mill_A1((6, 16, 1),           (1, 1, 0.4))
   #_run_code_mill_B1((214, 20, 1),           (1, 3, 0.4))
   _run_code_mill_D1((228, 56, 1),           (1, 1, 0.4))
   #_run_code_mill_AB1((154, 12, 1),      (5, 1, 0.4))
   #_run_code_mill_AB2((100, 12, 1),       (5, 1, 0.4))
   #_run_code_cut_A2((22, 76, 1),           (1, 1, 1))
   interpolation.check()
   locations, frames = interpolation.animate(target, timeFactor)
   for fcurve in target.animation_data.action.fcurves:
      for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
   print('-Animate done')