# -*- coding: utf-8 -*-
#
# purpose: handle request for completing datasets
# author:  MC, JvK
# date:  27.08.2015

# from config import es_constants
# from lib.python import metadata
# from .exceptions import (NoProductFound, MissingMapset)
# from .datasets import Dataset
# from .mapsets import Mapset

import os
import glob
import tarfile
import shutil
import tempfile
import json
import pprint
from apps.productmanagement.products import *
from lib.python import functions
from database import querydb
from config import es_constants

from lib.python import es_logging as log
logger = log.my_logger(__name__)

def create_request(productcode, version, mapsetcode=None, subproductcode=None):

    # Define the 'request' object
    request = {'product': productcode,
               'version': version}

    product = Product(product_code=productcode, version=version)
    # Check the level of the request
    if mapsetcode is None:
        if subproductcode is not None:
            logger.error('Create Request: If mapset is not defined, subproduct cannot be defined!')
            return request
        else:
            all_prod_mapsets = product.mapsets
            all_prod_subproducts = product.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                request['productmapsets'] = []
                mapset_dict = {}
                dataset_dict = {}
                for mapset in all_prod_mapsets:
                    mapset_dict = {'mapsetcode': mapset, 'mapsetdatasets': []}
                    # request['productmapsets'].append(mapset_dict)

                    dataset_dict = {}
                    all_mapset_datasets = product.get_subproducts(mapset=mapset)
                    for subproductcode in all_mapset_datasets:
                        missing = product.get_missing_datasets(mapset=mapset, sub_product_code=subproductcode, from_date=None, to_date=None)
                        # dataset_dict['subproductcode'] = row_dict['subproductcode']
                        # dataset_dict['product_type'] = row_dict['product_type']
                        dataset_dict = {'subproductcode': subproductcode,
                                        'missing': missing,
                                        'product_type': ''}
                        mapset_dict['mapsetdatasets'].append(dataset_dict)
                        dataset_dict = {}

                    request['productmapsets'].append(mapset_dict)
    # Mapset is defined
    else:
        if subproductcode is None:
            # Get full list of subproducts (ingest/derived) for the given mapset
            request['productmapsets'] = []
            mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}

            dataset_dict = {}
            all_mapset_datasets = product.get_subproducts(mapset=mapsetcode)
            for subproductcode in all_mapset_datasets:
                missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode, from_date=None, to_date=None)
                # dataset_dict['subproductcode'] = row_dict['subproductcode']
                # dataset_dict['product_type'] = row_dict['product_type']
                dataset_dict = {'subproductcode': subproductcode,
                                'missing': missing,
                                'product_type': ''}
                mapset_dict['mapsetdatasets'].append(dataset_dict)
                dataset_dict = {}

            request['productmapsets'].append(mapset_dict)

        else:
            # All variable defined -> get missing object
            # product = Product(product_code=productcode, version=version)
            missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode, from_date=None, to_date=None)
            request['productmapsets'] = []
            mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}
            dataset_dict = {'subproductcode': subproductcode, 'missing': missing}
            mapset_dict['mapsetdatasets'].append(dataset_dict)
            request['productmapsets'].append(mapset_dict)
    return request
    # Dump the request object to JSON

