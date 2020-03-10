from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Compute the rainfall onset
#	author:  M.Clerici, BDMS Staff
#	date:	 07.11.2016
#   descr:	 Computes the onset, only during the rainy season.
#	history: 1.0 - Initial Version
#

# Source my definitions
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import glob
# Import eStation2 modules

from lib.python import functions
from lib.python.image_proc import raster_image_math
from database import querydb
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

# Primary Production Monthly
activate_onset_comput=1

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None):

    # Definitions
    start_season = '0901'
    second_dekad = '0911'
    end_season = '0421'

    #   ---------------------------------------------------------------------
    #   Create lists

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files (10d)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, ext)
    input_dir = es2_data_dir+functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=glob.glob(input_dir+"*"+in_prod_ident)

    #   ---------------------------------------------------------------------
    #   Define output files (onset)

    output_sprod = proc_lists.proc_add_subprod("rain-onset", "none", final=False,
                                                descriptive_name='Rain Onset',
                                                description='Rainfall Start of the season',
                                                frequency_id='e1dekad',
                                                date_format='YYYYMMDD',
                                                masked=False,
                                                timeseries_role='',
                                                active_default=True)


    prod_ident_onset = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_onset = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_onset():

        starting_files.sort()

        for file_t0 in starting_files:
            # Get current date
            date_t0 = functions.get_date_from_path_full(file_t0)
            # Check if we are in the seasonal range [start < current <= end]
            dekad_t0 = int(date_t0[4:])
            dekad_start = int(start_season)
            dekad_second= int(second_dekad)
            dekad_end = int(end_season)

            # Initialize processing to 0
            do_proc=0
            in_season = False

            # Check we are within the season -> do_proc
            if dekad_start < dekad_end:
                if dekad_t0 > dekad_start and dekad_t0 <= dekad_end:
                    in_season = True
            else:
                if dekad_t0 > dekad_start or dekad_t0 <= dekad_end:
                    in_season = True
            if in_season and (dekad_t0 == dekad_second):
                do_proc = 1
            if in_season and (dekad_t0 != dekad_second):
                do_proc = 2

            if do_proc:

                output_file = es2_data_dir + subdir_onset + str(date_t0) + prod_ident_onset
                # Get files at t-1 and t-2 (if they exist)
                previous_files = functions.previous_files(file_t0)

                # Check if at least one previous file has been identified
                if do_proc == 1:

                    # Check at least 1 previous file exist
                    if len(previous_files) < 1:
                        print ('Error Case 1: no any previous file')
                    else:
                        # Pass two arguments (t0 and t0-1)
                        input_files = [file_t0, previous_files[0]]
                        yield (input_files, output_file)

                elif do_proc == 2:

                    error = False
                    # Check 2 previous files exist
                    if len(previous_files) < 2:
                        print ('Error Case 2: a previous file is missing')
                        error=True

                    # Look for previous output
                    previous_outputs = functions.previous_files(output_file)

                    if len(previous_outputs) < 1:
                        print ('Error Case 2: the previous output is missing')
                        error=True

                    # Pass four arguments (t0, t0-1, t0-2 and output-1)
                    if not error:
                        previous_output = previous_outputs[0]
                        if os.path.isfile(previous_output):
                            input_files = [file_t0, previous_files[0], previous_files[1], previous_output]
                            yield (input_files, output_file)

    @active_if(activate_onset_comput)
    @files(generate_parameters_onset)
    def rain_onset(input_files, output_file):
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        # Need to define the current_dekad number, wrt begin of season
        current_date=functions.get_date_from_path_full(output_file)
        current_dekad=current_date[4:]
        dekad_number = functions.dekad_nbr_in_season(current_dekad,start_season)

        # Call the function
        args = {"input_file": input_files, "output_file": output_file, 'input_nodata':None,
                'output_nodata':None, 'output_type':'Int16',
                "output_format": 'GTIFF', "options": "compress = lzw",
                'current_dekad':dekad_number}
        raster_image_math.do_rain_onset(**args)


#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_rain_onset(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                        starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_rain_onset')

    create_pipeline(prod, starting_sprod, mapset, version, starting_dates=starting_dates, proc_lists=None)

    spec_logger.info("Entering routine %s" % 'processing rain onset')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger,
                     log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_modis_pp.sqlite'),
                     checksum_level=0, one_second_per_job=True, multiprocess=1, multithread=0)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
