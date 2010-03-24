a=138.51
b=-2471.37
f(x)=a*x+b
set pointsize 4
plot f(x) title "Fit 139deg/s * t - 2471.4deg" linewidth 4, "zeit-winkel29-cassy.txt" using 1:3 title  "Messwerte" with dots linewidth 30
set key box linewidth 2
set key right bottom
set xrange [18.2:18.85]
set yrange [45:150]
set xlabel "Zeit t in [s]"
set ylabel "Drehwinkel in [deg]"
replot
#fit f(x) "zeit-winkel29-cassy.txt" using 1:3 via a,b
set term post enhanced solid color
set out "zeit-winkel29-cassy.ps"
replot
set term x11


#Final set of parameters            Asymptotic Standard Error
#=======================            ==========================
#
#a               = 138.51           +/- 2.904        (2.096%)
#b               = -2471.37         +/- 53.78        (2.176%)
#
# bei diagonaler Korelationsmatrix:
# a = 138.51 +/- 2.904
# b = -2471.37 +/- 0.552
