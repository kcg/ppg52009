#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr
import random, colorsys



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
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print i, "is not a float"
				row.append(0.)
		data.append(row)
	return(data)


# Dateien im Verzeichnis suchen
filenames = []
for i in os.walk('.'):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if filenames[i][-4:] != ".dat":
		del filenames[i]
	else:
		i += 1


for fname in filenames:
	data = readdata(fname)
	U = [i[0] for i in data]
	I = [i[1] for i in data]
	I_foto = [i[2] for i in data]
	
	#zufallsfarbe
	col = colorsys.hsv_to_rgb(random.random(),
		1., 1. - .5 * random.random()**2)
	
	pylab.plot(U, I, "-", color=col, label=fname[:-4], linewidth=2)
	pylab.plot(U, I_foto, "-", color=col, label=None, linewidth=.5)

pylab.xlabel(u"Poti Spannung")
pylab.ylabel(u"LED Spannung")
pylab.rcParams.update({'font.size' : 6})
pylab.legend(loc=u"best", ncol=2)
pylab.show()

