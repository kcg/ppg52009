#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize



# Die Modellfunktion
def fitfunc(p, xx):
	# a*x² + b*x + c
	return [p[0] * x**2 + p[1] * x + p[2] for x in xx]

# Abstandsfunktion zwischen Modell und Daten
# Muss nur modifiziert werden, wenn unterschiedliche Einzelfehler vorliegen
def errfunc(p, x, y):
	yw = fitfunc(p,x)
	return [yw[i] - y[i] for i in range(len(x))]


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


data = readdata("dateiname.txt")

# x-Werte in der ersten Spalte
x = [i[0] for i in data]
y = [i[1] for i in data]
print "x =", x
print "y =", y

# Anfangswert für Parameter
p0 = [1., 1., 1.]

# Fit durchführen
p1, success = optimize.leastsq(errfunc, p0[:], args=(x, y))
print p1

xarray = pylab.linspace(x[0], x[-1], 100)

#pylab.errorbar(x, y, [1.] * len(x), None, "ro")
pylab.plot(x, y, "ro", xarray, fitfunc(p1, xarray), "b-")
#pylab.xlim(0., 1.)
#pylab.ylim(0., 1.)

#pylab.title(u"ein Plot")
pylab.xlabel(u"x-Werte [s]")
pylab.ylabel(u"y-Werte [m]")

pylab.legend(('Messung', '$%.2f\cdot x^2 + %.2f\cdot x + %.2f$' % (p1[0], p1[1], p1[2])), loc=1)

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("bild.pdf")

# Anzeigen
pylab.show()

