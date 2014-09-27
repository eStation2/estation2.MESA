#
#	purpose: Define the get_internet service
#	author:  M.Clerici
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0

# Import local definitions
import locals

# Import standard modules
import pycurl
import signal
from StringIO import StringIO
import cStringIO
import tempfile
import os
#import unittest
import glob
import re
import pickle
from time import sleep

# Import eStation2 modules
from lib.python import es_logging as log
from config.es_constants import *
import database.querydb as querydb
from lib.python.functions import *

logger = log.my_logger(__name__)

#output_dir = ingest_server_in_dir

#   General definitions
c = pycurl.Curl()
buffer = StringIO()
tmpdir = tempfile.mkdtemp(prefix=__name__, dir=locals.es2globals['temp_dir'])
echo_query = False
user_def_sleep = poll_frequency

#   ---------------------------------------------------------------------------
#   Functions
#   ---------------------------------------------------------------------------

######################################################################################
#   signal_handler
#   Purpose: properly terminate the service, in case of interruption (copied from old get_eumetcast)
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: defaults for signa_handler

def signal_handler(signal, frame):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    logger.info("Len of proc list is %i" % len(processed_list))

    dump_obj_to_pickle(processed_list, processed_list_filename)
    dump_obj_to_pickle(processed_info, processed_info_filename)

    print 'Exit ' + sys.argv[0]
    logger.info("Stopping the service.")
    sys.exit(0)

######################################################################################
#   get_list_current_subdirs_ftp
#   Purpose: read a remote ftp directory and return contents
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: output_dir, or list of dirs
#   Output: list of dirs
#

def get_list_current_subdirs_ftp(remote_url, usr_pwd):

    d = pycurl.Curl()
    response = cStringIO.StringIO()
    d.setopt(pycurl.URL, remote_url)
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
#   get_list_matching_files_dir_ftp
#   Purpose: get the files matching a full_regex on a remote ftp
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: remote_url: ftp address (might incl. sub_dirs)
#           usr_pwd: credentials (username:password)
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#   Output: list of matched files
#

def get_list_matching_files_dir_ftp(remote_url, usr_pwd, full_regex):

    # Check the arguments (remote_url must end with os.sep and full_regex should begin with os.sep)
    remote_url=ensure_sep_present(remote_url,'end')
    full_regex=ensure_sep_present(full_regex,'begin')

    # Get list from a remote ftp
    list_matches=[]
    init_level = 1
    get_list_matching_files_subdir_ftp(list_matches, remote_url, usr_pwd, full_regex, init_level, '')

    # Debug
    toprint=''
    for elem in list_matches:
        toprint+=elem+','
    logger.info(toprint)

    return list_matches

######################################################################################
#   get_list_matching_files_subdir_ftp
#   Purpose: return the list of matching files, or iterate the search
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: list_matches: list of matching files, find so far
#           remote_url: ftp address (might incl. sub_dirs)
#           usr_pwd: credentials (username:password)
#           full_regex: re including subdirs (e.g. 'Collection51/TIFF/Win1[01]/201[1-3]/MCD45monthly.A20.*burndate.tif.gz'
#           level: position in the full_regex tree (increasing from 1 ON .. )
#           sub_dir: current subdir searched on the site (appended to remote_url)
#
#   Output: list of matched files (incremented)
#   TODO-M.C.: check if the '/' has to be replaced by os.sep (?)

def get_list_matching_files_subdir_ftp(list, remote_url, usr_pwd, full_regex, level, sub_dir):

    # split the regex
    tokens=full_regex.split('/')
    # regex for this level
    regex_my_level=tokens[level]
    max_level= len(re.findall("/",full_regex))

    my_list = get_list_current_subdirs_ftp(remote_url, usr_pwd)
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
                get_list_matching_files_subdir_ftp(list, new_remote_url, usr_pwd, full_regex, new_level, new_sub_dir)
    return 0

######################################################################################
#   get_list_matching_files_dir_local
#   Purpose: return the list of matching files from the local filesystem
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

######################################################################################
#   get_list_matching_files_subdir_local
#   Purpose: return the list of matching files, or iterate the search
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

######################################################################################
#   get_file_from_url
#   Purpose: download and save locally a file
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: remote_url_file: full file path
#           target_file: target file name (by default 'test_output_file')
#           target_dir: target directory (by default a tmp dir is created)
#   Output: full pathname is returned (or positive number for error)
def get_file_from_url(remote_url_file, target_file=None, target_dir=None, userpwd=''):

    if target_dir is None:
        tmpdir = tempfile.mkdtemp(prefix=__name__, dir=locals.es2globals['temp_dir'])
    else:
        tmpdir = target_dir

    if target_file is None:
        target_file='test_output_file'

    target_fullpath=tmpdir+os.sep+target_file

    outputfile=open(target_fullpath, 'wb')
    logger.debug('Output File: '+target_fullpath)

    c.setopt(c.URL,remote_url_file)
    c.setopt(c.WRITEFUNCTION,outputfile.write)
    if userpwd is not '':
        c.setopt(c.USERPWD,userpwd)
    c.perform()
    outputfile.close()

    return target_fullpath

