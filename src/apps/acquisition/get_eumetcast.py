#!/usr/bin/python

#
#	purpose: Define the get_eumetcast service
#	author:  M.Clerici & Jurriaan van 't Klooster
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0
#   Arguments: dry_run -> if 1, read tables and report activity ONLY
#

# Import standard modules
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import signal
import subprocess
import time
import datetime
import os
import re
import sys

# Import eStation2 modules
from lib.python import es_logging as log
from config import es_constants

from database import querydb

from lib.python import mapset
from lib.python import functions
from lib.python import metadata
from apps.acquisition.get_internet import *

logger = log.my_logger('apps.acquisition.get_eumetcast')

# Defined in lib.python.es_constants.py
input_dir = es_constants.eumetcast_files_dir
output_dir = es_constants.get_eumetcast_output_dir
user_def_sleep = es_constants.get_eumetcast_sleep_time_sec

# echo_query = False

def find_files(directory, pattern):
    lst = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if re.search(pattern, basename):
                fn = os.path.join(root, basename)
                lst.append(fn)
    return lst


def match_curlst(lst, pattern):
    currentlst = []
    for entry in lst:
        if re.search(pattern, os.path.basename(entry)):
            currentlst.append(entry)
    return currentlst


def get_eumetcast_info(eumetcast_id):

    filename = es_constants.get_eumetcast_processed_list_prefix+str(eumetcast_id)+'.info'
    info = functions.load_obj_from_pickle(filename)
    return info

# Get the MESA_JRC_.tif disseminated through EUMETCast
def get_archives_eumetcast_ftp():

    # Ad-hoc definitions (to be copied to settings file)
    source_id = 'MESA:JRC:Archives'
    filter_expression_mesa_jrc = 'MESA_JRC_.*.tif'

    # Get Access credentials
    ftp_eumetcast_url = es_constants.es2globals['ftp_eumetcast_url']
    ftp_eumetcast_userpwd =  es_constants.es2globals['ftp_eumetcast_userpwd']

    # Define a file_handler logger 'source-specific' (for GUI)
    logger_spec = log.my_logger('apps.get_archives_eumetcast')
    logger.info("Retrieving MESA_JRC files from PC1.")

    if sys.platform == 'win32':
        source_id=source_id.replace(':','_') #Pierluigi
    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix+str(source_id)+'.list'
    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix+str(source_id)+'.info'

    # Create objects for list and info
    processed_list = []
    processed_info = {'length_proc_list': 0,
                      'time_latest_exec': datetime.datetime.now(),
                      'time_latest_copy': datetime.datetime.now()}

    logger.debug("Loading the processed file list for source %s ", source_id)

    # Restore/Create List
    processed_list=functions.restore_obj_from_pickle(processed_list, processed_list_filename)
    # Restore/Create Info
    processed_info=functions.restore_obj_from_pickle(processed_info, processed_info_filename)
    # Update processing time (in case it is restored)
    processed_info['time_latest_exec']=datetime.datetime.now()

    logger.debug("Create current list of file to process for trigger %s.", source_id)
    try:
        current_list = get_list_matching_files(ftp_eumetcast_url, ftp_eumetcast_userpwd, filter_expression_mesa_jrc, 'ftp', my_logger=logger_spec)
    except:
        logger.error("Cannot connect to the PC1 via ftp. Wait 1 minute")
        current_list = []
        time.sleep(60)

    logger_spec.info("Number of files currently on PC1 for trigger %s is %i", source_id, len(current_list))

    if len(current_list) > 0:

        #logger.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
        logger_spec.debug("Number of files already copied for trigger %s is %i", source_id, len(processed_list))
        listtoprocess = []
        listtoprocess = set(current_list) - set(processed_list)
        #logger.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
        logger_spec.info("Number of files to be copied for trigger %s is %i", source_id, len(listtoprocess))
        if listtoprocess != set([]):
            logger_spec.debug("Loop on the found files.")
            for filename in list(listtoprocess):
                 try:
                    result = get_file_from_url(str(ftp_eumetcast_url)+os.path.sep+filename, target_file=os.path.basename(filename), target_dir=es_constants.ingest_dir, userpwd=str(ftp_eumetcast_userpwd))
                    if not result:
                        logger_spec.info("File %s copied.", filename)
                        processed_list.append(filename)
                    else:
                        logger_spec.warning("File %s not copied: ", filename)
                 except:
                   logger_spec.warning("Problem while copying file: %s.", filename)
        else:
            logger.debug("Nothing to process - go to next trigger.")
            pass

    for infile in processed_list:
           if not infile in current_list:
               processed_list.remove(infile)

    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
    functions.dump_obj_to_pickle(processed_info, processed_info_filename)

