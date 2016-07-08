#
#	purpose: Define a library of functions for general purpose operations
#	author:  M.Clerici
#	date:	 28.02.2014
#   descr:	 It correspond to the file 'Functions' in rel. 1.X, for bash functions.
#            It contains the following sets of functions:
#            System:    manage the 'system' tab
#            Date/Time: convert date/time between formats
#            Naming:    manage file naming
#            General:   general purpose functions
#
#	history: 1.0
#
#   TODO-M.C.: replace, where needed/applicable,  datetime()
#

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
import json
import glob
import subprocess
from socket import socket
import urllib2
import ast
from osgeo import gdal, osr

# Import eStation2 modules
from lib.python import es_logging as log
from config import es_constants

# from json import JSONEncoder
logger = log.my_logger(__name__)

dict_subprod_type_2_dir = {'Ingest': 'tif', 'Native': 'archive', 'Derived': 'derived'}

# class ObjectEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__dict__

def setThemaOtherPC(server_address, thema):
    from urllib2 import Request, urlopen, URLError
    thema_is_changed = False
    # Set "/esapp" in factorysettings.ini as webserver_root because on CentOS no /esapp is needed!
    url = "http://" + server_address + es_constants.es2globals['webserver_root'] + "/systemsettings/changethemafromotherpc?thema="+thema
    req = Request(url)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            logger.warning('We failed to reach a server to change the thema: %s' % server_address)
            logger.warning('Reason: %s' % e.reason)
        elif hasattr(e, 'code'):
            logger.warning('The server %s couldn\'t fulfill the request to change the thema.' % server_address)
            logger.warning('Error code: %s' % e.code)
        return thema_is_changed
    else:
        # everything is fine
        # response = urllib2.urlopen("http://" + server_address + "/esapp/dashboard/systemstatus")
        result = response.read()
        thema_is_changed = ast.literal_eval(result)
        response.close()  # best practice to close the file
    return thema_is_changed


def get_status_PC1():
    from urllib2 import Request, urlopen, URLError
    status_remote_machine = []
    # Set "/esapp" in factorysettings.ini as webserver_root because on CentOS no /esapp is needed!
    url = "http://mesa-pc1:5000/system-data"
    req = Request(url)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            logger.warning('We failed to reach a server: %s' % url)
            logger.warning('Reason: %s' % e.reason)
        elif hasattr(e, 'code'):
            logger.warning('The server %s couldn\'t fulfill the request.' % url)
            logger.warning('Error code: %s' % e.code)
        return status_remote_machine
    else:
        # everything is fine
        # response = urllib2.urlopen("http://" + server_address + "/esapp/dashboard/systemstatus")
        result = response.read()
        # status_remote_machine = ast.literal_eval(result)

        status_remote_machine = json.loads(result)

        response.close()  # best practice to close the file
    return status_remote_machine


def get_remote_system_status(server_address):
    from urllib2 import Request, urlopen, URLError
    status_remote_machine = []
    # Set "/esapp" in factorysettings.ini as webserver_root because on CentOS no /esapp is needed!
    url = "http://" + server_address + es_constants.es2globals['webserver_root'] + "/dashboard/systemstatus"
    req = Request(url)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            logger.warning('We failed to reach a server: %s' % server_address)
            logger.warning('Reason: %s' % e.reason)
        elif hasattr(e, 'code'):
            logger.warning('The server %s couldn\'t fulfill the request.' % server_address)
            logger.warning('Error code: %s' % e.code)
        return status_remote_machine
    else:
        # everything is fine
        # response = urllib2.urlopen("http://" + server_address + "/esapp/dashboard/systemstatus")
        result = response.read()
        status_remote_machine = ast.literal_eval(result)
        response.close()  # best practice to close the file
    return status_remote_machine


def _check_connection(server_info):
    cpos = server_info.find(':')
    try:
        sock = socket()
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((server_info[:cpos], int(server_info[cpos+1:])))
        # sock.shutdown(1)
        sock.close
        return True
    except:
        return False

