from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define a 'generic' chain for computing yearly stats (LTS) and anomalies (?)
#	author:  M. Clerici
#	date:	 07.09.2018
#   descr:	 It will be used in a first place for the MODIS PP (see ES2-291, ES2-45), which is computed both
#            at 8days and 1mon frequency.
#            The approach is that the 'frequency' will be detected from the INPUT product, and the OUTPUT subproducts
#            named accordingly.
#            The currently computed products are: yearly-min, yearly-max, yearly-avg
#	history: 1.0 - Initial Version
#

# Source my definitions
from future import standard_library
standard_library.install_aliases()
import os
import re
import glob, datetime

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from database import querydb
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext = es_constants.ES2_OUTFILE_EXTENSION


def exclude_current_year(input_list):
    output_list = []
    today = datetime.date.today()
    current_year = today.strftime('%Y')

    for myfile in input_list:
        if os.path.basename(myfile)[0:4] != current_year:
            output_list.append(myfile)
    return output_list


def create_pipeline(input_products, logfile=None, nrt_products=True, update_stats=False):

    proc_lists = None

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_pp')

    # Set DEFAULTS: all off
    activate_pp_comput = 0              # PP from Chla, SST, Kd490 and PAR

    activate_stats_comput = 0           # Stats computation (inter-annual clim, min, max)
    activate_anomalies_comput = 0       # Anomalies computation (not yet done!!)

    #   switch wrt groups - according to options
    if nrt_products:
        activate_pp_comput = 1          # PP from Chla, SST, Kd490 and PAR

    if update_stats:
        activate_stats_comput = 1
        activate_anomalies_comput = 1

    activate_pp_prod_comput = 1
    activate_pp_stats_clim_comput = 0
    activate_pp_stats_min_comput = 0
    activate_pp_stats_max_comput = 0

    #   ---------------------------------------------------------------------
    #   Create lists

    # my_date='20160601'
    my_date = ''
    es2_data_dir = es_constants.es2globals['processing_dir'] + os.path.sep

    #   ---------------------------------------------------------------------
    #    Parse the arguments and extract the 4 input variables
    #
    if len(input_products) != 4:
        spec_logger.error('Modis PP computation requires 4 inputs. Exit')
        return 1

    found_chla = False
    found_sst = False
    found_par = False
    found_kd490 = False

    for input_product in input_products:

        if re.search('.*chla.*', input_product.productcode):
            found_chla = True
            chla_prod = input_product.productcode
            chla_version = input_product.version
            chla_sprod = input_product.subproductcode
            chla_mapset = input_product.mapsetcode
            chla_prod_ident = functions.set_path_filename_no_date(chla_prod, chla_sprod, chla_mapset, chla_version, ext)
            chla_input_dir = es2_data_dir + \
                             functions.set_path_sub_directory(chla_prod, chla_sprod, 'Derived', chla_version,
                                                              chla_mapset)

        if re.search('.*sst.*', input_product.productcode):
            found_sst = True
            sst_prod = input_product.productcode
            sst_version = input_product.version
            sst_sprod = input_product.subproductcode
            sst_mapset = input_product.mapsetcode
            sst_prod_ident = functions.set_path_filename_no_date(sst_prod, sst_sprod, sst_mapset, sst_version, ext)
            sst_input_dir = es2_data_dir + \
                            functions.set_path_sub_directory(sst_prod, sst_sprod, 'Derived', sst_version, sst_mapset)

        if re.search('.*kd490.*', input_product.productcode):
            found_kd490 = True
            kd490_prod = input_product.productcode
            kd490_version = input_product.version
            kd490_sprod = input_product.subproductcode
            kd490_mapset = input_product.mapsetcode
            kd490_prod_ident = functions.set_path_filename_no_date(kd490_prod, kd490_sprod, kd490_mapset, kd490_version,
                                                                   ext)
            kd490_input_dir = es2_data_dir + \
                              functions.set_path_sub_directory(kd490_prod, kd490_sprod, 'Derived', kd490_version,
                                                               kd490_mapset)

        if re.search('.*par.*', input_product.productcode):
            found_par = True
            par_prod = input_product.productcode
            par_version = input_product.version
            par_sprod = input_product.subproductcode
            par_mapset = input_product.mapsetcode
            par_prod_ident = functions.set_path_filename_no_date(par_prod, par_sprod, par_mapset, par_version, ext)
            par_input_dir = es2_data_dir + \
                            functions.set_path_sub_directory(par_prod, par_sprod, 'Derived', par_version, par_mapset)

    # Check consistency of inputs
    if not (found_chla) or not (found_kd490) or not (found_par) or not (found_sst):
        spec_logger.error('At least one of 4 expected inputs missing. Exit')
        return 1

    if chla_mapset != sst_mapset or chla_mapset != kd490_mapset or chla_mapset != par_mapset:
        spec_logger.error('All 4 input mapset must be equals. Exit')
        return 1

    # Read input product nodata

    chla_prod_info = querydb.get_product_out_info(productcode=chla_prod, subproductcode=chla_sprod,
                                                  version=chla_version)
    chla_product_info = functions.list_to_element(chla_prod_info)
    chla_nodata = chla_product_info.nodata

    sst_prod_info = querydb.get_product_out_info(productcode=sst_prod, subproductcode=sst_sprod, version=sst_version)
    sst_product_info = functions.list_to_element(sst_prod_info)
    sst_nodata = sst_product_info.nodata

    kd_prod_info = querydb.get_product_out_info(productcode=kd490_prod, subproductcode=kd490_sprod,
                                                version=kd490_version)
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

    # Define outputs

    output_nodata = -32767

    # Get the first output -> PP subproduct generated (8daysavg or monavg)
    output_prod = output_product[0].productcode
    output_sprod = output_product[0].subproductcode
    output_version = output_product[0].version
    output_mapset = output_product[0].mapsetcode

    out_prod_ident = functions.set_path_filename_no_date(output_prod, output_sprod, output_mapset, output_version, ext)
    output_subdir = functions.set_path_sub_directory(output_prod, output_sprod, 'Derived', output_version,
                                                     output_mapset)

    # Fixes ES2-36
    def generate_input_files_pp():

        # Take kd490 as starting point
        kd_files = kd490_input_dir + my_date + "*" + kd490_prod_ident
        input_files = sorted(glob.glob(kd_files))

        for input_file in input_files:
            basename = os.path.basename(input_file)
            mydate = functions.get_date_from_path_filename(basename)

            ancillary_chla = chla_input_dir + mydate + chla_prod_ident
            ancillary_par = par_input_dir + mydate + par_prod_ident
            ancillary_sst = sst_input_dir + mydate + sst_prod_ident

            do_comp = True
            if not os.path.isfile(ancillary_chla):
                do_comp = False
            if not os.path.isfile(ancillary_par):
                do_comp = False
            if not os.path.isfile(ancillary_sst):
                do_comp = False

            if do_comp is True:
                output_file = es_constants.processing_dir + output_subdir + os.path.sep + mydate + out_prod_ident
                my_inputs = (input_file, ancillary_chla, ancillary_par, ancillary_sst)
                yield (my_inputs, output_file)

    @active_if(activate_pp_comput)
    @files(generate_input_files_pp)
    def modis_pp_comp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"chla_file": input_file[1], "sst_file": input_file[3], "kd_file": input_file[0],
                "par_file": input_file[2], \
                "sst_nodata": sst_nodata, "kd_nodata": kd_nodata, "chla_nodata": chla_nodata, \
                "par_nodata": par_nodata, "output_file": output_file, "output_nodata": output_nodata,
                "output_format": 'GTIFF', \
                "output_type": None, "options": "compress=lzw"}
        raster_image_math.do_compute_primary_production(**args)

    #   ---------------------------------------------------------------------
    #   Climatology (inter-annual average)

    # prod = output_prod
    # mapset = output_mapset
    # new_input_subprod = output_sprod
    # version = output_version
    # in_prod_ident = functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    # in_prod_subdir = functions.set_path_sub_directory(prod, new_input_subprod, 'Derived', version, mapset)
    # starting_files = es2_data_dir + in_prod_subdir + "*" + in_prod_ident
    #
    # output_sprod_group = proc_lists.proc_add_subprod_group("monstat")
    # output_sprod = proc_lists.proc_add_subprod("1monavg", "monstat", final=False,
    #                                            descriptive_name='1 Month PP_LTA',
    #                                            description='Long Term Average for 1 Month MODIS Primary Production',
    #                                            frequency_id='e1month',
    #                                            date_format='MMDD',
    #                                            masked=False,
    #                                            timeseries_role='',
    #                                            active_default=True)
    # out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
    #
    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + in_prod_ident
    # formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]
    #
    # @follows(modis_pp_comp)
    # @active_if(activate_stats_comput, activate_pp_stats_clim_comput)
    # @collate(starting_files, formatter(formatter_in), formatter_out)
    # def std_precip_1monavg(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     reduced_list = exclude_current_year(input_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
    #             "options": "compress=lzw"}
    #     raster_image_math.do_avg_image(**args)
    #
    # #   ---------------------------------------------------------------------
    # #   Minimum
    # output_sprod = proc_lists.proc_add_subprod("1monmin", "monstat", final=False,
    #                                            descriptive_name='1 Month PP_LT Min',
    #                                            description='Long Term Minimum for 1 Month MODIS Primary Production',
    #                                            frequency_id='e1month',
    #                                            date_format='MMDD',
    #                                            masked=False,
    #                                            timeseries_role='',
    #                                            active_default=True)
    # out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
    #
    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + in_prod_ident
    # formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]
    #
    # @follows(modis_pp_comp)
    # @active_if(activate_stats_comput, activate_pp_stats_min_comput)
    # @collate(starting_files, formatter(formatter_in), formatter_out)
    # def std_precip_1monmin(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     reduced_list = exclude_current_year(input_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
    #             "options": "compress=lzw"}
    #     raster_image_math.do_min_image(**args)
    #
    # #   ---------------------------------------------------------------------
    # #   Monthly Maximum
    # output_sprod = proc_lists.proc_add_subprod("1monmax", "monstat", final=False,
    #                                            descriptive_name='1 Month PP_LT Max',
    #                                            description='Long Term Maximun for 1 Month MODIS Primary Production',
    #                                            frequency_id='e1month',
    #                                            date_format='MMDD',
    #                                            masked=False,
    #                                            timeseries_role='',
    #                                            active_default=True)
    # out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
    #
    # reg_ex_in = "[0-9]{4}([0-9]{4})" + in_prod_ident
    #
    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + in_prod_ident
    # formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]
    #
    # @follows(modis_pp_comp)
    # @active_if(activate_stats_comput, activate_pp_stats_max_comput)
    # @collate(starting_files, formatter(formatter_in), formatter_out)
    # def std_precip_1monmax(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     reduced_list = exclude_current_year(input_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
    #             "options": "compress=lzw"}
    #     raster_image_math.do_max_image(**args)


