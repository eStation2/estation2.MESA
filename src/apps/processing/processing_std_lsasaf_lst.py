#
#	purpose: Define the processing service (by using ruffus)
#	author:  Olivier Thamba and Maixent Kambi 
#	date:	 20150318
#   	descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#

# Source my definitions
from config import es_constants
import os
import glob
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from apps.processing.proc_functions import reproject_output
from lib.python import es_logging as log

# Import third-party modules
from ruffus import *
import datetime
import itertools

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version, starting_dates=None, proc_lists=None):

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all ON
    activate_1dmax_comput=1
    activate_10dmax_comput=1
    activate_10d15min_comput=1
    activate_10dmin_comput=1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, native_mapset, version, ext)

    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, native_mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    # ----------------------------------------------------------------------------------------------------------------
    # 1dmax
    output_sprod=proc_lists.proc_add_subprod("1dman", "lsasaf-lst", final=False,
                                             descriptive_name='1d Maximum',
                                             description='Daily Maximum',
                                             frequency_id='e1day',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    output_sprod='1dmax'
    out_prod_ident_1dmax = functions.set_path_filename_no_date(prod, output_sprod, target_mapset, version, ext)
    output_subdir_1dmax  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, target_mapset)
    # Input files
    in_prod_1dmax='lst'
    in_prod_ident_1dmax = functions.set_path_filename_no_date(prod, in_prod_1dmax, target_mapset, version, ext)
    input_dir_1dmax = es_constants.processing_dir+ \
                     functions.set_path_sub_directory(prod, in_prod_1dmax, 'Derived', version, target_mapset)

    starting_files_1dmax = input_dir_1dmax+"*"+in_prod_ident_1dmax

    formatter_in_1dmax="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident_1dmax
    formatter_out_1dmax="{subpath[0][5]}"+os.path.sep+output_subdir_1dmax+"{YYYYMM[0]}"+'01'+out_prod_ident_1dmax
#
    @active_if(activate_1dmax_comput)
    @collate(starting_files_1dmax, formatter(formatter_in_1dmax),formatter_out_1dmax)
    def lsasaf_lst_1dmax(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-32768}
        raster_image_math.do_max_image(**args)

