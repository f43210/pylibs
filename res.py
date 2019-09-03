# -*- coding:utf-8 -*-f
import win32com.client
import os
import getopt
import re
import sys
from shutil import copyfile
import shutil
import lib

FROM 	= ""
TO		= ""
CHECK_PROCESSS 		= ["CocosStudio.exe", "webstorm64.exe"]
CHECK_PROCESS_NAME 	= ["CocosStudio", "WebStorm"]
clientDir = "../../" +  os.path.basename(os.path.abspath('..')).replace("uiResources","Client")
clientResDir = clientDir + "/res"
ccsDir = "cocosstudio"
ccsDirLocal = ccsDir + "/"
bakExt = ".mbak"
jsList = []
csdList = []

def processCheck():
	for i in range(0, len(CHECK_PROCESSS)):
		process = CHECK_PROCESSS[i]
		WMI = win32com.client.GetObject('winmgmts:')
		processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process)
		if len(processCodeCov) > 0:
			isExit = input('"%s" is running, CLOSE it?   (y/n)\n' % CHECK_PROCESS_NAME[i])
			if lib.isyes(isExit):
				 os.system('taskkill /F /IM %s' % process)
			else:
				quit()
def help():
	quit()
def clearbak():
	lib.rmFilesWithExt(ccsDir, bakExt, True)
	lib.rmFilesWithExt(clientDir, bakExt, False)
	lib.rmFilesWithExt(os.path.join(clientDir, "src"), bakExt, True)
def moveFile(ccsfrom, ccsto):
	ccsfrom = ccsfrom.replace("\\", "/")
	ccsto = ccsto.replace("\\", "/")
	reffrom = ccsfrom.replace(ccsDirLocal, "", 1)
	refto = ccsto.replace(ccsDirLocal, "", 1)
	clientfrom = clientResDir + "/" + reffrom
	creffrom = "res/" + reffrom
	clientto = clientResDir + "/" + refto
	crefto = "res/" + refto
	basefram = os.path.basename(ccsfrom)
	baseto = os.path.basename(ccsto)

	if os.path.isdir(ccsto) or os.path.isdir(ccsfrom):
		print('err')
		quit()
	if lib.fileExt(ccsfrom) != lib.fileExt(ccsto):
		print("MUST not change the file's ext-name")
		quit()

	# replace all CocosStudio res reference
	for idx in range(0, len(csdList)):
		csd = csdList[idx]
		f = open(csd, "r", encoding='UTF-8')
		oldContent = f.read()
		f.close
		newContent = oldContent.replace(reffrom, refto)
		if oldContent != newContent:
			# bak file to .mbak
			copyfile(csd, csd + bakExt)
			with open(csd, "w", encoding='UTF-8') as f:
				f.write(newContent)
	# replace all js reference
	fromKey = lib.fileKey(creffrom)

	fromDirKey = lib.fileKey(os.path.dirname(creffrom))
	toDirKey = lib.fileKey(os.path.dirname(crefto))
	fromKeyXZK = fromKey.replace(fromDirKey, 'xuzhikunnumberone');
	rNum = re.compile(r'\d+')
	fromKeyR = rNum.sub(r'[\\d\{\}]+', fromKeyXZK)
	fromKeyR = fromKeyR.replace('xuzhikunnumberone', fromDirKey)
	if fromKey != fromKeyR:
		checkSpecial = True
		rNum1 = re.compile(fromKeyR)
	else:
		checkSpecial = False
	print(fromKey)
	print(fromDirKey)
	print(fromKeyXZK)
	print(fromKeyR)
	print(checkSpecial)
	print(toDirKey)

	toKey = lib.fileKey(crefto)
	for idx in range(0, len(jsList)):
		js = jsList[idx]
		f = open(js, "r", encoding='UTF-8')
		oldContent = f.read()
		f.close
		newContent = oldContent.replace(creffrom, crefto)
		newContent = newContent.replace(fromKey, toKey)
		if basefram == baseto:
			# check special ref if the key has num
			if checkSpecial:
				fromMatch = rNum1.search(newContent)
				while fromMatch:
					group = fromMatch.group()
					rgroup = group.replace(fromDirKey, toDirKey, 1)
					print("special replace:", group, "===>", rgroup)
					newContent = newContent.replace(group, rgroup)
					fromMatch = rNum1.search(newContent)
		else:
			print("'%s' is renamed to '%s', skip special check!"%(reffrom, refto))

		if oldContent != newContent:
			# bak file to .mbak
			copyfile(js, js + bakExt)
			with open(js, "w", encoding='UTF-8') as f:
				f.write(newContent)
	# move file
	ccsTargetDir = os.path.dirname(ccsto)
	if not os.path.exists(ccsTargetDir):
		os.makedirs(ccsTargetDir)
	shutil.move(ccsfrom, ccsto)

