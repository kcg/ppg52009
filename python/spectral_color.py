# -*- coding: utf8 -*-



def spectral(lamb, bgcolor=None):
	'''
	calculates an rgba-color from wavelengths
	'''
	#   UV, violett, blau, türkis, grün, gelb, rot,  IR
	l = [350., 400., 450., 492., 535., 580., 650., 750.]
	colors = [[.5, .5, 0., 0., 0., 1., 1., 1.],
		[0., 0., 0., .8, 1., 1., 0., 0.],
		[1., 1., 1., .9, 0., 0., 0., 0.],
		[0., 1., 1., 1., 1., 1., 1., 0.]]
	
	rgba = []

	i = 0
	while i < len(l) - 1 and l[i+1] <= lamb:
		i += 1
	
	for j in range(4):
		if lamb <= l[0] or l[-1] <= lamb:
			rgba.append(colors[j][i])
		else:
			f = (lamb - l[i]) / (l[i+1] - l[i])
			rgba.append(colors[j][i] * (1. - f) + f * colors[j][i+1])		
	
	if bgcolor == None:
		return tuple(rgba)
	else:
		x = rgba[3]; y = 1. - x
		return tuple([x * rgba[i] + y * bgcolor[i] for i in range(3)])


'''
import pylab as pl
for i in range(300, 800):
	pl.plot([i, i+1], [0.,0.], linewidth=100, color=spectral(i, (1., 1., 1.)))
pl.show()
'''
