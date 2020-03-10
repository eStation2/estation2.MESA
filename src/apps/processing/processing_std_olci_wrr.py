from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing chain for 'ndvi-like' processing chains
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.01.2015
#   descr:	 Generate additional Derived products/implements processing chains
#	history: 1.0
#

# Import std modules
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import glob
import os
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from lib.python import metadata

# Import third-party modules
from ruffus import *
from datetime import datetime, timedelta

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, nrt_products=True,
                    logger=None):


    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all ON
    activate_3davg_comput=1
    activate_1monavg_comput=1


    sds_meta = metadata.SdsMetadata()
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files (chl)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, ext)
    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)
    starting_files = input_dir+"*"+in_prod_ident

    # ----------------------------------------------------------------------------------------------------------------
    # 1 . 3davg
    # 3 Day average of the 1 day Chl, re-projected on target mapset
    output_sprod=proc_lists.proc_add_subprod("3daysavg", "olci-wrr", final=False,
                                             descriptive_name='3day chl-oc4me',
                                             description='mean 3 day composite',
                                             frequency_id='e1day',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_3davg = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_3davg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    # Use a specific function, to skip the current day
    def generate_parameters_3davg():

        #   Look for all input files in input_dir, and sort them
        if starting_dates is not None:
            input_files = []
            for my_date in starting_dates:
                input_files.append(input_dir + my_date + in_prod_ident)
        else:
            starting_files = input_dir + "*" + in_prod_ident
            input_files = glob.glob(starting_files)

        logger.debug("starting_files %s" % input_files)

        day_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename = os.path.basename(input_file)
            mydate = functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd = str(mydate)[0:8]
            if mydate_yyyymmdd not in day_list:
                day_list.append(mydate_yyyymmdd)

        day_list = sorted(day_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.today()
        yesterday = today - timedelta(1)
        today_str = today.strftime('%Y%m%d')
        yesterday_str = yesterday.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        for myday in day_list:
            # Exclude the current day and yesterday
            #if myday != today_str or myday != yesterday_str:

                #some_list = ['abc-123', 'def-456', 'ghi-789', 'abc-456']
            input_file = [s for s in input_files if myday in s]
            file_list = []
                #for input_file in input_files:
                #for i, input_file in enumerate(input_files, 1):

            basename = os.path.basename(input_file[0])
            # Date is in format YYYYMMDD
            mydate_yyyymmdd = functions.get_date_from_path_filename(basename)

            #if mydate_yyyymmdd != day_list[i]:
            yyyy = int(mydate_yyyymmdd[0:4])
            mm = int(mydate_yyyymmdd[4:6])
            dd = int(mydate_yyyymmdd[6:8])
            day2 = datetime(yyyy,mm,dd) + timedelta(1)
            day2_filepath = input_dir + day2.strftime('%Y%m%d') + in_prod_ident
            if not functions.is_file_exists_in_path(day2_filepath):
                continue

            day3 = datetime(yyyy, mm, dd) + timedelta(2)
            day3_filepath = input_dir + day3.strftime('%Y%m%d') + in_prod_ident
            if not functions.is_file_exists_in_path(day3_filepath):
                continue

            file_list.append(input_file[0])
            file_list.append(day2_filepath)
            file_list.append(day3_filepath)

            output_file = es_constants.processing_dir + subdir_3davg + os.path.sep + mydate_yyyymmdd + prod_ident_3davg
            file_list = sorted(file_list)
            # Check here the number of missing files (for optimization)
            if len(file_list) == 3:
                yield (file_list, output_file)


    @active_if(activate_3davg_comput)
    @files(generate_parameters_3davg)
    def olci_wrr_3dcum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "", "input_nodata":1000, "output_nodata":1000}
        raster_image_math.do_avg_image(**args)

    # ----------------------------------------------------------------------------------------------------------------
    #  2. Chla Monthly product (avg)
    # 3 Day average of the 1 day Chl, re-projected on target mapset
    output_sprod=proc_lists.proc_add_subprod("monchla", "olci-wrr", final=False,
                                             descriptive_name='Monthly chl-oc4me',
                                             description='Mean 1 month composite',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_mon_chla = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_mon_chla = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_mon_chla+"{YYYYMM[0]}"+'01'+prod_ident_mon_chla

    @active_if(activate_1monavg_comput)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    def olci_wrr_monchla(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_olci_wrr(res_queue, pipeline_run_level=0, pipeline_printout_level=0, pipeline_printout_graph_level=0,
                        prod='', starting_sprod='', mapset='', version='', starting_dates=None,
                        nrt_products=True, write2file=None, logfile=None, touch_files_only=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_olci_wrr')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version, starting_dates=starting_dates,
                                 nrt_products=nrt_products, logger=spec_logger)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, touch_files_only=touch_files_only, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_'+prod+'_'+version+'.sqlite'),
                     checksum_level=0)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level) #, output_stream=fout)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True


# def processing_olci_wrr_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
#                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
#                           starting_dates=None, write2file=None,logfile=None,touch_files_only=False):
#
#     result = processing_olci_wrr(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  prod=prod,
#                                  starting_sprod=starting_sprod,
#                                  mapset=mapset,
#                                  version=version,
#                                  starting_dates_linearx2=starting_dates,
#                                  nrt_products=False,
#                                  update_stats=True,
#                                  write2file=write2file,
#                                  logfile=logfile,
#                                  touch_files_only=touch_files_only)
#
#     return result
#
# def processing_olci_wrr_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
#                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
#                           starting_dates=None,write2file=None, logfile=None,touch_files_only=False):
#
#     result = processing_olci_wrr(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  prod=prod,
#                                  starting_sprod=starting_sprod,
#                                  mapset=mapset,
#                                  version=version,
#                                  starting_dates_linearx2=starting_dates,
#                                  nrt_products=True,
#                                  update_stats=False,
#                                  write2file=write2file,
#                                  logfile=logfile,
#                                  touch_files_only=touch_files_only)
#
#     return result
#
# def processing_olci_wrr_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
#                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
#                           starting_dates=None, logfile=None,touch_files_only=False):
#
#     result = processing_olci_wrr(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  prod=prod,
#                                  starting_sprod=starting_sprod,
#                                  mapset=mapset,
#                                  version=version,
#                                  starting_dates_linearx2=starting_dates,
#                                  nrt_products=True,
#                                  update_stats=True,
#                                  logfile=logfile,
#                                  touch_files_only=touch_files_only)
#
#     return result
