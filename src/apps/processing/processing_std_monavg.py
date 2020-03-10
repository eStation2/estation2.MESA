from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing service (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0 - Initial Version
#            1.1 - Modify monavg computation to skip current month (MOI request)
#

# Source my definitions
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
import os
import datetime
import glob
import calendar
import fnmatch

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from lib.python import metadata

# Import third-party modules
from ruffus import *

ext = es_constants.ES2_OUTFILE_EXTENSION


def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, logger=None):
    my_date = None

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    sds_meta = metadata.SdsMetadata()
    es2_data_dir = es_constants.es2globals['processing_dir'] + os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es2_data_dir + functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if my_date is not None:
        starting_files = input_dir + my_date + "*" + in_prod_ident
    else:
        starting_files = input_dir + "*" + in_prod_ident


    #   ---------------------------------------------------------------------
    #   Monthly Average for a given month

    output_sprod_group = proc_lists.proc_add_subprod_group("monstats")
    output_sprod = proc_lists.proc_add_subprod("monavg", "monstats", final=False,
                                               descriptive_name='Monthly average',
                                               description='Monthly average',
                                               frequency_id='',
                                               date_format='YYYMMMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMM>[0-9]{6})[0-9]{2}" + in_prod_ident
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYYMM[0]}" + '01' + out_prod_ident

    @collate(starting_files, formatter(formatter_in), formatter_out)
    def compute_monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        out_filename = os.path.basename(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        no_data = int(sds_meta.get_nodata_value(input_file[0]))

        str_date = out_filename[0:6]
        today = datetime.date.today()
        today_yyyymm = today.strftime('%Y%m')

        # expected_ndays=functions.get_number_days_month(str_date)
        # current_ndays=len(input_file)
        if str_date == today_yyyymm:
            logger.info('Do not perform computation for current month {0}. Skip'.format(str_date))
        else:
            args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "input_nodata": no_data,
                    "options": "compress=lzw"}
            raster_image_math.do_avg_image(**args)


    return proc_lists


#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_monavg(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                                starting_dates=None, write2file=None, logfile=None):
    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_monavg')

    history_file = os.path.join(es_constants.log_dir, '.ruffus_history_{0}_{1}.sqlite').format(prod, starting_sprod)
    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, logger=spec_logger)

    if write2file is not None:
        fwrite_id = open(write2file, 'w')
    else:
        fwrite_id = None

    spec_logger.info("Entering routine %s" % 'processing_monavg')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        # Option to be added to pipeline_run to force files to appear up-to-date: touch_files_only = True
        pipeline_run(verbose=pipeline_run_level, history_file=history_file, checksum_level=0, touch_files_only=False)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
