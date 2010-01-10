# -*- coding:utf8 -*-

# Farbfunktionen

import pylab as pl


def spectral(lamb):
	'''
	Berechnet eine rgba-Farbe aus Wellenlängen
	'''
	l = [380., 400., 470., 535., 580., 650., 750.]
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



def show_spectrum():
	x = pl.linspace(370, 760, 760 - 370 + 1)
	y = [spectral(i) for i in x]
	for i in range(len(y)):
		a = y[i][3]
		y[i] = tuple(a * pl.array(y[i][:3]) + (1. - a) * pl.zeros(3))
	for i in range(len(x)):
		pl.plot(x[i], [0.], ".", color=y[i])
	pl.show()

