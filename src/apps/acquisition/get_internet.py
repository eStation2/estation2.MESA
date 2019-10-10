#
#        purpose: Define the get_internet service
#        author:  M.Clerici
#        date:    19.02.2014
#        descr    Reads the definition from eStation DB and execute the copy to local disk
#        history: 1.0
#                 1.1 (7/6/16): create methods to manage an 'html-type' response in dir-listing and
#                               - apply to http site where listing is possible (e.g. NASA-MODIS)
#                               - apply to ftp when a proxy exists (e.g. JRC server)
#
# Import standard modules
import pycurl
import certifi  # Pierluigi
import signal
import StringIO
import cStringIO
import tempfile
import sys
import os
import re
import datetime
import shutil
import time
import subprocess

from time import sleep

# Import eStation2 modules
from lib.python import es_logging as log
from config import es_constants
from database import querydb
from lib.python import functions
from apps.productmanagement import datasets
from apps.tools import motu_api
from apps.tools import jeodpp_api
from apps.tools import coda_eum_api

logger = log.my_logger(__name__)

#   General definitions
c = pycurl.Curl()
buffer = StringIO.StringIO()
if not os.path.isdir(es_constants.base_tmp_dir):
    os.makedirs(es_constants.base_tmp_dir)

#tmpdir = tempfile.mkdtemp(prefix=__name__, dir=es_constants.base_tmp_dir)
echo_query = False
user_def_sleep = es_constants.es2globals['poll_frequency']

#   ---------------------------------------------------------------------------
#   Functions
#   ---------------------------------------------------------------------------

######################################################################################
#   signal_handler
#   Purpose: properly terminate the service, in case of interruption
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: defaults for signal_handler

def signal_handler(signal, frame):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    logger.info("Length of processed list is %i" % len(processed_list))

    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
    functions.dump_obj_to_pickle(processed_info, processed_info_filename)

    print 'Exit ' + sys.argv[0]
    logger.warning("Get Internet service is stopped.")
    sys.exit(0)

######################################################################################
#   get_list_current_subdirs_ftp
#   Purpose: read a remote ftp directory and return contents.
#            It works on an 'ftp-type' response (i.e. dir listing)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: output_dir, or list of dirs
#   Output: list of dirs
#

def get_list_current_subdirs_ftp(remote_url, usr_pwd):

    d = pycurl.Curl()
    response = cStringIO.StringIO()
    d.setopt(pycurl.URL, remote_url)
    if usr_pwd != ':':
        d.setopt(pycurl.USERPWD, usr_pwd)
    d.setopt(pycurl.FOLLOWLOCATION, 1)
    d.setopt(pycurl.WRITEFUNCTION, response.write)
    d.perform()
    d.close()
    current_list = []
    content=response.getvalue()
    lines = content.split('\n')
    for line in lines:
        check_line = len(str(line))
        if check_line is not 0:
            line_dir=line.split()[-1]
            current_list.append(line_dir)
    
    return current_list
######################################################################################
#   get_list_current_subdirs_http
#   Purpose: read a remote http directory and return contents
#            It works on an 'http-type' response (from http-sites or ftp through proxy)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: output_dir, or list of dirs
#   Output: list of dirs
#

def get_list_current_subdirs_http(remote_url, usr_pwd, internet_type, path=None):

    if path is None:
        path= "/"

    if internet_type == 'http':
        pattern = '<a href=./%s.*?.>(.*?)</a></td>' % path
    elif internet_type == 'ftp':
        pattern = '<A HREF=.*?>(.*?)</A>'

    d = pycurl.Curl()
    response = cStringIO.StringIO()
    d.setopt(pycurl.URL, remote_url+path)
    d.setopt(pycurl.USERPWD, usr_pwd)
    d.setopt(pycurl.FOLLOWLOCATION, 1)
    d.setopt(pycurl.WRITEFUNCTION, response.write)
    d.perform()
    d.close()
    current_list = []
    content=response.getvalue()
    for filename in re.findall(pattern, content):
        current_list.append(filename)
    return current_list

######################################################################################
#   get_list_matching_files
#   Purpose: get the files matching a full_regex on a remote ftp.
#            It is the entry-point for 'ftp' type, and calls the recursive-method 'get_list_matching_files_subdirs'
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: remote_url: ftp address (might incl. sub_dirs)
#           usr_pwd: credentials (username:password)
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#   Output: list of matched files
#

def get_list_matching_files(remote_url, usr_pwd, full_regex, internet_type, my_logger=None, end_date=None):


    if my_logger is None:
        use_logger = logger
    else:
        use_logger = my_logger

    # Check the arguments (remote_url must end with os.sep and full_regex should begin with os.sep)
    remote_url=functions.ensure_sep_present(remote_url,'end')
    full_regex=functions.ensure_sep_present(full_regex,'begin')

    # Get list from a remote ftp
    list_matches=[]
    init_level = 1

    # Get contents of the current folder
    get_list_matching_files_subdirs(list_matches, remote_url, usr_pwd, full_regex, init_level, '', internet_type, my_logger=use_logger)
        
    # Manage end_date
    if end_date is not None:
        if isinstance(end_date,int) or isinstance(end_date,long):
            if (end_date < 0):
                try:
                    sorted_list = sorted(list_matches)
                    if len(sorted_list) >= -end_date:
                        list_matches = sorted_list[:end_date]
                except:
                    use_logger.warning('Error managing end_date: %i' % end_date)

    # Debug
    toprint=''
    for elem in list_matches:
        toprint+=elem+','

    use_logger.info('List in get_list_matching_files: %s' % toprint)

    return list_matches

