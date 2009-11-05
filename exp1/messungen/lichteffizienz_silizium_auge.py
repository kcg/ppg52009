#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize


filename1 = "lichteffizienz_auge.txt"
filename2 = "hamamatsuS1133.txt"
colsep = "\t"


ifile = open(filename1, "r")
data1 = []
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
	data1.append(row)
ifile = open(filename2, "r")
data2 = []
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
	data2.append(row)


# Werte Spaltenweise
lam1 = [i[0] for i in data1]
V1 = [i[1] for i in data1]
lam2 = [i[0] for i in data2]
V2 = [i[1] for i in data2]

# Flächen normieren
A1 = sum((lam1[i+1] - lam1[i]) * (V1[i] + V1[i+1]) / 2. for i in range(len(lam1)-1))
A2 = sum((lam2[i+1] - lam2[i]) * (V2[i] + V2[i+1]) / 2. for i in range(len(lam2)-1))

pylab.plot(lam1, V1, "k--")
pylab.plot(lam2, [i * A1 / A2 for i in V2], "k-")
pylab.xlim(290, 820)
pylab.ylim(0., 1.1)

pylab.xlabel(u"$\lambda\; [\mathrm{nm}]$")
pylab.ylabel(u"$V$ (Energieeffizienz)")
pylab.legend((u"Auge", u"Si-Diode"), loc='upper right')

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("lichteffizienz_silizium_auge.pdf")

# Anzeigen
pylab.show()

