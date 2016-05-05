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

from apps.productmanagement import requests
from lib.python import es_logging as log

logger = log.my_logger(__name__)


if __name__=='__main__':

    # Parse the input
    parser = argparse.ArgumentParser(description='Create bsx archive from request')
    parser.add_argument('req_file', type=str, help='Name of the request file to process')

    args = parser.parse_args()
    req_file= args.req_file
    if os.path.isfile(req_file):
        requests.create_archive_from_request(req_file)
    else:
        logger.error('Req. file does not exist: %s' % req_file)

    # # For debugging
    # req_file= '/home/adminuser/fewsnet-rfe_2.0_FEWSNET-Africa-8km_1monnp_2016-05-02_1153.req'
    # if os.path.isfile(req_file):
    #     requests.create_archive_from_request(req_file)
    # else:
    #     logger.error('Req. file does not exist: %s' % req_file)