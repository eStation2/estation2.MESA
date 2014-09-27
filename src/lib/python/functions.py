#
#	purpose: Define a library of functions for general purpose operations
#	author:  M.Clerici
#	date:	 28.02.2014
#   descr:	 It correspond to the file 'Functions' in rel. 1.X, for bash functions.
#            It contains the following sets of functions:
#            Time:      convert date/time between formats
#            Naming:    manage file naming
#            General:   general purpose functions
#
#	history: 1.0
#
#   TODO-M.C.: replace, where needed/applicable,  datetime()
#

# source eStation2 base definitions
import locals

# Import standard modules
import os
import math
import calendar
import datetime
import re
import resource
from datetime import date
import uuid
import pickle

# Import eStation2 modules
from lib.python import es_logging as log
from config.es_constants import *

logger = log.my_logger(__name__)

dict_subprod_type_2_dir = {'Ingest': 'tif', 'Native': 'archive', 'Derived': 'derived'}

######################################################################################
#                            DATE FUNCTIONS
######################################################################################

######################################################################################
#   is_date_yyyymmdd
#   Purpose: Function validates if a date has  the format YYYYMMDD.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYMMDD, otherwise return False
def is_date_yyyymmdd(string_date, silent=False):
    isdate_yyyymmdd = False
    # check the length of string_date
    if len(str(string_date)) != 8:
        if not silent:
            logger.error('Invalid Date Format %s' % string_date)
        return isdate_yyyymmdd

    # check the yyyymmdd format
    date_format_yyyymmdd = re.match('^[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9]', str(string_date))
    if date_format_yyyymmdd:
        year = int(string_date[0:4])
        month = int(string_date[4:6])
        day = int(string_date[6:8])
        # check the YYYY is real; between 1900 and current year
        if 1900 <= year <= date.today().year:
            # check the MM is real; => 1 and not greater than 12
            if 1 <= month <= 12:
                # check the DD is real; not greater than 31
                if 1 <= day <= 31:
                    # isdate_yyyymmdd = date_format_yyyymmdd.group(0)
                    isdate_yyyymmdd = True

    if (not isdate_yyyymmdd) and (not silent):
        logger.error('Invalid Date Format   %s' % string_date)

    return isdate_yyyymmdd


######################################################################################
#   is_date_mmdd
#   Purpose: Function validates if a date has  the format MMDD.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format MMDD, otherwise return False
def is_date_mmdd(string_date, silent=False):
    isdate_mmdd = False
    # check the length of string_date
    if len(str(string_date)) != 4:
        if not silent:
            logger.error('Invalid Date Format %s' % string_date)
        return isdate_mmdd

    # check the mmdd format
    date_format_mmdd = re.match('^[0-9][0-9][0-9][0-9]', str(string_date))
    if date_format_mmdd:
        month = int(string_date[0:2])
        day = int(string_date[2:4])
        # check the YYYY is real; between 1900 and current year
        if 1 <= month <= 12:
            # check the DD is real; not greater than 31
            if 1 <= day <= 31:
                isdate_mmdd = True

    if (not isdate_mmdd) and (not silent):
        logger.error('Invalid Date Format   %s' % string_date)

    return isdate_mmdd

######################################################################################
#   is_date_yyyymmddhhmm
#   Purpose: Function validates if a date has  the format YYYYMMDDHHMM.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYMMDDHHMM, otherwise return False
def is_date_yyyymmddhhmm(string_date, silent=False):
    isdate_yyyymmddhhmm = False
    # check the length of string_date
    if len(str(string_date)) != 12:
        if not silent:
            logger.error('Invalid Date Format %s' % string_date)
        return isdate_yyyymmddhhmm

    # check the yyyymmdd format
    date_format_yyyymmddhhmm = re.match('^[1-2][0-9][0-9][0-9][0-1][0-9][0-3][0-9][0-2][0-9][0-5][0-9]', str(string_date))
    if date_format_yyyymmddhhmm:
        year = int(string_date[0:4])
        month = int(string_date[4:6])
        day = int(string_date[6:8])
        hour = int(string_date[8:10])
        minutes = int(string_date[10:12])
        # check the MM and DD are  real; not 00 and 00, respectively
        if 1900 <= year <= date.today().year:
            # check the MM is  real; => 1 and not greater than 12
            if 1 <= month <= 12:
                # check the DD is  real; not greater than 31 and less than 1
                if 1 <= day <= 31:
                    # check the HH is real; not greater than 23 and smaller than 0
                    if 0 <= hour <= 23:
                        # check the MM is real; not greater than 59 and smaller than 0
                        if 0 <= minutes <= 59:
                            # isdate = date_format_yyyymmddhhmm.group(0)
                            isdate_yyyymmddhhmm = True

    if (not isdate_yyyymmddhhmm) and (not silent):
        logger.error('Invalid Date Format %s' % string_date)

    return isdate_yyyymmddhhmm


