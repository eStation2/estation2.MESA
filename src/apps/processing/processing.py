_author__ = "Marco Clerici"
#
#	purpose: Define the processing service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 17.12.2014
#   descr:	 Process files into the specified 'mapset'
#	history: 1.0
#

# source eStation2 base definitions
import os, sys
import shutil
import re

# import standard modules
import time
import datetime

# import eStation2 modules
from database import querydb
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from apps.productmanagement import datasets
from apps.processing import proc_functions

logger = log.my_logger(__name__)
data_dir= es_constants.es2globals['data_dir']

#   Main module in processing, driving a specific pipeline

from apps.processing import processing_std_precip
from apps.processing import processing_std_ndvi
from apps.processing import processing_merge

from lib.python.daemon import DaemonDryRunnable

def loop_processing(dry_run=False):

#    Driver of the process service
#    Reads configuration from the database
#    Creates the pipelines for the active processing
#    Calls the active pipelines with the relevant argument
#    Arguments: dry_run -> if > 0, it triggers pipeline_printout() rather than pipeline_run()
#                       -> if < 0, it triggers pipeline_printout_graph() rather than pipeline_run()

    # Clean dir with locks
    if os.path.isdir(es_constants.processing_tasks_dir):
        shutil.rmtree(es_constants.processing_tasks_dir)
    logger.info("Entering routine %s" % 'loop_processing')
    echo_query = False
    functions.check_output_dir(es_constants.processing_tasks_dir)
    while True :

        logger.debug("Entering infinite loop")
        # Get all active processing chains from the database.
        active_processing_chains = querydb.get_active_processing_chains()

        # Manage dry_run
        if dry_run:
            pipeline_run_level = 0
            pipeline_printout_level = 3
        else:
            pipeline_run_level = 3
            pipeline_printout_level = 0

        for chain in active_processing_chains:

            logger.debug("Processing Chain N.:%s" % str(chain.process_id))

            derivation_method = chain.derivation_method             # name of the method in the module
            algorithm = chain.algorithm                             # name of the .py module
            mapset = chain.output_mapsetcode
            process_id = chain.process_id

            # Get input products
            input_products = querydb.get_processing_chain_products(chain.process_id,type='input')

            # Case of a 'std_' (i.e. ruffus) processing -> get all info from 1st INPUT and manage dates
            if re.search('^std_.*',algorithm):

                product_code = input_products[0].productcode
                sub_product_code = input_products[0].subproductcode
                version = input_products[0].version
                start_date = input_products[0].start_date
                end_date = input_products[0].end_date

                # Manage the dates
                list_dates = proc_functions.get_list_dates_for_dataset(product_code, sub_product_code, version, start_date=start_date, end_date=end_date)

                # Prepare arguments
                args = {'pipeline_run_level':pipeline_run_level, \
                        'pipeline_printout_level':pipeline_printout_level,\
                        'starting_sprod': sub_product_code, \
                        'prod': product_code, \
                        'mapset':mapset,\
                        'starting_dates': list_dates,\
                        'version':version}

            # Case of no 'std' (i.e. ruffus processing) -> get output products and pass everything to function
            else:
                output_products = querydb.get_processing_chain_products(chain.process_id,type='output')
                # Prepare arguments
                args = {'pipeline_run_level':pipeline_run_level, \
                        'pipeline_printout_level':pipeline_printout_level,\
                        'input_products': input_products, \
                        'output_product': output_products}

            # Define an id from a combination of fields
            processing_unique_id='ID='+str(process_id)+'_METHOD='+derivation_method+'_ALGO='+algorithm+'.lock'
            processing_unique_lock=es_constants.processing_tasks_dir+processing_unique_id

            if not os.path.isfile(processing_unique_lock):
                logger.debug("Launching processing for ID: %s" % processing_unique_id)
                open(processing_unique_lock,'a').close()

                # Define the module name and function()
                module_name = 'processing_'+algorithm
                function_name = 'processing_'+derivation_method
                # Enter the module and walk until to the name of the function() to be executed
                proc_dir = __import__("apps.processing")
                proc_pck = getattr(proc_dir, "processing")
                proc_mod = getattr(proc_pck, module_name)
                proc_func= getattr(proc_mod, function_name)

                # fork and call the std_precip 'generic' processing
                pid = os.fork()
                if pid == 0:
                    # Call to the processing pipeline
                    [list_subprods, list_subprod_groups] = proc_func(**args)
                    # Simulate longer processing (TEMP)
                    logger.info("Going to sleep for a while - to be removed")
                    time.sleep(50)
                    os.remove(processing_unique_lock)
                    sys.exit(0)
                else:
                    # Qui sono il padre
                    pass
                    #os.wait()
            else:
                logger.debug("Processing already running for ID: %s " % processing_unique_id)

        logger.info("End of the loop ... wait a while")
        time.sleep(5)

class ProcessingDaemon(DaemonDryRunnable):
    def run(self):
        loop_processing(dry_run=self.dry_run)

