# -*- coding:utf8 -*-

# Graphische Oberfläche für einen Spektrumanalyzer
# verwendet Qt4 und Pylab
# benötigte Pakete: python-qt4, pyqt-tools

# 01012010 ppg5

import sys, signal, random, time, os, threading

from PyQt4 import QtGui
from PyQt4 import QtCore

import scipy as sc
from math import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from spectral_calc import *

myrand = [random.random() for i in xrange(3*5)]
         
class FormSpectral (threading.Thread, QtGui.QWidget):
	def __init__ (self, parent=None):
		QtGui.QWidget.__init__ (self, parent)
		threading.Thread.__init__(self)
		
		self.rlock = threading.Condition()
		
		
		## Fenstereigenschaften:
		self.setWindowTitle('spectral analyzer 0.5')
		self.resize(800, 500)
		self.center()
		self.setWindowIcon(QtGui.QIcon('icons/spectrum.png'))

		## Buttons/Widgets:
		self.signature = QtGui.QLabel('(c) ppg5', self)
		
		self.refresh = QtGui.QPushButton('refresh', self)
		self.refresh.setFocusPolicy(QtCore.Qt.NoFocus)
		self.connect(self.refresh, QtCore.SIGNAL('clicked()'), self.refresh_graph)
		
		self.darkframe = QtGui.QPushButton('dark frame', self)
		self.darkframe.setFocusPolicy(QtCore.Qt.NoFocus)
		self.connect(self.darkframe, QtCore.SIGNAL('clicked()'), self.take_dark_frame)
		
		self.continuous = QtGui.QCheckBox('continuous mode', self)
		self.continuous.setFocusPolicy(QtCore.Qt.NoFocus)
		#self.continous.toggle();	# beginne aktiviert
		self.connect(self.continuous, QtCore.SIGNAL('stateChanged(int)'), self.toggle_continuous)

		self.smoothlabel = QtGui.QLabel(u"Glättung:", self)
		self.smoothset = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.smoothset.setToolTip(u"Stärke der Funktionsglättung")
		self.smoothset.setSliderPosition(60)
		
		self.graph = QtGui.QWidget()
		self.dpi = 70
		self.mplbg = 239.0/255.0, 235.0/255.0, 231.0/255.0
		self.fig = Figure((50.0, 50.0), dpi=self.dpi, facecolor=self.mplbg, edgecolor=self.mplbg)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.graph)
		self.axes = self.fig.add_subplot(111)
		self.draw_initial()
				
		## Platziere Elemente:
		self.settingsGroup = QtGui.QGroupBox('settings', self)
		self.vboxSettings = QtGui.QVBoxLayout()
		self.vboxSettings.addWidget(self.refresh)
		self.vboxSettings.addWidget(self.darkframe)
		self.vboxSettings.addWidget(self.continuous)
		self.vboxSettings.addWidget(self.smoothlabel)
		self.vboxSettings.addWidget(self.smoothset)
		self.vboxSettings.addStretch(1)
		self.vboxSettings.addWidget(self.signature)
		self.settingsGroup.setLayout(self.vboxSettings)
		
		self.main_hbox = QtGui.QHBoxLayout()
		self.main_hbox.addStretch(1)
		self.main_hbox.addWidget(self.canvas)
		self.main_hbox.addWidget(self.settingsGroup)
		self.setLayout(self.main_hbox)

		## Spektren Berechnung vorbereiten
		self.spec = DataSpectral()
		
	def center (self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
		
	def draw_initial (self):
		## zeichnet den Startbildschirm

		boarder = self.axes.plot([300,700],[0,1.1], "w+")         
		self.axes.grid()
		self.axes.set_xlabel('wavelength $\\lambda$ [nm]')
		self.axes.set_ylabel('relative spectral power distribution')


	def refresh_graph (self):
		## aktualisiert den Graphen
		
		self.axes.clear()
		boarder = self.axes.plot([300,700],[0,1.1], "w+")         
		self.axes.grid()
		self.axes.set_xlabel('wavelength $\\lambda$ [nm]')
		self.axes.set_ylabel('relative spectral power distribution')

		# Erzeuge ein Testsignal
		testfunc = sc.array([0. for i in self.spec.lambdas])
		for i in range(len(myrand) / 3):
			testfunc = testfunc + .5*myrand[i/3] * sc.array(sc.exp(
			-((self.spec.lambdas - (400. + 300 * myrand[1+i/3])) / (10.+200.*myrand[2+i/3]))**2))
		testfunc /= max(testfunc)

		self.axes.plot(self.spec.lambdas, testfunc, "b--", linewidth=4, label="Testspektrum")
		testsignal = self.spec.make_signal(testfunc)
		# Signal verrauschen
		testsignal = sc.array([random.gauss(1.,.003) * i for i in testsignal])

		T = [0., 0.]; bbspec = self.spec.spectrum_blackbody(testsignal, T)
		self.axes.plot(self.spec.lambdas, bbspec,
			"-", color="#00ee00", linewidth=4,
			label=u"Blackbody $T=%i\,\mathrm{K}$" % (int(T[1]), ))

		self.axes.plot(self.spec.lambdas,
			self.spec.spectrum_leastsqr(testsignal,
			exp(-40.+.8*(self.smoothset.value()))), "r-", linewidth=4,
			label="aus LED-Signal errechnet")

		self.axes.legend(loc="best")
		self.axes.set_ylim(-.1, 1.3)

		# Testausgabe:
		#self.axes.plot([300,350,400,450,500,550,600,650,700],[random.random() for i in xrange(9)])

		self.canvas.draw()


	def toggle_continuous (self):
		## de/aktiviert automatische Aktualisierung

		if not self.is_alive():
			self.pause_continuous = True
			self.start()
		
		self.pause_continuous = not self.pause_continuous
		
		
	def take_dark_frame (self):
		## nimmt Dunkelbild auf
		
		print "dark: not implemented yet"
		
	def run (self):
		while 1:
			if not self.pause_continuous:
				self.refresh_graph()
				time.sleep(0.1)
			else:
				time.sleep(0.1)
		

