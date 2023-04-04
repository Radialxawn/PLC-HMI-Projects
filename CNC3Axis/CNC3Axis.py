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
      
   def get_location(self, value):
      return value - self._min
   
   def get_animation_location(self, value):
      return self.base + value

axis_x = Axis()
axis_y = Axis()
axis_z = Axis()

def run_code():
   R, LS = 3, 0.01 # Bit radius, length step
   FSM, FS = 100, 20 # Feed speed max, feed speed
   interpolation.set_data(mathutils.Vector((axis_x.max, axis_y.max, axis_z.max)))
   interpolation.refresh()
   #C1
   temp_vector = mathutils.Vector((axis_x.get_location(-41), axis_y.get_location(20), axis_z.get_location(0)))
   interpolation.line(temp_vector, FSM)
   interpolation.local_start()
   X = -12
   interpolation.line((X, 0, 0), FSM)
   Z = 7
   interpolation.line((X, 0, Z), FSM)
   interpolation.arc((0, 0, Z), (-7 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-6 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-5 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-5 - R, 0, Z), True, LS, FS)
   interpolation.line((-10.8336, -4.21366, Z), FSM)
   interpolation.arc((0, 12, Z), (10.8336, -4.21366, Z), False, LS, FS)
   interpolation.line((10.8336, -4.21366, 0), FSM)
   interpolation.line((-10.8336, -4.21366, 0), FSM)
   Z = 4.5
   interpolation.line((-6 - R, 0, Z), FSM)
   interpolation.arc((0, 0, Z), (-5 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-5 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-4 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-3.4 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-3.4 - R, 0, Z), True, LS, FS)
   Z = 1.5
   interpolation.line((-4 - R, 0, Z), FSM)
   interpolation.arc((0, 0, Z), (-3 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-2 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (-1 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (0 - R, 0, Z), True, LS, FS)
   interpolation.arc((0, 0, Z), (1 - R, 0, Z), True, LS, FS)
   interpolation.line((0, 0, 0), FSM)
   interpolation.local_end()
   #AB2
   temp_vector = mathutils.Vector((axis_x.get_location(-20.5), axis_y.get_location(-25), axis_z.get_location(0)))
   interpolation.line(temp_vector, FSM)
   #B1
   temp_vector = mathutils.Vector((axis_x.get_location(20), axis_y.get_location(20), axis_z.get_location(0)))
   interpolation.line(temp_vector, FSM)
   #AB1
   temp_vector = mathutils.Vector((axis_x.get_location(50.5), axis_y.get_location(-25), axis_z.get_location(0)))
   interpolation.line(temp_vector, FSM)
   #A1
   temp_vector = mathutils.Vector((axis_x.get_location(63), axis_y.get_location(20), axis_z.get_location(0)))
   interpolation.line(temp_vector, FSM)
   #End
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

def animate(target):
   locations, frames = interpolation.animate(target, 24)
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