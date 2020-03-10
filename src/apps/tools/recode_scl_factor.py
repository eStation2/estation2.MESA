from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = 'analyst'
#
#	purpose: Change the scl_factor value in a file
#	author:  M.Clerici
#	date:	 07.01.2016
#   descr:	 takes a list of input files, and convert the scl_factor value in the files, and their metadata
#
#	history: 1.0
#

from lib.python.image_proc import raster_image_math
from glob import *
from lib.python import es_logging as log
from lib.python import metadata

import shutil, os

logger = log.my_logger(__name__)

def convert_scl_factor_value(input_file,old_scl_factor, new_scl_factor):

    new_file_tmp = input_file+'.tmp'
    # Update the value
    shutil.copy(input_file,new_file_tmp)

    # Copy the metadata and update scl_factor field
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    sds_meta.read_from_file(input_file)
    sds_meta.assign_scl_factor(new_scl_factor)
    sds_meta.write_to_file(new_file_tmp)

    # Rename files
    shutil.move(new_file_tmp,input_file)
    return 0


if __name__=='__main__':

    input_dir = '/data/processing/modis-sst/v2013.1/MODIS-Africa-4km/derived/monanom/'
    old_scl_factor = 0
    new_scl_factor = 0.01

    files = glob(input_dir+'*.tif')
    print (files)
    for infile in sorted(files):
        print ('Working on file: ' + infile)
        try:
            result = convert_scl_factor_value(infile, old_scl_factor, new_scl_factor)
        except:
            print ('Error in processing file: ' + infile)