def create_archive_from_request(request_file):

    # Creates an archive file (.tgz) from a 'json' request file
    # Create a self-extracting archive (.bsx) from a template script and the .tgz

    # Read the request
    try:
        with open(request_file) as json_req:
            my_request = json.load(json_req)
            json_req.close()
    except:
        logger.error('Error in reading the request. Exit')
        return 1

    my_product = my_request['product']
    my_version = my_request['version']
    # See ES2-64 : mapset MUST be specified
    try:
        my_mapsets = my_request['productmapsets']
    except:
        logger.error('No mapset defined in the request: cannot proceed. Exit')
        return 1

    n_mapsets = len(my_mapsets)
    incresing_number=1

    # Loop over defined mapsets
    for my_mapset in my_mapsets:
        mapsetcode = my_mapset['mapsetcode']

        mapsetdatasets = my_mapset['mapsetdatasets']

        # Loop over all datasets in a mapset
        for mapsetdataset in mapsetdatasets:
            subproductcode =  mapsetdataset['subproductcode']
            missing_info = mapsetdataset['missing']
            archive_base_name=request_file.replace('.req','')
            archive_name=archive_base_name+'_{0:04d}'.format(incresing_number)+'.tgz'
            self_extracting_name=archive_name
            self_extracting_name=self_extracting_name.replace('.tgz','.bsx')
            logger.debug( 'Archive file name: {0}'.format(archive_name))

            # Create a product object - no date indication
            product = Product(product_code=my_product, version=my_version)
            [tarfile , results] = product.create_tar(missing_info, filetar=archive_name, tgz=True)
            logger.debug('Files found for {0}: {1}'.format(subproductcode,results['n_file_copied']))
            # Test there is - at list - 1 file missing
            if results['n_file_copied'] > 0:

                logger.info('Creating file {0}'.format(self_extracting_name))
                # Get the decompression script template
                decompress_file = es_constants.decompress_script

                target = open(self_extracting_name,'wb')
                shutil.copyfileobj(open(decompress_file,'rb'),target)
                shutil.copyfileobj(open(archive_name,'rb'),target)
                target.close()
                os.chmod(self_extracting_name,0775)
                # Increase the counter
                incresing_number+=1

            # Remove .tgz file
            os.remove(archive_name)
            product = None
    return 0

def get_archive_name(productcode, version, id):

    filename = es_constants.es2globals['base_tmp_dir']+os.path.sep
    filename += 'archive_'+productcode+'_'+version+'_'+id+'.tgz'
    return filename

def get_request_filename(productcode, version, subproductcode, mapsetcode, date=None):

    if date is None:
        filename = productcode+'_'+subproductcode+'_'+mapsetcode+'_'+version

    return filename

def create_archive_vars(productcode, version, mapsetcode, subproductcode, from_date=None, to_date=None, time_suffix=None, output_dir=None):

    # Creates an archive file (.tgz) for a single period (prod/version/sprod/mapset)
    incresing_number=1

    if output_dir is None:
        output_dir = es_constants.es2globals['base_tmp_dir']

    if time_suffix is not None:
        time_token=str(time_suffix)
    else:
        if from_date is not None:
            time_token=from_date
            if to_date is not None:
                time_token+='_to_'
                time_token+=to_date
        else:
            time_token='alltimes'

    # Define archive name
    archive_base_name=output_dir+os.path.sep+ \
                      productcode+'_'+version+'_'+mapsetcode+'_'+subproductcode+'_'+time_token

    archive_name=archive_base_name+'_{0:04d}'.format(incresing_number)+'.tgz'
    self_extracting_name=archive_name
    self_extracting_name=self_extracting_name.replace('.tgz','.bsx')

    logger.debug( 'Archive file name: {0}'.format(archive_name))

    # Create a product object - no date indication
    product = Product(product_code=productcode, version=version)
    [tarfile , results] = product.create_tar_vars(productcode, version, subproductcode, mapsetcode, from_date=from_date,
                                                  to_date=to_date, filetar=archive_name, tgz=True)

    logger.info( 'Tar archive created: {0}'.format(archive_name))
    logger.debug('Files found for {0}: {1}'.format(subproductcode,results['n_file_copied']))

    # Test there is - at list - 1 file missing
    if results['n_file_copied'] > 0:

        logger.info('Creating file {0}'.format(self_extracting_name))
        # Get the decompression script template
        decompress_file = es_constants.decompress_script

        target = open(self_extracting_name,'wb')
        shutil.copyfileobj(open(decompress_file,'rb'),target)
        shutil.copyfileobj(open(archive_name,'rb'),target)
        target.close()
        os.chmod(self_extracting_name,0775)
        # Increase the counter
        incresing_number+=1

    # Remove .tgz file
    os.remove(archive_name)
    product = None

    return self_extracting_name

