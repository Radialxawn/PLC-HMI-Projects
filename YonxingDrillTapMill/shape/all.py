shape = {
	'facex' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #b : LREAL := MAX{0, {$VB$-$VT$}*0.5}',
		'LET #w : LREAL := #b*2',
		'LET #e : LREAL := MAX{0.001, MIN{$VE$, #w}}',
		'LET #sc : LREAL := FLOOR{#w/#e}',
		'LET #si : LREAL := #sc+1',
		'LET #ai : LREAL := -#a',
		'LET #bi : LREAL := 0',
		#
		'N0 G36 O$VSX$ D{1-$VMODE$*2}',
		'N1 G0 X-#a',
		'N2 G0 Y-#b',
		'N3 G1 Z$VZ$ F$VFV$',
		#
		'N10 G36 O#ai D{-#ai}',
		'N11 G36 O#bi D{-#b+{#sc-#si+1}*#e}',
		'N12 G1 X-#ai Y#bi F$VFH$',
		'N13 G1 X#ai Y#bi',
		#
		'N20 G37 O#si D-1',
		'N30 G20 L10 K#si',
		#
		'N50 G36 O#ai D{-#ai}',
		'N51 G36 O#bi D{#b}',
		'N52 G1 X-#ai Y#bi F$VFH$',
		'N53 G1 X#ai Y#bi',
		#
		'N100 G0 Z0',
		'N110 G0 Y0',
		'N120 G0 X0',
	],
	'facey' : [
		'LET #a : LREAL := MAX{0, {$VA$-$VT$}*0.5}',
		'LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #w : LREAL := #a*2',
		'LET #e : LREAL := MAX{0.001, MIN{$VE$, #w}}',
		'LET #sc : LREAL := FLOOR{#w/#e}',
		'LET #si : LREAL := #sc+1',
		'LET #ai : LREAL := 0',
		'LET #bi : LREAL := #b',
		#
		'N0 G36 O$VSY$ D{1-$VMODE$*2}',
		'N1 G0 X-#a',
		'N2 G0 Y-#b',
		'N3 G1 Z$VZ$ F$VFV$',
		#
		'N10 G36 O#ai D{-#a+{#sc-#si+1}*#e}',
		'N11 G36 O#bi D{-#bi}',
		'N12 G1 X#ai Y#bi F$VFH$',
		'N13 G1 X#ai Y-#bi',
		#
		'N20 G37 O#si D-1',
		'N30 G20 L10 K#si',
		#
		'N50 G36 O#ai D{#a}',
		'N51 G36 O#bi D{-#bi}',
		'N52 G1 X#ai Y#bi F$VFH$',
		'N53 G1 X#ai Y-#bi',
		#
		'N100 G0 Z0',
		'N110 G0 Y0',
		'N120 G0 X0',
	],
	'drill': [
		'LET #f : LREAL := $VB$/60.0',
		'LET #a : LREAL := $VA$',
		'LET #e : LREAL := MAX{0.001, MIN{$VE$, #a}}',
		'LET #sc : LREAL := CEIL{#a/#e}',
		'LET #si : LREAL := #sc',
		'LET #ai : LREAL := 0',
		#
		'N10 G0 Z$VC$',
		'N11 G0 Z{$VC$-#ai}',
		'N12 G36 O#ai D{MIN{{#sc-#si+1}*#e, #a}}',
		'N13 G1 Z-#ai F#f',
		#
		'N20 G37 O#si D-1',
		'N30 G20 L10 K#si',
		#
		'N50 G1 Z-#a',
		#
		'N100 G0 Z0',
	],
	'tap': [
		'LET #rps : LREAL := $VB$/60.0',
		'LET #f : LREAL := MIN{#rps*$VP$, $VMZ$}',
		'LET #a : LREAL := $VA$',
		'LET #e : LREAL := MAX{0.001, MIN{$VE$, #a}}',
		'LET #sc : LREAL := CEIL{#a/#e}',
		'LET #si : LREAL := #sc',
		'LET #ai : LREAL := 0',
		#
		'N10 G1 Z0 F#f',
		'N11 G36 O#ai D{MIN{{#sc-#si+1}*#e, #a}}',
		'N12 G1 Z-#ai',
		#
		'N20 G37 O#si D-1',
		'N30 G20 L10 K#si',
		#
		'N50 G1 Z-#a',
		#
		'N100 G1 Z0',
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
		#
		'G36 O$VSX$ D{0.5*#w*{1-$VMODE$*2}/#r}',
		'G36 O$VSY$ D{0.5*#h/#r}',
		#
		'G0 X-#r',
		'G1 Z$VZ$ F$VFV$',
		'G2 I#r F$VFH$',
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
		#
		'N0 G36 O$VSX$ D{0.5*#w*{1-$VMODE$*2}/#r}',
		'N1 G36 O$VSY$ D{0.5*#h/#r}',
		'N2 G1 Z$VZ$ F$VFV$',
		#
		'N10 G1 X{{#si-1-#sc}*$VE$*#r/#whh} F$VFH$',
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
		'G36 O$VSX$ D{1-$VMODE$*2}',
		#
		'G0 X-#a',
		'G1 Z$VZ$ F$VFV$',
		'G1 Y#b-#r F$VFH$',
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
		'N0 G36 O$VSX$ D{1-$VMODE$*2}',
		'N1 G1 Z$VZ$ F$VFV$',
		#
		'N10 G36 O#ai D{{#sc-#si+1}*$VE$*#a/#abh}',
		'N20 G36 O#bi D{{#sc-#si+1}*$VE$*#b/#abh}',
		'N30 G36 O#ri D{MAX{0.0001, #r*#ai/#a}}',
		'N100 G1 X-#ai F$VFH$',
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
		#
		'G36 O$VSY$ D{1-$VMODE$*2}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$ F$VFV$',
		'G2 X#a-#r Y-#r R#r F$VFH$',
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
		#
		'G36 O$VSX$ D{-1}',
		'G36 O$VSY$ D{$VMODE$*2-1}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$ F$VFV$',
		'G2 X#a-#r Y-#r R#r F$VFH$',
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
	'lockb' : [
		'LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}',
		'LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}',
		'LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}',
		'LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}',
		#
		'G36 O$VSX$ D{1-$VMODE$*2}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$ F$VFV$',
		'G2 X#a-#r Y-#r R#r F$VFH$',
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
		#
		'G36 O$VSX$ D{$VMODE$*2-1}',
		'G36 O$VSY$ D{-1}',
		# capsule
		'G0 X#a',
		'G1 Z$VZ$ F$VFV$',
		'G2 X#a-#r Y-#r R#r F$VFH$',
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