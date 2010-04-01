#! /usr/bin/env python
# -*- coding: utf8 -*-


# Berechnet den Gitterwinkel aus direkter Messung und Laserreflexion erster Ordnung


from math import *
from scipy import optimize



helium_neon = 632.816
alpha_HeNe = 146.2
phi_mess = 67.5


d = 1e6 / 2400.
def lambda_von_alpha(alpha, phi):
	return d * (sin(radians(phi)) - sin(radians(alpha + phi)))
	
def alpha_von_lambda(lamb, phi):
	return optimize.fsolve(lambda alpha: lambda_von_alpha(alpha, phi) - lamb, 150.)

	
def winkel_err(phi):
	return (2.*(phi - phi_mess))**2 + (alpha_von_lambda(helium_neon, phi) - alpha_HeNe)**2


# Winkel fitten
phi, success = optimize.leastsq(winkel_err, 70.)
print "phi =", phi

# Ergebnis: phi = 68 grad (Drehwinkel Gitter gegen Achsennormale)


