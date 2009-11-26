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


data = readdata("messung_B-Feld-Abstand.txt")

x = [i[0] for i in data]
y = [i[1] for i in data]

p.plot(x,y, 'bo' )
                     
p.xlabel('Abstand in [mm]')      
p.ylabel('B-Feld in [mT] bei 1A')


# Speichern
p.gcf().set_size_inches(6, 4)
p.savefig("messung_B-Feld-Abstand.pdf")

# Anzeigen
p.show()

