#! /usr/bin/env python
# -*- coding: utf8 -*-

import pylab as pl
import scipy as sc
import scipy.linalg as la
import os, time, sys
from math import *
from scipy import dot
import scipy.interpolate as ip
from scipy import optimize


'''
Hier ist noch viel zu tun.
Wer an einem Programmteil Lust hat, kann gerne daran schreiben!
'''


'''
Reduktion der LED-Absorptionsspektren


liest ein:
-Drehwinkel in Abhängigkeit von der Poti-Spannung (I-1)
-LED-Spannung in Abhängigkeit von der Poti-Spannung (I-2)
-Das Spektrum der Leucht-LED (vom Spektrometer der Optiker) (I-3)


Umrechnungen:
-erzeugt Fitfunktion für alpha(U) (II-1)
-mapt die Intensitätskurven auf Winkel -> I(alpha) (II-2)

-bestimmt aus dem Peak Nullter Ordnung den Gitterwinkel (II-3)
und die Faltungsfunktion (II-4)
-Entfaltet die Intensitätskurven (II-5)

-berechnet lambda(alpha) mit dem Gitterwinkel (II-6)
-mapt die Intensitätskurven von alpha nach lambda (II-7)
-skaliert die Intensitätskurven nach dem Transformationssatz (II-8)
-skaliert die Intensitätskurven mit dem Spektrum der Leucht-LED (II-9)


Ausgabe:
-fertige LED-Absorptionsspektren I(lambda) (III-1)
'''


def readdata(filename, colsep="\t", comment="#"):
	ifile = open(filename, "r")
	data = []; l = 0
	for linetext in ifile.readlines():
		l += 1
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1].strip()
		if linetext == "": continue
		line = linetext.split(colsep)
		if len(line) <= 0: continue
		row = []
		for i in line:
			try:
				x = float(i)
				row.append(x)
			except ValueError:
				print 'File "' + filename + '",',
				print 'line ' + str(l) + ':',
				print '"' + i + '" is not a float'
				row.append(0.)
		data.append(row)
	ifile.close()
	return(data)



# Spektralfarben
def spectral(lamb):
	red = 0.; green = 0.; blue = 0.
	if lamb < 400.:
		pass
	elif lamb <= 470.:
		blue = (lamb-400.) / (470. - 400.)
		red = (lamb-400.) / (470. - 400.) * ( 1. - (lamb-400.) / (470. - 400.))
	elif lamb <= 525.:
		blue = (525. - lamb) / (525. - 470.)
		green = (lamb - 470.) / (525. - 470.)
	elif lamb <= 575.:
		green = 1.
		red = (lamb - 525.) / (575. - 525.)
	elif lamb <= 640.:
		red = 1.
		green = (640. - lamb) / (640. - 575.)
	elif lamb <= 700.:
		red = (700. - lamb) / (700. - 640.)
	red = hex(int(255.*red))[2:]
	green = hex(int(255.*green))[2:]
	blue = hex(int(255.*blue))[2:]
	while len(red) < 2:
		red = "0" + red
	while len(green) < 2:
		green = "0" + green
	while len(blue) < 2:
		blue = "0" + blue
	return "#" + red + green + blue







# Fitfunktion für die Winkelabhängigkeit der Potispannung
def U_von_winkel(p, x):
	return p[0] + exp(p[1] * x)
def winkel_func(p, xlist, ylist):
	y = [U_von_winkel(p, x) for x in xlist]
	return [y[i] - ylist[i] for i in range(len(xlist))]

# Drehwinkel in Abhängigkeit von der Poti-Spannung (I-1) <-- Ich (Karl) probiers mal (I-1 bis II-2)
data_winkel = readdata("winkel_data.txt")
w1 = [(360. - i[0]) for i in data_winkel]
U1 = [i[1] for i in data_winkel]

# Winkelfunktion fitten
par1, success = optimize.leastsq(winkel_func, [1.,1.], args=(w1, U1))

interval = sc.linspace(min(0, min(w1)-5.),max(w1)+5.,100)
'''
pl.plot(interval, [U_von_winkel(par1, a) for a in interval] , "k-", label="Fit: $%.4f + \\mathrm{exp}(%.4f\cdot\, \\alpha)$" % tuple(par1))
pl.plot(w1, U1, "bo", label="Messung")

# Speichern und zeichnen
pl.xlabel('Winkel $ \\alpha $ in [deg]')
pl.ylabel('Spannung $U$ in [mV]')
pl.legend(loc='upper left')
pl.gcf().set_size_inches(6, 4)
pl.savefig("winkel_spannung.pdf")
pl.show()
pl.clf()
'''




