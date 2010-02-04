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
from color_spectral import spectral


class DataSpectral():
	def __init__ (self):

		# lies die LED Sensitivitäten in den Arbeitsspeicher
		ledlist = readdata("led_spektren/list.dat", getFloats=False)
		leds = [i[0] for i in ledlist]
		self.led_label = [i[1] for i in ledlist]
		self.names = [i[3:-4] for i in leds]

		self.n0 = len(leds)
		A = []
		for led in leds:
			data = readdata("led_spektren/" + led)
			A.append([i[1] for i in data])
		A = sc.array(A)

		# Wellenlängen
		lambdas = [i[0] for i in readdata("led_spektren/" + leds[0])]

		# Binning vergrößern -> schnellere Berechnung
		bin = 5
		B = []; l = []
		for i in range(len(lambdas) / bin):
			l.append(sum(lambdas[bin * i:bin * (i + 1)]) / float(bin))
			B.append(sc.reshape(sc.mean(A[:,bin * i:bin * (i + 1)], 1), (self.n0, 1)))
		A = sc.concatenate(tuple(B), 1)

		self.lambdas = sc.array(l)
		self.m = len(self.lambdas)
		self.use = range(self.n0)

		# Absorptionskurven
		self.A0 = sc.array(A)
		self.weights = self.A0.sum(1)
		self.led_colors = dot(self.A0, self.lambdas) / self.weights
		self.print_colors0 = []
		for i in range(len(self.led_label)):
			try:
				j = float(self.led_label[i][0:3])
				self.print_colors0.append(spectral(j))
			except ValueError:
				self.print_colors0.append(spectral(self.led_colors[i]))

		# Dunkel- und Hellbild laden
		self.dark = sc.zeros(self.n0)
		self.bright = self.weights
		try:
			dark_dat = readdata("led_spektren/dark.dat")
			dark = [i[0] for i in dark_dat]
			if len(dark) == self.n0:
				self.dark = dark
				print "darkframe loaded"
		except IOError:
			pass
		try:
			bright_dat = readdata("led_spektren/bright.dat")
			bright = [i[0] for i in bright_dat]
			if len(bright) == self.n0:
				self.brigh = bright
				print "brightframe loaded"
		except IOError:
			pass

		self.make_matrices()

		# Glättungskern
		self.S = .5 * (sc.eye(self.m-2, self.m, 0) + sc.eye(self.m-2, self.m, 2))
		self.S -= sc.eye(self.m-2, self.m, 1)
		self.STS = dot(self.S.T, self.S)



	def make_matrices(self):
		A = self.A0.copy()
		self.print_colors = self.print_colors0[:]
		for i in range(self.n0):
			A[i, :] *= (self.bright[i] - self.dark[i]) / sum(A[i, :])
			if self.use.count(i) == 0:
				# Balkenfarbe entsättigen
				mean = sum(self.print_colors0[i]) / 3.
				self.print_colors[i] =  tuple([.3 * self.print_colors0[i][j] + .7 * mean for j in range(3)])
		self.A = A[self.use, :]
		self.n = self.A.shape[0]

		# Rechne ein paar aufwändige Sachen aus, die wir später öfters brauchen
		self.AT = self.A.T
		self.ATA = dot(self.AT, self.A)
		# Singulärwertzerlegung
		self.SVD  = la.svd(self.A)
		# Pseudoinverse
		self.PINV = la.pinv(self.A)



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
		smooth = smooth**5 / (smooth**5 + (1. - smooth)**5)
		return dot(la.pinv(self.ATA * (1. - smooth) + smooth * self.m * self.STS),
			dot(self.AT * (1. - smooth), input_signal))



	def spectrum_pinv(self, input_signal):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		Berechnet die Lösung mit der Pseudoinversen
		Rückgabe: das Spektrum als Vektor
		'''

		return dot(self.PINV, input_signal)



	def blackbody(self, T):
		h = 6.6261e-34
		c = 2.9979e8
		k = 1.3807e-23
		return 5e30 * self.lambdas**(-5.) / (T**4 * (sc.exp(h * c / ((self.lambdas / 1e9) * k * T)) - 1.))

	def spectrum_blackbody(self, input_signal, temp_output):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		temp_output: Rückgabe der Temperatur

		sucht ein Schwarzkörperspektrum, das gut aufs Signal passt
		'''

		def err(p, signal):
			print p[0]
			return dot(self.A, p[0] * self.blackbody(abs(p[1]))) - signal

		# TODO: Startwerte müssen vorberechnet werden
		# sonst konvergierts oft nicht
		p, success = op.leastsq(err, [1., 6e3], args=(input_signal,), maxfev=2000)
		temp_output[0], temp_output[1] = p[0], abs(p[1])
		return p[0] * self.blackbody(abs(p[1]))



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
			err_signal = ((dot(self.A, s) - input_signal)**2).mean() * s.mean()
			err_zero = ((sc.absolute(s) - s) ** 2).mean() / 4.
			err_smooth = ((s[1:-1] - .5 * (s[2:] + s[:-2])) ** 2).mean()
			return smooth * err_smooth + (1. - smooth) * (err_signal) + err_zero

		spectrum = op.fmin_bfgs(err, self.spectrum_smooth(input_signal), disp=0)

		return spectrum



	def spectrum_gauss_single(self, input_signal):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		erzeugt eine optimale Gaußkurve
		'''

		try:
			s = input_signal / self.weights[self.use]
			mean0 = dot(s, self.led_colors[self.use]) / sc.sum(s, 0)
			sigma0 = sqrt(dot(s, self.led_colors[self.use]**2) / sc.sum(s, 0) - mean0 ** 2)
			def gauss((mean, sigma, height)):
				return height * sc.exp(- ((self.lambdas - mean) / sigma) ** 2)
			def err((mean, sigma, height)):
				return dot(self.A, gauss((mean, sigma, height))) - input_signal
			s2 = dot(self.A, gauss((mean0, sigma0, 1)))
			height0 = dot(s2, input_signal) / dot(s2, s2)

			p, success = op.leastsq(err, x0=(mean0, sigma0, height0), maxfev=80)
			return gauss(p)
		except (ValueError, ZeroDivisionError):
			print "error fitting gauss"
			return sc.zeros(self.m)