#     #   ---------------------------------------------------------------------
#     #   Dekad average for every 30min (mm/h)
#     #   NOTE: this product is compute w/o re-projection, i.e. on the 'native' mapset
#
#     output_sprod_group=proc_lists.proc_add_subprod_group("lsasaf-et")
#     output_sprod=proc_lists.proc_add_subprod("10d30min", "lsasaf-et", final=False,
#                                              descriptive_name='10day Average over 30 min',
#                                              description='10day Average computed for every 30 min',
#                                              frequency_id='e30minute', # Is it OK ???????
#                                              date_format='YYYYMMDD',
#                                              masked=False,
#                                              timeseries_role='',
#                                              active_default=True)
#
#     out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, native_mapset, version, ext)
#     output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, native_mapset)
#
#     def generate_parameters_10d30min():
#
#         #   Look for all input files in input_dir, and sort them
#         input_files = glob.glob(starting_files)
#         dekad_list = []
#         # Create unique list of all dekads (as 'Julian' number)
#         for input_file in input_files:
#             basename=os.path.basename(input_file)
#             mydate=functions.get_date_from_path_filename(basename)
#             mydate_yyyymmdd=str(mydate)[0:8]
#             mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
#             if mydekad_nbr not in dekad_list:
#               dekad_list.append(mydekad_nbr)
#
#         dekad_list = sorted(dekad_list)
#
#         # Compute the 'julian' dakad for the current day
#         today = datetime.date.today()
#         today_str = today.strftime('%Y%m%d')
#         dekad_now = functions.conv_date_2_dekad(today_str)
#
#         # Generate the list of 30 min time in a day
#         timelist = [datetime.time(h,m).strftime("%H%M") for h,m in itertools.product(xrange(0,24),xrange(0,60,30))]
#
#         for time in timelist:
#             files_for_time = glob.glob(input_dir+os.path.sep+'*'+time+in_prod_ident)
#             for dekad in dekad_list:
#                 # Exclude the current dekad
#                 if dekad != dekad_now:
#                     file_list = []
#                     my_dekad_str = functions.conv_dekad_2_date(dekad)
#                     output_file=es_constants.processing_dir+output_subdir+os.path.sep+my_dekad_str+time+out_prod_ident
#
#                     for myfile in files_for_time:
#                         basename=os.path.basename(myfile)
#                         mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
#                         mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
#                         if mydekad_nbr == dekad:
#                             file_list.append(myfile)
#
#                     yield (file_list, output_file)
#
#     @active_if(activate_10d30min_comput)
#     @files(generate_parameters_10d30min)
#     def lsasaf_etp_10d30min(input_file, output_file):
#
#         output_file = functions.list_to_element(output_file)
#         functions.check_output_dir(os.path.dirname(output_file))
#         args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
#                 "options": "compress=lzw", "input_nodata":-32768}
#
#         raster_image_math.do_avg_image(**args)
#
#     # ----------------------------------------------------------------------------------------------------------------
#     #   10 day Cumulate (mm)
#     #   NOTE: this product is compute with re-projection, i.e. on the 'target' mapset
#
#     output_sprod=proc_lists.proc_add_subprod("10dcum", "lsasaf-et", final=False,
#                                              descriptive_name='10day Cumulate',
#                                              description='10day Cumulate in mm',
#                                              frequency_id='e1dekad',
#                                              date_format='YYYYMMDD',
#                                              masked=False,
#                                              timeseries_role='',
#                                              active_default=True)
#     out_prod_ident_10dcum = functions.set_path_filename_no_date(prod, "10dcum", target_mapset, version, ext)
#     output_subdir_10dcum  = functions.set_path_sub_directory   (prod, "10dcum", 'Derived', version, target_mapset)
#
#     #   Define input files
#     in_prod_10dcum = '10d30min'
#     in_prod_ident_10dcum = functions.set_path_filename_no_date(prod, in_prod_10dcum, native_mapset, version, ext)
#
#     input_dir_10dcum = es_constants.processing_dir+ \
#                 functions.set_path_sub_directory(prod, in_prod_10dcum, 'Derived', version, native_mapset)
#
#     starting_files_10dcum = input_dir_10dcum+"*"+in_prod_ident_10dcum
#
#     formatter_in="(?P<YYYYMMDD>[0-9]{8})[0-9]{4}"+in_prod_ident_10dcum
#     formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir_10dcum+"{YYYYMMDD[0]}"+out_prod_ident_10dcum]
#
#     @follows(lsasaf_etp_10d30min)
#     @active_if(activate_10dcum_comput)
#     @collate(starting_files_10dcum, formatter(formatter_in),formatter_out)
#     def lsasaf_etp_10dcum(input_file, output_file):
#
#         output_file = functions.list_to_element(output_file)
#         # Get the number of days of that dekad
#         basename=os.path.basename(output_file)
#         mydate=functions.get_date_from_path_filename(basename)
#         nbr_days_dekad = functions.day_per_dekad(mydate)
#         # Compute the correcting factor: we sum-up all 48 30min cycles and:
#         # Divide by 2 (mm/h -> mm)
#         # Multiply by number of days
#         # Divide by 100, so that the scale factor changes from 0.0001 (30min) to 0.01
#         factor = float(nbr_days_dekad)*0.005
#         functions.check_output_dir(os.path.dirname(output_file))
#
#         tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)
#
#         tmp_output_file = tmpdir+os.path.sep+os.path.basename(output_file)
#
#         args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF',
#                 "options": "compress=lzw", "scale_factor": factor, "input_nodata":-32768}
#
#         raster_image_math.do_cumulate(**args)
#
#         reproject_output(tmp_output_file, native_mapset, target_mapset)
#
#         shutil.rmtree(tmpdir)
#
#     # ----------------------------------------------------------------------------------------------------------------
#     # 1moncum
#     output_sprod=proc_lists.proc_add_subprod("1moncum", "lsasaf-et", final=False,
#                                              descriptive_name='1mon Cumulate',
#                                              description='Monthly Cumulate in mm',
#                                              frequency_id='e1month',
#                                              date_format='YYYYMMDD',
#                                              masked=False,
#                                              timeseries_role='',
#                                              active_default=True)
#     output_sprod='1moncum'
#     out_prod_ident_1moncum = functions.set_path_filename_no_date(prod, output_sprod, target_mapset, version, ext)
#     output_subdir_1moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, target_mapset)
#     #file d'entre
#     in_prod_1moncum='10dcum'
#     in_prod_ident_1moncum = functions.set_path_filename_no_date(prod, in_prod_1moncum, target_mapset, version, ext)
#     input_dir_1moncum = es_constants.processing_dir+ \
#                      functions.set_path_sub_directory(prod, in_prod_1moncum, 'Derived', version, target_mapset)
#
#     starting_files_1moncum = input_dir_1moncum+"*"+in_prod_ident_1moncum
#
#     formatter_in_1moncum="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident_1moncum
#     formatter_out_1moncum="{subpath[0][5]}"+os.path.sep+output_subdir_1moncum+"{YYYYMM[0]}"+'01'+out_prod_ident_1moncum
# #
#     @follows(lsasaf_etp_10dcum)
#     @active_if(activate_1moncum_comput)
#     @collate(starting_files_1moncum, formatter(formatter_in_1moncum),formatter_out_1moncum)
#     def lsasaf_etp_1moncum(input_file, output_file):
# #
#         output_file = functions.list_to_element(output_file)
#         functions.check_output_dir(os.path.dirname(output_file))
#         args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
#                 "options": "compress=lzw", "input_nodata":-32768}
#         raster_image_math.do_cumulate(**args)

    return proc_lists

def processing_std_lsasaf_lst(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, prod='', starting_sprod='', native_mapset='',
                             target_mapset='', version='',
                             starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_precip')

    proc_lists = None
    proc_lists = create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version,
                                 starting_dates=starting_dates, proc_lists=proc_lists)
    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_lsasaf_lst')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger)
        tasks = pipeline_get_task_names()
        spec_logger.info("After running the pipeline %s" % 'processing_std_precip')



    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True
