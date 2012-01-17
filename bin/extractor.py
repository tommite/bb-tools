#!/usr/bin/python

###
#   This file is part of bb-tools.
#
#   (c) Damir Vandic and Tommi Tervonen, 2011.
#
#   bb-tools is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   bb-tools is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with bb-tools.  If not, see <http://www.gnu.org/licenses/>.
###

import csv
import os
import re
import shutil
import sys
import getopt
import zipfile

tempFolder = './temp-extractor-bb'

def usage():
	print """usage: extractor.py -z <zipFile> -o <targetDir> -g <groupsFile>
	<zipFile> is the source zipfile to extract
	<targetDir> is the target destination for the groups (must not exist)
	<groupsFile> is the file that defines the groups

	-z zipfile to extract
	-o target location
	-g group text file, having format: STUDENT_ID,GROUP_ID

	long options also work:
	--zipfile=<zipFile>
	--outdir=<targetDir>
	--groups=<groupsFile>"""


def extractResources(zipsource, dir = tempFolder):
	if not dir.endswith(':') and not os.path.exists(dir):
		os.mkdir(dir)
	zf = zipfile.ZipFile(zipsource)
	zf.extractall(path = dir)


def moveFiles(resultdest):
	"""
	moves all files to the corresponding students' folders
	"""
	unknownIndex = 1
	if not os.path.exists(resultdest):
		os.makedirs(resultdest)
	dirList = os.listdir(tempFolder)
	p = re.compile('\d{6}[a-z]{2}', re.IGNORECASE)
	path = ""
	for fname in dirList:
		uname = p.findall(fname)
		if len(uname) == 0:
			uname = 'UNKNOWN_' + str(unknownIndex)
			unknownIndex = unknownIndex + 1
		else:
			uname = uname[0][:6]
		path = resultdest + "/" + uname
		if not os.path.exists(path):
			os.makedirs(path)

		f = tempFolder + "/" + fname
		fnew = path + "/" + fname
		shutil.move(f, fnew)


def renameFiles(path, filesList):
	i = 0
	fnew = ""

	zipfound = False
	
	for f in filesList:
		i = f.find('attempt')
		fnew = f[i:]
		i = fnew.rfind('_')
		fnew = fnew[(i + 1):]
		f = path + "/" + f
		fnew = path + "/" + fnew
		if fnew.endswith("zip"):
			shutil.move(f, fnew)
		elif f.endswith("zip"):
			fnew = f
		if fnew.endswith("zip"):
			extractResources(fnew, path)
			zipfound = True
	return zipfound


def filterStudentFiles(resultdest):
	dirList = os.listdir(resultdest)
	withZip = []
	withoutZip = []
	for fname in dirList:
		filesList = os.listdir(resultdest + "/" + fname)
		if renameFiles(resultdest + "/" + fname, filesList):
			withZip.append(fname)
		else:
			withoutZip.append(fname)
	return {'zip':withZip, 'nozip':withoutZip}


def groupFolders(resultdest, groupDict):

	dirList = os.listdir(resultdest)
	g = ""
	for fname in dirList:
		g = "UNKNOWN"
		if groupDict.has_key(fname):
			g = groupDict[fname]
		groupPath = resultdest + "/" + g
		if not os.path.exists(groupPath): os.mkdir(groupPath)
		shutil.move(resultdest + "/" + fname, groupPath + "/" + fname)


def main():
	shortargs = 'hz:o:g:'
	longargs = ['help', 'zipfile=', 'outdir=', 'groups=']
	try:
		opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	zipsource = ""
	resultdest = ""
	groupFile = ""
	for o, a in opts:
		if o in ("-z", "--zipfile"):
			zipsource = a
		elif o in ("-o", "--outdir"):
			resultdest = a
		elif o in ("-g", "--group"):
			groupFile = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()

	if zipsource == "" or resultdest == "" or resultdest == "":
		usage()
		sys.exit(1)

	if os.path.exists(resultdest):
		print "Error: target directory {} exists (remove and re-try)".format(resultdest)
		sys.exit(1)

	csvReader = csv.reader(open(groupFile), delimiter = ',')
	groupDict = {}
	userDict = {}
	
	for line in csvReader:
		groupDict[line[0]] = line[1]
  		if not line[1] in userDict.keys():
			userDict[line[1]] = [line[0]]
		else:
			arr = userDict[line[1]]
			arr.append(line[0])
			userDict[line[1]] = arr

	extractResources(zipsource)
	moveFiles(resultdest)
	zipInfo = filterStudentFiles(resultdest)
	groupFolders(resultdest, groupDict)
	shutil.rmtree(tempFolder)
	print "==="
	print "Submissions with zip (files extracted, total {}):".format(len(zipInfo['zip'])),
	for ug in sorted(getUsersWithGroups(zipInfo['zip'], groupDict)):
		print ug,
	print "\n---"
	print "Submissions without zip (total {}):".format(len(zipInfo['nozip'])),
	for ug in sorted(getUsersWithGroups(zipInfo['nozip'], groupDict)):
		print ug,
	print "\n==="

def getUsersWithGroups(users, groupDict):
	groups = set(groupDict.values())
	groups.add("UNKNOWN")
	res = []
	for user in users:
		group = "UNKNOWN"
		if groupDict.has_key(user):
			group = groupDict[user]
		res.append(group+"/"+user)
	return res


if __name__ == '__main__': main()
