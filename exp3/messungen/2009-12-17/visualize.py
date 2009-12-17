#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr



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
	if len(filenames[i]) < 7:
		filenames = filenames[0:i] + filenames[i+1:-1]
	elif filenames[i][:3] != "led":
		filenames = filenames[0:i] + filenames[i+1:-1]
	elif filenames[i][-4:] != ".dat":
		filenames = filenames[0:i] + filenames[i+1:-1]
	else:
		i += 1

# Spektralfarben
def spectral(lamb):
	red = 0.; green = 0.; blue = 0.
	if lamb < 400.:
		pass
	elif lamb <= 470.:
		blue = (lamb-400.) / (470. - 400.)
		red = (lamb-400.) / (470. - 400.) * ( 1. - (lamb-400.) / (470. - 400.))
	elif lamb <= 525.:
		blue = (525. - lamb) / (525. - 470.)
		green = (lamb - 470.) / (525. - 470.)
	elif lamb <= 575.:
		green = 1.
		red = (lamb - 525.) / (575. - 525.)
	elif lamb <= 640.:
		red = 1.
		green = (640. - lamb) / (640. - 575.)
	elif lamb <= 700.:
		red = (700. - lamb) / (700. - 640.)
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


for fname in filenames:
	data = readdata(fname)
	U = [i[0] for i in data]
	I = [i[1] for i in data]

	try:
		x = float(fname[3:6])
		col = spectral(x)
	except ValueError:
		col = "#000000"
	pylab.plot(U, I, "-", color=col, label=fname[3:-3])

pylab.xlabel(u"Poti Spannung")
pylab.ylabel(u"LED Spannung")
pylab.rcParams.update({'font.size' : 5})
pylab.legend(loc=u"best")
pylab.show()

