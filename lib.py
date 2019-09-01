# encoding: utf-8
import hashlib
import os
import socket
import json
import re
import sys
import urllib.request
import itertools

# reload(sys)
# sys.setdefaultencoding('utf-8')
pattern = re.compile(r'[/.]')

blankList = {}
lineList = {}
blankList[0] = ""
lineList[0] = ""
for i in range(1, 119):
	blankList[i] = blankList[i - 1] + " "
	lineList[i] = lineList[i - 1] + "-"

def isyes(val):
	return val == 'y' or val == 'Y'
def fileExt(_f):
	if _f.endswith("\\") or _f.endswith("/"):
		return None
	else:
		return os.path.splitext(_f)[1]
def fileKey(_f):
	return pattern.sub("_", _f).lower()
def printLocalTestUrl(tag):
	ip = socket.gethostbyname(socket.gethostname())
	f = open("subGameResourceModule.json", "r", encoding='UTF-8')
	subGamesConf = json.load(f)
	f.close()
	urls = ""
	for subgame in subGamesConf:
		if subGamesConf[subgame]["id"] != "0":
			urls = urls + "http://%s/gemhunter/%s/%s \t%s的单元测试地址\n"%(ip, tag, subGamesConf[subgame]["id"], subGamesConf[subgame]["name"])
	urls = urls + "http://%s/gemhunter/%s/none \t不包含(具有独立更新)子游戏的单元测试地址\n"%(ip, tag)
	urls = urls + "http://%s/gemhunter/%s/all \t非单元测试地址\t*注：一般情况不要访问该地址\n"%(ip, tag)
	print("请把下列单元测试地址发给测试同事!\n%s"%urls)

def getFileSize(path):
	compressRatio = 1
	if path.endswith(".js") or path.endswith(".jsc") or path.endswith(".jse") or path.endswith(".plist") or path.endswith(".json") or path.endswith(".atlas"):
		compressRatio = 0.15
	return int(os.path.getsize(path) * compressRatio)

def getMd5(path):
	with open(path,'rb') as f:
		md5obj = hashlib.md5()
		md5obj.update(f.read())
		hash = md5obj.hexdigest()
		# print(path + ": " + hash)
		return hash

def listDir(root, exceptArr, result, postFix=None, deep=True):
	for item in os.listdir(root):
		filepath = root + "/" + item
		if item.startswith(".") or item.endswith("Thumbs.db"):
			continue
		if os.path.isdir(filepath):
			if deep:
				if filepath in exceptArr:
					continue
				else:
					listDir(filepath, exceptArr, result, postFix)
		else:
			if postFix == ".proto" and getFileSize(filepath) == 0:
				print("[SKIP FILE] " + filepath)
				continue
			elif filepath in exceptArr:
				continue
			else:
				if postFix is None or filepath.endswith(postFix):
					result.append(filepath)

def rmFilesWithExt(dir, ext, deep = False):
	for f in os.listdir(dir):
		fPath = os.path.join(dir, f)
		if os.path.isdir(fPath):
			if deep:
				rmFilesWithExt(fPath, ext, deep)
		elif f.endswith(ext):
			os.remove(fPath)

def compressJs(array, dst, isReleased, isDropConsole):
	command = "uglifyjs "
	for item in array:
		command += item + " "
	command += "-o " + dst
	if not(isReleased):
		command += " -b"
	else:
		command += " -m -b -c hoist_vars"
		# command += " -m -c hoist_vars"
		if isDropConsole:
			command += ",drop_console"
	print("[COMPRESSING_JS] " + command)
	os.system(command)

_jsAddedCache = {}
def getJsListOfModule(_map, mod, dir):
	if mod in _jsAddedCache:
		return []
	ret = []
	if mod not in _map:
		print("module {0} doesn't exists.".format(mod))
		quit()
	tempList = _map[mod]
	for i in range(0, len(tempList)):
		item = tempList[i]
		if item in _jsAddedCache:
			continue
		if (item.endswith(".js")):
			ret.append(dir + item)
		else:
			arr = getJsListOfModule(_map, item, dir)
			ret.extend(arr)
		_jsAddedCache[item] = True
	return ret
