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
	# U² * R / (R + R2)²
	return [p[0]**2 * x / (x + p[1])**2 for x in xx]


# Abstandsfunktion zwischen Modell und Daten
# Muss nur modifiziert werden, wenn unterschiedliche Einzelfehler vorliegen
def errfunc(p, x, y, delta_y):
	yw = fitfunc(p,x)
	return [(yw[i] - y[i]) / delta_y[i] for i in range(len(x))]

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


# zusätzlicher Widerstand des Amperemeters
R_amp = 5.22
# Werte Spaltenweise
R1 = [i[0] + R_amp for i in data]
U = [i[1] for i in data]
I = [i[2] for i in data]
P = [i[1] * i[2] for i in data]

U_error = 0.2
I_error = 0.1
# Fehlerfortpflanzung
P_error = [P[i] * sqrt((U_error/U[i])**2 + (I_error/I[i])**2) for i in range(len(R1))]

# Anfangswert für Parameter
p0 = [150., 19.]

# Fit durchführen
p1, success = optimize.leastsq(errfunc, p0[:], args=(R1, P, P_error))
print p1

print "fitfunc([0,1,2,3]) =", fitfunc(p1, [0,1,2,3])

xarray = pylab.linspace(R1[0]-2., R1[-1]+2., 100)

pylab.plot(xarray, fitfunc(p1, xarray), "k-", label='$(%.0f\,\mathrm{mV})^2 \cdot \\frac{R}{(R+%.0f\,\mathrm{k\Omega})^2}$' % (p1[0], p1[1]))
pylab.errorbar(R1, P, P_error, None, "bo", label="Messwerte")
pylab.xlim(0., R1[-1]+3.)
pylab.ylim(0., 330.)

pylab.xlabel(u"$R\; [\mathrm{k\Omega}]$")
pylab.ylabel(u"$P\; [\mathrm{nW}]$")

pylab.legend(loc='lower right')

x_max = p1[1]
y_max = p1[0]**2 / (4. * p1[1])
pylab.annotate('%.0f nW' % (y_max,), xy=(x_max, y_max+18),  xycoords='data', horizontalalignment='center', verticalalignment='bottom')


# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_leistung.pdf")

# Anzeigen
pylab.show()

