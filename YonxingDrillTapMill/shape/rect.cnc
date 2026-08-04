LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, $VC$-$VT$*0.5}
N3 G36 O$VSX$ D{1-$VMODE$*2}
N4 G0 X-#a
N5 G1 Z$VZ$
N6 G1 Y#b-#r
N7 G2 X-#a+#r Y#b R#r
N8 G1 X#a-#r
N9 G2 X#a Y#b-#r R#r
N10 G1 Y-#b+#r
N11 G2 X#a-#r Y-#b R#r
N12 G1 X-#a+#r
N13 G2 X-#a Y-#b+#r R#r
N14 G1 Y0
N15 G1 X0 Y0
N16 G0 Z0