#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
from math import *
import scipy.interpolate as ip



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




data1 = readdata("led640nm_5mm.dat")
w1 = sc.array([i[0] for i in data1])
U1 = sc.array([i[1] for i in data1])
U1 /= max(U1)

data2 = readdata("ledplcc-2_smd.dat")
w2 = sc.array([i[0] for i in data2])
U2 = sc.array([i[1] for i in data2])
U2 /= max(U2)

wgrid = sc.linspace(-90., 90., 181)

spline1 = ip.splrep(w1, U1, k=1)
U1grid = ip.splev(wgrid, spline1)

spline2 = ip.splrep(w2, U2, k=3)
U2grid = ip.splev(wgrid, spline2)

# Plot
pl.rcParams['figure.subplot.left'] = 0.1
pl.rcParams['figure.subplot.right'] = 0.9
pl.rcParams['figure.subplot.bottom'] = 0.09
pl.rcParams['figure.subplot.top'] = 0.96

pl.plot(wgrid, U2grid, "r-", label="SMD LED plcc-2 flach")
pl.plot(w2, U2, "ro")

pl.plot(wgrid, U1grid, "b-", label="5mm Standard LED")
pl.plot(w1, U1, "bo")


pl.xlim(-92., 92.)
pl.ylim(0., 1.3)
pl.xticks(range(-90, 105, 15), [str(i) + u"°" for i in range(-90, 105, 15)])
pl.grid()
pl.xlabel(u"Einstrahlwinkel")
pl.ylabel(u"Spannungssignal an der LED")
pl.legend(loc=u"upper right")
# Speichern
pl.gcf().set_size_inches(7, 5)
pl.savefig("richtungsabhaengigkeit.pdf")

