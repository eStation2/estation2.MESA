__author__ = 'analyst'
#
#	purpose: Run the script to create an archive from a request
#	author:  M.Clerici
#	date:	 28.08.2015
#   descr:	 It processes a request, and generates a .bsx (auto-installing archive)
#   Usage:   python create_archive_from_request.py <name_of_request.req>
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

    if not debug:
    # Parse the input
        parser = argparse.ArgumentParser(description='Create bsx archive from request')
        parser.add_argument('req_file', type=str, help='Name of the request file/dir to process')
        parser.add_argument('--file', type=str, help='The passed arg is full filename')
        parser.add_argument('--directory', type=str, help='The passed arg is directory name')

        args = parser.parse_args()
        req_file= args.req_file

        if args.file:
            logger.info('Working on a .req file: %s' % req_file)
            if os.path.isfile(req_file):
                requests.create_archive_from_request(req_file)
            else:
                logger.error('Req. file does not exist: %s' % req_file)

        if args.directory:
            logger.info('Working on a directory: %s' % req_file)
            if os.path.isdir(req_file):
                req_files = glob.glob(req_file+'*.req')
                for my_req in req_files:
                    requests.create_archive_from_request(my_req)
            else:
                logger.error('Req. file does not exist: %s' % req_file)
            # Get list of all req. in the dir
    # else:
    # # # For debugging
    #     req_file= '/data/User_Requests/Yoseph-ICPAC/missing_data/vgt-ndvi_sv2-pv2.1_all_enabled_mapsets_2016-05-26_1334.req'
    #     if os.path.isfile(req_file):
    #         requests.create_archive_from_request(req_file)
    #     else:
    #         logger.error('Req. file does not exist: %s' % req_file)