#! /usr/bin/env python
# -*- coding: utf8 -*-

# Entfernt unnötige zehnfache Einträge
# Wandelt , zu .
# Entfernt die NAN Spalte

colsep="\t"; comment="#"
ifile = open("Strommessung.txt", "r")
ofile = open("Strommessung_reduzuert.txt", "w")

ofile.writelines(["# Spalte1: Zeit [s]\n",
"# Spalte2: Zellspannung [mV]\n",
"# Spalte3: Spulenstrom [A]\n",
"# Spalte4: Magn. Flussdichte [mT]\n"])

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
			for i in range(len(line_new) - 1):
				ofile.write(line_new[i] + "\t")
			ofile.write(line_new[-1] + "\n")
		continue
	except ValueError:
		continue




