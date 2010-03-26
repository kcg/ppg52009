#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab
import scipy
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr
import random, colorsys

import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..', '..', '..', 'python'))
from read_data import *



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
	#zufallsfarbe
	col = colorsys.hsv_to_rgb(random.random(),
		1., 1. - .5 * random.random()**2)
		
	data = readdata(fname)
	U = [i[0] for i in data]
	if len(data[0]) == 2:
		I_foto = [i[1] for i in data]
		pylab.plot(U, I_foto, "-", color=col, label=None, linewidth=.5)
	else:
		I = [i[1] for i in data]
		I_foto = [i[2] for i in data]
	
		pylab.plot(U, I, "-", color=col, label=fname[:-4], linewidth=2)
		pylab.plot(U, I_foto, "-", color=col, label=None, linewidth=.5)

pylab.xlabel(u"Poti Spannung")
pylab.ylabel(u"LED Spannung")
pylab.rcParams.update({'font.size' : 6})
pylab.legend(loc=u"best", ncol=2)
pylab.show()

