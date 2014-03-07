#
#	purpose: Define a library of functions for general purpose operations
#	author:  M.Clerici
#	date:	 28.02.2014
#   descr:	 It correspond to the 1.X Functions file, for bash functions.
#            It contains the following sets of functions:
#            Time:  convert date/time between formats
#            Naming:manage file naming
#            General: general purpose functions
#
#	history: 1.0
#
try:
	import os, glob, es_logging, es_logging.handlers
except ImportError:
	pass

try:
    baseDir=os.environ['ESTATION2PATH']
except:
    print 'Error - ESTATION2PATH variable not defined ! Exit'
    exit

