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

import os
import getopt
import sys
import shutil
import subprocess
import re

def usage():
	print """usage: compiler.py -d <dir>
	<dir> is the directory where the source files are residing

	-d directory with the java source files

	long options also work:
	--dir=<dir>"""

def main():
	shortargs = 'h:d:'
	longargs = ['help', 'dir=']
	try:
		opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	directory = ""
	for o, a in opts:
		if o in ("-d", "--dir"):
			directory = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()

	if directory == "" or not os.path.exists(directory):
		usage()
		sys.exit()

	compileFiles(directory)

def compileFiles(directory):
	# first level is groups
	groupList = os.listdir(directory)
	okStudents = []
	notOkStudents = []
	for group in groupList:
		students = os.listdir(directory + group)
		for student in students:
			if compileJava(directory + group + os.sep + student):
				okStudents.append(student)
			else:
				notOkStudents.append(student)
	print("Students with compiling files: {}".format(okStudents))
	print("Students with compilation errors: {}".format(notOkStudents))

def compileJava(directory):
	files = os.listdir(directory)
	p = re.compile('\.java$')
	retval = True
	for f in [f for f in files if p.search(f)]:
		fullfile = directory + os.sep + f
		cmd = "javac -source 1.6 -target 1.6 -d " + directory + " -sourcepath " + directory + " " + fullfile
		fnull=open('/dev/null', 'w')
		ret = subprocess.call(cmd, stdout=fnull, shell=True)
		if ret != 0:
			retval = False
	return retval


if __name__ == '__main__': main()


