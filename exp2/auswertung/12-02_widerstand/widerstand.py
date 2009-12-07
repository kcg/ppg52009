#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as p
#import scipy
#import numpy
from math import *
#from scipy import optimize
#import scipy.interpolate
from matplotlib import colors as clr
import copy

def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]
		line = linetext.split(colsep)
		if len(line) <= 0:
			continue
		row = []
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				pass
		data.append(row)
	return(data)


data 		= readdata("messwerte_30s.dat")
#data_short 	= readdata("messwerte_1s.dat")

v_min = 0
for i in xrange(len(data)):
	if abs(data[i][1]) > v_min:
		v_min = data[i][1]
i_min = 0
for i in xrange(len(data)):
	if data[i][2] < i_min:
		i_min = data[i][2]
		
current = [abs(i[2] - i_min) for i in data]
voltage = [abs(i[1] - v_min) for i in data]

# ansteigende Flanke extrahieren
up_limit_upper	= 500 + 35
up_limit_lower	= 100
current_up = current[up_limit_lower:up_limit_upper]
voltage_up = voltage[up_limit_lower:up_limit_upper]

# fallende Flanke extrahieren
down_limit_upper = 1230 + 45
down_limit_lower = 900
current_down = current[down_limit_lower:down_limit_upper]
voltage_down = voltage[down_limit_lower:down_limit_upper]

# unerklärliche Drift (linear bei kurzen Zeiten):
# ansteigend:	dU/dt = 0.415 mV/s (@ 2.3 µA -> offset: 2.45 µA)
# fallend:	dU/dt = -0.274 mV/s (@ -0.15 µA -> offset: 0.0 µA)
# // verworfen: lineare Interpolation (nehme I-Abhängigkeit an):
# // 		U'(I) = 0.281 mV/s/µA * I - 0.274 mV/s
# => lineare Interpolation:
# up:	1.8 -> 2.45, 0 -> 0.415
# dU = (0.415 mV / (2.45 µA - 1.8 µA) * (I - 1.8 µA)) * dt
# down:	0.7 -> 0.0, 0 -> -0.274
# dU = (-0.274 mV / (-0.7 µA)) * (I - 0.7 µA)) * dt
# 	dt der Messwerte:	0.1 s

dvoltage_up = []
counter = 0
for i in xrange(len(voltage_up)):
	if current_up[i] >= 1.8:
		dvoltage_up.append(dvoltage_up[i-1] + (0.415 / (2.45 - 1.8) * (current_up[i] - 1.8)) * 0.1)
		counter += 1
	else:
		dvoltage_up.append(0.0)
		
dvoltage_down = []
counter = 0
for i in xrange(len(voltage_down)):
	if current_down[i] <= 0.7:
		dvoltage_down.append(dvoltage_down[i-1] + (-0.274 / (-0.7)) * (current_down[i] - 0.7) * 0.1)
		counter += 1
	else:
		dvoltage_down.append(0.0)
		

# Drifteffekt _abziehen_
voltage_up_corrected = [0.0] * len(voltage_up)
voltage_down_corrected = [0.0] * len(voltage_up)
for i in xrange(len(voltage_up)):
	voltage_up_corrected[i]		= voltage_up[i] - dvoltage_up[i]
	
for i in xrange(len(voltage_down)):
	voltage_down_corrected[i]	= voltage_down[i] - dvoltage_down[i]


# Steigung berechnen: R = dU/dI
resistance_up	= []
resistance_down	= []
dx		= 16*4	# = 4.0 s; dI/dt = 0.052 µA/s

resistance_up			= []
resistance_down			= []
resistance_up_corrected		= []
resistance_down_corrected	= []

for i in xrange (up_limit_upper-up_limit_lower-dx):
	try:
		resistance_up.append((voltage_up[i] - voltage_up[i+dx]) /		\
				(current_up[i] - current_up[i+dx]))
	except ZeroDivisionError:
		resistance_up.append(float('nan'))
		
	try:
		resistance_up_corrected.append((voltage_up_corrected[i] - voltage_up_corrected[i+dx]) /		\
				(current_up[i] - current_up[i+dx]))
	except ZeroDivisionError:
		resistance_up_corrected.append(float('nan'))
		
