#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as p
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


data = readdata("messung_Strom-B-Feld.txt")

x = [i[0] for i in data]
y = [i[1] for i in data]
delta_B = [i[2] for i in data]
delta_I = [i[3] for i in data]
u = p.linspace(-0.05,2.05,100)





ax = p.figure().add_subplot(111)

ax.plot(u, (94.3416*u+16.0346), 'k--' )  # fit

ic = 16

ax.errorbar(x[:ic], y[:ic], delta_I[:ic], delta_B[:ic], "bo", label=u"Netzgeräte einzeln")
ax.errorbar(x[ic:], y[ic:], delta_I[ic:], delta_B[ic:], "ro", label=u"Netzgeräte zusammen")


p.xlim(-0.05,+2.05)
p.ylim(-5,+250)

p.grid()                      
p.xlabel('Spulenstrom I in [A]')
p.ylabel('B-Feld B in [mT] bei 1mm Jochabstand')

p.legend(('$94.34 \\frac{\mathrm{mT}}{\mathrm{A}} \cdot I + 16.03\mathrm{mT}$', 'Messwerte'),loc='lower right')  # Legende



# Speichern
p.gcf().set_size_inches(6, 4)
p.savefig("messung_Strom-B-Feld.pdf")

# Anzeigen
p.show()

