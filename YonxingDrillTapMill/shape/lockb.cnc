LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #h : LREAL := MAX{0.001, $VC$-$VB$*0.5-$VT$*0.5}
LET #w : LREAL := MAX{0.001, {$VD$-$VT$}*0.5}
N4 G0 X#a
N5 G1 Z$VZ$
N6 G2 X#a-#r Y-#r R#r
N7 G1 X-#a+#r
N8 G2 Y#r R#r
N9 G1 X#a-#r
N10 G2 X#a Y0 R#r
N11 G1 X#w Y0
N12 G1 Y-#h
N13 G1 X-#w
N14 G1 Y0
N15 G1 X0 Y0
N16 G0 Z0