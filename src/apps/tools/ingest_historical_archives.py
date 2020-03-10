from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
__author__ = 'analyst'
#
#	purpose: Run the script to ingest Historical archives
#	author:  M.Clerici
#	date:	 28.08.2015
#   descr:	 It runs the ingestion of historical files (e.g. after the initial installation)
#
#	history: 1.0
#

import sys, time
from apps.acquisition.ingestion import *
from config import es_constants
from lib.python import es_logging as log
# logger = log.my_logger(__name__)
logger = log.my_logger('apps.es2system.ingest_archive')


def ingest_historical_archives(input_dir=None, dry_run=False):
    #    Ingest the files in format MESA_JRC_<prod>_<sprod>_<date>_<mapset>_<version>
    #    from a given location
    #    Gets the list of products/version/subproducts active for ingestion and active for processing

    input_dir_def = es_constants.es2globals['archive_dir']
    if input_dir is None:
        input_dir = input_dir_def

    logger.info("Entering routine %s" % 'ingest_historical_archives')
    # echo_query = False

    # time.sleep(30)
    logger.info("Entering loop")
    # exit(1)
    # Get all active product ingestion records with a subproduct count.
    active_product_ingestions = querydb.get_ingestion_product(allrecs=True)
    for active_product_ingest in active_product_ingestions:

        productcode = active_product_ingest[0]
        productversion = active_product_ingest[1]

        # For the current active product ingestion: get all
        product = {"productcode": productcode,
                   "version": productversion}

        # Get the list of acquisition sources that are defined for this ingestion 'trigger' (i.e. prod/version)
        # NOTE: the following implies there is 1 and only 1 '_native' subproduct associated to a 'subproduct';
        native_product = {"productcode": productcode,
                          "subproductcode": productcode + "_native",
                          "version": productversion}
        sources_list = querydb.get_product_sources(**native_product)

        logger.debug("For product [%s] N. %s  source is/are found" % (productcode,len(sources_list)))

        ingestions = querydb.get_ingestion_subproduct(allrecs=False, **product)
        for ingest in ingestions:
            logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (productcode, productversion,ingest.subproductcode, ingest.mapsetcode))
            ingest_archives_eumetcast_product(productcode, productversion,ingest.subproductcode,ingest.mapsetcode, dry_run=dry_run, input_dir=input_dir, no_delete=True)

    # Get all active processing chains [product/version/algo/mapset].
    active_processing_chains = querydb.get_active_processing_chains()
    for chain in active_processing_chains:
        a = chain.process_id
        logger.debug("Processing Chain N.:%s" % str(chain.process_id))
        processed_products = querydb.get_processing_chain_products(chain.process_id, type='output')
        for processed_product in processed_products:
            productcode = processed_product.productcode
            version = processed_product.version
            subproductcode = processed_product.subproductcode
            mapset = processed_product.mapsetcode
            logger.debug("Looking for product [%s]/version [%s]/subproducts [%s]/mapset [%s]" % (productcode, version,subproductcode,mapset))
            ingest_archives_eumetcast_product(productcode, version,subproductcode,mapset, dry_run=dry_run, input_dir=input_dir, no_delete=True)


if __name__ == '__main__':
    # input_dir = str(sys.argv[1])
    input_dir = es_constants.es2globals['archive_dir']
    print (input_dir)
    ingest_historical_archives(input_dir=input_dir)
