#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
from math import *
from scipy import optimize
import scipy.interpolate
from matplotlib import colors as clr



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


data = readdata("vormessung_leitfaehigkeit.txt")
salz = [i[0] for i in data]
I = [i[1] for i in data]
U = [i[2] for i in data]

# Salz Konzentration
wasser = 14.3 * 14.3 * 1.4
c = [i / (i + wasser) for i in salz]

# Leitfähigkeit
l = 14.3
A = 14.3 * 1.4
sigma = [I[i] / U[i] * l / A for i in range(len(I))]

"""
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
"""

# make colors from values
def mycolor(x):
	x = 4.*(x%1.)
	num = int(x); frac = x - num;
	red = 0.; green = 0.; blue = 0.
	if num == 0:
		green = frac; blue = 1.
	elif num == 1:
		green = 1.; blue = 1. - frac
	elif num == 2:
		green = 1.; red = frac
	else:
		green = 1. - frac; red = 1.
	red = hex(int(255.*red))[2:]
	green = hex(int(255.*green))[2:]
	blue = hex(int(255.*blue))[2:]
	while len(red) < 2:
		red = "0" + red
	while len(green) < 2:
		green = "0" + green
	while len(blue) < 2:
		blue = "0" + blue
	return "#" + red + green + blue
U_min = min(U)
U_max = max(U) + 0.001 * (max(U) - min(U))



# Plot
pylab.rcParams['figure.subplot.left'] = 0.14
pylab.rcParams['figure.subplot.bottom'] = 0.11
pylab.rcParams['figure.subplot.top'] = 0.96
#pylab.plot([0.,0.], [0.,90.], "k-", [16.,16.], [0.,90.], "k-")

for i in range(len(c)):
	if U[i] <= 370:
		err = 5
	else:
		err = 30
	# Fehler aus der Strommessung
	err = sigma[i] / U[i] * err
	err = sqrt(err**2 + (sigma[i] / 14.)**2)
	pylab.errorbar([c[i]], [sigma[i]], [err], None, "o", color=mycolor((U[i] - U_min) / (U_max - U_min)))
# blau: wenig Spannung, rot: viel Spannung

'''for di, col in zip(d3, colors):
	xx = []; BB = []
	for i in range(len(d)):
		if d[i] == di:
			xx.append(x[i])
			BB.append(B[i])
	pylab.plot(xx, BB, col+'o')'''

pylab.xlim(min(c) - 0.01, max(c) + 0.01)
#pylab.ylim(0., 90.)

pylab.xlabel(u"Salzkonzentration [% Masse]")
pylab.ylabel(u"Leitfähigkeit [$\Omega^{-1}m^{-1}$]")


# Speichern
pylab.gcf().set_size_inches(6, 4)
pylab.savefig("vormessung_leitfaehigkeit.pdf")

# Anzeigen
pylab.show()

