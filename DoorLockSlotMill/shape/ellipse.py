import math

lines = [
	'F$VF$',
	'G0 X0 Y0 Z0',
	'G1 Z$VZ$',
	'G42 D$VT$*0.5',
	'G1 X$VA$*0.5',
	'G38',
]

rad_step = 3
for i in range(int(390/rad_step)):
	x = 0.5*math.cos(math.radians(-i*rad_step))
	y = 0.5*math.sin(math.radians(-i*rad_step))
	l = 'G1 X$VA$*%.5f Y$VB$*%.5f' % (x, y)
	lines.append(l)

lines = lines + [
	'G39',
	'G40',
	'G1 X0 Y0',
	'G1 Z0',
]

for i in range(len(lines)):
	lines[i] = 'N%d %s\n' % (i, lines[i])
lines[-1] = lines[-1][:-1]

with open("ellipse.cnc", "w") as f:
    f.writelines(lines)