######################################################################################
#   get_list_matching_files_subdirs
#   Purpose: return the list of matching files, or iterate the search
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: list: list of matching files, find so far
#           remote_url: ftp address (might incl. sub_dirs)
#           usr_pwd: credentials (username:password)
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           level: position in the full_regex tree (increasing from 1 ON .. )
#           sub_dir: current subdir searched on the site (appended to remote_url)
#
#   Output: list of matched files (incremented)
#   TODO-M.C.: check if the '/' has to be replaced by os.sep (?)

def get_list_matching_files_subdirs(list, remote_url, usr_pwd, full_regex, level, sub_dir, internet_type, my_logger=None):

    # Use generic logger (logger) for get_internet or my_logger (from get_eumetcast)
    if my_logger is None:
        use_logger = logger
    else:
        use_logger = my_logger

    # split the regex
    tokens=full_regex.split('/')
    # regex for this level
    regex_my_level=tokens[level]
    max_level= len(re.findall("/",full_regex))


    # Determine if there is a proxy
    proxy_exists = functions._proxy_defined()

    # Call functions for ftp-type or http-type response
    if internet_type == 'http' or (internet_type == 'ftp' and proxy_exists):
        #my_list = get_list_current_subdirs_ftp(remote_url, usr_pwd)
        my_list = get_list_current_subdirs_http(remote_url, usr_pwd, internet_type)
    elif internet_type == 'ftp_tmpl':
        my_list = get_list_current_subdirs_http(remote_url, usr_pwd, 'ftp')
    else:
        my_list = get_list_current_subdirs_ftp(remote_url, usr_pwd)

    use_logger.info("Working on %s" % regex_my_level)
    for element in my_list:
        if re.match(regex_my_level,element) is not None:
            # Is it already the file ?
            if max_level == level:
                list.append(sub_dir+element)
            else:
                # Enter the subdir
                new_level=level+1
                new_sub_dir=sub_dir+element+'/'
                new_remote_url=remote_url+'/'+element+'/'
                get_list_matching_files_subdirs(list, new_remote_url, usr_pwd, full_regex, new_level, new_sub_dir, internet_type)
    return 0

######################################################################################
#   build_list_matching_files_tmpl
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2015/02/18
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_tmpl(base_url, template, from_date, to_date, frequency_id, multi_template=False):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        if sys.platform == 'win32':
            template.replace("-","#")

        list_filenames = []

        if multi_template:
            list_temp = template.split(',')
            for temp in list_temp:
                list_matches = frequency.get_internet_dates(dates, temp)
                list_filenames = list_filenames + list_matches
        else:
            list_filenames = frequency.get_internet_dates(dates, template)

    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
        raise

    return list_filenames


######################################################################################
#   build_list_matching_files_tmpl_probavito
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: VIJAY CHARAN VENKATACHALAM, JRC, European Commission
#   Date: 2019/07
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_tmpl_vito(base_url, template, from_date, to_date, frequency_id):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        if sys.platform == 'win32':
            template.replace("-","#")
        #TODO store this list in factory settings or similar location
        xy_africa_list = ['X16Y04','X16Y05','X16Y06','X17Y03','X17Y04','X17Y05','X17Y06','X17Y07','X18Y03','X18Y04','X18Y05','X18Y06','X18Y07','X19Y03','X19Y04','X19Y05','X19Y06','X19Y07','X19Y08','X19Y09','X19Y10','X20Y04','X20Y05','X20Y06','X20Y07','X20Y08','X20Y09','X20Y10','X21Y04','X21Y05','X21Y06','X21Y07','X21Y08','X21Y09','X21Y10','X22Y05','X22Y06','X22Y07','X22Y08','X22Y09','X22Y10','X23Y06','X23Y08','X23Y09']
        list_filenames_vito = frequency.get_internet_dates(dates, template)
    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
        raise

    list_matches = []
    # init_level = 1

    for xy_value in xy_africa_list:
        for filename_vito in list_filenames_vito:
        # Get contents of the current folder
            filename_vito_replaced = filename_vito.replace("@@@@", xy_value)
            list_matches.append(filename_vito_replaced)

    # toprint = ''
    # for elem in list_matches:
    #     toprint += elem + ','
    #
    #     logger.info('List in get_list_matching_files: %s' % toprint)

    return list_matches

#####################################################################################
#   build_list_matching_files_tmpl_theia
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: VIJAY CHARAN VENKATACHALAM, JRC, European Commission
#   Date: 2019/08
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_tmpl_theia(base_url, template, from_date, to_date, frequency_id,username,password):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        if sys.platform == 'win32':
            template.replace("-","#")

        list_matches = []
        import json
        # Load the template json object and get the parameters
        parameters = json.loads(template)
        products = parameters.get('products')
        format = parameters.get('format')

        for waterbody in products.split():
            for date in dates:
                # authdownload?products=@@@@&format=csv&user=xxxxxxxxxxx
                template_filled = 'authdownload?products=' + waterbody + '&sdate=' + str(date.date()) + '&edate=' + str(
                    frequency.next_date(date).date()) + '&format=' + format + '&user=' + username + '&pwd=' + password
                file_name = "hydroprd_" + waterbody + "_from_" + str(date.date()) + "_to_" + str(
                    frequency.next_date(date).date()) + "." + format  # hydroprd_L_nasser_from_20150101_to_20151231.csv
                list_matches.append(template_filled + os.path.sep + file_name)

    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
        raise



    return list_matches

#####################################################################################
#   build_list_matching_files_jeodpp
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: VIJAY CHARAN VENKATACHALAM, JRC, European Commission
#   Date: 2019/09
#   Inputs: template: object with the needed parameters to fill the template get
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_jeodpp(base_url, template, from_date, to_date, frequency_id,usr_pwd):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        if sys.platform == 'win32':
            template.replace("-","#")

        list_productid_band = jeodpp_api.generate_list_products(dates, template, frequency, base_url, usr_pwd)

    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
        raise

    return list_productid_band



