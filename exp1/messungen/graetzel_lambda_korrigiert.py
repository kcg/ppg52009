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


E = [U[i] / hell[i] for i in range(color_diods)]
max_E = max(E)
E_norm = [i / max_E for i in E]


# Spline Interpolation
#lam.reverse()
#E_norm.reverse()
#newx = pylab.linspace(400, 660, 100)
#tck = scipy.interpolate.splrep(lam,E_norm)
#newy = scipy.interpolate.splev(newx,tck,der=0)
#print [[lam[i], E_norm[i]] for i in range(len(lam))]
# Spline-liste von mathematica
x_spline = [420., 430., 440., 450., 460., 470., 480., 490., 500., 510., 520., 530., 540., 550., 560., 570., 580., 590., 600., 610., 620., 630., 640, 650., 660.]
y_spline = [1.001, 1., 0.998, 0.991, 0.973, 0.938, 0.883, 0.813, 0.734, 0.654, 0.578, 0.507, 0.440, 0.379, 0.321, 0.269, 0.220, 0.175, 0.134, 0.100, 0.073, 0.056, 0.046, 0.039, 0.035]



pylab.plot(x_spline, y_spline)
pylab.plot(lam, E_norm, "bo")
pylab.xlim(380., 700.)
pylab.ylim(0., 1.1)

pylab.xlabel(u"$\lambda\; [\mathrm{nm}]$")
pylab.ylabel(u"$V$ (Energieeffizienz)")
pylab.legend((u"Spline-Fit", u"Messung",), loc='upper right')

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_lambda_korrigiert.pdf")

# Anzeigen
pylab.show()