# erzeuge Fitfunktion für alpha(U) (II-1)
def winkel_von_U(U):
	return optimize.fsolve(lambda a: U_von_winkel(par1, a) - U, 0.)




# Lies LED-Spannungen in Abhängigkeit von der Poti-Spannung (I-2)
print "Rohspektren einlesen..."
filenames = []; pfad_rohspektren = '2009-12-17'
for i in os.walk(pfad_rohspektren):
	filenames = i[2];
	break;
i = 0
while i < len(filenames):
	if len(filenames[i]) < 7:
		del filenames[i]
	elif filenames[i][:3] != "led" or filenames[i][-4:] != ".dat":
		del filenames[i]
	else:
		i += 1
spektren = []
for fname in filenames:
	data = readdata(pfad_rohspektren + "/" + fname)
	U = [i[0] for i in data]
	I = [i[1] for i in data]
	# nach U sortieren
	permut = sc.argsort(U)
	U = [U[i] for i in permut]
	I = [I[i] for i in permut]
	# mehrfache Einträge entfernen
	i = 0
	while i < len(U):
		n = 1
		while i < len(U)-1 and U[i] == U[i+1]:
			n += 1
			I[i] = (I[i] * (n-1.) + I[i+1]) / n
			del U[i+1]; del I[i+1]
		i += 1

	spektren.append([U,I])




# Intensitätskurven von Spannung auf Winkel mappen -> I(alpha) (II-2)
for s in spektren:
	for i in range(len(s[0])):
		s[0][i] = winkel_von_U(s[0][i])
# "spektren" enthält nun jeweils [winkel, Intensität]

#'''
'''
for i in range(len(filenames)):
	try:
		x = float(filenames[i][3:6])
		col = spectral(x)
	except ValueError:
		col = "#000000"
	pl.plot(spektren[i][0], spektren[i][1], ".", color=col, label=filenames[i][3:-4])
pl.xlabel(u"Winkel")
pl.ylabel(u"LED Spannung")
pl.rcParams.update({'font.size' : 7})
pl.legend(loc=u"best")
'''
#pl.show()
#'''




# bestimme aus dem Peak Nullter Ordnung den Gitterwinkel (II-3)
spektren1 = [] # Spektren mit vernünftigem Peak 0. Ordnung
for sp in spektren:
	cut = False
	small = True
	spektrum = [[], []]
	for i in range(len(sp[0])):
		if 45. <= sp[0][i] and sp[0][i] <= 51.:
			spektrum[0].append(sp[0][i])
			spektrum[1].append(sp[1][i])
			if sp[0][i] - sp[0][i-1] >= 0.5:
				cut = True # Das Spektrum wurde wohl abgeschnitten
			if sp[1][i] >= 0.004:
				small = False # Das Spektrum ist stark genug
	if cut == False and small == False:
		spektren1.append(spektrum)
sum_U = 0.; sum_wU = 0.
for sp in spektren1:
	for i in range(1, len(sp[0])-1):
		sum_U += (sp[0][i+1] - sp[0][i-1]) * sp[1][i]
		sum_wU += (sp[0][i+1] - sp[0][i-1]) * sp[1][i] * sp[0][i]
# Nun Gitterwinkel ausrechnen aus Mittelwert des 0. Peaks
alpha_zero = sum_wU / sum_U
phi = 90. - alpha_zero / 2.
print u"phi = %.1f°" % (phi,)




# führe Binning der Winkel ein
bin_alpha = 0.1 # Grad




# bestimme die diskrete Faltungsfunktion (II-4)
breite_f = 5.
alpha_f = sc.linspace(-round((breite_f/2.)/bin_alpha)*bin_alpha, round((breite_f/2.)/bin_alpha)*bin_alpha, 1 + 2 * round((breite_f/2.)/bin_alpha))
spektren1_spline = []
for sp in spektren1:
	spektren1_spline.append(ip.splrep(sp[0], sp[1], k=3))
I_f = sc.array([ip.splev(alpha_f + alpha_zero, spektren1_spline[i]) for i in range(len(spektren1_spline))]).sum(0)
'''
pl.clf()
pl.plot(alpha_f, I_f)
for i in range(len(spektren1_spline)):
	pl.plot(alpha_f, ip.splev(alpha_f + alpha_zero, spektren1_spline[i], der=0),".")
pl.show()
'''




# Bringe die Intensitäten auf gleichmäßiges Gitter
print "Daten binnen..."
winkel_sp = (110., 164.)
alpha_s = sc.linspace(round(winkel_sp[0]/bin_alpha)*bin_alpha, round(winkel_sp[1]/bin_alpha)*bin_alpha, 1 + 2 * round((winkel_sp[1]-winkel_sp[0])/bin_alpha))
spektren_s = [] # gleichmäßig gebinnte Spektren über alpha_s

