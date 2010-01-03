#! /usr/bin/env python
# -*- coding:utf8 -*-

# Berechnet das komplette Spektrum aus Messsignalen

from math import *
import scipy as sc
import scipy.linalg as la
import scipy.optimize as op
from scipy import dot
from file_parse import *


class DataSpectral():
	def __init__ (self):
		'''
		liest die LED Sensitivitäten in den Arbeitsspeicher 
		'''
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
		self.lambdas = sc.array([i[0] for i in readdata("led_spektren/" + leds[0])])
		self.A = sc.array(A)
		self.AT = self.A.T
		self.ATA = dot(self.AT, self.A)

		# Glättungskern
		S = -sc.eye(self.m);
		S[0][0] = S[-1][-1] = 0.
		for i in range(1, self.m-1):
			S[i][i-1] = S[i][i+1] = .5
		self.STS = dot(S.T, S)



	def make_signal(self, signal):
		'''
		signal: Vektor kompatibel zu self.lambdas (Länge self.m),
		enthält eine ursprüngliche Intensitätsverteilung

		Simuliert Signale, um die Algorithmen zu testen.
		'''
		return dot(self.A, signal)



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

		return la.solve(self.ATA + smoothing * self.STS,
			dot(self.AT, input_signal))



	def spectrum_blackbody(self, input_signal, temp_output):
		'''
		input_signal: Intensitätswert jeder LED (ca. 16 Werte)
		temp_output: Rückgabe der Temperatur

		sucht ein Schwarzkörperspektrum, das gut aufs Signal passt
		'''

		h = 6.63e-34
		c = 3e8
		k = 1.38e-23
		# p = [faktor, Temperatur]
		def I(p, l):
			return p[0] * l**(-5.) / (sc.exp(h * c / ((l / 1e9) * k * p[1])) - 1.)
		def err(p, signal):
			return dot(self.A, I(p, self.lambdas)) - signal

		p, success = op.leastsq(err, [1e16, 1e5], args=(input_signal,), maxfev=2000)
		temp_output[0], temp_output[1] = p
		return I(p, self.lambdas)


