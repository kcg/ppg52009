# -*- coding:utf8 -*-

# Berechnet das komplette Spektrum aus Messsignalen

from math import *
import scipy as sc
import scipy.linalg as la
import scipy.optimize as op
import scipy.special as sp
from scipy import dot
from file_parse import *


class DataSpectral():
	def __init__ (self):

		# lies die LED Sensitivitäten in den Arbeitsspeicher 
		leds = ["led14mCd-1.dat", "led44kmCd-1.dat", "led500-505nm-1.dat",
		"led525nm-1.dat", "led585-590nm-1.dat", "led570nmGruenH-1.dat",
		"led588nm-1_1.dat", "led600-610nm-1.dat", "led620nm-1.dat",
		"led635nm-1.dat", "led625-630nm-1.dat", "led640nm-1.dat"]
		self.n = len(leds)
		A = []
		for led in leds:
			data = readdata("led_spektren/" + led)
			A.append([i[1] for i in data])		
		self.m = len(A[0])

		# Wellenlängen
		self.lambdas = sc.array([i[0] for i in readdata("led_spektren/" + leds[0])])
		# Aborptionskurven
		self.A = sc.array(A)
		self.AT = self.A.T
		self.ATA = dot(self.AT, self.A)

		# Pseudoinverse
		self.PINV = la.pinv(A)

		# Glättungskern
		S = -sc.eye(self.m);
		S[0][0] = S[-1][-1] = 0.
		for i in range(1, self.m-1):
			S[i][i-1] = S[i][i+1] = .5
		self.STS = dot(S.T, S)




	def spectrum_leastsqr(self, input_signal, smoothing=1e4):
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
		return la.solve(self.ATA + smoothing * self.STS,
			dot(self.AT, input_signal))



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
		p, success = op.leastsq(err, [1e16, 1e5], args=(input_signal,), maxfev=1800)
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