######################################################################################
#   is_date_yyyymmdd
#   Purpose: Function validates if a date has  the format YYYYDOY where DOY is Day Of Year.
#   Author: Jurriaan van 't Klooster, JRC, European Commission
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYDOY, otherwise return False
def is_date_yyyydoy(string_date, silent=False):
    isdate_yyyydoy = False
    # check the length of string_date
    if 5 >= len(str(string_date)) <= 7:
        if not silent:
            logger.error('Invalid Date Format %s' % string_date)
        return isdate_yyyydoy

    # check the yyyymmdd format
    date_format_yyyydoy = re.match('^[1-2][0-9][0-9][0-9][0-3][0-9][0-9]', str(string_date))
    if date_format_yyyydoy:
        year = string_date[0:4]
        doy = string_date[4:7]
        # check the YYYY is real; between 1900 and current year
        if 1900 <= int(year) <= date.today().year:
            # check the DOY is real; => 1 and not greater than 366
            if 1 <= int(doy) <= 366:
                # isdate_yyyydoy = date_format_yyyydoy.group(0)
                isdate_yyyydoy = True

    if (not isdate_yyyydoy) and (not silent):
        logger.error('Invalid Date Format   %s' % string_date)

    return isdate_yyyydoy

######################################################################################
#   conv_date_2_dekad
#   Purpose: Function returns a dekad by using a date (YYYYMMDD) as input.
#            The dekads are counted having as reference January 1, 1980.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers in the format YYYYMMDD
#   Output: dekad number in the range starting on Jan 1980, otherwise -1
def conv_date_2_dekad(year_month_day):
    dekad_no = -1
    # check the format of year_month_day. It must be a valid YYYYMMDD format.
    if is_date_yyyymmdd(year_month_day):
        # check if the year is equal or greater than 1980
        if not int(str(year_month_day)[0:4]) >= 1980:
            logger.error('Invalid Year of Date. Must be >= 1980 %s' % year_month_day)
        else:
            year = int(str(year_month_day)[0:4])            
            month = int(str(year_month_day)[4:6])
            day = int(str(year_month_day)[6:8])
            if day == 31:
                dekad_no = (year - 1980) * 36 + (month - 1) * 3 + 3
            if day != 31:
                dekad_no = (year - 1980) * 36 + (month - 1) * 3 + (day - 1) / 10 + 1

    return dekad_no


######################################################################################
#   conv_date_2_month
#   Purpose: Function returns the no of month by using a date (YYYYMMDD) as input
#            The months are counted having as reference January 1, 1980.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: YYYYMMDD
#   Output: month number in the range starting on Jan 1980, otherwise -1
def conv_date_2_month(year_month_day):
    month_no = -1
    # check the format of year_month_day. It must be a valid YYYYMMDD format.
    if is_date_yyyymmdd(year_month_day):
        # check if the year is equal or greater than 1980
        if not int(str(year_month_day)[0:4]) >= 1980:
            logger.error('Invalid Year of Date. Must be >= 1980 %s' % year_month_day)
        else:
            year = int(str(year_month_day)[0:4])
            month = int(str(year_month_day)[4:6])
            month_no = (year - 1980) * 12 + month

    return month_no


######################################################################################
#   conv_dekad_2_date
#   Purpose: Function returns a date (YYYYMMDD) by using a 'julian' dekad as input
#            The dekads are counted having as reference January 1, 1980.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: dekad 
#   Output: YYYYMMDD, otherwise 0
def conv_dekad_2_date(dekad):
    dekad_date = -1
    if int(str(dekad)) <= 0:
        logger.error('Invalid Dekad Value: %s. Must be >= 1' % dekad)
    else:
        dekad = int(str(dekad)) - 1
        year = dekad / 36
        month = (dekad - year * 36) / 3
        day = dekad - year * 36 - month * 3
        dekad_date = 10000 * (year + 1980) + 100 * (month + 1) + day * 10 + 1

    return str(dekad_date)


