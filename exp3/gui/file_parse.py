# -*- coding:utf8 -*-


def readdata(filename, colsep="\t", comment="#", getFloats=True):
	ifile = open(filename, "r")
	data = []
	for linetext in ifile.readlines():
		if linetext[0] == comment:
			continue
		linetext = linetext[:-1]
		if len(linetext) <= 1:
			continue
		while linetext[-1] == " " or linetext[-1] == "\t":
			if len(linetext) == 1:
				continue
			else:
				linetext = linetext[:-1]
		line = linetext.split(colsep)
		if len(line) <= 0:
			continue
		row = []
		for i in line:
			if getFloats:
				try:
					x = float(i)
					row.append(x)
				except ValueError:
					print i, "is not a float"
					row.append(0.)
			else:
				row.append(i)
		data.append(row)
	return(data)
