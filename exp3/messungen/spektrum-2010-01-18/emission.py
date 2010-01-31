#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as p
import scipy as sc
import numpy
from math import *
from scipy import optimize
import scipy.interpolate
from matplotlib import colors as clr


def spectral(lamb):
	'''
	Berechnet eine rgba-Farbe aus Wellenlängen
	'''
	l = [360., 400., 470., 535., 580., 650., 750.]
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
	


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []; l = 0
	for linetext in ifile.readlines():
		l += 1
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1].strip()
		if linetext == "": continue
		line = linetext.split(colsep)
		if len(line) <= 0: continue
		row = []
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print 'File "' + filename + '",',
				print 'line ' + str(l) + ':',
				print '"' + i + '" is not a float'
				row.append(0.)
		data.append(row)
	ifile.close()
	return(data)



# Plot initialisieren
ax = p.figure().add_subplot(111)


# Daten einlesen
data_emitt = [readdata("led465-470.txt"), readdata("led525.txt"), readdata("led640.txt")]
data_absorb = [readdata("absorb/led465-470nm.dat"), readdata("absorb/led525nm-1.dat"), readdata("absorb/led640nm-1.dat")]
data_dark = readdata("dark.txt")
dark = sc.array([i[1] for i in data_dark])

col = ["465", "525", "640"]


# Emitt-Daten verarbeiten
x_em = [0 for i in range(0, len(data_emitt))]
y_em = [0 for i in range(0, len(data_emitt))]

for k in range(0, len(data_emitt)):
	x_em[k] = sc.array([i[0] for i in data_emitt[k]])
	y_em[k] = sc.array([i[-1] for i in data_emitt[k]])

	for l in range(0, len(dark)):	# Dark-Rate abziehen
		y_em[k][l] = (y_em[k][l]-dark[l])
		if y_em[k][l] < 0:
			y_em[k][l] = 0
			
	maximum = max(y_em[k])	# auf "1" normieren
	y_em[k] = y_em[k]/maximum
	
	ax.plot(x_em[k], y_em[k], "--", color=spectral(int(col[k])), linewidth=4)
	
	
# Absorb-Daten verarbeiten
x_ab = [0 for i in range(0, len(data_absorb))]
y_ab = [0 for i in range(0, len(data_absorb))]

for k in range(0, len(data_absorb)):
	x_ab[k] = sc.array([i[0] for i in data_absorb[k]])
	y_ab[k] = sc.array([i[-1] for i in data_absorb[k]])

	maximum = max(y_ab[k])	# auf "1" normieren
	y_ab[k] = y_ab[k]/maximum
	
	ax.plot(x_ab[k], y_ab[k], "-", color=spectral(int(col[k])), label=(str(col[k])+" nm"), linewidth=4)


                  
p.xlabel(u'Wellenlänge $\lambda\; [\\mathrm{nm}]$')
p.ylabel(u'normierte Intensität')
p.xlim(300,740)
p.ylim(0,1.2)

p.legend(loc='upper center', ncol=3)



# Speichern
p.gcf().set_size_inches(9, 6)
p.savefig("absorp-emit.pdf")