for i in xrange (down_limit_upper-down_limit_lower-dx):
	try:
		resistance_down.append((voltage_down[i] - voltage_down[i+dx]) /		\
				(current_down[i] - current_down[i+dx]))
	except ZeroDivisionError:
		resistance_down.append(float('nan'))
		
	try:
		resistance_down_corrected.append((voltage_down_corrected[i] - voltage_down_corrected[i+dx]) /	\
				(current_down[i] - current_down[i+dx]))
	except ZeroDivisionError:
		resistance_down_corrected.append(float('nan'))


#sum_up = 0
#for i in xrange(len(resistance_up)):	
#	sum_up += resistance_up[i]		
#resistance_media	= sum_up / len(resistance_up)

#print resistance_media

# entferne bis auf jedes 3. element -> schönerer plot
h_current_up 				= []
h_voltage_up				= []
h_resistance_up				= []
h_voltage_up_corrected			= []
h_resistance_up_corrected		= []
h_current_down 				= []
h_voltage_down				= []
h_resistance_down			= []
h_voltage_down_corrected		= []
h_resistance_down_corrected		= []
for i in xrange(len(resistance_up)):
	if i % 5 == 0:
		h_current_up.append(current_up[i])
		h_voltage_up.append(voltage_up[i])
		h_resistance_up.append(resistance_up[i])
		h_voltage_up_corrected.append(voltage_up_corrected[i])
		h_resistance_up_corrected.append(resistance_up_corrected[i])
for i in xrange(len(resistance_down)):
	if i % 5 == 0:
		h_current_down.append(current_down[i])
		h_voltage_down.append(voltage_down[i])
		h_resistance_down.append(resistance_down[i])
		h_voltage_down_corrected.append(voltage_down_corrected[i])
		h_resistance_down_corrected.append(resistance_down_corrected[i])
current_down			= h_current_down
voltage_down			= h_voltage_down
resistance_down			= h_resistance_down
voltage_down_corrected		= h_voltage_down_corrected
resistance_down_corrected	= h_resistance_down_corrected
current_up			= h_current_up
voltage_up			= h_voltage_up
resistance_up			= h_resistance_up
voltage_up_corrected		= h_voltage_up_corrected
resistance_up_corrected		= h_resistance_up_corrected

# corrected-werte sichern
current_up_corrected	= copy.copy(current_up)
current_down_corrected	= copy.copy(current_down)

# "Anlaufbereich" rausziehen
current_up_corrected 		= current_up_corrected[15:]
resistance_up_corrected		= resistance_up_corrected[15:]
current_down_corrected 		= current_down_corrected[20:]
resistance_down_corrected	= resistance_down_corrected[20:]

# Mittelwert berechnen:

sum_up 		= 0
sum_down	= 0
square_sum_up	= 0
square_sum_down	= 0
for i in xrange(len(resistance_up_corrected)):	
	sum_up += resistance_up_corrected[i]
for i in xrange(len(resistance_down_corrected)):	
	sum_down += resistance_down_corrected[i]
n = len(resistance_up_corrected) + len(resistance_down_corrected)
resistance_media	= (sum_up + sum_down) / n
for i in xrange(len(resistance_up_corrected)):	
	square_sum_up += (resistance_up_corrected[i] - resistance_media)**2
for i in xrange(len(resistance_down_corrected)):	
	square_sum_down += (resistance_down_corrected[i]- resistance_media)**2
	
resistance_dev = sqrt((square_sum_up + square_sum_down) / (n-1))
print resistance_media," +/- ",resistance_dev

p.plot(current,voltage, 'grey', label="$I$-$U$-Kennline")	# I-U-Diagramm

# plotte widerstände
p.plot(current_up,resistance_up, "oc")
p.plot(current_down,resistance_down,"oy")

p.plot(current_up_corrected,resistance_up_corrected, "ob", label = "$R$ bei $\\frac{dI}{dt} > 0 $")
p.plot(current_down_corrected,resistance_down_corrected,"og",label = "$R$ bei $\\frac{dI}{dt} < 0 $")

p.plot([current_up[0],current_down[0]],[resistance_media,resistance_media],color="r",label = "$<R>$ = ("+str(round(resistance_media,2))+"$\pm$"+str(round(resistance_dev,2))+") k$\\Omega$")

p.grid()                      
p.xlabel('Strom $I$ in $\\mu$A')
p.ylabel('Widerstand $R$ in k$\\Omega$ bzw. Spannung $U$ in mV')
p.legend(loc="upper left")

# Speichern
p.gcf().set_size_inches(7.5, 5)
p.savefig("messung_widerstand.pdf")

# Anzeigen
p.show()
