# -*- coding:utf8 -*-

# Enthält die Klasse zur Spektrensimulation

from math import *
import random
import scipy as sc
from scipy import dot

class DataSimulation():
	def __init__(self, lambdas, absorption, noise=0.):
		self.lambdas = lambdas
		self.make_spec()
		self.make_signal(absorption, noise)


	def make_spec(self):
		'''
		erzeugt ein Zufallsspektrum
		'''
		myrand = [random.random() for i in xrange(3*7)]
		spectrum = sc.array([0. for i in self.lambdas])
		for i in range(len(myrand) / 3):
			spectrum = spectrum + sqrt(myrand[i/3]) * sc.array(sc.exp(
			-((self.lambdas - (400. + 300 * myrand[1+i/3])) / (5.+150.*myrand[2+i/3]**2))**2))
		# normieren
		self.spectrum = spectrum / max(spectrum)



	def make_signal(self, absorption, noise=0.):
		'''
		simuliert ein Messsignal
		'''
		self.signal_clean = dot(absorption, self.spectrum)
		# Signal verrauschen
		self.noise = noise
		signal = [random.gauss(1., self.noise) * i for i in self.signal_clean]

		self.signal = sc.array(signal)
		
