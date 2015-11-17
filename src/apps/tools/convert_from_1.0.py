__author__ = 'analyst'
#
#	purpose: Run the script to convert a list of 1.0 files to 2.0
#	author:  M.Clerici
#	date:	 05.11.2015
#   descr:	 takes a list of input files, and convert from 1.0 format to 2.0
#
#	history: 1.0
#

from apps.acquisition import ingestion
from glob import *
from lib.python import es_logging as log
import os
logger = log.my_logger(__name__)

def ingest_from_vers_1_vgt_dmp(input_file,dry_run=False):

    in_date = os.path.basename(input_file).split('_')[0]

    product_def = {'productcode': 'vgt-dmp',
                   'subproductcode': 'dmp',
                   'version': 'sv-v1',
                   'type': 'Ingest'}

    product_in_info= {'scale_factor': 0.01,
                      'scale_offset': 0.0,
                      'no_data': -32768,
                      'mask_min': None,
                      'mask_max': None,
                      'data_type_id': 'Ingest'}

    target_mapset= 'SPOTV-Africa-1km'
    ingestion.ingest_file_vers_1_0(input_file, in_date, product_def, target_mapset, logger, product_in_info, echo_query=False)
    return 0

def ingest_from_vers_1_lsasaf_et(input_file,dry_run=False):


    in_date = os.path.basename(input_file).split('_')[0]

    product_def = {'productcode': 'lsasaf-et',
                   'subproductcode': 'et',
                   'version': 'undefined',
                   'type': 'Ingest'}

    product_in_info= {'scale_factor': 0.0001,
                      'scale_offset': 0.0,
                      'no_data': -1,
                      'mask_min': None,
                      'mask_max': None,
                      'data_type_id': 'Ingest'}

    target_mapset= 'MSG-satellite-3km'
    ingest_file_vers_1_0(input_file, in_date, product_def, target_mapset, logger, product_in_info, echo_query=False)
    return 0

if __name__=='__main__':

    input_dir = '/data/from_1_0/vgt-dmp/'
    files = glob(input_dir+'*')
    for infile in files:
        result = ingest_from_vers_1_vgt_dmp(infile,dry_run=False)