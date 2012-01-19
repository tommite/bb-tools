#!/usr/bin/python

###
#   This file is part of bb-tools.
#
#   (c) Tommi Tervonen and Damir Vandic, 2011-12.
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
import subprocess

# constants
TEMP_FOLDER = './temp-extractor-bb'
UNKNOWN = 'UNKNOWN'
BINDIR = 'bin'
SRCDIR = 'src'
# globals
nextUnknownIndex = 1

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


def extractResources(zipsource, dir):
	if not dir.endswith(':') and not os.path.exists(dir):
		os.mkdir(dir)
	zf = zipfile.ZipFile(zipsource)
	zf.extractall(path = dir)

def renameFile(path, f):
	i = f.find('attempt')
	fnew = f[i:]
	i = fnew.rfind('_')
	fnew = fnew[(i + 1):]
	f = path + os.sep + f
	fnew = path + os.sep + fnew
	shutil.move(f, fnew)
			
def readGroups(groupFile):
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
	userDict[UNKNOWN] = []
	return {'byGroup' : userDict, 'byUser' : groupDict}

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

	gDicts = readGroups(groupFile)
	extractResources(zipsource, TEMP_FOLDER)
	os.makedirs(resultdest)
	makeGroupFolders(resultdest, gDicts['byGroup'].keys())

	dirList = os.listdir(TEMP_FOLDER) ## list files in the temp folder

	for fname in os.listdir(TEMP_FOLDER):
		processSubmission(fname, resultdest, gDicts)

	shutil.rmtree(TEMP_FOLDER)

def makeGroupFolders(resultDest, groups):
	for g in groups:
		os.makedirs(resultDest + os.sep + g)

def addStudentToUnknownGroup(student, gDict):
	gDict['byUser'][student] = UNKNOWN
	gDict['byGroup'][UNKNOWN].append(student)
	

def processSubmission(srcFile, destDir, gDicts):
	studId = getStudentID(srcFile)
	group = UNKNOWN # default group is unknown
	if (studId in gDicts['byUser'].keys()):
		group = gDicts['byUser'][studId]
	else:
		addStudentToUnknownGroup(studId, gDicts)
	
	path = destDir + os.sep + group + os.sep + studId
	srcD = path + os.sep + SRCDIR
	dstD = path + os.sep + BINDIR
	if not os.path.exists(path):
		os.makedirs(path)
		os.makedirs(srcD)
		os.makedirs(dstD)
	f = TEMP_FOLDER + os.sep + srcFile
	fnew = path + os.sep + srcFile
	shutil.move(f, fnew)
	if (fnew.endswith('zip')):
		extractResources(fnew, srcD)
		compileFiles(srcD, dstD)

	renameFile(path, srcFile)

def compileFiles(srcD, dstD):
	files = os.listdir(srcD)
	p = re.compile('\.java$')
	retval = True
	for f in [f for f in files if p.search(f)]:
		fullfile = srcD + os.sep + f
		cmd = "javac -source 1.6 -target 1.6 -d " + dstD + " -sourcepath " + srcD + " " + fullfile
		fnull=open(os.path.devnull, 'w')
		ret = subprocess.call(cmd, stdout=fnull, stderr=fnull, shell=True)
		if ret != 0:
			retval = False
	return retval

def getStudentID(srcFile):
	global nextUnknownIndex	
	p = re.compile('\d{6}[a-z]{2}', re.IGNORECASE)
	hits = p.findall(srcFile)
	uname = ""
	if len(hits) == 0:
		uname = 'UNKNOWN_' + str(nextUnknownIndex)
		nextUnknownIndex = nextUnknownIndex + 1
	else:
		uname = hits[0][:6]
	return uname

	
if __name__ == '__main__': main()
