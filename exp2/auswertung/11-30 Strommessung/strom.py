#! /usr/bin/env python
# -*- coding: utf8 -*-

# Ermittung der des Generatorstromes in Abhängigkeit vom Magnetfeld

import pylab
import scipy
from math import *
from scipy import optimize


# Abstandsfunktion zwischen Modell und Daten
def linearfit(p, x, y):
	yw = [p[0] + p[1] * xx for xx in x]
	return [yw[i] - y[i] for i in range(len(x))]
def fitfunc2(p, x, y):
	yw = [p[0] * xx / (xx + p[1]) for xx in x]
	return [yw[i] - y[i] for i in range(len(x))]


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1].strip()
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


# Daten einlesen
data = readdata("11-30_strommessung.txt")
t = [i[0] for i in data]
U = [i[1] for i in data]
IS = [i[2] for i in data]
B = [i[3] for i in data]
RL = [i[4] for i in data]

# Zeitintervalle für Spannungsbereiche
# erst Zwei Intervalle für die Nullspannung, dann eines mit B-Feld an
ti = [
[44, 64, 164, 194, 83, 92],
[218, 229, 493, 544, 307, 322],
[629, 664, 1167, 1207, 870, 923],
[1324, 1365, 2187, 2336, 1752, 1909],
[2583, 3030, 3979, 4087, 3440, 3603],
[4434, 4518, 5326, 5428, 4786, 4959],
[5580, 5717, 6491, 6612, 6096, 6296],
[6786, 6966, 8150, 8274, 7540, 7854],
[8368, 8430, 8925, 9020, 8630, 8764],
[9058, 9106, 9483, 9507, 9254, 9368],
[9527, 9560, 9809, 9840, 9663, 9726]]
# nimm an, dass genau alle ganzzahligen Zeiten vorhanden sind
for i in range(1000):
	if i != t[i]:
		print i, t[i]

# Plot Rohdaten
ax = pylab.figure().add_subplot(111)
ax.plot(t, [B[i] / 100. for i in range(len(B))], "-", color="#00ff00", label=u"Magnetfeld $B\, [\mathrm{100mT}]$")
ax.plot(t, U, "b-", label=u"Spannung am Außenwiderstand $U\, [\mathrm{mV}]$")

# Auswertung für jeden Widerstandswert
R_out = [] # äußerer Widerstand pro Einstellung
dUdB = [] # Spannung zu B-Feld Verhältnis bei jedem Widerstand
for tt in ti:
	R_out.append(RL[tt[0]])
	t_fit = range(tt[0], tt[1]+1) + range(tt[2], tt[3]+1)
	U_fit = [U[i] for i in t_fit]
	B_fit = [B[i] for i in t_fit]
	pU, success = optimize.leastsq(linearfit, [0.,0.], args=(t_fit, U_fit))
	pB, success = optimize.leastsq(linearfit, [0.,0.], args=(t_fit, B_fit))
	ax.plot([t_fit[0], t_fit[-1]], [pU[0] + pU[1] * t_fit[0], pU[0] + pU[1] * t_fit[-1]], "r-")
	t_mess = range(tt[4], tt[5]+1)
	U_mess = [U[i] - (pU[0] + pU[1] * t[i]) for i in t_mess]
	B_mess = [B[i] - (pB[0] + pB[1] * t[i]) for i in t_mess]
	dUdB_mess = [U_mess[i] / B_mess[i] for i in range(len(U_mess))]
	dUdB.append(sum(dUdB_mess) / float(len(dUdB_mess)))

# Plot Rohdaten
pylab.xlabel(u"Zeit $t\,[\mathrm{s}]$")
pylab.legend(loc='lower right', numpoints=1)
pylab.ylim(-4.5, 2.5)
pylab.gcf().set_size_inches(7, 5)
pylab.savefig("rohdaten.pdf")

# Vorbereitung fuer Plots
pylab.rcParams['figure.subplot.left'] = 0.14
pylab.rcParams['figure.subplot.bottom'] = 0.12
pylab.rcParams['figure.subplot.top'] = 0.96



# Plot
pylab.clf()
ax = pylab.figure().add_subplot(111)

pU, success = optimize.leastsq(fitfunc2, [1.,1.], args=(R_out, dUdB))
print "Leerlaufspannung", pU[0], "mV"
print "Zellwiderstand", pU[1], "kOhm"
R_array = pylab.linspace(0., max(R_out), 40.)
B_array = [pU[0] * rr / (rr + pU[1]) for rr in R_array]
ax.plot(R_array, B_array, "k-", label='$(%.4f\,\\frac{\mathrm{mV}}{\mathrm{mT}} \cdot \\frac{R_L}{R_L+%.1f\,\mathrm{k\Omega}}$' % (pU[0], pU[1]))

ax.plot(R_out, dUdB, "bo", label=u"Messwerte")

pylab.ylim(0.0,0.025)
#ax.plot(B_array, fitfunc(ib, B_array), "-", color="#0099dd", label=u"Fit: $I\, [\mathrm{mA}] = %.4f \cdot B\, [\mathrm{mT}]$" % (ib[1],))
pylab.xlabel(u"Außenwiderstand $R\,[\mathrm{k\Omega}]$")
pylab.ylabel(u"Spannung am Außenwiderstand $U/B\, [\mathrm{mV/mT}]$")
pylab.legend(loc='lower right', numpoints=1)

# Speichern
pylab.gcf().set_size_inches(7, 4.5)
pylab.savefig("strom.pdf")

# Anzeigen
#pylab.show()


