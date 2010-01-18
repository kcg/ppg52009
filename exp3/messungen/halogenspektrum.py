#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy as sc
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr



def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]
		if len(linetext) <= 1:
			continue
		while linetext[-1] == " " or linetext[-1] == "\t":
			if len(linetext) == 1:
				continue
			else:
				linetext = linetext[:-1]
		line = linetext.split(colsep)
		if len(line) <= 0:
			continue
		row = []
		appending = True
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print i, "is not a float"
				appending = False
		if appending:
			data.append(row)
	return(data)


# Datei öffnen
halo = readdata("spektrum-2010-01-18/halogen.txt")
lam = [i[0] for i in halo]
i1 = sc.array([i[1] for i in halo])

dark = readdata("spektrum-2010-01-18/dark current2.txt")
lam2 = [i[0] for i in dark]
i2 = sc.array([i[1] for i in dark])

intensity = i1 - i2
intensity2 = intensity.copy()

# Glätten
for i in range(1, len(intensity)-1):
	if intensity[i] < 100. and i > 4 and i < len(intensity)-4:
		intensity2[i] = sum(intensity[i-4:i+5]) / 9.
	else:
		intensity2[i] = sum(intensity[i-1:i+2]) / 3.


ofile = open("kalibrationsspektrum/halogen.dat", "w")
ofile.write("# Spektrum der Halogenlampe bei 4,8 A\n")
ofile.write("# Spalte1: Wellenlänge [nm]\n")
ofile.write("# Spalte2: Intensität\n")
for i in range(len(intensity)):
	ofile.write("%.2f\t%.0f.\n" % (lam[i], intensity2[i]))
ofile.close()


pylab.plot(lam, i2, "r-", label="offset")
pylab.plot(lam, i1, "b-", label="roh")
pylab.plot(lam, intensity2, "-", color="#00cc00", label="fertig")



pylab.xlabel(u"Wellenlänge")
pylab.ylabel(u"Intensität")
pylab.legend(loc=u"best")
pylab.show()

