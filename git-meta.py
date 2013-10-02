#!/usr/bin/env python
# *-* coding: utf-8 *-*

from sys import stdout, exit as sys_exit
from os import popen, environ, walk
from os.path import join, exists, isfile
import re
from git import Repo, GitCommandError, InvalidGitRepositoryError
from textwrap import wrap

## retrieve the size of the terminal
rows, columns = popen('stty size', 'r').read().split()

class Bcolors:
    """
    Enlighten the terminal with fancy colors !
    """
    BOLD = '\033[1m'
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

    def bold(self, color=None):
        """ Return the bold balise for color
        """
        ## Get balise
        if color != None:
            exec("balise = self.%s"%(color))
        else:
            balise = ""
        ## Return bold color
        return self.BOLD + balise

    def disable(self):
        self.BOLD = ''
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class GitRepo:
    """
    Repository object, to retrieve statuses and stuff
    """
    def __init__(self,path):
        self.bcolors = Bcolors()
        self.path = path
        self.er_num = 0
        self.forward = ""
        self.stashed = None
        self.status = None
        self.er_num = self.set_status()


    def get_error(self):
        """ Return error number
        """
        return self.er_num

    def set_status(self):
        """
        Retrieve all the information needed from the repo 

        Return -1,0,1 respectively for:
            -1: InvalidGitRepository
            0:  Valid git repo, status = "ok" or "no"
            1:  Git bare repo
        """
        ## Status is (bool, str)
        self.status = ()

        ## Get git.Repo and git.Repo.git
        try:
            self.repo = Repo(self.path)
            git = self.repo.git
            if git.rev_parse("--is-bare-repository") == 'true':
                self.status = (False, "bare")
                return 1
        except InvalidGitRepositoryError:
            self.status = (False, "InvalidGitRepository")
            return -1

        ## Set stashed
        if git.stash('list') != "":
            self.stashed = True
        else:
            self.stashed = False

        ## Set forward
        nb_status_ok = 0
        forward = ""
        branch_forward = ""
        active_branch = self.repo.active_branch
        try:
            for branch in self.repo.branches:
                git.checkout(str(branch))
                regex = re.compile(r'^\# Your branch .+ by (\d+) commits?\.',re.M)
                status = git.status().split("\n")[1]
                if regex.search(status):
                    branch_forward += str(branch)+":"+str(int(regex.sub(r'\1',status)))+","
                else:
                    forward += git.status()

                if git.status('--porcelain') == "":
                    nb_status_ok += 1
            git.checkout(str(active_branch))
        except GitCommandError as e:
            nb_status_ok = 0
            forward = "'%s' returned exit status %s: %s"%(
                                " ".join(e.command), e.status, e.stderr)

        ## Remove forward string when working directory is clean
        if forward != "# On branch master\nnothing to commit, working directory clean":
            ## Wrap text for terminal size
            # width = columns      - len(">> ") - len("[ OK ]")
            width = int(columns) - 3 - 6
            forward = "\n".join([ "\n".join(wrap(text, width)) for text in forward.split("\n") ])
            ## Add 3 white spaces to indent text
            forward = "   " + forward.replace("\n", "\n   ")
        else:
            forward = ""

        ## Set self.forward
        self.forward = forward
        

        ## Set final status
        if nb_status_ok == len(self.repo.branches):
            self.status = (True, "ok")
            return 0
        else:
            self.status = (True, "no")
            return 0

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
        ## Remove bold balise
        string = string.replace(self.bcolors.bold(), "")
        ## Remove all color
        for balise in self.bcolors.list:
            exec("string = string.replace(self.bcolors.%s, '')"%(balise))
        return len(string)

    def print_status(self, verbose=False):
        """
        Print a one line status of the repo including stashes, forward commits

        Display OK if there is nothig to display on <git status> command, NO otherwise
        """
        ## Get status and display
        # status = (bool, str)
        if self.status[0]:
            if self.status[1] == "ok":
                status_level = True
                status = "[ "+self.bcolors.OKGREEN+"OK"+self.bcolors.ENDC+" ]"
                display = ">> " + self.path
            elif self.status[1] == "no":
                status_level = False
                status = self.bcolors.bold() + "[ " + self.bcolors.bold("FAIL") +\
                        "NO" + self.bcolors.bold("ENDC") + self.bcolors.bold() + " ]" +\
                        self.bcolors.bold("ENDC")
                display = ">> " + self.path
                display = self.bcolors.bold() + display + self.bcolors.ENDC
            else:
                raise ValueError("'%s' not a valid value for True status string"%(self.status[1]))
        else:
            status = ""
            if self.status[1] == "InvalidGitRepository":
                display = ">> " + self.path + self.bcolors.FAIL +\
                      " is not a valid git repo" + self.bcolors.ENDC
            elif self.status[1] == "bare":
                display = ">> " + self.path +\
                      self.bcolors.WARNING + " is a bare git repo" + self.bcolors.ENDC
            else:
                raise ValueError("'%s' not a valid value for False status string"%(self.status[1]))

        ## Get stash
        if self.stashed:
            if status_level:
                stash = "(" + self.bcolors.WARNING + "stash" + self.bcolors.ENDC + ")"
            else:
                stash = self.bcolors.bold() + "(" + self.bcolors.bold("WARNING") +\
                        "stash" + self.bcolors.bold("ENDC") + self.bcolors.bold() + ")" +\
                        self.bcolors.bold("ENDC")
        else:
            stash = ""

        ## Get forward
        if verbose:
            forward = self.forward
        else:
            forward = ""

        ## Filling with whitespace
        # Full string = display + whitespace + stash + status
        # Get lenght of string without whitespace
        str_len = self._get_str_len(display) + self._get_str_len(stash)\
                    + self._get_str_len(status)
        nb_whitespace = int(columns) - str_len
        whitespace = "".join([" "]*nb_whitespace)

        ## Show display
        if verbose and forward != "":
            display += whitespace + stash + status + "\n" + forward
        else:
            display += whitespace + stash + status
        print display


