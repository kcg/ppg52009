#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize


filename = "graetzel_P 29-10-09.txt"
colsep = "\t"


# Die Modellfunktion
def fitfunc(p, xx):
	# U² * (R+R1) / (R+R1 + R2)²
	return [p[0]**2 * (x+p[2]) / (x+p[2]+p[1])**2 for x in xx]

# Abstandsfunktion zwischen Modell und Daten
# Muss nur modifiziert werden, wenn unterschiedliche Einzelfehler vorliegen
def errfunc(p, x, y):
	yw = fitfunc(p,x)
	return [yw[i] - y[i] for i in range(len(x))]

ifile = open(filename, "r")
data = []
for linetext in ifile.readlines():
	if linetext[0] == "#":
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
	data.append(row)

# Werte Spaltenweise
R1 = [i[0] for i in data]
U = [i[1] for i in data]
I = [i[2] for i in data]
P = [i[3] for i in data]
R2 = [i[4] for i in data]

U_error = 0.2
I_error = 0.1
P_error = [P[i] * sqrt((U_error/U[i])**2 + (I_error/I[i])**2) for i in range(len(R1))]

# Anfangswert für Parameter
p0 = [150., 19., 6.]

# Fit durchführen
p1, success = optimize.leastsq(errfunc, p0[:], args=(R1, P))
print p1

xarray = pylab.linspace(R1[0]-2., R1[-1]+2., 100)

pylab.plot(xarray, fitfunc(p1, xarray), "b-")
pylab.errorbar(R1, P, P_error, None, "ro")
pylab.xlim(R1[0] -2.5, R1[-1]+2.5)
pylab.ylim(0., 350.)

#pylab.title(u"ein Plot")
pylab.xlabel(u"$R\; [\mathrm{k\Omega}]$")
pylab.ylabel(u"$P\; [\mathrm{nW}]$")

pylab.legend(('$(%.0f\,\mathrm{V})^2 \cdot \\frac{R+%.1f\,\mathrm{k\Omega}}{(R+%.1f\,\mathrm{k\Omega}+%.1f\,\mathrm{k\Omega})^2}$' % (p1[0], p1[2], p1[2], p1[1]), 'Fehler', 'Fehler', 'Messwerte'), loc=4)

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_leistung.pdf")

# Anzeigen
pylab.show()

