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

# Import eStation2 modules
from lib.python import es_logging as log
from lib.python import functions
from database import querydb
logger = log.my_logger(__name__)

metadata_spirits= {'prod_values': '{NDVI-toc, -, 0, 250, 0, 250, -0.08, 0.004}',
                   'flags': '{251=missing, 252=cloud, 253=snow, 254=sea, 255=back, 254=back}', \
                   'data_ignore_value':'255', \
                   'days': 10, \
                   'sensor_type':'VEGETATION', \
                   'comment':'My comment', \
                   'sensor_filename_prefix':'', \
                   'frequency_filename_prefix':'', \
                   'pa_filename_prefix':''}

def write_properties(filename,dictionary):
    """ Writes the provided dictionary in key-sorted order to a properties file with each line of the format key=value

    Keyword arguments:
        filename -- the name of the file to be written
        dictionary -- a dictionary containing the key/value pairs.
    """
    with open(filename, "wb") as csvfile:
        writer = csv.writer(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
        for key, value in sorted(dictionary.items(), key=operator.itemgetter(0)):
                writer.writerow([ key, value])

def read_properties(filename,dictionary):
    """ Reads a given properties file with each line of the format key=value.  Returns a dictionary containing the pairs.

    Keyword arguments:
        filename -- the name of the file to be read
    """
    result={ }
    with open(filename, "rb") as csvfile:
        reader = csv.reader(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) != 2:
                raise csv.Error("Too many fields on row with contents: "+str(row))
            result[row[0]] = row[1]
    return result

# Modify the header file created by the conversion
def append_to_header_file(header_file, metadata_spirit):

    # Check the file exists
    if os.path.isfile(header_file):
        with open(header_file, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter='=', escapechar='\\', quoting=csv.QUOTE_NONE)
            for key, value in sorted(metadata_spirit.items(), key=operator.itemgetter(0)):
                    writer.writerow([ key, value])
    else:
         logger.error('The header file does not exist : : %s' % header_file)

# Convert a single file
def convert_geotiff_file(input_file, output_dir, str_date, md_spirit):

    extension_bin = '.bin'
    extension_hdr = '.hdr'

    # Define output filename
    output_base_name = md_spirit['sensor_filename_prefix']+'_'+\
                  md_spirit['frequency_filename_prefix']+'_'+\
                  str_date+'_'+ \
                  md_spirit['pa_filename_prefix']

    output_path = output_dir+os.path.sep+output_base_name+extension_bin

    command = es_constants.es2globals['gdal_translate']+ \
              ' -of ENVI ' + \
              input_file  + ' ' + \
              output_path

    print command

    # Execute command
    status = os.system(command)
    if status:
         logger.error('Error in converting file to SPIRITS format: %s' % input_file)

    # Modify the header
    header_file_name = output_dir+os.path.sep+output_base_name+extension_hdr
    status = append_to_header_file(header_file_name, metadata_spirits)

    if status:
         logger.error('Error in modifying SPIRITS header: %s' % header_file_name)

def convert_driver():
    # Read the spirits table and convert all existing files
    pass