#!/usr/bin/env python
# *-* utf-8 *-*

from sys import stdout, exit as sys_exit
from os import popen, environ, walk
from os.path import join, exists, isfile
#from re import search, sub, compile as re_compile
import re
from git import *

rows, columns = popen('stty size', 'r').read().split()
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

	def disable(self):
		self.HEADER = ''
		self.OKBLUE = ''
		self.OKGREEN = ''
		self.WARNING = ''
		self.FAIL = ''
		self.ENDC = ''

class git_repo:
	def __init__(self,path):
		self.path = path
		if isfile(path+"/.git/config"):
			self.er_num = 0
		else:
			self.er_num = -1
		try:
			self.get_error()
		except:
			sys_exit(0)

	def get_error(self):
		if self.er_num == 0:
			return 0
		if self.er_num == -1:
			print self.path+" is not a valid git repo"
		return er_num

	def get_status(self):
		"""
		Retrieve all the information needed from the repo 
		"""
		repo = Repo(self.path)
		git = repo.git
		if git.stash('list') != "":
			self.stashed = True
		else:
			self.stashed = False

		tmp_status = 0
		tmp_forward = ""
		for branch in repo.branches:
			#exec "repo.heads."+str(branch)+".checkout()"
			git.checkout(str(branch))
			regex = re.compile(r'^\# Your branch .+ by (\d+) commits?\.',re.M)
			status = git.status().split("\n")[1]
			if regex.search(status):
				tmp_forward += str(branch)+":"+str(int(regex.sub(r'\1',status)))+","

			if git.status('--porcelain') == "":
				tmp_status += 1
		repo.heads.master.checkout()
		self.forward = tmp_forward[0:-1]
		if tmp_status == len(repo.branches):
			self.status = True
		else:
			self.status = False
		
	def print_status(self):
		"""
		Print a one line status of the repo including stashes, forward commits

		Display OK if there is nothig to display on <git status> command, NO otherwise
		"""
		display = ">> "+self.path
		print display,

		self.get_status()
		## Displaying path of the repo
		if self.stashed:
			stash = "("+bcolors.WARNING+"stash"+bcolors.ENDC+")"
			display = display+stash+" " 
			#last space to compensate the print xxx, space
			print stash,

		if self.forward:
			forward = "("+str(self.forward)+")"
		else:
			forward = ""
		space = ""

		## Filling with space
		for i in range(int(columns)-len(display.replace(bcolors.WARNING,'').replace(bcolors.ENDC,''))-8-len(forward)):
			space += " "
		space += forward
		print space,

		if self.status:
			status = "[ "+bcolors.OKGREEN+"OK"+bcolors.ENDC+" ]"
		else:
			status = "[ "+bcolors.FAIL+"NO"+bcolors.ENDC+" ]"
		display = display+space+status
		print status
		#else:
			#space = ""
			#for i in range(int(columns)-len(display)-8):
				#space += " "
			#display = display + space + "[ "+bcolors.WARNING+"??"+bcolors.ENDC+" ]"
		#print display

class git_check:
	def __init__(self,force_scan=False,root=environ['HOME']):
		self.fname = environ['HOME']+'/.gitdb'
		self.root = root
		self.repos = []
		self.update_db(force_scan)
	def update_db(self,force_scan):
		"""
		Keep the list of repositories up to date
		"""
		if force_scan or not exists(self.fname):
			f = open(self.fname,'w')
			self.repos = self.scan(f)
			f.close()
		else:
			f = open(self.fname,'r')
			self.repos = [line.replace('\n','') for line in f.readlines()]
			f.close()
	def scan(self,f):
		"""
		Scan the computer to find all repositories
		"""
		repos = []
 
		print "=== Scanning"
		animation = "|/-\\"
		
		count=0
		for root, dirs, files in walk(self.root):
			for f2 in files:
				fpath = join(root,f2)
				if re.search(r'.git/config$',fpath):
					repos.append(fpath.replace('/.git/config',''))
			if count % 11 == 0:
				stdout.write("\r"+animation[count % len(animation)]+" ")
				stdout.flush()
			count += 1
		stdout.write("\r")
				
		for item in repos:
			f.write("%s\n" % item)
		return repos

	def list_all(self):
		"""
		Check statuses of all repositories listed in .gitdb file
		"""
		for repo in self.repos:
			a = git_repo(repo)
			a.print_status()
			#self.print_status(repo)
		
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Verify all git repository.')
	parser.add_argument('-s','--scan',dest='scan',action='store_true',default=False,help='Perform a complete tree scan of your data to search for git repositories')
	args = parser.parse_args()
	
	verif = git_check(args.scan)
	verif.list_all()
