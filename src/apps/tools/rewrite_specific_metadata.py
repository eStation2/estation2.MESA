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
import os
import shutil

logger = log.my_logger(__name__)

def rewrite_metadata_single_paramater(input_file, parameter_key, parameter_value):

    # new_file_tmp = input_file+'.old'
    # shutil.copy(input_file, new_file_tmp)
    # Update the value
    # raster_image_math.do_mask_image(input_file=input_file, mask_file=input_file, output_file=new_file_tmp,output_format=None,
    #               output_type=None, options='', mask_value=old_nodata, out_value=new_nodata)

    # Copy the metadata and update nodata field
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    sds_meta.read_from_file(input_file)
    sds_meta.assign_single_paramater(parameter_key, parameter_value)
    sds_meta.write_to_file(input_file)

    # Rename files
    # shutil.move(input_file,input_file+'.old')
    # shutil.move(new_file_tmp,input_file)

    return 0


def rewrite_metadata(input_file, product, subproduct, version):

    # Copy the metadata and update nodata field
    sds_meta = metadata.SdsMetadata()

    # Check if the input file is single, or a list
    sds_meta.read_from_file(input_file)
    sds_meta.assign_from_product(product, subproduct, version)
    sds_meta.write_to_file(input_file)

    return 0


if __name__=='__main__':

    input_dir = '/data/processing/lsasaf-lst/undefined/SPOTV-Africa-1km/derived/10dmin/'
    # old_nodata = -32767
    # new_nodata = 0
    parameter_key = 'eStation2_unit'
    parameter_value = 'Celsius'

    files = glob(input_dir+'*.tif')
    print files
    for infile in sorted(files):
        print 'Working on file: '+infile
        try:
            result = rewrite_metadata_single_paramater(infile, parameter_key, parameter_value)
            # result = rewrite_metadata_single_paramater(infile, parameter_key, parameter_value)
        except:
            print 'Error in processing file: '+infile
