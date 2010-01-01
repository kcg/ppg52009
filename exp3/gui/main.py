#! /usr/bin/env python
# -*- coding:utf8 -*-

# spectrum analyzer
# 0101210 ppg5

import sys, signal, random, time, os
from PyQt4 import QtGui
from PyQt4 import QtCore
from form_spectral import *

# Signale abfangen (Strg+C...)
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

# GUI starten:
app = QtGui.QApplication(sys.argv)
form = FormSpectral()
form.show()
sys.exit(app.exec_())