#   Target dir is created as 'tmpdir' if not passed
#   Full pathname is returned (or positive number for error)
#   TODO-M.C.: return in a python object rather than writing in a file

def get_dir_contents_from_url(remote_url_dir, target_file=None, target_dir=None, userpwd=''):

    if target_dir is None:
        tmpdir = tempfile.mkdtemp(prefix=__name__, dir=locals.es2globals['temp_dir'])
    else:
        tmpdir = target_dir

    if target_file is None:
        target_file='test_output_file'

    target_fullpath=tmpdir+os.sep+target_file

    outputfile=open(target_fullpath, 'wb')
    logger.debug('Output File: '+target_fullpath)

    c.setopt(c.URL,remote_url_dir)
    c.setopt(c.WRITEFUNCTION,outputfile.write)
    if userpwd is not '':
        c.setopt(c.USERPWD,userpwd)
    c.perform()
    outputfile.close()

    return target_fullpath

######################################################################################
#   drive_get_internet
#   Purpose: drive the get_internet as a service
#   Author: Marco Clerici, JRC, European Commission
#   Date: 2014/09/01
#   Inputs: none

def drive_get_internet():

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)

    logger.info("Starting retrieving data from INTERNET.")

    output_dir = ingest_server_in_dir
    logger.debug("Check if the Ingest Server output directory : %s exists.", output_dir)
    if not os.path.exists(output_dir):
        logger.fatal("The Ingest Server output directory : %s doesn't exists.", output_dir)
        exit(1)

    if not os.path.exists(processed_list_int_dir):
        os.mkdir(processed_list_int_dir)

    while 1:

        try:
            time_sleep = user_def_sleep
            logger.debug("Sleep time set to : %s.", time_sleep)
        except:
            logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
            time_sleep = 60

#        try:
        logger.debug("Reading active INTERNET data sources from database")
        internet_sources_list = querydb.get_active_internet_sources(echo=echo_query)

        # Loop over active triggers
        for internet_source in internet_sources_list:
            logger.debug("Processing internet source  %s.", internet_source.descriptive_name)

            processed_list_filename = get_internet_processed_list_prefix+str(internet_source.internet_id)+'.list'
            processed_info_filename = get_internet_processed_list_prefix+str(internet_source.internet_id)+'.info'

            # Create objects for list and info
            processed_list = []
            processed_info = {'lenght_proc_list': 0,
                              'time_latest_exec': datetime.datetime.now(),
                              'time_latest_copy': datetime.datetime.now()}
            # Restore/Create List
            processed_list=restore_obj_from_pickle(processed_list, processed_list_filename)
            # Restore/Create Info
            processed_info=restore_obj_from_pickle(processed_info, processed_info_filename)
            # Update processing time (in case it is restored)
            processed_info['time_latest_exec']=datetime.datetime.now()

            logger.debug("Create current list of file to process for source %s.", internet_source.internet_id)
            #if isinstance(internet_source.user_name,str) and isinstance(internet_source.password,str):
            usr_pwd = str(internet_source.user_name)+':'+internet_source.password
            #else:
            #    usr_pwd =''

            logger.debug("              Url is %s.", internet_source.url)
            logger.debug("              usr/pwd is %s.", usr_pwd)
            logger.debug("              regex   is %s.", internet_source.include_files_expression)

            current_list = get_list_matching_files_dir_ftp(str(internet_source.url), str(usr_pwd), str(internet_source.include_files_expression))

            logger.debug("Number of files currently available for source %s is %i", internet_source.internet_id, len(current_list))
            if len(current_list) > 0:
                logger.debug("Number of files already copied for trigger %s is %i", internet_source.internet_id, len(processed_list))
                listtoprocess = []
                for current_file in current_list:
                    if len(processed_list) == 0:
                        listtoprocess.append(current_file)
                    else:
                        if os.path.basename(current_file) not in processed_list:
                            listtoprocess.append(current_file)

                logger.debug("Number of files to be copied for trigger %s is %i", internet_source.internet_id, len(listtoprocess))
                if listtoprocess != set([]):
                     logger.debug("Loop on the found files.")
                     for filename in list(listtoprocess):
                         logger.debug("Processing file: "+os.path.basename(filename))
                         #try:
                         target_file=filename
                         get_file_from_url(str(internet_source.url)+'/'+target_file, target_file=os.path.basename(target_file), target_dir=ingest_server_in_dir, userpwd=str(usr_pwd))
                         logger.info("File %s copied.", filename)
                         processed_list.append(os.path.basename(filename))
                         #except:
                         #   logger.warning("Problem while copying file: %s.", filename)

            dump_obj_to_pickle(processed_list, processed_list_filename)
            dump_obj_to_pickle(processed_info, processed_info_filename)

            sleep(float(user_def_sleep))
#        except Exception, e:
#            logger.fatal(str(e))
#            exit(1)
    exit(0)

