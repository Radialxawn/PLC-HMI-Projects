LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
N2 G0 X-#a
N3 G1 Z$VZ$
N4 G2 X-#a+#r Y#r R#r
N5 G1 X#a-#r
N6 G2 Y-#r R#r
N7 G1 X-#a+#r
N8 G2 X-#a Y0 R#r
N9 G0 Z0
N10 G0 X0 Y0