def get_archives_eumetcast():

    input_dir='/eumetcast_test/'

    # Ad-hoc definitions (to be copied to settings file)
    source_id = 'MESA:JRC:Archives'
    filter_expression_mesa_jrc = 'MESA_JRC_.*.tif'

    # Define a file_handler logger 'source-specific' (for GUI)
    logger_spec = log.my_logger('apps.get_archives_eumetcast')
    logger.info("Retrieving MESA_JRC files from PC1.")

    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix+str(source_id)+'.list'
    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix+str(source_id)+'.info'

    # Create objects for list and info
    processed_list = []
    processed_info = {'length_proc_list': 0,
                      'time_latest_exec': datetime.datetime.now(),
                      'time_latest_copy': datetime.datetime.now()}

    logger.warning("Input DIR for get_archives_eumetcast is defined as: *** %s ***", input_dir)
    logger.debug("Loading the processed file list for source %s ", source_id)

    # Restore/Create List
    processed_list=functions.restore_obj_from_pickle(processed_list, processed_list_filename)
    # Restore/Create Info
    processed_info=functions.restore_obj_from_pickle(processed_info, processed_info_filename)
    # Update processing time (in case it is restored)
    processed_info['time_latest_exec']=datetime.datetime.now()

    logger.debug("Create current list of file to process for trigger %s.", source_id)
    try:
        current_list = find_files(input_dir, filter_expression_mesa_jrc)
    except:
        logger.error("Cannot connect to the PC1 via ftp. Wait 1 minute")
        current_list = []
        time.sleep(60)

    logger_spec.info("Number of files currently on PC1 for trigger %s is %i", source_id, len(current_list))
    if len(current_list) > 0:

        #logger.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
        logger_spec.debug("Number of files already copied for trigger %s is %i", source_id, len(processed_list))
        listtoprocess = []
        listtoprocess = set(current_list) - set(processed_list)
        #logger.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
        logger_spec.info("Number of files to be copied for trigger %s is %i", source_id, len(listtoprocess))
        if listtoprocess != set([]):
            logger_spec.debug("Loop on the found files.")
            for filename in list(listtoprocess):
                 try:
                    if subprocess.getstatusoutput("cp " + filename + " " + output_dir + os.sep + os.path.basename(filename))[0] == 0:
                        logger_spec.info("File %s copied.", filename)
                        processed_list.append(filename)
                        # Update processing info
                        processed_info['time_latest_copy']=datetime.datetime.now()
                        processed_info['length_proc_list']=len(processed_list)
                    else:
                        logger_spec.warning("Problem while copying file: %s.", filename)
                 except:
                   logger_spec.warning("Problem while copying file: %s.", filename)
        else:
            logger.debug("Nothing to process - go to next trigger.")
            pass

    for infile in processed_list:
           if not infile in current_list:
               processed_list.remove(infile)

    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
    functions.dump_obj_to_pickle(processed_info, processed_info_filename)


#   It will ensure backup of the ongoing list
def signal_handler(signal, frame):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    logger.info("Len of proc list is %i" % len(processed_list))

    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
    functions.dump_obj_to_pickle(processed_info, processed_info_filename)

    print ('Exit ' + sys.argv[0])
    logger.info("Stopping the service.")
    sys.exit(0)

