import re
import math
from pathlib import Path

class GCode(object):
    read_pattern = re.compile(r'(?<=[^\s])(?=[A-Z])', re.IGNORECASE)
    parse_pattern = re.compile(r'([A-Z])(-?\d+\.?\d*)', re.IGNORECASE)

    def __init__(self):
        self.path = None
        self.raw = []
        self.combine = ''
        self.parsed = []

    @staticmethod
    def _clean(line: str) -> str:
        line = re.sub(r'\(.*?\)', '', line)
        line = line.split(';')[0]
        return re.sub(r'\s+', '', line)

    def read(self, _path_):
        self.path = _path_
        with self.path.open(mode='r') as file:
            for line in file:
                l = re.sub(GCode.read_pattern, ' ', GCode._clean(line))
                if len(l) > 0:
                    self.raw.append(l)
        imax = len(self.raw) - 1
        for i, line in enumerate(self.raw):
            self.combine += f'N%d %s%s' % (i, line, '\r\n' if i < imax else '')
        return self

    def chunks(self, _size_):
        chunks = []
        for i in range(0, len(self.combine), _size_):
            chunk = self.combine[i : i + _size_]
            chunks.append(chunk)
        return chunks
    
    def parse(self):
        self.parsed = []
        for line in self.raw:
            matches = re.findall(GCode.parse_pattern, line)
            l = {}
            for letter, value in matches:
                if value:
                    l[letter.lower()] = float(value) if '.' in value else int(value)
                else:
                    l[letter.lower()] = True
            self.parsed.append(l)
    
    def linear(self, _tolerance_):
        relative = False
        cx, cy, cz = 0, 0, 0
        points = [[cx, cy, cz]]
        for line in self.parsed:
            if 'g' in line:
                gc = line['g']
                if gc == 0 or gc == 1:
                    x = line['x'] if 'x' in line else None
                    y = line['y'] if 'y' in line else None
                    z = line['z'] if 'z' in line else None
                    if relative:
                        x = cx if x == None else x + cx
                        y = cy if y == None else y + cy
                        z = cz if z == None else z + cz
                    else:
                        x = cx if x == None else x
                        y = cy if y == None else y
                        z = cz if z == None else z
                    points.append([x, y, z])
                    cx, cy, cz = x, y, z
                elif gc == 2 or gc == 3:
                    x = line['x'] if 'x' in line else None
                    y = line['y'] if 'y' in line else None
                    z = line['z'] if 'z' in line else None
                    i = line['i'] if 'i' in line else 0
                    j = line['j'] if 'j' in line else 0
                    r = line['r'] if 'r' in line else None
                    if relative:
                        x = cx if x == None else cx
                        y = cy if y == None else cy
                        z = cz if z == None else cz
                    else:
                        x = cx if x == None else x
                        y = cy if y == None else y
                        z = cz if z == None else z
                    arc_points = GCode._linear_arc(gc, cx, cy, cz, x, y, z, i, j, r, _tolerance_)
                    points.extend(arc_points)
                    cx, cy, cz = arc_points[-1]
                elif gc == 90:
                    relative = False
                elif gc == 91:
                    relative = True
        return points
    
    @staticmethod
    def _linear_arc(_type_, _sx_, _sy_, _sz_, _ex_, _ey_, _ez_, _i_, _j_, _r_, _tolerance_):
        points = [[_sx_, _sy_, _sz_]]
        if _r_ != None:
            _i_, _j_ = GCode._r_to_ij(_sx_, _sy_, _ex_, _ey_, _r_, _type_ == 2, _r_ < 0)
        cx = _sx_ + _i_
        cy = _sy_ + _j_
        rs = math.hypot(_sx_ - cx, _sy_ - cy)
        re = math.hypot(_ex_ - cx, _ey_ - cy)
        radius = (rs + re) / 2.0
        if radius == 0:
            return points
        angle_s = math.atan2(_sy_ - cy, _sx_ - cx)
        angle_e = math.atan2(_ey_ - cy, _ex_ - cx)
        if _type_ == 2:
            if angle_e >= angle_s:
                    angle_e -= 2 * math.pi
        elif _type_ == 3:
            if angle_e <= angle_s:
                angle_e += 2 * math.pi
        #
        angle_sweep = angle_e - angle_s
        max_step_angle = 2 * math.acos(1 - (_tolerance_ / radius))
        segments = math.ceil(abs(angle_sweep) / max_step_angle)
        segments = max(1, segments)
        for step in range(1, segments + 1):
            t = step / segments
            current_angle = angle_s + (angle_sweep * t)
            if step == segments:
                x = _ex_
                y = _ey_
            else:
                x = cx + radius * math.cos(current_angle)
                y = cy + radius * math.sin(current_angle)                
            points.append([round(x, 4), round(y, 4), _ez_])
        #
        return points

    @staticmethod
    def _r_to_ij(_sx_, _sy_, _ex_, _ey_, _r_, _cw_, _large_=False):
        dx = _ex_ - _sx_
        dy = _ey_ - _sy_
        d = math.sqrt(dx**2 + dy**2)
        if _r_ < d / 2:
            raise ValueError('Radius is too small to reach the end point.')
        h = math.sqrt(_r_**2 - (d / 2)**2)
        mx = (_sx_ + _ex_) / 2
        my = (_sy_ + _ey_) / 2
        nx = -(_ey_ - _sy_) / d
        ny = (_ex_ - _sx_) / d        
        if _cw_: # True if Clockwise (G02), False if Counter-clockwise (G03)
            nx, ny = -nx, -ny
        if _large_: # True if sweep angle > 180 degrees (often denoted by a negative R)
            nx, ny = -nx, -ny
        cx = mx + nx * h
        cy = my + ny * h        
        i = cx - _sx_
        j = cy - _sy_
        return round(i, 4), round(j, 4)