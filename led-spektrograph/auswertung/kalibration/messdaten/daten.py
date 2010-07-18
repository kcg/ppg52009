#! /usr/bin/env python
# -*- coding: utf8 -*-


# Führt die Kalibration der Spektren durch.
# Alle Wellenlaengenbereiche der Eingbedaten muessen gleich sein


import pylab as pl
import scipy as sc
import scipy.interpolate as ip
import os
from math import *
from matplotlib import colors as clr
import random, colorsys



def readdata(filename, colsep="\t", comment="#"):
	'''
	reads floating-point data from a file
	'''
	ifile = open(filename, "r")
	data = []; l = 0
	for linetext in ifile.readlines():
		l += 1
		if linetext[0] == comment: continue
		linetext = linetext[:-1].strip()
		line = linetext.split(colsep)
		if len(line) <= 0: continue
		if line == ['']: continue
		row = []
		for i in line:
			try:
				x = float(i.replace(",", "."))
				row.append(x)
			except ValueError:
				print 'File "' + filename + '",',
				print 'line ' + str(l) + ':',
				print '"' + i + '" is not a float'
				row.append(0.)
		data.append(row)
	return(data)




# Dateien im Verzeichnis suchen
folder_in = '.'
filenames = []
for i in os.walk(folder_in):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if filenames[i][:3] != "neu":
		del filenames[i]
	else:
		i += 1

# Daten einlesen
I = []
for fname in filenames:
	data = readdata(folder_in + "/" + fname)
	I.append([i[1] for i in data[:16]])
I = sc.array(I)

I -= 24

#print I.mean(1) / I.mean()

# Normiere alle Messreihen auf gleichen Mittelwert
I2 = (I.T / I.mean(1)).T * I.mean()

means = I2.mean(0)


#print I2[:,14]
#print I2[:,15]

for i in range(len(means)):
	print '{0:.1f}'.format(means[i]),
	vals = I2[:,i]
	print '{0:.1f},'.format(sqrt(sum((vals - means[i])**2) / (len(vals) - 1.)))




