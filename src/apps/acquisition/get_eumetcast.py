#!/usr/bin/python

#
#	purpose: Define the get_eumetcast service
#	author:  M.Clerici
#	date:	 19.02.2014
#   descr:	 Reads the definition from eStation DB and execute the copy to local disk
#	history: 1.0

#import os, sys, re, signal, commands, time, datetime
#from time import sleep
#from lxml import etree
#import pickle


from config.es2 import *

logger = log.my_logger(__name__)

# Defined in lib.python.es_constants.py
#eumetcast_files_dir = '/home/esuser/my_eumetcast_dir/'
#ingest_server_in_dir = '/home/esuser/my_data_ingest_dir/'
input_dir = eumetcast_files_dir
output_dir = ingest_server_in_dir
sleep = poll_frequency
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
    curentlst = []
    for entry in lst:
        if re.search(pattern, os.path.basename(entry)):
            curentlst.append(entry)
    return curentlst


processed_list = []
processlist = get_eumetcast_processed_list


def signal_handler(signal, frame):
    process_files = open(processlist, 'wb')
    pickle.dump(processed_list, process_files)
    process_file.close()
    print 'Exit ' + sys.argv[0]
    logger.info("Stopping the service.")
    sys.exit(0)


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

if not os.path.exists(processed_list_dir):
    os.mkdir(processed_list_dir)

logger.debug("Loading the processed file list.")
if os.path.exists(processlist):
    try:
        process_file = open(processlist, 'r')
        processed_list = pickle.load(process_file)
        logger.debug("Processed file list loaded.")
    except:
        logger.warning("Processed file can't be loaded, the file will be removed.")
        os.remove(processlist)
else:
    # Create an empty file in the tmp dir
    open(processlist, 'a').close()

    
while 1:
    try:
        time_sleep = sleep
        logger.debug("Sleep time set to : %s.", time_sleep)
    except:
        logger.warning("Sleep time not defined. Setting to default=1min. Continue.")
        time_sleep = 60

    try:
        logger.debug("Reading active EUMETCAST data sources from database")
        eumetcast_sources_list = querydb.get_eumetcast_sources(echo=echo_query)
        for eumetcast_source in eumetcast_sources_list:
            logger.debug("Create current list of file to process for trigger %s.", eumetcast_source.eumetcast_id)
            current_list = find_files(input_dir, eumetcast_source.filter_expression_jrc)
            myprocesslst = match_curlst(processed_list, eumetcast_source.filter_expression_jrc)
            listtoprocess = []
            listtoprocess = set(current_list).symmetric_difference(set(myprocesslst))
            if listtoprocess != set([]):
                logger.debug("Loop on the found files.")
                for filename in list(listtoprocess):
                    if os.path.isfile(os.path.join(input_dir, filename)):
                        if os.stat(os.path.join(input_dir, filename)).st_mtime < int(time.time()):
                            logger.debug("Processing file: "+os.path.basename(filename))
                            if commands.getstatusoutput("cp " + filename + " " + output_dir + '/' + os.path.basename(filename))[0] == 0:
                                logger.info("File %s copied.", filename)
                                processed_list.append(filename)
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

        process_file = open(processlist, 'wb')
        pickle.dump(processed_list, process_file)
        process_file.close()
        sleep(float(time_sleep))
    except Exception, e:
        logger.fatal(str(e))
        exit(1)
exit(0)