# lineare Interpolation über die Daten
for i in range(len(spektren)):
	tck = ip.splrep(spektren[i][0], spektren[i][1], k=1)
	spektren_s.append(ip.splev(alpha_s, tck))
'''
	try:
		x = float(filenames[i][3:6])
		col = spectral(x)
	except ValueError:
		col = "#000000"
	pl.plot(alpha_s, spektren_s[-1], "--", color=col)
pl.show()
'''




# Entfaltung der Intensitätskurven (II-5)
entfalten = True
def matrix_deconvolution (dx, b, f, s1=0., s2=1.):
	'''
	dx: Abstand der Messstellen
	b: gemessene Werte
	f: Array der Faltungsfunktion (muss nicht normiert sein) (symmetrisches Intervall)
	s: Glättungsfaktor
	gibt den entfalteten Punktvektor a zurück
	geht von gleichmäßig gebinnten Daten aus
	'''
	n = len(b)

	# Matrix der f-Differenzen A_{ij} = f(x_j - x_i) * delta_x
	if len(f) < 2 * n - 1:
		d = sc.array((n - (len(f) + 1) / 2) * [0.] + list(f) + (n - (len(f) + 1) / 2) * [0.])
	else:
		d = sc.array(f[(len(f)-n)/2:(len(f)+n)/2])

	A = sc.array([d[n-i-1:2*n-i-1] for i in range(n)])
	# normieren
	A = A / A.sum(1)

	# Glättungskerne
	c = [[-1., .5], [1., -2/3., 1/6.]]

	# Randsteigung möglichst klein machen
	R = sc.zeros((n,n))
	wert0 = 0; steigung0 = n
	R[0][0] = R[-1][-1] = wert0 + steigung0
	R[0][1] = R[-1][-2] = -steigung0

	# erster Term: A^T * A * a = A^T * b
	# Andere Terme beschränken die Fluktiationen
	AA = dot(A.T, A) + dot(R.T, R)
	bb = dot(A.T, b)
	L = sc.zeros((n,n));
	for i in range(2):
		L = sc.zeros((n,n));
		for j in range(i+1,n-(i+1)):
			for ii in range(-(i+1), (i+2)):
				L[j][j+ii] = c[i][abs(ii)]
		AA += [s1, s2][i] * dot(L.T, L)

	a = la.solve(AA, bb)
	return a

if entfalten == False:
	spektren_d = spektren_s
else:
	print "Spektren entfalten", ; sys.stdout.flush()
	spektren_d = [] # entfaltete Spektren über alpha_s
	for i in range(len(spektren_s)):
		print ".", ; sys.stdout.flush()
		spektrum = matrix_deconvolution(bin_alpha, spektren_s[i], I_f, 5e2, 5e6)
		spektren_d.append(spektrum)
	'''
		try:
			x = float(filenames[i][3:6])
			col = spectral(x)
		except ValueError:
			col = "#000000"
		pl.plot(alpha_s, spektrum, "-", color=col)
	pl.show()
	'''
	print
# negative Intensitätswerte abschneiden
for s in spektren_d:
	for i in range(len(s)):
		if s[i] < 0.:
			s[i] = 0.




# berechne lambda(alpha) mit dem Gitterwinkel (II-6)
'''
Sei phi der Winkel, den das Gitter aus der Normalposition geschwenkt ist.
Sei alpha der Winkel, um den der Strahl am Gitter gebeugt wird.
d = 1mm/2400

lambda / d = sin(phi) - sin(alpha+phi)

z.B. phi = 66°, alpha = 140°
=> lambda = d * (sin(phi) - sin(alpha+phi)) = 563nm
'''
def lambda_von_alpha(alpha):
	d = 1e6 / 2400.
	return d * (sin(radians(phi)) - sin(radians(alpha + phi)))




# Intensitätskurven von alpha nach lambda mappen (II-7)
lambda_d = sc.array([lambda_von_alpha(i) for i in alpha_s])
# Spektren sind nun ambda_d -> spektren_d[i]
'''
for i in range(len(spektren_d)):
	try:
		x = float(filenames[i][3:6])
		col = spectral(x)
	except ValueError:
		col = "#000000"
	pl.plot(lambda_d, spektren_d[i], "-", color=col)
pl.show()
'''




# Intensitätskurven nach dem Transformationssatz skalieren (II-8)
# ?




# Lies das Spektrum der Leucht-LED (I-3)
print "Leuchtspektrum einlesen ..."
leucht_data = readdata("kalibrationsspektrum/kalibrationsspek.dat")
lambda_leucht = sc.array([i[1] for i in leucht_data])
leucht_I = sc.array([i[2] for i in leucht_data])

