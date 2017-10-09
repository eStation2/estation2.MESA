__author__ = 'clerima'
#
#	purpose: Write/Change the nodata value in a file
#	author:  M.Clerici
#	date:	 01.09.2017
#   descr:	 write/update metadata on an existing file, by using the assign_metadata_processing() method of raster_image_math.py
#            initially written for the modis-firms v6.0 10dcount10k product (see ES2-38)
#	history: 1.0
#

from lib.python.image_proc import raster_image_math
from glob import *
from lib.python import es_logging as log
from lib.python import functions
import os

logger = log.my_logger(__name__)

if __name__=='__main__':

    files_dir = '/data/processing/modis-firms/v6.0/SPOTV-Africa-10km/derived/10dcount10k/'
    files = glob(files_dir+'*.tif')

    input_file_dir='/data/processing/modis-firms/v6.0/SPOTV-Africa-1km/derived/10dcount/'

    for myfile in sorted(files):
        print 'Working on file: '+myfile
        try:
            date = functions.get_date_from_path_full(myfile)
            input_file = glob(input_file_dir+date+'*.tif')

            if not os.path.isfile(input_file[0]):
                print 'No input file found for: '+myfile
            else:
                raster_image_math.assign_metadata_processing(input_file, myfile)
        except:
            print 'Error in processing file: '+myfile
