#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
from math import *
import scipy.interpolate as ip


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
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]
		line = linetext.split(colsep)
		if len(line) <= 0:
			continue
		row = []
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print i, "is not a float"
				row.append(0.)
		data.append(row)
	return(data)



# Drehwinkel in Abhängigkeit von der Poti-Spannung (I-1)
#data_winkel = readdata("...")
#w1 = [i[0] for i in data_winkel]
#U1 = [i[1] for i in data_winkel]

# erzeuge Fitfunktion für alpha(U) (II-1)



# LED-Spannung in Abhängigkeit von der Poti-Spannung (I-2)

# Lies das Spektrum der Leucht-LED (I-3)
#data_leucht = readdata("...")


# erzeuge Fitfunktion für alpha(U) (II-1)

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



