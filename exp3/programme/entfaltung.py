#! /usr/bin/env python
# -*- coding: utf8 -*-

'''
Enftaltet diskrete Funktionen
http://de.wikipedia.org/wiki/Faltung_(Mathematik)

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
Wir brauchen noch was besseres!
Vielleicht reicht SVD, ansonsten vielleicht maximum likelihood
'''


import pylab
import scipy as sc
import scipy.linalg as la
from math import *



def entfalte (x, b, f):
	'''
	x: Messstellen
	b: gemessene Werte
	f: Faltungsfunktion (muss nicht normiert sein)
	gibt den entfalteten Punktvektor a zurück
	'''

	n = len(x)
	norm = sum([f(xi) for xi in x])
	
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



def falte (x, a, f):
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
		b[i] = sc.sum(sc.dot(a, F)) / sc.sum(F)
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
	a = sc.sin(3*x)
	pylab.plot(x,a,"bo-",label="original", markersize=8.5, markeredgewidth=0.5)

	# Faltungskern
	f = lambda x: exp(-(2.1*x)**2)

	# Falte die Funktion!
	b = falte(x, a, f)
	pylab.plot(x, b, "ro-", label="gefaltet")

	# Entfalte die Funktion wieder!
	c = entfalte(x, b, f)
	pylab.plot(x, c, "o-", color="#00ff00", label="entfaltet")

	pylab.legend(loc="center right")
	pylab.show()


test1()

