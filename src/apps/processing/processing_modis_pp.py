#
#	purpose: Define the primary production processing chain (by using ruffus)
#	author:  B. Motah [& E. Martial]
#	date:	 25.03.2015
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0 - Initial Version
#

# Source my definitions
import os
import re

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

def create_pipeline(input_products, output_product, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_pp')

    #   ---------------------------------------------------------------------
    #   Create lists

    #my_date='20160601'
    my_date = ''
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

   #   ---------------------------------------------------------------------
   #    Parse the arguments and extract the 4 input variables
   #
    if len(input_products) <> 4:
        spec_logger.error('Modis PP computation requires 4 inputs. Exit')
        return 1

    found_chla = False
    found_sst = False
    found_par = False
    found_kd490 = False

    for input_product in input_products:

        if re.search('.*chla.*',input_product.productcode):
            found_chla = True
            chla_prod=input_product.productcode
            chla_version = input_product.version
            chla_sprod = input_product.subproductcode
            chla_mapset = input_product.mapsetcode
            chla_prod_ident = functions.set_path_filename_no_date(chla_prod, chla_sprod, chla_mapset, chla_version, ext)
            chla_input_dir = es2_data_dir+ \
                    functions.set_path_sub_directory(chla_prod, chla_sprod, 'Derived', chla_version, chla_mapset)


        if re.search('.*sst.*',input_product.productcode):
            found_sst = True
            sst_prod=input_product.productcode
            sst_version = input_product.version
            sst_sprod = input_product.subproductcode
            sst_mapset = input_product.mapsetcode
            sst_prod_ident = functions.set_path_filename_no_date(sst_prod, sst_sprod, sst_mapset, sst_version, ext)
            sst_input_dir = es2_data_dir+ \
                    functions.set_path_sub_directory(sst_prod, sst_sprod, 'Derived', sst_version, sst_mapset)

        if re.search('.*kd490.*',input_product.productcode):
            found_kd490 = True
            kd490_prod=input_product.productcode
            kd490_version = input_product.version
            kd490_sprod = input_product.subproductcode
            kd490_mapset = input_product.mapsetcode
            kd490_prod_ident = functions.set_path_filename_no_date(kd490_prod, kd490_sprod, kd490_mapset, kd490_version, ext)
            kd490_input_dir = es2_data_dir+ \
                    functions.set_path_sub_directory(kd490_prod, kd490_sprod, 'Derived', kd490_version, kd490_mapset)

        if re.search('.*par.*',input_product.productcode):
            found_par = True
            par_prod=input_product.productcode
            par_version = input_product.version
            par_sprod = input_product.subproductcode
            par_mapset = input_product.mapsetcode
            par_prod_ident = functions.set_path_filename_no_date(par_prod, par_sprod, par_mapset, par_version, ext)
            par_input_dir = es2_data_dir+ \
                    functions.set_path_sub_directory(par_prod, par_sprod, 'Derived', par_version, par_mapset)

    # Check consistency of inputs
    if not(found_chla) or not(found_kd490) or not(found_par) or not(found_sst):
        spec_logger.error('At least one of 4 expected inputs missing. Exit')
        return 1

    if chla_mapset <> sst_mapset or chla_mapset <> kd490_mapset or chla_mapset <> par_mapset:
        spec_logger.error('All 4 input mapset must be equals. Exit')
        return 1

    # Read input product nodata

    chla_prod_info = querydb.get_product_out_info(productcode=chla_prod, subproductcode=chla_sprod, version=chla_version)
    chla_product_info = functions.list_to_element(chla_prod_info)
    chla_nodata = chla_product_info.nodata

    sst_prod_info = querydb.get_product_out_info(productcode=sst_prod, subproductcode=sst_sprod, version=sst_version)
    sst_product_info = functions.list_to_element(sst_prod_info)
    sst_nodata = sst_product_info.nodata

    kd_prod_info = querydb.get_product_out_info(productcode=kd490_prod, subproductcode=kd490_sprod, version=kd490_version)
    kd_product_info = functions.list_to_element(kd_prod_info)
    kd_nodata = kd_product_info.nodata

    par_prod_info = querydb.get_product_out_info(productcode=par_prod, subproductcode=par_sprod, version=par_version)
    par_product_info = functions.list_to_element(par_prod_info)
    par_nodata = par_product_info.nodata

    # Define input files
    # if starting_dates is not None:
    #     starting_files = []
    #     for my_date in starting_dates:
    #         starting_files.append(input_dir+my_date+in_prod_ident)
    # else:
    #     starting_files=input_dir+"*"+in_prod_ident

    kd_files = kd490_input_dir+my_date+"*"+kd490_prod_ident

    # Define outputs

    output_prod=output_product[0].productcode
    output_sprod=output_product[0].subproductcode
    output_version=output_product[0].version
    output_mapset=output_product[0].mapsetcode

    out_prod_ident = functions.set_path_filename_no_date(output_prod, output_sprod, output_mapset,output_version, ext)
    output_subdir  = functions.set_path_sub_directory (output_prod, output_sprod, 'Derived', output_version, output_mapset)

    #   Starting files monthly composites
    formatter_kd="(?P<YYYYMMDD>[0-9]{8})"+kd490_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMMDD[0]}"+out_prod_ident

    ancillary_chla  = chla_input_dir+"{YYYYMMDD[0]}"+chla_prod_ident
    ancillary_par = par_input_dir+"{YYYYMMDD[0]}"+par_prod_ident
    ancillary_sst = sst_input_dir+"{YYYYMMDD[0]}"+sst_prod_ident

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

def processing_modis_pp(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, input_products='', output_product='',
                        write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_pp')

    create_pipeline(input_products, output_product, logfile=logfile)

    spec_logger.info("Entering routine %s" % 'processing modis - Primary Production')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file='/eStation2/log/.ruffus_history_modis_pp.sqlite', checksum_level=0)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