def check_connection(server_info):
    try:
        # response = os.system("ping -c 1 " + hostname)
        response = os.system("ping -c 1 -w2 " + server_info + " > /dev/null 2>&1")
        # check the response...
        if response == 0:
          return True
        else:
          return False
    except:
        return False


def getStatusPostgreSQL():
    try:
        # Get status of postgresql
        command = [es_constants.es2globals['postgresql_executable'], 'status']  # /etc/init.d/postgresql-9.3  on CentOS
        # print command
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if re.search('online', out) or re.search('en cours', out):      # ToDo: Add Portuguese!
            psql_status = True
        else:
            psql_status = False

        return psql_status
    except:
        return False

def system_status_filename():
    check_output_dir(es_constants.es2globals['status_system_dir'])
    pickle_filename = es_constants.es2globals['status_system_pickle']
    return pickle_filename


def getStatusAllServices():
    from apps.acquisition import acquisition
    from apps.processing import processing
    from apps.es2system import es2system
    dry_run = True  # TODO: for getting the status of the services dry_run has to be False?

    # Get status of the ingestion service
    pid_file = es_constants.ingestion_pid_filename
    ingest_daemon = acquisition.IngestionDaemon(pid_file, dry_run=dry_run)
    ingest = ingest_daemon.status()

    # Get status of the get_internet service
    pid_file = es_constants.get_internet_pid_filename
    getinternet_daemon = acquisition.GetInternetDaemon(pid_file, dry_run=dry_run)
    internet = getinternet_daemon.status()

    # Get status of the get_eumetcast service
    pid_file = es_constants.get_eumetcast_pid_filename
    geteumetcast_daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=dry_run)
    eumetcast = geteumetcast_daemon.status()

    # Get status of the processing service
    pid_file = es_constants.processing_pid_filename
    processing_daemon = processing.ProcessingDaemon(pid_file, dry_run=dry_run)
    process = processing_daemon.status()

    # Get status of system service
    pid_file = es_constants.system_pid_filename
    system_daemon = es2system.SystemDaemon(pid_file, dry_run=dry_run)
    system = system_daemon.status()

    services_status = {'eumetcast': str(eumetcast).lower(),
                       'internet': str(internet).lower(),
                       'ingest': str(ingest).lower(),
                       'process': str(process).lower(),
                       'system': str(system).lower()}

    return services_status


def getListVersions():
    # Return the list of installed versions as a dictionary, by looking at versioned dirs
    base = es_constants.es2globals['base_dir']+"-"
    versions = []
    vers_dirs = glob.glob(base+'*')
    for ver in vers_dirs:
        if os.path.isdir(ver):
            v = ver.replace(base, '')
            versions.append(v)

    # Create empty dict
    versions_dict = []
    for v in versions:
        versions_dict.append({'version': v})

    return versions_dict


def setSystemSetting(setting=None, value=None):
    import ConfigParser
    if setting is not None:
        systemsettingsfilepath = es_constants.es2globals['settings_dir']+'/system_settings.ini'
        config_systemsettings = ConfigParser.ConfigParser()
        config_systemsettings.read(['system_settings.ini', systemsettingsfilepath])

        if config_systemsettings.has_option('SYSTEM_SETTINGS', setting):
            config_systemsettings.set('SYSTEM_SETTINGS', setting, value)

        # Writing our configuration file to 'system_settings.ini' - COMMENTS ARE NOT PRESERVED!
        with open(systemsettingsfilepath, 'wb') as configfile:
            config_systemsettings.write(configfile)
            configfile.close()
        return True
    else:
        return False


def setUserSetting(setting=None, value=None):
    import ConfigParser
    if setting is not None:
        usersettingsfilepath = es_constants.es2globals['settings_dir']+'/user_settings.ini'
        config_usersettings = ConfigParser.ConfigParser()
        config_usersettings.read(['user_settings.ini', usersettingsfilepath])

        if config_usersettings.has_option('USER_SETTINGS', setting):
            config_usersettings.set('USER_SETTINGS', setting, value)

        # Writing our configuration file to 'user_settings.ini' - COMMENTS ARE NOT PRESERVED!
        with open(usersettingsfilepath, 'wb') as configfile:
            config_usersettings.write(configfile)
            configfile.close()

        # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
        from lib.python import reloadmodules
        reloadmodules.reloadallmodules()
        # Reloading the settings does not work well so set manually
        es_constants.es2globals[setting] = value

        return True
    else:
        return False


