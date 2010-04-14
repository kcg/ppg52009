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
folder_in = 'spektren_alt'
filenames = []
for i in os.walk(folder_in):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if filenames[i][-4:] != ".dat":
		del filenames[i]
	else:
		i += 1
# Dateinamen muessen in alphabetischer Reihenfolge stehen
filenames.sort()

# Daten einlesen
lam = []
I = []
for fname in filenames:
	data = readdata(folder_in + "/" + fname)
	lam = [i[0] for i in data]
	I.append([i[1] for i in data])
lam = sc.array(lam)
I = sc.array(I)
# Die Eingabedaten stehen jetzt in zwei Matrizen

# Erzeuge das theoretische Spektrum
I_theo = None
while True:
	data = readdata("theoretisches_spektrum.dat")
	x = [i[0] for i in data]
	y = [i[1] for i in data]
	spline = ip.splrep(x, y, k=min(3, len(x)-1))
	I_theo = ip.splev(lam, spline)
	break

# Welche theoretischen Signale wuerde man mit den Kurven erhalten ?
signal_theo = sc.dot(I, I_theo)

# lies das tatsaechliche Signal
signal_mess = None
while True:
	data = readdata("mess_signal.dat")
	signal_mess = sc.array([i[0] for i in data])
	break


# Skaliere die Spektren um
for i in range(I.shape[0]):
	I[i] *= signal_mess[i] / signal_theo[i]

# Normiere alle Spektren gemeinsam
# Das absolute Maximum wird 1 gesetzt
I /= I.max()


# Schreibe die neuen Spektren
folder_out = 'spektren_neu'
for fname, i in zip(filenames, range(len(filenames))):
	ofile = open(folder_out + "/" + fname, "w")
	ofile.write('# absorption spectrum of LED "' + fname[:-4] + '"\n')
	ofile.write('# column 1: wavelength [nm]\n')
	ofile.write('# column 2: intensity in arbitrary units')
	for j in range(len(lam)):
		ofile.write("\n{0}\t{1:.6f}".format(lam[j], I[i, j]))
	ofile.close()

