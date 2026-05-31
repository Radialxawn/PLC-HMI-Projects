LET #r : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
N1 G0 X-#r
N2 G1 Z$VZ$
N3 G2 X#r R#r
N4 G2 X-#r R#r
N5 G0 X0 Y0