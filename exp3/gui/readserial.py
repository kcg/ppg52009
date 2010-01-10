# -*- coding:utf8 -*-

# liest Daten von der seriellen Schnittstelle
# benötigtes Paket: python-serial
# 10012010 ppg5

import sys, os, time, serial

class ReadSerial ():
	def __init__ (self):
	
		self.baudrate		= 9600
		self.read_delay 	= 0.2
		self.adc_upper_limit	= 1000
		self.adc_lower_limit	= 30
		self.data_lenght	= 100
		
		self.ser = serial.Serial(0, self.baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, \
			stopbits=serial.STOPBITS_ONE, timeout=1, xonxoff=0, rtscts=0)
			
		# Teste Hardware:	
		self.ser.write("?")
		time.sleep(0.1)
		if "spectral" in self.ser.read(10):
			# Teste korrekte Verstärker-Einstellung:
			self.ser.write(".")
			time.sleep(0.1)
			if int(self.ser.read(10)) > self.adc_upper_limit:
				print ("Einstellungen für AREF fehlerhaft!")
		else:
			print "Hardware nicht angeschlossen!"
			self.ser.close()

		
	def get_data ():
		# Gibt Intensitätswerte der Leds zurück
		# Format:	[I(led0), I(led1), ..., I(led15)]
		
		self.ser.write("!")
		time.sleep(self.read_delay)
		self.data = self.ser.read(self.data_lenght)
		self.data = self.data.split(".")
		self.data = [int(self.data[i]) for i in xrange(len(self.data))]
		return self.data
		
	def close_port ():
		self.ser.close()		
