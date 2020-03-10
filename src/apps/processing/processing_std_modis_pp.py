from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the primary production processing chain (by using ruffus)
#	author:  B. Motah [& E. Martial]
#	date:	 25.03.2015
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0 - Initial Version
#

# Source my definitions
from future import standard_library
standard_library.install_aliases()
import os

# Import eStation2 modules

from lib.python import functions
from lib.python.image_proc import raster_image_math
from database import querydb
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

# Primary Production Monthly
activate_pp_1mon_comput=1

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, nrt_products=True,
                    update_stats=False):

    #   ---------------------------------------------------------------------
    #   Create lists

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all off
    activate_pp_1mon_comput = 0  # 10d stats
    activate_10danomalies_comput = 0  # 10d anomalies

    activate_monthly_comput = 0  # monthly cumulation
    activate_monstats_comput = 0  # monthly stats
    activate_monanomalies_comput = 0  # monthly anomalies

    #   switch wrt groups - according to options
    if nrt_products:
        activate_pp_1mon_comput = 1  # Primary Production Monthly

        activate_monthly_comput = 1  # monthly cumulation
        activate_monanomalies_comput = 1  # monthly anomalies

    if update_stats:
        activate_pp_8dstats_comput = 1  # 10d stats
        activate_pp_monstats_comput = 1  # monthly stats

    # Primary Production Monthly
    # Always true
    #activate_pp_1mon_comput = 1

    #my_date='20160601'
    my_date = ''
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

   #   ---------------------------------------------------------------------
   #   Primary Productivity from chl-a, sst, kd490 and par data

   # Define inputs
    chla_prod=prod
    chla_version = 'v2013.1'
    chla_prod_ident = functions.set_path_filename_no_date(chla_prod, starting_sprod, mapset, chla_version, ext)
    chla_input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(chla_prod, starting_sprod, 'Derived', chla_version, mapset)
                
    #   ---------------------------------------------------------------------
    sst_prod="modis-sst"
    sst_version = 'v2013.1'
    sst_prod_ident = functions.set_path_filename_no_date(sst_prod, starting_sprod, mapset, sst_version, ext)
    sst_input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(sst_prod, starting_sprod, 'Derived', sst_version, mapset)

    #   ---------------------------------------------------------------------
    kd_prod="modis-kd490"
    kd_version = 'v2012.0'
    kd_prod_ident = functions.set_path_filename_no_date(kd_prod, starting_sprod, mapset, kd_version, ext)

    kd_input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(kd_prod, starting_sprod, 'Derived', kd_version, mapset)

    kd_files = kd_input_dir+my_date+"*"+kd_prod_ident

    #   ---------------------------------------------------------------------
    par_prod="modis-par"
    par_version = 'v2012.0'
    par_prod_ident = functions.set_path_filename_no_date(par_prod, starting_sprod, mapset, par_version, ext)

    par_input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(par_prod, starting_sprod, 'Derived', par_version, mapset)

    # Read input product nodata

    chla_prod_info = querydb.get_product_out_info(productcode=chla_prod, subproductcode="monavg", version=chla_version)
    chla_product_info = functions.list_to_element(chla_prod_info)
    chla_nodata = chla_product_info.nodata

    sst_prod_info = querydb.get_product_out_info(productcode=sst_prod, subproductcode="monavg", version=sst_version)
    sst_product_info = functions.list_to_element(sst_prod_info)
    sst_nodata = sst_product_info.nodata

    kd_prod_info = querydb.get_product_out_info(productcode=kd_prod, subproductcode="monavg", version=kd_version)
    kd_product_info = functions.list_to_element(kd_prod_info)
    kd_nodata = kd_product_info.nodata

    par_prod_info = querydb.get_product_out_info(productcode=par_prod, subproductcode="monavg", version=par_version)
    par_product_info = functions.list_to_element(par_prod_info)
    par_nodata = par_product_info.nodata

   #   Define outputs

    output_prod="modis-pp"
    output_sprod=starting_sprod
    out_prod_ident = functions.set_path_filename_no_date(output_prod, output_sprod, mapset,version, ext)
    output_subdir  = functions.set_path_sub_directory (output_prod, output_sprod, 'Derived', version, mapset)

    #   Starting files monthly composites
    formatter_kd="(?P<YYYYMMDD>[0-9]{8})"+kd_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMMDD[0]}"+out_prod_ident

    ancillary_sst = sst_input_dir+"{YYYYMMDD[0]}"+sst_prod_ident
    ancillary_par = par_input_dir+"{YYYYMMDD[0]}"+par_prod_ident
    ancillary_chla  = chla_input_dir+"{YYYYMMDD[0]}"+chla_prod_ident

    @active_if(activate_pp_1mon_comput)
    @transform(kd_files, formatter(formatter_kd), add_inputs(ancillary_chla, ancillary_par, ancillary_sst), formatter_out)
    def modis_pp_1mon(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"chla_file": input_file[1], "sst_file": input_file[3], "kd_file": input_file[0],"par_file": input_file[2], \
                "sst_nodata": sst_nodata, "kd_nodata": kd_nodata, "chla_nodata": chla_nodata,\
                "par_nodata": par_nodata, "output_file": output_file, "output_nodata": -9999, "output_format": 'GTIFF',\
                "output_type": None, "options": "compress=lzw"}
        raster_image_math.do_compute_primary_production(**args)

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_modis_pp(res_queue, pipeline_run_level=0, pipeline_printout_level=0, pipeline_printout_graph_level=0,
                            prod='', starting_sprod='', mapset='', version='', starting_dates=None, write2file=None,
                            logfile=None, nrt_products=True, update_stats=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_msg_mpe')

    create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, nrt_products=nrt_products, update_stats=update_stats)

    spec_logger.info("Entering routine %s" % 'processing modis - Primary Production')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_modis_pp.sqlite'), checksum_level=0)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    return True


def processing_std_modis_pp_stats_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                            pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                            starting_dates=None, write2file=None, logfile=None):

    result = processing_std_modis_pp(res_queue, pipeline_run_level=pipeline_run_level,
                                     pipeline_printout_level=pipeline_printout_level,
                                     pipeline_printout_graph_level=pipeline_printout_graph_level, prod=prod,
                                     starting_sprod=starting_sprod, mapset=mapset, version=version,
                                     starting_dates=starting_dates, write2file=write2file, logfile=logfile, nrt_products=False,update_stats=True)

    return result
