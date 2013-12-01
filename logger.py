#!/usr/bin/env python
#-*-coding: utf8 -*-

""" Logger class"""

class Log(object):
    """Logger"""
    def __init__(self, fname="/tmp/logger.log"):
        self.fname = fname
        self.fstream = open(self.fname, 'w')

    def write(self, text):
        """Write text on log file"""
        self.fstream.write(text + "\n")

    def debug(self, text):
        """ Write debug message"""
        self.write("DEBUG: " + text)

    def show(self):
        """ Show on stdout the content of the logfile"""
        self.fstream.close()
        with open(self.fname, 'r') as fstream:
            lines = fstream.readlines()

        print "".join(lines)
        self.fstream = open(self.fname, 'a')

    def __del__(self):
        """Catch any weird interruption and close file"""
        self.fstream.close()