######################################################################################
#   build_list_matching_files_ftp_tmpl
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'ftp_templ' source type
#   Author: Vijay CHaran Venkatachalam, JRC, European Commission
#   Date: 2019/05/16
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_ftp_tmpl(base_url, template, from_date, to_date, frequency_id, usr_pwd, files_filter_expression):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        if sys.platform == 'win32':
            template.replace("-","#")
        list_ftp_pathes = frequency.get_internet_dates(dates, template)
    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" %inst.args[0])
        raise

    # Check the arguments (remote_url must end with os.sep and full_regex should begin with os.sep)
    remote_url = functions.ensure_sep_present(base_url, 'end')
    full_regex = functions.ensure_sep_present(files_filter_expression, 'begin')

    # Get list from a remote ftp
    list_matches = []
    init_level = 1

    for ftp_path in list_ftp_pathes:
        # Get contents of the current folder
        get_list_matching_files_subdirs(list_matches, remote_url+ftp_path, usr_pwd, full_regex, init_level, ftp_path, 'ftp_tmpl',
                                        my_logger=logger)

    # Manage end_date
    # if end_date is not None:
    #     if isinstance(end_date, int) or isinstance(end_date, long):
    #         if (end_date < 0):
    #             try:
    #                 sorted_list = sorted(list_matches)
    #                 if len(sorted_list) >= -end_date:
    #                     list_matches = sorted_list[:end_date]
    #             except:
    #                 use_logger.warning('Error managing end_date: %i' % end_date)

    # Debug
        toprint = ''
        for elem in list_matches:
            toprint += elem + ','

        logger.info('List in get_list_matching_files: %s' % toprint)

    return list_matches




######################################################################################
#   build_list_matching_files_sentinel_sat
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_templ' source type
#   Author: Vijay Charan Venkatachalam, JRC, European Commission
#   Date: 2019/02/18
#   Inputs: template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
# def build_list_matching_files_sentinel_sat(base_url, template, from_date, to_date, frequency_id,  username, password):
#
#     # Add a check on frequency
#     try:
#         frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
#     except Exception as inst:
#         logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
#         raise
#
#     # Manage the start_date (mandatory).
#     try:
#         # If it is a date, convert to datetime
#         if functions.is_date_yyyymmdd(str(from_date), silent=True):
#             datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
#         else:
#             # If it is a negative number, subtract from current date
#             if isinstance(from_date,int) or isinstance(from_date,long):
#                 if from_date < 0:
#                     datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
#             else:
#                 logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
#                 raise Exception("Start Date not valid")
#     except:
#         raise Exception("Start Date not valid")
#
#     # Manage the end_date (mandatory).
#     try:
#         if functions.is_date_yyyymmdd(str(to_date), silent=True):
#             datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
#         # If it is a negative number, subtract from current date
#         elif isinstance(to_date,int) or isinstance(to_date,long):
#             if to_date < 0:
#                 datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
#         else:
#             datetime_end=datetime.datetime.today()
#     except:
#         pass
#
#     try:
#         list_filenames = sentinelsat_api.sentinelsat_getlists(base_url, template, datetime_start, datetime_end)#frequency.get_dates(datetime_start, datetime_end)
#     except Exception as inst:
#         logger.debug("Error in sentinelsat.get_lists: %s" %inst.args[0])
#         raise
#
#     return list_filenames


