#! /usr/bin/env python
# -*- coding: utf8 -*-

# Ermittung der des Generatorstromes in Abhängigkeit vom Magnetfeld

import pylab
import scipy
from math import *
from scipy import optimize

# Die Modellfunktion
def fitfunc(p, xx):
	return [p[0] + p[1] * x for x in xx]
# Abstandsfunktion zwischen Modell und Daten
def errfunc(p, x, y):
	yw = fitfunc(p,x)
	return [yw[i] - y[i] for i in range(len(x))]


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1].strip()
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


# Daten einlesen
data = readdata("11-25_strommessung.txt")
t = [i[0] for i in data]
I = [i[1] for i in data]
IS = [i[2] for i in data]
B = [i[3] for i in data]

# Vorbereitung fuer Plots
pylab.rcParams['figure.subplot.bottom'] = 0.12
pylab.rcParams['figure.subplot.top'] = 0.96

# Nullstrom Fitten
t_f = []; I_f = []
intervall = [430, 705]
for i in range(intervall[0], intervall[1]):
	if B[i] == 0.:
		t_f.append(t[i])
		I_f.append(I[i])
p1, success = optimize.leastsq(errfunc, [1.,1.], args=(t_f, I_f))

# Rohdaten plotten
ax = pylab.figure().add_subplot(111)
ax.plot(t[intervall[0]-20:intervall[1]+20], I[intervall[0]-20:intervall[1]+20], "bo", label=u"Strom [mA]")
ax.plot(intervall, fitfunc(p1, intervall), "r-", label=u"$I_0$ Fit")
ax.plot(t[intervall[0]-20:intervall[1]+20], [b / 50. for b in B[intervall[0]-20:intervall[1]+20]], "go", label=u"B [50$\,$mT]")
pylab.xlabel(u"$t\, [\mathrm{s}]$")
pylab.ylim(0., 7.)
pylab.legend(loc='upper left', numpoints=1)
# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("messkurve_strom.pdf")
pylab.clf()

# Die I(B) Funktion aus dem hintersten Peak bestimmen
B_coil = []; I_generator = []
for i in range(len(t)):
	if t[i] >= 635.:
		break
	if t[i] >= 518.:
		I0 = p1[0] + p1[1] * t[i]
		I_generator.append(I[i] - I0)
		B_coil.append(B[i])

# I(B) fitten
ib, success = optimize.leastsq(errfunc, [1.,1.], args=(B_coil, I_generator))
print "I(B) = (", ib[0], "+", ib[1], "* B [mT] ) mA"

# Plot
ax = pylab.figure().add_subplot(111)
B_array = [0., 190.]
ax.plot(B_coil, I_generator, "kx", label=u"Generatorstrom")
ax.plot(B_array, fitfunc(ib, B_array), "-", color="#0099dd", label=u"Fit: $I\, [\mathrm{mA}] = %.4f \cdot B\, [\mathrm{mT}]$" % (ib[1],))
pylab.xlabel(u"Magnetfeld $B\,[\mathrm{mT}]$")
pylab.ylabel(u"Generatorstrom $I\, [\mathrm{mA}]$")
pylab.legend(loc='lower right', numpoints=1)

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("strom.pdf")

# Anzeigen
#pylab.show()


