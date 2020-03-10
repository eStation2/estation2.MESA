from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
_author__ = "Marco Clerici"
#
#	purpose: Define the processing service
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 17.12.2014
#   descr:	 Process files into the specified 'mapset'
#	history: 1.0
#

# # import standard modules
import os, sys
import shutil
import re
import time
from multiprocessing import *

# import eStation2 modules
from database import querydb
from lib.python import functions
from lib.python import es_logging as log
from config import es_constants
from apps.productmanagement import datasets
from apps.processing import proc_functions

logger = log.my_logger(__name__)
data_dir = es_constants.es2globals['data_dir']

#   Main module in processing, driving a specific pipeline

from apps.processing import processing_std_precip
from apps.processing import processing_std_ndvi
from apps.processing import processing_std_fronts
from apps.processing import processing_merge
from apps.processing import processing_std_lsasaf_lst
from apps.processing import processing_std_lsasaf_et
from apps.processing import processing_std_modis_monavg
from apps.processing import processing_std_modis_firms
from apps.processing import processing_modis_pp
from apps.processing import processing_std_msg_mpe
from apps.processing import processing_std_rain_onset
from apps.processing import processing_std_seas_cum
from apps.processing import processing_std_precip_1day
from apps.processing import processing_std_olci_wrr
from apps.processing import processing_std_gradient
from apps.processing import processing_std_monavg
from apps.processing import processing_std_3dayavg
from apps.processing import processing_std_dmp
from apps.processing import processing_std_opfish
from apps.processing import processing_std_vgt

from lib.python.daemon import DaemonDryRunnable

class ProcessingDaemon(DaemonDryRunnable):
    def run(self):
        loop_processing(dry_run=self.dry_run)

def upsert_database(process_id, productcode, version, mapset, proc_lists, input_product_info):

#    Ensure all derived output product are in the 'product' and 'process_product' table
#    Arguments: process_id
#               productcode, version, mapset
#               proc_lists: as returned by the pipeline
#               input_product_info: metadata from the input products

    out_sprods = proc_lists.list_subprods
    for proc_sub_product in out_sprods:
        try:
            querydb.update_processing_chain_products(process_id,
                                                     productcode,
                                                     version,
                                                     mapset,
                                                     proc_sub_product,
                                                     input_product_info)
        except:
            logger.error("Error in upsert_database")


def loop_processing(dry_run=False, serialize=False, test_one_product=None):

