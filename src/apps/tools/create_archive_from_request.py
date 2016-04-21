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

    if os.path.isfile(args.req_file):
        requests.create_archive_from_request(args.req_file)
    else:
        logger.error('Req. file does not exist: %s' % args.req_file)