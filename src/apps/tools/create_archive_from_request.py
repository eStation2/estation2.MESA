__author__ = 'clerima'
#
#	purpose: Run the script to create an archive from a request
#	author:  M.Clerici
#	date:	 28.08.2015
#   descr:	 It processes a request, and generates a .bsx (auto-installing archive)
#   Usage:   python create_archive_from_request.py
#	history: 1.0
#
import os
import glob
import shutil

from apps.productmanagement import requests
from lib.python import es_logging as log
from lib.python import functions

logger = log.my_logger(__name__)

def create_archive_from_file(req_file):

    if req_file is not None:
        logger.info('Working on a .req file: %s' % req_file)
        if os.path.isfile(req_file):
            requests.create_archive_from_request(req_file)
        else:
            logger.error('Req. file does not exist: %s' % req_file)
    else:
        logger.error('Req. file must be defined')

def create_archives_from_dir(req_directory):

    # It processes all .req files in a dir, and moves both .req and .bsx (if any) in:
    #   req_directory/Done    -> when ok
    #   req_directory/Faulty  -> in case of errors

    if req_directory is not None:
        logger.info('Working on a directory: %s' % req_directory)
        if os.path.isdir(req_directory):
            req_files = glob.glob(req_directory+'*.req')
            for my_req in req_files:
                logger.info('Working on file: %s' % my_req)
                try:
                    # Create the .bsx files
                    status = requests.create_archive_from_request(my_req)
                    # If ok, set target to Done
                    if status == 0:
                        target_dir ='{}{}{}'.format(req_directory,os.path.sep,'Done')
                    # Also check at least one .bsx has been generated
                    bsx_files=glob.glob(my_req.replace('.req','*.bsx'))
                    if len(bsx_files)==0:
                        target_dir ='{}{}{}'.format(req_directory,os.path.sep,'NothingDone')

                except:
                    logger.error('Error in processing request: %s' % my_req)
                    status=1
                if status:
                    target_dir ='{}{}{}'.format(req_directory,os.path.sep,'Faulty')

                # Move to target dir (Done or Faulty)
                functions.check_output_dir(target_dir)
                files=glob.glob(my_req.replace('.req','*.bsx'))
                shutil.move(my_req,target_dir)
                for my_file in files:
                    shutil.move(my_file,target_dir)

        else:
            logger.error('Req. directory does not exist: %s' % req_directory)
    else:
        logger.error('Req. directory must be defined')

if __name__=='__main__':

    req_directory='/data/processing/exchange/Requests/'

    create_archives_from_dir(req_directory)
#
#     debug = 0
#     req_file = None
#     req_directory = '/data/processing/exchange/requests/20170414_Ref_Station_JRC/'
#     debug_req_file = None
#
#     if not debug:
#     # Parse the input
#     #     parser = argparse.ArgumentParser(description='Create bsx archive from request')
#     #     parser.add_argument('req_file', type=str, help='Name of the request file/dir to process')
#
#         # Commented FTTB: to be implemented through a GUI
#         # parser.add_argument('--file', type=str, help='The passed arg is full filename')
#         # parser.add_argument('--directory', type=str, help='The passed arg is directory name')
#         #
#         # args = parser.parse_args()
#         # req_file= args.req_file
#
#
#         # Commented FTTB: to be implemented through a GUI
#             # Get list of all req. in the dir
#     else:
#     # For debugging
#         req_file= debug_req_file
#         if os.path.isfile(req_file):
#             requests.create_archive_from_request(req_file)
#         else:
#             logger.error('Req. file does not exist: %s' % req_file)
#