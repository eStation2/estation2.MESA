#
#	purpose: Define the processing chain for 'ndvi-like' processing chains
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.01.2015
#   descr:	 Generate additional Derived products /implements processing chains
#	history: 1.0
#

# Import std modules
import glob
import os, sys

# Import eStation2 modules
#from database import querydb
from lib.python import functions
from lib.python import metadata
from lib.python.image_proc import raster_image_math
from database import crud
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

logger = log.my_logger(__name__)

#   Still to be done

#   General definitions for this processing chain
#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION
multiprocess = 0
#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, list_subprods=None,
                    update_stats=False, nrt_products=True):

    #   ---------------------------------------------------------------------
    #   Create lists
    proc_lists = functions.ProcLists()
    if list_subprods is not None:
        list_subprods = proc_lists.list_subprods
        list_subprod_groups = proc_lists.list_subprod_groups


# # switch for 'final' products (e.g. products to be controlled by the User)
    # final_ndvi_linearx2=0
    # final_diff_linearx2=0
    # final_linearx2diff_linearx2=0
    # final_vci=0
    # final_icn=0
    # final_vci_linearx2=0
    # final_icn_linearx2=0

    #   switch wrt groups - according to options

    # DEFAULT: ALL off
    group_no_filter_stats = 0                  # 1.a
    group_no_filter_anomalies = 0              # 1.b    -> To be done

    group_filtered_prods = 0                   # 2.a
    group_filtered_stats = 0                   # 2.b
    group_filtered_masks = 0                   # 2.c
    group_filtered_anomalies = 0               # 2.d

    group_monthly_prods = 0                    # 3.a
    group_monthly_stats = 0                    # 3.b
    group_monthly_masks = 0                    # 3.c
    group_monthly_anomalies = 0                # 3.d

    if nrt_products:
        group_no_filter_anomalies = 0              # 1.b    -> no relevant - FTTB
        group_filtered_prods = 1                   # 2.a
        group_filtered_masks = 1                   # 2.c
        group_filtered_anomalies = 1               # 2.d
        group_monthly_prods = 0                    # 3.a
        group_monthly_masks = 0                    # 3.c
        group_monthly_anomalies = 0                # 3.d    # To be done

    if update_stats:
        group_no_filter_stats = 0                  # 1.a    -> no relevant - FTTB
        group_filtered_stats = 1                   # 2.b
        group_monthly_stats = 0                    # 3.b

    #   switch wrt single products: not to be changed !!
    #   for Group 1.a (ndvi_no_filter_stats)
    activate_10davg_no_filter = 1
    activate_10dmin_no_filter = 1
    activate_10dmax_no_filter = 1
    activate_10dmed_no_filter = 1
    activate_10dstd_no_filter = 0              # TBDone

    #   for Group 1.b (ndvi_no_filter_anom)

    #   for Group 2.a (filtered_prods)
    activate_ndvi_linearx1 = 1
    activate_ndvi_linearx2 = 1

    #   for Group 2.b  (filtered_stats)
    activate_10davg_linearx2 = 1
    activate_10dmin_linearx2 = 1
    activate_10dmax_linearx2 = 1
    activate_10dmed_linearx2 = 1
    activate_10dstd_linearx2 = 0                # To be done

    activate_year_min_linearx2 = 1
    activate_year_max_linearx2 = 1

    activate_absol_min_linearx2 = 1
    activate_absol_max_linearx2 = 1

    #   for Group 2.c  (filtered_masks)
    activate_baresoil_linearx2 = 1

    #   for Group 2.d  (filtered_anomalies)
    activate_diff_linearx2 = 1
    activate_linearx2_diff_linearx2 = 1
    activate_stddiff_linearx2 = 0               # To be done
    activate_icn = 1
    activate_vci = 1
    activate_icn_linearx2 = 1
    activate_vci_linearx2 = 1

    #   for Group 3.a (monthly_prods)
    activate_monndvi = 0

    #   for Group 3.b (monthly_masks)
    activate_monthly_baresoil = 0

    #   for Group 3.c  (monthly_stats)
    activate_1monavg = 1
    activate_1monmax = 1
    activate_1monmin = 1
    activate_1monstd = 1

    #   for Group 3.d  (monthly_anomalies) -> TB Done
    activate_1monsndvi = 1
    activate_1monandvi = 1
    activate_1monvci = 1
    activate_1monicn = 1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep
    #   ---------------------------------------------------------------------
    #   Define input files (NDV)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, ext)

    logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    logger.debug('Input data directory is: %s' % input_dir)
    starting_files = input_dir+"*"+in_prod_ident
    logger.debug('Starting files wild card is: %s' % starting_files)

    #   ---------------------------------------------------------------------
    #   1.a 10Day non-filtered Stats
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   NDV avg x dekad (i.e. avg_dekad)
    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod = proc_lists.proc_add_subprod("10davg", "10dstats", False, True)
    prod_ident_10davg = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10davg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10davg+"{MMDD[0]}"+prod_ident_10davg]

    @active_if(group_no_filter_stats, activate_10davg_no_filter)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def vgt_ndvi_10davg_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV min x dekad (i.e. min_dekad)
    output_sprod=proc_lists.proc_add_subprod("10dmin", "10dstats", False, True)
    prod_ident_10dmin = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmin = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmin+"{MMDD[0]}"+prod_ident_10dmin]

    @active_if(group_no_filter_stats, activate_10dmin_no_filter)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    #@follows(vgt_ndvi_10davg_no_filter)
    def vgt_ndvi_10dmin_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV max x dekad (i.e. max_dekad)
    output_sprod=proc_lists.proc_add_subprod("10dmax", "10dstats", False, True)
    prod_ident_10dmax = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmax = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmax+"{MMDD[0]}"+prod_ident_10dmax]

    @active_if(group_no_filter_stats, activate_10dmax_no_filter)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    #@follows(vgt_ndvi_10dmin_no_filter)
    def vgt_ndvi_10dmax_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV std x dekad (i.e. std_dekad)
    output_sprod = "10DSTD"


    #  ---------------------------------------------------------------------
    #   NDV med x dekad (i.e. med_dekad)

    output_sprod=proc_lists.proc_add_subprod("10dmed", "10dstats", False, True)
    prod_ident_10dmed = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmed = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmed+"{MMDD[0]}"+prod_ident_10dmed]

    @active_if(group_no_filter_stats, activate_10dmed_no_filter)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    #@follows(vgt_ndvi_10dmax_no_filter)
    def vgt_ndvi_10dmed_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_med_image(**args)

    #   ---------------------------------------------------------------------
    #   1.b 10Day non-filtered Anomalies
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   2.a NDVI linearx1/x2
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_prods")
    output_sprod=proc_lists.proc_add_subprod("ndvi_linearx1", "filtered_prods", False, True)
    prod_ident_linearx1 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_linearx1 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_ndvi_linearx1():

            #   Look for all input files in input_dir, and sort them
            input_files = glob.glob(starting_files)
            input_files.sort()

            for file_t0 in input_files:
                # Get current date
                date_t0 = functions.get_date_from_path_full(file_t0)
                output_file = es2_data_dir+subdir_linearx1+str(date_t0)+prod_ident_linearx1

                # Get files at t-1 and t+1
                adjac_files = functions.files_temp_ajacent(file_t0)

                if len(adjac_files) == 2:

                    # Prepare and return arguments
                    three_files_in_a_row = [adjac_files[0], file_t0, adjac_files[1]]
                    yield (three_files_in_a_row, output_file)

    @files(generate_parameters_ndvi_linearx1)
    #@follows(vgt_ndvi_10dmed_no_filter)
    @active_if(group_filtered_prods, activate_ndvi_linearx1)
    def vgt_ndvi_linearx1(input_files, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_files[1], "before_file":input_files[0], "after_file": input_files[2], "output_file": output_file,
                 "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
        print args
        raster_image_math.do_ts_linear_filter(**args)

    output_sprod=proc_lists.proc_add_subprod("ndvi_linearx2", "filtered_prods", False, True)
    prod_ident_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_ndvi_linearx2():

            wild_card_linearx1 = es2_data_dir+subdir_linearx1+'*'+prod_ident_linearx1
            #   Look for all input files in input_dir, and sort them
            input_files = glob.glob(wild_card_linearx1)
            input_files.sort()

            for file_t0 in input_files:
                # Get current date
                date_t0 = functions.get_date_from_path_full(file_t0)
                output_file = es2_data_dir+subdir_linearx2+str(date_t0)+prod_ident_linearx2

                # Get files at t-1 and t+1
                adjac_files = functions.files_temp_ajacent(file_t0)

                if len(adjac_files) == 2:

                    # Prepare and return arguments
                    three_files_in_a_row = [adjac_files[0], file_t0, adjac_files[1]]
                    yield (three_files_in_a_row, output_file)

    @active_if(group_filtered_prods,activate_ndvi_linearx2)
    @files(generate_parameters_ndvi_linearx2)
    @follows(vgt_ndvi_linearx1)
    def vgt_ndvi_linearx2(input_files, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_files[1], "before_file":input_files[0], "after_file": input_files[2], "output_file": output_file,
                 "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
        raster_image_math.do_ts_linear_filter(**args)


    #   ---------------------------------------------------------------------
    #   2.b NDVI_LINEARX2 statistics
    #
    #   Note: I have to re-initialize the 'starting-files', as referring to
    #         ndvi_linearx2 in '@collate' does not work (variable overwriting?)
    #   ---------------------------------------------------------------------

    input_subprod_linearx2 = "ndvi_linearx2"
    in_prod_ident_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_linearx2,mapset, version, ext)

    input_dir_linearx2 = es2_data_dir+ functions.set_path_sub_directory(prod, input_subprod_linearx2, 'Derived', version, mapset)

    starting_files_linearx2 = input_dir_linearx2+"*"+in_prod_ident_linearx2

    #   ---------------------------------------------------------------------
    #   Linearx2 avg x dekad
    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_stats")
    output_sprod=proc_lists.proc_add_subprod("10davg_linearx2", "filtered_stats", False, True)
    prod_ident_10davg_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10davg_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    @active_if(group_filtered_stats, activate_10davg_linearx2)
    @collate(starting_files_linearx2,
             formatter("[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2),
             ["{subpath[0][5]}"+os.path.sep+subdir_10davg_linearx2+"{MMDD[0]}"+prod_ident_10davg_linearx2])
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_10davg_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Linearx2 min x dekad
    output_sprod=proc_lists.proc_add_subprod("10dmin_linearx2", "filtered_stats", False, True)
    prod_ident_10dmin_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmin_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmin_linearx2+"{MMDD[0]}"+prod_ident_10dmin_linearx2]

    @active_if(group_filtered_stats, activate_10dmin_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_10dmin_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Linearx2 max x dekad
    output_sprod=proc_lists.proc_add_subprod("10dmax_linearx2", "filtered_stats", False, True)
    prod_ident_10dmax_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmax_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmax_linearx2+"{MMDD[0]}"+prod_ident_10dmax_linearx2]

    @active_if(group_filtered_stats, activate_10dmax_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_10dmax_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   Linearx2 std x dekad
    output_sprod = "10dstd"


    #  ---------------------------------------------------------------------
    #   Linearx2 med x dekad

    output_sprod=proc_lists.proc_add_subprod("10dmed_linearx2", "filtered_stats", False, True)
    prod_ident_10dmed_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmed_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmed_linearx2+"{MMDD[0]}"+prod_ident_10dmed_linearx2]

    @active_if(group_filtered_stats, activate_10dmed_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_10dmed_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_med_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 min x year

    output_sprod=proc_lists.proc_add_subprod("year_min_linearx2", "filtered_stats", False, True)
    prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_year_min_linearx2   = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_year_min_linearx2+"{YYYY[0]}"+prod_ident_year_min_linearx2]

    @active_if(group_filtered_stats, activate_year_min_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10dmin_linearx2)
    def vgt_ndvi_year_min_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 max x year

    output_sprod=proc_lists.proc_add_subprod("year_max_linearx2", "filtered_stats", False, True)
    prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_year_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_year_max_linearx2+"{YYYY[0]}"+prod_ident_year_max_linearx2]

    @active_if(group_filtered_stats, activate_year_max_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10dmax_linearx2)
    def vgt_ndvi_year_max_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 absolute min: Starting files re-initialized to year-min
    #   ---------------------------------------------------------------------

    input_subprod_year_min_linearx2 = "year_min_linearx2"
    in_prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_min_linearx2,mapset, version, ext)

    input_dir_year_min_linearx2 = es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_year_min_linearx2, 'Derived', version, mapset)

    starting_files_year_min_linearx2 = input_dir_year_min_linearx2+"*"+in_prod_ident_year_min_linearx2

    #  ---------------------------------------------------------------------
    output_sprod=proc_lists.proc_add_subprod("absol_min_linearx2", "filtered_stats", False, True)
    prod_ident_absol_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_absol_min_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}"+in_prod_ident_year_min_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_absol_min_linearx2+'Overall'+prod_ident_absol_min_linearx2]

    @active_if(group_filtered_stats, activate_absol_min_linearx2)
    @collate(starting_files_year_min_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_year_min_linearx2)
    def vgt_ndvi_absol_min_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 absolute max

    input_subprod_year_max_linearx2 = "year_max_linearx2"
    in_prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_max_linearx2,mapset, version, ext)

    input_dir_year_max_linearx2 = es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_year_max_linearx2, 'Derived', version, mapset)

    starting_files_year_max_linearx2 = input_dir_year_max_linearx2+"*"+in_prod_ident_year_max_linearx2

    #  ---------------------------------------------------------------------
    output_sprod=proc_lists.proc_add_subprod("absol_max_linearx2", "filtered_stats", False, True)
    prod_ident_absol_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_absol_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}"+in_prod_ident_year_max_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_absol_max_linearx2+'Overall'+prod_ident_absol_max_linearx2]

    @active_if(group_filtered_stats, activate_absol_max_linearx2)
    @collate(starting_files_year_max_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_year_max_linearx2)
    def vgt_ndvi_absol_max_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   2.b NDVI_baresoil mask
    #       TODO-M.C.: FTTB does not use min/max ... to be changed ??
    #   ---------------------------------------------------------------------
    #
    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_masks")
    output_sprod = proc_lists.proc_add_subprod("baresoil_linearx2", "filtered_masks", False, True)
    prod_ident_baresoil_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_baresoil_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_baresoil_linearx2+"{YYYYMMDD[0]}"+prod_ident_baresoil_linearx2]

    @active_if(group_filtered_masks, activate_baresoil_linearx2)
    @transform(starting_files_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_absol_max_linearx2)
    def vgt_ndvi_baresoil_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_baresoil(**args)

    #   ---------------------------------------------------------------------
    #   2.c NDVI_linearx2 anomalies
    #   ---------------------------------------------------------------------

    #  ---------------------------------------------------------------------
    #   'diff' vs. avg_filtered (NDV - avg_dekad_filtered)

    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_anomalies")
    output_sprod = proc_lists.proc_add_subprod("diff_linearx2", "filtered_anomalies", False, True)
    prod_ident_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_diff_linearx2]

    ancillary_sprod = "10davg_linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod,mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @active_if(group_filtered_anomalies, activate_diff_linearx2)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_diff_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_subtraction(**args)


    #  ---------------------------------------------------------------------
    #   Linearx2 'diff' (Linearx2 - avg_dekad_filtered)

    output_sprod = proc_lists.proc_add_subprod("linearx2diff_linearx2", "filtered_anomalies", False, True)
    prod_ident_linearx2_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_linearx2_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_linearx2_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_linearx2_diff_linearx2]

    ancillary_sprod = "10davg_linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod,mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident


    @active_if(group_filtered_anomalies, activate_linearx2_diff_linearx2)
    @transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(vgt_ndvi_diff_linearx2)
    def vgt_ndvi_linearx2_diff_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 'stddiff2avg' (Linearx2 -avg/std)
    #   TODO-M.C.: STD missing !!!!
    #
    # output_sprod = "STDDIFF2AVG_LINEARX2"
    # prod_ident_stddiff2avg_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    # subdir_stddiff2avg_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
    #
    # formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    # formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_stddiff2avg_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_stddiff2avg_linearx2]
    #
    # ancillary_sprod_1 = "10DAVG_LINEARX2"
    # ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    # ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    # ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1
    #
    # ancillary_sprod_2 = "10DSTD_LINEARX2"
    # ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    # ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    # ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2
    #
    # @active_if(activate_vgt_ndvi_comput, activate_filtered_stats, activate_linearx2_diff_linearx2)
    # @transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2), formatter_out)
    # def vgt_ndvi_stddiff2avg_linearx2(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    #     raster_image_math.do_oper_subtraction(**args)

    #  ---------------------------------------------------------------------
    #   vci (NDV - min)/(max - min)  -> min/max per dekad

    output_sprod = proc_lists.proc_add_subprod("vci", "filtered_anomalies", False, True)
    prod_ident_vci = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_vci = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_vci+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci]

    ancillary_sprod_1 = "10dmax_linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmin_linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_vci)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_linearx2_diff_linearx2)
    def vgt_ndvi_vci(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "max_file": input_file[1],"min_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

    #  ---------------------------------------------------------------------
    #   icn (NDV - min)/(max - min)  -> min/max absolute

    output_sprod = proc_lists.proc_add_subprod("icn", "filtered_anomalies", False, True)
    prod_ident_icn = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_icn = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_icn+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn]

    ancillary_sprod_1 = "absol_max_linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "absol_min_linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_icn)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_vci)
    def vgt_ndvi_icn(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0],"max_file": input_file[1], "min_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

    #  ---------------------------------------------------------------------
    #   vci_linearx2 (linearx2 - min)/(max - min)  -> min/max per dekad
    output_sprod = proc_lists.proc_add_subprod("icn", "filtered_anomalies", False, True)
    output_sprod = proc_lists.proc_add_subprod("vci_linearx2", "filtered_anomalies", False, True)
    prod_ident_vci_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_vci_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_vci_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci_linearx2]

    ancillary_sprod_1 = "10dmax_linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmin_linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_vci_linearx2)
    @transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_icn)
    def vgt_ndvi_vci_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "max_file": input_file[1], "min_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

    #  ---------------------------------------------------------------------
    #   icn_linearx2 (linearx2 - min)/(max - min)  -> min/max absolute
    output_sprod = proc_lists.proc_add_subprod("icn_linearx2", "filtered_anomalies", False, True)
    prod_ident_icn_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_icn_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_icn_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn_linearx2]

    ancillary_sprod_1 = "absol_max_linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "absol_min_linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_icn_linearx2)
    @transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_vci_linearx2)
    def vgt_ndvi_icn_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "max_file": input_file[1], "min_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

    #   ---------------------------------------------------------------------
    #   3.a NDVI monthly product (avg)
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("monthly_prod")
    output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)
    prod_ident_mon_ndvi = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_mon_ndvi = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident_linearx2
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_mon_ndvi+"{YYYYMM[0]}"+'01'+prod_ident_mon_ndvi

    @active_if(group_monthly_prods, activate_monndvi)
    @collate(starting_files_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_icn_linearx2)
    def vgt_ndvi_monmdvi(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   3.b NDVI monthly masks
    #   ---------------------------------------------------------------------
    input_subprod_monndvi = "monndvi"
    output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)
    in_prod_ident_monndvi = functions.set_path_filename_no_date(prod, input_subprod_monndvi,mapset, version, ext)

    input_dir_monndvi =es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_monndvi, 'Derived', version, mapset)

    starting_files_monndvi = input_dir_monndvi+"*"+in_prod_ident_monndvi

    #   ---------------------------------------------------------------------
    #   3.c NDVI monthly stats
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   NDV  avg x month

    output_sprod_group=proc_lists.proc_add_subprod_group("monthly_stats")
    output_sprod = proc_lists.proc_add_subprod("1monavg", "monthly_stats", False, True)
    prod_ident_1monavg = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1monavg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1monavg+"{MMDD[0]}"+prod_ident_1monavg

    @active_if(group_monthly_stats, activate_1monavg)
    @collate(starting_files_monndvi, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_monmdvi)
    def vgt_ndvi_1monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV  min x month
    output_sprod = proc_lists.proc_add_subprod("1monmin", "monthly_stats", False, True)
    prod_ident_1monmin = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1monmin = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1monmin+"{MMDD[0]}"+prod_ident_1monmin

    @active_if(group_monthly_stats, activate_1monmin)
    @collate(starting_files_monndvi, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_1monavg)
    def vgt_ndvi_1monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV  max x month
    output_sprod = proc_lists.proc_add_subprod("1monmax", "monthly_stats", False, True)
    prod_ident_1monmax = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1monmax = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1monmax+"{MMDD[0]}"+prod_ident_1monmax

    @active_if(group_monthly_stats, activate_1monmax)
    @collate(starting_files_monndvi, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_1monmin)
    def vgt_ndvi_1monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)


