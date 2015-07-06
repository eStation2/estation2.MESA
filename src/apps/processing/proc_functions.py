# Helpers for the processing.py and processing_..py

# import standard modules
import datetime

# import eStation2 modules
from database import querydb
from apps.productmanagement import datasets
from apps.productmanagement import products

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
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code, version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code,'',version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end),'%Y%m%d')
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

def create_permanently_missing_for_dataset(product_code, sub_product_code, version, mapset_code, start_date=None, end_date=None):

    # Get the existing dates for the dataset
    product = products.Product(product_code,version=version)
    missing_filenames = product.get_missing_filenames({'product':product_code, 'version':version})

    # Manage the dates
    if (start_date != None) or (end_date != None):
        # Get the frequency from product table
        product_info = querydb.get_product_out_info(productcode=product_code, subproductcode=sub_product_code, version=version)
        frequency_id = product_info[0].frequency_id
        dateformat = product_info[0].date_format
        cDataset = datasets.Dataset(product_code, sub_product_code,'',version=version)
        cFrequency = cDataset.get_frequency(frequency_id, dateformat)

        # Build the list of dates
        date_start = cFrequency.extract_date(str(start_date))
        if (end_date != '' and end_date is not None):
            date_end = cFrequency.extract_date(str(end_date))
        else:
            date_end = datetime.date.today()

        list_dates = cFrequency.get_internet_dates(cFrequency.get_dates(date_start, date_end),'%Y%m%d')
    else:
        list_dates = None

    return list_dates
