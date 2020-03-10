from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define a processing chain for 'modis-firms' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.05.2016
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0
#

# Source generic modules
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os, time, sys
import glob, datetime

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None,
                    update_stats=False, nrt_products=True):

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all off
    activate_10dstats_comput=0              # 10d stats
    activate_10danomalies_comput=0          # 10d anomalies

    #   switch wrt groups - according to options
    if nrt_products:
        activate_10dcount_comput=1          # 10d anomalies
        activate_10danomalies_comput=1      # monthly anomalies

    if update_stats:
        activate_10dstats_comput= 1         # 10d stats

    #   switch wrt single products: not to be changed !!
    activate_10dcount_comput=1              # 10d count

    activate_10dcountavg_comput=1
    activate_10dcountmin_comput=1
    activate_10dcountmax_comput=1

    activate_10ddiff_comput=1

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
    #   10dcount

    output_sprod_group=proc_lists.proc_add_subprod_group("10dcount")
    output_sprod=proc_lists.proc_add_subprod("10dcount", "10dcount", final=False,
                                             descriptive_name='10d Count',
                                             description='Fire Count for dekad',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident_10dcount = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_10dcount  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_10dcount():

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

                    output_file=es_constants.processing_dir+output_subdir_10dcount+os.path.sep+my_dekad_str+out_prod_ident_10dcount

                yield (file_list, output_file)

    @active_if(activate_10dcount_comput)
    @files(generate_parameters_10dcount)
    def std_precip_10dcount(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   10dcountavg

    starting_files_10dcount = es_constants.processing_dir+output_subdir_10dcount+"*"+out_prod_ident_10dcount

    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod=proc_lists.proc_add_subprod("10dcountavg", "10dstats", final=False,
                                             descriptive_name='10d Fire Average',
                                             description='Average fire for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+out_prod_ident_10dcount
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountavg_comput)
    @collate(starting_files_10dcount, formatter(formatter_in),formatter_out)
    def std_precip_10davg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   10dcountmin

    output_sprod=proc_lists.proc_add_subprod("10dcountmin", "10dstats", final=False,
                                             descriptive_name='10d Fire Minimum',
                                             description='Minimum Fire for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+out_prod_ident_10dcount
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountmin_comput)
    @collate(starting_files_10dcount, formatter(formatter_in),formatter_out)
    def std_precip_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   10dcountmax
    output_sprod=proc_lists.proc_add_subprod("10dcountmax", "10dstats", final=False,
                                             descriptive_name='10d Maximum',
                                             description='Maximum rainfall for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+out_prod_ident_10dcount
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountmax_comput)
    @collate(starting_files_10dcount, formatter(formatter_in),formatter_out)
    def std_precip_10dmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    # #   ---------------------------------------------------------------------
    # #   10dDiff
    # output_sprod_group=proc_lists.proc_add_subprod_group("10danomalies")
    # output_sprod=proc_lists.proc_add_subprod("10dcountdiff", "10danomalies", final=False,
    #                                          descriptive_name='10d Absolute Difference',
    #                                          description='10d Absolute Difference vs. LTA',
    #                                          frequency_id='e1dekad',
    #                                          date_format='YYYYMMDD',
    #                                          masked=False,
    #                                          timeseries_role='10d',
    #                                          active_default=True)
    # out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    #
    # #   Starting files + avg
    # formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    # formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident
    #
    # ancillary_sprod = "10davg"
    # ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    # ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    # ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident
    #
    # @follows(std_precip_10davg)
    # @active_if(activate_10danomalies_comput, activate_10ddiff_comput)
    # @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    # def std_precip_10ddiff(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
    #     raster_image_math.do_oper_subtraction(**args)

    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline


def processing_modis_firms(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, update_stats=False, nrt_products=True, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_firms')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, update_stats=update_stats, nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_modis_firms')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history.sqlite'))
        spec_logger.info("After running the pipeline %s" % 'processing_modis_firms')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True

def processing_modis_firms_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None):

    result = processing_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
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
                          logfile=logfile)

    return result


def processing_modis_firms_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None):

    result = processing_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
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
                          logfile=logfile)

    return result


def processing_modis_firms_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None):

    result = processing_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
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
                          logfile=logfile)

    return result