def getSystemSettings():
    import ConfigParser

    thisfiledir = os.path.dirname(os.path.abspath(__file__))

    systemsettingsfile = es_constants.es2globals['settings_dir']+'/system_settings.ini'
    if not os.path.isfile(systemsettingsfile):
        systemsettingsfile = os.path.join(thisfiledir, 'config/install/', 'system_settings.ini')

    config_systemsettings = ConfigParser.ConfigParser()
    config_systemsettings.read([systemsettingsfile])

    systemsettings = config_systemsettings.items('SYSTEM_SETTINGS')  # returns a list of tuples
    # for setting, value in systemsettings:
    #      print setting + ': ' + value
    systemsettings = dict(systemsettings)   # convert list of tuples to dict
    # print systemsettings
    return systemsettings


def getUserSettings():
    import ConfigParser

    thisfiledir = os.path.dirname(os.path.abspath(__file__))

    if es_constants.es2globals['settings_dir'] != '':
        usersettingsfile = es_constants.es2globals['settings_dir']+'/user_settings.ini'
    else:
        usersettingsfile = '/eStation2/settings/user_settings.ini'

    if not os.path.isfile(usersettingsfile):
        usersettingsfile = os.path.join(thisfiledir, 'config/install/', 'user_settings.ini')

    config_usersettings = ConfigParser.ConfigParser()
    config_usersettings.read([usersettingsfile])

    usersettings = config_usersettings.items('USER_SETTINGS')  # returns a list of tuples
    # for setting, value in usersettings:
    #      print setting + ': ' + value
    usersettings = dict(usersettings)   # convert list of tuples to dict
    # print usersettings
    return usersettings


def checkIP():
    import socket

    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    return IP


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def unix_time_millis(d):
    dt = datetime.datetime.combine(d, datetime.time.min)
    return unix_time(dt) * 1000.0

######################################################################################
# Second function, rgb2html converts its arguments (r, g, b) to hexadecimal html-color string #RRGGBB
# Arguments are converted to integers and trimmed to 0..255 range. It is possible to call it with array argument
# rgb2html(array_of_three_ints) or specifying each component value separetly rgb2html(r, g, b).
#
def rgb2html(rgb):
    r = int(rgb[0])
    g = int(rgb[1])
    b = int(rgb[2])

    r = 0 if r < 0 else 255 if r > 255 else r
    r = "%x" % r

    g = 0 if g < 0 else 255 if g > 255 else g
    g = "%x" % g

    b = 0 if b < 0 else 255 if b > 255 else b
    b = "%x" % b

    color = '0' if len(r) < 2 else '' + r
    color += '0' if len(g) < 2 else '' + g
    color += '0' if len(b) < 2 else '' + b

    return '#'+color


def row2dict(row):
    d = {}
    if hasattr(row, "c"):
        for column in row.c._all_col_set:
            value = '' if str(getattr(row, column.name)) == 'None' else str(getattr(row, column.name))
            d[column.name] = value
    if hasattr(row, "_parent"):
        for column in row._parent.keys:
            value = '' if str(getattr(row, column)) == 'None' else str(getattr(row, column))
            d[column] = value

    return d


def tojson(queryresult):
    jsonresult = ''
    for row in queryresult:
        da = row2dict(row)
        jsonresult = jsonresult + json.dumps(da,
                                             ensure_ascii=False,
                                             sort_keys=True,
                                             indent=4,
                                             separators=(',', ': ')) + ', '
    jsonresult = jsonresult[:-2]
    return jsonresult

def _proxy_defined():

    proxy_def = True

    # Check if proxy is defined
    try:
        proxy_def = es_constants.es2globals['proxy']
    except:
        proxy_def = False

    if proxy_def:
        if proxy_def == '':
            proxy_def = False

    return proxy_def

