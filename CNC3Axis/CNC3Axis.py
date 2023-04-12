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

R, LS = 3, 0.01 # Bit radius, length step
FSM, FS = 100, 10 # Feed speed max, feed speed

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

def _run_code_test(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   interpolation.line((-5 - R, 0, 0), FSM)
   interpolation.arc((0, 0, 0), (-5 - R, 0, 0), True, 0.1, FS)
   interpolation.arc((0, 0, 0), (-5 - R, 0, 0), False, 0.1, FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()

def _run_code_mill_A1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kx, ky = -0.1, -10
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
   #Out face
   ox, oy = -16.5 - R, -16.5 - R
   dx, dy = -12.5 - R, -14 - R
   for iz in _get_range(h, h + 5, zStep):
      interpolation.line((ox, oy, iz), FS)
      for id in _get_range(oy, dy, yStep):
         interpolation.line((id, id, iz), FS)
         interpolation.line((id, -id, iz), FS)
         interpolation.line((-id, -id, iz), FS)
         interpolation.line((-id, id, iz), FS)
         interpolation.line((id, id, iz), FS)
      for id in _get_range(dy, dx, yStep):
         interpolation.line((id, dy, iz), FS)
         interpolation.line((id, -dy, iz), FS)
         interpolation.line((-id, -dy, iz), FS)
         interpolation.line((-id, dy, iz), FS)
         interpolation.line((id, dy, iz), FS)
      interpolation.line((ox, oy, iz), FS)
   interpolation.line((ox, oy, 0), FS)
   #Out edge
   kxs = [-16, -6, 6, 16, 16, 6, -6, -16, -16]
   kys = [-8, -18, -18, -8, 8, 18, 18, 8, -8]
   iz_last = h
   for iz in _get_range(h, h + 5, zStep):
      for id in _get_range(2, 0, yStep * 0.7071067):
         for i, (x, y) in enumerate(zip(kxs, kys)):
            dx = x < 0 and -id or id
            dy = y < 0 and -id or id
            if i == 0:
               interpolation.line((x + dx, y + dy, iz_last), FS)
            interpolation.line((x + dx, y + dy, iz), FS)
      iz_last = iz
   interpolation.line((ox, oy, 0), FS)
   interpolation.line((0, 0, 0), FSM)
   #4Hole
   interpolation.line((-17.5, -17.5, 0), FSM)
   for iz in _get_range(h, h + 5, zStep):
      interpolation.line((-17.5, -17.5, 0), FS)
      for id in _get_range(2, 0, yStep * 0.7071067):
         dx, dy = -id, -id
         interpolation.line((-15.5 + dx, -6.5 + dy, iz), FS)
         interpolation.arc((-11.5 + dx, -6.5 + dy, iz), (-11.5 + dx, -10.5 + dy, iz), False, LS, FS)
         interpolation.line((-9 + dx, -10.5 + dy, iz), FS)
         interpolation.line((-9 + dx, -13 + dy, iz), FS)
         interpolation.arc((-5 + dx, -13 + dy, iz), (-5 + dx, -17 + dy, iz), False, LS, FS)
         interpolation.line((-4 + dx, -17 + dy, iz), FS)
         dx, dy = id, -id
         interpolation.line((5 + dx, -17 + dy, iz), FS)
         interpolation.arc((5 + dx, -13 + dy, iz), (9 + dx, -13 + dy, iz), False, LS, FS)
         interpolation.line((9 + dx, -10.5 + dy, iz), FS)
         interpolation.line((11.5 + dx, -10.5 + dy, iz), FS)
         interpolation.arc((11.5 + dx, -6.5 + dy, iz), (15.5 + dx, -6.5 + dy, iz), False, LS, FS)
         dx, dy = id, id
         interpolation.line((15.5 + dx, 6.5 + dy, iz), FS)
         interpolation.arc((11.5 + dx, 6.5 + dy, iz), (11.5 + dx, 10.5 + dy, iz), False, LS, FS)
         interpolation.line((9 + dx, 10.5 + dy, iz), FS)
         interpolation.line((9 + dx, 12.5 + dy, iz), FS)
         interpolation.arc((5 + dx, 13 + dy, iz), (5 + dx, 17 + dy, iz), False, LS, FS)
         dx, dy = -id, id
         interpolation.line((-5 + dx, 17 + dy, iz), FS)
         interpolation.arc((-5 + dx, 13 + dy, iz), (-9 + dx, 13 + dy, iz), False, LS, FS)
         interpolation.line((-9 + dx, 10.5 + dy, iz), FS)
         interpolation.line((-11.5 + dx, 10.5 + dy, iz), FS)
         interpolation.arc((-11.5 + dx, 6.5 + dy, iz), (-15.5 + dx, 6.5 + dy, iz), False, LS, FS)
         interpolation.line((-15.5 + dx, -5.5 + dy, iz), FS)
         interpolation.line((-15.5 + dx, -7.5 + dy, iz), FS)
   interpolation.line((-15.5 + dx, -7.5 + dy, 0), FS)
   interpolation.line((0, 0, 0), FS)
   interpolation.local_end()

def _run_code_mill_C1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   #Top face
   x = -9 - R
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(h, h + 0.5, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      for ix in _get_range(x, 1 - R + 1, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), False, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Mid
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(h + 0.5, h + 3.5, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      k = -3.4 - R
      for ix in _get_range(x, k, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), False, LS, FS)
      interpolation.arc((0, 0, z), (k, 0, z), False, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Bottom
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(h + 3.5, h + 6, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      kx = -5 - R
      for ix in _get_range(x, kx, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), False, LS, FS)
      interpolation.arc((0, 0, z), (kx, 0, z), False, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Curve
   kx, ky, clockwise = -((16.5 + R) * math.sin(math.pi / 6)), -((16.5 + R) * math.cos(math.pi / 6) - 12), False
   for iz in _get_range(h + 3.5, h + 6, zStep):
      z = iz
      ix = clockwise and -kx or kx
      interpolation.line((ix, ky, z), FSM)
      interpolation.arc((0, 12, z), (-ix, ky, z), clockwise, LS, FS)
      clockwise = not clockwise
   interpolation.line((-ix, ky, 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #Weld cut
   r0, r = 9, 6.5
   kas = [25, -50, -130, 180 - 25]
   for i, ka in enumerate(kas):
      x0, y0 = -math.cos(math.radians(ka)) * r0, -math.sin(math.radians(ka)) * r0
      x, y = -math.cos(math.radians(ka)) * r, -math.sin(math.radians(ka)) * r
      iz = h + 3.5 + 0.2
      if i == 0:
         interpolation.line((x0, y0, 0), FS)
      else:
         interpolation.arc((0, 0, iz), (x0, y0, iz), True, 1, FS)
      interpolation.line((x0, y0, iz), FS)
      interpolation.line((x, y, iz), FS)
      interpolation.line((x0, y0, iz), FS)
   interpolation.line((x0, y0, 0), FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()

def _run_code_mill_D1(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   kxs = [-1, -1, 1, 1]
   kys = [-23, 7.75, 7.75, -23]
   first = False
   for iz in _get_range(h, h + 21, zStep):
     for x, y in zip(kxs, kys):
         if not first:
            interpolation.line((x, y, 0), FS)
            first = True
         interpolation.line((x, y, iz), FS)
   interpolation.line((0, 0, 0), FSM)
   kxs = [-13.5, -12.75, -12.75, -13.5] + [-13.5, -12.5, -12.5, -13.5]
   kys = [-1, -0.5, -3.5, -3] + [-1, -0.5, -3.5, -3]
   for sign in [1, -1]:
      first = False
      for iz in _get_range(h + 7, h + 14, zStep):
         for x, y in zip(kxs, kys):
            if not first:
               interpolation.line((sign * x, y, 0), FS)
               first = True
            interpolation.line((sign * x, y, iz), FS)
      interpolation.line((sign * x, y, 0), FS)
   interpolation.line((0, 0, 0), FSM)
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
         for iy in _get_range(17 * factor - 5.5, 0, 1):
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
      for i, ix in enumerate(_get_range(-0.5, 2, yStep)):
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
   kxs = [-33.2574, -30.2575, 17.9714, 26.2135]
   kys = [-20, -17, -17, -20]
   interpolation.line((kxs[0], kys[0], 0), FSM)
   for iz in _get_range(8.1, 27, zStep):
      factor = math.cos(math.asin(1 - (iz / 17)))
      for iy in _get_range(17 * factor - 14, 0, 1):
         interpolation.line((kxs[0], kys[0], iz), FSM)
         interpolation.line((kxs[1], kys[1] - iy, iz), FS)
         interpolation.line((kxs[2], kys[2] - iy, iz), FS)
         interpolation.line((kxs[3], kys[3], iz), FS)
   interpolation.line((kxs[3], kys[3], 0), FS)
   interpolation.line((0, 0, 0), FSM)
   #SideB
   kx, oy = -34, 20
   interpolation.line((kx, oy, 0), FSM)
   for iz in _get_range(8.1, 27, zStep):
      interpolation.line((kx, oy, iz), FSM)
      factor = math.cos(math.asin(1 - (iz / 17)))
      left = True
      for iy in _get_range(17 * factor - 14, 0, 1):
         ix = left and -kx or kx
         ky = oy - 3 + iy
         interpolation.line((-ix, ky, iz), FS)
         interpolation.line((ix, ky, iz), FS)
         left = not left
   interpolation.line((kx, oy, 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   #
   interpolation.local_end()

def _run_code_cut_A2(location, xyzStep):
   h, xStep, yStep, zStep = location[2], xyzStep[0], xyzStep[1], xyzStep[2]
   interpolation.line((location[0], location[1], 0), FSM)
   interpolation.local_start()
   radius = 12.5
   kx, ky = 2 + radius, 35
   for iz in _get_range(h + 8.75, h + 9.25, zStep):
      for i, ix in enumerate(_get_range(-1 - radius, 4 - radius, yStep)):
         if i == 0:
            interpolation.line((kx, 0, 0), FS)
         interpolation.line((kx, 0, iz), FS)
         interpolation.line((-ix, 0, iz), FS)
         interpolation.line((-ix, ky, iz), FS)
         interpolation.line((kx, ky, iz), FS)
   interpolation.line((kx, ky, 0), FS)
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

def int_to_dword(value):
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
      _run_code_test,         (183, 69, 1),        (1, 1, 1),
      _run_code_mill_A1,      (183, 69, 1),        (1, 1, 1),
      _run_code_mill_B1,      (140, 70, 1),        (1, 1, 1),
      _run_code_mill_C1,      (79, 70, 1),         (1, 1, 1),
      _run_code_mill_D1,      (105, 71, 1),        (1, 1, 1),
      _run_code_mill_AB1,     (170.5, 25, 0.5),    (1, 1, 1),
      _run_code_mill_AB2,     (99.5, 25, 0.5),     (1, 1, 1),
      _run_code_cut_A2,       (16, 42, 2.5),       (1, 1, 1),
   ]
   print('-Export data')
   for i in range(0, len(fs), 3):
      interpolation.refresh()
      function, center, xyzStep = fs[i], fs[i + 1], fs[i + 2]
      function(center, xyzStep)
      interpolation.line((0, 0, 0), FSM)
      _export_data(function.__name__[10:])
      interpolation.check()
   print('-Export data done')

def _export_data(file_name):
   locations, speeds = interpolation.get_data()
   def fx(value):
      return int(round(value * 1000))
   byte_arr = []
   for i in range(6):
      byte_arr += int_to_dword(len(locations))
   for l, s in zip(locations, speeds):
      byte_arr += int_to_dword(fx(l.x))
      byte_arr += int_to_dword(fx(l.y))
      byte_arr += int_to_dword(fx(l.z))
      byte_arr += int_to_dword(fx(s.x))
      byte_arr += int_to_dword(fx(s.y))
      byte_arr += int_to_dword(fx(s.z))
   some_bytes = bytearray(byte_arr)
   immutable_bytes = bytes(some_bytes)
   with open(('C:\EBpro\emfile\%s.emi' % file_name), 'wb') as binary_file:
      binary_file.write(immutable_bytes)

def animate(target, timeFactor):
   print('-Animate')
   interpolation.refresh()
   _run_code_test((183, 69, 1),               (1, 1, 1))
   #_run_code_mill_A1((183, 69, 1),           (1, 1, 1))
   #_run_code_mill_B1((140, 70, 1),           (1, 1, 1))
   #_run_code_mill_C1((79, 70, 1),            (1, 1, 1))
   #_run_code_mill_D1((105, 71, 1),           (1, 1, 1))
   #_run_code_mill_AB1((170.5, 25, 0.5),      (1, 1, 1))
   #_run_code_mill_AB2((99.5, 25, 0.5),       (1, 1, 1))
   _run_code_cut_A2((16, 42, 2.5),           (1, 1, 1))
   interpolation.line((0, 0, 0), FSM)
   interpolation.check()
   locations, frames = interpolation.animate(target, timeFactor)
   for fcurve in target.animation_data.action.fcurves:
      for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
   print('-Animate done')