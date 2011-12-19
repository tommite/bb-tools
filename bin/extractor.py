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
	if not os.path.exists(resultdest):
		os.makedirs(resultdest)
	dirList = os.listdir(tempFolder)
	p = re.compile('\d{6}[a-z]{2}', re.IGNORECASE)
	path = ""
	for fname in dirList:
		path = resultdest + "/" + p.findall(fname)[0]
		if not os.path.exists(path):
			os.makedirs(path)

		f = tempFolder + "/" + fname
		fnew = path + "/" + fname
		shutil.move(f, fnew)


def renameFiles(path, filesList):
	i = 0
	fnew = ""
	for f in filesList:
		i = f.find('attempt')
		fnew = f[i:]
		i = fnew.rfind('_')
		fnew = fnew[(i + 1):]
		f = path + "/" + f
		fnew = path + "/" + fnew
		shutil.move(f, fnew)
		if fnew.endswith("zip"):
			extractResources(fnew, path)


def filterStudentFiles(resultdest):
	dirList = os.listdir(resultdest)
	for fname in dirList:
		filesList = os.listdir(resultdest + "/" + fname)
		renameFiles(resultdest + "/" + fname, filesList)


def groupFolders(resultdest, groupFile):
	csvReader = csv.reader(open(groupFile), delimiter = ',')
	groupDict = {}
	for line in csvReader:
		groupDict[line[0]] = line[1]

	dirList = os.listdir(resultdest)
	g = ""
	for fname in dirList:
		g = "UNKNOWN"
		if groupDict.has_key(fname[:6]):
			g = groupDict[fname[:6]]
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

	if zipsource == "" or resultdest == "" or os.path.exists(resultdest):
		usage()
		sys.exit()

	extractResources(zipsource)
	moveFiles(resultdest)
	filterStudentFiles(resultdest)
	groupFolders(resultdest, groupFile)
	shutil.rmtree(tempFolder)

if __name__ == '__main__': main()
