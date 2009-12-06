#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as p
import scipy
from math import *
from scipy import optimize
import scipy.interpolate
from matplotlib import colors as clr

def fit(p, x, y):
	yw = [p[0] / (xx + p[1]) for xx in x]
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


data = readdata("messung_B-Feld-Abstand.txt")

d = [i[0] for i in data]
B = [i[1] for i in data]

# Fitten
p1, success = optimize.leastsq(fit, [1., 0.], args=(d, B))
d_array = scipy.linspace(5., 50., 41)

p.plot(d_array, [p1[0] / (i + p1[1]) for i in d_array], 'k-', label=u"Fit: $\\frac{%.0f\,\mathrm{mT}}{(d + %.1f\,\mathrm{mm})/\mathrm{cm}}$" % (p1[0]/10., p1[1]))

p.plot(d, B, 'bo', label="Messung")
                     
p.xlabel('Abstand in [mm]')
p.ylabel('B-Feld in [mT] bei 1A')


# Speichern
p.gcf().set_size_inches(6, 4)
p.legend()
p.savefig("messung_B-Feld-Abstand.pdf")

# Anzeigen
p.show()