def _proxy_internet_on():
    import urllib2

    test_url = 'http://google.com'
    # Case 1: proxy
    if _proxy_defined():
        try:
            proxy = urllib2.ProxyHandler({'http': _proxy_defined()})
            opener = urllib2.build_opener(proxy)
            response = opener.open(test_url)
            return True
        except:
            pass
        finally:
            opener = None
            proxy = None
    # Case 2: no proxy
    else:
        try:
            response = urllib2.urlopen(test_url, timeout=1)
            return True
        except:
            pass

    return False

def _internet_on():
    import os
    command = 'ping -c 1 -W 2 8.8.8.8'
    try:
        response = os.system(command)
    except: 
        pass    #  ping error
        return False
    if response == 0:
        return True
    else:
        return False

def internet_on():     # is_connected():
    import socket
    REMOTE_SERVER = "www.google.com"
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


######################################################################################
#                            DATE FUNCTIONS
######################################################################################

# Return True if the date is in the correct format
def checkDateFormat(myString):
    isDate = re.match('[0-1][0-9]\/[0-3][0-9]\/[1-2][0-9]{3}', myString)
    return isDate

######################################################################################
#   is_date_yyyymmdd
#   Purpose: Function validates if a date has  the format YYYYMMDD.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYMMDD, otherwise return False
#
def is_date_yyyymmdd(string_date, silent=False):
    isdate_yyyymmdd = False
    # check the length of string_date
    if len(str(string_date)) != 8:
        if not silent:
            logger.warning('Invalid Date Format %s' % string_date)
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
        logger.warning('Invalid Date Format   %s' % string_date)

    return isdate_yyyymmdd


######################################################################################
#   is_date_mmdd
#   Purpose: Function validates if a date has  the format MMDD.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format MMDD, otherwise return False
#
def is_date_mmdd(string_date, silent=False):
    isdate_mmdd = False
    # check the length of string_date
    if len(str(string_date)) != 4:
        if not silent:
            logger.warning('Invalid Date Format %s' % string_date)
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
        logger.warning('Invalid Date Format   %s' % string_date)

    return isdate_mmdd

######################################################################################
#   is_date_yyyymmddhhmm
#   Purpose: Function validates if a date has  the format YYYYMMDDHHMM.
#   Author: Simona Oancea, JRC, European Commission
#   Refactored by: Jurriaan van 't Klooster
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYMMDDHHMM, otherwise return False
#
def is_date_yyyymmddhhmm(string_date, silent=False):
    isdate_yyyymmddhhmm = False
    # check the length of string_date
    if len(str(string_date)) != 12:
        if not silent:
            logger.warning('Invalid Date Format %s' % string_date)
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
        logger.warning('Invalid Date Format %s' % string_date)

    return isdate_yyyymmddhhmm


######################################################################################
#   is_date_yyyymmdd
#   Purpose: Function validates if a date has  the format YYYYDOY where DOY is Day Of Year.
#   Author: Jurriaan van 't Klooster, JRC, European Commission
#   Date: 2014/05/06
#   Input: string of numbers
#   Output: return True if the input has the format YYYYDOY, otherwise return False
#
def is_date_yyyydoy(string_date, silent=False):
    isdate_yyyydoy = False
    # check the length of string_date
    if 5 >= len(str(string_date)) <= 7:
        if not silent:
            logger.warning('Invalid Date Format %s' % string_date)
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
        logger.warning('Invalid Date Format   %s' % string_date)

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
#
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
#
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
#
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
#
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
#
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
#
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
#
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
#
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
#   conv_yyyydmmdk_2_yyyymmdd
#   Purpose: Function returns a date (YYYYMMDD) with YYYYdMMdK as input.
#            K = 1 is day 1
#            K = 2 is day 11
#            K = 3 is day 21
#   Author: M. Clerici
#   Date: 2015/02/25
#   Input: string of numbers in the format YYYYdMMdK
#   Output: date (YYYYMMDD), otherwise -1
#
def conv_yyyydmmdk_2_yyyymmdd(yymmk):

    year = int(str(yymmk)[0:4])
    month = str(yymmk)[5:7]
    dekad = int(str(yymmk)[8:9])
    if dekad == 1:
        day = '01'
    elif dekad == 2:
        day = '11'
    elif dekad == 3:
        day = '21'
    else:
        date_yyyymmdd = -1

    #date_tmp = datetime.datetime(year=year, month=month, day=day)
    date_yyyymmdd = str(year)+month+day
    return date_yyyymmdd

