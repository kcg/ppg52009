#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize
import scipy.interpolate



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


data = readdata("vormessung_magnetfeld.txt")
d = [i[0] for i in data]
x = [i[1] for i in data]
z = [i[2] for i in data]
B = [i[3] for i in data]


# collect values of d in d3
d2 = 1 * d; d2.sort(); d3 = []
for i in d2:
	if len(d3) == 0 or i != d3[-1]:
		d3.append(i)

# Spline Interpolation
splines = {}
for di in d3:
	xx = []; BB = []
	for i in range(len(d)):
		if d[i] == di and z[i] == z[0]:
			xx.append(x[i])
			BB.append(B[i])
	'''
	x_spline = pylab.linspace(min(xx), max(xx), 40)
	spline = scipy.interpolate.splrep(xx, BB)
	y_spline = scipy.interpolate.splev(x_spline, spline, der=0)
	splines[di] = [x_spline, y_spline]
	'''
	splines[di] = [xx, BB]


# Plot
pylab.rcParams['figure.subplot.bottom'] = 0.11
pylab.rcParams['figure.subplot.top'] = 0.96
pylab.plot([0.,0.], [0.,90.], "k-", [16.,16.], [0.,90.], "k-")

colors = ('rgb')
for di, col in zip(splines.iteritems(), colors):
	pylab.plot(di[1][0], di[1][1], col, label="d=%.1f cm" % di[0])
for di, col in zip(d3, colors):
	xx = []; BB = []
	for i in range(len(d)):
		if d[i] == di:
			xx.append(x[i])
			BB.append(B[i])
	pylab.plot(xx, BB, col+'o')
pylab.xlim(min(x) - 1., max(x) + 1.)
pylab.ylim(0., 90.)

pylab.xlabel(u"Position [cm]")
pylab.ylabel(u"Magnetfeld [mT]  bei 1A")
pylab.legend(loc=8)

# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("vormessung_magnetfeld.pdf")

# Anzeigen
pylab.show()

