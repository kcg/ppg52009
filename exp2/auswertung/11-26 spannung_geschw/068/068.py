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


data = readdata("068-all.txt")

t = [i[0] for i in data]
U = [-i[1] for i in data]
B = [0.1*i[3] for i in data]
#u = p.linspace(0,1.2,100)





ax = p.figure().add_subplot(111)

#ax.plot(u, (19.0646*u-0.0622608), 'k--', label="$19.065 \\frac{ \\frac{\mathrm{mV}}{\mathrm{T}} }{ \\frac{\mathrm{m}}{\mathrm{s}}} \cdot v - 0.0623 \mathrm{mV}$" )  # fit
ax.plot(t, U, "k-", label="Spannung")
ax.plot(t, B, "g-", label="B-Feld")



#p.grid()                      
p.xlabel('Zeitverlauf t in [s]')
p.ylabel('Spannung U in [mV], Magnetfeld B in [$10^{-2}$T]')

p.legend(loc='lower right')  # Legende



# Speichern
p.gcf().set_size_inches(6, 4)
p.savefig("messung_Spannung-Geschw.pdf")

# Anzeigen
p.show()

