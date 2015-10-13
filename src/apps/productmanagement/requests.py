# -*- coding: utf-8 -*-
#
# purpose: handle request for completing datasets
# author:  MC, JvK
# date:  27.08.2015

import os
import glob
import tarfile
import shutil
import tempfile

# from config import es_constants
# from lib.python import es_logging as log
# from lib.python import functions
# from lib.python import metadata
# from database import querydb
#
# from .exceptions import (NoProductFound, MissingMapset)
# from .datasets import Dataset
# from .mapsets import Mapset
from apps.productmanagement.products import *

logger = log.my_logger(__name__)

def create_request(productcode, version, mapsetcode=None, subproductcode=None):

    product = Product(product_code=productcode, version=version)

    # Define the 'request' object
    request = {'product': productcode,
               'version': version,}

    # Check the level of the request
    if mapsetcode is None:
        if subproductcode is not None:
            logger.error('If mapset in not defined, subproduct cannot be defined !')
            return 1
        else:
            # Get list of all ACTIVE ingested/derived subproducts and associated mapsets
            pass

    # Mapset is defined
    else:
        if subproductcode is None:
            # Get full list of subproducts (ingest/derived) for the given mapset
            pass
        else:
            # All variable defined -> get missing object
            missing = product.get_missing_datasets(mapset=mapsetcode, sub_product_code=subproductcode, from_date=None, to_date=None)

    # Dump the request object to JSON


def handle_request():
    pass