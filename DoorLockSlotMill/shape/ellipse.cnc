LET #x : LREAL := {$VA$+$VB$}*0.5
LET #y : LREAL := {$VA$-$VB$}*0.5
LET #a : LREAL := #x*#x
LET #b : LREAL := #y*#y
LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}
LET #c : LREAL := PI*#x*{1+{3*#b/#k}}
LET #r : LREAL := #c*0.5/PI

N0 F60
N1 G0 X0 Y0 Z0
N2 G1 Z$VZ$
N3 G36 O$VI$ D{0.5*$VA$/#r}
N4 G36 O$VJ$ D{0.5*$VB$/#r}

N10 G42 D$VT$*0.5
N11 G1 X-#r
N12 G2 X#r R#r
N13 G2 X-#r R#r
N14 G2 X0 Y#r R#r
N19 G40

N30 G1 X0 Y0
N31 G1 Z0