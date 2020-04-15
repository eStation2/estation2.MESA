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
import os
import shutil

logger = log.my_logger(__name__)

def return_as_list(input_args):

    my_list = []
    if isinstance(input_args, list):
        my_list = input_args
    else:
        for item in input_args:
            my_list.append(item)
    return my_list

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


def rewrite_metadata(input_file, productcode, subproductcode, version, mapsetcode, output_directory):

    # Copy the metadata and update nodata field
    sds_meta = metadata.SdsMetadata()

    sds_meta.assign_es2_version()
    if mapsetcode is not None:
        sds_meta.assign_mapset(mapsetcode)
    sds_meta.assign_from_product(productcode, subproductcode, version)

    if output_directory is not None:
        sds_meta.assign_subdir_from_fullpath(output_directory)
    sds_meta.assign_compute_time_now()

    sds_meta.assign_input_files(input_file)
    sds_meta.assign_date(sds_meta.get_item('eStation2_input_files')[0:8])
    sds_meta.write_to_file(input_file)

    return 0

def assign_metadata_full(input_dir, productcode, subproductcode, productversion, mapsetcode, output_directory ):

    # input_dir = return_as_list(input_file)
    files = glob(input_dir + '*')
    print (files)
    for infile in sorted(files):
        print ('Working on assign_metadata_full : ' + infile)
        try:
            result = rewrite_metadata(input_dir, productcode, subproductcode, productversion, mapsetcode,
                                      output_directory)
        except:
            print ('Error in processing file assign_metadata_full : ' + infile)
    # print 'Working on metadata_single_parameter : ' + input_file
    # try:
    #
    # except:
    #     print 'Error in processing file metadata_single_parameter : '+input_file

def assign_metadata_single_parameter(input_dir, parameter_key, parameter_value ):
    # input_dir = return_as_list(input_file)
    files = glob(input_dir + '*.tif')
    print (files)
    for infile in sorted(files):
        print ('Working on metadata_single_parameter : ' + infile)
        try:
            result = rewrite_metadata_single_paramater(infile, parameter_key, parameter_value)
            # result = rewrite_metadata_single_paramater(infile, parameter_key, parameter_value)
        except:
            print ('Error in processing file metadata_single_parameter : ' + infile)


if __name__=='__main__':

    input_dir = '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS-AVG/tif/occurr/'
    # old_nodata = -32767
    # new_nodata = 0
    parameter_key = 'eStation2_unit'
    parameter_value = 'Celsius'

    in_date = '20180801'
    productcode = 'wd-gee'
    productversion = '1.0'
    subproductcode = 'occurr'
    mapsetcode = 'WD-GEE-ECOWAS-AVG'
    datasource_descrID = 'JRC:WBD:GEE'
    output_directory = '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS-AVG/tif/occurr/'
    input_file = '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS-AVG/tif/occurr/20181001_wd-gee_occurr_WD-GEE-ECOWAS-AVG_1.0.tif'
    assign_metadata_full(input_file, productcode, subproductcode, productversion, mapsetcode, '/data/processing/wd-gee/1.0/WD-GEE-ECOWAS-AVG/tif/occurr/')
    # assign_metadata_single_parameter(input_dir, parameter_key, parameter_value)


