#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc


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



# Spektralfarben
def spectral(lamb):
	'''
	Berechnet eine rgba-Farbe aus Wellenlängen
	'''
	l = [350., 400., 450., 535., 580., 650., 750.]
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



# erste Version
a = pl.subplot(111)
for lampe in ["LED", "halogen"]:
	lampe_data = readdata("kalibrationsspektrum/" + {"halogen":"halogen", "LED":"kalibrationsspek"}[lampe] + ".dat")
	k = 0
	if lampe == "LED":
		k = 1
	lampe_lambda = sc.array([i[0+k] for i in lampe_data])
	lampe_I = sc.array([i[1+k] for i in lampe_data])
	lampe_I /= max(lampe_I)
	a.plot(lampe_lambda, lampe_I, "k-", linewidth=5)
	for i in range(1, len(lampe_lambda)):
		c1 = spectral(lampe_lambda[i-1])
		c2 = (c1[0] * c1[3], c1[1] * c1[3], c1[2] * c1[3])
		if lampe_lambda[i] >= 350. and lampe_lambda[i-1] <= 750.:
			a.plot(lampe_lambda[i-1:i+1], lampe_I[i-1:i+1], "-", linewidth=2, color=c2)


a.annotate(u'Weiße LED', xy=(630, 0.15), horizontalalignment='left', verticalalignment='bottom', fontsize=16)
a.annotate(u'Halogenlampe', xy=(630, 0.8), horizontalalignment='left', verticalalignment='bottom', fontsize=16)
pl.title(u"Weißlichtquellen")
pl.xlim(250, 850)
pl.ylim(0, 1.1)
pl.xlabel(u"Wellenlänge [nm]")
pl.ylabel(u"Intensität")

pl.gcf().set_size_inches(7, 5)
pl.savefig("quellspektren.pdf")


# zweite Version
a = pl.subplot(111)

lampe_lambda = None; lampe_I = {}

# farbiger Hintergrund
for lampe in ["LED", "halogen"]:
	lampe_data = readdata("kalibrationsspektrum/" + {"halogen":"halogen", "LED":"kalibrationsspek"}[lampe] + ".dat")
	k = 0
	if lampe == "LED":
		k = 1
	lampe_lambda = sc.array([i[0+k] for i in lampe_data])
	lampe_I[lampe] = sc.array([i[1+k] for i in lampe_data])
	lampe_I[lampe] /= max(lampe_I[lampe])
	
for i in range(1, len(lampe_lambda)):
	c1 = spectral(lampe_lambda[i-1])
	x1 = 1.
	x2 = .65
	c2 = tuple(1.+x1*(1.+c1[3]*(sc.array(c1[:3])-1.)-1.))
	c3 = tuple(1.+x2*(1.+c1[3]*(sc.array(c1[:3])-1.)-1.))
	if lampe_lambda[i] >= 350. and lampe_lambda[i-1] <= 750.:
		a.plot(2 * [lampe_lambda[i]], [0., min(lampe_I["LED"][i], lampe_I["halogen"][i])], "-", linewidth=1.1, color=c2)
		a.plot(2 * [lampe_lambda[i]], [min(lampe_I["LED"][i], lampe_I["halogen"][i]), max(lampe_I["LED"][i], lampe_I["halogen"][i])], "-", linewidth=1.1, color=c3)

# schwarze Konturen
for lampe in ["LED", "halogen"]:
	lampe_data = readdata("kalibrationsspektrum/" + {"halogen":"halogen", "LED":"kalibrationsspek"}[lampe] + ".dat")
	k = 0
	if lampe == "LED":
		k = 1
	lampe_lambda = sc.array([i[0+k] for i in lampe_data])
	lampe_I = sc.array([i[1+k] for i in lampe_data])
	lampe_I /= max(lampe_I)
	a.plot(lampe_lambda, lampe_I, "k-", linewidth=5)


a.annotate(u'Weiße LED', xy=(630, 0.15), horizontalalignment='left', verticalalignment='bottom', fontsize=16)
a.annotate(u'Halogenlampe', xy=(630, 0.8), horizontalalignment='left', verticalalignment='bottom', fontsize=16)
pl.title(u"Weißlichtquellen")
pl.xlim(250, 850)
pl.ylim(0, 1.1)
pl.xlabel(u"Wellenlänge [nm]")
pl.ylabel(u"Intensität")

pl.gcf().set_size_inches(7, 5)
pl.savefig("quellspektren2.pdf")


