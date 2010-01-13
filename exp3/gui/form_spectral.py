# -*- coding:utf8 -*-

# Graphische Oberfläche für einen Spektrumanalyzer
# verwendet Qt4 und Pylab
# benötigte Pakete: python-qt4, pyqt-tools

# 01012010 ppg5

import sys, signal, random, time, os, threading

from PyQt4 import QtGui
from PyQt4 import QtCore

import pylab as pl
import scipy as sc
import scipy.optimize as op
from math import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from spectral_calc import *
from simulation import *
from color_spectral import spectral

         
class FormSpectral (threading.Thread, QtGui.QWidget):
	def __init__ (self, parent=None):
		QtGui.QWidget.__init__ (self, parent)
		threading.Thread.__init__(self)

		self.pause_continuous = True
		
		
		## Fenstereigenschaften:
		self.setWindowTitle('spectral analyzer 0.6')
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
		
		self.saveplot = QtGui.QPushButton('save plot', self)
		self.saveplot.setFocusPolicy(QtCore.Qt.NoFocus)
		self.connect(self.saveplot, QtCore.SIGNAL('clicked()'), self.save_plot)
		
		self.continuous = QtGui.QCheckBox('continuous mode', self)
		self.continuous.setFocusPolicy(QtCore.Qt.NoFocus)
		#self.continous.toggle();	# beginne aktiviert
		self.connect(self.continuous, QtCore.SIGNAL('stateChanged(int)'), self.toggle_continuous)

		# Modus Auswahl
		self.msGroup = QtGui.QGroupBox(u"mode", self)
		self.vboxMs = QtGui.QVBoxLayout()
		self.msGroup.setLayout(self.vboxMs)
		self.radio_measure = QtGui.QRadioButton(u"measure", self)
		self.radio_simulate = QtGui.QRadioButton(u"simulate", self)
		self.vboxMs.addWidget(self.radio_measure)
		self.vboxMs.addWidget(self.radio_simulate)
		self.radio_simulate.setChecked(True)
		self.connect(self.radio_measure, QtCore.SIGNAL('toggled(bool)'), self.toggle_mode_ms)
		self.connect(self.radio_simulate, QtCore.SIGNAL(
			'toggled(bool)'), self.toggle_mode_ms)

		# Rekonstruktionsmethode
		self.cboxMethod = QtGui.QComboBox(self)
		self.cboxMethod.addItem(u"exact+smooth")
		self.cboxMethod.addItem(u"pseudo-inverse")
		self.cboxMethod.addItem(u"optimize")
		self.cboxMethod.addItem(u"least-square")
		self.cboxMethod.addItem(u"blackbody")
		self.cboxMethod.addItem(u"polynomial")
		self.cboxMethod.addItem(u"spline")

		# Schieber für Glättungsintensität
		self.labelSmooth = QtGui.QLabel(u"smoothing:", self)
		self.sliderSmooth = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.sliderSmooth.setToolTip(u"Stärke der Funktionsglättung")
		self.sliderSmooth.setMaximum(100)
		self.sliderSmooth.setSliderPosition(60)

		# Einstellungen der Datensimulation
		self.simGroup = QtGui.QGroupBox(u"simulation", self)
		self.vboxSim = QtGui.QVBoxLayout()
		self.simGroup.setLayout(self.vboxSim)
		self.simButton = QtGui.QPushButton(u"new spectrum", self)
		self.vboxSim.addWidget(self.simButton)
		self.connect(self.simButton, QtCore.SIGNAL('clicked()'), self.sim_spec)
		self.sliderNoise = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.sliderNoise.setMaximum(100)
		self.sliderNoise.setSliderPosition(10)
		self.valueNoise = QtGui.QLabel(u"noise: " + str(round(self.noise_from_slider(),5)),self)
		self.connect(self.sliderNoise, QtCore.SIGNAL('valueChanged(int)'), self.noise_from_slider)
		self.vboxSim.addWidget(self.valueNoise)
		self.vboxSim.addWidget(self.sliderNoise)

		# Graph (Spektrum)
		self.graph = QtGui.QWidget()
		self.dpi = 70
		self.mplbg = self.palette().background().color().getRgbF()
		self.fig = Figure((50.0, 50.0), dpi=self.dpi, facecolor=self.mplbg, edgecolor=self.mplbg)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.graph)
		self.axes = self.fig.add_axes([0.1, 0.35, 0.8, 0.6])#add_subplot(211)
		self.axes2 = self.fig.add_axes([0.1, 0.1, 0.8, 0.15])#subplot(414) # Graph (Wellenlängen-Signal)
		self.draw_initial()
		
		## Platziere Elemente:
		self.settingsGroup = QtGui.QGroupBox('settings', self)
		self.vboxSettings = QtGui.QVBoxLayout()
		self.vboxSettings.addWidget(self.refresh)
		self.vboxSettings.addWidget(self.darkframe)
		self.vboxSettings.addWidget(self.saveplot)
		self.vboxSettings.addWidget(self.continuous)
		self.vboxSettings.addWidget(self.msGroup)
		self.vboxSettings.addWidget(self.cboxMethod)
		self.vboxSettings.addWidget(self.labelSmooth)
		self.vboxSettings.addWidget(self.sliderSmooth)
		self.vboxSettings.addWidget(self.simGroup)
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

		self.axes.plot([300,700],[0,1.1], "w+")
		self.axes.grid()
		self.axes.set_xlabel('wavelength $\\lambda$ [nm]')
		self.axes.set_ylabel('relative spectral power distribution')
		
		self.axes2.set_xlabel('channel')
		self.axes2.set_ylabel('relative signal')


	def refresh_graph (self):
		## aktualisiert den Graphen
		
		self.axes.clear()
		self.axes2.clear()
		self.draw_initial()

		if self.radio_measure.isChecked():
			# Testausgabe:
			self.axes.plot([300,350,400,450,500,550,600,650,700],[random.random() for i in xrange(9)])
		else:
			try:
				self.simulation.make_signal(self.spec.A, self.noise_from_slider())
			except AttributeError:
				# Erzeuge ein Testsignal
				self.simulation = DataSimulation(
					self.spec.lambdas, self.spec.A, self.noise_from_slider())

			# Testsignal
			self.axes.plot(self.spec.lambdas, self.simulation.spectrum,
				"--", color="#0000ff", linewidth=4,
				label=u"test spectrum")

			if self.cboxMethod.currentText() == u"pseudo-inverse":
				y = self.spec.spectrum_pinv(self.simulation.signal)
				text = u"pseudo-inverse"
			elif self.cboxMethod.currentText() == u"least-square":
				y = self.spec.spectrum_leastsqr(self.simulation.signal,
					exp(-40.+.8*(self.sliderSmooth.value())))
				text = u"least-square"
			elif self.cboxMethod.currentText() == u"blackbody":
				T = [0., 0.]
				y = self.spec.spectrum_blackbody(self.simulation.signal, T)
				text = u"blackbody $T=%i\,\mathrm{K}$" % (int(T[1]), )
			elif self.cboxMethod.currentText() == u"polynomial":
				y = self.spec.spectrum_polynomial(self.simulation.signal)
				text = "polynomial"
			elif self.cboxMethod.currentText() == u"spline":
				y = self.spec.spectrum_spline(self.simulation.signal)
				text = "spline"
			elif self.cboxMethod.currentText() == u"exact+smooth":
				y = self.spec.spectrum_smooth(self.simulation.signal)
				text = "exact and as smooth as possible"
			elif self.cboxMethod.currentText() == u"optimize":
				y = self.spec.spectrum_optimize(self.simulation.signal,
					self.sliderSmooth.value() / float(self.sliderSmooth.maximum()))
				text = "nonlinear optimized"

			self.axes.plot(self.spec.lambdas, y, "r-", linewidth=4, label=text)
			self.axes.set_ylim(-.19, 1.4)
			self.axes.legend(loc="best")

			#Signalanzeige der einzelnen LEDs
			led_label = ["14mCd", "44kmCd", "500nm", "525nm", "570nm", "585nm", "588nm", "600nm", "620nm", "625nm", "635nm", "640nm"]
			x = [i for i in xrange(1,13)]
			y = self.simulation.signal / self.spec.weights
			maxi = max(self.simulation.signal)
			y = y / max(y)
			colors = []
			for i in range(len(led_label)):
				try:
					j = float(led_label[i][0:3])
					colors.append(spectral(j))
				except ValueError:
					colors.append(spectral(self.spec.led_colors[i]))
			#colors = [spectral(i) for i in self.spec.led_colors]
			self.axes2.bar(x, y, width=0.9, color=colors, align="center", label="max: "+str(round(maxi,2)))
			self.axes2.set_xticks(xrange(1,13), minor=False)
			self.axes2.set_xticklabels(led_label, fontdict=None, minor=False, rotation=45)
			self.axes2.legend(loc="best")

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
		
		
	def save_plot(self):
		## speichert Plot als Screenshot auf Festplatte

		#pl.gcf().set_size_inches(6, 4)
		self.fig.savefig(os.path.relpath(str(QtGui.QFileDialog.getSaveFileName(self, "save graph"))))


	def toggle_mode_ms(self, checked):
		if self.pause_continuous:
			self.refresh_graph()


	def noise_from_slider(self):
		value = .4 * (self.sliderNoise.value() / float(self.sliderSmooth.maximum()))**2
		try:
			self.valueNoise.setText(u"noise: " + str(round(value,5)))
		except:
			pass
		return value


	def sim_spec(self):
		## simuliert ein neues Spektrum
		try:
			test = self.simulation
		except AttributeError:
			# Erzeuge ein Testsignal
			self.simulation = DataSimulation(self.spec.lambdas,
				self.spec.A, self.noise_from_slider())
		else:
			self.simulation.make_spec()
			self.simulation.make_signal(self.spec.A, self.noise_from_slider())

		if self.pause_continuous:
			self.refresh_graph()

		
	def run (self):
		while 1:
			if not self.pause_continuous:
				self.refresh_graph()
			time.sleep(.5)