# linearen Offset aus Spektrum entfernen
remove_offset = 0.75 # wie Stark
lambda_leucht_off = []; leucht_I_off = []
for i in range(len(lambda_leucht)):
	if 200. <= lambda_leucht[i] and lambda_leucht[i] <= 300. or 900. <= lambda_leucht[i] and lambda_leucht[i] <= 1000.:
		lambda_leucht_off.append(lambda_leucht[i])
		leucht_I_off.append(leucht_I[i])
lambda_leucht_off = sc.array(lambda_leucht_off)
leucht_I_off = sc.array(leucht_I_off)
def linfunc(p, x):
	return p[0] + p[1] * x
def linerr(p, x, y):
	return y - linfunc(p, x)
p_leucht, success = optimize.leastsq(linerr, [0.,0.], args=(lambda_leucht_off, leucht_I_off))
leucht_I = leucht_I - remove_offset * linfunc(p_leucht, lambda_leucht)

# Spline zur späteren Verwenung erzeugen
leucht = ip.splrep(lambda_leucht, leucht_I, k=1)




# Intensitätskurven mit dem Spektrum der Leucht-LED skalieren (II-9)
print "Spektren mit der Weißlicht-LED skalieren ..."
spektren_fertig = []
for i in range(len(spektren_d)):
	spektrum = []
	I_weiss = ip.splev(lambda_d, leucht)
	spektrum = spektren_d[i] / (I_weiss / 1e5)
	for j in range(len(spektrum)):
		if abs(I_weiss[j]) <= 7.:
			spektrum[j] = 0.
	spektren_fertig.append(spektrum)




# Plot erstellen
print "Plotten..."
l_range = (350., 700.)
lambda_plot = sc.linspace(l_range[0], l_range[1], l_range[1] - l_range[0] + 1)
pl.subplot(311)
pl.title("Gemessene Spektren")
for i in range(len(spektren_s)):
	try:
		x = float(filenames[i][3:6])
		col = spectral(x)
	except ValueError:
		if filenames[i][3:6] == "rot":
			col = "#ff0000"
		elif filenames[i][3:8] == "gruen":
			col = "#00cc00"
		else:
			col = "#000000"

	if max(spektren_s[i]) >= 0.001:
		tck = ip.splrep(lambda_d, spektren_s[i], k=1)
		spektrum = ip.splev(lambda_plot, tck)
		pl.plot(lambda_plot, spektrum, "-", color=col)
pl.xlim(l_range[0], l_range[1])
pl.ylim(0., .11)
pl.grid(True)

pl.subplot(312)
for i in [0]:
	tck = ip.splrep(lambda_leucht, leucht_I, k=1)
	spektrum = ip.splev(lambda_plot, tck)
	pl.plot(lambda_plot, spektrum, "k-")
pl.title("Beleuchtung")
pl.xlim(l_range[0], l_range[1])
pl.grid(True)

pl.subplot(313)
for i in range(len(spektren_fertig)):
	try:
		x = float(filenames[i][3:6])
		col = spectral(x)
	except ValueError:
		if filenames[i][3:6] == "rot":
			col = "#ff0000"
		elif filenames[i][3:8] == "gruen":
			col = "#00cc00"
		else:
			col = "#000000"

	tck = ip.splrep(lambda_d, spektren_fertig[i], k=1)
	spektrum = ip.splev(lambda_plot, tck)
	pl.plot(lambda_plot, spektrum, "-", color=col)

pl.xlim(l_range[0], l_range[1])
pl.ylim(0., 2.1)
pl.title("Reduzierte Spektren")
pl.xlabel(u"Wellenlänge [nm]")
pl.grid(True)
pl.gcf().set_size_inches(7, 10)
pl.subplots_adjust(hspace=0.25)
pl.savefig("spektren_mit_weisslicht.pdf")





# fertige LED-Absorptionsspektren I(lambda) ausgeben (III-1)
lambda_fertig = sc.array(range(417, 670 + 1))
for i in range(len(spektren_fertig)):
	tck = ip.splrep(lambda_d, spektren_fertig[i], k=1)
	spektrum = ip.splev(lambda_fertig, tck)
	ofile = open("spektren_reduziert" + "/" + filenames[i], "w")
	ofile.write("# Spalte1: Wellenlänge [nm]\n")
	ofile.write("# Spalte2: Intensität\n")
	for j in range(len(lambda_fertig)):
		ofile.write("%.0f\t%.6f\n" % (lambda_fertig[j], spektrum[j]))
	ofile.close()


