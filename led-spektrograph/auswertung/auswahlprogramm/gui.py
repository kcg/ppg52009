# -*- coding:utf8 -*-

# Graphische Oberfläche für die Auswahl der Spektren
# verwendet Qt4 und Pylab
# benötigte Pakete: python-qt4, pyqt-tools

# 01.04.2010 ppg5

import sys, signal, random, time, os, threading

from PyQt4 import QtGui
from PyQt4 import QtCore

import pylab as pl
import scipy as sc
import scipy.optimize as op
from math import *

import matplotlib
import matplotlib.cm as cm
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

sys.path.append(os.path.join(os.getcwd(), '..', '..', '..', 'python'))
from read_data import *
from spectral_color import *

         
class Window (threading.Thread, QtGui.QWidget):
	def __init__ (self, parent=None):
		QtGui.QWidget.__init__ (self, parent)
		threading.Thread.__init__(self)

		## Generelle Initialisierungen
		self.xrange = (330., 750.)
		self.spektren = self.loadSpektra('../../spektren1')
		self.active = sc.array([True] * len(self.spektren))
		print "creating matrix ...",
		self.A = []
		for sp in self.spektren:
			ma = max(sp[2])
			if ma <= 0.: ma = -min(sp[2])
			self.A.append([max(i / ma, -ma) for i in sp[2]])
		self.A = sc.array(self.A)
		print "done"
		
		## Fenstereigenschaften:
		self.setWindowTitle('spektren Auswahl')
		self.resize(950, 680)
		self.center()


		## Grafische Elemente im Fenster:
		splitter1 = QtGui.QSplitter(QtCore.Qt.Vertical)
		splitter2 = QtGui.QSplitter(QtCore.Qt.Horizontal)
		self.main_vbox = QtGui.QVBoxLayout()
		self.main_vbox.addWidget(splitter1)
		splitter1.addWidget(splitter2)
		self.setLayout(self.main_vbox)
		
		## Graphen
		self.graph1 = QtGui.QWidget()
		self.dpi = 70
		
		# Graph 1
		self.mplbg = self.palette().background().color().getRgbF()
		self.fig1 = Figure((50.0, 50.0), dpi=self.dpi, facecolor=self.mplbg, edgecolor=self.mplbg)
		self.canvas1 = FigureCanvas(self.fig1)
		self.canvas1.setParent(self.graph1)
		self.canvas1.setMinimumSize(80, 60)
		self.axes1 = self.fig1.add_axes([0.09, 0.07, 0.85, 0.9])
		splitter2.addWidget(self.canvas1)
		self.refresh_graph1()
		
		# Graph 2
		self.graph2 = QtGui.QWidget()
		self.fig2_have_colorbar = False
		self.fig2 = Figure((50.0, 50.0), dpi=self.dpi, facecolor=self.mplbg, edgecolor=self.mplbg)
		self.canvas2 = FigureCanvas(self.fig2)
		self.canvas2.setParent(self.graph2)
		self.canvas2.setMinimumSize(80, 60)
		self.axes2 = self.fig2.add_axes([0.09, 0.07, 0.85, 0.9])
		splitter2.addWidget(self.canvas2)
		self.refresh_graph2()

		## Steuerungsboxen
		
		self.activationGroup = QtGui.QGroupBox('activation', self)
		self.gridActivation = QtGui.QGridLayout()
		self.gridActivation.setHorizontalSpacing(0)
		self.activationGroup.setLayout(self.gridActivation)
		self.checkboxes_spectra = []
		for i in range(len(self.spektren)):
			c = QtGui.QCheckBox(self)
			c.setMinimumWidth(14)
			c.setMinimumHeight(14)
			c.setChecked(True)
			c.setText(self.spektren[i][0])
			self.checkboxes_spectra.append(c)
			n = 10 # boxes per line
			self.gridActivation.addWidget(c, i/n, i%n)
			self.connect(c, QtCore.SIGNAL('toggled(bool)'), self.check_spectra)
		splitter1.addWidget(self.activationGroup)
		
		



	def loadSpektra(self, path):
		print "loading spectra from", path, "...",
		spektren = []
		filenames = []
		# find filenames
		for i in os.walk(path):
			filenames.append(i[2])
		filenames = filenames[0]
		i = 0
		while i < len(filenames):
			if filenames[i][-4:] != ".dat": del filenames[i]
			else: i += 1
		# load files
		for fname in filenames:
			data = readdata(path + "/" + fname)
			lamb = sc.array([i[0] for i in data])
			I = sc.array([i[1] for i in data])
			intensity = I.mean()
			lmean = sc.dot(lamb, I) / I.sum()
			spektren.append([fname[:-4], lamb, I, intensity, lmean])
		# sort spectry by mean wavelength
		permut = sc.array([i[4] for i in spektren]).argsort()
		spektren = [spektren[i] for i in permut]
		print "done"
		return spektren
	
	
	
	def center (self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
	
	
	
	def draw_initial1(self):
		## zeichnet den Startbildschirm
		self.axes1.set_xlim(self.xrange)
		self.axes1.grid()
		self.axes1.set_xlabel('wavelength $\\lambda$ [nm]')
		self.axes1.set_ylabel('I [mA]')
		
		
		
	def draw_initial2(self):
		## zeichnet den Startbildschirm
		self.axes2.grid()
		self.axes2.set_xlabel('wavelength $\\lambda$ [nm]')
		self.axes2.set_ylabel('led')
	
	
	
	def refresh_graph1(self):
		## aktualisiert den Graph1
		self.axes1.clear()
		self.draw_initial1()
		# draw inactive leds
		for i in range(len(self.spektren)):
			if self.active[i]: continue
			sp = self.spektren[i]
			col = spectral(sp[4], bgcolor=(0., 0., 0.))
			col = tuple([.9 + .1 * col[i] for i in range(3)])
			self.axes1.plot(sp[1], sp[2], "-", color=col, linewidth=1)
		# draw active leds
		for i in range(len(self.spektren)):
			if not self.active[i]: continue
			sp = self.spektren[i]
			col = spectral(sp[4], bgcolor=(0., 0., 0.))
			self.axes1.plot(sp[1], sp[2], "-", color=col, linewidth=1)
		self.axes1.set_xlim(self.xrange) 
		#ymin, ymax = self.axes1.get_ylim()
		#self.axes1.set_ylim(ymin=-0.05*ymax)
		self.axes1.set_ylim(-0.25, 5.)
		self.canvas1.draw()
	
	
	
	def refresh_graph2(self):
		## aktualisiert den Graph2
		self.axes2.clear()
		#self.fig2.clf()
		self.draw_initial2()
		#self.axes2.imshow(self.A[self.active], aspect="auto", interpolation="nearest", cmap=cm.gray)
		self.axes2.imshow(self.A[self.active], aspect="auto", interpolation="nearest")
		self.axes2.set_xticklabels(range(int(self.spektren[0][1][0])-100, int(self.spektren[0][1][0])+500, 100))
		if not self.fig2_have_colorbar:
			self.fig2.colorbar(self.axes2.get_images()[0], fraction=.06, pad=.02)
			self.fig2_have_colorbar = True
		self.canvas2.draw()
	
	
	
	def refresh(self):
		self.refresh_graph1()
		self.refresh_graph2()
	
	
	
	def printout(self):
		print "-- auswahl --"
		for i in range(len(self.spektren)):
			if self.active[i]:
				print self.spektren[i][0], "  \tStrom ca. {0:.4f} mA".format(self.spektren[i][3])
		print
				
	
	
	def check_spectra(self, checked):
		changed = False
		for i in range(len(self.checkboxes_spectra)):
			if self.checkboxes_spectra[i].isChecked() != self.active[i]:
				self.active[i] = self.checkboxes_spectra[i].isChecked()
			changed = True
		if changed:
			self.printout()
			self.refresh()


