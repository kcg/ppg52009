#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize
import scipy.interpolate
from scipy import signal



filename_graetzel = "graetzel1 28-10-09.txt"
filename_diode = "hamamatsuS1133.txt"
colsep = "\t"


ifile = open(filename_graetzel, "r")
data_graetzel = []
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
	data_graetzel.append(row)
ifile = open(filename_diode, "r")
data_diode = []
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
	data_diode.append(row)

color_diods = 6

# Werte Spaltenweise
lam = [i[1] for i in data_graetzel[:color_diods]]
U = [i[2] for i in data_graetzel[:color_diods]]
lux = [i[3] for i in data_graetzel[:color_diods]]
lambda_diode = [i[0] for i in data_diode]
V_diode = [i[1] for i in data_diode]

def V(lamb):
	i0 = 0
	i1 = len(lambda_diode)-1
	for i in range(len(lambda_diode)):
		if lambda_diode[i] <= lamb:
			i0 = i
		if lambda_diode[i] >= lamb:
			i1 = i
			break
	if i0 == i1:
		return V_diode[i0]

	return (V_diode[i0] * (lambda_diode[i1] - lamb) + V_diode[i1] * (lamb - lambda_diode[i0])) / (lambda_diode[i1] - lambda_diode[i0])

hell = [lux[i] / V(lam[i]) for i in range(color_diods)]
max_hell = max(hell)
hell_norm = [i / max_hell for i in hell]

print hell_norm

E = [U[i] / hell[i] for i in range(color_diods)]
max_E = max(E)
E_norm = [i / max_E for i in E]
print E_norm


# Spline Interpolation
#lam.reverse()
#E_norm.reverse()
#newx = pylab.linspace(400, 660, 100)
#newx)
#tck = scipy.interpolate.splrep(lam,E_norm)
#newy = scipy.interpolate.splev(newx,tck,der=0)



#pylab.plot(newx, newy)
pylab.plot(lam, E_norm, "bo")
pylab.xlim(380., 700.)
pylab.ylim(0., 1.1)

pylab.xlabel(u"$\lambda\; [\mathrm{nm}]$")
pylab.ylabel(u"$V$ (Energieeffizienz)")
pylab.legend((u"Messung",), loc='upper right')

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_lambda_korrigiert.pdf")

# Anzeigen
pylab.show()

