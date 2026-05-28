import math

rad_step = 1

for i in range(int(390/rad_step)):
	x = 0.5*math.cos(math.radians(-i*rad_step))
	y = 0.5*math.sin(math.radians(-i*rad_step))
	print('N%d G1 X$VA$*%.5f Y$VB$*%.5f' % (i+20, x, y))