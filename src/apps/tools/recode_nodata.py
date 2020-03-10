from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = 'analyst'
#
#	purpose: Change the nodata value in a file
#	author:  M.Clerici
#	date:	 07.01.2016
#   descr:	 takes a list of input files, and convert the nodata value in the files, and their metadata
#
#	history: 1.0
#

from lib.python.image_proc import raster_image_math
from glob import *
from lib.python import es_logging as log
from lib.python import metadata

import shutil

logger = log.my_logger(__name__)

def convert_nodata_value(input_file,old_nodata, new_nodata):

    new_file_tmp = input_file+'.tmp'
    # Update the value
    raster_image_math.do_mask_image(input_file=input_file, mask_file=input_file, output_file=new_file_tmp,output_format=None,
                  output_type=None, options='', mask_value=old_nodata, out_value=new_nodata)

    # Copy the metadata and update nodata field
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    sds_meta.read_from_file(input_file)
    sds_meta.assign_nodata(new_nodata)
    sds_meta.write_to_file(new_file_tmp)

    # Rename files
    shutil.move(input_file,input_file+'.old')
    shutil.move(new_file_tmp,input_file)

    return 0


if __name__=='__main__':

    input_dir = '/data/processing/modis-sst/v2013.1/MODIS-Africa-4km/tif/sst-day-all/'
    old_nodata = -32767
    new_nodata = 0

    files = glob(input_dir+'*.tif')
    print (files)
    for infile in sorted(files):
        print ('Working on file: ' + infile)
        try:
            result = convert_nodata_value(infile, old_nodata, new_nodata)
        except:
            print ('Error in processing file: ' + infile)
