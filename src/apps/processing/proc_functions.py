from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Helpers for the processing.py and processing_..py

# import standard modules
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import datetime
import os
import glob
import subprocess
import fnmatch

# import eStation2 modules
from database import querydb
from apps.productmanagement import datasets
from apps.productmanagement import products
from config import es_constants
from lib.python import metadata
from lib.python import functions
from lib.python import es_logging as log


######################################################################################
#
#   Purpose: for a prod/subprod/version returns a list of date adapted to its frequency and dateformat, and
#
#            start_date |-| end_date        [if both are provided]
#            start_date  -> today           [if only start is provided]
#            None                           [if none is provided]
#
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/02/15
#   Inputs:
#   Output: none
#

def get_list_dates_for_dataset(product_code, sub_product_code, version, start_date=None, end_date=None):
    # Manage the dates
    if (start_date != None) or (end_date != None):
        # Get the frequency from product table
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code,
                                                    version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code, '', version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        if dateformat == 'YYYYMMDDHHMM':
            list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end), '%Y%m%d%H%M')
        else:
            list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end), '%Y%m%d')

    else:
        list_dates = None

    return list_dates


######################################################################################
#
#   Purpose: for a prod/subprod/version/mapset creates the permanently missing files
#            within the period:
#            start_date |-| end_date                     [if both are provided]
#            start_date  -> last_existing_date           [if only start is provided]
#            first_existing_date |-| last_existing_date  [if none is provided]
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs:
#   Output: none
#

def create_permanently_missing_for_dataset(product_code, sub_product_code, version, mapset_code, start_date=None,
                                           end_date=None):
    # Get the existing dates for the dataset
    product = products.Product(product_code, version=version)
    missing_filenames = product.get_missing_filenames({'product': product_code, 'version': version})

    # Manage the dates
    if (start_date != None) or (end_date != None):
        # Get the frequency from product table
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code,
                                                    version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code, '', version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end), '%Y%m%d')
    else:
        list_dates = None

    return list_dates


######################################################################################
#
#   Purpose: ensure the subproducts are present in the products.product table
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs:
#   Output: none
#

def upsert_database(product_code, version, proc_lists, input_product_info):
    # Get the existing dates for the dataset
    product = products.Product(product_code, version=version)
    missing_filenames = product.get_missing_filenames({'product': product_code, 'version': version})

    return 1


######################################################################################
#
#   Purpose: Remove files older than a number of months
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/05/15
#   Inputs: product identifiers (prod/sprod/version/mapset)
#           number of months
#   Output: none
#

def remove_old_files(productcode, subproductcode, version, mapsetcode, product_type, nmonths, logger=None):
    # Check logger
    if logger is None:
        logger = log.my_logger(__name__)

    # Get the existing dates for the dataset
    logger.info("Entering routine %s " % 'remove_old_files')

    # Check the installation type
    sysSettings = functions.getSystemSettings()
    if sysSettings['type_installation'] == 'Server':
        logger.info("File housekeeping not done on Server ")
        return

    prod_subdir = functions.set_path_sub_directory(productcode, subproductcode, product_type, version, mapsetcode)
    prod_dir = es_constants.es2globals['processing_dir'] + os.path.sep + prod_subdir
    list_files = sorted(glob.glob(prod_dir + os.path.sep + '*.tif'))

    # Define the earliest date to be kept
    month_now = datetime.date.today().month
    year_now = datetime.date.today().year

    for my_file in list_files:
        # Extract the date
        date = functions.get_date_from_path_filename(os.path.basename(my_file))
        date_yyyy = int(date[0:4])
        date_month = int(date[4:6])

        if date_yyyy < year_now or (date_month + nmonths) <= month_now:
            logger.debug("Deleting file %s " % my_file)
            os.remove(my_file)


######################################################################################
#
#   Purpose: Check a directory and remove corrupted files
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2017/07/13
#   Inputs: directory to work on
#   Output: none
#

def clean_corrupted_files(check_directory, logger=None, dry_run=False):
    # Check logger
    if logger is None:
        logger = log.my_logger(__name__)

    # Get the existing dates for the dataset
    logger.info("Entering routine %s " % 'clean_corrupted_files')

    # Get list of files
    list_files = []
    for root, dirnames, filenames in os.walk(check_directory):
        for filename in fnmatch.filter(filenames, '*.tif'):
            list_files.append(os.path.join(root, filename))

    if len(list_files) > 0:
        for my_file in list_files:
            logger.debug('Checking file: {0}'.format(my_file))

            # Check the file by using gdalinfo
            command = ['gdalinfo', my_file]
            status = subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if status:
                logger.info('Error in file: {0}'.format(my_file))
                if not dry_run:
                    os.remove(my_file)
                    logger.info('File removed: {0}'.format(my_file))

                else:
                    logger.info('Not removing file {0} - Dry Run'.format(my_file))
