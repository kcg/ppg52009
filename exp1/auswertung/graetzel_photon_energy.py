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



# Die Modellfunktion
def fitfunc(p, xx):
	return [p[0] * (x - p[1]) for x in xx]

# Abstandsfunktion zwischen Modell und Daten
def errfunc(p, x, y, hwhm):
	yw = fitfunc(p,x)
	# Berücksichtigen, dass ein Teil des LED-Spektrums abgeschnitten wird (da Energie zu klein)
	return [yw[i] - y[i] for i in range(len(x))]


# Datne einlesen
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
# E = h * c / lambda
energy = [1.23986E3 / i for i in lam]

# Fehler (FWHM Spektrenbreite)
delta_lam = [i[5]/2. for i in data_graetzel[:color_diods]]
delta_energy = [energy[i] / lam[i] * delta_lam[i] for i in range(len(energy))]

def V(lamb):
	"""
	interpoliert das Spektrum der Si-Diode an beliebiger Stelle
	"""
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
print hell_norm
print E_norm


# Anfangswert für Parameter
p0 = [1.3, 2.]
# Fit durchführen
p1, success = optimize.leastsq(errfunc, p0[:], args=(energy, E_norm, delta_energy))
print p1
xarray = pylab.linspace(p1[1], energy[-1] + 0.07, 2)

# Plotten
pylab.rcParams['figure.subplot.bottom'] = 0.12
pylab.rcParams['figure.subplot.top'] = 0.96
pylab.plot([0.], [0.], "ko", markersize=10., markeredgewidth=1., markerfacecolor="white")
pylab.plot(xarray, fitfunc(p1, xarray), "k-")
colors=['#de2b35', '#f48622', '#f9df30', '#82b8e6', '#887ecd', '#2656a8']
for i in range(len(lam)):
	pylab.errorbar(energy[i], E_norm[i], None, delta_energy[i], "ko", markersize=10., markeredgewidth=1., markerfacecolor=colors[i])

pylab.xlim(1.78, 2.9)
pylab.ylim(0., 1.1)

pylab.xlabel(u"$E_\mathrm{phot}\; [\mathrm{eV}]$")
pylab.ylabel(u"$V$ (Energieeffizienz)")
pylab.legend(("LEDs", "$V_0\cdot(E-%.2f\,\mathrm{eV})$" % (p1[1])), loc='lower right', numpoints=1)

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_photon_energy.pdf")

# Anzeigen
pylab.show()

