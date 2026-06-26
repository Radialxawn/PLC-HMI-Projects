shape = {
	'drill': [
		'LET #f : LREAL := $VB$/60.0'
		'N0 F#f',
		'N1 G1 Z-$VA$',
		'N2 G0 Z0',
	],
	'tap': [
		'LET #f : LREAL := $VB$/60.0'
		'N0 F#f',
		'N1 G1 Z-$VA$',
		'N2 G1 Z0',
	],
	'circle' : [
		'LET #x : LREAL := {$VA$+$VB$}*0.5',
		'LET #y : LREAL := {$VA$-$VB$}*0.5',
		'LET #a : LREAL := MAX{0.001, #x*#x}',
		'LET #b : LREAL := MAX{0.001, #y*#y}',
		'LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}',
		'LET #c : LREAL := PI*#x*{1+{3*#b/#k}}',
		'LET #r : LREAL := MAX{0.001, {#c*0.5/PI}-{$VT$*0.5}}',
		'LET #w : LREAL := MAX{0.001, $VA$-$VT$}',
		'LET #h : LREAL := MAX{0.001, $VB$-$VT$}',
		'G36 O$VI$ D{0.5*#w/#r}',
		'G36 O$VJ$ D{0.5*#h/#r}',
		#
		'G0 X-#r',
		'G1 Z$VZ$',
		'G2 I#r',
		#
		'G1 X0 Y0',
		'G0 Z0',
	],
	'circles' : [
		'LET #x : LREAL := {$VA$+$VB$}*0.5',
		'LET #y : LREAL := {$VA$-$VB$}*0.5',
		'LET #a : LREAL := MAX{0.001, #x*#x}',
		'LET #b : LREAL := MAX{0.001, #y*#y}',
		'LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}',
		'LET #c : LREAL := PI*#x*{1+{3*#b/#k}}',
		'LET #r : LREAL := MAX{0.001, {#c*0.5/PI}-{$VT$*0.5}}',
		'LET #w : LREAL := MAX{0.001, $VA$-$VT$}',
		'LET #h : LREAL := MAX{0.001, $VB$-$VT$}',
		'LET #whh : LREAL := MAX{#w, #h}*0.5',
		'LET #sc : LREAL := FLOOR{#whh/MAX{0.001, MIN{$VE$, #whh}}}',
		'LET #si : LREAL := #sc+1',
		'N0 G36 O$VI$ D{0.5*#w/#r}',
		'N1 G36 O$VJ$ D{0.5*#h/#r}',
		'N2 G1 Z$VZ$',
		#
		'N10 G1 X{{#si-1-#sc}*$VE$*#r/#whh}',
		'N20 G2 I{{#sc-#si+1}*$VE$*#r/#whh}',
		'N30 G37 O#si D-1',
		'N40 G20 L10 K#si',
		#
		'N100 G1 X-#r',
		'N110 G2 I#r',
		#
		'N200 G1 X0 Y0',
		'N210 G0 Z0',
	],
	'rect' : [
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
	'rects' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.0001, $VC$-$VT$*0.5}',
		'LET #abh : LREAL := MAX{#a, #b}',
		'LET #sc : LREAL := FLOOR{#abh/MAX{0.001, MIN{$VE$, #abh}}}',
		'LET #si : LREAL := #sc+1',
		'LET #ai : LREAL := 0.0',
		'LET #bi : LREAL := 0.0',
		'LET #ri : LREAL := 0.0',
		#
		'N0 G1 Z$VZ$',
		#
		'N10 G36 O#ai D{{#sc-#si+1}*$VE$*#a/#abh}',
		'N20 G36 O#bi D{{#sc-#si+1}*$VE$*#b/#abh}',
		'N30 G36 O#ri D{MAX{0.0001, #r*#ai/#a}}',
		'N100 G1 X-#ai',
		'N110 G1 Y#bi-#ri',
		'N120 G2 X-#ai+#ri Y#bi R#ri',
		'N130 G1 X#ai-#ri',
		'N140 G2 X#ai Y#bi-#ri R#ri',
		'N150 G1 Y-#bi+#ri',
		'N160 G2 X#ai-#ri Y-#bi R#ri',
		'N170 G1 X-#ai+#ri',
		'N180 G2 X-#ai Y-#bi+#ri R#ri',
		'N190 G1 Y0',
		#
		'N200 G37 O#si D-1',
		'N210 G20 L10 K#si',
		#
		'N300 G1 X-#a',
		'N310 G1 Y#b-#r',
		'N320 G2 X-#a+#r Y#b R#r',
		'N330 G1 X#a-#r',
		'N340 G2 X#a Y#b-#r R#r',
		'N350 G1 Y-#b+#r',
		'N360 G2 X#a-#r Y-#b R#r',
		'N370 G1 X-#a+#r',
		'N380 G2 X-#a Y-#b+#r R#r',
		'N390 G1 Y0',
		#
		'N500 G1 X0 Y0',
		'N510 G0 Z0',
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
		#
		'G1 X0 Y0',
		'G0 Z0',
	]
}

for k, v in shape.items():
	for i, j in enumerate(v):
		if j[0] == 'N' or j[:3] == 'LET':
			v[i] = '%s\n' % (j)
		else:
			v[i] = 'N%d %s\n' % (i, j)
	v[-1] = v[-1][:-1]
	with open("%s.cnc" % (k), "w") as f:
		f.writelines(v)