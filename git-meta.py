#!/usr/bin/env python
# *-* coding: utf-8 *-*

from sys import stdout, exit as sys_exit
from os import popen, environ, walk
from os.path import join, exists, isfile
import re
from git import *

## retrieve the size of the terminal
rows, columns = popen('stty size', 'r').read().split()

class bcolors:
    """
    Enlighten the terminal with fancy colors !
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    list = ["HEADER",
            "OKBLUE",
            "OKGREEN",
            "WARNING",
            "FAIL",
            "ENDC"]

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class gitRepo:
    """
    Repository object, to retrieve statuses and stuff
    """
    def __init__(self,path):
        self.path = path
        if isfile(path+"/.git/config"):
            self.er_num = 0
            self.repo = Repo(self.path)
            self.get_status()
        else:
            self.er_num = -1

    def get_error(self):
        if self.er_num == 0:
            return 0
        if self.er_num == -1:
            print ">> "+bcolors.FAIL+self.path+" is not a valid git repo"+bcolors.ENDC
        return self.er_num

    def get_status(self):
        """
        Retrieve all the information needed from the repo 
        """
        git = self.repo.git
        if git.stash('list') != "":
            self.stashed = True
        else:
            self.stashed = False

        tmp_status = 0
        tmp_forward = ""
        tmp_active_branch = self.repo.active_branch
        try:
            for branch in self.repo.branches:
                git.checkout(str(branch))
                regex = re.compile(r'^\# Your branch .+ by (\d+) commits?\.',re.M)
                status = git.status().split("\n")[1]
                if regex.search(status):
                    tmp_forward += str(branch)+":"+str(int(regex.sub(r'\1',status)))+","

                if git.status('--porcelain') == "":
                    tmp_status += 1
            git.checkout(str(tmp_active_branch))
        except:
            tmp_status = 0
            tmp_forward = ""
        self.forward = tmp_forward[0:-1]

        if tmp_status == len(self.repo.branches):
            self.status = True
        else:
            self.status = False
    def push(self):
        """
        Equivalent of a `git push` command
        """
        if self.forward:
            git = self.repo.git
            try:
                git.push()
                self.forward = "pushed"
            except:
                self.forward = "push error - "+self.forward

    def _get_str_len(self, string, dbg=False):
        """ Return the lenght of a string without the bcolors code
        """
        for balise in bcolors.list:
            exec("string = string.replace(bcolors.%s, '')"%(balise))
        return len(string)

    def print_status(self):
        """
        Print a one line status of the repo including stashes, forward commits

        Display OK if there is nothig to display on <git status> command, NO otherwise
        """
        display = ">> " + self.path

        ## Get stash
        if self.stashed:
            stash = "(" + bcolors.WARNING + "stash" + bcolors.ENDC + ")"
        else:
            stash = ""

        ## Get forward
        if self.forward:
            forward = "(" + str(self.forward) + ")"
        else:
            forward = ""

        ## Get status
        if self.status:
            status = "[ "+bcolors.OKGREEN+"OK"+bcolors.ENDC+" ]"
        else:
            status = "[ "+bcolors.FAIL+"NO"+bcolors.ENDC+" ]"

        ## Filling with whitespace
        # Full string = display + whitespace + stash + forward + status
        # Get lenght of string without whitespace
        str_len = self._get_str_len(display) + self._get_str_len(stash)\
                    + self._get_str_len(forward) + self._get_str_len(status)
        nb_whitespace = int(columns) - str_len
        whitespace = "".join([" "]*nb_whitespace)

        ## Show display
        display += whitespace + stash + forward + status
        print display

class gitMeta:
    def __init__(self,force_scan=False,root=environ['HOME']):
        self.fname = environ['HOME']+'/.gitdb'
        self.ignore_fname = environ['HOME']+'/.gitdb_ignore'
        self.root = root
        self.repos = []
        self.ignore = []
        self.update_db(force_scan)

    def update_db(self,force_scan):
        """
        Keep the list of repositories up to date
        """
        if exists(self.ignore_fname):
            f2 = open(self.ignore_fname,'r')
            self.ignore = [line.replace('\n','') for line in f2.readlines()]
            f2.close()
        else:
            self.ignore = []
        if force_scan or not exists(self.fname):
            f = open(self.fname,'w')
            self.repos = self.scan(f)
            f.close()
        else:
            f = open(self.fname,'r')
            self.repos = [line.replace('\n','') for line in f.readlines()]
            f.close()
            self.clean_db()

    def clean_db(self):
        """
        Remove repo which not exists on the disk
        """
        clean_repos = [repo for repo in self.repos if exists(repo)]
        remov_repos = [repo for repo in self.repos if not exists(repo)]
        if remov_repos != []:
            ## Print warning and which repo will be removed
            print "/!\\ Following repo not exist and will be removed in the data base"
            for repo in remov_repos:
                print "/!\\ '%s' removed from data base"%(repo)
            print

            ## Update data base file
            with open(self.fname, 'w') as f:
                f.write("\n".join(clean_repos))

            ## Update self.repos list
            self.repos = clean_repos

    def scan(self,f):
        """
        Scan the computer to find all repositories
        """
        repos = []

        base = "=== Scanning"
        animation = "|/-\\"
        count=0

        # Prepare regexp list for verification
        ignore = "|".join(self.ignore)

        for root, dirs, files in walk(self.root):
            for f2 in files:
                fpath = join(root,f2)
                # if this is a repo ...
                if re.search(r'.git/config$',fpath):
                    fpath = fpath.replace('/.git/config','')
                    #  ... and is not ignored
                    if ignore == "" or not re.search(ignore,fpath):
                        repos.append(fpath)
                # Animation
                if count % 11 == 0:
                    stdout.write("\r"+base+" "+animation[count % len(animation)]+" ")
                    stdout.flush()
                count += 1
        stdout.write("\r=== "+str(len(repos))+" repos found\n")

        for item in repos:
            f.write("%s\n" % item)
        return repos

    def list_all(self,list_all=False,push_all=False):
        """
        Check statuses of all repositories listed in .gitdb file
        """
        for repo in self.repos:
            if repo not in self.ignore or list_all:
                a = gitRepo(repo)
                if (a.get_error()) == 0:
                    if a.forward and push_all:
                        a.push()
                    a.print_status()
                else:
                    pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify all git repository.')
    parser.add_argument('-a','--all',dest='list_all',action='store_true',default=False,help='List all the repositories even those ignored')
    parser.add_argument('-P','--push-all',dest='push_all',action='store_true',default=False,help='Push all repositories to their remote servers')
    parser.add_argument('-s','--scan',dest='scan',action='store_true',default=False,help='Perform a complete tree scan of your data to search for git repositories')
    args = parser.parse_args()

    verif = gitMeta(args.scan)
    verif.list_all(args.list_all,args.push_all)