######################################################################################
#   conv_yyyymmdd_g2_2_yyyymmdd
#   Purpose: Function returns a date (YYYYMMDD) with YYYYdMMdK as input.
#   Author: M. Clerici
#   Date: 2015/02/25
#   Input: string of numbers in the format YYYYdMMdK
#   Output: date (YYYYMMDD), otherwise -1
#
def conv_yyyymmdd_g2_2_yyyymmdd(yymmk):

    year = int(str(yymmk)[0:4])
    month = str(yymmk)[4:6]
    day = int(str(yymmk)[6:8])
    if day <= 10:
        day = '01'
    elif day <= 20:
        day = '11'
    else:
        day = '21'

    date_yyyymmdd = str(year)+month+day
    return date_yyyymmdd

######################################################################################
#   day_per_dekad
#   Purpose: Function returns the number of days per dekad (from 8 to 11)
#   Author: M. Clerici
#   Date: 2015/02/25
#   Input: dekad in format YYYYMMDD
#   Output: number of days
#
def day_per_dekad(yyyymmdd):

    from calendar import monthrange
    year = int(str(yyyymmdd)[0:4])
    month = int(str(yyyymmdd)[4:6])
    dekad = int(str(yyyymmdd)[6:8])
    if dekad <= 20:
        days = 10
    else:
        tot_days = monthrange(year,month)[1]
        days = tot_days - 20

    return days

######################################################################################
#   day_per_dekad
#   Purpose: Function returns the number of days per dekad (from 8 to 11)
#   Author: M. Clerici
#   Date: 2015/02/25
#   Input: dekad in format YYYYMMDD
#   Output: number of days
#
def get_number_days_month(yyyymmdd):

    from calendar import monthrange
    year = int(str(yyyymmdd)[0:4])
    month = int(str(yyyymmdd)[4:6])
    tot_days = monthrange(year,month)[1]

    return tot_days

######################################################################################
#   conv_list_2_string
#   Purpose: convert a list of strings in a single string (mainly for messages)
#   Author: M. Clerici
#   Date: 2015/02/25
#   Input: string of numbers in the format YYYYdMMdK
#   Output: date (YYYYMMDD), otherwise -1
#
def conv_list_2_string(inlist):
    file_string = ''
    try:
        if isinstance(inlist,basestring):
            file_string+=inlist
        else:
            for ifile in inlist:
                file_string+=ifile+';'
    except:
        pass
    return file_string

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
#
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
#       e.g.            /data/processing/vgt-ndvi/spot-v1/vgt/derived/10davg
#
#       filename is always
#                       <product-code>_'<sub-product-code>'_'<datefield>'_'<mapset>'_'<version>'.'<ext>
#       e.g.            vgt-ndvi_ndv_20150101_WGS84-Africa-1km_spot-v1.tif
#
#   Conventions: product_code and sub_product_code should not contains '_' !!!
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
def set_path_filename_no_date(product_code, sub_product_code, mapset_id, version, extension):

    filename_nodate =     "_" + str(product_code) + '_' \
                              + str(sub_product_code) + "_" \
                              + mapset_id +  "_" \
                              + version + extension

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
def set_path_filename(date_str, product_code, sub_product_code, mapset_id, version,  extension):

    filename = date_str + set_path_filename_no_date(product_code, sub_product_code, mapset_id, version, extension)
    return filename