def moveDir(_from, _to):
	for f in os.listdir(_from):
		fPath = os.path.join(_from, f)
		tPath = os.path.join(_to, f)
		if os.path.isdir(fPath):
			if f.startswith("."):
				if not os.path.exists(_to):
					os.makedirs(_to)
				os.rename(fPath, tPath)
			else:
				moveDir(fPath, tPath)
		else:
			moveFile(fPath, tPath)
	os.rmdir(_from)

def initPath(p):
	idx = p.find('/cocosstudio/')
	if idx == -1:
		idx = p.find('\\cocosstudio\\')
	if idx > -1:
		p = p[(idx + 13):]
	return os.path.join(ccsDir, p)

stateMarkDict = {False: "(-)", True: "(+)"}
def printConstruct(_path, _blank, isAdd = None):
	basename = os.path.basename(_path)
	blankLen = 20 - len(basename)
	if blankLen < 0:
		blankLen = 0
	if isAdd == None:
		if os.path.exists(_path):
			print(_blank, basename)
		else:
			print(_blank, basename, lib.lineList[blankLen], stateMarkDict[True])
		_blank = _blank + lib.blankList[len(basename)]
		print(_blank, "|")
	else:
		print(_blank, basename, lib.lineList[blankLen], stateMarkDict[isAdd])

	return _blank
def printPath(_path, isAdd):
	_path = _path.replace("\\", "/")
	if _path.endswith('/'):
		_path = _path[0:-1]
	consts = _path.split('/')
	_curPath = ""
	_blank = ""
	_len = len(consts)
	for i in range(0, _len - 1):
		_curPath = os.path.join(_curPath, consts[i])
		if _curPath != "":
			_blank = printConstruct(_curPath, _blank)
	printConstruct(_path, _blank, isAdd)

def moveConfirm():
	print("remove list:")
	printPath(FROM, False)
	print("add list:")
	printPath(TO, True)
	isMove = input('start move?!   (y/n)\n')
	if not lib.isyes(isMove):
		quit()

if __name__ == "__main__":
	opts, args = getopt.getopt(sys.argv[1:], "f:t:h", ["from", "to", "help"])

	skipMaking = False
	for option, value in opts:
		if option in ["-h", "--help"]:
			help()
		elif option in ["-t", "--to"]:
			TO = value
		elif option in ["-f", "--from"]:
			FROM = value
	if FROM == "" or TO == "":
		quit()
	processCheck()

	FROM = initPath(FROM)
	TO = initPath(TO)

	if not os.path.exists(FROM):
		print(FROM,' not exists!!!')
		quit()

	lib.listDir("cocosstudio", [], csdList, ".csd")
	jsList.append(os.path.join(clientDir, "loaderScene.js"))
	jsList.append(os.path.join(clientDir, "main.js"))
	lib.listDir(os.path.join(clientDir, "src"), ["config", "protobuf", "root.js", "Proto.js"], jsList, ".js")


	if os.path.isdir(FROM):
		if not (FROM.endswith("/") or FROM.endswith("\\")):
			TO = os.path.join(TO, os.path.basename(FROM))
		moveConfirm()
		moveDir(FROM, TO)
	else:
		if lib.fileExt(FROM) != lib.fileExt(TO):
			TO = os.path.join(TO, os.path.basename(FROM))
		moveConfirm()
		moveFile(FROM, TO)

	clearbak()
