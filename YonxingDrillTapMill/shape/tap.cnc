LET #rps : LREAL := $VB$/60.0
LET #f : LREAL := MIN{#rps*$VP$, $VMZ$}
LET #a : LREAL := $VA$
LET #e : LREAL := MAX{0.001, MIN{$VE$, #a}}
LET #sc : LREAL := CEIL{#a/#e}
LET #si : LREAL := #sc
LET #ai : LREAL := 0
N10 G1 Z0 F#f
N11 G36 O#ai D{MIN{{#sc-#si+1}*#e, #a}}
N12 G1 Z-#ai
N20 G37 O#si D-1
N30 G20 L10 K#si
N50 G1 Z-#a
N100 G1 Z0