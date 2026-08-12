LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #w : LREAL := #a*2
LET #e : LREAL := MAX{0.001, MIN{$VE$, #w}}
LET #sc : LREAL := FLOOR{#w/#e}
LET #si : LREAL := #sc+1
LET #ai : LREAL := 0
LET #bi : LREAL := -#b
N0 G36 O$VSY$ D{1-$VMODE$*2}
N1 G0 X-#a
N2 G0 Y-#b
N3 G1 Z$VZ$ F$VFV$
N10 G36 O#ai D{-#a+{#sc-#si+1}*#e}
N11 G36 O#bi D{-#bi}
N12 G1 X#ai Y#bi F$VFH$
N13 G1 X#ai Y-#bi
N20 G37 O#si D-1
N30 G20 L10 K#si
N50 G36 O#ai D{#a}
N51 G36 O#bi D{-#bi}
N52 G1 X#ai Y#bi F$VFH$
N53 G1 X#ai Y-#bi
N100 G0 Z0
N110 G0 Y0
N120 G0 X0