######################################################################################
#   conv_month_2_date
#   Purpose: Function returns a date by using the 'julian' month as input
#            The months are counted having as reference January 1, 1980.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: the no of month
#   Output: YYYYMMDD, otherwise 0
def conv_month_2_date(month):
    month_date = -1
    if not 1 <= int(str(month)):
        logger.error('Invalid Month Value: %s. Must be >= 1 ' % month)
    else:
        month = int(str(month)) - 1
        year = month / 12
        month -= year * 12
        #returns always the first dekad of the month
        month_date = 10000 * (year + 1980) + 100 * (month + 1) + 1

    return str(month_date)


######################################################################################
#   conv_date_yyyydoy_2_yyyymmdd
#   Purpose: Function returns YYYYMMDD by using 2 inputs:year(YYYY) and doy(DayofYear:1-365/366)
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Inputs: YYYY, DayofYear
#   Output: YYYYMMDD, otherwise 0
def conv_date_yyyydoy_2_yyyymmdd(yeardoy):
    # Convert Year and Day of Year to date
    # 1) datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1)
    # or
    # 2) date.fromordinal(date(year, 1, 1).toordinal() + doy - 1)

    year = yeardoy[0:4]
    doy = yeardoy[4:7]

    if len(str(year)) != 4:
        logger.error('Invalid Year Value. %s' % year)
        return -1
    if len(str(doy)) >= 4:
        logger.error('Invalid DayOfYear Value. %s' % doy)
        return -1
    year_leap = calendar.isleap(int(str(year)))
    if not year_leap:
        if int(str(doy)) <= 0 or int(str(doy)) >= 366:
            logger.error('Invalid DayOfYear Value. %s' % doy)
            return -1
    else:
        if int(str(doy)) <= 0 or int(str(doy)) >= 367:
            logger.error('Invalid DayOfYear Value. %s' % doy)
            return -1
    date_yyyymmdd = (datetime.datetime(int(str(year)), 1, 1) + datetime.timedelta(int(str(doy)) - 1)).strftime('%Y%m%d')    

    return date_yyyymmdd


######################################################################################
#   conv_date_yyyymmdd_2_doy
#   Purpose: Function returns DOY by using YYYYMMDD as input
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Inputs: YYYYMMDD
#   Output: DayofYear, otherwise 0
def conv_date_yyyymmdd_2_doy(year_month_day):
    day_of_year = -1
    if is_date_yyyymmdd(year_month_day):
        year = int(str(year_month_day)[0:4])
        month = int(str(year_month_day)[4:6])
        day = int(str(year_month_day)[6:8])
        dt = datetime.datetime(year=year, month=month, day=day)
        # year_leap = calendar.isleap(year)
        day_of_year = dt.timetuple().tm_yday

    return day_of_year


######################################################################################
#   conv_yyyy_mm_dkx_2_yyyymmdd
#   Purpose: Function returns a date (YYYYMMDD) with yyyy_mm_dkx as input.
#            DK1 is day 1
#            DK2 is day 11
#            DK3 is day 21
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers in the format YYYYMMDD
#   Output: date (YYYYMMDD), otherwise -1
def conv_yyyy_mm_dkx_2_yyyymmdd(yyyy_mm_dkx):
    date_yyyymmdd = -1
    # if is_yyyy_mm_dkx(yyyy_mm_dkx):

    # check if the year is equal or greater than 1980
    if not int(str(yyyy_mm_dkx)[0:4]) >= 1980:
        logger.error('Invalid Year of Date. Must be >= 1980 %s' % yyyy_mm_dkx)
    else:
        year = str(yyyy_mm_dkx)[0:4]
        month = str(yyyy_mm_dkx)[5:7]
        dekad = int(str(yyyy_mm_dkx)[10:11])
        if dekad == 1:
            day = '01'
        if dekad == 2:
            day = '11'
        if dekad == 3:
            day = '21'
        #date_tmp = datetime.datetime(year=year, month=month, day=day)
        date_yyyymmdd = year+month+day
    return date_yyyymmdd


