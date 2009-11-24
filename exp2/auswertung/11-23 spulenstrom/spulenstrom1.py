#! /usr/bin/env python
# -*- coding: utf8 -*-

# Auslesen der Spannungsdifferenzen aus den gemessenen Rohdaten

import pylab
import scipy
from math import *
from scipy import optimize


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]
		linetext = linetext.strip()
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
data = readdata("spulenstrom1.txt")

# Werte Spaltenweise
t = [i[1] for i in data]
U = [i[2] for i in data]

# Vorbereitung fuer Plots
pylab.rcParams['figure.subplot.bottom'] = 0.12
#pylab.rcParams['figure.subplot.top'] = 0.96
ax = pylab.figure().add_subplot(111)



# Punktzahl reduzieren
i500 = 0
print len(t)
t1 = t[:]
U1 = U[:]
for j in range(8):
	i = 0
	m = 2
	while i < len(t1):
		if (i >= m - 1 and abs(max(U1[i-m+1:i+1]) - min(U1[i-m+1:i+1])) <= 0.25):
			t1 = t1[:i-m+1] + [sum(t1[i-m+1:i+1]) / float(m)] + t1[i+1:]
			U1 = U1[:i-m+1] + [sum(U1[i-m+1:i+1]) / float(m)] + U1[i+1:]
			i += m
		else:
			i += 1
		if i < len(t1) and t1[i] < 500:
			i500 = i
	print len(t1)

ic = 6
# Plot1
ax.plot(t1[i500:], U1[i500:], "kx", label=u"gemessene Spannung", markersize=3.)


# Fits
f1 = lambda x: 15.33 + 208.9 / sqrt(x)
f2 = lambda x: 46.47 - 3.538 * log(x)
xx = scipy.linspace(500., 1350., 40)
ax.plot(xx, [f1(x) for x in xx], "r-", label=u"Fit1")
for i in [[825,895,0.67], [875,912,1.35], [924,971,2.01], [971,1030,2.52], [1040,1100,2.91], [1110,1180,3.06]]:
	xx = scipy.linspace(i[0], i[1], 10)
	ax.plot(xx, [f1(x) + i[2] for x in xx], "r-")
xx = scipy.linspace(1200., 2300., 40)
ax.plot(xx, [f2(x) for x in xx], "-", color="#00ff00", label=u"Fit2")
for i in [[1580,1675,3.13], [1750,1820,2.40], [1980,2045,3.64], [2070,2126,3.20], [2137,2190,3.42]]:
	xx = scipy.linspace(i[0], i[1], 10)
	ax.plot(xx, [f2(x) + i[2] for x in xx], "-", color="#00ff00")

pylab.xlim(500., 2300.)
pylab.ylim(17., 25.5)
pylab.xlabel(u"$t$ [s]")
pylab.ylabel(u"Zellspannung $U\, [\mathrm{mV}]$")
pylab.legend(loc='lower left', numpoints=1)
# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("spannung1.pdf")


# Plot2
# Theoretische Werte: U / B = v * d = 1.23m/s * 1.8cm = 22 mV/T
#B_array = scipy.array([0., 200.])
#ax = pylab.figure().add_subplot(111)
#ax.plot(B_array, 0.022 * B_array, "k--", label=u"Theorie: $U/B = v\cdot d$")



# Anzeigen
pylab.show()

