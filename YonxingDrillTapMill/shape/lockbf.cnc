LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}
LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}
N4 G36 O$VSX$ D{$VMODE$*2-1}
N5 G36 O$VSY$ D{-1}
N6 G0 X#a
N7 G1 Z$VZ$ F$VFV$
N8 G2 X#a-#r Y-#r R#r F$VFH$
N9 G1 X-#a+#r
N10 G2 Y#r R#r
N11 G1 X#a-#r
N12 G2 X#a Y0 R#r
N13 G1 X#w Y0
N14 G1 Y-#h
N15 G1 X-#w
N16 G1 Y0
N17 G1 X#w
N18 G1 X0 Y0
N19 G0 Z0