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


data = readdata("messung_Strom-B-Feld.txt")

x = [i[0] for i in data]
y = [i[1] for i in data]
delta_B = [i[2] for i in data]
delta_I = [i[3] for i in data]
u = p.linspace(-0.05,2.05,100)





ax = p.figure().add_subplot(111)

ax.plot(u, (204.087*numpy.arctan(u*0.666)), 'k--', label="$204.087 \mathrm{mT} \cdot arctan(I*0.666 \\frac{1}{\mathrm{A}})$" )  # fit

ic = 16

ax.errorbar(x[:ic], y[:ic], delta_I[:ic], delta_B[:ic], "bo", label=u"Netzgeräte einzeln")
ax.errorbar(x[ic:], y[ic:], delta_I[ic:], delta_B[ic:], "ro", label=u"Netzgeräte zusammen")


p.xlim(-0.05,+2.05)
p.ylim(-5,+250)

p.grid()                      
p.xlabel('Spulenstrom I in [A]')
p.ylabel('B-Feld B in [mT] bei 1mm Jochabstand')

p.legend(loc='lower right')  # Legende



# Speichern
p.gcf().set_size_inches(7.5, 5)
p.savefig("messung_Strom-B-Feld.pdf")

# Anzeigen
p.show()

