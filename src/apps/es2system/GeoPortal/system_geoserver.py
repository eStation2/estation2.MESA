#!/usr/bin/env python
# _author__ = "Marco Clerici"
#
#	purpose: Synchronize data towards GeoServer
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 26.05.2015
#       descr:	 For a list of 'active' datasets, ensure synchronization towards GeoServer, by considering:
#               - .tif file copy
#               - Workspaces, styles and raster upload to geoserver
#
#	history: 1.0
#

# import eStation2 modules
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
#!/usr/bin/env python
# _author__ = "Marco Clerici"
#
#	purpose: Synchronize data towards GeoServer
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 26.05.2015
#       descr:	 For a list of 'active' datasets, ensure synchronization towards GeoServer, by considering:
#               - .tif file copy
#               - Workspaces, styles and raster upload to geoserver
#
#	history: 1.0
#

# import eStation2 modules
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div

from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from database import querydb
import datetime
from apps.es2system.GeoPortal import eStationTools as esTools
from apps.es2system.GeoPortal import geoserverREST
import time

from apps.productmanagement import datasets
from apps.productmanagement import products
from lib.python.daemon import DaemonDryRunnable

logger = log.my_logger(__name__)
#   Definitions
local_data_dir = es_constants.es2globals['processing_dir']
remote_data_dir = geoserverREST.restBaseDir

def syncGeoserver():

    #
    #   Copy some 'relevant' datasets to GeoServer
    #   Selection of datasets is done on the basis of the product.geoserver table
    #


    # Get list of all 'relevant' subproducts (see 2. above)
    list_active_geoserver = esTools.get_activated_geoserver()

    # Loop over existing sub_products
    for geoserver_sprod in list_active_geoserver:


        # Extract local variable:
        my_prod     = geoserver_sprod.productcode
        my_subprod  = geoserver_sprod.subproductcode
        my_version  = geoserver_sprod.version
        start_date  = geoserver_sprod.startdate
        end_date    = geoserver_sprod.enddate

        logger.info("Working on Product/Subproduct/Version: {0}/{1}/{2}".format(my_prod, my_subprod, my_version))

        # Manage dates from bigint to datetime
        if functions.is_date_yyyymmdd(str(start_date), silent=True):
            date_start = datetime.datetime.strptime(str(start_date), '%Y%m%d').date()
        else:
            date_start = None

        if functions.is_date_yyyymmdd(str(end_date), silent=True):
            date_end = datetime.datetime.strptime(str(end_date), '%Y%m%d').date()
        else:
            date_end = None

        # Get additional products info
        product_info = querydb.get_product_out_info(productcode=my_prod,
                                                    subproductcode=my_subprod,
                                                    version=my_version)

        # my_mapset   = subprod.mapsetcode
        my_type     = product_info[0].product_type
        my_category = product_info[0].category_id

        # Create a Product object (to get mapsets)
        my_product = products.Product(my_prod, version=my_version)
        my_mapsets = my_product.mapsets

        if len(my_mapsets) > 1:
            logger.info('More than 1 mapset exists. Take the first')

        if len(my_mapsets) == 0:
            logger.warning('No any mapset exists. Skip.')
            continue

        my_mapset = my_mapsets[0]

        # Create a Dataset object (to get file list)
        # If data_start is not set (e.g. for 10davg prod) create w/o dates
        if date_start:
            my_dataset = datasets.Dataset(my_prod, my_subprod, my_mapset, version=my_version, from_date=date_start, to_date=date_end)
            if my_dataset._frequency.dateformat == 'MMDD':
                logger.warning('Product of type MMDD: date specification not supported. Skip.')
                continue
            file_list = my_dataset.get_filenames_range()
        else:
            my_dataset = datasets.Dataset(my_prod, my_subprod, my_mapset, version=my_version)
            file_list = my_dataset.get_filenames()

        # Check that there is at least 1 file
        if len(file_list) > 0:
            # Check the Workspace exists, or create it
            my_workspace = esTools.setWorkspaceName(my_category, my_prod, my_subprod, my_version, my_mapset, nameType= geoserverREST.geoserverWorkspaceName)

            if not geoserverREST.isWorkspace(my_workspace):
                geoserverREST.createWorkspace(my_workspace)

            # Loop over files and upload
            for my_file in file_list:

                my_date = functions.get_date_from_path_full(my_file)

                # if subprod in list_active_subprods:
                logger.debug("Working on Product/Subproduct/Version/Mapset/Date: {0}/{1}/{2}/{3}/{4}".format(
                    my_prod, my_subprod, my_version, my_mapset, my_date))

                # Upload the file and register
                esTools.uploadAndRegisterRaster(my_category, my_prod, my_subprod, my_version, my_mapset, my_date, my_type, local_data_dir)


def loop_geoserver():

    logger.info("Entering routine %s" % 'loop_geoserver')
    sleep_time = 300

    while 1:

        logger.info("Calling %s" % 'syncGeoserver')
        syncGeoserver()
        logger.info("Waiting %s minute" % str(old_div(sleep_time,60)))
        time.sleep(sleep_time)

class SystemDaemon(DaemonDryRunnable):
    def run(self):
        loop_geoserver()
