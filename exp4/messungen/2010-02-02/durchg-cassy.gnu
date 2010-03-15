plot "02-02data.txt" using 1:2 with boxes
unset key
set xrange [22.8:29]
set yrange [0:265]
set xlabel "Zeit t in [s]"
set ylabel "Summe N der Durchgaenge"
replot
set term post enhanced solid color
set out "durchg02-cassy.ps"
replot
set term x11

