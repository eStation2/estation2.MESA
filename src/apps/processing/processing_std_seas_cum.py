from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define a processing chain for 'precipitation-like' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0
#

# Source generic modules
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os, time, sys
import tempfile
import shutil
import glob

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from apps.processing import proc_functions

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, native_mapset, version, starting_dates=None, proc_lists=None,
                    logger=None, mapset=None):

    # Definitions
    start_season = '0901'
    end_season = '0421'
    agriculture_mask = '/data/temp/AGRIC_MASK.tif'

    # Manage mapset
    if mapset is None:
        mapset=native_mapset

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all off
    activate_seas_cum_comput=1          # season cumulation
    activate_cum_comput=1               # season cumulation

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
        starting_files=glob.glob(input_dir+"*"+in_prod_ident)

    #   ---------------------------------------------------------------------
    #   3.a NDVI linearx2 Season Cumulation masked using Crop Mask
    #   ---------------------------------------------------------------------
    # Define output subproduct
    out_sub_prod_name = 'seas-cum-of-'+starting_sprod
    output_sprod_group=proc_lists.proc_add_subprod_group("seas_cum_prods")
    output_sprod=proc_lists.proc_add_subprod(out_sub_prod_name, "seas_cum_prods", final=True,
                                             descriptive_name='Season Cumulation for '+out_sub_prod_name,
                                             description='Season Cumulation for '+out_sub_prod_name,
                                             frequency_id='e1year',
                                             date_format='YYYYMMDD',
                                             masked=True,
                                             timeseries_role='',
                                             active_default=True)

    # Generate prod_identifier (_fewsnet-rfe_seas-cum-of-10d_FEWSNET-Africa-8km_2.0.tif) ad subdir
    prod_ident_seas_cum = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_ident_seas_cum = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_seas_cum():

        starting_files.sort()
        # Convert from string to in (for comparison)
        dekad_start = int(start_season)
        dekad_end = int(end_season)

        # Loop over all input files
        for file_t0 in starting_files:
            # Get current date (in format '19980901')
            date_t0 = functions.get_date_from_path_full(file_t0)

            # Extract from date-string the dekad/year as integer
            dekad_t0 = int(date_t0[4:])
            year2 = int(date_t0[0:4])

            # Check if season goes across two years -> define year1/2
            if dekad_start < dekad_end:
                if dekad_t0 >= dekad_start and dekad_t0 <= dekad_end:
                    year1 = year2
            else:
                if dekad_t0 > dekad_start or dekad_t0 <= dekad_end:
                    year1 = year2 - 1

            # Detect the end of the season and trigger processing
            if dekad_t0 == dekad_end:

                # Define output filename
                output_file = es2_data_dir + subdir_ident_seas_cum + str(year2) + end_season + prod_ident_seas_cum

                # Get list of dates from start of season to end of season
                list_dates = proc_functions.get_list_dates_for_dataset(prod, starting_sprod, version,
                                                                       start_date=str(year1)+start_season, end_date=str(year2)+end_season)
                input_files = []
                missing_file=False
                for ldate in list_dates:
                    # Append the file to list if it exists ...
                    if os.path.isfile(input_dir+ldate+in_prod_ident):
                        input_files.append(input_dir+ldate+in_prod_ident)
                    # ... otherwise raise a warning and break
                    else:
                        logger.warning('Missing file for date {0}. Season not computed.'.format(ldate))
                        missing_file=True
                        break

                if not missing_file:
                    yield (input_files, output_file)

    @active_if(activate_seas_cum_comput)
    @files(generate_parameters_seas_cum)

    # Function to do actual computation from inputs to output
    def seas_cum(input_files, output_file):
        # Ensure out subdirectory exists
        functions.check_output_dir(os.path.dirname(output_file))

        # If output_file it is a list, force to a string
        output_file = functions.list_to_element(output_file)

        # Prepare temporary working directory for intermediate results
        tmpdirpath = tempfile.mkdtemp()
        # Cumulated but not masked output
        tmp_output_file = tmpdirpath + os.path.sep+os.path.basename(output_file)
        # Temp mask in the final projection (mapset)
        tmp_reproj_file = tmpdirpath + os.path.sep+'my_temp_reprojected_output.tif'

        # Call the function for cumulating
        args = {"input_file": input_files, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

        # Create from the original mask a new one, by using raster_image_math.do_reprojection()
        # and save it as a temporary mask

        # raster_image_math.do_reproject(agriculture_mask, tmp_reproj_file, 'SPOTV-SADC-1km', mapset)
        raster_image_math.do_reproject(tmp_output_file, tmp_reproj_file, native_mapset, mapset)

        # Call the function for masking
        args = {"input_file": tmp_reproj_file, "mask_file": agriculture_mask,
                "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "mask_value": 0, "out_value": 0}
        raster_image_math.do_mask_image(**args)

        # Remove temp directory
        shutil.rmtree(tmpdirpath)

    #   ---------------------------------------------------------------------
    #   3.a Season Cumulation fron start of season to current dekad till end of season
    #   ---------------------------------------------------------------------
    # Define output subproduct
    out_sub_prod_name = 'cum-of-' + starting_sprod
    output_sprod_group = proc_lists.proc_add_subprod_group("cum_prods")
    output_sprod = proc_lists.proc_add_subprod(out_sub_prod_name, "cum_prods", final=True,
                                               descriptive_name='Cumulation for ' + out_sub_prod_name,
                                               description='Cumulation for ' + out_sub_prod_name,
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    # Generate prod_identifier (_fewsnet-rfe_cum-of-10d_FEWSNET-Africa-8km_2.0.tif) ad subdir
    prod_ident_cum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_ident_cum = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_cum():

        starting_files.sort()
        # Convert from string to in (for comparison)
        dekad_start = int(start_season)
        dekad_end = int(end_season)

        # Loop over all input files
        for file_t0 in starting_files:
            # Get current date (in format '19980901')
            date_t0 = functions.get_date_from_path_full(file_t0)

            # Extract from date-string the dekad/year as integer
            dekad_t0 = int(date_t0[4:])
            year_t0 = int(date_t0[0:4])
            in_season = False

            # Check if season goes across two years -> define year1/2
            if dekad_start < dekad_end:
                if dekad_t0 >= dekad_start and dekad_t0 <= dekad_end:
                    year_sos = year_t0
                    in_season = True
            else:
                if dekad_t0 >= dekad_start:
                    year_sos = year_t0
                    in_season = True
                if dekad_t0 <= dekad_end:
                    year_sos = year_t0 - 1
                    in_season = True

            # Detect the end of the season and trigger processing
            if in_season:

                # Define output filename
                output_file = es2_data_dir + subdir_ident_cum + date_t0 + prod_ident_cum

                # Get list of dates from start of season to end of season
                list_dates = proc_functions.get_list_dates_for_dataset(prod, starting_sprod, version,
                                                                       start_date=str(year_sos) + start_season,
                                                                       end_date=date_t0)
                input_files = []
                missing_file = False
                for ldate in list_dates:
                    # Append the file to list if it exists ...
                    if os.path.isfile(input_dir + ldate + in_prod_ident):
                        input_files.append(input_dir + ldate + in_prod_ident)
                    # ... otherwise raise a warning and break
                    else:
                        logger.warning('Missing file for date {0}. Season not computed.'.format(ldate))
                        missing_file = True
                        break

                if not missing_file:
                    yield (input_files, output_file)

    @active_if(activate_cum_comput)
    @files(generate_parameters_cum)
    # Function to do actual computation from inputs to output
    def cum(input_files, output_file):
        # Ensure out subdirectory exists
        functions.check_output_dir(os.path.dirname(output_file))

        # If output_file it is a list, force to a string
        output_file = functions.list_to_element(output_file)

        # Prepare temporary working directory for intermediate results
        tmpdirpath = tempfile.mkdtemp()
        # Cumulated but not masked output
        tmp_output_file = tmpdirpath + os.path.sep + os.path.basename(output_file)

        # Call the function for cumulating
        args = {"input_file": input_files, "output_file": tmp_output_file, "output_format": 'GTIFF',
                "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

        # Create from the original mask a new one, by using raster_image_math.do_reprojection()
        # and save it as a temporary mask

        # raster_image_math.do_reproject(agriculture_mask, tmp_reproj_file, 'SPOTV-SADC-1km', mapset)
        raster_image_math.do_reproject(tmp_output_file, output_file, native_mapset, mapset)

        # Remove temp directory
        shutil.rmtree(tmpdirpath)


    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline


def processing_std_seas_cum(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', native_mapset='', version='',
                          mapset=None, starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_seas_cum')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, native_mapset=native_mapset, version=version,
                                 mapset=mapset, starting_dates=starting_dates, proc_lists=proc_lists, logger=spec_logger)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_precip')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history.sqlite'))
        tasks = pipeline_get_task_names()
        spec_logger.info("Run the pipeline %s" % tasks[0])
        spec_logger.info("After running the pipeline %s" % 'processing_std_precip')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    return True
