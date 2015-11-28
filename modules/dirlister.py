import os

def run(**args):
	print "[*] in dirlister module"
	files=os.listdir(".");
	print str(files)
	return str(files)
