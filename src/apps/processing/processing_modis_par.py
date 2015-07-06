#
#	purpose: Define the processing service (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#

# Source my definitions
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
prod="modis-par"
mapset='MODIS-IOC-4km'
ext='.tif'
version='undefined'

#   specific switch for each subproduct
# 1. Prod stats
activate_monavg_comput=1
activate_monclim_comput=0
activate_monanom_comput=0


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
    
    print in_nodata
    
   #   ---------------------------------------------------------------------
   #   Monthly Average for a given month
    output_sprod="monavg"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+out_prod_ident]
   
    @active_if(activate_monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def modis_par_monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
        "options": "compress=lzw", "input_nodata": in_nodata}
        raster_image_math.do_avg_image(**args)
 

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_modis_par(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    create_pipeline(starting_sprod='par-day')

    logger.info("Entering routine %s" % 'processing_modis par-day')
    if pipeline_run_level > 0:
        logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