#   ---------------------------------------------------------------------
#   3.d NDVI monthly anomalies
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------
#   Run the pipeline
def processing_std_ndvi(pipeline_run_level=0, pipeline_run_touch_only=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                        starting_dates=None, update_stats=False, nrt_products=True):

    global list_subprods, list_subprod_groups

    list_subprods = []
    list_subprod_groups = []
    create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                    starting_dates=starting_dates, update_stats=update_stats)

    logger.info("Entering routine %s" % 'processing_std_ndvi')
    logger.info("pipeline_run_level %i" % pipeline_run_level)

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only, multiprocess=multiprocess)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    return list_subprods, list_subprod_groups


def processing_std_ndvi_stats_only(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None):

    [list_subprods, list_subprod_groups] = processing_std_ndvi(pipeline_run_level=pipeline_run_level,
                                                               pipeline_run_touch_only=pipeline_run_touch_only,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates=starting_dates,
                                                               nrt_products=False,
                                                               update_stats=True)

    return list_subprods, list_subprod_groups

def processing_std_ndvi_prods_only(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None):

    [list_subprods, list_subprod_groups] = processing_std_ndvi(pipeline_run_level=pipeline_run_level,
                                                               pipeline_run_touch_only=pipeline_run_touch_only,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates=starting_dates,
                                                               nrt_products=True,
                                                               update_stats=False)

    return list_subprods, list_subprod_groups

def processing_std_ndvi_all(pipeline_run_level=0,pipeline_run_touch_only=0, pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None):

    [list_subprods, list_subprod_groups] = processing_std_ndvi(pipeline_run_level=pipeline_run_level,
                                                               pipeline_run_touch_only=pipeline_run_touch_only,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates=starting_dates,
                                                               nrt_products=True,
                                                               update_stats=True)

    return list_subprods, list_subprod_groups