def loop_eumetcast_ftp(dry_run=False):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)

    logger.info("Starting retrieving EUMETCast data.")

    ftp_eumetcast_url = es_constants.es2globals['ftp_eumetcast_url']
    ftp_eumetcast_userpwd =  es_constants.es2globals['ftp_eumetcast_userpwd']

    while True:

        logger.debug("Check if the Ingest Server input directory : %s exists.", output_dir)
        if not os.path.exists(output_dir):
            logger.fatal("The Ingest Server input directory : %s doesn't exists.", output_dir)
            exit(1)

        if not os.path.exists(es_constants.base_tmp_dir):
            os.mkdir(es_constants.base_tmp_dir)

        if not os.path.exists(es_constants.processed_list_base_dir):
            os.mkdir(es_constants.processed_list_base_dir)

        if not os.path.exists(es_constants.processed_list_eum_dir):
            os.mkdir(es_constants.processed_list_eum_dir)

        while 1:
            try:
                time_sleep = user_def_sleep
                logger.debug("Sleep time set to : %s.", time_sleep)
            except:
                logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
                time_sleep = 60

            # try:
            logger.debug("Reading active EUMETCAST data sources from database")
            eumetcast_sources_list = querydb.get_eumetcast_sources()
            logger.debug("N. %i active EUMETCAST data sources found", len(eumetcast_sources_list))

            # Get the EUMETCast MESA_JRC files
            try:
                get_archives_eumetcast_ftp()
            except:
                logger.error("Error in executing get_archives_eumetcast_ftp. Continue")

            # Loop over active triggers
            for eumetcast_source in eumetcast_sources_list:

                # Define a file_handler logger 'source-specific' (for GUI)
                logger_spec = log.my_logger('apps.get_eumetcast.'+eumetcast_source.eumetcast_id)
                logger.info("Processing eumetcast source  %s.", eumetcast_source.eumetcast_id)

                if sys.platform == 'win32': #Pierluigi
                    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix + str(
                        eumetcast_source.eumetcast_id).replace(':','_') + '.list'
                    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix + str(
                        eumetcast_source.eumetcast_id).replace(':','_') + '.info'
                else:
                    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.list'
                    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.info'

                # Create objects for list and info
                processed_list = []
                processed_info = {'length_proc_list': 0,
                                  'time_latest_exec': datetime.datetime.now(),
                                  'time_latest_copy': datetime.datetime.now()}

                logger.debug("Loading the processed file list for source %s ", eumetcast_source.eumetcast_id)

                # Restore/Create List
                processed_list=functions.restore_obj_from_pickle(processed_list, processed_list_filename)
                # Restore/Create Info
                processed_info=functions.restore_obj_from_pickle(processed_info, processed_info_filename)
                # Update processing time (in case it is restored)
                processed_info['time_latest_exec']=datetime.datetime.now()

                logger.debug("Create current list of file to process for trigger %s.", eumetcast_source.eumetcast_id)
                try:
                    current_list = get_list_matching_files(ftp_eumetcast_url, ftp_eumetcast_userpwd, eumetcast_source.filter_expression_jrc, 'ftp', my_logger=logger_spec)
                except:
                    logger.error("Cannot connect to the PC1 via ftp. Wait 1 minute")
                    current_list = []
                    time.sleep(60)

                if len(current_list) > 0:
                    # See ES2-204
                    logger_spec.debug("Number of files currently on PC1 for trigger %s is %i", eumetcast_source.eumetcast_id, len(current_list))

                    #logger.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
                    logger_spec.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
                    listtoprocess = []
                    listtoprocess = set(current_list) - set(processed_list)
                    #logger.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
                    logger_spec.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
                    if listtoprocess != set([]):
                        logger_spec.debug("Loop on the found files.")
                        for filename in list(listtoprocess):
                             try:
                                result = get_file_from_url(str(ftp_eumetcast_url)+os.path.sep+filename, target_file=os.path.basename(filename), target_dir=es_constants.ingest_dir, userpwd=str(ftp_eumetcast_userpwd))
                                if not result:
                                    logger_spec.info("File %s copied.", filename)
                                    processed_list.append(filename)
                                else:
                                    logger_spec.warning("File %s not copied: ", filename)
                             except:
                               logger_spec.warning("Problem while copying file: %s.", filename)
                    else:
                        logger.debug("Nothing to process - go to next trigger.")
                        pass

                for infile in processed_list:
                       if not infile in current_list:
                           processed_list.remove(infile)

                if not dry_run:
                    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
                    functions.dump_obj_to_pickle(processed_info, processed_info_filename)

            logger.info("End of Get EUMETCast loop. Sleep")
            time.sleep(float(time_sleep))

    exit(0)

