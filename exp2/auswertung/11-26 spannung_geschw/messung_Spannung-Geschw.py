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


data = readdata("fertig1.txt")

x = [i[0] for i in data]
y = [i[1] for i in data]
#delta_B = [i[2] for i in data]
#delta_I = [i[3] for i in data]
u = p.linspace(0.25,1.01,100)





ax = p.figure().add_subplot(111)

ax.plot(u, (-19.0646*u+0.0622608), 'k--', label="$-19.065 \\frac{ \\frac{\mathrm{mV}}{\mathrm{T}} }{ \\frac{\mathrm{m}}{\mathrm{s}}} \cdot v + 0.0623 \mathrm{mV}$" )  # fit
ax.plot(x, y, "bo", label="Messung")


#ax.errorbar(x[:ic], y[:ic], delta_I[:ic], delta_B[:ic], "bo", label=u"Netzgeräte einzeln")
#ax.errorbar(x[ic:], y[ic:], delta_I[ic:], delta_B[ic:], "ro", label=u"Netzgeräte zusammen")

#p.grid()                      
p.xlabel('Geschwindigkeit v in [m/s]')
p.ylabel('$\Delta$U/$\Delta$B in [mV/T]')

p.legend(loc='lower left')  # Legende



# Speichern
p.gcf().set_size_inches(6, 4)
p.savefig("messung_Spannung-Geschw.pdf")

# Anzeigen
p.show()

