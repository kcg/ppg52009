plot "28-01data.txt" using 1:2 with boxes
unset key
set xrange [12.7:22]
set yrange [0:245]
set xlabel "Zeit t in [s]"
set ylabel "Summe N der Durchgaenge"
replot
set term post enhanced solid color
set out "durchg28-cassy.ps"
replot
set term x11

