#!/usr/bin/python

#
#	purpose: Define the get_eumetcast service
#	author:  M.Clerici & Jurriaan van 't Klooster
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0

# Import local definitions

# Import standard modules
import signal
import commands
from time import sleep

#from lxml import etree

# Import eStation2 modules
from lib.python import es_logging as log
from config.es_constants import *

#import database.querydb as querydb
from database.querydb import *

from lib.python.mapset import *
from lib.python.functions import *
from lib.python.metadata import *
import datetime

logger = log.my_logger(__name__)

# Defined in lib.python.es_constants.py
input_dir = eumetcast_files_dir
output_dir = ingest_server_in_dir
user_def_sleep = poll_frequency

echo_query = False


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

    filename = get_eumetcast_processed_list_prefix+str(eumetcast_id)+'.info'
    info = load_obj_from_pickle(filename)
    return info


#   It will ensure backup of the ongoing list
def signal_handler(signal, frame):

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    logger.info("Len of proc list is %i" % len(processed_list))

    dump_obj_to_pickle(processed_list, processed_list_filename)
    dump_obj_to_pickle(processed_info, processed_info_filename)

    print 'Exit ' + sys.argv[0]
    logger.info("Stopping the service.")
    sys.exit(0)


def drive_eumetcast():

    global processed_list_filename, processed_list
    global processed_info_filename, processed_info

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGILL, signal_handler)

    logger.info("Starting retrieving EUMETCast data.")

    logger.debug("Check if the EUMETCast input directory : %s exists.", input_dir)
    if not os.path.exists(input_dir):
        logger.error("The EUMETCast input directory : %s is not yet mounted.", input_dir)

    logger.debug("Check if the Ingest Server output directory : %s exists.", output_dir)
    if not os.path.exists(output_dir):
        logger.fatal("The Ingest Server output directory : %s doesn't exists.", output_dir)
        # TODO Jurvtk: Create the Ingest Server output directory if it doesn't exist!
        exit(1)

    if not os.path.exists(base_tmp_dir):
        os.mkdir(base_tmp_dir)

    if not os.path.exists(processed_list_base_dir):
        os.mkdir(processed_list_base_dir)

    if not os.path.exists(processed_list_eum_dir):
        os.mkdir(processed_list_eum_dir)

    while 1:
        try:
            time_sleep = user_def_sleep
            logger.debug("Sleep time set to : %s.", time_sleep)
        except:
            logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
            time_sleep = 60

        # try:
        logger.debug("Reading active EUMETCAST data sources from database")
        eumetcast_sources_list = db.get_eumetcast_sources(echo=echo_query)
        logger.debug("N. %i active EUMETCAST data sources found", len(eumetcast_sources_list))

        # Loop over active triggers
        for eumetcast_source in eumetcast_sources_list:

            logger.debug("Processing eumetcast source  %s.", eumetcast_source.eumetcast_id)

            processed_list_filename = get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.list'
            processed_info_filename = get_eumetcast_processed_list_prefix+str(eumetcast_source.eumetcast_id)+'.info'

            # Create objects for list and info
            processed_list = []
            processed_info = {'lenght_proc_list': 0,
                              'time_latest_exec': datetime.datetime.now(),
                              'time_latest_copy': datetime.datetime.now()}

            logger.debug("Loading the processed file list for source %s ", eumetcast_source.eumetcast_id)

            # Restore/Create List
            processed_list=restore_obj_from_pickle(processed_list, processed_list_filename)
            # Restore/Create Info
            processed_info=restore_obj_from_pickle(processed_info, processed_info_filename)
            # Update processing time (in case it is restored)
            processed_info['time_latest_exec']=datetime.datetime.now()

            logger.debug("Create current list of file to process for trigger %s.", eumetcast_source.eumetcast_id)
            current_list = find_files(input_dir, eumetcast_source.filter_expression_jrc)
            logger.debug("Number of files currently on PC1 for trigger %s is %i", eumetcast_source.eumetcast_id, len(current_list))
            if len(current_list) > 0:

                logger.debug("Number of files already copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(processed_list))
                listtoprocess = []
                listtoprocess = set(current_list) - set(processed_list)
                logger.debug("Number of files to be copied for trigger %s is %i", eumetcast_source.eumetcast_id, len(listtoprocess))
                if listtoprocess != set([]):
                    logger.debug("Loop on the found files.")
                    for filename in list(listtoprocess):
                        if os.path.isfile(os.path.join(input_dir, filename)):
                            if os.stat(os.path.join(input_dir, filename)).st_mtime < int(time.time()):
                                logger.debug("Processing file: "+os.path.basename(filename))
                                if commands.getstatusoutput("cp " + filename + " " + output_dir + os.sep + os.path.basename(filename))[0] == 0:
                                    logger.info("File %s copied.", filename)
                                    processed_list.append(filename)
                                    # Update processing info
                                    processed_info['time_latest_copy']=datetime.datetime.now()
                                    processed_info['lenght_proc_list']=len(processed_list)
                                else:
                                    logger.warning("Problem while copying file: %s.", filename)
                        else:
                            logger.error("File %s removed by the system before being processed.", filename)
                else:
                    logger.debug("Nothing to process - go to next trigger.")
                    pass

            for infile in processed_list:
                   if not os.path.exists(infile):
                       processed_list.remove(infile)

            dump_obj_to_pickle(processed_list, processed_list_filename)
            dump_obj_to_pickle(processed_info, processed_info_filename)

        sleep(float(user_def_sleep))

        # except Exception, e:
        #     logger.fatal(str(e))
        #     exit(1)
    exit(0)

