LET #x : LREAL := {$VA$+$VB$}*0.5
LET #y : LREAL := {$VA$-$VB$}*0.5
LET #a : LREAL := MAX{0.001, #x*#x}
LET #b : LREAL := MAX{0.001, #y*#y}
LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}
LET #c : LREAL := PI*#x*{1+{3*#b/#k}}
LET #r : LREAL := MAX{0.001, {#c*0.5/PI}-{$VT$*0.5}}
LET #w : LREAL := MAX{0.001, $VA$-$VT$}
LET #h : LREAL := MAX{0.001, $VB$-$VT$}
N9 G36 O$VI$ D{0.5*#w/#r}
N10 G36 O$VJ$ D{0.5*#h/#r}
N11 G0 X-#r
N12 G1 Z$VZ$
N13 G2 X#r R#r
N14 G2 X-#r R#r
N15 G0 X0 Y0