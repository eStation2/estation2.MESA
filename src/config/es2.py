#
#	purpose: Define variables common to the project (dirs, DB access, ..)
#	author:  M. Clerici
#	date:	 19.02.2014
#   descr:	 It is now a plain module in python (to be converted into other format ?)
#

# Import generic modules
import os
import sys
import re
import signal
import commands
import datetime
import tempfile
import ntpath
import time
import string
import glob
import time
import zipfile
import bz2
import gzip
import resource    # for monitoring memory usage
import shutil

# Import gdal/osr/numpy
from osgeo.gdalconst import *
from osgeo import gdal
from osgeo import osr
import pygrib
import numpy as N

# Base dir
os.environ['ESTATION2PATH'] = '/srv/www/eStation2/'
# Base eStation path
sys.path.append(os.environ['ESTATION2PATH'])
# Test specific paths
sys.path.append((os.environ['ESTATION2PATH'])+'apps/acquisition/.test/')

# Import eStation lib modules
from lib.python import es_logging as log
from lib.python.es_constants import *
import lib.python.querydb as querydb
from lib.python.mapset import *
from lib.python.functions import *
from lib.python.metadata import *