######################################################################################
#   build_list_matching_files_motu
#   Purpose: return the list of file names matching a motu template with 'date' placeholders
#            It is the entry point for the 'motu_client' source type
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2018/11/05
#   Inputs: base_url: base url of motu client
#   `       template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#           username: username of motu client
#           password: password of motu client
#           files_filter_expression: output name template of motu client
#
def build_list_matching_files_motu(base_url, template, from_date, to_date, frequency_id, username, password, files_filter_expression):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
            elif to_date > 0:
                datetime_end = datetime.datetime.today() + datetime.timedelta(days=to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        list_filenames = motu_api.motu_4_dates(dates, template, base_url, username, password, files_filter_expression)
        #list_filenames = frequency.get_internet_dates(dates, template)
    except Exception as inst:
        logger.debug("Error in motu_api.motu_getlists: %s" %inst.args[0])
        raise

    return list_filenames

######################################################################################
#   build_list_matching_files_eum_http
#   Purpose: return the list of uuid/filename matching a query object with 'date' placeholders
#            It is the entry point for the 'eum_http' source type
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2019/06/04
#   Inputs: base_url: base url of motu client
#   `       template: regex including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#           username: username
#           password: password
#
def build_list_matching_files_eum_http(base_url, template, from_date, to_date, frequency_id, username, password):

    # Add a check on frequency
    try:
        frequency = datasets.Dataset.get_frequency(frequency_id, datasets.Frequency.DATEFORMAT.DATETIME)
    except Exception as inst:
        logger.debug("Error in datasets.Dataset.get_frequency: %s" %inst.args[0])
        raise

    # Manage the start_date (mandatory).
    try:
        # If it is a date, convert to datetime
        if functions.is_date_yyyymmdd(str(from_date), silent=True):
            datetime_start=datetime.datetime.strptime(str(from_date),'%Y%m%d')
        else:
            # If it is a negative number, subtract from current date
            if isinstance(from_date,int) or isinstance(from_date,long):
                if from_date < 0:
                    datetime_start=datetime.datetime.today() - datetime.timedelta(days=-from_date)
            else:
                logger.debug("Error in Start Date: must be YYYYMMDD or -Ndays")
                raise Exception("Start Date not valid")
    except:
        raise Exception("Start Date not valid")

    # Manage the end_date (mandatory).
    try:
        if functions.is_date_yyyymmdd(str(to_date), silent=True):
            datetime_end=datetime.datetime.strptime(str(to_date),'%Y%m%d')
        # If it is a negative number, subtract from current date
        elif isinstance(to_date,int) or isinstance(to_date,long):
            if to_date < 0:
                datetime_end=datetime.datetime.today() - datetime.timedelta(days=-to_date)
            elif to_date > 0:
                datetime_end = datetime.datetime.today() + datetime.timedelta(days=to_date)
        else:
            datetime_end=datetime.datetime.today()
    except:
        pass

    try:
        dates = frequency.get_dates(datetime_start, datetime_end)
    except Exception as inst:
        logger.debug("Error in frequency.get_dates: %s" %inst.args[0])
        raise

    try:
        list_filenames = coda_eum_api.generate_list_uuid(dates, template, base_url, username, password)
    except Exception as inst:
        logger.debug("Error in coda_eum_api.coda_getlists: %s" %inst.args[0])
        raise

    return list_filenames


######################################################################################
#   get_file_from_motu_command
#   Purpose: download and save motu file
#   Author: Vijay Charan Venkatachalam, JRC, European Commission
#   Date: 2018/11/05
#   Inputs: motu_command: full motu command
#           target_file: target file name (by default 'test_output_file')
#           target_dir: target directory (by default a tmp dir is created)
#   Output: full pathname is returned (or positive number for error)
#
def get_file_from_motu_command(motu_command,  target_dir,userpwd=''):

    # Create a tmp directory for download
    tmpdir = es_constants.es2globals['base_tmp_dir']
    result = 1

    # if target_file is None:
    #     target_file='test_output_file'

    list_motu_cmd = motu_command.split()
    target_file = list_motu_cmd[-1]

    target_fullpath=tmpdir+os.sep+target_file
    target_final=target_dir+os.sep

    #c = pycurl.Curl()

    try:
        #subprocess.call([motu_command])
        os.system(motu_command)
        #Check file exist in the path
        if functions.is_file_exists_in_path(target_fullpath):
            shutil.move(target_fullpath, target_final)
            result = 0
        else:
            result = 1

        # mv_cmd = "mv "+target_fullpath+' '+target_final
        # os.system(mv_cmd)
        #shutil.move(target_fullpath, target_final)
        return result
    except OSError:
        logger.warning('Output NOT downloaded: %s - error : %i' %(motu_command))
        return 1
    # finally:
    #     c = None
    #     shutil.rmtree(tmpdir)

######################################################################################
#   get_file_from_sentinelsat_url
#   Purpose: download and save locally a file
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: remote_url_file: full file path
#           target_file: target file name (by default 'test_output_file')
#           target_dir: target directory (by default a tmp dir is created)
#   Output: full pathname is returned (or positive number for error)

# def get_file_from_sentinelsat_url(uuid,  target_dir, target_file=None,userpwd=''):
#
#     # Create a tmp directory for download
#     tmpdir = tempfile.mkdtemp(prefix=__name__, dir=es_constants.es2globals['base_tmp_dir'])
#
#     # if target_file is None:
#     #     target_file='test_output_file'
#     #
#     target_fullpath=tmpdir+os.sep
#     target_final=target_dir+os.sep
#
#     try:
#         sentinelsat_api.download_sentinelsat_getlists(uuid, target_fullpath )
#         #TODO Below command has to be changed for windows version
#         mv_cmd = "mv "+target_fullpath+'* '+target_final
#         os.system(mv_cmd)
#         #outputfile.close()
#         #shutil.move(target_fullpath, target_final)
#
#         return 0
#     except:
#         logger.warning('Output NOT downloaded: %s - error : %i' %(uuid))
#         return 1
#     finally:
#         shutil.rmtree(tmpdir)


######################################################################################
#   get_file_from_url
#   Purpose: download and save locally a file
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: remote_url_file: full file path
#           target_file: target file name (by default 'test_output_file')
#           target_dir: target directory (by default a tmp dir is created)
#   Output: full pathname is returned (or positive number for error)
#
def get_file_from_url(remote_url_file, target_dir, target_file=None, userpwd='', https_params=''):

    # Create a tmp directory for download
    tmpdir = tempfile.mkdtemp(prefix=__name__, dir=es_constants.es2globals['base_tmp_dir'])

    if target_file is None:
        target_file='test_output_file'

    target_fullpath=tmpdir+os.sep+target_file
    target_final=target_dir+os.sep+target_file

    c = pycurl.Curl()

    try:
        outputfile=open(target_fullpath, 'wb')
        logger.debug('Output File: '+target_fullpath)
        remote_url_file = remote_url_file.replace('\\','') #Pierluigi
        c.setopt(c.URL,remote_url_file)
        c.setopt(c.WRITEFUNCTION,outputfile.write)
        if remote_url_file.startswith('https'):
            c.setopt(c.CAINFO, certifi.where()) #Pierluigi
            if https_params is not '':
            #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
                c.setopt(pycurl.HTTPHEADER, [https_params])
        if userpwd is not ':':
            c.setopt(c.USERPWD,userpwd)
        c.perform()
        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if c.getinfo(pycurl.HTTP_CODE) >= 400:
            outputfile.close()
            os.remove(target_fullpath)
            raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
        # See ES2-67
        elif c.getinfo(pycurl.HTTP_CODE) == 301:
            outputfile.close()
            os.remove(target_fullpath)
            raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
        else:
            outputfile.close()
            shutil.move(target_fullpath, target_final)
            return 0
    except:
        logger.warning('Output NOT downloaded: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
        return 1
    finally:
        c = None
        shutil.rmtree(tmpdir)


# ######################################################################################
# #   get_json_from_url
# #   Purpose: download and save locally a file
# #   Author: Vijay Charan, JRC, European Commission
# #   Date: 2019/09/13
# #   Inputs: remote_url_file: full file path
# #           target_file: target file name (by default 'test_output_file')
# #           target_dir: target directory (by default a tmp dir is created)
# #   Output: full pathname is returned (or positive number for error)
# #
# def get_json_from_url(remote_url_file, target_dir, target_file=None, userpwd='', https_params=''):
#
#     c = pycurl.Curl()
#
#     try:
#         from io import BytesIO
#         import json
#         data = BytesIO()
#
#         # outputfile=open(target_fullpath, 'wb')
#         # logger.debug('Output File: '+target_fullpath)
#         remote_url_file = remote_url_file.replace('\\','') #Pierluigi
#         c.setopt(c.URL,remote_url_file)
#         c.setopt(c.WRITEFUNCTION,data.write)
#         if remote_url_file.startswith('https'):
#             c.setopt(c.CAINFO, certifi.where()) #Pierluigi
#             if https_params is not '':
#             #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
#                 c.setopt(pycurl.HTTPHEADER, [https_params])
#         if userpwd is not ':':
#             c.setopt(c.USERPWD,userpwd)
#         c.perform()
#
#         # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
#         if c.getinfo(pycurl.HTTP_CODE) >= 400:
#             # outputfile.close()
#             # os.remove(target_fullpath)
#             raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
#         # See ES2-67
#         elif c.getinfo(pycurl.HTTP_CODE) == 301:
#             # outputfile.close()
#             # os.remove(target_fullpath)
#             raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
#         else:
#             list_dict = json.loads(data.getvalue())
#             # outputfile.close()
#             # shutil.move(target_fullpath, target_final)
#             return 0
#     except:
#         logger.warning('Output NOT downloaded: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
#         return 1
#     finally:
#         c = None
#         # shutil.rmtree(tmpdir)


######################################################################################
#   loop_get_internet
#   Purpose: drive the get_internet as a service
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: none
#   Arguments: dry_run -> if set, read tables and report activity ONLY
def loop_get_internet(dry_run=False, test_one_source=False):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)

    logger.info("Starting retrieving data from INTERNET.")

    while True:
        output_dir = es_constants.get_internet_output_dir
        logger.debug("Check if the Ingest Server input directory : %s exists.", output_dir)
        if not os.path.exists(output_dir):
            # ToDo: create output_dir - ingest directory
            logger.fatal("The Ingest Server input directory : %s doesn't exists.", output_dir)
            exit(1)

        if not os.path.exists(es_constants.processed_list_int_dir):
            os.mkdir(es_constants.processed_list_int_dir)

        while 1:

            # Check internet connection (or continue)
            if not functions.internet_on():
                logger.error("The computer is not currently connected to the internet. Wait 1 minute.")
                time.sleep(60)

            else:                
                    try:
                        time_sleep = user_def_sleep
                        logger.debug("Sleep time set to : %s.", time_sleep)
                    except:
                        logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
                        time_sleep = 60

                    logger.info("Reading active INTERNET data sources from database")
                    internet_sources_list = querydb.get_active_internet_sources()

                    # Loop over active triggers
                    for internet_source in internet_sources_list:
                      try:

                        if test_one_source and (internet_source.internet_id != test_one_source):
                            logger.info("Running in test mode, and source is not %s. Continue.", test_one_source)
                            continue
                        execute_trigger = True
                        # Get this from the pads database table (move from internet_source 'pull_frequency' to the pads table,
                        # so that it can be exploited by eumetcast triggers as well). It is in minute
                        pull_frequency = internet_source.pull_frequency

                        # Manage the case of files to be continuously downloaded (delay < 0)
                        if pull_frequency < 0:
                            do_not_consider_processed_list = True
                            delay_time_source_minutes = -pull_frequency
                        else:
                            do_not_consider_processed_list = False
                            delay_time_source_minutes = pull_frequency

                        if sys.platform == 'win32':
                            internet_id = str(internet_source.internet_id).replace(':', '_')
                        else:
                            internet_id = str(internet_source.internet_id)

                        logger_spec = log.my_logger('apps.get_internet.'+internet_id)
                        logger.info("Processing internet source  %s.", internet_source.descriptive_name)

                        # Create objects for list and info
                        processed_info_filename = es_constants.get_internet_processed_list_prefix+str(internet_id)+'.info'

                        # Restore/Create Info
                        processed_info = None
                        processed_info=functions.restore_obj_from_pickle(processed_info, processed_info_filename)
                        if processed_info is not None:
                            # Check the delay
                            current_delta=datetime.datetime.now()-processed_info['time_latest_exec']
                            current_delta_minutes=int(current_delta.seconds/60)
                            if current_delta_minutes < delay_time_source_minutes:
                                logger.debug("Still waiting up to %i minute - since latest execution.", delay_time_source_minutes)
                                execute_trigger = False
                        else:
                            # Create processed_info object
                            processed_info = {'lenght_proc_list': 0,
                                              'time_latest_exec': datetime.datetime.now(),
                                              'time_latest_copy': datetime.datetime.now()}
                            execute_trigger = True

                        if execute_trigger:
                            # Restore/Create List
                            processed_list = []
                            if not do_not_consider_processed_list:
                                processed_list_filename = es_constants.get_internet_processed_list_prefix+internet_id+'.list'
                                processed_list=functions.restore_obj_from_pickle(processed_list, processed_list_filename)

                            processed_info['time_latest_exec']=datetime.datetime.now()

                            logger.debug("Create current list of file to process for source %s.", internet_source.internet_id)
                            if internet_source.user_name is None:
                                user_name = "anonymous"
                            else:
                                user_name = internet_source.user_name

                            if internet_source.password is None:
                                password = "anonymous"
                            else:
                                password = internet_source.password

                            usr_pwd = str(user_name)+':'+str(password)

                            logger_spec.debug("              Url is %s.", internet_source.url)
                            logger_spec.debug("              usr/pwd is %s.", usr_pwd)
                            logger_spec.debug("              regex   is %s.", internet_source.include_files_expression)

                            internet_type = internet_source.type

                            if internet_type == 'ftp' or internet_type == 'http':
                                # Manage the end_date (added for MODIS_FIRMS)
                                if (internet_source.end_date != ''):
                                    end_date = internet_source.end_date
                                else:
                                    end_date = None
                                # Note that the following list might contain sub-dirs (it reflects full_regex)
                                try:
                                    current_list = get_list_matching_files(str(internet_source.url), str(usr_pwd), str(internet_source.include_files_expression), internet_type, end_date=end_date)
                                except:
                                    logger.error("Error in creating file lists. Continue")
                                    continue

                            elif internet_type == 'ftp_tmpl':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_ftp_tmpl(str(internet_source.url),
                                                                                str(internet_source.include_files_expression),
                                                                                internet_source.start_date,
                                                                                internet_source.end_date,
                                                                                str(internet_source.frequency_id),str(usr_pwd), str(internet_source.files_filter_expression) )
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue


                            elif internet_type == 'http_tmpl':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_tmpl(str(internet_source.url),
                                                                                  str(internet_source.include_files_expression),
                                                                                  internet_source.start_date,
                                                                                  internet_source.end_date,
                                                                                  str(internet_source.frequency_id))
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue

                            elif internet_type == 'http_multi_tmpl':
                                # Create the full filename from a multiple 'template' eg(product.img, product.hdr) which contains
                                try:
                                    current_list = build_list_matching_files_tmpl(str(internet_source.url),
                                                                                  str(internet_source.include_files_expression),
                                                                                  internet_source.start_date,
                                                                                  internet_source.end_date,
                                                                                  str(internet_source.frequency_id),
                                                                                  multi_template=True)
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue


                            elif internet_type == 'http_tmpl_vito':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_tmpl_vito(str(internet_source.url),
                                                                                str(internet_source.include_files_expression),
                                                                                internet_source.start_date,
                                                                                internet_source.end_date,
                                                                                str(internet_source.frequency_id))
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue

                            elif internet_type == 'http_tmpl_theia':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_tmpl_theia(str(internet_source.url),
                                                                                str(internet_source.include_files_expression),
                                                                                internet_source.start_date,
                                                                                internet_source.end_date,
                                                                                str(internet_source.frequency_id),
                                                                                user_name,
                                                                                password)
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue

                            elif internet_type == 'motu_client':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_motu(str(internet_source.url),
                                                                                str(internet_source.include_files_expression),
                                                                                internet_source.start_date,
                                                                                internet_source.end_date,
                                                                                str(internet_source.frequency_id),
                                                                                str(internet_source.user_name),
                                                                                str(internet_source.password),
                                                                                str(internet_source.files_filter_expression),
                                                                                  )

                                except:
                                    logger.error("Error in creating motu_client lists. Continue")
                                    continue

                            elif internet_type == 'jeodpp':
                                # Create the full filename from a 'template' which contains
                                jeodpp_internet_url = str(internet_source.url)

                                ongoing_list = []
                                ongoing_list_filename = es_constants.get_internet_processed_list_prefix + str(internet_source.internet_id) + '_Ongoing' + '.list'
                                ongoing_list = functions.restore_obj_from_pickle(ongoing_list, ongoing_list_filename)


                                try:
                                    current_list = []
                                    # Create current list in format IM:Band
                                    current_list = build_list_matching_files_jeodpp(jeodpp_internet_url,
                                                                                    str(internet_source.include_files_expression),
                                                                                    internet_source.start_date,
                                                                                    internet_source.end_date,
                                                                                    str(internet_source.frequency_id),
                                                                                    str(usr_pwd)
                                                                                    )

                                    # ongoing_product_list = jeodpp_api.get_product_id_from_list(ongoing_list)
                                    # product_product_list = jeodpp_api.get_product_id_from_list(processed_list)

                                    # read ongoing list from the file (in format IM:Band:ID:url) and convert to format IM:Band
                                    ongoing_product_band_list = jeodpp_api.get_product_id_band_from_list(ongoing_list)
                                    # read processed list from the file (in format IM:Band:ID:url) and convert to format IM:Band
                                    # processed_product_band_list = jeodpp_api.get_product_id_band_from_list(processed_list)
                                    # Loop over current list
                                    if len(current_list) > 0:
                                        listtoprocessrequest = []
                                        for current_file in current_list:
                                            # Check if current list is not in processed list
                                            if len(processed_list) == 0 and len(ongoing_list) == 0:
                                                listtoprocessrequest.append(current_file)
                                            else:
                                                if current_file not in processed_list and current_file not in ongoing_product_band_list:
                                                    # if current_file not in processed_list and current_file not in ongoing_product_band_list:
                                                    listtoprocessrequest.append(current_file)
                                        #ongoing_list= listtoprocessrequest   #line for test vto be commented
                                        if listtoprocessrequest != set([]):   #What if error occurs in this loop
                                            # logger_spec.info("Loop on the List to Process Request files.")
                                            for filename in list(listtoprocessrequest):  #What if error occurs in this loop
                                                logger_spec.info("Creating Job request for Product ID with Band: " + filename)
                                                try:
                                                    # Give request to JEODPP to process
                                                    # HTTP request to JEODPP follow here once the request is success add the oid to ongoing list
                                                    current_product_id = filename.split(':')[0]
                                                    current_product_band = filename.split(':')[1]
                                                    created_ongoing_link = jeodpp_api.create_jeodpp_job(
                                                                            base_url=jeodpp_internet_url,
                                                                            product_id=current_product_id, band=current_product_band,
                                                                            usr_pwd=usr_pwd,
                                                                            https_params=str(internet_source.https_params)
                                                    )
                                                    if created_ongoing_link is not None:
                                                        ongoing_list.append(created_ongoing_link) ## TODO have to dump object to pickle
                                                        functions.dump_obj_to_pickle(ongoing_list, ongoing_list_filename)
                                                except:
                                                    logger_spec.warning(
                                                        "Problem while creating Job request to JEODPP: %s.", filename)
                                    # functions.dump_obj_to_pickle(ongoing_list, ongoing_list_filename)
                                    if len(ongoing_list) > 0:
                                        logger_spec.info("Loop over the downloadable list files.")
                                        ongoing_product_list = jeodpp_api.get_product_id_from_list(ongoing_list)
                                        #Make the ongoing_product_list unique to loop over
                                        ongoing_product_list = functions.conv_list_2_unique_value(ongoing_product_list)
                                        # ongoing_job_list = jeodpp_api.get_job_id_from_list(ongoing_list)
                                        for each_product_id in ongoing_product_list: #What if error occurs in this loop
                                            listtodownload = []
                                            for ongoing in ongoing_list:
                                                ongoing_product_id = ongoing.split(':')[0]

                                                if each_product_id == ongoing_product_id:
                                                    ongoing_job_id = ongoing.split(':')[2]
                                                    job_status = jeodpp_api.get_jeodpp_job_status(
                                                                        base_url=jeodpp_internet_url,
                                                                        job_id=ongoing_job_id, usr_pwd=usr_pwd,
                                                                        https_params=str(internet_source.https_params))
                                                    if job_status:
                                                        listtodownload.append(ongoing)

                                            if listtodownload != set([]):
                                                download_urls = []
                                                for ongoing in list(listtodownload):
                                                    download_urls.append(ongoing.split(':')[3])

                                                if len(download_urls) > 0:
                                                    logger_spec.info("Downloading Product: " + str(each_product_id))
                                                    try:
                                                        download_result = jeodpp_api.download_file(
                                                            jeodpp_internet_url, target_dir=es_constants.ingest_dir,
                                                            product_id=each_product_id, userpwd=usr_pwd,
                                                            https_params=str(internet_source.https_params),
                                                            download_urls=download_urls)
                                                        if download_result:
                                                            logger_spec.info("Downloading Success for : " + str(each_product_id))
                                                            for ongoing in list(listtodownload):
                                                                ongoing_product_id = ongoing.split(':')[0]
                                                                ongoing_product_band = ongoing.split(':')[1]
                                                                ongoing_product_id_band = str(ongoing_product_id)+':'+str(ongoing_product_band)
                                                                processed_list.append(ongoing_product_id_band)   # Add the processed list only with product id and band
                                                                # processed_list.append(ongoing)
                                                                functions.dump_obj_to_pickle(processed_list, processed_list_filename)
                                                                ongoing_list.remove(ongoing)
                                                                functions.dump_obj_to_pickle(ongoing_list, ongoing_list_filename)
                                                                ongoing_job_id = ongoing.split(':')[2]
                                                                deleted = jeodpp_api.delete_results_jeodpp_job(
                                                                                    base_url=jeodpp_internet_url,
                                                                                    job_id=ongoing_job_id, usr_pwd=usr_pwd,
                                                                                    https_params=str(internet_source.https_params))
                                                                if not deleted:   # To manage the delete store the job id in the  delete list and remove the job
                                                                    logger_spec.warning("Problem while deleting Product job id: %s.",str(each_product_id)+str(ongoing_job_id))
                                                    except:
                                                        logger_spec.warning("Problem while Downloading Product: %s.",str(each_product_id))
                                    functions.dump_obj_to_pickle(ongoing_list, ongoing_list_filename)
                                    # functions.dump_obj_to_pickle(ongoing_info, ongoing_info_filename)
                                    #  Processed list will be added atlast
                                    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
                                    # functions.dump_obj_to_pickle(processed_info, processed_info_filename)


                                except:
                                    logger.error("Error in JEODPP Internet service. Continue")

                                finally:
                                    logger.info("JEODPP Internet service completed")
                                    current_list = []


                            # elif internet_type == 'sentinel_sat':
                            #     # Create the full filename from a 'template' which contains
                            #     try:
                            #         current_list = build_list_matching_files_sentinel_sat(str(internet_source.url),
                            #                                                     str(internet_source.include_files_expression),
                            #                                                     internet_source.start_date,
                            #                                                     internet_source.end_date,
                            #                                                     str(internet_source.frequency_id),
                            #                                                     str(internet_source.user_name),
                            #                                                     str(internet_source.password),
                            #                                                     #str(internet_source.files_filter_expression),
                            #                                                       )
                            #
                            #     except:
                            #         logger.error("Error in creating sentinel_sat lists. Continue")
                            #         continue


                            elif internet_type == 'http_coda_eum':
                                # Create the full filename from a 'template' which contains
                                try:
                                    current_list = build_list_matching_files_eum_http(str(internet_source.url),
                                                                                str(internet_source.include_files_expression),
                                                                                internet_source.start_date,
                                                                                internet_source.end_date,
                                                                                str(internet_source.frequency_id),
                                                                                str(internet_source.user_name),
                                                                                str(internet_source.password),
                                                                                  )

                                except:
                                    logger.error("Error in creating http_coda_eum lists. Continue")
                                    continue


                            elif internet_type == 'local':
                                logger.info("This internet source is meant to copy data on local filesystem")
                                try:
                                    current_list = get_list_matching_files_dir_local(str(internet_source.url),str(internet_source.include_files_expression))
                                except:
                                    logger.error("Error in creating date lists. Continue")
                                    continue

                            elif internet_type == 'offline':
                                     logger.info("This internet source is meant to work offline (GoogleDrive)")
                                     current_list = []
                            else:
                                     logger.error("No correct type for this internet source type: %s" %internet_type)
                                     current_list = []
                            logger_spec.debug("Number of files currently available for source %s is %i", internet_id, len(current_list))

                            if len(current_list) > 0:
                                logger_spec.debug("Number of files already copied for trigger %s is %i",internet_id, len(processed_list))
                                listtoprocess = []
                                for current_file in current_list:
                                    if len(processed_list) == 0:
                                        listtoprocess.append(current_file)
                                    else:
                                        #if os.path.basename(current_file) not in processed_list: -> save in .list subdirs as well !!
                                        if current_file not in processed_list:
                                            listtoprocess.append(current_file)

                                logger_spec.debug("Number of files to be copied for trigger %s is %i", internet_id, len(listtoprocess))
                                if listtoprocess != set([]):
                                     # # Debug
                                     # toprint=''
                                     # for elem in listtoprocess:
                                     #    toprint+=elem+','
                                     #    logger_spec.info('List in get_list_matching_files: %s' % toprint)

                                     logger_spec.debug("Loop on the found files.")
                                     if not dry_run:
                                         for filename in list(listtoprocess):
                                             logger_spec.debug("Processing file: "+str(internet_source.url)+os.path.sep+filename)
                                             try:
                                                if internet_type == 'local':
                                                     shutil.copyfile(
                                                         str(internet_source['url']) + os.path.sep + filename,
                                                         es_constants.ingest_dir + os.path.basename(filename))
                                                     result = 0
                                                elif internet_type == 'motu_client':
                                                    result = get_file_from_motu_command(str(filename),
                                                                                        #target_file=internet_source.files_filter_expression,
                                                                                        target_dir=es_constants.ingest_dir,
                                                                                        userpwd=str(usr_pwd))

                                                # elif internet_type == 'sentinel_sat':
                                                #     result = get_file_from_sentinelsat_url(str(filename),
                                                #                                            target_dir=es_constants.ingest_dir)
                                                elif internet_type == 'http_tmpl_vito':
                                                    result = get_file_from_url(str(internet_source.url) + os.path.sep + filename,
                                                                               target_dir=es_constants.ingest_dir,
                                                                               target_file=os.path.basename(filename),
                                                                               userpwd=str(usr_pwd), https_params='Referer: '+str(internet_source.url)+os.path.dirname(filename)+'?mode=tif')

                                                elif internet_type == 'http_tmpl_theia':
                                                    result = get_file_from_url(str(internet_source.url+ os.path.sep + os.path.split(filename)[0]),
                                                                               target_dir=es_constants.ingest_dir,
                                                                               target_file=os.path.basename(os.path.split(filename)[1]),
                                                                               userpwd=str(usr_pwd), https_params=str(internet_source.https_params))

                                                elif internet_type == 'http_coda_eum':
                                                    download_link = 'https://coda.eumetsat.int/odata/v1/Products(\'{0}\')/$value'.format(os.path.split(filename)[0])
                                                    result = get_file_from_url(str(download_link), target_dir=es_constants.ingest_dir, target_file=os.path.basename(filename) + '.zip', userpwd=str(usr_pwd), https_params=str(internet_source.https_params))
                                                else:
                                                    result = get_file_from_url(
                                                        str(internet_source.url) + os.path.sep + filename,
                                                        target_dir=es_constants.ingest_dir,
                                                        target_file=os.path.basename(filename), userpwd=str(usr_pwd), https_params=str(internet_source.https_params))
                                                if not result:
                                                    logger_spec.info("File %s copied.", filename)
                                                    processed_list.append(filename)
                                                else:
                                                    logger_spec.warning("File %s not copied: ", filename)
                                             except:
                                               logger_spec.warning("Problem while copying file: %s.", filename)
                                     else:
                                         logger_spec.info('Dry_run is set: do not get files')

                            if not dry_run:
                                functions.dump_obj_to_pickle(processed_list, processed_list_filename)
                                functions.dump_obj_to_pickle(processed_info, processed_info_filename)

                        sleep(float(user_def_sleep))
                      # Loop over sources
                      except Exception as inst:
                        logger.error("Error while processing source %s. Continue" % internet_source.descriptive_name)
                    sleep(float(user_def_sleep))

    exit(0)

######################################################################################
#   get_list_matching_files_dir_local
#   Purpose: return the list of matching files from the local filesystem ( ONLY used in test/development)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: local_dir: local directory (might incl. sub_dirs)
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#   Output: list of matched files

def get_list_matching_files_dir_local(local_dir, full_regex):

    # Local implementation (filesystem)
    list_matches=[]
    level = 1
    max_level=len(full_regex.split('/'))
    toprint=''
    get_list_matching_files_subdir_local(list_matches, local_dir, full_regex, level, max_level,'')
    for elem in list_matches:
        toprint+=elem+','
    logger.info(toprint)
    return list_matches

######################################################################################
#   get_list_matching_files_subdir_local
#   Purpose: return the list of matching files, or iterate the search ( ONLY used in test/development)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: list_matches: list of matching files, find so far
#           local_dir: local directory
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           level: position in the full_regex tree (increasing from 1 ON .. )
#           sub_dir: current subdir searched on the site (appended to remote_url)
#
def get_list_matching_files_subdir_local(list, local_dir, regex, level, max_level, sub_dir):

    # split the regex
    tokens=regex.split(os.sep)
    regex_my_level=''
    # regex for this level
    regex_my_level+=tokens[level-1]

    my_list = os.listdir(local_dir)
    for element in my_list:
        if re.match(regex_my_level,element) is not None:
            # Is it already the file ?
            if max_level == level:
                list.append(sub_dir+element)
            else:
                # Enter the subdir
                new_level=level+1
                new_sub_dir=sub_dir+element+os.sep
                get_list_matching_files_subdir_local(list, local_dir+os.sep+element, regex, new_level, max_level, new_sub_dir)

    return 0
