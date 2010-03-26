#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
from math import *
from scipy import optimize

import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..', 'python'))
from read_data import *



# Fitfunktion für die Winkelabhängigkeit der Potispannung
def winkel_von_U(p, x):
	return p[0] + p[1] * x + p[2] * (sqrt(1 + (p[3] * (x - p[4]))**2) - 1.)
	
def winkel_err(p, xlist, ylist):
	y = [winkel_von_U(p, x) for x in xlist]
	return [y[i] - ylist[i] for i in range(len(xlist))]


data_winkel = readdata("../messungen/2010-03-24/winkelmessungen/winkel-spannung-poti.txt")
w1 = [i[0] for i in data_winkel]
U1 = [i[1] for i in data_winkel]

# Winkelfunktion fitten
par1, success = optimize.leastsq(winkel_err, [-100., 300., -20., 6., .6], args=(U1, w1))
print par1
print "Messfehler", sqrt(sum([i**2 for i in winkel_err(par1, U1, w1)]) / (len(w1) - len(par1))), "grad"

interval = sc.linspace(.47, .83, 100)

pl.plot(interval, [winkel_von_U(par1, a) for a in interval] , "k-", label="Fit")
pl.plot(U1, w1, "bo", label="Messung")

# Speichern und zeichnen
pl.xlabel('Spannung $U$ in [V]')
pl.ylabel('Winkel $ \\alpha $ in [deg]')
pl.legend(loc='upper left')
pl.gcf().set_size_inches(6, 4)
pl.savefig("grafiken/spannung_winkel.pdf")
pl.show()
pl.clf()



