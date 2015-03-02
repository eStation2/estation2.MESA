#
#	purpose: Define a processing chain for 'precipitation-like' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0
#
#   Still to be done
#   TODO-M.C.: more checks on the IN/OUT
#   TODO-M.C.test: Add a mechanism to extract/visualize the 'status' -> pipeline_printout(verbose=3)+grep-like function ?
#   TODO-M.C.test: find a robust method to solve the tuple/string issue in filename (fttb: return_as_element_of_list() ?)
#

# Source generic modules
import os, sys

# Import eStation2 modules
from lib.python import functions
#from lib.python import metadata
from lib.python.image_proc import raster_image_math
#from lib.python.image_proc import recode
#from database import crud
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

logger = log.my_logger(__name__)

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, list_subprods=None, update_stats=False):

    #   ---------------------------------------------------------------------
    #   Create lists

    proc_lists = functions.ProcLists()

    if list_subprods is not None:
        list_subprods = proc_lists.list_subprods
        list_subprod_groups = proc_lists.list_subprod_groups
    
    #   switch wrt groups - according to options
    if not update_stats:
        activate_10danomalies_comput=1      # 10d anomalies
        activate_monthly_comput=1           # monthly cumulation
        activate_monanomalies_comput=1      # monthly anomalies
        activate_10dstats_comput=0          # 10d stats
        activate_monstats_comput=0          # 1mon stats
    else:
        activate_10danomalies_comput=0      # 10d anomalies
        activate_monthly_comput=0           # monthly cumulation
        activate_monanomalies_comput=0      # monthly anomalies
        activate_10dstats_comput=1          # 1.
        activate_monstats_comput=1          # 3.b

    #   switch wrt single products: not to be changed !!
    activate_10davg_comput=1
    activate_10dmin_comput=1
    activate_10dmax_comput=1
    activate_10ddiff_comput=1
    activate_10dperc_comput=1
    activate_10dnp_comput=1

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

    logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    logger.debug('Input data directory is: %s' % input_dir)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    logger.debug('Starting files wild card is: %s' % starting_files)

    #   ---------------------------------------------------------------------
    #   Average
    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod=proc_lists.proc_add_subprod("10davg", "10dstats", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10davg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10davg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Minimum
    output_sprod=proc_lists.proc_add_subprod("10dmin", "10dstats", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Maximum
    output_sprod=proc_lists.proc_add_subprod("10dmax", "10dstats", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10dmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   10dDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("10anomalies")
    output_sprod=proc_lists.proc_add_subprod("10ddiff", "10anomalies", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_10davg)
    @active_if(activate_10danomalies_comput, activate_10ddiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_10ddiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   10dperc
    output_sprod=proc_lists.proc_add_subprod("10dperc", "10anomalies", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "10davg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_10davg)
    @active_if(activate_10danomalies_comput, activate_10dperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_10dperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   10dnp
    output_sprod=proc_lists.proc_add_subprod("10dnp", "10anomalies", False, True)
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

    @follows(std_precip_10dmin, std_precip_10dmax)
    @active_if(activate_10danomalies_comput, activate_10dnp_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    def std_precip_10dnp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_make_vci(**args)

    #   ---------------------------------------------------------------------
    #   1moncum
    output_sprod_group=proc_lists.proc_add_subprod_group("monthly")
    output_sprod=proc_lists.proc_add_subprod("1moncum", "monthly", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs: files from same months
    formatter_in="(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+'01'+out_prod_ident

    # @follows(std_precip_10davg)
    @active_if(activate_monthly_comput, activate_1moncum_comput)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    def std_precip_1moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Average
    new_input_subprod='1moncum'
    in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    output_sprod_group=proc_lists.proc_add_subprod_group("monstat")
    output_sprod=proc_lists.proc_add_subprod("1monavg", "monstat", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monavg_comput)
    @collate(std_precip_1moncum, formatter(formatter_in),formatter_out)
    def std_precip_1monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Minimum
    output_sprod=proc_lists.proc_add_subprod("1monmin", "monstat", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monmin_comput)
    @collate(std_precip_1moncum, formatter(formatter_in),formatter_out)
    def std_precip_1monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Maximum
    output_sprod=proc_lists.proc_add_subprod("1monmax", "monstat", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monmax_comput)
    @collate(std_precip_1moncum, formatter(formatter_in),formatter_out)
    def std_precip_1monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   1monDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("monanomalies")
    output_sprod=proc_lists.proc_add_subprod("1mondiff", "monanomalies", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_1monavg)
    @active_if(activate_monanomalies_comput, activate_1mondiff_comput)
    @transform(std_precip_1moncum, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_1mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   1monperc
    output_sprod=proc_lists.proc_add_subprod("1monperc", "monanomalies", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_1monavg)
    @active_if(activate_monanomalies_comput, activate_1monperc_comput)
    @transform(std_precip_1moncum, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_1monperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   1monnp
    output_sprod=proc_lists.proc_add_subprod("1monnp", "monanomalies", False, True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "1monmin"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "1monmax"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, version, ext)
    ancillary_subdir_2      = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived',version, mapset)
    ancillary_input_2="{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @follows(std_precip_1monmin, std_precip_1monmax)
    @active_if(activate_monanomalies_comput, activate_1monnp_comput)
    @transform(std_precip_1moncum, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    def std_precip_1monnp(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_make_vci(**args)

    #   ---------------------------------------------------------------------
        #   Upsert in the DB table a product generated by ruffus

    # def upsert_processed_ruffus(file_fullpath):
    #
    #         # -------------------------------------------------------------------------
    #         # Upsert into DB table 'products_data'
    #         # -------------------------------------------------------------------------
    #
    #         filename = os.path.basename(file_fullpath)
    #         dirname = os.path.dirname(file_fullpath)
    #
    #         # TODO-M.C.: add tests, try/except
    #         [productcode, subproductcode, version, mapsetcode] = functions.get_from_path_dir(dirname)
    #         str_date = functions.get_date_from_path_filename(filename)
    #         [str_year, str_month, str_day, str_hour] = functions.extract_from_date(str_date)
    #
    #         if str_year == '':
    #             str_year='0'
    #         cruddb = crud.CrudDB()
    #         recordkey = {'productcode': productcode.lower(),
    #                      'subproductcode': subproductcode.lower(),
    #                      'version': 'undefined',
    #                      'mapsetcode': mapsetcode,
    #                      'product_datetime': str_date}
    #
    #
    #         record = {'productcode': productcode.lower(),
    #                   'subproductcode': subproductcode.lower(),
    #                   'version': 'undefined',
    #                   'mapsetcode': mapsetcode,
    #                   'product_datetime': str_date,
    #                   'directory': dirname,
    #                   'filename': filename,
    #                   'year': int(str_year),
    #                   'month': int(str_month),
    #                   'day': int(str_day),
    #                   'hour': int(str_hour),
    #                   'file_role': 'active',
    #                   'file_type': 'GTiff'}
    #
    #         if len(cruddb.read('products.products_data', **recordkey)) > 0:
    #             logger.debug('Updating products_data record: ' + str(recordkey))
    #             cruddb.update('products.products_data', record)
    #         else:
    #             logger.debug('Creating products_data record: ' + str(recordkey))
    #             cruddb.create('products.products_data', record)

#   ---------------------------------------------------------------------
#   Run the pipeline


def processing_std_precip(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, update_stats=False):

    global list_subprods, list_subprod_groups

    list_subprods = []
    list_subprod_groups = []
    create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                    starting_dates=starting_dates, update_stats=update_stats)

    logger.info("Entering routine %s" % 'processing_std_precip')
    logger.info("pipeline_run_level %i" % pipeline_run_level)
    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    return list_subprods, list_subprod_groups

def processing_std_precip_stats(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None):

    processing_std_precip(pipeline_run_level=pipeline_run_level,
                          pipeline_run_touch_only=pipeline_run_touch_only,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          update_stats=True)

def get_subprods_std_precip():

    pid = os.fork()
    if pid == 0:
        # Qui sono il figlio
        [list_subprods, list_subprod_groups]  = processing_std_precip(pipeline_run_level=0,pipeline_run_touch_only=0,
                          pipeline_printout_level=0, pipeline_printout_graph_level=0,
                          prod='', starting_sprod='', mapset='', version='')

        return list_subprods, list_subprod_groups
        sys.exit(0)
    else:
        # Qui sono il padre
        os.wait()

