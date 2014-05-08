__author__ = "Jurriaan van 't Klooster"

#import os
execfile('/srv/www/eStation2/locals.py')

import filecmp
from config.es2 import *
from apps.acquisition import ingestion
import time

start = time.clock()

ingestion.drive_ingestion()

elapsed = time.clock()-start
print elapsed

exit()

