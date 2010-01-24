# -*- coding:utf8 -*-

# Berechnet das komplette Spektrum aus Messsignalen

import time
from math import *
import scipy as sc
import scipy.linalg as la
import scipy.optimize as op
import scipy.special as sp
import scipy.interpolate as ip
from scipy import dot
from file_parse import *


class DataSpectral():
	def __init__ (self):

		# lies die LED Sensitivitäten in den Arbeitsspeicher 
		leds = ["led375nm-1_1-h.dat", "led395nm-1_1-h.dat", "led465-470nm-1_2-h.dat", "led480nm-1_1-h.dat", "led500-505nm-1_1-h.dat", "led505nm-1_1-h.dat", "led515nm-1_1-h.dat", "led525nm-1_1-h.dat", "led540nm-2_1-h.dat", "led585-590nm-1_1-h.dat", "led588nm-1_1-h.dat", "led600-610nm-1_1-h.dat", "led620nm-1_1-h.dat", "led625-630nm-1_1-h.dat", "led635nm-1_1-h.dat", "led640nm-1_3-h.dat"]

		self.names = [i[3:-4] for i in leds]

		self.n = len(leds)
		A = []
		for led in leds:
			data = readdata("led_spektren/" + led)
			A.append([i[1] for i in data])
		A = sc.array(A)

		# Wellenlängen
		lambdas = [i[0] for i in readdata("led_spektren/" + leds[0])]

		# Binning vergrößern -> schnellere Berechnung
		bin = 7
		B = []; l = []
		for i in range(len(lambdas) / bin):
			l.append(sum(lambdas[bin * i:bin * (i + 1)]) / float(bin))
			B.append(sc.reshape(sc.mean(A[:,bin * i:bin * (i + 1)], 1), (self.n, 1)))
		A = sc.concatenate(tuple(B), 1)

		self.lambdas = sc.array(l)
		self.m = len(self.lambdas)

		# Absorptionskurven
		self.A = sc.array(A)
		self.weights = self.A.sum(1)
		self.led_colors = dot(self.A, self.lambdas) / self.weights

		# Rechne ein paar aufwändige Sachen aus, die wir später öfters brauchen
		self.AT = self.A.T
		self.ATA = dot(self.AT, self.A)
		# Singulärwertzerlegung
		self.SVD  = la.svd(A)
		# Pseudoinverse
		self.PINV = la.pinv(A)
		# Glättungskern
		self.S = .5 * (sc.eye(self.m-2, self.m, 0) + sc.eye(self.m-2, self.m, 2))
		self.S -= sc.eye(self.m-2, self.m, 1)
		self.STS = dot(self.S.T, self.S)




	def spectrum_leastsqr(self, input_signal, smooth=.5):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)

		löst die Matrizengleichung:
		sensitivities * spectrum = input_signal
		mit dem least-squares Ansatz:
		AT * A * x = AT * b
		nach x;
		und schätzt somit das gesamte Spektrum anhand der Messwerte:
		Rückgabe: das Spektrum als Vektor
		'''

		# Vorsicht! Offensichtlich ist das numerisch instabil!
		#return la.solve(self.ATA + smoothing * self.STS,
		#	dot(self.AT, input_signal))
		# etwas stabiler aber langsamer:
		smooth = smooth**4 / (smooth**4 + (1. - smooth)**4)
		return dot(la.pinv(self.ATA * (1. - smooth) + smooth * self.m * self.STS),
			dot(self.AT * (1. - smooth), input_signal))



	def spectrum_pinv(self, input_signal):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		Berechnet die Lösung mit der Pseudoinversen
		Rückgabe: das Spektrum als Vektor
		'''

		return dot(self.PINV, input_signal)



	def spectrum_blackbody(self, input_signal, temp_output):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		temp_output: Rückgabe der Temperatur

		sucht ein Schwarzkörperspektrum, das gut aufs Signal passt
		'''

		h = 6.6261e-34
		c = 2.9979e8
		k = 1.3807e-23
		# p = [faktor, Temperatur]
		def I(p, l):
			return p[0] * l**(-5.) / (sc.exp(h * c / ((l / 1e9) * k * abs(p[1]))) - 1.)
		def err(p, signal):
			return dot(self.A, I(p, self.lambdas)) - signal

		# TODO: Startwerte müssen vorberechnet werden
		# sonst konvergierts oft nicht
		p, success = op.leastsq(err, [1e16, 8e4], args=(input_signal,), maxfev=2000)
		temp_output[0], temp_output[1] = p[0], abs(p[1])
		return I(p, self.lambdas)



	def spectrum_polynomial(self, input_signal):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)

		entwickelt das Signal nach Polynomen
		dies erzielt in der unmodifizierten Form kaum ein gutes Resultat
		'''

		# Benutze Legendre-polynome.
		# Prinzipiell könnte man auch sonst welche nehmen,
		# aber so ist es numerisch stabiler
		P = sc.zeros((self.m, self.n))
		# das Befüllen der Matrix kommt mir noch etwas ineffizient vor ...
		for j in xrange(self.n):
			poly = sp.legendre(j)
			for i in xrange(self.m):
				P[i][j] = poly(2. * (i + .5) / self.m - 1.)
		# Errechne Polynomkoeffizienten p
		p = la.solve(dot(self.A, P), input_signal)
		# Entferne Terme höherer Ordnung
		# (das geht nur weil unsere Polynome orthogonal sind)
		#for i in range(self.n / 2, self.n): p[i] = 0.

		return dot(P, p)



	def spectrum_spline(self, input_signal, k=3):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)

		entwickelt das Signal in einen Spline vom Grad k
		'''

		P = sc.zeros((self.m, self.n))
		for j in xrange(self.n):
			e = sc.zeros(self.n)
			e[j] = 1.
			spline = ip.splrep(sc.linspace(self.lambdas[0], self.lambdas[-1], self.n), e, k=min(k, self.n-1))
			for i in xrange(self.m):
				P[i][j] = ip.splev(self.lambdas[i], spline)
		# Errechne Koeffizienten p
		p = la.solve(dot(self.A, P), input_signal)

		return dot(P, p)


	def spectrum_smooth(self, input_signal):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		erzeugt eine exakte Lösung mit minimaler Gesamtkrümmung
		(analog zur Pseudoinversen, die minimale Gesamtnorm erzeugt)
		funktioniert nur mit m >= n
		'''

		# Eine spezielle Lösung:
		l = dot(self.PINV, input_signal)
		# Lösungen der homogenen Gleichung
		L = self.SVD[2][self.n:, :].T
		# ziehe von der speziellen Lösung eine Linearkombination der
		# homogenen Lösungen so ab, dass damit die Krümmung minimiert wird
		return l - dot(L, la.lstsq(dot(self.S, L), dot(self.S, l))[0])



	def spectrum_optimize(self, input_signal, smooth=.5):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		erzeugt eine Näherungslösung
		dabei wird versucht, nicht unter 0 zu kommen,
		das Eingangssignal gut nachzubilden,
		und eine Glatte Kurve zu erzeugen
		'''

		smooth = smooth**2 / (smooth**2 + (1. - smooth)**2)
		def err(s):
			err_signal = (((dot(self.A, s) - input_signal) / self.weights)**2).mean() * s.mean()
			err_zero = ((sc.absolute(s) - s) ** 2).mean() / 4.
			err_smooth = ((s[1:-1] - .5 * (s[2:] + s[:-2])) ** 2).mean()
			return smooth * err_smooth + (1. - smooth) * (err_signal) + err_zero

		spectrum = op.fmin_bfgs(err, self.spectrum_smooth(input_signal), disp=0)

		return spectrum



