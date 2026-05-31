LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, $VC$-$VT$*0.5}
N3 G0 X-#a
N4 G1 Z$VZ$
N5 G1 Y#b-#r
N6 G2 X-#a+#r Y#b R#r
N7 G1 X#a-#r
N8 G2 X#a Y#b-#r R#r
N9 G1 Y-#b+#r
N10 G2 X#a-#r Y-#b R#r
N11 G1 X-#a+#r
N12 G2 X-#a Y-#b+#r R#r
N13 G1 Y0
N14 G0 X0 Y0