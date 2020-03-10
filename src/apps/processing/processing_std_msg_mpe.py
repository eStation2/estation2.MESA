from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing service (by using ruffus)
#	author:  Olivier Thamba and Maixent Kambi 
#	date:	 20150318
#  	descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#   NOTE (to be included in doc):
#         a. Units: the grib product is in unit Kg/m2/sec (i.e. mmmm/sec)
#                   mpe product is in mm*100 (scale factor=0.01) over 15 min -> to be compared with EUM viewer multiply by 4 (15min -> hr)
#                   1dcum and 10dcum in mm*10 (scale factor=0.1)
#
# Source my definitions
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from config import es_constants
import os
import glob
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from apps.productmanagement.products import reproject_output
from lib.python import es_logging as log

# Import third-party modules
from ruffus import *
import datetime

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version, starting_dates=None, proc_lists=None, day_time=None, logger=None):

    # Test flag (to save non-projected cumulated products)
    test_mode = False

    # Create Logger
    # logger.fatal('Version 13.06.2017 !!!!!!!!!!!!!!!!!!!!!!!!!!')

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all ON
    activate_1dcum_comput=1
    activate_10dcum_comput=1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files ('mpe' subproduct)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, native_mapset, version, ext)

    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, native_mapset)

    # ----------------------------------------------------------------------------------------------------------------
    # 1dcum
    # Daily cumulate of the 15 min MPE, re-projected on target mapset
    output_sprod=proc_lists.proc_add_subprod("1dmax", "msg-mpe", final=False,
                                             descriptive_name='1d Cumulate',
                                             description='Daily Cumulate',
                                             frequency_id='e1day',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    output_sprod='1dcum'
    out_prod_ident_1dcum = functions.set_path_filename_no_date(prod, output_sprod, target_mapset, version, ext)
    output_subdir_1dcum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, target_mapset)

    # Use a specific function, to skip the current day
    def generate_parameters_1dcum():

        #   Look for all input files in input_dir, and sort them
        if starting_dates is not None:
            input_files = []
            for my_date in starting_dates:
                input_files.append(input_dir+my_date+in_prod_ident)
        else:
            starting_files=input_dir+"*"+in_prod_ident
            input_files = glob.glob(starting_files)

        logger.debug("starting_files %s" % input_files)

        day_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            if mydate_yyyymmdd not in day_list:
              day_list.append(mydate_yyyymmdd)

        day_list = sorted(day_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        for myday in day_list:
            # Exclude the current day
             if myday != today_str:
                file_list = []
                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    # Date is in format YYYYMMDDhhmm
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    if day_time is None:
                    # Append files for myday
                        if mydate_yyyymmdd[0:8] == myday:
                            file_list.append(input_file)
                    else:
                    # Append files in time range myday+hhmm |-| (myday+1)+ hhmm
                        if int(mydate_yyyymmdd) >= int(myday)*10000+int(day_time) and int(mydate_yyyymmdd) < (int(myday)+1)*10000+int(day_time):
                            file_list.append(input_file)

                output_file=es_constants.processing_dir+output_subdir_1dcum+os.path.sep+str((int(myday))*10000+int(day_time))+out_prod_ident_1dcum
                file_list = sorted(file_list)
                # Check here the number of missing files (for optimization)
                if len(file_list) > 86:
                    yield (file_list, output_file)
#
    @active_if(activate_1dcum_comput)
    @files(generate_parameters_1dcum)
    def msg_mpe_1dcum(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)

        tmp_output_file = tmpdir+os.path.sep+os.path.basename(output_file)
        # Divide by 10 to pass from 0.01 to 0.1 as scale factor for 1d cum
        factor = 0.1
        args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "scale_factor": factor, "input_nodata":-32768}

        raster_image_math.do_cumulate(**args)

        reproject_output(tmp_output_file, native_mapset, target_mapset)

        # Copy the non-reprojected file for validation, only in test_mode
        if test_mode:
            msg_proj_dir= es_constants.processing_dir+functions.set_path_sub_directory(prod, '1dcum', 'Derived', version, native_mapset)
            functions.check_output_dir(msg_proj_dir)
            shutil.copy(tmp_output_file, msg_proj_dir+os.path.sep)

        # Copy the non-reprojected file for validation, only in test_mode
        shutil.rmtree(tmpdir)


    # ----------------------------------------------------------------------------------------------------------------
    #   10 day Cumulate (mm)

    output_sprod=proc_lists.proc_add_subprod("10dcum", "msg-mpe", final=False,
                                             descriptive_name='10day Cumulate',
                                             description='10day Cumulate in mm',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident_10dcum = functions.set_path_filename_no_date(prod, "10dcum", target_mapset, version, ext)
    output_subdir_10dcum  = functions.set_path_sub_directory   (prod, "10dcum", 'Derived', version, target_mapset)

    in_prod_10dcum = '1dcum'
    in_prod_ident_10dcum = functions.set_path_filename_no_date(prod, in_prod_10dcum, target_mapset, version, ext)
    input_dir_10dcum = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, in_prod_10dcum, 'Derived', version, target_mapset)

    starting_files_10dcum = input_dir_10dcum+"*"+in_prod_ident_10dcum

    #   Define input files
    def generate_parameters_10dcum():

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files_10dcum)
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

                    output_file=es_constants.processing_dir+output_subdir_10dcum+os.path.sep+my_dekad_str+out_prod_ident_10dcum

                yield (file_list, output_file)

    @follows(msg_mpe_1dcum)
    @active_if(activate_10dcum_comput)
    @files(generate_parameters_10dcum)
    def msg_mpe_10dcum(input_file, output_file):

        if len(input_file) > 8:
            output_file = functions.list_to_element(output_file)
            # Get the number of days of that dekad
            basename=os.path.basename(output_file)
            mydate=functions.get_date_from_path_filename(basename)
            nbr_days_dekad = functions.day_per_dekad(mydate)
            factor = 1.0
            functions.check_output_dir(os.path.dirname(output_file))


            args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                    "options": "compress=lzw", "scale_factor": factor, "input_nodata":-32768}

            raster_image_math.do_cumulate(**args)

        else:
            logger.warning('More than 2 files missing for output {0}: Skip'.format(os.path.basename(output_file)))

    return proc_lists

def processing_std_msg_mpe(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, prod='', starting_sprod='', native_mapset='',
                             mapset='', version='',
                             starting_dates=None, write2file=None, logfile=None, day_time=None):

    native_mapset='MSG-satellite-3km'
    target_mapset=mapset

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_msg_mpe')

    if day_time is None:
        day_time = '0600'

    proc_lists = None
    proc_lists = create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, day_time=day_time, logger=spec_logger)
    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_msg_mpe')
        # Option to be added to pipeline_run to force files to appear up-to-date: touch_files_only = True
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_msg_mpe.sqlite'), checksum_level=0)
        tasks = pipeline_get_task_names()
        spec_logger.info("After running the pipeline %s" % 'processing_std_msg_mpe')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    return True
