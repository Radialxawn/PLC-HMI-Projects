LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}
LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}
N4 G36 O$VSX$ D{1-$VMODE$*2}
N5 G0 X#a
N6 G1 Z$VZ$ F$VFV$
N7 G2 X#a-#r Y-#r R#r F$VFH$
N8 G1 X-#a+#r
N9 G2 Y#r R#r
N10 G1 X#a-#r
N11 G2 X#a Y0 R#r
N12 G1 X#w Y0
N13 G1 Y-#h
N14 G1 X-#w
N15 G1 Y0
N16 G1 X#w
N17 G1 X0 Y0
N18 G0 Z0