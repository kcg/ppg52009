#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
import os
import random, colorsys
from math import *



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

def spectral(lamb, bgcolor=None):
	'''
	calculates an rgba-color from wavelengths
	'''
	#   UV, violett, blau, türkis, grün, gelb, rot,  IR
	l = [350., 400., 450., 492., 535., 580., 650., 750.]
	colors = [[.5, .5, 0., 0., 0., 1., 1., 1.],
		[0., 0., 0., .8, 1., 1., 0., 0.],
		[1., 1., 1., .9, 0., 0., 0., 0.],
		[0., 1., 1., 1., 1., 1., 1., 0.]]
	
	rgba = []

	i = 0
	while i < len(l) - 1 and l[i+1] <= lamb:
		i += 1
	
	for j in range(4):
		if lamb <= l[0] or l[-1] <= lamb:
			rgba.append(colors[j][i])
		else:
			f = (lamb - l[i]) / (l[i+1] - l[i])
			rgba.append(colors[j][i] * (1. - f) + f * colors[j][i+1])		
	
	if bgcolor == None:
		return tuple(rgba)
	else:
		x = rgba[3]; y = 1. - x
		return tuple([x * rgba[i] + y * bgcolor[i] for i in range(3)])


# Dateien im Verzeichnis suchen
filenames = []
for i in os.walk('.'):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if len(filenames[i]) < 4:
		del filenames[i]
	elif filenames[i][-4:] != ".dat":
		del filenames[i]
	else:
		i += 1


filenames.sort()
#filenames.reverse()
pl.clf()
for k in range(len(filenames)):
	fname = filenames[k]
	data = readdata(fname)
	U = [i[0] for i in data]
	I = [i[1] for i in data]
	
	lmean = sc.dot(U,I) / sum(I)

	col = spectral(lmean, (0,0,0))
	#col = colorsys.hsv_to_rgb(random.random(),
	#	1., 1. - .5 * random.random()**2)
	pl.plot(U, I, "-", color=col, label=fname[:-4], linewidth=3)

pl.xlabel(u"Wellenlänge [nm]")
pl.ylabel(u"LED Signal")
#pl.xlim(345., 675.)
pl.ylim(0., 1.02)
pl.rcParams.update({'font.size' : 14})
pl.legend(loc=u"best", ncol=3)
pl.show()

