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

class Axis:
   _min = 0.0
   _max = 0.0
   min = 0.0
   max = 0.0
   base = 0.0
   object = {}
   
   def set_data(self, object, axis, current):
      self.object = object
      _constraint = object.constraints['Limit Location']
      _min = getattr(_constraint, 'min_%s' % (axis))
      _max = getattr(_constraint, 'max_%s' % (axis))
      current = max(_min, current)
      current = min(_max, current)
      self.base = current
      self.min = 0
      self.max = _max - current
      self._min = _min
      self._max = _max
      
   def get_machine_location(self, value):
      return value - self._min
   
   def get_animation_location(self, value):
      return self.base + value

axis_x = Axis()
axis_y = Axis()
axis_z = Axis()
R, LS = 3, 0.01 # Bit radius, length step
FSM, FS = 100, 20 # Feed speed max, feed speed

def _to_machine_location(x, y, z):
   return (axis_x.get_machine_location(x), axis_y.get_machine_location(y), axis_z.get_machine_location(z))

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
      i = increase and i + step or i - step
      if increase:
         if i >= b:
            break
      else:
         if i <= b:
            break
      count += 1
      if (count == count_max):
         print('_get_range overflow')
         return []
   result.append(b)
   return result

def _run_code_C1(xStep, zStep):
   interpolation.local_start()
   #Top face
   x = -9 - R
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(1.25, 1.5, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      for ix in _get_range(x, 1 - R + 1, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), True, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Mid
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(1.6, 4.5, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      k = -3.4 - R
      for ix in _get_range(x, k, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), True, LS, FS)
      interpolation.arc((0, 0, z), (k, 0, z), True, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Bottom
   interpolation.line((x, 0, 0), FSM)
   for iz in _get_range(4.6, 7, zStep):
      z = iz
      interpolation.line((x, 0, z), FSM)
      kx = -5 - R
      for ix in _get_range(x, kx, xStep):
         interpolation.arc((0, 0, z), (ix, 0, z), True, LS, FS)
      interpolation.arc((0, 0, z), (kx, 0, z), True, LS, FS)
      z = 0
      interpolation.line((x, 0, z), FSM)
   #Curve
   kx, ky, clockwise = -((16.5 + R) * math.sin(math.pi / 6)), -((16.5 + R) * math.cos(math.pi / 6) - 12), False
   for iz in _get_range(4.6, 7, zStep):
      z = iz
      interpolation.line((clockwise and -kx or kx, ky, z), FSM)
      interpolation.arc((0, 12, z), (clockwise and kx or -kx, ky, z), clockwise, LS, FS)
      clockwise = not clockwise
   interpolation.line((kx, ky, 0), FSM)
   #
   interpolation.local_end()

def run_code():
   interpolation.set_data(mathutils.Vector((axis_x.max, axis_y.max, axis_z.max)))
   interpolation.refresh()
   #C1
   interpolation.line(_to_machine_location(-41, 20, 0), FSM)
   _run_code_C1(1, 1)
   #C1-End
   '''
   #D1
   interpolation.line(_to_machine_position(-15, 21, 0), FSM)
   #AB2
   interpolation.line(_to_machine_position(-20.5, -25, 0), FSM)
   #B1
   interpolation.line(_to_machine_position(20, 20, 0), FSM)
   #AB1
   interpolation.line(_to_machine_position(50.5, -25, 0), FSM)
   #A1
   interpolation.line(_to_machine_position(63, 20, 0), FSM)
   #End
   '''
   x, y, z = interpolation.get_location()
   interpolation.line((x, y, 0), FSM)
   interpolation.line((0, 0, 0), FSM)
   interpolation.check()

def export_data():
   f = open('C:\EBpro\emfile\em0.emi', "w")
   locations, speeds = interpolation.get_data()
   lines = []
   def fx(value):
      return int(round(value * 1000))
   for l, s in zip(locations, speeds):
      lines.append('%s,%s,%s:%s,%s,%s\n' % (fx(l.x), fx(l.y), fx(l.z), fx(s.x), fx(s.y), fx(s.z)))
   f.writelines(lines)
   f.close()

def animate(target, timeFactor):
   locations, frames = interpolation.animate(target, timeFactor)
   axis_x.object.animation_data_clear()
   axis_y.object.animation_data_clear()
   axis_z.object.animation_data_clear()
   temp_vector = mathutils.Vector((0, 0, 0))
   for location, frame in zip(locations, frames):
      temp_vector.x = axis_x.get_animation_location(location.x)
      axis_x.object.location = temp_vector
      axis_x.object.keyframe_insert(data_path='location', frame=frame)
      temp_vector.x = 0
      temp_vector.y = axis_y.get_animation_location(location.y)
      axis_y.object.location = temp_vector
      axis_y.object.keyframe_insert(data_path='location', frame=frame)
      temp_vector.y = 0
      temp_vector.z = axis_z.get_animation_location(location.z)
      axis_z.object.location = temp_vector
      axis_z.object.keyframe_insert(data_path='location', frame=frame)
   for o in [target, axis_x.object, axis_y.object, axis_z.object]:
      for fcurve in o.animation_data.action.fcurves:
         for kf in fcurve.keyframe_points:
               kf.interpolation = 'LINEAR'