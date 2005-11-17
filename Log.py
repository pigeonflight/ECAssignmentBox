# @(#) $Id$
#
# Copyright (c) 2004 by Otto-von-Guericke-University, Magdeburg.
#
# Created:  2004/11/03
# Author:   Mario Amelung
#
# Simple class used for debug logging
#
from time import *
import os
import sys

# Constants
LOG_NONE = 0           # => No log output
LOG_INFO = 1           # => Notices (Special conditions, ...)
LOG_DEBUG = 2          # => Debug (Debugging information)
LOG_WARN = 3           # => Warning (non-blocking exceptions, ...)
LOG_ERROR = 4          # => Error (runtime exceptions, ...)

class MyLog:
    """
    Simple class definition for logging capabilities
    """

    _DEFAULT_STD_LOG_FILE = "status.log"
    _DEFAULT_ERROR_LOG_FILE = "error.log"

    _DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %X"

    # Default Constructor
    def __init__(self, level=LOG_INFO, stdFile=_DEFAULT_STD_LOG_FILE, errorFile=_DEFAULT_ERROR_LOG_FILE):
        self.level = level
        self.stdFile = stdFile
        self.errorFile = errorFile
        self.datetimeFormat = self._DEFAULT_DATETIME_FORMAT

    # Public Methods
    def info(self, msg):
        if self.level >= LOG_INFO:
            self._writeLog(self.stdFile, "[INFO]  - ", msg)
    
    def debug(self, msg):
        if self.level >= LOG_DEBUG:
            self._writeLog(self.stdFile, "[DEBUG] - ", msg)
    
    def warn(self, msg):
        if self.level >= LOG_WARN:
            self._writeLog(self.stdFile, "[WARN]  - ", msg)

        self._writeLog(self.errorFile, "[WARN]  - ", msg)
    
    def error(self, msg):
        #if self.level >= LOG_ERROR:
            self._writeLog(self.errorFile, "[ERROR] - ", msg)
            
    def setDatetimeFormat(self, formatStr):
        self.datetimeFormat = formatStr

    # Private Methods
    def _datetime(self):
        """ Returns current date and time """
        return strftime(self.datetimeFormat);
        
    def _writeLog(self, fileName, level, msg):
        """ Write message to specified file """
        #2005-04-13 18:35:00.000 [DEBUG] - 
        prefix = self._datetime() + " " + level
        
        file = open(os.path.dirname(__file__) + '/' + fileName, "a")
        file.write(prefix)
        try:
            #file.write(msg.encode('utf-8'))
            file.write(str(msg))
        except Exception, e:
            print >> sys.stderr, e

        file.write('\n')
        file.close()

        #try:
        #    print >> sys.stdout, prefix + msg
        #except Exception, e:
        #    print >> sys.stderr, e
        
#log = MyLog(LOG_DEBUG)