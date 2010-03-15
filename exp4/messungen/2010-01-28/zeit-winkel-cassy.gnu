a=256.396
b=-3300
f(x)=a*x+b
#plot "28-01data.txt" using 1:3
set pointsize 4
plot f(x) title "Fit 256.396deg/s * t - 3300deg" linewidth 4, "28-01data.txt" using 1:3 title "Messwerte" with dots linewidth 12
set key box linewidth 2
set key right bottom
set xrange [13.5:17.5]
set yrange [50:1250]
set xlabel "Zeit t in [s]"
set ylabel "Drehwinkel in [deg]"
replot
#f(x)=a*x+b
#fit f(x) "28-01data.txt" using 1:3 via a,b
set term post enhanced solid color
set out "zeit-winkel28-cassy.ps"
replot
set term x11

#Final set of parameters            Asymptotic Standard Error
#=======================            ==========================
#
#a               = 256.396          +/- 0.9872       (0.385%)
#b               = -3300            +/- 15.35        (0.465%)



