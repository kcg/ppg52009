#! /usr/bin/env python
# -*- coding: utf8 -*-

'''
Enftaltet diskrete Funktionen
http://de.wikipedia.org/wiki/Dekonvolution

Anwendung:
Nimmt man ein verschmiertes Signal auf, also zum Beispiel ein unscharfes
Spektrum, so misst man nicht das Originalspektrum, sondern eine Faltung
des Spektrums mit einer Verbreiterungsfunktion. Wenn man dies nun als Matrix
hinschreibt und invertiert, so erhält man die Originalfunktion zurück.
Dabei werden allerdings auch statistische Fehler verstärkt.
'''

'''
Stand der Dinge:
-Der naive Matrizeninvertierungsalgorithmus wird schnell instabil
-Wir brauchen auf jeden Fall was besseres!
-SVD ist auch nicht viel besser.
-Wiener Deconvolution scheint zu klappen, jedoch muss man da die Parameter gut einstellen. Vielleicht ist es besser, die
Fouriertrafo gleich auf den ungleich gebinnten
Originaldaten auszuführen.
-Matrixinversion mit Quadratabstandsminimierung geht nun auch recht gut
-biser am Besten: Matrixminimierung mit Welligkeitsminimierung
'''


import pylab
import scipy as sc
import scipy.linalg as la # lineare algebra
from scipy import dot
from math import *
import scipy.fftpack as ft # fourier transformation
import scipy.interpolate as ip
import scipy.optimize as op
import random
import time



def rebin(x, b, dx):
	'''
	Binnt Daten b von beliebigen Rastern x
	auf ein gleichmäßiges Raster mit Abstand dx
	mit Hilfe von Splines
	'''
	# sortieren
	xb = [[x[i], b[i]] for i in range(len(x))]
	xb.sort()
	xs = [i[0] for i in xb]
	bs = [i[1] for i in xb]

	# neue x-Werte
	x0 = ceil(xs[0] / dx)
	x1 = floor(xs[-1] / dx)
	xnew = sc.linspace(x0 * dx, x1 * dx, 1 + x1 - x0)

	# Spline Interpolation
	tck = ip.splrep(xs, bs, k=min(3, len(xs)-1))
	bnew = ip.splev(xnew, tck, der=0)
	return xnew, bnew



def entfalte_matrix (x0, b0, f, dx, k=[1., 0.], l=[]):
	'''
	x: Messstellen
	b: gemessene Werte
	f: Faltungsfunktion (muss nicht normiert sein)
	dx: Abstand der neuen x-Werte
	k: Array der Gewichtungen von Entfaltung und Abstand
	l: Array der Gewichtungen der Anteile n-ter Ordnung
	gibt den entfalteten Punktvektor a zurück
	'''

	if dx > 0.:
		x, b = rebin (x0, b0, dx)
	else:
		x, b = x0, b0
		dx = (x[-1] - x[0]) / (len(x) - 1.)
	n = len(x)
	# gehe von gleichmäßig gebinnten Daten aus

	t1 = time.time()
	# Matrix der f-Differenzen A_{ij} = f(x_j - x_i) * delta_x
	d = sc.array([f(dx * (i - n + 1)) for i in range(2 * n - 1)])
	A = sc.array([d[n-i-1:2*n-i-1] for i in range(n)])

	# Polynomkoeffizient-Extraktionsvektoren
	# Multipliziert man einen dieser Vektoren mit einem Punktvektor,
	# dann erhält man eine Zahl proportional zum Term (n-1)-ter
	# Ordnung im Entwicklungspolynom
	# quasi "diskrete Taylorentwicklung"
	c = [	[-1., .5],
		[1., -2/3., 1/6.],
		[-1., .75, -.3, .05],
		[1., -.8, .4, -4/35., 1/70.],
		[-1., 5/6., -10/21., 5/28., -5/126., 1/252.]]
	t2 = time.time()
	# Randwerte kontrollieren
	R = sc.zeros((n,n))
	wert0 = n; steigung0 = n / 2.
	R[0][0] = R[-1][-1] = wert0 + steigung0
	R[0][1] = R[-1][-2] = -steigung0

	# erster Term: A^T * A * a = A^T * b
	# Andere Terme beschränken die Fluktiationen
	AA = k[0] * dot(A.T, A) + k[1] * sc.eye(n) + k[0] * dot(R.T, R)
	bb = k[0] * dot(A.T, b) + k[1] * b
	for i in range(len(l)):
		L = sc.zeros((n,n));
		for j in range(i+1,n-(i+1)):
			for ii in range(-(i+1), (i+2)):
				L[j][j+ii] = c[i][abs(ii)]
		AA += l[i] * dot(L.T, L)
	t3 = time.time()
	a = la.solve(AA, bb)
	t4 = time.time()
	#print "timing:", (t2-t1)/(t4-t1), (t3-t2)/(t4-t1), (t4-t3)/(t4-t1)
	return x, a



