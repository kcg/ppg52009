#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
import scipy.linalg as la
import time
from math import *
from scipy import dot
import scipy.interpolate as ip
from scipy import optimize

import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..', 'python'))
from read_data import *


'''
Reduktion des darkframes
'''


mess_error = 5e-6 # volts
lambda_bin = sc.array(range(335, 740 + 1)) # nanometers
delta_alpha_phot = 2.9 # degree



def alpha_von_U(U):
	'''
	see "winkel_spannung.py" for parameters
	'''
	p = [-87.666840, 345.873839, -17.170723, 5.992822, 0.540028]
	return p[0] + p[1] * U + p[2] * (sqrt(1 + (p[3] * (U - p[4]))**2) - 1.)



def lambda_von_alpha(alpha):
	d = 1e6 / 2400. # grid constant in nm
	phi = 68. # grid angle
	return d * (sin(radians(phi)) - sin(radians(alpha + phi)))
'''
show voltage values at all wavelengths
for j in [[i, optimize.fsolve(lambda U: lambda_von_alpha(alpha_von_U(U)) - i, .7)] for i in lambda_bin]: print j
'''



def sort_arrays(*arrays):
	permut = arrays[0].argsort()
	return [i[permut] for i in arrays]




def interpolate_linear(x, y, t):
	'''
	interpolate data x,y to x-values at t
	'''
	# remove double values
	xx = []; yy = []
	ys = 0.; n = 0
	for i in range(len(x)):
		n += 1; ys += y[i]
		if i == len(x) - 1 or x[i] != x[i+1]:
			xx.append(x[i])
			yy.append(ys / n)
			ys = 0.; n = 0
	spline = ip.splrep(xx, yy, k=1)
	return ip.splev(t, spline)




def interpolate_smooth(l, I):
	'''
	interpolate data l,I to l-values at lambda_bin
	'''
	# remove double values
	ll = []; II = []
	Is = 0.; n = 0
	for i in range(len(l)):
		n += 1; Is += I[i]
		if i == len(l) - 1 or l[i] != l[i+1]:
			ll.append(l[i])
			II.append(Is / n)
			Is = 0.; n = 0
	# find error estimates and weights
	sqr_err_est = []
	for i in range(1, len(ll) - 1):
		y = sc.array(II[i-1:i+2])
		x = sc.array([ll[i], ll[i+1], ll[i-1]])
		d = sc.array([ll[i] - ll[i+1], ll[i+1] - ll[i-1], ll[i-1] - ll[i]])
		sqr_err_est.append(.5 * dot(y, d)**2 / dot(x, d))
	sqr_err_est = [.5 * (II[1] - II[0])**2] + sqr_err_est + [.5 * (II[-1] - II[-2])**2]
	weights = sc.array([1. / sqrt(0.2*mess_error**2 + .75*i) for i in sqr_err_est])
			
	l0 = max(lambda_bin[0], ceil(l[0]))
	l1 = min(lambda_bin[-1], floor(l[-1]))
	lamb = sc.arange(l0, l1 + 1)
	spline = ip.splrep(ll, II, w=weights, s=len(ll))
	v = ip.splev(lamb, spline)
	return sc.array([0.] * (l0 - lambda_bin[0])
		+ list(v)
		+ [0.] * (lambda_bin[-1] - l1))




# Start data analysis here
mess_path = "../messungen/"