def getJsListOfModules(_map, mods, dir, jsList):
	global _jsAddedCache
	_jsAddedCache = {}
	for item in mods:
		arr = getJsListOfModule(_map, item, dir)
		jsList.extend(arr)

###############################xxtea start####################################
from cffi import FFI
from os.path import join, relpath, dirname
__PATH = "frameworks/cocos2d-x/external/xxtea"
__IS_XXTEA = os.path.exists(join(__PATH, 'xxtea.cpp'))
if __IS_XXTEA:
	__SOURCES = [relpath(join(__PATH, 'xxtea.cpp'))]

	ffi = FFI()
	ffi.cdef('''
	typedef long xxtea_long;
	unsigned char *xxtea_encrypt(unsigned char *data, xxtea_long data_len, unsigned char *key, xxtea_long key_len, xxtea_long *ret_length);
	''')
	# ffi.C = ffi.dlopen(None)
	xxtealib = ffi.verify('#include <xxtea.h>', sources = __SOURCES, include_dirs=[__PATH])

	if sys.version_info < (3, 0):
	    def __tobytes(v):
	        if isinstance(v, unicode):
	            return v.encode('utf-8')
	        else:
	            return v
	else:
	    def __tobytes(v):
	        if isinstance(v, str):
	            return v.encode('utf-8')
	        else:
	            return v
	def encrypt(data, key):
	    data = __tobytes(data)
	    data_len = len(data)
	    key = __tobytes(key)
	    key_len = len(key)
	    data = ffi.new('unsigned char[]', data)
	    key = ffi.new('unsigned char[]', key)
	    ret_length = ffi.new('xxtea_long *')
	    result = xxtealib.xxtea_encrypt(data, data_len, key, key_len, ret_length)
	    return ffi.buffer(result, ret_length[0])[:]
###############################xxtea end####################################

def encryDir(dir, key, ext, replaceExt = None):
	if replaceExt == None:
		replaceExt = ext
	jsList = []
	lenext = len(ext)
	listDir(dir, [], jsList, ext)
	for i in range(0, len(jsList)):
		_from = open(jsList[i], "r", encoding='UTF-8')
		_content = _from.read()
		_from.close()
		with open(jsList[i][:-lenext] + replaceExt, "wb") as _to:
			_to.write(encrypt(_content, key))
		os.remove(jsList[i])

def patch(publishDir, ip, patchRoot, user = "root"):
	print("************************start patch**************************")
	patchAssets = []
	manifests = []
	listDir(publishDir, [], manifests, "project.manifest", False)
	for i in range(0, len(manifests)):
		with open(manifests[i], "r", encoding='UTF-8') as f:
			mf = json.load(f)
		try:
			with urllib.request.urlopen(mf["remoteManifestUrl"]) as rsp:
				remotemf = json.load(rsp)
				remoteAssets = remotemf["assets"]
				for res in mf["assets"]:
					if res in remoteAssets:
						if remoteAssets[res]["md5"] != mf["assets"][res]["md5"]:
							patchAssets.append(res)
							print("[U]\t" + res)
					else:
						patchAssets.append(res)
						print("[A]\t" + res)
		except:
			for res in mf["assets"]:
				patchAssets.append(res)
				print("[A]\t" + res)
	exec_confirm = input('start patch?   (y/n)\n')
	if isyes(exec_confirm):
		dirDicts = []
		for i in range(0, len(patchAssets)):
		 	res = patchAssets[i]
		 	resdir = os.path.dirname(res)
		 	isCheck = True
		 	if resdir in dirDicts:
		 		isCheck = False
		 	else:
			 	for j in range(0, len(dirDicts)):
			 		if dirDicts[j].startswith(resdir):
			 			isCheck = False
			 			break
		 	if isCheck:
			 	os.system('ssh ' + user + "@" + ip + ' "[-d ' + patchRoot + resdir + '] && echo ok || mkdir -p ' + patchRoot + resdir + '"')
			 	dirDicts.append(resdir)
		 	os.system('scp -pv ' + publishDir + '/' + res + ' ' + user + '@' + ip + ":" + patchRoot + resdir)
		os.system('scp ' + publishDir + "/*.manifest " + user + '@' + ip + ":" + patchRoot)
		print("************************patch successed**************************")
	else:
		print("************************patch canceled**************************")