######################################################################################
#   conv_yymmk_2_yyyymmdd
#   Purpose: Function returns a date (YYYYMMDD) with yymmk as input.
#            K = 1 is day 1
#            K = 2 is day 11
#            K = 3 is day 21
#   Author: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers in the format YYYYMMDD
#   Output: date (YYYYMMDD), otherwise -1
def conv_yymmk_2_yyyymmdd(yymmk):
    #date_yyyymmdd = -1
    # if is_yymmk(yymmk):

    year = int(str(yymmk)[0:2])
    if year >= 80:
        year += 1900
    else:
        year += 2000
    month = str(yymmk)[2:4]
    dekad = int(str(yymmk)[4:5])
    if dekad == 1:
        day = '01'
    if dekad == 2:
        day = '11'
    if dekad == 3:
        day = '21'
    #date_tmp = datetime.datetime(year=year, month=month, day=day)
    date_yyyymmdd = str(year)+month+day
    return date_yyyymmdd

######################################################################################
#   extract_from_date
#   Purpose: extract year, month, day, hour and min from string date
#            String is in format:
#            YYYYMMDDHHMM or
#            YYYYMMDD -> hh=0 and mm=0
#   Author: Marco Clerici
#   Date: 2014/06/22
#   Input: string in the format YYYYMMDDHHMM/YYYYMMDD
#   Output: year, month, day,

def extract_from_date(str_date):

    str_hour = '0000'

    if is_date_mmdd(str_date, silent=True):
        str_year=''
        str_month=str_date[0:2]
        str_day=str_date[2:4]

    if is_date_yyyymmdd(str_date, silent=True):
        str_year=str_date[0:4]
        str_month=str_date[4:6]
        str_day=str_date[6:8]

    if is_date_yyyymmddhhmm(str_date, silent=True):
        str_year=str_date[0:4]
        str_month=str_date[4:6]
        str_day=str_date[6:8]
        str_hour=str_date[8:12]

    return [str_year, str_month, str_day, str_hour]

######################################################################################
#                            FILE/DIRECTORY  NAMING and MANAGEMENT
######################################################################################
#
#   General rules:
#       dir is always
#                       ['data_dir']+<product_code>+<mapset>+[derived/tif]+<sub_product_code>
#       e.g.            /data/processing/FEWSNET_RFE/FEWSNET_Africa_8km/derived/10davg
#
#       filename is always
#                       <datefield>'_'<product_code>['_'<version>]'_'<sub_product_code>'_'<mapset>'_'<ext>
#       e.g.            0611_FEWSNET_RFE_10davg_FEWSNET_Africa_8km.tif
#
#   Conventions: product_code :  1+ '_" separators
#                sub_product_code : 0+ '_" separators
#
######################################################################################
#   set_path_filename_nodate
#   Purpose: From product_code, sub_product_code, mapset, extension -> filename W/O date
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: sub_product_code, mapset
#   Output: process_id, subdir
#   Description: creates filename WITHOUT date field (for ruffus formatters)
#
#
def set_path_filename_no_date(product_code, sub_product_code, mapset_id, extension):

    filename_nodate =     "_" + str(product_code) + '_' \
                              + str(sub_product_code) + "_" \
                              + mapset_id + extension

    return filename_nodate

######################################################################################
#   set_path_filename
#   Purpose: From date, product_code, sub_product_code, mapset, extension -> filename
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: sub_product_code, mapset
#   Output: process_id, subdir
#   Description: creates filename
#
#
def set_path_filename(date_str, product_code, sub_product_code, mapset_id, extension):

    filename = date_str + set_path_filename_no_date(product_code, sub_product_code, mapset_id, extension)
    return filename

######################################################################################
#   set_path_sub_directory
#   Purpose: From product_code, sub_product_code, product_type, version, mapset  -> sub_directory
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: product_code, sub_product_code, product_type, version
#   Output: subdir, e.g. FEWSNET_RFE/FEWSNET_Africa_8km/tif/RFE/
#   Description: creates filename
#
#
def set_path_sub_directory(product_code, sub_product_code, product_type, version, mapset):

    type_subdir = dict_subprod_type_2_dir[product_type]

    sub_directory = str(product_code) + os.path.sep + \
                    mapset + os.path.sep +\
                    type_subdir + os.path.sep +\
                    str(sub_product_code) + os.path.sep

    return sub_directory


######################################################################################
#   get_from_path_dir
#   Purpose: From full_dir -> prod, subprod, version, mapset
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: output_dir
#   Output: none
#   Description: returns information form the directory
#
#
#   NOTE:

def get_from_path_dir(dir_name):

    # Make sure there is a leading separator at the end of 'dir'
    mydir=dir_name+os.path.sep

    [head, sub_product_code] = os.path.split(os.path.split(mydir)[0])

    [head1, mapset] = os.path.split(os.path.split(head)[0])

    [head, product_code] = os.path.split(head1)

    # TODO-M.C.: implement version management
    version = 'undefined'

    return [product_code, sub_product_code, version, mapset]