for k in [0]:
	filename = mess_path + "2010-03-26/reichelt_alt/photodiode_3_dark.dat"

	data = readdata(filename)
	U_dark = sc.array([i[0] for i in data])
	I_dark = sc.array([i[1] for i in data])
	U_dark, I_dark = sort_arrays(U_dark, I_dark)
	lamb_dark = sc.array([lambda_von_alpha(alpha_von_U(Ui) + delta_alpha_phot) for Ui in U_dark])

	I = interpolate_smooth(lamb_dark, I_dark)

	# Ende abrunden
	def parabula(p, x):
		return p[0] + p[1] * x + p[2] * x**2
	def err(p, x, y):
		return y - parabula(p, x)

	i0 = 695 - lambda_bin[0]
	par, success = optimize.leastsq(err, [0., 0., 0.], args=(lambda_bin[i0:i0+5], I[i0:i0+5]))
	for i in range(i0, len(lambda_bin)):
		I[i] = parabula(par, i + lambda_bin[0])


	ofile = open(mess_path + "photo_dark_normal.dat", "w")
	ofile.write("# Spalte1: Wellenlaenge [nm]\n")
	ofile.write("# Spalte2: Intensitaet\n")
	for j in range(len(lambda_bin)):
		ofile.write("%.0f\t%.9f\n" % (lambda_bin[j], I[j]))
	ofile.close()


for k in [1]:
	filename = mess_path + "2010-03-26/zylinderlinse/LBT67C_dark.dat"

	data = readdata(filename)
	U_dark = sc.array([i[0] for i in data])
	I_dark = sc.array([i[2] for i in data])
	U_dark, I_dark = sort_arrays(U_dark, I_dark)
	lamb_dark = sc.array([lambda_von_alpha(alpha_von_U(Ui) + delta_alpha_phot) for Ui in U_dark])

	I = interpolate_smooth(lamb_dark, I_dark)
	
	# Ende abrunden
	def line(p, x):
		return p[0] + p[1] * x
	def err(p, x, y):
		return y - line(p, x)

	i0 = 360 - lambda_bin[0]
	par, success = optimize.leastsq(err, [0., 0.], args=(lambda_bin[i0:i0+4], I[i0:i0+4]))
	for i in range(0, i0):
		I[i] = line(par, i + lambda_bin[0])
	
	i0 = 686 - lambda_bin[0]
	par, success = optimize.leastsq(err, [0., 0.], args=(lambda_bin[i0:i0+4], I[i0:i0+4]))
	for i in range(i0, len(lambda_bin)):
		I[i] = line(par, i + lambda_bin[0])

	ofile = open(mess_path + "photo_dark_zylinder.dat", "w")
	ofile.write("# Spalte1: Wellenlaenge [nm]\n")
	ofile.write("# Spalte2: Intensitaet\n")
	for j in range(len(lambda_bin)):
		ofile.write("%.0f\t%.9f\n" % (lambda_bin[j], I[j]))
	ofile.close()




for k in [2]:
	filename = mess_path + "halogen_raw.dat"

	data = readdata(filename)
	lamb = sc.array([i[0] for i in data])
	I = sc.array([i[1] for i in data])

	I = interpolate_linear(lamb, I, lambda_bin) - 4.
	for i in range(len(I)):
		if I[i] < 0.:
			I[i] = 0.
	I /= max(I)
	
	ofile = open(mess_path + "halogen.dat", "w")
	ofile.write("# Spalte1: Wellenlaenge [nm]\n")
	ofile.write("# Spalte2: Intensitaet\n")
	for j in range(len(lambda_bin)):
		ofile.write("%.0f\t%.9f\n" % (lambda_bin[j], I[j]))
	ofile.close()




for k in [3]:
	filename = mess_path + "2010-03-26/reichelt_alt/photodiode_3_dark.dat"

	data = readdata(filename)
	U = sc.array([i[0] for i in data])
	I = sc.array([i[1] for i in data])
	lamb = sc.array([lambda_von_alpha(alpha_von_U(Ui) + delta_alpha_phot) for Ui in U])
	lamb, I = sort_arrays(lamb, I)

	I = interpolate_linear(lamb, I, lambda_bin)
	for i in range(len(I)):
		if I[i] < 0.:
			I[i] = 0.
	
	ofile = open(mess_path + "photo_dark_reichelt.dat", "w")
	ofile.write("# Spalte1: Wellenlaenge [nm]\n")
	ofile.write("# Spalte2: Intensitaet\n")
	for j in range(len(lambda_bin)):
		ofile.write("%.0f\t%.9f\n" % (lambda_bin[j], I[j]))
	ofile.close()