######################################################################################
#   set_path_sub_directory
#   Purpose: From product_code, sub_product_code, product_type, version, mapset  -> sub_directory
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: product_code, sub_product_code, product_type, version
#   Output: subdir, e.g. vgt-ndvi/spot-v1/vgt/derived/10davg/
#   Description: creates filename
#
def set_path_sub_directory(product_code, sub_product_code, product_type, version, mapset):

    type_subdir = dict_subprod_type_2_dir[product_type]

    if product_type == 'Native':
        # In case of 'Native product' do not add final 'subproductcode' and do not use 'mapset'
        sub_directory = str(product_code) + os.path.sep + \
                        str(version) + os.path.sep + \
                        type_subdir + os.path.sep

    else:
        sub_directory = str(product_code) + os.path.sep + \
                        str(version) + os.path.sep + \
                        mapset + os.path.sep +\
                        type_subdir + os.path.sep +\
                        str(sub_product_code) + os.path.sep

    return sub_directory

######################################################################################
#   set_path_filename_eumetcast
#   Purpose: From date, product_code, sub_product_code, mapset, extension -> filename
#            for the EUMETCast dissemination
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/06/22
#   Inputs: ...
#   Output: filename
#   Description: creates filename
#
def set_path_filename_eumetcast(date_str, product_code, sub_product_code, mapset_id, version,  extension):

    filename = es_constants.es2globals['prefix_eumetcast_files'] +\
               product_code + '_' + \
               sub_product_code + '_' +\
               date_str + '_'+\
               mapset_id + '_' +\
               version +\
               extension

    return filename

######################################################################################
#   get_from_path_dir
#   Purpose: From full_dir -> prod, subprod, version, mapset
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: output_dir
#   Output: none
#   Description: returns information form the directory
#
def get_from_path_dir(dir_name):

    # Make sure there is a leading separator at the end of 'dir'
    mydir=dir_name+os.path.sep

    tokens = [token for token in mydir.split(os.sep) if token]
    sub_product_code = tokens[-1]
    mapset = tokens[-3]
    version =  tokens[-4]
    product_code =  tokens[-5]

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
def get_date_from_path_filename(filename):

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
def get_date_from_path_full(full_path):

    # Remove the directory
    dir, filename = os.path.split(full_path)

    # Get the date string
    str_date = get_date_from_path_filename(filename)

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
def get_subdir_from_path_full(full_path):

    # Remove the directory
    subdirs = full_path.split(os.path.sep)
    str_subdir = subdirs[-6]+os.path.sep+subdirs[-5]+os.path.sep+subdirs[-4]+os.path.sep+subdirs[-3]+os.path.sep+subdirs[-2]+os.path.sep

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
def get_all_from_path_full(full_path):

    # Split directory and filename
    dir, filename = os.path.split(full_path)

    # Get info from directory
    product_code, sub_product_code, version, mapset = get_from_path_dir(dir)

    # Get info from filename
    str_date = get_date_from_path_filename(filename)

    return [product_code, sub_product_code, version, str_date, mapset]


######################################################################################
#   get_all_from_filename
#   Purpose: Extract all components from filename (no full_path)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: product_code, sub_product_code, date, mapset, version
#   Description: returns information form the fullpath
#
# def get_all_from_filename(full_path):
#
#     # Split directory and filename
#     dir, filename = os.path.split(full_path)
#
#     # Get info from directory
#     product_code, sub_product_code, version, mapset = get_from_path_dir(dir)
#
#     # Get info from filename
#     str_date = get_date_from_path_filename(filename)
#
#     return [product_code, sub_product_code, version, str_date, mapset]

######################################################################################
#   get_all_from_filename
#   Purpose: Extract all components from filename (no full_path)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: product_code, sub_product_code, date, mapset, version
#   Description: returns information form the fullpath
#
def get_all_from_filename(filename):

    # Get info from directory
    tokens = [token for token in filename.split('_') if token]
    str_date = tokens[0]
    product_code = tokens[1]
    sub_product_code = tokens[2]
    mapset = tokens[3]
    # Remove extension from tokens[4] -> version
    parts = tokens[4].split('.')
    version = tokens[4].replace('.'+parts[-1],'')

    return [str_date, product_code, sub_product_code, mapset, version]

