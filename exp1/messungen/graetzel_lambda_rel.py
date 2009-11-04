#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize


filename = "graetzel1 28-10-09.txt"
colsep = "\t"


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


# bisher Schätzwerte:
lam = [i[1] for i in data[:6]]
U = [i[2] for i in data[:6]]
lux = [i[3] for i in data[:6]]


#xarray = pylab.linspace(R1[0]-2., R1[-1]+2., 100)

pylab.plot(lam, [U[i] / lux[i] for i in range(len(lam))], "bo", label="Mesung")
#pylab.errorbar(R1, P, P_error, None, "bo", label="Messwerte")
pylab.xlim(380., 700.)
pylab.ylim(0., 1.1*max([U[i] / lux[i] for i in range(len(lam))]))

pylab.xlabel(u"$\lambda\; [\mathrm{nm}]$")
pylab.ylabel(u"$U/V [\mathrm{V/lux}]$")

#pylab.legend(loc='lower right')


# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("graetzel_lambda_rel.pdf")

# Anzeigen
pylab.show()

