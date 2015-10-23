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

from apps.productmanagement.products import *
from lib.python import functions
from database import querydb

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
            logger.error('If mapset is not defined, subproduct cannot be defined !')
            return 1
        else:
            # Get list of all ACTIVE ingested/derived subproducts and associated mapsets
            product_mapsets_subproducts = querydb.get_enabled_ingest_derived_of_product(productcode=productcode, version=version)
            if product_mapsets_subproducts.__len__() > 0:
                request['productmapsets'] = []
                mapset_dict = {}
                dataset_dict = {}
                mapsetcode = ''
                for row in product_mapsets_subproducts:
                    row_dict = functions.row2dict(row)
                    if row_dict['mapsetcode'] != mapsetcode:
                        if mapsetcode != '':
                            request['productmapsets'].append(mapset_dict)
                        mapsetcode = row_dict['mapsetcode']
                        mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}
                        dataset_dict = {}

                    missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=row_dict['subproductcode'], from_date=None, to_date=None)
                    # dataset_dict['subproductcode'] = row_dict['subproductcode']
                    # dataset_dict['product_type'] = row_dict['product_type']
                    dataset_dict = {'subproductcode': row_dict['subproductcode'], 'missing': missing,
                                    'product_type': row_dict['product_type']}
                    mapset_dict['mapsetdatasets'].append(dataset_dict)
                    dataset_dict = {}
                request['productmapsets'].append(mapset_dict)
    # Mapset is defined
    else:
        if subproductcode is None:
            # Get full list of subproducts (ingest/derived) for the given mapset
            request['productmapsets'] = []
            mapset_dict = {'mapsetcode': mapsetcode, 'mapsetdatasets': []}
            # product = Product(product_code=productcode, version=version)
            product_mapset_subproducts = querydb.get_enabled_ingest_derived_of_product(productcode=productcode, version=version, mapsetcode=mapsetcode)
            if product_mapset_subproducts.__len__() > 0:
                # dataset_dict = {}
                for row in product_mapset_subproducts:
                    row_dict = functions.row2dict(row)
                    missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=row_dict['subproductcode'], from_date=None, to_date=None)
                    # dataset_dict['subproductcode'] = row_dict['subproductcode']
                    dataset_dict = {'subproductcode': row_dict['subproductcode'], 'missing': missing,
                                    'product_type': row_dict['product_type']}
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

#
# def handle_request(json_request):
#
#     product = json_request.
#     version = json_request.