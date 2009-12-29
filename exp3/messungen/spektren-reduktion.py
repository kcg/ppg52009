#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
from math import *
import scipy.interpolate as ip
from scipy import optimize


'''
Hier ist noch viel zu tun.
Wer an einem Programmteil Lust hat, kann gerne daran schreiben!
'''


'''
Reduktion der LED-Absorptionsspektren


liest ein:
-Drehwinkel in Abhängigkeit von der Poti-Spannung (I-1)
-LED-Spannung in Abhängigkeit von der Poti-Spannung (I-2)
-Das Spektrum der Leucht-LED (vom Spektrometer der Optiker) (I-3)


Umrechnungen:
-erzeugt Fitfunktion für alpha(U) (II-1)
-mapt die Intensitätskurven auf Winkel -> I(alpha) (II-2)

-bestimmt aus dem Peak Nullter Ordnung den Gitterwinkel (II-3)
und die Faltungsfunktion (II-4)
-Entfaltet die Intensitätskurven (II-5)

-berechnet lambda(alpha) mit dem Gitterwinkel (II-6)
-mapt die Intensitätskurven von alpha nach lambda (II-7)
-skaliert die Intensitätskurven nach dem Transformationssatz (II-8)
-skaliert die Intensitätskurven mit dem Spektrum der Leucht-LED (II-9)


Ausgabe:
-fertige LED-Absorptionsspektren I(lambda) (III-1)
'''


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []; l = 0
	for linetext in ifile.readlines():
		l += 1
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]#.strip()
		line = linetext.split(colsep)
		if len(line) <= 0:
			continue
		row = []
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print 'File "' + filename + '",',
				print 'line ' + str(l) + ':',
				print '"' + i + '" is not a float'
				row.append(0.)
		data.append(row)
	return(data)



# Fitfunktion für die Winkelabhängigkeit der Potispannung
''' Hyperbel passt sogar noch besser:
def winkel_f(p, x):
	return p[0] + p[1] * x + p[2] * (sqrt(1. + ((x - p[4]) / p[3])**2) - 1.)
Startwerte: [-.5,.003,.02,40.,50.]
'''
def U_von_winkel(p, x):
	return p[0] + exp(p[1] * x)
def winkel_func(p, xlist, ylist):
	y = [U_von_winkel(p, x) for x in xlist]
	return [y[i] - ylist[i] for i in range(len(xlist))]


# Drehwinkel in Abhängigkeit von der Poti-Spannung (I-1) <-- Ich (Karl) probiers mal (I-1 bis II-2)
data_winkel = readdata("winkel_data.txt")
w1 = [(-i[0]+312) for i in data_winkel]
U1 = [i[1] for i in data_winkel]

# Winkelfunktion fitten
par1, success = optimize.leastsq(winkel_func, [1.,1.], args=(w1, U1))


interval = sc.linspace(-20,120,100)
pl.plot(interval, [U_von_winkel(par1, a) for a in interval] , "k-", label="Fit: $%.4f + \\mathrm{exp}(%.4f\, \cdot \\alpha)$" % tuple(par1))
pl.plot(w1, U1, "bo", label="Messung")

# Speichern und zeichnen
pl.xlabel('Winkel $ \\alpha $ in [deg]')
pl.ylabel('Spannung $U$ in [mV]')
pl.legend(loc='upper left')
pl.gcf().set_size_inches(6, 4)
pl.savefig("winkel_spannung.pdf")
pl.show()





# LED-Spannung in Abhängigkeit von der Poti-Spannung (I-2)

# Lies das Spektrum der Leucht-LED (I-3)
#data_leucht = readdata("...")


# erzeuge Fitfunktion für alpha(U) (II-1)
def winkel_von_U(U):
	return optimize.fsolve(lambda a: U_von_winkel(par1, a) - U, 0.)

# Intensitätskurven von Spannung auf Winkel mappen -> I(alpha) (II-2)

# bestimme aus dem Peak Nullter Ordnung den Gitterwinkel (II-3)

# bestimme die Faltungsfunktion (II-4)

# entfalte die Intensitätskurven (II-5)

# berechne lambda(alpha) mit dem Gitterwinkel (II-6)
'''
So kompliziert ist das Gitter auch wieder nicht:
Sei phi der Winkel, den das Gitter aus der Normalposition geschwenkt ist.
Sei alpha der Winkel, um den der Strahl am Gitter gebeugt wird.
d = 1mm/2400

Anstatt
lambda / d = sin(alpha)
gibts dann:
lambda / d = sin(phi) - sin(alpha+phi)

z.B. phi = 66°, alpha = 140°
=> lambda = d * (sin(phi) - sin(alpha+phi)) = 563nm
'''


# Intensitätskurven von alpha nach lambda mappen (II-7)

# Intensitätskurven nach dem Transformationssatz skalieren (II-8)

# Intensitätskurven mit dem Spektrum der Leucht-LED skalieren (II-9)

# fertige LED-Absorptionsspektren I(lambda) ausgeben (III-1)



