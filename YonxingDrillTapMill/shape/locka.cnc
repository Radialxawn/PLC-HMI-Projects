LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #r : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #rc : LREAL := MAX{0.001, {$VC$-$VT$}*0.5}
N3 G36 O$VSY$ D{1-$VMODE$*2}
N4 G0 X#a
N5 G1 Z$VZ$ F$VFV$
N6 G2 X#a-#r Y-#r R#r F$VFH$
N7 G1 X-#a+#r
N8 G2 Y#r R#r
N9 G1 X#a-#r
N10 G2 X#a Y0 R#r
N11 G2 X#a-#rc*2 Y0 R#rc
N12 G2 X#a R#rc
N13 G1 X0 Y0
N14 G0 Z0