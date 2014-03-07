#
#	purpose: Define variables common to the project (dirs, DB access, ..)
#	author:  M. Clerici
#	date:	 19.02.2014
#   descr:	 It is now a plain module in python (to be converted into other format ?)
#

# Import standard module
import os, sys

sys.path.append('mypath')

# Import eStation lib modules
from eStation2.lib.python import es_logging as log

# Define eStation specific variables
baseDir='/opt/facilities/eStation2/'
logDir=baseDir+'log/'

log.output_error('test_error')
