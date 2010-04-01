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
Reduktion der LED-Absorptionsspektren
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
#show voltage values at all wavelengths
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


'''
def bin_to_lambda(lambda_array, I_array, fill="zero"):
	lamb = sc.arange(
		max(lambda_bin[0], ceil(lambda_array[0])),
		min(lambda_bin[-1], floor(lambda_array[-1])) + 1)
	
	# initialize 
	I = interpolate_linear(lambda_array, I_array, lamb)
'''



# Start data analysis here
mess_path = "../messungen/"

# theoretical curve of photodiode
data_photo = readdata(mess_path + "photodiode-daten.dat", colsep=" ")
lambda_photo = sc.array([i[0] for i in data_photo])
I_photo_raw = sc.array([i[1] for i in data_photo])
I_photo_theo = interpolate_linear(lambda_photo, I_photo_raw, lambda_bin)
#pl.plot(lambda_photo, I_photo_raw, "bo-")
#pl.plot(lambda_bin, I_photo_theo, "go-")
#pl.show()

# dark-curve of photodiode
data_dark = readdata(mess_path + "photo_dark_normal.dat")
I_photo_dark = sc.array([i[1] for i in data_dark])

data_dark_z = readdata(mess_path + "photo_dark_zylinder.dat")
I_photo_dark_z = sc.array([i[1] for i in data_dark_z])

data_dark_r = readdata(mess_path + "photo_dark_reichelt.dat")
I_photo_dark_r = sc.array([i[1] for i in data_dark_r])

# halogen lamp
data_halogen = readdata(mess_path + "halogen.dat")
I_halogen = sc.array([i[1] for i in data_halogen])


# get measurement data
folders = [mess_path + i for i in ["2010-03-23/Conrad", "2010-03-23/Roithner", "2010-03-24/reichelt", "2010-03-26/reichelt_alt", "2010-03-26/zylinderlinse"]]
filenames = []
for folder in folders:
	for i in os.walk(folder):
		filenames.append([folder + "/", i[2]]);
	i = 0
	while i < len(filenames[-1][1]):
		if filenames[-1][1][i][-4:] != ".dat": del filenames[-1][1][i]
		else: i += 1

for fnames in filenames:
	fnames[1].sort()
	for i in range(len(fnames[1])):
		pl.clf()
		fname = fnames[1][i]
		if fname[-9:-4] == "_dark": continue
		print fname
		
		I_led_dark = None; I_photo_dark = None
		if i < len(fnames[1]) - 1 and fnames[1][i+1] == fname[:-4] + "_dark.dat":
			data_dark = readdata(fnames[0] + fnames[1][i+1])
			U_dark_mess = sc.array([i[0] for i in data_dark])
			I_led_dark_mess = sc.array([i[1] for i in data_dark])
			I_photo_dark_mess = sc.array([i[2] for i in data_dark])
			lamb_dark = sc.array([lambda_von_alpha(alpha_von_U(Ui)) for Ui in U_dark_mess])
			lamb_dark, I_led_dark_mess, I_photo_dark_mess = sort_arrays(lamb_dark, I_led_dark_mess, I_photo_dark_mess)
			I_led_dark = interpolate_smooth(lamb_dark, I_led_dark_mess)
			I_photo_dark = interpolate_smooth(lamb_dark, I_photo_dark_mess)
		
		
		data = readdata(fnames[0] + fname)
		U_led_mess = sc.array([i[0] for i in data])
		I_led_mess = sc.array([i[1] for i in data])
		I_photo_mess = sc.array([i[2] for i in data])
		lamb_led = sc.array([lambda_von_alpha(alpha_von_U(Ui)) for Ui in U_led_mess])
		lamb_photo = sc.array([lambda_von_alpha(alpha_von_U(Ui) + delta_alpha_phot) for Ui in U_led_mess])
		lamb_led, I_led_mess, lamb_photo, I_photo_mess = sort_arrays(lamb_led, I_led_mess, lamb_photo, I_photo_mess)
		I_led = interpolate_smooth(lamb_led, I_led_mess)
		I_photo = interpolate_smooth(lamb_photo, I_photo_mess)
		
		if fnames[0] == mess_path + "2010-03-26/zylinderlinse/":
			print "zylinder"
			# no led dark-frames available
			I_photo -= I_photo_dark_z
		elif fnames[0] == mess_path + "2010-03-26/reichelt_alt/":
			print "reichelt"
			# no led dark-frames available
			I_photo -= I_photo_dark_r * 0.5
		else:
			# subtract dark current from led
			if I_led_dark != None:
				I_led -= I_led_dark
			else: print "no dark frame"
		
			# subtract dark current from photodiode
			if I_photo_dark != None:
				I_photo -= I_photo_dark
			else: print "no photo dark frame"
		
		#offset = min(sc.median(I_led[2:2+10]),
		#	sc.median(I_led[len(I_led)/2-5:len(I_led)/2+5]),
		#	sc.median(I_led[-2-10:-2]))
		#offset = min(0.00002, sc.median(I_led[20:40]))
		#I_led -= offset
		
		
		# divide intensity by photodiode
		I1 = I_led * I_photo_theo / (I_photo / .04)
		
		for j in range(len(I1)):
			if I_photo[j] == 0: I1[j] = 0.
		
		'''
		# halogen lamp yielded bad results...
		# divide intensity by halogen lamp spectrum
		I2 = I_led / I_halogen
		
		# put different wavelength-ranges together
		patch = [400, 440]
		factor = sc.array([I1[j] / I2[j] for j in range(patch[0]-lambda_bin[0], 1+patch[-1]-lambda_bin[0])]).mean()
		I2 *= factor
		
		def ratio(l):
			if l <= patch[0]: return 0.
			elif l >= patch[1]: return 1.
			f = (l - patch[0]) / float(patch[1] - patch[0])
			return .5 + 2. * (.75 * (f - .5) - (f - .5)**3)
		
		I = sc.array([ratio(l) * I1[l-lambda_bin[0]]
			+ (1. - ratio(l)) * I2[l-lambda_bin[0]]
			for l in lambda_bin])
		'''
		I = I1 # take photodiode only
		
		#pl.plot(lambda_bin, I_photo, "go-")
		#pl.plot(lambda_bin, I_photo_d, "yo-")
		#pl.plot(lambda_bin[10:], I1[10:], "g-")
		#pl.plot(lambda_bin[10:], I2[10:], "y-")
		#pl.plot(lambda_bin, I_led, "b.-")
		pl.plot(lambda_bin[10:], I[10:], "r.-")
		#pl.ylim(min(min(I), min(I_led)), max(max(I), max(I_led)))
		pl.ylim(ymin=0.)
		pl.draw()
		#pl.show()
		#time.sleep(1.)
		


		# Ausgabe
		ofile = open("../spektren1/" + fname, "w")
		ofile.write("# Spalte1: Wellenlänge [nm]\n")
		ofile.write("# Spalte2: Intensität [mV]\n")
		for j in range(len(lambda_bin)):
			ofile.write("%.0f\t%.6f\n" % (lambda_bin[j], 1000. * I[j]))
		ofile.close()


