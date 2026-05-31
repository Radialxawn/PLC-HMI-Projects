LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #rc : LREAL := MAX{0.001, {$VC$-$VT$}*0.5}
N3 G0 X-#a
N4 G1 Z$VZ$
N5 G2 X-#a+#r Y#r R#r
N6 G1 X#a-#r
N7 G2 Y-#r R#r
N8 G1 X-#a+#r
N9 G2 X-#a Y0 R#r
N10 G1 X#a-#rc*2 Y0
N11 G2 X#a R#rc
N12 G2 X#a-#rc*2 R#rc
N13 G0 X0 Y0
N14 G0 Z0