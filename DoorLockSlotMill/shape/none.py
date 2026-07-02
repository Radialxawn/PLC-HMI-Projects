shape = {
	'circle' : [
		'LET #r : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		#
		'G0 X-#r',
		'G1 Z$VZ$',
		'G2 X#r R#r',
		'G2 X-#r R#r',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'rect' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		#
		'G0 X-#a',
		'G1 Z$VZ$',
		'G1 Y#b',
		'G1 X#a',
		'G1 Y-#b',
		'G1 X-#a',
		'G1 Y0',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'capsule' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		#
		'G0 X-#a',
		'G1 Z$VZ$',
		'G2 X-#a+#r Y#r R#r',
		'G1 X#a-#r',
		'G2 Y-#r R#r',
		'G1 X-#a+#r',
		'G2 X-#a Y0 R#r',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'rectr' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, $VC$-$VT$*0.5}',
		#
		'G0 X-#a',
		'G1 Z$VZ$',
		'G1 Y#b-#r',
		'G2 X-#a+#r Y#b R#r',
		'G1 X#a-#r',
		'G2 X#a Y#b-#r R#r',
		'G1 Y-#b+#r',
		'G2 X#a-#r Y-#b R#r',
		'G1 X-#a+#r',
		'G2 X-#a Y-#b+#r R#r',
		'G1 Y0',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'ellipse' : [
		'LET #x : LREAL := {$VA$+$VB$}*0.5',
		'LET #y : LREAL := {$VA$-$VB$}*0.5',
		'LET #a : LREAL := MAX{0.001, #x*#x}',
		'LET #b : LREAL := MAX{0.001, #y*#y}',
		'LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}',
		'LET #c : LREAL := PI*#x*{1+{3*#b/#k}}',
		'LET #r : LREAL := MAX{0.001, {#c*0.5/PI}-{$VT$*0.5}}',
		'LET #w : LREAL := MAX{0.001, $VA$-$VT$}',
		'LET #h : LREAL := MAX{0.001, $VB$-$VT$}',
		'G36 O$VSX$ D{0.5*#w/#r}',
		'G36 O$VSY$ D{0.5*#h/#r}',
		#
		'G0 X-#r',
		'G1 Z$VZ$',
		'G2 X#r R#r',
		'G2 X-#r R#r',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'locka' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #rc : LREAL := MAX{0.001, {$VC$-$VT$}*0.5}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$',
		'G2 X#a-#r Y-#r R#r',
		'G1 X-#a+#r',
		'G2 Y#r R#r',
		'G1 X#a-#r',
		'G2 X#a Y0 R#r',
		# circle
		'G2 X#a-#rc*2 Y0 R#rc',
		'G2 X#a R#rc',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'lockaf' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #rc : LREAL := MAX{0.001, {$VC$-$VT$}*0.5}',
		# capsule
		'G0 X-#a',
		'G1 Z$VZ$',
		'G2 X-#a+#r Y#r R#r',
		'G1 X#a-#r',
		'G2 Y-#r R#r',
		'G1 X-#a+#r',
		'G2 X-#a Y0 R#r',
		# circle
		'G2 X-#a+#rc*2 Y0 R#rc',
		'G2 X-#a R#rc',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'lockb' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}',
		'LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$',
		'G2 X#a-#r Y-#r R#r',
		'G1 X-#a+#r',
		'G2 Y#r R#r',
		'G1 X#a-#r',
		'G2 X#a Y0 R#r',
		#
		'G1 X#w Y0',
		'G1 Y-#h',
		'G1 X-#w',
		'G1 Y0',
		'G1 X#w',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'lockbf' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}',
		'LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}',
		# capsule
		'G0 X-#a',
		'G1 Z$VZ$',
		'G2 X-#a+#r Y#r R#r',
		'G1 X#a-#r',
		'G2 Y-#r R#r',
		'G1 X-#a+#r',
		'G2 X-#a Y0 R#r',
		#
		'G1 X-#w Y0',
		'G1 Y#h',
		'G1 X#w',
		'G1 Y0',
		'G1 X-#w',
		#
		'G1 X0 Y0',
		'G0 Z0',
	]
}

for k, v in shape.items():
	for i, j in enumerate(v):
		if j[:3] == 'LET':
			v[i] = '%s\n' % (j)
		else:
			v[i] = 'N%d %s\n' % (i, j)
	v[-1] = v[-1][:-1]
	with open("%s.cnc" % (k), "w") as f:
		f.writelines(v)