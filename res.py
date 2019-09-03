#coding=utf-8

import sys
import os
import json
import getopt
import shutil
import subprocess
import ftplib
import platform
import lib
# reload(sys)
# sys.setdefaultencoding('utf-8')

CONTENT_STR = """/** This file is automatically generated by createResourceJs.py script.
Do not modify this file -- YOUR CHANGES WILL BE ERASED! **/
var resources = {
    __CONTENT_REPLACE__
};
_g.resources = resources;"""
Str1 = """
	__key__: "__path__",__blank__//count=__count__,  sameFiles=__same__"""
rkey = "__key__"
rpath = "__path__"
rcount = "__count__"
rsame = "__same__"
rblank = "__blank__"
def copyFiles(fromDir, toDir, exts=None):
	if not os.path.exists(toDir):
		os.mkdir(toDir)
	for f in os.listdir(fromDir):
		if f.startswith(".") or f.endswith("Thumbs.db"):
			continue
		src = os.path.join(fromDir, f)
		dest = os.path.join(toDir, f)
		if os.path.isdir(src):
			copyFiles(src, dest, exts)
		else:
			if exts != None and lib.fileExt(f) not in exts:
				continue
			shutil.copy2(src, toDir)

def checkSameFiles(fileList, f):
	if "md5" not in f:
		return
	fp = f["path"]
	if not(fp.endswith(".jpg") or fp.endswith(".png")):
		return
	fMd5 = f["md5"]
	sameFiles = []
	for _f in fileList:
		if fileList[_f]["path"] != fp:
			if "md5" in fileList[_f]:
				if fileList[_f]["md5"] == fMd5:
					sameFiles.append(fileList[_f]["path"])
	if len(sameFiles) > 0:
		f["same"] = ",".join(sameFiles)

def statCount(fileList, f, k="key"):
	key = f[k]
	l = len(key)
	for _f in fileList:
		if fileList[_f]["content"].find(key) > -1:
			f["count"] = 1
		# tmp = fileList[_f]["content"].find(key)
		# while tmp > -1:
		# 	f["count"] = f["count"] + 1
		# 	tmp = fileList[_f]["content"].find(key, tmp + l)

def genResList(resList):
	ret = ""
	for k in resList:
		s = Str1
		s = s.replace(rkey, resList[k]["key"])
		s = s.replace(rpath, k)
		blankLen = 120 - 2 * len(k)
		if blankLen < 0:
			blankLen = 0
		s = s.replace(rblank, lib.blankList[blankLen])
		if resList[k]["count"] > 0:
			s = s.replace(rcount, str(resList[k]["count"]))
		else:
			s = s.replace(rcount, "1+")
		if "same" in resList[k]:
			s = s.replace(rsame, resList[k]["same"])
		else:
			s = s.replace(rsame, "[]")
		ret = ret + s
		resList[k]["newKey"] = "resources." + resList[k]["key"]
	return ret

def genResJs(isUpdateRes=True):
	if isUpdateRes:
		resRoot = "res"
		if not os.path.exists(resRoot):
			quit()
		for f in os.listdir(resRoot):
			fPath = os.path.join(resRoot, f)
			if os.path.isdir(fPath):
				shutil.rmtree(fPath)
		copyFiles("../" + os.path.basename(os.getcwd()).replace("Client","uiResources") + "/gragonball/cocosstudio", "res", [".png", ".mp3", ".atlas", ".json", ".plist"])
	jsList = {}
	expJsArray = [
		"src/protobuf",
		"src/config",
		"src/lib/Proto.js",
		"src/base/Resources.js"
	]
	jsFiles = []
	lib.listDir("src", expJsArray, jsFiles, ".js")
	for i in range(0, len(jsFiles)):
		fp = jsFiles[i]
		jsList[fp] = {}
		with open(fp, "r", encoding='UTF-8') as f:
			jsList[fp]["content"] = f.read()
	jsonFiles = []
	expJsonArray = [
		"res/audio",
		"res/bigImage",
		"res/font",
		"res/h5",
		"res/particle",
		"res/plists",
		"res/png",
		"res/spine",
		"res/games"
	]
	lib.listDir("res", expJsonArray, jsonFiles, ".json", False)
	jsonList = {}
	for i in range(0, len(jsonFiles)):
		fp = jsonFiles[i]
		jsonList[fp] = {}
		jsonList[fp]["path"] = fp
		jsonList[fp]["key"] = lib.fileKey(fp)
		jsonList[fp]["count"] = 0
		with open(fp, "r", encoding='UTF-8') as f:
			jsonList[fp]["content"] = f.read()
		statCount(jsList, jsonList[fp])
	resFiles = []
	lib.listDir("res", jsonFiles, resFiles)
	lib.listDir("src/config", [], resFiles)
	resList = {}
	for i in range(0, len(resFiles)):
		fp = resFiles[i]
		resList[fp] = {}
		resList[fp]["path"] = fp[4:]
		resList[fp]["key"] = lib.fileKey(fp)
		resList[fp]["count"] = 0
		if fp.endswith(".jpg") or fp.endswith(".png"):
			resList[fp]["md5"] = lib.getMd5(fp)
		statCount(jsonList, resList[fp], "path")
	for k in resList:
		if resList[k]["count"] == 0:
			statCount(jsList, resList[k])
		# else:
		# 	resList[k]["count"] = 999
		checkSameFiles(resList, resList[k])
	mapStr = ""
	mapStr = mapStr + genResList(jsonList)
	mapStr = mapStr + genResList(resList)
	ContentStr = CONTENT_STR.replace("__CONTENT_REPLACE__", mapStr)
	with open("src/base/Resources.js", "w", encoding='UTF-8') as f:
		f.write(ContentStr)