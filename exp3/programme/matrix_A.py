#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
import os
from math import *
import scipy.interpolate
from matplotlib import colors as clr
import matplotlib.cm as cm



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

fpath = "../gui/led_spektren"
# Dateien im Verzeichnis suchen
filenames = []
for i in os.walk(fpath):
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


j = 0
S = []
for k in range(len(filenames)):
	fname = filenames[k]
	data = readdata(fpath + "/" + fname)
	U = [i[0] for i in data]
	I = [i[1] for i in data]

	S.append(sc.array(I) / max(I))

# sortieren nach Schwerpunkt der Kurven
xm = []
for s in S:
	sum1 = 0.; sum2 = 0.
	for i in range(len(s)):
		sum1 += i * s[i]
		sum2 += s[i]
	xm.append(sum1 / sum2)

permut = sc.array(xm).argsort()
A = []
for i in permut:
	A.append(S[i])
A = sc.array(A)

# Plotten
pl.rcParams['figure.subplot.left'] = 0.1
pl.rcParams['figure.subplot.right'] = 1.0
pl.rcParams['figure.subplot.bottom'] = 0.125
pl.rcParams['figure.subplot.top'] = 0.96

pl.imshow(A, aspect="auto", interpolation="nearest", cmap=cm.gray)

pl.xticks(range(0, len(A[0]), 50), [350 + i for i in range(0, len(A[0]), 50)])
pl.xlabel(u"$\lambda\; [\mathrm{nm}]$")
pl.ylabel(u"LED Nummer")
pl.colorbar(fraction=.08, pad=.04)
pl.gcf().set_size_inches(7, 3.5)
pl.savefig("matrix_A.pdf")
#pl.show()