#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_modis_pp(res_queue, pipeline_run_level=0, pipeline_printout_level=0, pipeline_printout_graph_level=0,
                        input_products='', output_product='', write2file=None, logfile=None, nrt_products=True,
                        update_stats=False):
    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_pp')

    create_pipeline(input_products, output_product, logfile=logfile, nrt_products=nrt_products,
                    update_stats=update_stats)

    spec_logger.info("Entering routine %s" % 'processing modis - Primary Production')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_modis_pp.sqlite'), checksum_level=0)
    
    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')


# def processing_modis_pp_stats_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
#                                    pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
#                                    starting_dates=None, write2file=None, logfile=None, input_products='',
#                                    output_product=''):
#     result = processing_modis_pp(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  write2file=write2file,
#                                  logfile=logfile,
#                                  nrt_products=False,
#                                  update_stats=True,
#                                  input_products=input_products,
#                                  output_product=output_product
#                                  )
#
#     return result
#
#
# def processing_modis_pp_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
#                              pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
#                              starting_dates=None, write2file=None, logfile=None, input_products='', output_product=''):
#     result = processing_modis_pp(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  write2file=write2file,
#                                  logfile=logfile,
#                                  nrt_products=True,
#                                  update_stats=False,
#                                  input_products=input_products,
#                                  output_product=output_product
#                                  )
#
#     return result
#
#
# def processing_modis_pp_all(res_queue, pipeline_run_level=0, pipeline_printout_level=0, pipeline_printout_graph_level=0,
#                             prod='', starting_sprod='', mapset='', version='', starting_dates=None, write2file=None,
#                             logfile=None, input_products='', output_product=''):
#     result = processing_modis_pp(res_queue, pipeline_run_level=pipeline_run_level,
#                                  pipeline_printout_level=pipeline_printout_level,
#                                  pipeline_printout_graph_level=pipeline_printout_graph_level,
#                                  write2file=write2file,
#                                  logfile=logfile,
#                                  nrt_products=True,
#                                  update_stats=True,
#                                  input_products=input_products,
#                                  output_product=output_product
#                                  )
#
#     return result