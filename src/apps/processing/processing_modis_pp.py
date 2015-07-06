#
#	purpose: Define the primary production processing chain (by using ruffus)
#	author:  B. Motah [& E. Martial]
#	date:	 25.03.2015
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0
#

# Source my definitions
from config import es_constants
import os

# Import eStation2 modules

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
prod="modis-pp"
mapset='MODIS-IOC-4km'
ext='.tif'
version='undefined'

# Primary Production Monthly
activate_pp_1mon_comput=1


def create_pipeline(starting_sprod):

    #   ---------------------------------------------------------------------
    #   Define input files: Chla is the 'driver', sst,kd and par 'ancillary inputs'

    chla_prod="modis-chla"
    chla_prod_ident = functions.set_path_filename_no_date(chla_prod, starting_sprod, mapset, version, ext)
    chla_input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(chla_prod, starting_sprod, 'Derived', version, mapset)
                
    #chla_files = chla_input_dir+"2014*"+chla_prod_ident

    #   ---------------------------------------------------------------------
    sst_prod="modis-sst"
    sst_prod_ident = functions.set_path_filename_no_date(sst_prod, starting_sprod, mapset, version, ext)
    sst_input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(sst_prod, starting_sprod, 'Derived', version, mapset)

    #   ---------------------------------------------------------------------
    kd_prod="modis-kd490"
    kd_prod_ident = functions.set_path_filename_no_date(kd_prod, starting_sprod, mapset, version, ext)

    kd_input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(kd_prod, starting_sprod, 'Derived', version, mapset)

    kd_files = kd_input_dir+"*"+kd_prod_ident

    #   ---------------------------------------------------------------------
    par_prod="modis-par"
    par_prod_ident = functions.set_path_filename_no_date(par_prod, starting_sprod, mapset, version, ext)

    par_input_dir = es_constants.processing_dir+ \
                functions.set_path_sub_directory(par_prod, starting_sprod, 'Derived', version, mapset)

    # Read input product nodata

    chla_prod_info = querydb.get_product_out_info(productcode=chla_prod, subproductcode="chla-day", version=version)
    chla_product_info = functions.list_to_element(chla_prod_info)
    chla_nodata = chla_product_info.nodata

    sst_prod_info = querydb.get_product_out_info(productcode=sst_prod, subproductcode="sst-day", version=version)
    sst_product_info = functions.list_to_element(sst_prod_info)
    sst_nodata = sst_product_info.nodata

    kd_prod_info = querydb.get_product_out_info(productcode=kd_prod, subproductcode="kd490-day", version=version)
    kd_product_info = functions.list_to_element(kd_prod_info)
    kd_nodata = kd_product_info.nodata

    par_prod_info = querydb.get_product_out_info(productcode=par_prod, subproductcode="par-day", version=version)
    par_product_info = functions.list_to_element(par_prod_info)
    par_nodata = par_product_info.nodata

   #   ---------------------------------------------------------------------
   #   Monthly Primary Productivity from chl-a, sst, kd490 and par monthly data

    output_sprod="1mon"
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset,version, ext)
    output_subdir  = functions.set_path_sub_directory (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files monthly composites
    formatter_kd="(?P<YYYYMM>[0-9]{6})"+kd_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+out_prod_ident

    ancillary_sst = sst_input_dir+"{YYYYMM[0]}"+sst_prod_ident
    ancillary_par = par_input_dir+"{YYYYMM[0]}"+par_prod_ident
    ancillary_chla  = chla_input_dir+"{YYYYMM[0]}"+chla_prod_ident

    @active_if(activate_pp_1mon_comput)
    @transform(kd_files, formatter(formatter_kd), add_inputs(ancillary_chla, ancillary_par, ancillary_sst), formatter_out)
    def modis_pp_1mon(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"chla_file": input_file[1], "sst_file": input_file[3], "kd_file": input_file[0],"par_file": input_file[2], \
                "sst_nodata": sst_nodata, "kd_nodata": kd_nodata,\
                "par_nodata": par_nodata, "output_file": output_file, "output_nodata": -9999, "output_format": 'GTIFF',\
                "output_type": None, "options": "compress=lzw"}
        raster_image_math.do_compute_primary_production(**args)

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_modis_primary_production(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    create_pipeline(starting_sprod='monavg')

    logger.info("Entering routine %s" % 'processing modis - Primary Production')
    if pipeline_run_level > 0:
        logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
