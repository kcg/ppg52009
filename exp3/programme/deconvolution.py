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
Der naive Matrizeninvertierungsalgorithmus wird schnell instabil
Wir brauchen auf jeden Fall was besseres!
SVD ist auch nicht viel besser.
Vielleicht kommen wir mit sowas wie "maximum likelihood" weiter
Wahrscheinlich ist die Wiener Entfaltung recht gut

Nach oder beim Entfalten sollten wir die Kurven vielleicht noch
glätten, wenn sie statistisch streuen.
'''


import pylab
import scipy as sc
import scipy.linalg as la # lineare algebra
from scipy import dot
from math import *
import scipy.fftpack as ft # fourier transformation


def entfalte (x, b, f):
	'''
	x: Messstellen
	b: gemessene Werte
	f: Faltungsfunktion (muss nicht normiert sein)
	gibt den entfalteten Punktvektor a zurück
	'''

	n = len(x)
	
	# b_i = \sum_j f(x_j - x_i) * a_j
	# b = A_{ij} * a
	# a = A_{ij}^{-1} * b

	# Matrix der x-Differenzen D_{ij} = x_j - x_i
	A = sc.array([[f(x[i] - x[j]) #
		for j in range(n)] for i in range(n)])
	# Zeilen normieren
	s = sc.sum(A, axis=1)
	for i in range(n):
		for j in range(n):
			A[i][j] /= s[i]

	a = la.solve(A, b)
	return a



def entfalte_svd (x, b, f):
	'''
	x: Messstellen
	b: gemessene Werte
	f: Faltungsfunktion (muss nicht normiert sein)
	gibt den entfalteten Punktvektor a zurück
	'''

	n = len(x)
	
	# b_i = \sum_j f(x_j - x_i) * a_j
	# b = A_{ij} * a
	# a = A_{ij}^{-1} * b

	# Matrix der x-Differenzen D_{ij} = x_j - x_i
	A = sc.array([[f(x[i] - x[j]) #
		for j in range(n)] for i in range(n)])
	# Zeilen normieren
	s = sc.sum(A, axis=1)
	for i in range(n):
		for j in range(n):
			A[i][j] /= s[i]

	svdA = la.svd(A)
	# Matrizen(pseudo)inversion mit der Singulärwertzerlegung
	a = dot(b, dot(dot(svdA[0], sc.eye(n) / svdA[1]), svdA[2]))
	return a



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



def wiener_deconvolution (x, b, f, dx):
	'''
	x: Messstellen
	b: Messwerte Array
	nsr: noise-to-signal-ratio, array in Abhängigkeit von f
	f: Faltungsfunktion (muss nicht normiert sein)
	dx: neuer Abstand fürs äquidistante rebinning
	gibt den geschätzten Originalvektor a zurück

	bisher noch total verbuggt!
	'''

	# äquidistantes Binning
	xnew = sc.linspace(ceil(x[0]/dx)*dx, floor(x[-1]/dx)*dx,
				1 + floor(x[-1]/dx) - ceil(x[0]/dx))

	# erstmal nur testweise: linear interpolieren
	# simpel und ineffizient
	bnew = []
	for i in range(len(xnew)):
		j = 0; j0 = 0; j1 = 0
		while j < len(x) and x[j] <= xnew[i]:
			j0 = j
			j += 1
		j = max(0,j-1)
		while x[j] < xnew[i]:
			j += 1
			j1 = j
		if x[j0] == x[j1]:
			bnew.append(b[j0])
		else:
			bnew.append((b[j0] * (x[j1] - xnew[i]) +
			b[j1] * (xnew[i] - x[j0])) / (x[j1] - x[j0]))
	
	# Faltungsfunktion in den Frequenzraum transformieren
	# die Berechnung von h ist noch falsch !!
	h = sc.array([f(xi - xnew[0] - 0.5*dx) + f(xnew[-1] - xi + 0.5*dx)
					for xi in xnew])
	h = h / h.sum()
	H = ft.fft(h)

	# noise to signal ratio: größer bei hohen frequenzen
	nsr = sc.array([5e-4*i**1 for i in range(len(xnew))])
	# Wiener Filter im Frequenzraum
	G = H.conj() / (H * H.conj() + nsr)
	A = G * ft.fft(bnew)

	return xnew, ft.ifft(A)



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




def test1():
	'''
	Testweise Hin- und Rücktransformation einer Funktion
	Fazit: bei breiter Faltungsfunktion instabil
	=> es entstehen Oszillationen
	'''
	# Ungleiche x-Wert Verteilung
	x = sc.concatenate((sc.linspace(1,2,5), sc.linspace(2.1,4,20), sc.linspace(4.3,5,3)), axis=0)

	# Beispielfunktion
	a = sc.sin(2*x + 0.4*x**2) * (2. - 0.3 * x)
	pylab.plot(x,a,"bo-",label="original", markersize=9, markeredgewidth=0.5)

	# Faltungskern
	f = lambda x: exp( -( 6. * (x) )**2 )


	# Falte die Funktion!
	#b = falte_diskret(x, a, f)
	b = falte(x, lambda x: sin(2.*x+0.4*x**2) * (2. - 0.3 * x), f, sc.linspace(-2., 2.,81))
	pylab.plot(x, b, "ro-", label="gefaltet")

	# Entfalte die Funktion wieder!

	# primitive Inversion
	c = entfalte(x, b, f)
	pylab.plot(x, c, "o-", color="#00ff00", label="mat-inv")

	# wiener deconvolution
	xnew, d = wiener_deconvolution (x, b, f, 0.043)
	pylab.plot(xnew, d, "o-", color="#ffff00", label="wiener")

	pylab.ylim(-1.5, 1.5)
	pylab.legend(loc="lower right")
	pylab.show()





test1()

