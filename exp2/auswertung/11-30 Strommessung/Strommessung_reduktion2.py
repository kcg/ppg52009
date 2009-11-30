#! /usr/bin/env python
# -*- coding: utf8 -*-

# Entfernt unnötige zehnfache Einträge
# Wandelt , zu .
# Entfernt die NAN Spalte

colsep="\t"; comment="#"
ifile = open("Strommessung_reduzuert.txt", "r")
ofile = open("11-30_strommessung.txt", "w")

ofile.writelines(["# Spalte1: Zeit [s]\n",
"# Spalte2: Zellspannung [mV]\n",
"# Spalte3: Spulenstrom [A]\n",
"# Spalte4: Magn. Flussdichte [mT]\n",
"# Spalte5: Widerstand [kOhm]\n"])

for linetext in ifile.readlines():
	if linetext[0] == comment:
		continue
	linetext = linetext[:-1]
	linetext = linetext.replace(",", ".")
	line = linetext.split(colsep)
	if len(line) <= 0:
		continue
	row = []
	# Erstes token muss eine Zahl sein
	# nimm nur ganzzahlige Werte, keine mit 0,1
	try:
		x = float(line[0])
		if abs(x - round(x)) < 0.05:
			# Spalte ok => ausgeben
			line_new = []
			for i in range(len(line)):
				try:
					x = float(line[i])
					if x == x: # False wenn x=NAN
						if (i == 0):
							line_new.append(str(int(round(x))))
						else:
							line_new.append(str(x))
				except ValueError:
					pass
			if int(line_new[0]) < 198:
				line_new.append("%.2f" % (100.,))
			elif int(line_new[0]) < 547:
				line_new.append("%.2f" % (1./(1./100. + 1./100.),))
			elif int(line_new[0]) < 1213:
				line_new.append("%.2f" % (1./(1./100. + 1./50.),))
			elif int(line_new[0]) < 2354:
				line_new.append("%.2f" % (1./(1./100. + 1./20.),))
			elif int(line_new[0]) < 4121:
				line_new.append("%.2f" % (1./(1./100. + 1./14.),))
			elif int(line_new[0]) < 5438:
				line_new.append("%.2f" % (1./(1./100. + 1./10.),))
			elif int(line_new[0]) < 6627:
				line_new.append("%.2f" % (1./(1./100. + 1./7.),))
			elif int(line_new[0]) < 8281:
				line_new.append("%.2f" % (1./(1./100. + 1./5.),))
			elif int(line_new[0]) < 9028:
				line_new.append("%.2f" % (1./(1./100. + 1./2.),))
			elif int(line_new[0]) < 9512:
				line_new.append("%.2f" % (1./(1./100. + 1./1.),))
			else:
				line_new.append("%.2f" % (1./(1./100. + 1./.5),))

			for i in range(len(line_new) - 1):
				ofile.write(line_new[i] + "\t")
			ofile.write(line_new[-1] + "\n")
		continue
	except ValueError:
		continue




