#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr


# Zeigt einzelne Spektren an
# lässt manuelle Grenzwerte eingeben, ab welchen die Intensität
# zur Null hin interpoliert wird.


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





def spectral(lamb):
	'''
	Berechnet eine rgba-Farbe aus Wellenlängen
	'''
	l = [360., 400., 470., 535., 580., 650., 720.]
	#   UV, violett, blau, grün, gelb, rot,  IR

	red = 0.; green = 0.; blue = 0.; alpha = 1.
	if lamb < l[0]:
		alpha = 0.
	elif lamb <= l[1]:
		alpha = (lamb - l[0]) / (l[1] - l[0])
		blue = (lamb - l[0]) / (l[1] - l[0])
		red = .5 * (lamb - l[0]) / (l[1] - l[0])
	elif lamb <= l[2]:
		red = .5 * (l[2] - lamb) / (l[2] - l[1])
		blue = 1.
	elif lamb <= l[3]:
		blue = 1. - (1. - (l[3] - lamb) / (l[3] - l[2])) **2
		green = 1. - (1. - (lamb - l[2]) / (l[3] - l[2])) **2
	elif lamb <= l[4]:
		green = 1.
		red = (lamb - l[3]) / (l[4] - l[3])
	elif lamb <= l[5]:
		red = 1.
		green = (l[5] - lamb) / (l[5] - l[4])
	elif lamb <= l[6]:
		red = 1.
		alpha = (l[6] - lamb) / (l[6] - l[5])
	else:
		alpha = 0.

	return (red, green, blue, alpha)



# Dateien im Verzeichnis suchen
filenames = []
for i in os.walk('.'):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if len(filenames[i]) < 7:
		del filenames[i]
	elif filenames[i][:3] != "led" or filenames[i][-4:] != ".dat":
		del filenames[i]
	else:
		i += 1
filenames.sort()
filenames.reverse()


j = 0
while True:
	pl.clf()
	fname = filenames[j]
	data = readdata(fname)
	l = [int(i[0]) for i in data]
	I = [i[1] for i in data]

	try:
		x = float(fname[3:6])
		col = spectral(x)[:3]
	except ValueError:
		col = "#000000"
	pl.plot(l, I, "-", color=col, label=fname[3:-4])

	pl.xlabel(u"Poti Spannung")
	pl.ylabel(u"LED Spannung")
	pl.xlim(345., 675.)
	pl.rcParams.update({'font.size' : 9})
	pl.legend(loc=u"best", ncol=5)
	pl.show()
	j = (j + 1) % len(filenames)
	print fname
	nix = raw_input("nullen einfügen=n: ")
	if nix == "n":
		a = int(raw_input("0: "))
		b = int(raw_input("erhalten: "))
		ofile = open(fname, "w")
		ofile.write("# " + fname + "\n")
		ofile.write("# Spalte1: Wellenlänge [nm]\n")
		ofile.write("# Spalte2: Intensität\n")
		for i in range(len(l)):
			if (l[i] - b) * (b - a) > 0.:
				ofile.write(str(l[i]) + "\t%.6f\n" % (I[i],))
			elif (l[i] - a) * (a - b) >= 0.:
				ofile.write(str(l[i]) + "\t0.000000\n")
			else:
				ofile.write(str(l[i]) + "\t%.6f\n" % ((l[i] - a) / float(b - a) * I[b-l[0]],))
		ofile.close()












