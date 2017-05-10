__author__ = 'analyst'
#
#	purpose: Run the script to create an archive from a request
#	author:  M.Clerici
#	date:	 28.08.2015
#   descr:	 It processes a request, and generates a .bsx (auto-installing archive)
#   Usage:   python create_archive_from_request.py
#	history: 1.0
#
import os
import argparse
import glob

from apps.productmanagement import requests
from lib.python import es_logging as log

logger = log.my_logger(__name__)

if __name__=='__main__':

    debug = 0
    # req_file = '/home/adminuser/fewsnet-rfe_2.0_all_enabled_mapsets_2016-05-02_1156.req'
    req_file = None
    req_directory = '/data/processing/exchange/requests/20170414_Ref_Station_JRC/'
    debug_req_file = None

    if not debug:
    # Parse the input
    #     parser = argparse.ArgumentParser(description='Create bsx archive from request')
    #     parser.add_argument('req_file', type=str, help='Name of the request file/dir to process')

        # Commented FTTB: to be implemented through a GUI
        # parser.add_argument('--file', type=str, help='The passed arg is full filename')
        # parser.add_argument('--directory', type=str, help='The passed arg is directory name')
        #
        # args = parser.parse_args()
        # req_file= args.req_file

        # Commented FTTB: to be implemented through a GUI
        if req_file is not None:
            logger.info('Working on a .req file: %s' % req_file)
            if os.path.isfile(req_file):
                requests.create_archive_from_request(req_file)
            else:
                logger.error('Req. file does not exist: %s' % req_file)

        # Commented FTTB: to be implemented through a GUI
        if req_directory is not None:
            logger.info('Working on a directory: %s' % req_directory)
            if os.path.isdir(req_directory):
                req_files = glob.glob(req_directory+'*.req')
                for my_req in req_files:
                    logger.info('Working on file: %s' % my_req)
                    requests.create_archive_from_request(my_req)
            else:
                logger.error('Req. file does not exist: %s' % req_file)
            # Get list of all req. in the dir
    else:
    # For debugging
        req_file= debug_req_file
        if os.path.isfile(req_file):
            requests.create_archive_from_request(req_file)
        else:
            logger.error('Req. file does not exist: %s' % req_file)