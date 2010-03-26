# -*- coding: utf8 -*-



def readdata(filename, colsep="\t", comment="#"):
	'''
	reads floating-point data from a file
	'''
	ifile = open(filename, "r")
	data = []; l = 0
	for linetext in ifile.readlines():
		l += 1
		if linetext[0] == comment: continue
		linetext = linetext[:-1].strip()
		line = linetext.split(colsep)
		if len(line) <= 0: continue
		if line == ['']: continue
		row = []
		for i in line:
			try:
				x = float(i.replace(",", "."))
				row.append(x)
			except ValueError:
				print 'File "' + filename + '",',
				print 'line ' + str(l) + ':',
				print '"' + i + '" is not a float'
				row.append(0.)
		data.append(row)
	return(data)