def wiener_deconvolution (x, b, f, dx):
	'''
	x: Messstellen
	b: Messwerte Array
	nsr: noise-to-signal-ratio, array in Abhängigkeit von f
	f: Faltungsfunktion (muss nicht normiert sein)
	dx: neuer Abstand fürs äquidistante rebinning
	gibt den geschätzten Originalvektor a zurück
	'''

	xnew, bnew = rebin(x, b, dx)

	# Faltungsfunktion in den Frequenzraum transformieren
	# die Berechnung von h ist evtl falsch !
	h = sc.array([f(xi - xnew[0]) + f(xi - xnew[-1] - dx)
					for xi in xnew])
	h = h / h.sum()
	H = ft.fft(h)

	# noise to signal ratio: größer bei hohen frequenzen
	#nsr = sc.array([1e-6*i**1. for i in range(len(xnew))])
	nsr = sc.array([5e-4*i for i in range(len(xnew))])
	# nimm als Schätzung ein Standard-rauschen
	#nsr = ft.fft(0.002 * sc.random.standard_normal((len(xnew),)))

	# Wiener Filter im Frequenzraum
	G = H / (H * H.conj() + nsr)
	A = G * ft.fft(bnew)
	a = ft.ifft(A)

	# Rücktransformation auf x mit Splines
	tck = ip.splrep(xnew, a, k=min(3, len(x)-1))
	anew = ip.splev(x, tck, der=0)

	return x, anew




def falte (x, g, f, xf):
	'''
	x: Messstellen
	g: Originalfunktion
	f: Faltungsfunktion (muss nicht normiert sein), aber integrabel
	dx: ungefähre Breite von f
	gibt den gefalteten Punktvektor b zurück
	sinnvoll für Tests
	'''

	yf = [f(xi) for xi in xf]
	# normieren
	yf = sc.array(yf) / sum(yf)

	b = sc.zeros(len(x))
	# Faltung ausführen
	for i in range(len(x)):
		b[i] = sum([yf[j] * g(x[i] + xf[j]) for j in range(len(xf))])
	return b




def falte_diskret (x, a, f):
	'''
	x: Messstellen
	a: Originalwerte
	f: Faltungsfunktion (muss nicht normiert sein)
	gibt den gefalteten Punktvektor b zurück
	sinnvoll für Tests
	'''

	# Initialisieren
	n = len(x)
	b = sc.zeros(n)
	for i in range(n):
		# Funktion der Abstände
		F = sc.array([f(x[i] - x[j]) for j in range(n)])
		# b_i = \sum_j a_j * f(x_i - x_j)  (+normiere F)
		b[i] = sc.sum(dot(a, F)) / sc.sum(F)
	return b



def fun (x):
	'''
	Testfunktion
	[0,7]
	'''
	if x <= 3.:
		return exp(-(3.*(x-2.))**2) - .2*exp(-(8.*(x-2.1))**2)
	elif x <= 6.:
		return -53./360*(x-3.)**5 + 31./36*(x-3.)**4 - 151./120*(x-3.)**3
	else:
		return 0.



def test1():
	'''
	Testweise Hin- und Rücktransformation einer Funktion
	Fazit: bei breiter Faltungsfunktion instabil
	=> es entstehen Oszillationen
	'''
	# Ungleiche x-Wert Verteilung
	x = [0., 0.02]
	while x[-1] < 6.9:
		dx = 0.
		while dx < 0.002 or dx > 0.09:
			dx = random.gauss(x[-1]-x[-2], 0.02)
		x.append(x[-1] + dx)
	x = sc.array(x)

	# Beispielfunktion
	a = sc.array([fun(xi) for xi in x])
	pylab.plot(x,a,"bo-",label="original", markersize=8, markeredgewidth=0.5)

	# Faltungskern
	f = lambda x: exp( -( 2.5 * (x) )**4 ) - 0.4*exp( -( 16.0 * (x) )**4 )

	pylab.plot(sc.linspace(1.,3., 161), [f(i-2.)-1.1 for i in sc.linspace(1.,3., 161)], "-", color="#00ffff", label="Faltungskern")

	# Falte die Funktion!
	#b = falte_diskret(x, a, f)
	b = falte(x, fun, f, sc.linspace(-2., 2.,81))

	# Rauschen hinzufügen
	b = b + 0.003 * sc.random.standard_normal((len(b),))
	pylab.plot(x, b, "ro-", label="gefaltet + noise", markersize=5)

	# Entfalte die Funktion wieder!

	# Wiener deconvolution
	xnew, d = wiener_deconvolution (x, b, f, 0.023)
	#pylab.plot(xnew, d, "o-", color="#00ff00", label="Wiener Deconvolution", markersize=5)

	# Lösung mit Matrix Inversion
	x2, c = entfalte_matrix (x, b, f, 0.04, [1., 0.05])
	#pylab.plot(x2, c, "o-", color="#ffff00", label="mat-inv", markersize=5)
	x2, c = entfalte_matrix (x, b, f, 0.04, [1., 0.001], [1.])
	#pylab.plot(x2, c, "o-", color="#ffc000", label="mat-inv2", markersize=5)
	x2, c = entfalte_matrix (x, b, f, 0.04, [1., 0.], [0., 50.])
	pylab.plot(x2, c, "o-", color="#ff00ff", label="mat-inv3", markersize=5)

	pylab.ylim(-1.3, 1.2)
	pylab.legend(loc="upper right")
	pylab.show()



test1()


