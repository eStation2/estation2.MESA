#
#   File defining 'local' variables, i.e. variables referring to the local machine (quigon, vm19, aniston)
#   Indeed, this is not to be synchronized through machines
#

import os

# Base dir
os.environ['ESTATION2PATH'] = '/srv/www/eStation2/'

import sys
# Base eStation path
sys.path.append(os.environ['ESTATION2PATH'])
# Test specific paths
sys.path.append((os.environ['ESTATION2PATH'])+'apps/acquisition/.test/')

# Set all variables/import all modules
from config.es2 import *

