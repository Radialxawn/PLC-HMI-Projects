LET #a : LREAL := MAX{0.001, {$VA$-$VT$}*0.5}
LET #b : LREAL := MAX{0.001, {$VB$-$VT$}*0.5}
LET #r : LREAL := MAX{0.0001, $VC$-$VT$*0.5}
LET #abh : LREAL := MAX{#a, #b}
LET #sc : LREAL := FLOOR{#abh/MAX{0.001, MIN{$VE$, #abh}}}
LET #si : LREAL := #sc+1
LET #ai : LREAL := 0.0
LET #bi : LREAL := 0.0
LET #ri : LREAL := 0.0
N0 G36 O$VSX$ D{1-$VMODE$*2}
N1 G1 Z$VZ$ F$VFV$
N10 G36 O#ai D{{#sc-#si+1}*$VE$*#a/#abh}
N20 G36 O#bi D{{#sc-#si+1}*$VE$*#b/#abh}
N30 G36 O#ri D{MAX{0.0001, #r*#ai/#a}}
N100 G1 X-#ai F$VFH$
N110 G1 Y#bi-#ri
N120 G2 X-#ai+#ri Y#bi R#ri
N130 G1 X#ai-#ri
N140 G2 X#ai Y#bi-#ri R#ri
N150 G1 Y-#bi+#ri
N160 G2 X#ai-#ri Y-#bi R#ri
N170 G1 X-#ai+#ri
N180 G2 X-#ai Y-#bi+#ri R#ri
N190 G1 Y0
N200 G37 O#si D-1
N210 G20 L10 K#si
N300 G1 X-#a
N310 G1 Y#b-#r
N320 G2 X-#a+#r Y#b R#r
N330 G1 X#a-#r
N340 G2 X#a Y#b-#r R#r
N350 G1 Y-#b+#r
N360 G2 X#a-#r Y-#b R#r
N370 G1 X-#a+#r
N380 G2 X-#a Y-#b+#r R#r
N390 G1 Y0
N500 G1 X0 Y0
N510 G0 Z0