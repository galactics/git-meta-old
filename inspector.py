#!/usr/bin/env python
#-*-coding: utf8 -*-

""" Inspector class for Git repository
"""

class Inspector(object):
    """ Inspector Git repo"""
    def __init__(self, repo, **kwarg):
        log = None if not 'log' in kwarg.keys() else kwarg['log']
        if log != None:
            log.debug(repo)

if __name__ == "__main__":
    import logger
    log = logger.Log()
    Inspector("Test a string", log=log)
