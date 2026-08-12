LET #x : LREAL := {$VA$+$VB$}*0.5
LET #y : LREAL := {$VA$-$VB$}*0.5
LET #a : LREAL := MAX{0.001, #x*#x}
LET #b : LREAL := MAX{0.001, #y*#y}
LET #k : LREAL := #a*{SQRT{4-{3*#b/#a}}+10}
LET #c : LREAL := PI*#x*{1+{3*#b/#k}}
LET #r : LREAL := MAX{0.001, {#c*0.5/PI}-{$VT$*0.5}}
LET #w : LREAL := MAX{0.001, $VA$-$VT$}
LET #h : LREAL := MAX{0.001, $VB$-$VT$}
LET #whh : LREAL := MAX{#w, #h}*0.5
LET #sc : LREAL := FLOOR{#whh/MAX{0.001, MIN{$VE$, #whh}}}
LET #si : LREAL := #sc+1
N0 G36 O$VSX$ D{0.5*#w*{1-$VMODE$*2}/#r}
N1 G36 O$VSY$ D{0.5*#h/#r}
N2 G1 Z$VZ$ F$VFV$
N10 G1 X{{#si-1-#sc}*$VE$*#r/#whh} F$VFH$
N20 G2 I{{#sc-#si+1}*$VE$*#r/#whh}
N30 G37 O#si D-1
N40 G20 L10 K#si
N100 G1 X-#r
N110 G2 I#r
N200 G1 X0 Y0
N210 G0 Z0