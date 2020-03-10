from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing service (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#

# Source my definitions
from builtins import open
from future import standard_library
standard_library.install_aliases()
import os

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None):

    my_date=None

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # 1. 10d prod stats
    activate_monavg_comput=1
    activate_monclim_comput=1
    activate_monanom_comput=0

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)
                
    if my_date is not None:
        starting_files = input_dir+my_date+"*"+in_prod_ident
    else:
        starting_files = input_dir+"*"+in_prod_ident

   #   ---------------------------------------------------------------------
   #   Monthly Average for a given month

    output_sprod_group=proc_lists.proc_add_subprod_group("monstats")
    output_sprod=proc_lists.proc_add_subprod("monavg", "monstats", final=False,
                                             descriptive_name='Monthly average',
                                             description='Chla Monthly average',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+out_prod_ident]
   
    @active_if(activate_monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def modis_chla_monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        out_filename=os.path.basename(output_file)
        str_date=out_filename[0:6]
        expected_ndays=functions.get_number_days_month(str_date)
        functions.check_output_dir(os.path.dirname(output_file))
        current_ndays=len(input_file)

        # if expected_ndays != current_ndays:
        #     logger.info('Missing days for period: %s. Skip' % str_date)
        # else:
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)
 
    #   ---------------------------------------------------------------------
    #   Monthly Climatology for all years

    output_sprod=proc_lists.proc_add_subprod("monclim", "monstats", final=False,
                                             descriptive_name='Monthly climatology',
                                             description='Chla Monthly climatology',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    new_input_subprod='monavg'
    new_in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    new_input_dir = es2_data_dir+functions.set_path_sub_directory(prod, new_input_subprod, 'Derived', version, mapset)

    new_starting_files = new_input_dir+"*"+new_in_prod_ident

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="[0-9]{4}(?P<MM>[0-9]{2})"+new_in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MM[0]}"+out_prod_ident]

    @active_if(activate_monclim_comput)
    @collate(new_starting_files, formatter(formatter_in),formatter_out)
    def modis_chla_monclim(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
	    "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)
  
    
   #   ---------------------------------------------------------------------
   #   Monthly Anomaly for a given monthly    
    output_sprod=proc_lists.proc_add_subprod("monanom", "monstats", final=False,
                                             descriptive_name='Monthly anomaly',
                                             description='Chla Monthly anomaly',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset,version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)    
    
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MM>[0-9]{2})"+new_in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MM[0]}"+out_prod_ident
        
    ancillary_sprod = "monclim"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset,version,ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MM[0]}"+ancillary_sprod_ident

    @active_if(activate_monanom_comput)
    @transform(new_starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def modis_chla_mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    return proc_lists

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_modis_chla(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, write2file=None, logfile=None):


    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_fronts')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    spec_logger.info("Entering routine %s" % 'processing_modis')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    #return list_subprods, list_subprod_groups
