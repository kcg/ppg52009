#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy as sc
from math import *
from scipy import optimize


filename = "graetzel_P 29-10-09.txt"
colsep = "\t"


# Die Modellfunktion
def fitfunc(p, x):
	# U² * R / (R + RZ)²
	return p[0]**2 * x / (x + p[1])**2


# Abstandsfunktion zwischen Modell und Daten
def errfunc(p, x, y, var_y):
	yw = fitfunc(p, x)
	# Korelation hier noch nicht berücksichtigt!
	return (yw - y) / sc.sqrt(sc.diag(var_P))

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
R = sc.array([i[0] + R_amp for i in data])
U = sc.array([i[1] for i in data])
I = sc.array([i[2] for i in data])
n = len(R)


############ Fehlerrechnung #################
# Wir vernachlässigen die Fehler in R
U_error = 1.	# 1mV Ablesefehler
I_error_e = 0.1	# 0.1µA Ablesefehler
I_error_c = 0.1	# 0.1µA Offsetungenauigkeit

# Kovarianzmatrizen
var_U = U_error**2 * sc.eye(n)
var_I = I_error_c**2 * sc.ones((n, n)) + I_error_e**2 * sc.eye(n)

P = [U[i] * I[i] for i in range(n)]
var_P = sc.dot(var_U, sc.diag(I)**2) + sc.dot(sc.diag(U), sc.dot(var_I, sc.diag(U)))


################# Fit ######################
# Anfangswert für Parameter
p0 = [135., 16.]
# Fit durchführen
fit = optimize.leastsq(errfunc, p0[:], args=(R, P, var_P), full_output=True)
p1 = fit[0]

print "best-fit Werte:"
for i in range(len(fit[0])):
	print "%.3f +- %.3f" % (fit[0][i], sqrt(fit[1][i][i]))


################# Plot #####################
pylab.rcParams['figure.subplot.bottom'] = 0.11
pylab.rcParams['figure.subplot.top'] = 0.96
xarray = pylab.linspace(R[0]-2., R[-1]+2., 100)
pylab.plot(xarray, fitfunc(p1, xarray), "k-", label='$(%.0f\,\mathrm{mV})^2 \cdot \\frac{R}{(R+%.0f\,\mathrm{k\Omega})^2}$' % (p1[0], p1[1]))
pylab.errorbar(R, P, sc.sqrt(sc.diag(var_P)), None, "bo", label="Messwerte")
pylab.xlim(0., R[-1]+3.)
pylab.ylim(0., 330.)

pylab.xlabel(u"$R\; [\mathrm{k\Omega}]$")
pylab.ylabel(u"$P\; [\mathrm{nW}]$")

pylab.legend(loc='lower right')

x_max = p1[1]
y_max = p1[0]**2 / (4. * p1[1])
print "maximale Leistung:"
jacobi_dmax = sc.array([2.*p1[0] / (4. * p1[1]), -p1[0]**2 / (4. * p1[1]**2)])
print "%.3f +- %.3f" % (y_max, sqrt(sc.dot(jacobi_dmax, sc.dot(fit[1], jacobi_dmax.transpose()))))
pylab.annotate('%.0f nW' % (y_max,), xy=(x_max, y_max+18),  xycoords='data', horizontalalignment='center', verticalalignment='bottom')


# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_leistung.pdf")

# Anzeigen
pylab.show()