#    Driver of the process service
#    Reads configuration from the database
#    Creates the pipelines for the active processing
#    Calls the active pipelines with the relevant argument
#    Arguments: dry_run -> if > 0, it triggers pipeline_printout() rather than pipeline_run()
#                       -> if < 0, it triggers pipeline_printout_graph() rather than pipeline_run()
#               serialize -> False (default): detach the process and work in parallel
#                         -> True: do NOT detach processes and work in series (mainly for debugging)

    # Clean dir with locks at restart
    if os.path.isdir(es_constants.processing_tasks_dir):
        shutil.rmtree(es_constants.processing_tasks_dir)

    logger.info("Entering routine %s" % 'loop_processing')
    functions.check_output_dir(es_constants.processing_tasks_dir)

    # Read sleep time (used by each processing chain)
    sleep_time=es_constants.processing_sleep_time_sec

    while True:

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

        logger.debug("Pipeline run level: %i" % pipeline_run_level)
        logger.debug("Pipeline printout level: %i" % pipeline_printout_level)

        for chain in active_processing_chains:

            derivation_method = chain.derivation_method             # name of the method in the module
            algorithm = chain.algorithm                             # name of the .py module
            mapset = chain.output_mapsetcode
            process_id = chain.process_id

            do_processing_singleproduct = False
            if test_one_product:
                if process_id != test_one_product:
                    do_processing_singleproduct = True

            if do_processing_singleproduct:
                continue

            # Get input products
            input_products = querydb.get_processing_chain_products(chain.process_id,type='input')
            product_code = input_products[0].productcode
            sub_product_code = input_products[0].subproductcode
            version = input_products[0].version
            native_mapset=input_products[0].mapsetcode

            logger.info("Algorithm %s applied to [%s]/[%s]" % (str(algorithm), str(product_code),str(sub_product_code)))

            # Get product metadata for output products (from first input)
            input_product_info = querydb.get_product_out_info(productcode=product_code,
                                                              subproductcode=sub_product_code,
                                                              version=version)

            # Define a standard logfile associated to the processing chain
            processing_unique_id='ID='+str(process_id)+'_PROD='+product_code+'_METHOD='+derivation_method+'_ALGO='+algorithm
            logfile='apps.processing.'+processing_unique_id

            # Case of a 'std_' processing (i.e. ruffus with 1 input) -> get all info from 1st INPUT and manage dates
            if re.search('^std_.*',algorithm):
                logger.debug("Processing Chain is standard type")

                # Define dates interval from input product
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
                        'version':version,
                        'logfile':logfile}
                        # 'native_mapset':native_mapset}

                logger.debug('RL:{pipeline_run_level}; PL:{pipeline_printout_level},prod:{prod}, sprod:{starting_sprod},mapset:{mapset},\
                            dates:{starting_dates},version:{version}'.format(**args))

                # Define an id from a combination of fields
                processing_unique_lock=es_constants.processing_tasks_dir+processing_unique_id+'.lock'

                # Check the processing chain is not locked
                if not os.path.isfile(processing_unique_lock):

                    # # Perform sanity check on the output files
                    # processing_base_directory = es_constants.es2globals['processing_dir']+\
                    #                             os.path.sep+product_code+\
                    #                             os.path.sep+version+\
                    #                             os.path.sep+mapset+os.path.sep+'derived'
                    #
                    # proc_functions.clean_corrupted_files(processing_base_directory, dry_run=True)

                    open(processing_unique_lock,'a').close()
                    logger.debug("Unique lock created: % s" % processing_unique_id)
                    # Define the module name and function()
                    module_name = 'processing_'+algorithm
                    function_name = 'processing_'+derivation_method
                    # Enter the module and walk until to the name of the function() to be executed
                    proc_dir = __import__("apps.processing")
                    try:
                        proc_pck = getattr(proc_dir, "processing")
                    except:
                        logger.error("Error in loading module apps.processing.processing")
                        return
                    try:
                        proc_mod = getattr(proc_pck, module_name)
                    except:
                        logger.error("Error in loading module [%s]" % module_name)
                        return
                    try:
                        proc_func= getattr(proc_mod, function_name)
                    except:
                        logger.error("Error in loading algoritm [%s] for module [%s]" % (function_name,module_name))
                        return

                    #  Check serialize option
                    if serialize==False:

                        # Call to the processing pipeline
                        logger.debug("Launching the pipeline")

                        #proc_lists = proc_func(**args)
                        results_queue = Queue()
                        p = Process(target=proc_func, args=(results_queue,), kwargs=args)
                        #p.daemon = True
                        logger.debug("Before starting the process .. %i", p.is_alive())

                        p.start()
                        logger.debug("After start  .. %i", p.is_alive())
                        #proc_lists=results_queue.get()
                        p.join()
                        logger.debug("After join  .. %i", p.is_alive())
                        # Sleep time to be read from processing
                        time.sleep(float(sleep_time))
                        logger.debug("Execution finished - remove lock")
                        try:
                            os.remove(processing_unique_lock)
                        except:
                            logger.warning("Lock not removed: %s" % processing_unique_lock)

                    # Do NOT detach process (work in series)
                    else:
                        logger.info("Work in series - do not detach process")
                        results_queue = Queue()
                        proc_lists = proc_func(results_queue, **args)
                        os.remove(processing_unique_lock)
                        time.sleep(float(sleep_time))
                else:
                    logger.debug("Lock already exist: %s" % processing_unique_id)


            # Case of no 'std' (e.g. merge processing - or more than 1 input) -> get output products and pass everything to function
            else:
                output_products = querydb.get_processing_chain_products(chain.process_id,type='output')
                # Prepare arguments
                args = {'pipeline_run_level':pipeline_run_level,
                        'pipeline_printout_level':pipeline_printout_level,
                        'input_products': input_products,
                        'output_product': output_products,
                        'logfile': logfile}

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

                    if re.search('.*merge.*',algorithm):
                        logger.debug("Processing Chain is merge type")
                        # Do NOT detach process (work in series)
                        proc_lists = proc_func(**args)

                        time.sleep(float(sleep_time))
                        logger.info("Waking-up now, and removing the .lock")
                        os.remove(processing_unique_lock)
                    else:
                        logger.info("Processing Chain is more-inputs type (e.g. modis-pp)")

                        # We have to 'detach' the process for avoiding ruffus exception 'error_duplicate_task_name'
                        results_queue = Queue()
                        p = Process(target=proc_func, args=(results_queue,), kwargs=args)
                        p.start()
                        p.join()

                        # Sleep time to be read from processing
                        time.sleep(float(sleep_time))
                        logger.debug("Execution finished - remove lock")
                        try:
                            os.remove(processing_unique_lock)
                        except:
                            logger.warning("Lock not removed: %s" % processing_unique_lock)

                else:
                    logger.debug("Processing already running for ID: %s " % processing_unique_id)

        if do_processing_singleproduct:
            logger.info("End of the loop for single product ... Exit")
            return

        logger.info("End of the loop ... wait a while")
        time.sleep(1)


# Pierluigi
def worker(num):
    """thread worker function"""
    #print 'Worker:', num
    name = current_process().name
    print((name, 'Starting'))
    time.sleep(2)
    print((name, 'Exiting'))


if __name__ == '__OLDmain__':
    freeze_support()
    jobs = []
    for i in range(5):
        p = Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()

if __name__ == '__main__':
    freeze_support()
    loop_processing(False,False)