class GitMeta:
    """ GitMeta class
    """
    def __init__(self, force_scan=False, root=environ['HOME']):
        self.fname = environ['HOME']+'/.gitdb'
        self.ignore_fname = environ['HOME']+'/.gitdb_ignore'
        self.root = root
        self.repos = []
        self.gitrepo = []
        self.ignore = []
        self.update_db(force_scan)

    def update_db(self, force_scan):
        """
        Keep the list of repositories up to date
        """
        ## Get ignore repo from ignore_fname
        if exists(self.ignore_fname):
            f2 = open(self.ignore_fname,'r')
            self.ignore = [line.replace('\n', '') for line in f2.readlines()]
            f2.close()
        else:
            self.ignore = []

        ## Get repos list
        if force_scan or not exists(self.fname):
            f = open(self.fname, 'w')
            self.repos = self.scan(f)
            f.close()
        else:
            f = open(self.fname, 'r')
            self.repos = [line.replace('\n', '') for line in f.readlines()]
            f.close()
            self.clean_db()

    def clean_db(self):
        """
        Remove repo which not exists on the disk
        """
        ## init local variable
        clean_repos = [repo for repo in self.repos if exists(repo)]
        remov_repos = [repo for repo in self.repos if not exists(repo)]

        ## Remove repos in data base
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

    def scan(self, fname):
        """
        Scan the computer to find all repositories
        """
        ## init local variable
        repos = []

        ## Init scanning animation
        base = "=== Scanning"
        animation = "|/-\\"
        count=0

        ## Prepare regexp list for verification
        ignore = "|".join(self.ignore)

        ## Walk in repo and get git repo
        for root, dirs, files in walk(self.root):
            for f2 in files:
                fpath = join(root,f2)
                ## if this is a repo ...
                if re.search(r'.git/config$',fpath):
                    fpath = fpath.replace('/.git/config','')
                    ##  ... and is not ignored
                    if ignore == "" or not re.search(ignore,fpath):
                        repos.append(fpath)
                ## Animation
                if count % 11 == 0:
                    stdout.write("\r"+base+" "+animation[count % len(animation)]+" ")
                    stdout.flush()
                count += 1
        stdout.write("\r=== "+str(len(repos))+" repos found\n")

        ## Write repo in fname
        for item in repos:
            fname.write("%s\n" % item)
        return repos

    def list_all(self,list_all=False,push_all=False):
        """
        Check statuses of all repositories listed in .gitdb file
        """
        print "=== Loading"

        ## Walk in repo and get GitRepo
        for repo in self.repos:
            if repo not in self.ignore or list_all:
                a = GitRepo(repo)
                self.gitrepo.append([a, a.path, a.status[1]])
                if (a.get_error()) == 0:
                    if a.forward and push_all:
                        a.push()
                else:
                    pass
        print "\r=== "+str(len(self.gitrepo))+" repos scanned"

    def print_status(self, verbose=False, sortNOOK=True, reverse=True, select=None):
        """ Print status for repo
        """
        ## Sort repo by status NO/OK
        if sortNOOK:
            self.gitrepo = sorted(self.gitrepo, key=lambda col: col[2], reverse=reverse)

        ## Get only 'select' status git repo
        if select == "no":
            self.gitrepo = [ repo for repo in self.gitrepo if repo[2] == "no" ]
        elif select == "ok":
            self.gitrepo = [ repo for repo in self.gitrepo if repo[2] == "ok" ]
        elif select == "other":
            self.gitrepo = [ repo for repo in self.gitrepo if repo[2] != "ok" and repo[2] != "no" ]
        elif select == None:
            pass
        else:
            raise ValueError("'%s' not a valid value for --select option"%(select))


        ## Show full list
        if select != None:
            print "=== %d repos selected by '%s'\n"%(len(self.gitrepo), select)
        else:
            print ""
        for repo in self.gitrepo:
            repo[0].print_status(verbose=verbose)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify all git repository.')
    parser.add_argument('-a', '--all', dest='list_all',
                        action='store_true', default=False,
                        help='List all the repositories even those ignored')
    parser.add_argument('-P', '--push-all', dest='push_all',
                        action='store_true', default=False,
                        help='Push all repositories to their remote servers')
    parser.add_argument('-s', '--scan', dest='scan',
                        action='store_true', default=False,
                        help='Perform a complete tree scan of your data to search for git repositories')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', default=False,
                        help="Active verbose mode: print git status for 'NO' repo")
    parser.add_argument('-S', '--sort', dest='sortNOOK',
                       action='store_true', default=False,
                       help="Sort git repo by status NO/OK (NO first)")
    parser.add_argument('--reverse', dest='reverse',
                       action='store_true', default=False,
                       help="Reverse sort function")
    parser.add_argument('--select', dest='select', type=str,
                       action='store', choices=('ok', 'no', 'other'),
                       help="Select only git repo by status. value=ok/no/other")
    args = parser.parse_args()

    verif = GitMeta(args.scan)
    verif.list_all(args.list_all,args.push_all)
    verif.print_status(args.verbose, args.sortNOOK, args.reverse, args.select)

