#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as p
import scipy
import numpy
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


data = readdata("data.txt")

x = [i[0] for i in data]
y = [i[1] for i in data]
delta_y = [i[2] for i in data]
u = p.linspace(0,0.6,100)
delta_x = 0





ax = p.figure().add_subplot(111)

ax.plot(u, (33.3479*u+14.2684), 'k--', label="$33.35 \\frac{ \mathrm{deg} }{ \mathrm{s} } \cdot t - 14.27 \mathrm{deg}$" )  # fit
#ax.plot(x, y, "bo", label="Messung")


ic = 6
ax.errorbar(x[:ic], y[:ic], delta_y[:ic], delta_x, "ro", label="Messung")
ax.errorbar(x[ic:], y[ic:], delta_y[ic:], delta_x, "bo", label="")

#p.grid()                      
p.xlabel('Zeit t in [s]')
p.ylabel('Drehwinkel $\phi$ in [deg]')

p.legend(loc='best')  # Legende



# Speichern
p.gcf().set_size_inches(6, 4)
p.savefig("messung_Video.pdf")

# Anzeigen
p.show()

