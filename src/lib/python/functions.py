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

import os
import sys
import math
import calendar
import datetime
import re
import resource
from datetime import date

#sys.path.append('/srv/www/eStation2/')                  # needed for offline processing TODO-M.C. : remove ?
#from lib.python import es_logging as log
from config.es2 import *

logger = log.my_logger(__name__)


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
def is_date_yyyymmdd(string_date):
    isdate_yyyymmdd = False
    # check the length of string_date
    if len(str(string_date)) != 8:
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

    if not isdate_yyyymmdd:
        logger.error('Invalid Date Format   %s' % string_date)

    return isdate_yyyymmdd


######################################################################################
#   is_date_yyyymmddhhmm
#   Purpose: Function validates if a date has  the format YYYYMMDDHHMM.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYMMDDHHMM, otherwise return False
def is_date_yyyymmddhhmm(string_date):
    isdate_yyyymmddhhmm = False
    # check the length of string_date
    if len(str(string_date)) != 12:
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

    if not isdate_yyyymmddhhmm:
        logger.error('Invalid Date Format %s' % string_date)

    return isdate_yyyymmddhhmm


######################################################################################
#   is_date_yyyymmdd
#   Purpose: Function validates if a date has  the format YYYYDOY where DOY is Day Of Year.
#   Author: Jurriaan van 't Klooster, JRC, European Commission
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYDOY, otherwise return False
def is_date_yyyydoy(string_date):
    isdate_yyyydoy = False
    # check the length of string_date
    if 5 >= len(str(string_date)) <= 7:
        logger.error('Invalid Length in Date Format %s' % string_date)
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

    if not isdate_yyyydoy:
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
#   Purpose: Function returns a date (YYYYMMDD) by using a dekad as input
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

    return dekad_date


######################################################################################
#   conv_month_2_date
#   Purpose: Function returns a date by using the no of month as input
#            The months are counted having as reference January 1, 1980.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: the no of month
#   Output: YYYYMMDD, otherwise 0
def conv_month_2_date(month):
    month_date = -1
    if not 1 <= int(str(month)) <= 12:
        logger.error('Invalid Month Value: %s. Must be >= 1 and <= 12' % month)
    else:
        month = int(str(month)) - 1
        year = month / 12
        month -= year * 12
        #returns always the first dekad of the month
        month_date = 10000 * (year + 1980) + 100 * (month + 1) + 1

    return month_date


###
#
# date2RepCycle
# author: Marco Clerici, JRC, European Commission
# date: 04/05/2010
# Converts a date in format YYYYMMDDHHMM to the MSG repeat cycle (15 min) since 1980:01:01 00:00
###
#function date2RepCycle(){
#    if [ $# -ne 1 ]; then
#	echo '0'
#    else
#	if [ -z "$(isYYYYMMDDHHMM $1)" ]; then
#	    echo "0"
#	else
#	    local date=${1:0:8}
#	    local hh=${1:8:2}
#	    local min=${1:10:2}
#		jday=$(YYYYMMDD2Jday $date)
#	    str=` echo " (${jday}-1)*96 + ${hh}*4 + ${min}/15+1" | bc`
#		echo $str
#	fi
#    fi
#}


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
#                            OTHER FUNCTIONS
######################################################################################


#  Simple function to show the memory Usage
# (see http://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python)
def mem_usage(point=""):
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           ''' % (point, usage[0], usage[1], (usage[2]*resource.getpagesize())/1000000.0)


######################################################################################
#   create_prod_filename
#   Purpose: Create the full product path+name
#   Author: Simona Oancea, JRC, European Commission
#   Date: 2014/04/08
#   Inputs: product, subproduct, version, mapset, date
#   Output: directory and filename
#
def create_prod_filename(product, subproduct, version, mapset, date):

    sub_dir = 'VGT_NDVI/tif/NDV/'
    filename = '20130701_VGT_NDVI_NDV_WGS84_Africa_1km.tif'
    return sub_dir, filename


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
