#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize
import scipy.interpolate
from scipy import signal



# Die Modellfunktion
def fitfunc(p, xx):
	return [p[0] * (x - p[1]) for x in xx]

# Abstandsfunktion zwischen Modell und Daten
def errfunc(p, x, y, hwhm):
	yw = fitfunc(p,x)
	# Berücksichtigen, dass ein Teil des LED-Spektrums abgeschnitten wird (da Energie zu klein)
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


# Daten einlesen
data = readdata("11-23 induzuerte_spannung.txt")

# Werte Spaltenweise
I = [i[0] for i in data]
U = [i[1] for i in data]
delta_I = [i[2] for i in data]
delta_U = [i[3] for i in data]

# Vorbereitung fuer Plots
pylab.rcParams['figure.subplot.bottom'] = 0.12
#pylab.rcParams['figure.subplot.top'] = 0.96
ax = pylab.figure().add_subplot(111)

ic = 6
# Plot1
ax.errorbar(I[:ic], U[:ic], delta_U[:ic], delta_I[:ic], "bo", label=u"Netzgeräte einzeln")
ax.errorbar(I[ic:], U[ic:], delta_U[ic:], delta_I[ic:], "ro", label=u"Netzgeräte zusammen")
pylab.ylim(0., 4.)
pylab.xlabel(u"Spulenstrom $I\, [\mathrm{A}]$")
pylab.ylabel(u"Zellspannung $U\, [\mathrm{mV}]$")
pylab.legend(loc='lower right', numpoints=1)
# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("induzuerte_spannung(I).pdf")


# Plot2
pylab.clf()
# Theoretische Werte: U / B = v * d = 1.23m/s * 1.8cm = 22 mV/T
B_array = scipy.array([0., 200.])
ax = pylab.figure().add_subplot(111)
ax.plot(B_array, 0.022 * B_array, "k--", label=u"Theorie: $U/B = v\cdot d$")

B = [89. * Ii for Ii in I]
# Der Fehler fürs Magnetfeld ist nicht sicher, weil B(I) noch nicht bekannt ist
delta_B = [89. * delta_I[i] + B[i] * 0.1 for i in range(len(delta_I))]
ax.errorbar(B[:ic], U[:ic], delta_U[:ic], delta_B[:ic], "bo", label=u"Netzgeräte einzeln")
ax.errorbar(B[ic:], U[ic:], delta_U[ic:], delta_B[ic:], "ro", label=u"Netzgeräte zusammen")
pylab.xlim(0., 200.)
pylab.ylim(0., 4.)
pylab.xlabel(u"Magnetfeld $B\, [\mathrm{mT}]$")
pylab.ylabel(u"Zellspannung $U\, [\mathrm{mV}]$")
pylab.title(u"Ausgangsspannung des MHD-Generators")
pylab.legend(loc='lower right', numpoints=1)
# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("induzuerte_spannung(B).pdf")

# Anzeigen
#pylab.show()

