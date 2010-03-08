a=417.133
b=-9602.73
f(x)=a*x+b
#plot "02-02data.txt" using 1:3
plot f(x) title "Fit 417.133deg/s * t - 9602.73deg", "02-02data.txt" using 1:3 title "Messwerte"
set key box linewidth 2
set key right bottom
set xrange [24:26.8]
set yrange [300:1600]
set xlabel "Zeit t in [s]"
set ylabel "Drehwinkel in [deg]"
replot
#f(x)=a*x+b
#fit f(x) "02-02data.txt" using 1:3 via a,b
set term post enhanced solid color
set out "zeit-winkel02-cassy.ps"
replot
set term x11

#Final set of parameters            Asymptotic Standard Error
#=======================            ==========================
#
#a               = 417.133          +/- 2.622        (0.6286%)
#b               = -9602.73         +/- 66.56        (0.6931%)