def loop_eumetcast(dry_run=False):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)

    logger.info("Starting retrieving EUMETCast data.")

    while True:
        logger.debug("Check if the EUMETCast input directory : %s exists.", input_dir)
        if not os.path.exists(input_dir):
            logger.error("The EUMETCast input directory : %s is not yet mounted.", input_dir)

        logger.debug("Check if the Ingest Server input directory : %s exists.", output_dir)
        if not os.path.exists(output_dir):
            logger.fatal("The Ingest Server input directory : %s doesn't exists.", output_dir)
            exit(1)

        if not os.path.exists(es_constants.base_tmp_dir):
            os.mkdir(es_constants.base_tmp_dir)

        if not os.path.exists(es_constants.processed_list_base_dir):
            os.mkdir(es_constants.processed_list_base_dir)

        if not os.path.exists(es_constants.processed_list_eum_dir):
            os.mkdir(es_constants.processed_list_eum_dir)

        while 1:
            try:
                time_sleep = user_def_sleep
                logger.debug("Sleep time set to : %s.", time_sleep)
            except:
                logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
                time_sleep = 60

            # try:
            logger.debug("Reading active EUMETCAST data sources from database")
            eumetcast_sources_list = querydb.get_eumetcast_sources()
            logger.debug("N. %i active EUMETCAST data sources found", len(eumetcast_sources_list))

            # Get the EUMETCast MESA_JRC files
            try:
                get_archives_eumetcast()
            except:
                logger.error("Error in executing get_archives_eumetcast. Continue")

            # Loop over active triggers
            for eumetcast_source in eumetcast_sources_list:

                # Define a file_handler logger 'source-specific' (for GUI)
                logger_spec = log.my_logger('apps.get_eumetcast.'+eumetcast_source.eumetcast_id)
                logger.info("Processing eumetcast source  %s.", eumetcast_source.eumetcast_id)

                if sys.platform == 'win32': # Pierluigi
                    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix + str(
                        eumetcast_source.eumetcast_id).replace(':','_') + '.list'
                    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix + str(
                        eumetcast_source.eumetcast_id).replace(':','_') + '.info'

                else:
                    processed_list_filename = es_constants.get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.list'
                    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.info'

                # Create objects for list and info
                processed_list = []
                processed_info = {'length_proc_list': 0,
                                  'time_latest_exec': datetime.datetime.now(),
                                  'time_latest_copy': datetime.datetime.now()}

                logger.debug("Loading the processed file list for source %s ", eumetcast_source.eumetcast_id)

                # Restore/Create List
                processed_list=functions.restore_obj_from_pickle(processed_list, processed_list_filename)
                # Restore/Create Info
                processed_info=functions.restore_obj_from_pickle(processed_info, processed_info_filename)
                # Update processing time (in case it is restored)
                processed_info['time_latest_exec']=datetime.datetime.now()

                logger.debug("Create current list of file to process for trigger %s.", eumetcast_source.eumetcast_id)
                current_list = find_files(input_dir, eumetcast_source.filter_expression_jrc)
                #logger.debug("Number of files currently on PC1 for trigger %s is %i", eumetcast_source.eumetcast_id, len(current_list))
                logger_spec.info("Number of files currently on PC1 for trigger %s is %i", eumetcast_source.eumetcast_id, len(current_list))
                if len(current_list) > 0:

                    #logger.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
                    logger_spec.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
                    listtoprocess = []
                    listtoprocess = set(current_list) - set(processed_list)
                    #logger.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
                    logger_spec.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
                    if listtoprocess != set([]):
                        logger_spec.debug("Loop on the found files.")
                        for filename in list(listtoprocess):
                            if os.path.isfile(os.path.join(input_dir, filename)):
                                if os.stat(os.path.join(input_dir, filename)).st_mtime < int(time.time()):
                                    logger_spec.debug("Processing file: "+os.path.basename(filename))
                                    if not dry_run:
                                        if subprocess.getstatusoutput("cp " + filename + " " + output_dir + os.sep + os.path.basename(filename))[0] == 0:
                                            logger_spec.info("File %s copied.", filename)
                                            processed_list.append(filename)
                                            # Update processing info
                                            processed_info['time_latest_copy']=datetime.datetime.now()
                                            processed_info['length_proc_list']=len(processed_list)
                                        else:
                                            logger_spec.warning("Problem while copying file: %s.", filename)
                                    else:
                                        logger_spec.info('Dry_run is set: do not get files')
                            else:
                                logger_spec.error("File %s removed by the system before being processed.", filename)
                    else:
                        logger.debug("Nothing to process - go to next trigger.")
                        pass

                for infile in processed_list:
                       if not os.path.exists(infile):
                           processed_list.remove(infile)

                if not dry_run:
                    functions.dump_obj_to_pickle(processed_list, processed_list_filename)
                    functions.dump_obj_to_pickle(processed_info, processed_info_filename)

            logger.info("End of Get EUMETCast loop. Sleep")
            time.sleep(float(time_sleep))

    exit(0)


