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
from apps.productmanagement.products import reproject_output
from lib.python import es_logging as log

# Import third-party modules
from ruffus import *
import datetime

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version, starting_dates=None, proc_lists=None):

    # Create Logger
    logger = log.my_logger('msg-mpe.log')
    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all ON
    activate_1dcum_comput=1

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
        input_files = glob.glob(starting_files)
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
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    if mydate_yyyymmdd[0:8] == myday:
                        file_list.append(input_file)

                output_file=es_constants.processing_dir+output_subdir_1dcum+os.path.sep+myday+out_prod_ident_1dcum
                file_list = sorted(file_list)
                yield (file_list, output_file)

#
    @active_if(activate_1dcum_comput)
    @files(generate_parameters_1dcum)
    def lsasaf_msg_mpe_1dmax(input_file, output_file):
#
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='',dir=es_constants.base_tmp_dir)

        tmp_output_file = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file": input_file, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata":-32768}

        raster_image_math.do_cumulate(**args)

        reproject_output(tmp_output_file, native_mapset, target_mapset)

        shutil.rmtree(tmpdir)

    return proc_lists

def processing_std_msg_mpe(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                             pipeline_printout_graph_level=0, prod='', starting_sprod='', native_mapset='',
                             mapset='', version='',
                             starting_dates=None, write2file=None, logfile=None):

    native_mapset='MSG-satellite-3km'
    target_mapset=mapset

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_msg_mpe')

    proc_lists = None
    proc_lists = create_pipeline(prod, starting_sprod, native_mapset, target_mapset, version,
                                 starting_dates=starting_dates, proc_lists=proc_lists)
    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_msg_mpe')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file='/eStation2/log/.ruffus_history.sqlite')
        tasks = pipeline_get_task_names()
        spec_logger.info("After running the pipeline %s" % 'processing_std_msg_mpe')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    return True
