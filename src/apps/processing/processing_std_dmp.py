from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing chain for 'dmp-like' processing chains
#	author:  Vijay Charan Venkatachalam
#	date:	 01.08.2018
#   descr:	 Generate additional Derived products/implements processing chains
#	history: 1.0
#


# Import std modules
from builtins import open
from future import standard_library
standard_library.install_aliases()
import glob
import os
import tempfile
import shutil

# Import eStation2 modules
import datetime

from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from lib.python import metadata

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def exclude_current_year(input_list):

    output_list = []
    today = datetime.date.today()
    current_year = today.strftime('%Y')

    for myfile in input_list:
        if os.path.basename(myfile)[0:4] != current_year:
            output_list.append(myfile)
    return output_list

#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

# def create_pipeline(prod, starting_sprod, mapset, version, starting_dates_linearx2=None, proc_lists=None,
#                     update_stats=False, nrt_products=True):
def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None,
                    update_stats=False, nrt_products=True):

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    #   switch wrt groups - according to options

    # DEFAULT: ALL off

    activate_10dstats_comput=0          # 10d stats
    activate_10danomalies_comput=0      # 10d anomalies

    activate_monthly_comput=0           # monthly cumulation
    activate_monstats_comput=0          # monthly stats
    activate_monanomalies_comput=0      # monthly anomalies

    if nrt_products:
        activate_monthly_comput=0           # monthly cumulation
        activate_monanomalies_comput=0      # monthly anomalies
        activate_10danomalies_comput = 1               # 2.d


    if update_stats:
        activate_10dstats_comput=1          # 10d stats
        activate_monstats_comput=0          # monthly stats

    #   switch wrt single products: not to be changed !!
    activate_10davg_comput=1
    activate_10dmin_comput=1
    activate_10dmax_comput=1
    activate_10ddiff_comput=1
    activate_10dperc_comput=1
    activate_10dnp_comput=0
    activate_10dratio_comput=1

    activate_1moncum_comput=1
    activate_1monavg_comput=1
    activate_1monmin_comput=1
    activate_1monmax_comput=1
    activate_1mondiff_comput=1
    activate_1monperc_comput=1
    activate_1monnp_comput=1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    #logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   Average
    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod=proc_lists.proc_add_subprod("10davg", "10dstats", final=False,
                                             descriptive_name='10d Average',
                                             description='Average dry matter productivity for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10davg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_dmp_10davg(input_file, output_file):

        reduced_list = exclude_current_year(input_file)
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Minimum
    output_sprod=proc_lists.proc_add_subprod("10dmin", "10dstats", final=False,
                                             descriptive_name='10d Minimum',
                                             description='Minimum DMP for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_dmp_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Maximum
    output_sprod=proc_lists.proc_add_subprod("10dmax", "10dstats", final=False,
                                             descriptive_name='10d Maximum',
                                             description='Maximum DMP for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_dmp_10dmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   10dDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("10anomalies")
    output_sprod=proc_lists.proc_add_subprod("10ddiff", "10anomalies", final=False,
                                             descriptive_name='10d Absolute Difference',
                                             description='10d Absolute Difference vs. LTA',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @active_if(activate_10danomalies_comput, activate_10ddiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_dmp_10ddiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   10dperc
    output_sprod=proc_lists.proc_add_subprod("10dperc", "10anomalies",  final=False,
                                             descriptive_name='10d Percent Difference',
                                             description='10d Percent Difference vs. LTA',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_dmp_10davg)
    @active_if(activate_10danomalies_comput, activate_10dperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_dmp_10dperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   10dnp
    output_sprod=proc_lists.proc_add_subprod("10dnp", "10anomalies",  final=False,
                                             descriptive_name='10d Normalized Anomaly',
                                             description='10d Normalized Anomaly',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "10dmin"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmax"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, version, ext)
    ancillary_subdir_2      = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived',version, mapset)
    ancillary_input_2="{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @active_if(activate_10danomalies_comput, activate_10dnp_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    def std_dmp_10dnp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_make_vci(**args)

    #   ---------------------------------------------------------------------
    #   10dratio
    output_sprod=proc_lists.proc_add_subprod("10dratio", "10anomalies",  final=False,
                                             descriptive_name='10d Ratio',
                                             description='10d Ratio (curr/avg)',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "10davg"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    @active_if(activate_10danomalies_comput, activate_10dratio_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1), formatter_out)
    def std_dmp_10dratio(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)


    return proc_lists
#   ---------------------------------------------------------------------


#   Run the pipeline
def processing_std_dmp(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, update_stats=False, nrt_products=True, write2file=None, logfile=None, touch_only=False):
    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_dmp')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, update_stats=update_stats,
                                 nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id = open(write2file, 'w')
    else:
        fwrite_id = None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_dmp')
        pipeline_run(touch_files_only=touch_only, verbose=pipeline_run_level, logger=spec_logger,
                     log_exceptions=spec_logger,
                     history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod, starting_sprod))
        tasks = pipeline_get_task_names()
        spec_logger.info("Run the pipeline %s" % tasks[0])
        spec_logger.info("After running the pipeline %s" % 'processing_std_dmp')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id,
                          history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod, starting_sprod))

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    # res_queue.put(proc_lists)
    return True


def processing_std_dmp_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

    result = processing_std_dmp(res_queue, pipeline_run_level=pipeline_run_level,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          nrt_products=False,
                          update_stats=True,
                          write2file=write2file,
                          logfile=logfile,
                          touch_only=touch_only)

    return result

def processing_std_dmp_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

    result = processing_std_dmp(res_queue, pipeline_run_level=pipeline_run_level,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          nrt_products=True,
                          update_stats=False,
                          write2file=write2file,
                          logfile=logfile,
                          touch_only=touch_only)

    return result

def processing_std_dmp_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

    result = processing_std_dmp(res_queue, pipeline_run_level=pipeline_run_level,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          nrt_products=True,
                          update_stats=True,
                          write2file=write2file,
                          logfile=logfile,
                          touch_only=touch_only)

    return result