######################################################################################
#   get_from_path_filename
#   Purpose: From filename-> str_date
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: date, mapset and version
#   Description: returns information form the filename
#
#

def get_date_from_path_filename(filename, extension=None):

    if extension is None:
        extension = '.tif'


    # Get the date string
    str_date = filename.split('_')[0]

    return str_date

######################################################################################
#   get_date_from_path_full
#   Purpose: From full_path -> date
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: date
#   Description: returns information form the fullpath
#
#

def get_date_from_path_full(full_path):

    # Remove the directory
    dir, filename = os.path.split(full_path)

    # Get the date string
    str_date = filename.split('_')[0]

    return str_date

######################################################################################
#   get_subdir_from_path_full
#   Purpose: From full_path -> subdir
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: date
#   Description: returns subdir from the fullpath
#
#

def get_subdir_from_path_full(full_path):

    # Remove the directory
    subdirs =  full_path.split(os.path.sep)
    str_subdir = subdirs[-5]+os.path.sep+subdirs[-4]+os.path.sep+subdirs[-3]+os.path.sep+subdirs[-2]+os.path.sep

    return str_subdir

######################################################################################
#   get_all_from_path_full
#   Purpose: From full_path -> product_code, sub_product_code, date, mapset, (version)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: date
#   Description: returns information form the fullpath
#
#

def get_all_from_path_full(full_path):

    # Split directory and filename
    dir, filename = os.path.split(full_path)

    # Get info from directory
    product_code, sub_product_code, version, mapset = get_from_path_dir(dir)

    # Get info from filename
    str_date = get_date_from_path_filename(filename)

    return [product_code, sub_product_code, version, str_date, mapset]

######################################################################################
#   check_output_dir
#   Purpose: Check output directory exists, otherwise create it.
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: output_dir, or list of dirs
#   Output: none
#

def check_output_dir(output_dir):

    # Is it a list ?
    if isinstance(output_dir, list):
        my_dir=output_dir[0]
    else:
        my_dir=output_dir
    # It does exist ?
    if not os.path.isdir(my_dir):
        try:
            os.makedirs(my_dir)
        except:
            logger.error("Cannot create directory %s"  % my_dir)

        logger.info("Output directory %s created" % my_dir)

    else:

        logger.debug("Output directory %s already exists" % my_dir)

######################################################################################
#   ensure_sep_present
#   Purpose: Check output directory exists, otherwise create it.
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: output_dir, or list of dirs
#   Output: none
#

def ensure_sep_present(path, position):

    if position=='begin':
        if not path.startswith("/"):
            path='/'+path
    elif position=='end':
        if not path.endswith("/"):
            path=path+'/'

    return path

######################################################################################
#                            MISCELLANEOUS
######################################################################################

