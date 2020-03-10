from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing service (by using ruffus)
#	author:  Olivier Thamba and Maixent Kambi 
#	date:	 20150318
#   	descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#            1.1 31/05/2016: create a specific .sqlite history file
#                            change the checksum_level = 0 (default is 1) so to check only output-files time.

# Source my definitions
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from config import es_constants
import os
import glob
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from apps.productmanagement.products import reproject_output
from apps.processing.proc_functions import remove_old_files
from lib.python import es_logging as log

# Import third-party modules
from ruffus import *
import datetime
import itertools

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version, starting_dates=None, proc_lists=None):

    # Create Logger
    logger = log.my_logger('log.lst')
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
    #   Define input files ('lst' subproduct)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, native_mapset, version, ext)

    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, native_mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    logger.info("starting_files %s" % starting_files)

    # ----------------------------------------------------------------------------------------------------------------
    # 1dmax
    # Daily maximum from 15min lst, re-projected on target mapset
    output_sprod=proc_lists.proc_add_subprod("1dmax", "lsasaf-lst", final=False,
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

    formatter_in_1dmax="(?P<YYYYMMDD>[0-9]{8})[0-9]{4}"+in_prod_ident
    formatter_out_1dmax="{subpath[0][5]}"+os.path.sep+output_subdir_1dmax+"{YYYYMMDD[0]}"+out_prod_ident_1dmax
#
    @active_if(activate_1dmax_comput)
    @collate(starting_files, formatter(formatter_in_1dmax),formatter_out_1dmax)
    def lsasaf_lst_1dmax(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)

        tmp_output_file = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-32768}

        raster_image_math.do_max_image(**args)

        reproject_output(tmp_output_file, native_mapset, target_mapset)

        shutil.rmtree(tmpdir)

    # ----------------------------------------------------------------------------------------------------------------
    # 10dmax
    # 10 Day maximum from daily max, on target mapset
    output_sprod=proc_lists.proc_add_subprod("10dmax", "lsasaf-lst", final=False,
                                             descriptive_name='10d Maximum',
                                             description='10d Maximum',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    output_sprod_10dmax='10dmax'
    out_prod_ident_10dmax = functions.set_path_filename_no_date(prod, output_sprod_10dmax, target_mapset, version, ext)
    output_subdir_10dmax  = functions.set_path_sub_directory   (prod, output_sprod_10dmax, 'Derived', version, target_mapset)

    # #   Define input files
    in_prod_10dmax = '1dmax'
    in_prod_ident_10dmax = functions.set_path_filename_no_date(prod, in_prod_10dmax, target_mapset, version, ext)
    #
    input_dir_10dmax = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, in_prod_10dmax, 'Derived', version, target_mapset)
    #
    starting_files_10dmax = input_dir_10dmax+"*"+in_prod_ident_10dmax

    #
    def generate_parameters_10dmax():

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files_10dmax)
        dekad_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
            if mydekad_nbr not in dekad_list:
              dekad_list.append(mydekad_nbr)

        dekad_list = sorted(dekad_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        for dekad in dekad_list:
            # Exclude the current dekad
             if dekad != dekad_now:
                file_list = []
                my_dekad_str = functions.conv_dekad_2_date(dekad)
                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+output_subdir_10dmax+os.path.sep+my_dekad_str+out_prod_ident_10dmax

                yield (file_list, output_file)

#
    @active_if(activate_10dmax_comput)
    @files(generate_parameters_10dmax)
    def lsasaf_lst_10dmax(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-32768}

        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   Dekad maximum for every 15min
    #   NOTE: this product is compute w/o re-projection, i.e. on the 'native' mapset

    output_sprod=proc_lists.proc_add_subprod("10d15min", "lsasaf-lst", final=False,
                                             descriptive_name='10day Maximum over 15 min',
                                             description='10day Maximum computed for every 15 min',
                                             frequency_id='e15minute', # Is it OK ???????
                                             date_format='YYYYMMDDHHMM',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, native_mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, native_mapset)

    def generate_parameters_10d15min():

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files)
        dekad_list = []
        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
            if mydekad_nbr not in dekad_list:
              dekad_list.append(mydekad_nbr)

        dekad_list = sorted(dekad_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        # Generate the list of 30 min time in a day
        timelist = [datetime.time(h,m).strftime("%H%M") for h,m in itertools.product(range(0,24),range(0,60,15))]

        for time in timelist:
            files_for_time = glob.glob(input_dir+os.path.sep+'*'+time+in_prod_ident)
            for dekad in dekad_list:
                # Exclude the current dekad
                if dekad != dekad_now:
                    file_list = []
                    my_dekad_str = functions.conv_dekad_2_date(dekad)
                    output_file=es_constants.processing_dir+output_subdir+os.path.sep+my_dekad_str+time+out_prod_ident

                    for myfile in files_for_time:
                        basename=os.path.basename(myfile)
                        mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                        mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                        if mydekad_nbr == dekad:
                            file_list.append(myfile)
                    if len(file_list)> 8:
                        yield (file_list, output_file)

    @active_if(activate_10d15min_comput)
    @files(generate_parameters_10d15min)
    def lsasaf_lst_10d15min(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
                "options": "compress=lzw", "input_nodata":-32768}

        raster_image_math.do_max_image(**args)

        # Do also the house-keeping, by deleting the files older than 6 months
        number_months_keep = 6
        remove_old_files(prod, starting_sprod, version, native_mapset, 'Ingest', number_months_keep)

    # ----------------------------------------------------------------------------------------------------------------
    #   10 day minimum (mm)
    #   NOTE: this product is compute with re-projection, i.e. on the 'target' mapset

    output_sprod=proc_lists.proc_add_subprod("10dmin", "lsasaf-et", final=False,
                                             descriptive_name='10day Minimum',
                                             description='10day minimum',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    out_prod_ident_10dmin = functions.set_path_filename_no_date(prod, "10dmin", target_mapset, version, ext)
    output_subdir_10dmin  = functions.set_path_sub_directory   (prod, "10dmin", 'Derived', version, target_mapset)

    #   Define input files
    in_prod_10dmin = '10d15min'
    in_prod_ident_10dmin = functions.set_path_filename_no_date(prod, in_prod_10dmin, native_mapset, version, ext)

    input_dir_10dmin = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, in_prod_10dmin, 'Derived', version, native_mapset)

    starting_files_10dmin = input_dir_10dmin+"*"+in_prod_ident_10dmin

    formatter_in="(?P<YYYYMMDD>[0-9]{8})[0-9]{4}"+in_prod_ident_10dmin
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir_10dmin+"{YYYYMMDD[0]}"+out_prod_ident_10dmin]

    @follows(lsasaf_lst_10d15min)
    @active_if(activate_10dmin_comput)
    @collate(starting_files_10dmin, formatter(formatter_in),formatter_out)
    def lsasaf_lst_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        # Get the number of days of that dekad
        basename=os.path.basename(output_file)
        mydate=functions.get_date_from_path_filename(basename)
        functions.check_output_dir(os.path.dirname(output_file))

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)

        tmp_output_file = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-32768}

        raster_image_math.do_min_image(**args)

        reproject_output(tmp_output_file, native_mapset, target_mapset)

        shutil.rmtree(tmpdir)

        # Do also the house-keeping, by deleting the files older than 6 months
        number_months_keep = 6
        remove_old_files(prod, '10d15min', version, native_mapset, 'Ingest', number_months_keep)

    return proc_lists

def processing_std_lsasaf_lst(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, prod='', starting_sprod='', native_mapset='',
                             mapset='', version='',
                             starting_dates=None, write2file=None, logfile=None):

    native_mapset='MSG-satellite-3km'
    target_mapset=mapset

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_lsasaf_lst')

    proc_lists = None
    proc_lists = create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version,
                                 starting_dates=starting_dates, proc_lists=proc_lists)
    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_lsasaf_lst')
        # Option to be added to pipeline_run to force files to appear up-to-date: touch_files_only = True
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_lsasaf_lst.sqlite'), checksum_level=0) #Pierluigi modificato path
        tasks = pipeline_get_task_names()
        spec_logger.info("After running the pipeline %s" % 'processing_std_lsasaf_lst')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_lsasaf_lst.sqlite'), checksum_level=0) # Pierluigi fixed path for history file
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    return True
