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
from future import standard_library
standard_library.install_aliases()
from config import es_constants
import os

# Import eStation2 modules
#from database import querydb
from lib.python import functions
from lib.python import metadata
from lib.python.image_proc import raster_image_math
from lib.python.image_proc import recode
from database import crud
from database import querydb
from lib.python import es_logging as log

# This is temporary .. to be replace with a DB call
from apps.processing.processing_switches import *

# Import third-party modules
from ruffus import *

logger = log.my_logger(__name__)

#   General definitions for this processing chain
prod="modis-sst"
mapset='MODIS-IOC-4km'
ext='.tif'
version='undefined'

#   switch wrt temporal resolution
activate_10d_comput=1

#   specific switch for each subproduct
# 1. 10d prod stats
activate_monavg_comput=0
activate_monclim_comput=1
activate_mondiff_comput=1


def create_pipeline(starting_sprod):
    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)
                
    starting_files = input_dir+"*"+in_prod_ident
    # Read input product nodata
    in_prod_info = querydb.get_product_out_info(productcode=prod, subproductcode=starting_sprod, version=version)  
    product_info = functions.list_to_element(in_prod_info)
    in_nodata = product_info.nodata
    
   #   ---------------------------------------------------------------------
   #   Monthly Average for a given month
    output_sprod="monavg"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+out_prod_ident]
   
    @active_if(activate_monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def modis_sst_monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
        "options": "compress=lzw", "input_nodata": in_nodata}
        raster_image_math.do_avg_image(**args)
 
    #   ---------------------------------------------------------------------
    #   Monthly Climatology for all years
    new_input_subprod='monavg'
    new_in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    new_input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(prod, new_input_subprod, 'Derived', version, mapset)

    new_starting_files = new_input_dir+"*"+new_in_prod_ident

    output_sprod="monclim"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="[0-9]{4}(?P<MM>[0-9]{2})"+new_in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MM[0]}"+out_prod_ident]

    @active_if(activate_monclim_comput)
    @collate(new_starting_files, formatter(formatter_in),formatter_out)
    def modis_sst_monclim(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
	    "options": "compress=lzw", "input_nodata": in_nodata}
        raster_image_math.do_avg_image(**args)
  
    
   #   ---------------------------------------------------------------------
   #   Monthly Anomaly for a given monthly    
    output_sprod="mondiff"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset,version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)    
    
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MM>[0-9]{2})"+new_in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MM[0]}"+out_prod_ident
        
    ancillary_sprod = "monclim"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset,version,ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MM[0]}"+ancillary_sprod_ident

    @active_if(activate_mondiff_comput)
    @transform(new_starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def modis_sst_mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)
        
#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_modis_sst(pipeline_run_level=0,pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    create_pipeline(starting_sprod='sst-day')

    logger.info("Entering routine %s" % 'processing_modis')
    if pipeline_run_level > 0:
        logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