#  Simple function to show the memory Usage
# (see http://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python)
def mem_usage(point=""):
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           ''' % (point, usage[0], usage[1], (usage[2]*resource.getpagesize())/1000000.0)

#  Dump an object info a file (pickle serialization)
def dump_obj_to_pickle(object, filename):

    dump_file = open(filename, 'wb')
    pickle.dump(object, dump_file)
    dump_file.close()

#  Restore an object from a file (pickle serialization), if the file exist
#  If file does not exist, create it empty
#  If file cannot be loaded, delete it

def restore_obj_from_pickle(object, filename):

    # Restore/Create Info
    if os.path.exists(filename):
        try:
            dump_file_info = open(filename, 'r')
            tmp_object = pickle.load(dump_file_info)
            logger.debug("Dump file info loaded from %s.", filename)
            object=tmp_object
        except:
            logger.warning("Dump file %s can't be loaded, the file will be removed.", filename)
            os.remove(filename)
    else:
        # Create an empty file in the tmp dir
        open(filename, 'a').close()

    return object

#  Load an object from a file (pickle serialization), if the file exist


def load_obj_from_pickle(filename):

    object = None

    # Restore/Create Info
    if os.path.exists(filename):
        try:
            dump_file_info = open(filename, 'r')
            object = pickle.load(dump_file_info)

        except:
            logger.warning("Dump file %s can't be loaded, the file will be removed.", filename)
    else:
        # Raise warning
        logger.warning("Dump file %s does not exist.", filename)

    return object


######################################################################################
#   modis_latlon_to_hv_tile
#   Purpose: Given a lat/lon coordinate, converts it to hv tile
#   Author: Simona Oancea, JRC, European Commission
#   Date: 2014/05/06
#   Inputs: latitude, longitude
#   Output: tile horizontal "code" and vertical "code"
#
def modis_latlon_to_hv_tile(latitude, longitude):

    # Check args valid range
    if latitude > 90.0 or latitude < -90.0:
        logger.error('Latitude invalid %s' % latitude)
        return 1
    if longitude > 180.0 or longitude < -180.0:
        logger.error('Longitude invalid %s' % longitude)
        return 1

    #convert the data to tiles
    rad_sphere = 6371007.181
    t_size = 1111950
    pi_val = math.pi
    x_val = rad_sphere * math.cos(latitude * pi_val / 180.0) * longitude * pi_val / 180.0
    y_val = rad_sphere * latitude * pi_val / 180.0
    # We subtract -0.5 to have to 'round' below working as a 'integer_part' (as in original algo)
    h1 = round(x_val / t_size - 0.5) + 18
    # We subtract -0.5 to have to 'round' below working as a 'integer_part' (as in original algo)
    v1 = 8 - round(y_val / t_size - 0.5)

    return h1, v1


######################################################################################
#   get_modis_tiles_list
#   Purpose: Given a mapset, returns list of MODIS tiles it overlaps
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2013/03/11
#   Inputs: mapset
#   Output: list of tiles.
#
def get_modis_tiles_list(mapset):

    tiles_list = ['h01v01', 'h01v02']
    return tiles_list


######################################################################################
#
#   Purpose: convert a non list/tuple object to a list
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs:
#   Output: none
#

def element_to_list(input_arg):

    # Is it a list or a tuple ?
    if type(input_arg) in (type([]), type(())):
        return input_arg
    else:
        my_list = []
        my_list.append(input_arg)
    return my_list

######################################################################################
#
#   Purpose: converts from list/tuple to element (the first one)
#            it raises a warning if there is more than one element
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs:
#   Output: none
#

def list_to_element(input_arg):

    # Is it a list or a tuple
    if type(input_arg) in (type([]), type(())):
        if len(input_arg) > 1:
            logger.warning('List/tuple contains more than 1 element !')

        return input_arg[0]
    else:
        return input_arg

######################################################################################
#
#   Purpose: given a file (t0), returns the two 'temporally-adjacent' ones
#            It also checks files exists (single file or empty list)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/07/09
#   Inputs:
#   Output: none
#
def files_temp_ajacent(file_t0, step='dekad', extension='.tif'):

    # Checks t0 exists
    if not os.path.isfile(file_t0):
        logger.warning('Input file does not exist: %s ' % file_t0)
        return None
    file_list = []

    # Extract dir input file
    dir, filename  = os.path.split(file_t0)

    # Extract all info from full path
    product_code, sub_product_code, version, date_t0, mapset = get_all_from_path_full(file_t0)

    if step == 'dekad':

        dekad_t0 = conv_date_2_dekad(date_t0)
        # Compute/Check file before
        dekad_m = dekad_t0-1
        date_m = conv_dekad_2_date(dekad_m)
        file_m = dir+os.path.sep+set_path_filename(str(date_m), product_code, sub_product_code, mapset, extension)

        if os.path.isfile(file_m):
            file_list.append(file_m)
        else:
            logger.warning('File before t0 does not exist: %s ' % file_m)

        # Compute/Check file after
        dekad = conv_date_2_dekad(date_t0)
        dekad_p = dekad_t0+1
        date_p = conv_dekad_2_date(dekad_p)
        file_p = dir+os.path.sep+set_path_filename(str(date_p), product_code, sub_product_code, mapset, extension)

        if os.path.isfile(file_p):
            file_list.append(file_p)
        else:
            logger.warning('File after t0 does not exist: %s ' % file_p)

        return file_list

    else:
        logger.warning('Time step (%s) not yet foreseen. Exit. ' % step)
        return None

######################################################################################
#
#   Purpose: return the machine address
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/07/09
#   Inputs:
#   Output: none
#

def get_machine_mac_address():

    return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def get_eumetcast_info(eumetcast_id):

    filename = get_eumetcast_processed_list_prefix+str(eumetcast_id)+'.info'
    info = load_obj_from_pickle(filename)
    return info
