# -*- coding: utf-8 -*-
#
#    purpose: Convert from eStation2 to SPIRITS format
#    author:  Marco Clerici
#    date:    09.09.2015

__author__ = 'clerima'

import os
import csv
import operator
from config import es_constants
import fnmatch
import datetime

# Import eStation2 modules
from lib.python import es_logging as log
from lib.python import functions
from database import querydb
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product

logger = log.my_logger(__name__)

naming_spirits = { 'sensor_filename_prefix':'', \
                   'frequency_filename_prefix':'', \
                   'pa_filename_prefix':''}

metadata_spirits= {'values': '',
                   'date': '', \
                   'flags': '', \
                   'data_ignore_value':'', \
                   'days': 0, \
                   'sensor_type':'', \
                   'comment':''}

#
# def write_properties(filename,dictionary):
#     """ Writes the provided dictionary in key-sorted order to a properties file with each line of the format key=value
#
#     Keyword arguments:
#         filename -- the name of the file to be written
#         dictionary -- a dictionary containing the key/value pairs.
#     """
#     with open(filename, "wb") as csvfile:
#         writer = csv.writer(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
#         for key, value in sorted(dictionary.items(), key=operator.itemgetter(0)):
#                 writer.writerow([ key, value])
#
# def read_properties(filename,dictionary):
#     """ Reads a given properties file with each line of the format key=value.  Returns a dictionary containing the pairs.
#
#     Keyword arguments:
#         filename -- the name of the file to be read
#     """
#     result={ }
#     with open(filename, "rb") as csvfile:
#         reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
#         for row in reader:
#             if len(row) != 2:
#                 raise csv.Error("Too many fields on row with contents: "+str(row))
#             result[row[0]] = row[1]
#     return result

# Modify the header file created by the conversion
def append_to_header_file(header_file, metadata_spirit):

    # Check the file exists
    if os.path.isfile(header_file):
        with open(header_file, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_MINIMAL, quotechar=' ')
            for key, value in sorted(metadata_spirit.items(), key=operator.itemgetter(0)):
                    writer.writerow([ key, value])
    else:
         logger.error('The header file does not exist : : %s' % header_file)

# Convert a single file
def convert_geotiff_file(input_file, output_dir, str_date, naming_spirits, metadata_spirits, overwrite=False):

    extension_bin = '.img'
    extension_hdr = '.hdr'
    status = 0

    # Define output filename
    output_base_name = naming_spirits['sensor_filename_prefix']+\
                  naming_spirits['frequency_filename_prefix']+\
                  str_date+ \
                  naming_spirits['pa_filename_prefix']

    output_path = output_dir+os.path.sep+output_base_name+extension_bin

    # Check output file exist
    if not os.path.isfile(output_path) and not overwrite:
        command = es_constants.es2globals['gdal_translate']+ \
                  ' -of ENVI ' + \
                  input_file  + ' ' + \
                  output_path

        # Execute command
        status = os.system(command)
        if status:
             logger.error('Error in converting file to SPIRITS format: %s' % input_file)

        # Modify the header
        header_file_name = output_dir+os.path.sep+output_base_name+extension_hdr
        status = append_to_header_file(header_file_name, metadata_spirits)

    if status:
         logger.error('Error in modifying SPIRITS header: %s' % header_file_name)

def convert_driver(output_dir=None):

    # Definitions
    input_dir = es_constants.es2globals['processing_dir']

    # Check base output dir
    if output_dir is None:
        output_dir=es_constants.es2globals['spirits_output_dir']

    functions.check_output_dir(output_dir)

    # Read the spirits table and convert all existing files
    spirits_list = querydb.get_spirits()
    for entry in spirits_list:
        use_range = False
        product_code = entry['productcode']
        sub_product_code = entry['subproductcode']
        version = entry['version']
        mapset = entry['mapsetcode']

        # Prepare the naming dict
        naming_spirits = { 'sensor_filename_prefix':entry['sensor_filename_prefix'], \
                           'frequency_filename_prefix':entry['frequency_filename_prefix'], \
                           'pa_filename_prefix':entry['product_anomaly_filename_prefix']}

        metadata_spirits= {'values': entry['prod_values'],
                           'flags': entry['flags'], \
                           'data_ignore_value':entry['data_ignore_value'], \
                           'days': entry['days'], \
                           'sensor_type':entry['sensor_type'], \
                           'comment':entry['comment'], \
                           'date':''}

        # Manage mapsets: if defined use it, else read the existing ones from filesystem
        my_mapsets = []
        if entry['mapsetcode']:
            my_mapsets.append(entry['mapsetcode'])
        else:
            prod = Product(product_code,version=version)
            for mp in prod.mapsets:
                my_mapsets.append(mp)

        # Manage dates
        if entry['start_date']:
            from_date=datetime.datetime.strptime(str(entry['start_date']), '%Y%m%d').date()
            use_range=True
        else:
            from_date = None
        if entry['end_date']:
            to_date=datetime.datetime.strptime(str(entry['end_date']), '%Y%m%d').date()
            use_range=True
        else:
            to_date = None

        for my_mapset in my_mapsets:
            # Manage output dirs
            out_sub_dir = my_mapset+os.path.sep+\
                          product_code+os.path.sep+\
                          entry['product_anomaly_filename_prefix']+\
                          entry['frequency_filename_prefix']+\
                          str(entry['days'])+os.path.sep

            logger.info('Working on [%s]/[%s]/[%s]/[%s]' % (product_code,version,my_mapset,sub_product_code))
            ds = Dataset(product_code,sub_product_code,my_mapset,version=version,from_date=from_date,to_date=to_date)
            if use_range:
                available_files=ds.get_filenames_range()
            else:
                available_files=ds.get_filenames()

            # Convert input products
            if len(available_files) > 0:
                for input_file in available_files:

                    # Check it is a .tif file (not .missing)
                    path, ext=os.path.splitext(input_file)
                    if ext == '.tif':
                        functions.check_output_dir(output_dir+out_sub_dir)
                        str_date = functions.get_date_from_path_filename(os.path.basename(input_file))

                        # Check input file exists
                        if os.path.isfile(input_file):
                            if len(naming_spirits['frequency_filename_prefix']) > 1:
                                my_str_date=naming_spirits['frequency_filename_prefix'][1:5]+str_date
                                metadata_spirits['date'] = my_str_date
                            else:
                                metadata_spirits['date'] = str_date

                            # Check output file exists
                            convert_geotiff_file(input_file, output_dir+out_sub_dir, str_date, naming_spirits, metadata_spirits)
                        else:
                            logger.debug('Input file does not exist: %s' % input_file)