######################################################################################
#   get_all_from_filename_eumetcast
#   Purpose: Extract all components from filename_eumetcast (no full_path)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: product_code, sub_product_code, date, mapset, version
#   Description: returns information form the fullpath
#
def get_all_from_filename_eumetcast(filename):

    extension='.tif'
    # Ensure there is no dir path
    fileonly = os.path.basename(filename)
    # Get info from directory
    tokens = [token for token in fileonly.split('_') if token]
    product_code = tokens[2]
    sub_product_code = tokens[3]
    str_date = tokens[4]
    mapset = tokens[5]
    version =  tokens[6].strip(extension)

    return [str_date, product_code, sub_product_code, mapset, version]
######################################################################################
#   get_product_type_from_subdir
#   Purpose: get the product type (Ingest/Derived) from subdir
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: sub_dir (like vgt-ndvi/spot-v1/WGS84-Africa-1km/tif/ndv/)
#   Output: product_type
#
def get_product_type_from_subdir(subdir):

    # Get info from directory
    tokens = [token for token in subdir.split(os.path.sep) if token]
    product_subdir = tokens[-2]
    for type, name in dict_subprod_type_2_dir.iteritems():
        if name == product_subdir:
            product_type = type
    return product_type

######################################################################################
#   convert_name_to_eumetcast
#   Purpose: Convert filename from the internal eStation to the EUMETCast transmission format
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename
#   Output: filename_eumetccast
#   Description: returns information form the fullpath
#
def convert_name_to_eumetcast(filename):

    extension = '.tif'
    [dir, name] = os.path.split(filename)

    [str_date, product_code, sub_product_code, mapset, version] = get_all_from_filename(name)

    filename_eumetcast = set_path_filename_eumetcast(str_date, product_code, sub_product_code, mapset, version, extension)

    return filename_eumetcast

######################################################################################
#   convert_name_from_eumetcast
#   Purpose: Convert filename from the EUMETCast transmission format to the internal eStation
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: filename_eumetcast (might contain a dirpath, which is cut)
#           product_type: Ingest or Derived
#           with_dir -> if set, it adds sub_dir
#   Output: filename           (only filename, no dir)
#   Description: returns information form the fullpath
#
def convert_name_from_eumetcast(filename, product_type, with_dir=False, new_mapset=False):

    extension = '.tif'
    [dir, name] = os.path.split(filename)
    [str_date, product_code, sub_product_code, mapset, version] = get_all_from_filename_eumetcast(name)
    if new_mapset:
        mapset = new_mapset
    filename = set_path_filename(str_date, product_code, sub_product_code, mapset, version, extension)
    if with_dir:
        subdir=set_path_sub_directory(product_code, sub_product_code, product_type, version, mapset)
        filename = subdir+filename
    return filename

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
            logger.error("Cannot create directory %s" % my_dir)

        logger.info("Output directory %s created" % my_dir)

    else:
        logger.debug("Output directory %s already exists" % my_dir)


######################################################################################
#   create_sym_link
#   Purpose: Create a (new) symbolic link from src_file -> trg_file
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/06/22
#   Inputs: output_dir, or list of dirs
#   Output: none
#
def create_sym_link(src_file, trg_file, force=False):

    # Does the source file already exist ?
    if not os.path.isfile(src_file):
        logger.info('Source file does not exist. Exit')
        return 1
    # Does the target file already exist ?
    if os.path.exists(trg_file):
        if os.path.islink(trg_file):
            if force:
                logger.info('Target file exists and FORCE=1. Overwrite')
                os.remove(trg_file)
            else:
                logger.debug('Target file exists and FORCE=0. Exit')
                return 1
        else:
            logger.debug('Target file exists as regular file. Exit')
            return 1
    # Create the symbolic link
    try:
        os.symlink(src_file, trg_file)
    except:
        logger.error('Error in creating symlink %s' % trg_file)


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

