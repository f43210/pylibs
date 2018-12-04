# -*- coding:utf-8 -*-f
# Created by Fang tianlei

import getopt
import sys
import os
import move

def png8(dir):
	if not os.path.isdir(dir):
		return
	files = os.listdir(dir)
	for f in files:
		fp = os.path.join(dir, f)
		if os.path.isdir(fp) and (not f.startswith(".")):
			png8(fp)
		elif fp.endswith(".png"):
			os.system("pngquant --force --skip-if-larger --ext .png " + fp)
			print(fp, "   -----ok")
if __name__ == "__main__":
	opts, args = getopt.getopt(sys.argv[1:], "l:", [])
	root = "cocosstudio"
	for option, value in opts:
		if option in ["-l"]:
			root = value
	png8(root)