######################################################################################
#  Simple function to show the memory Usage
# (see http://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python)
#
def mem_usage(point=""):
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           ''' % (point, usage[0], usage[1], (usage[2]*resource.getpagesize())/1000000.0)


######################################################################################
#  Dump an object info a file (pickle serialization)
#
def dump_obj_to_pickle(obj, filename):

    dump_file = open(filename, 'wb')
    pickle.dump(obj, dump_file)
    dump_file.close()


######################################################################################
#  Restore an object from a file (pickle serialization), if the file exist
#  If file does not exist, do not alter the passed object
#  If file cannot be loaded (corrupted), delete it (and return the passed object)
#
def restore_obj_from_pickle(obj, filename):

    # Restore/Create Info
    if os.path.exists(filename):
        try:
            dump_file_info = open(filename, 'r')
            tmp_object = pickle.load(dump_file_info)
            logger.debug("Dump file info loaded from %s.", filename)
            obj = tmp_object
        except:
            logger.debug("Dump file %s can't be loaded, the file will be removed.", filename)
            os.remove(filename)
    # else:
        # Create an empty file in the tmp dir
        # logger.debug("Dump file %s does not exist", filename)
        #open(filename, 'a').close()

    return obj


######################################################################################
#  Load an object from a file (pickle serialization), if the file exist
#
def load_obj_from_pickle(filename):

    obj = None

    # Restore/Create Info
    if os.path.exists(filename):
        try:
            dump_file_info = open(filename, 'r')
            obj = pickle.load(dump_file_info)
        except:
            logger.debug("Dump file %s can't be loaded, the file will be removed.", filename)
    # else:
        # Raise warning
        # logger.debug("Dump file %s does not exist.", filename)

    return obj


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
    dir, filename = os.path.split(file_t0)

    # Extract all info from full path
    product_code, sub_product_code, version, date_t0, mapset = get_all_from_path_full(file_t0)

    if step == 'dekad':

        dekad_t0 = conv_date_2_dekad(date_t0)
        # Compute/Check file before
        dekad_m = dekad_t0-1
        date_m = conv_dekad_2_date(dekad_m)
        file_m = dir+os.path.sep+set_path_filename(str(date_m), product_code, sub_product_code, mapset, version, extension)

        if os.path.isfile(file_m):
            file_list.append(file_m)
        else:
            logger.warning('File before t0 does not exist: %s ' % file_m)

        # Compute/Check file after
        dekad = conv_date_2_dekad(date_t0)
        dekad_p = dekad_t0+1
        date_p = conv_dekad_2_date(dekad_p)
        file_p = dir+os.path.sep+set_path_filename(str(date_p), product_code, sub_product_code, mapset, version, extension)

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

    filename = es_constants.es2globals.get_eumetcast_processed_list_prefix+str(eumetcast_id)+'.info'
    info = load_obj_from_pickle(filename)
    return info


######################################################################################
#                            PROCESSING CHAINS
######################################################################################

class ProcLists:

    def __init__(self):
        self.list_subprods = []
        self.list_subprod_groups = []

    def proc_add_subprod(self, sprod, group,
                         final=False,
                         descriptive_name='',
                         description = '',
                         frequency_id = '',
                         date_format = '',
                         masked = '',
                         timeseries_role = '10d',
                         active_default=True):

        self.list_subprods.append(ProcSubprod(sprod, group, final,
                                              descriptive_name=descriptive_name,
                                              description = description,
                                              frequency_id = frequency_id,
                                              date_format = date_format,
                                              masked = masked,
                                              timeseries_role = timeseries_role,
                                              active_default=True))
        return sprod

    def proc_add_subprod_group(self, sprod_group, active_default=True):
        self.list_subprod_groups.append(ProcSubprodGroup(sprod_group, active_default=True))
        return sprod_group


class ProcSubprod:
    def __init__(self, sprod, group,
                 final=False,
                 descriptive_name='',
                 description = '',
                 frequency_id = '',
                 date_format = '',
                 masked = '',
                 timeseries_role = '',
                 active_default=True,
                 active_depend=False):

        self.sprod = sprod
        self.group = group
        self.descriptive_name = descriptive_name
        self.description = description
        self.frequency_id = frequency_id
        self.date_format = date_format
        self.masked = masked
        self.timeseries_role = timeseries_role
        self.final = final
        self.active_default=active_default
        self.active_user = True
        self.active_depend = active_depend


class ProcSubprodGroup:
    def __init__(self, group, active_default=True):
        self.group = group
        self.active_default=active_default
        self.active_user = True
