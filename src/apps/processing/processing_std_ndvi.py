from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define the processing chain for 'ndvi-like' processing chains
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.01.2015
#   descr:	 Generate additional Derived products/implements processing chains
#	history: 1.0
#

# Import std modules
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import glob
import os
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from lib.python import metadata

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates_linearx2=None, proc_lists=None,
                    update_stats=False, nrt_products=True):


    #   ---------------------------------------------------------------------
    #   NOTE: starting_dates_linearx2 apply to linearx2 statistics (not to the initial product)
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    #   switch wrt groups - according to options

    # DEFAULT: ALL off
    group_no_filter_stats = 0                  # 1.a
    group_no_filter_anomalies = 0              # 1.b
    group_no_filter_masks = 0                  # 1.c

    group_filtered_prods = 0                   # 2.a
    group_filtered_stats = 0                   # 2.b
    group_filtered_masks = 0                   # 2.c
    group_filtered_anomalies = 0               # 2.d

    group_monthly_prods = 0                    # 3.a
    group_monthly_stats = 0                    # 3.b
    group_monthly_masks = 0                    # 3.c
    group_monthly_anomalies = 0                # 3.d

    if nrt_products:
        group_no_filter_anomalies = 0              # 1.b    -> To be done
        group_no_filter_masks = 1                  # 1.c    -> NDV no-filtered + Abs_Max_Linearx2
        group_filtered_prods = 1                   # 2.a
        group_filtered_masks = 1                   # 2.c
        group_filtered_anomalies = 1               # 2.d
        group_monthly_prods = 1                    # 3.a
        group_monthly_masks = 0                    # 3.c    -> To be done
        group_monthly_anomalies = 1                # 3.d    -> To be done

    if update_stats:
        group_no_filter_stats = 0                  # 1.a    -> Not done anymore
        group_filtered_stats = 1                   # 2.b
        group_monthly_stats = 1                    # 3.b

    #   switch wrt single products: not to be changed

    #   for Group 1.a (ndvi_no_filter_stats)
    activate_10davg_no_filter = 1
    activate_10dmin_no_filter = 1
    activate_10dmax_no_filter = 1
    activate_10dmed_no_filter = 1
    activate_10dstd_no_filter = 0              # To be done

    #   for Group 1.b (ndvi_no_filter_anom)
    activate_10ddiff_no_filter = 0
    activate_icn = 1
    activate_vci = 1
    activate_diff_linearx2 = 0                  # NDV (non filtered) - 10davg_linearx2 (NOT computed and masked in DB!)

    #   for Group 1.c (no_filter_mask)
    activate_baresoil = 1

    #   for Group 2.a (filtered_prods)
    activate_ndvi_linearx1 = 1
    activate_ndvi_linearx2 = 1

    #   for Group 2.b  (filtered_stats)
    activate_10davg_linearx2 = 1
    activate_10dmin_linearx2 = 1
    activate_10dmax_linearx2 = 1
    activate_10dmed_linearx2 = 1
    activate_10dstd_linearx2 = 1                # done

    activate_year_min_linearx2 = 1
    activate_year_max_linearx2 = 1

    activate_absol_min_linearx2 = 1
    activate_absol_max_linearx2 = 1

    #   for Group 2.c  (filtered_masks)
    activate_baresoil_linearx2 = 1
    activate_ndvi_linearx2_agric = 0            # TEMP

    #   for Group 2.d  (filtered_anomalies)
    activate_linearx2_diff_linearx2 = 1
    activate_icn_linearx2 = 1
    activate_vci_linearx2 = 1
    activate_10ddiff_linearx2 = 0               # This product is a duplication of linearx2_diff_linearx2 and does not include baresoil mask -> to be removed
    activate_10dperc_linearx2 = 1
    activate_10dsndvi_linearx2 = 1
    activate_ratio_linearx2 = 1
    activate_stddiff_linearx2 = 0               # To be done

    #   for Group 3.a (monthly_prods)
    activate_monndvi = 1

    #   for Group 3.c (monthly_masks)
    activate_monthly_baresoil = 1

    #   for Group 3.b  (monthly_stats)
    activate_1monavg = 1
    activate_1monmax = 1
    activate_1monmin = 1
    activate_1monstd = 1


    #   for Group 3.d  (monthly_anomalies) -> TB Done
    activate_1monsndvi = 1
    activate_1monandvi = 1
    activate_1monvci = 1
    activate_1monicn = 1
    activate_1mondiff = 1
    activate_1monperc = 1

    activate_monthly_ratio = 1

    sds_meta = metadata.SdsMetadata()
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files (NDV)
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod,mapset, version, ext)
    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)
    starting_files = input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   1.a 10Day non-filtered Stats
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   NDV avg x dekad (i.e. avg_dekad)
    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod=proc_lists.proc_add_subprod("10davg", "10dstats", final=False,
                                             descriptive_name='10d Average',
                                             description='Average NDVI for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

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
    output_sprod=proc_lists.proc_add_subprod("10dmin", "10dstats", final=False,
                                             descriptive_name='10d Minimum',
                                             description='Minimum NDVI for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    prod_ident_10dmin = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmin = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmin+"{MMDD[0]}"+prod_ident_10dmin]

    @active_if(group_no_filter_stats, activate_10dmin_no_filter)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def vgt_ndvi_10dmin_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV max x dekad (i.e. max_dekad)
    output_sprod=proc_lists.proc_add_subprod("10dmax", "10dstats", final=False,
                                             descriptive_name='10d Maximum',
                                             description='Maximum NDVI for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    prod_ident_10dmax = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmax = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmax+"{MMDD[0]}"+prod_ident_10dmax]

    @active_if(group_no_filter_stats, activate_10dmax_no_filter)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    def vgt_ndvi_10dmax_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #  ---------------------------------------------------------------------
    #   NDV med x dekad (i.e. med_dekad)

    output_sprod=proc_lists.proc_add_subprod("10dmed", "10dstats", final=False,
                                             descriptive_name='10d Median',
                                             description='Median NDVI for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)

    prod_ident_10dmed = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmed = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmed+"{MMDD[0]}"+prod_ident_10dmed]

    @active_if(group_no_filter_stats, activate_10dmed_no_filter)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def vgt_ndvi_10dmed_no_filter(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_med_image(**args)

    #   ---------------------------------------------------------------------
    #   1.b 10Day non-filtered Anomalies
    #   ---------------------------------------------------------------------

    #   Not yet done (diff, vci, icn of ndv vs non filtered stats)

    #   ---------------------------------------------------------------------
    #   2.a NDVI linearx1/x2
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_prods")
    output_sprod=proc_lists.proc_add_subprod("ndvi-linearx1", "filtered_prods", final=False,
                                             descriptive_name='Filtered NDVI linearx1',
                                             description='Filtered NDVI linearx1',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=True,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)

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
    @active_if(group_filtered_prods, activate_ndvi_linearx1)
    @follows(vgt_ndvi_10dmed_no_filter)
    def vgt_ndvi_linearx1(input_files, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_files[1], "before_file":input_files[0], "after_file": input_files[2], "output_file": output_file,
                 "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
        raster_image_math.do_ts_linear_filter(**args)

    output_sprod=proc_lists.proc_add_subprod("ndvi-linearx2", "filtered_prods", final=False,
                                             descriptive_name='Filtered NDVI linearx2',
                                             description='Filtered NDVI linearx2',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

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
    #   2.a NDVI linearx2 masked using Crop Mask
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_prods")
    output_sprod=proc_lists.proc_add_subprod("ndvi-linearx2_agric", "filtered_prods", final=False,
                                             descriptive_name='10d Filtered NDVI Crop Masked',
                                             description='Ten day Filtered NDVI Masked using Crop Mask',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=True,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_linearx2_agric = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_linearx2_agric = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    input_subprod_linearx2 = "ndvi-linearx2"
    in_prod_ident_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_linearx2,mapset, version, ext)
    input_dir_linearx2 = es2_data_dir+ functions.set_path_sub_directory(prod, input_subprod_linearx2, 'Derived', version, mapset)

    if starting_dates_linearx2 is not None:
        starting_files_linearx2 = []
        for my_date in starting_dates_linearx2:
            if functions.is_file_exists_in_path(input_dir_linearx2 + my_date + in_prod_ident_linearx2):
                starting_files_linearx2.append(input_dir_linearx2 + my_date + in_prod_ident_linearx2)
    else:
        starting_files_linearx2 = input_dir_linearx2 + "*" + in_prod_ident_linearx2

    formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_linearx2_agric+"{YYYYMMDD[0]}"+prod_ident_linearx2_agric]

    @active_if(group_filtered_prods, activate_ndvi_linearx2_agric)
    @transform(starting_files_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_linearx2_agric(input_files, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_files[1], "before_file":input_files[0], "after_file": input_files[2], "output_file": output_file,
                 "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
        print (args)
        #raster_image_math.do_ts_linear_filter(**args)


    #   ---------------------------------------------------------------------
    #   2.b NDVI_LINEARX2 statistics
    #
    #   Note: I have to re-initialize the 'starting-files', as referring to
    #         ndvi_linearx2 in '@collate' does not work (variable overwriting?)
    #   ---------------------------------------------------------------------

    input_subprod_linearx2 = "ndvi-linearx2"
    in_prod_ident_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_linearx2,mapset, version, ext)

    input_dir_linearx2 = es2_data_dir+ functions.set_path_sub_directory(prod, input_subprod_linearx2, 'Derived', version, mapset)

    # if starting_dates_linearx2 is not None:
    #     starting_files_linearx2 = []
    #     for my_date in starting_dates_linearx2:
    #         starting_files_linearx2.append(input_dir_linearx2+my_date+in_prod_ident_linearx2)
    # else:
    #     starting_files_linearx2 = input_dir_linearx2+"*"+in_prod_ident_linearx2

    #   ---------------------------------------------------------------------
    #   Linearx2 avg x dekad
    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_stats")
    output_sprod=proc_lists.proc_add_subprod("10davg-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d lineax2 Average',
                                             description='Average NDVI linearx2 for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='ndvi_linearx2',
                                             active_default=True)

    prod_ident_10davg_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10davg_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    @active_if(group_filtered_stats, activate_10davg_linearx2)
    @collate(starting_files_linearx2, formatter("[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2), ["{subpath[0][5]}"+os.path.sep+subdir_10davg_linearx2+"{MMDD[0]}"+prod_ident_10davg_linearx2])
    @follows(vgt_ndvi_linearx2)
    def vgt_ndvi_10davg_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Linearx2 min x dekad
    output_sprod=proc_lists.proc_add_subprod("10dmin-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d lineax2 Minimum',
                                             description='Minimum NDVI linearx2 for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='ndvi_linearx2',
                                             active_default=True)
    prod_ident_10dmin_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmin_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmin_linearx2+"{MMDD[0]}"+prod_ident_10dmin_linearx2]

    @active_if(group_filtered_stats, activate_10dmin_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10davg_linearx2)
    def vgt_ndvi_10dmin_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Linearx2 max x dekad
    output_sprod=proc_lists.proc_add_subprod("10dmax-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d lineax2 Maximum',
                                             description='Maximum NDVI linearx2 for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='ndvi_linearx2',
                                             active_default=True)
    prod_ident_10dmax_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmax_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmax_linearx2+"{MMDD[0]}"+prod_ident_10dmax_linearx2]

    @active_if(group_filtered_stats, activate_10dmax_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10dmin_linearx2)
    def vgt_ndvi_10dmax_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)


    output_sprod = "10dstd"
    #  ---------------------------------------------------------------------
    #  Linearx2 std x dekad
    output_sprod = proc_lists.proc_add_subprod("10dstd-linearx2", "filtered_stats", final=False,
                                               descriptive_name='10d lineax2 Standard deviation',
                                               description='Standard deviation NDVI linearx2 for dekad',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='ndvi_linearx2',
                                               active_default=True)

    prod_ident_10dstd = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_10dstd = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    #formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_linearx2
    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dstd+"{MMDD[0]}"+prod_ident_10dstd]
    #formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_10dstd + "{YYYY[0]}{MMDD[0]}" + prod_ident_10dstd

    ancillary_sprod = "10davg-linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @active_if(group_filtered_stats, activate_10dstd_linearx2)
    @follows(vgt_ndvi_10davg_linearx2)
    #@transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @collate(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_10dstddev(input_file, output_file):

        #[current_file, avg_file] = input_file
        current_file = [i[0] for i in input_file]
        avg_file = [i[1] for i in input_file][0]

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": current_file, "avg_file": avg_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "output_stddev": output_file}
        raster_image_math.do_stddev_image(**args)


    #  ---------------------------------------------------------------------
    #   Linearx2 med x dekad

    output_sprod=proc_lists.proc_add_subprod("10dmed-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d lineax2 Median',
                                             description='Median NDVI linearx2 for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='ndvi_linearx2',
                                             active_default=True)

    prod_ident_10dmed_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_10dmed_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_10dmed_linearx2+"{MMDD[0]}"+prod_ident_10dmed_linearx2]

    @active_if(group_filtered_stats, activate_10dmed_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10dmax_linearx2)
    def vgt_ndvi_10dmed_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_med_image(**args)



    #  ---------------------------------------------------------------------
    #   Linearx2 min x year

    output_sprod=proc_lists.proc_add_subprod("year-min-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d yearly Minimum',
                                             description='Minimum NDVI for year',
                                             frequency_id='e1year',
                                             date_format='YYYY',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_year_min_linearx2   = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_year_min_linearx2+"{YYYY[0]}"+prod_ident_year_min_linearx2]

    @active_if(group_filtered_stats, activate_year_min_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_10dmed_linearx2)
    def vgt_ndvi_year_min_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 max x year

    output_sprod=proc_lists.proc_add_subprod("year-max-linearx2", "filtered_stats", final=False,
                                             descriptive_name='10d yearly Maximum',
                                             description='Maximum NDVI for year',
                                             frequency_id='e1year',
                                             date_format='YYYY',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_year_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_year_max_linearx2+"{YYYY[0]}"+prod_ident_year_max_linearx2]

    @active_if(group_filtered_stats, activate_year_max_linearx2)
    @collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
    @follows(vgt_ndvi_year_min_linearx2)
    def vgt_ndvi_year_max_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 absolute min: Starting files re-initialized to year-min
    #   ---------------------------------------------------------------------

    input_subprod_year_min_linearx2 = "year-min-linearx2"
    in_prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_min_linearx2,mapset, version, ext)

    input_dir_year_min_linearx2 = es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_year_min_linearx2, 'Derived', version, mapset)

    starting_files_year_min_linearx2 = input_dir_year_min_linearx2+"*"+in_prod_ident_year_min_linearx2

    #  ---------------------------------------------------------------------
    output_sprod=proc_lists.proc_add_subprod("absol-min-linearx2", "filtered_stats", final=False,
                                             descriptive_name='Absolute Minimum',
                                             description='Absolute Minimum NDVI',
                                             frequency_id='undefined',
                                             date_format='YYYY',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_absol_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_absol_min_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}"+in_prod_ident_year_min_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_absol_min_linearx2+'Overall'+prod_ident_absol_min_linearx2]

    @active_if(group_filtered_stats, activate_absol_min_linearx2)
    @collate(starting_files_year_min_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_year_max_linearx2)
    def vgt_ndvi_absol_min_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 absolute max

    input_subprod_year_max_linearx2 = "year-max-linearx2"
    in_prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_max_linearx2,mapset, version, ext)

    input_dir_year_max_linearx2 = es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_year_max_linearx2, 'Derived', version, mapset)

    starting_files_year_max_linearx2 = input_dir_year_max_linearx2+"*"+in_prod_ident_year_max_linearx2

    #  ---------------------------------------------------------------------
    output_sprod=proc_lists.proc_add_subprod("absol-max-linearx2", "filtered_stats", final=False,
                                             descriptive_name='Absolute Maximum',
                                             description='Absolute Maximum NDVI',
                                             frequency_id='undefined',
                                             date_format='YYYY',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_absol_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_absol_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}"+in_prod_ident_year_max_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_absol_max_linearx2+'Overall'+prod_ident_absol_max_linearx2]

    @active_if(group_filtered_stats, activate_absol_max_linearx2)
    @collate(starting_files_year_max_linearx2, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_absol_min_linearx2)
    def vgt_ndvi_absol_max_linearx2(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   1.c NDVI_baresoil mask (non-filtered NDVI)
    #   ---------------------------------------------------------------------
    #

    output_sprod_group=proc_lists.proc_add_subprod_group("no_filter_masks")
    output_sprod=proc_lists.proc_add_subprod("baresoil", "no_filter_stats", final=False,
                                             descriptive_name='Baresoil Mask',
                                             description='Baresoil Mask NDVI',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_baresoil = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_baresoil = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_baresoil+"{YYYY[0]}{MMDD[0]}"+prod_ident_baresoil]

    ancillary_sprod_1 = "10davg-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    @active_if(group_no_filter_masks, activate_baresoil)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1), formatter_out)
    @follows(vgt_ndvi_absol_max_linearx2)
    def vgt_ndvi_baresoil(input_file, output_file):

        [current_file, average_file] = input_file

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": current_file, "avg_file": average_file, "output_file": output_file, "output_format": 'GTIFF', "ndvi_max":0.18, "options": "compress = lzw"}
        raster_image_math.do_make_baresoil(**args)


    #   ---------------------------------------------------------------------
    #   2.c NDVI_baresoil mask (using avg NDV linearx2)
    #   ---------------------------------------------------------------------
    #
    starting_files_linearx2_all = input_dir_linearx2+"*"+in_prod_ident_linearx2

    output_sprod_group=proc_lists.proc_add_subprod_group("filtered_masks")
    output_sprod=proc_lists.proc_add_subprod("baresoil-linearx2", "filtered_stats", final=False,
                                             descriptive_name='Baresoil Mask',
                                             description='Baresoil Mask NDVI linearx2',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_baresoil_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_baresoil_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_baresoil_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_baresoil_linearx2]

    ancillary_sprod_1 = "10davg-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    @active_if(group_filtered_masks, activate_baresoil_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input_1), formatter_out)
    @follows(vgt_ndvi_10davg_linearx2,vgt_ndvi_baresoil)
    def vgt_ndvi_baresoil_linearx2(input_file, output_file):

        [current_file, average_file] = input_file

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": current_file, "avg_file": average_file, "output_file": output_file, "output_format": 'GTIFF', "ndvi_max": 0.18 ,  "options": "compress = lzw"}
        raster_image_math.do_make_baresoil(**args)

    #   ---------------------------------------------------------------------
    #   2.D NDVI_linearx2 anomalies
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   Linearx2 10dperc
    output_sprod = proc_lists.proc_add_subprod("10dperc-linearx2", "filtered_anomalies", final=False,
                                               descriptive_name='10d Percent Difference',
                                               description='10d Percent Difference vs. LTA',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='ndvi_linearx2',
                                               active_default=True)
    prod_ident_10dperc_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_10dperc_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_linearx2
    formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_10dperc_linearx2 + "{YYYY[0]}{MMDD[0]}" + prod_ident_10dperc_linearx2

    ancillary_sprod = "10davg-linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @follows(vgt_ndvi_10davg_linearx2)
    @active_if(group_filtered_anomalies, activate_10dperc_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_10dperc_linearx2(input_file, output_file):
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file,
                "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)


    #  ---------------------------------------------------------------------
    #   'diff' vs. avg_filtered (NDV - avg_dekad_filtered)

    output_sprod_group=proc_lists.proc_add_subprod_group("no_filter_anomalies")
    output_sprod=proc_lists.proc_add_subprod("diff-linearx2", "no_filter_anomalies", final=False,
                                             descriptive_name='NDVI difference',
                                             description='NDVI difference vs. filtered average',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_diff_linearx2]

    ancillary_sprod_1 = "10davg-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "baresoil"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_diff_linearx2)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_diff_linearx2(input_file, output_file):

        [current_file, average_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        # Compute temporary file
        args = {"input_file": [current_file,average_file], "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_subtraction(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)
    #
    #   ---------------------------------------------------------------------
    #   Linearx2 Diff x dekad
    #output_sprod_group=proc_lists.proc_add_subprod_group("10anomalies")
    #
    #   This product is a duplication of linearx2diff-linearx2 - and no baresoil mask applied
    #   Execution commented on 17.06.2019 (during WorkSpaces validation creation)

    # output_sprod=proc_lists.proc_add_subprod("10ddiff-linearx2", "filtered_anomalies", final=False,
    #                                          descriptive_name='10d Absolute Difference',
    #                                          description='10d Absolute Difference vs. LTA',
    #                                          frequency_id='e1dekad',
    #                                          date_format='YYYYMMDD',
    #                                          masked=False,
    #                                          timeseries_role='ndvi_linearx2',
    #                                          active_default=True)
    # #out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # #output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    # prod_ident_10ddiff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    # subdir_10ddiff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
    #
    # #   Starting files + avg
    # formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    # #formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + in_prod_ident_linearx2
    # formatter_out="{subpath[0][5]}"+os.path.sep+subdir_10ddiff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_10ddiff_linearx2
    #
    # ancillary_sprod = "10davg-linearx2"
    # ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    # ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    # ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident
    #
    # @follows(vgt_ndvi_10davg_linearx2)
    # @active_if(group_filtered_anomalies, activate_10ddiff_linearx2)
    # @transform(starting_files_linearx2, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    # def vgt_ndvi_10ddiff_linearx2(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
    #     raster_image_math.do_oper_subtraction(**args)

    #  ---------------------------------------------------------------------
    #   Linearx2 'diff' (Linearx2 - avg_dekad_filtered)

    output_sprod=proc_lists.proc_add_subprod("linearx2diff-linearx2", "filtered_anomalies", final=False,
                                             descriptive_name='NDVI filter_x2 difference',
                                             description='NDVI filter_x2 difference vs. filtered average',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_linearx2_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_linearx2_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_linearx2_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_linearx2_diff_linearx2]

    ancillary_sprod_1 = "10davg-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "baresoil-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_2

    @active_if(group_filtered_anomalies, activate_linearx2_diff_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2), formatter_out)
    @follows(vgt_ndvi_10davg_linearx2, vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_linearx2_diff_linearx2(input_file, output_file):

        [current_file, average_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        # Compute temporary file
        args = {"input_file": [current_file,average_file], "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_subtraction(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   vci (NDV - min)/(max - min)  -> min/max per dekad - filtered

    output_sprod=proc_lists.proc_add_subprod("vci", "filtered_anomalies", final=False,
                                             descriptive_name='VCI',
                                             description='Vegetation Condition Index',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_vci = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_vci = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_vci+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci]

    ancillary_sprod_1 = "10dmax-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmin-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    ancillary_sprod_3 = "baresoil"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3,mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_3+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_3

    @active_if(group_filtered_anomalies, activate_vci)
    @follows(vgt_ndvi_10dmax_linearx2, vgt_ndvi_10dmin_linearx2, vgt_ndvi_baresoil)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2, ancillary_input_3), formatter_out)
    def vgt_ndvi_vci(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        # Compute temporary file
        args = {"input_file":current_file, "max_file": max_file,"min_file": min_file, "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   icn (NDV - min)/(max - min)  -> min/max absolute

    output_sprod=proc_lists.proc_add_subprod("icn", "filtered_anomalies", final=False,
                                             descriptive_name='ICN',
                                             description='ICN',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_icn = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_icn = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_icn+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn]

    ancillary_sprod_1 = "absol-max-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "absol-min-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

    ancillary_sprod_3 = "baresoil"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3,mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_3+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_3

    @active_if(group_filtered_anomalies, activate_icn)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2,ancillary_input_3), formatter_out)
    @follows(vgt_ndvi_absol_min_linearx2, vgt_ndvi_absol_max_linearx2, vgt_ndvi_baresoil)
    def vgt_ndvi_icn(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        # Compute temporary file
        args = {"input_file":current_file, "max_file": max_file,"min_file": min_file, "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   vci_linearx2 (linearx2 - min)/(max - min)  -> min/max per dekad
    output_sprod=proc_lists.proc_add_subprod("vci-linearx2", "filtered_anomalies", final=False,
                                             descriptive_name='VCI linearx2',
                                             description='Vegetation Condition Index',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_vci_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_vci_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_vci_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci_linearx2]

    ancillary_sprod_1 = "10dmax-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "10dmin-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    ancillary_sprod_3 = "baresoil-linearx2"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3,mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_3+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_3

    @active_if(group_filtered_anomalies, activate_vci_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2, ancillary_input_3), formatter_out)
    @follows(vgt_ndvi_10dmax_linearx2, vgt_ndvi_10dmin_linearx2, vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_vci_linearx2(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file":current_file, "max_file": max_file,"min_file": min_file, "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   icn_linearx2 (linearx2 - min)/(max - min)  -> min/max absolute
    output_sprod=proc_lists.proc_add_subprod("icn-linearx2", "filtered_anomalies", final=False,
                                             descriptive_name='ICN linearx2',
                                             description='Vegetation Condition Index',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_icn_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_icn_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_icn_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn_linearx2]

    ancillary_sprod_1 = "absol-max-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "absol-min-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

    ancillary_sprod_3 = "baresoil-linearx2"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3,mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_3+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_3

    @active_if(group_filtered_anomalies, activate_icn_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2, ancillary_input_3), formatter_out)
    @follows(vgt_ndvi_absol_min_linearx2, vgt_ndvi_absol_max_linearx2, vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_icn_linearx2(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file": current_file, "max_file": max_file, "min_file": min_file, "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   ratio_linearx2 (linearx2/avg) -> 0-100 % value

    output_sprod=proc_lists.proc_add_subprod("ratio-linearx2", "filtered_anomalies", final=False,
                                             descriptive_name='Ratio linearx2',
                                             description='Ratio linearx2 (curr/avg)',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_ratio_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_ratio_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_ratio_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_ratio_linearx2]

    ancillary_sprod = "10davg-linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod,mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    ancillary_sprod_1 = "baresoil-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_1

    @active_if(group_filtered_anomalies, activate_ratio_linearx2)
    @transform(starting_files_linearx2_all, formatter(formatter_in), add_inputs(ancillary_input, ancillary_input_1), formatter_out)
    @follows(vgt_ndvi_10davg_linearx2, vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_ratio_linearx2(input_file, output_file):

        [current_file, avg_file, baresoil_file] = input_file

        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file": [current_file,avg_file], "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #   ---------------------------------------------------------------------
    #   Standardized NDVI linearx2 (aka Z-score)

    output_sprod = proc_lists.proc_add_subprod("10dsndvi-linearx2", "filtered_anomalies", final=False,
                                               descriptive_name='10d Standardized NDVI',
                                               description='Standardized NDVI for dekad',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)

    prod_ident_10dsndvi = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_10dsndvi = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    input_subprod_10diff = "linearx2diff-linearx2"
    # output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)

    in_prod_ident_10diff = functions.set_path_filename_no_date(prod, input_subprod_10diff, mapset, version, ext)

    input_dir_10diff = es2_data_dir + \
                        functions.set_path_sub_directory(prod, input_subprod_10diff, 'Derived', version, mapset)

    starting_files_10ddiff = input_dir_10diff + "*" + in_prod_ident_10diff

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_10diff
    formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_10dsndvi + "{YYYY[0]}{MMDD[0]}" + prod_ident_10dsndvi

    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    # formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1mondiff+"{MMDD[0]}"+prod_ident_1mondiff

    ancillary_sprod = "10dstd-linearx2"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir +"{MMDD[0]}"+ ancillary_sprod_ident

    ancillary_sprod_1 = "baresoil-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_1

    @active_if(group_filtered_anomalies, activate_10dsndvi_linearx2)
    #@follows(vgt_ndvi_10ddiff_linearx2, vgt_ndvi_10dstddev)
    @transform(starting_files_10ddiff, formatter(formatter_in), add_inputs(ancillary_input, ancillary_input_1), formatter_out)
    def vgt_ndvi_10dsndvi(input_file, output_file):

        [current_file, file_10dstd, baresoil_file] = input_file

        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": [current_file, file_10dstd], "output_file": output_file_temp, "output_format": 'GTIFF',
                "options": "compress=lzw"}
        raster_image_math.do_oper_division_perc(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #   ---------------------------------------------------------------------
    #   3.a NDVI monthly product (avg)
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("monthly_prod")
    output_sprod=proc_lists.proc_add_subprod("monndvi", "monthly_prod", final=False,
                                             descriptive_name='Monthly NDVI',
                                             description='Monthly NDVI',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_mon_ndvi = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_mon_ndvi = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident_linearx2
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_mon_ndvi+"{YYYYMM[0]}"+'01'+prod_ident_mon_ndvi

    @active_if(group_monthly_prods, activate_monndvi)
    @collate(starting_files_linearx2_all, formatter(formatter_in), formatter_out)
    # @follows(vgt_ndvi_ratio_linearx2)
    def vgt_ndvi_monndvi(input_file, output_file):

        #ES2- 235 Do not show temporary products like composite not complete (ex monthly composite available mid month...)
        input_file_date = functions.get_date_from_path_full(input_file[0])

        if len(input_file) == 3:
            if not functions.is_date_current_month(input_file_date):
                output_file = functions.list_to_element(output_file)
                functions.check_output_dir(os.path.dirname(output_file))
                args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
                raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   3.C baresoil monthly product (avg)
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("filtered_masks")
    output_sprod = proc_lists.proc_add_subprod("monthly-baresoil", "filtered_masks", final=False,
                                               descriptive_name='Monthly Baresoil',
                                               description='Monthly Baresoil',
                                               frequency_id='e1month',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)

    input_subprod_baresoil_linearx2 = "baresoil-linearx2"
    in_prod_ident_baresoil_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_baresoil_linearx2,mapset, version, ext)

    input_dir_baresoil_linearx2 = es2_data_dir + functions.set_path_sub_directory(prod, input_subprod_baresoil_linearx2, 'Derived', version, mapset)

    starting_files_baresoil_linearx2_all = input_dir_baresoil_linearx2 + "*" + in_prod_ident_baresoil_linearx2

    prod_ident_mon_baresoil = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_mon_baresoil = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})" + in_prod_ident_baresoil_linearx2
    formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_mon_baresoil + "{YYYYMM[0]}" + '01' + prod_ident_mon_baresoil

    @active_if(group_filtered_masks, activate_monthly_baresoil)
    @collate(starting_files_baresoil_linearx2_all, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_baresoil_linearx2)
    def vgt_ndvi_monbaresoil(input_file, output_file):
        #ES2- 235 Do not show temporary products like composite not complete (ex monthly composite available mid month...)
        input_file_date = functions.get_date_from_path_full(input_file[0])

        if len(input_file) == 3:
            if not functions.is_date_current_month(input_file_date):
                output_file = functions.list_to_element(output_file)
                functions.check_output_dir(os.path.dirname(output_file))
                args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
                raster_image_math.do_avg_image(**args)


    #   ---------------------------------------------------------------------
    #   3.b NDVI monthly masks
    #   ---------------------------------------------------------------------
    input_subprod_monndvi = "monndvi"
    #output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)

    in_prod_ident_monndvi = functions.set_path_filename_no_date(prod, input_subprod_monndvi,mapset, version, ext)

    input_dir_monndvi =es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_monndvi, 'Derived', version, mapset)

    starting_files_monndvi = input_dir_monndvi+"*"+in_prod_ident_monndvi

    #   ---------------------------------------------------------------------
    #   3.b NDVI monthly stats
    #   ---------------------------------------------------------------------

    #   ---------------------------------------------------------------------
    #   NDV  avg x month

    output_sprod_group=proc_lists.proc_add_subprod_group("monthly_stats")
    output_sprod=proc_lists.proc_add_subprod("1monavg", "monthly_stats", final=False,
                                             descriptive_name='Monthly Average NDVI',
                                             description='Monthly Average NDVI',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_1monavg = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1monavg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1monavg+"{MMDD[0]}"+prod_ident_1monavg

    @active_if(group_monthly_stats, activate_1monavg)
    @collate(starting_files_monndvi, formatter(formatter_in), formatter_out)
    @follows(vgt_ndvi_monndvi)
    def vgt_ndvi_1monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   NDV  min x month
    output_sprod=proc_lists.proc_add_subprod("1monmin", "monthly_stats", final=False,
                                             descriptive_name='Monthly Minimum NDVI',
                                             description='Monthly Minimum NDVI',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

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
    output_sprod=proc_lists.proc_add_subprod("1monmax", "monthly_stats", final=False,
                                             descriptive_name='Monthly Maximum NDVI',
                                             description='Monthly Maximum NDVI',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

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


    #  ---------------------------------------------------------------------
    #  Monthly standard deviation () ->
    output_sprod=proc_lists.proc_add_subprod("1monstd", "monthly_stats", final=False,
                                             descriptive_name='Monthly Standard deviation NDVI',
                                             description='Monthly Standard deviation NDVI',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_1mondev = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1mondev = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    # formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    # formatter_out="{subpath[0][5]}"+os.path.sep+subdir_1mondev+"{YYYY[0]}{MMDD[0]}"+prod_ident_1mondev
    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1mondev+"{MMDD[0]}"+prod_ident_1mondev

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @active_if(group_monthly_stats, activate_1monstd)
    @follows(vgt_ndvi_1monavg)
    #@transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @collate(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_1monstddev(input_file, output_file):

        #[current_file, avg_file] = input_file
        current_file = [i[0] for i in input_file]
        avg_file = [i[1] for i in input_file][0]

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": current_file, "avg_file": avg_file, "output_format": 'GTIFF', "options": "compress=lzw", "output_stddev":output_file}
        raster_image_math.do_stddev_image(**args)



    #   ---------------------------------------------------------------------
    #   3.d NDVI monthly anomalies
    #   ---------------------------------------------------------------------
    #   ---------------------------------------------------------------------
    #   NDV  Diff x month
    output_sprod=proc_lists.proc_add_subprod("1mondiff", "filtered_anomalies", final=False,
                                             descriptive_name='Monthly Absolute Difference NDVI',
                                             description='Monthly Difference NDVI',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_1mondiff = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1mondiff = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out="{subpath[0][5]}"+os.path.sep+subdir_1mondiff+"{YYYY[0]}{MMDD[0]}"+prod_ident_1mondiff

    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    # formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1mondiff+"{MMDD[0]}"+prod_ident_1mondiff

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @active_if(group_monthly_anomalies, activate_1mondiff)
    @follows(vgt_ndvi_1monavg)
    @transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_1mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   NDV 1monperc

    output_sprod = proc_lists.proc_add_subprod("1monperc", "filtered_anomalies", final=False,
                                               descriptive_name='Monthly Percent Difference',
                                               description='Monthly Percent Difference Precipitation',
                                               frequency_id='e1month',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)
    prod_ident_1monperc = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_1monperc = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    # inputs
    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_monndvi
    formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monperc + "{YYYY[0]}{MMDD[0]}" + prod_ident_1monperc

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @follows(vgt_ndvi_1monavg)
    @active_if(group_monthly_anomalies, activate_1monperc)
    @transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_1monperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file,
                "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #  ---------------------------------------------------------------------
    #   monthly vci_linearx2 (linearx2 - min)/(max - min)  -> min/max per month
    output_sprod=proc_lists.proc_add_subprod("1monvci", "filtered_anomalies", final=False,
                                             descriptive_name='Monthly VCI linearx2',
                                             description='Monthly Vegetation Condition Index',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_vci_linearx2 = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_vci_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    formatter_out = ["{subpath[0][5]}"+os.path.sep+subdir_vci_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci_linearx2]

    ancillary_sprod_1 = "1monmax"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1,mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1  = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    ancillary_sprod_2 = "1monmin"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2,mapset, version, ext)
    ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

    ancillary_sprod_3 = "monthly-baresoil"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3,mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}"+os.path.sep+ancillary_subdir_3+"{YYYY[0]}{MMDD[0]}"+ancillary_sprod_ident_3

    @active_if(group_monthly_anomalies, activate_1monvci)
    @transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input_1,ancillary_input_2, ancillary_input_3), formatter_out)
    @follows(vgt_ndvi_1monmax, vgt_ndvi_1monmin, vgt_ndvi_monbaresoil, vgt_ndvi_icn_linearx2)
    def vgt_ndvi_monthly_vci_linearx2(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        args = {"input_file":current_file, "max_file": max_file,"min_file": min_file, "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file":output_file, "options":"compress = lzw" , "mask_value":no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #   Montly icn(linearx2 - min)/(max - min)  -> min/max absolute

    output_sprod = proc_lists.proc_add_subprod("1monicn", "filtered_anomalies", final=False,
                                               descriptive_name='Monthly ICN linearx2',
                                               description='Monthly Vegetation Condition Index',
                                               frequency_id='e1month',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)

    prod_ident_icn_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_icn_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_monndvi
    formatter_out = ["{subpath[0][5]}" + os.path.sep + subdir_icn_linearx2 + "{YYYY[0]}{MMDD[0]}" + prod_ident_icn_linearx2]

    ancillary_sprod_1 = "absol-max-linearx2"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_1 + "Overall" + ancillary_sprod_ident_1

    ancillary_sprod_2 = "absol-min-linearx2"
    ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, version, ext)
    ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
    ancillary_input_2 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_2 + "Overall" + ancillary_sprod_ident_2

    ancillary_sprod_3 = "monthly-baresoil"
    ancillary_sprod_ident_3 = functions.set_path_filename_no_date(prod, ancillary_sprod_3, mapset, version, ext)
    ancillary_subdir_3 = functions.set_path_sub_directory(prod, ancillary_sprod_3, 'Derived', version, mapset)
    ancillary_input_3 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_3 + "{YYYY[0]}{MMDD[0]}" + ancillary_sprod_ident_3

    @active_if(group_monthly_anomalies, activate_1monicn)
    @transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input_1, ancillary_input_2, ancillary_input_3), formatter_out)
    @follows(vgt_ndvi_absol_min_linearx2, vgt_ndvi_absol_max_linearx2, vgt_ndvi_monbaresoil, vgt_ndvi_monthly_vci_linearx2)
    def vgt_ndvi_monthly_icn_linearx2(input_file, output_file):

        [current_file, max_file, min_file, baresoil_file] = input_file
        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir + os.path.sep + os.path.basename(output_file)

        args = {"input_file": current_file, "max_file": max_file, "min_file": min_file, "output_file": output_file_temp,
                "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file": output_file,
                "options": "compress = lzw", "mask_value": no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)

    #  ---------------------------------------------------------------------
    #  Monthly ratio_linearx2 (linearx2/avg) -> 0-100 % value

    output_sprod = proc_lists.proc_add_subprod("monthly-ratio", "filtered_anomalies", final=False,
                                               descriptive_name='Ratio linearx2',
                                               description='Ratio linearx2 (curr/avg)',
                                               frequency_id='e1month',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='',
                                               active_default=True)

    prod_ident_ratio_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    subdir_ratio_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_monndvi
    formatter_out = ["{subpath[0][5]}" + os.path.sep + subdir_ratio_linearx2 + "{YYYY[0]}{MMDD[0]}" + prod_ident_ratio_linearx2]

    ancillary_sprod = "1monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    ancillary_sprod_1 = "monthly-baresoil"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
    ancillary_input_1 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_1 + "{YYYY[0]}{MMDD[0]}" + ancillary_sprod_ident_1

    @active_if(group_monthly_anomalies, activate_monthly_ratio)
    @transform(starting_files_monndvi, formatter(formatter_in), add_inputs(ancillary_input, ancillary_input_1), formatter_out)
    @follows(vgt_ndvi_1monavg, vgt_ndvi_monbaresoil, vgt_ndvi_monthly_icn_linearx2)
    def vgt_ndvi_monthly_ratio(input_file, output_file):

        [current_file, avg_file, baresoil_file] = input_file

        output_file = functions.list_to_element(output_file)

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir + os.path.sep + os.path.basename(output_file)

        args = {"input_file": [current_file, avg_file], "output_file": output_file_temp, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file": output_file,
                "options": "compress = lzw", "mask_value": no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        shutil.rmtree(tmpdir)


    #   ---------------------------------------------------------------------
    #   Standardized NDVI (aka Z-score)
    output_sprod=proc_lists.proc_add_subprod("1monsndvi", "filtered_anomalies", final=False,
                                             descriptive_name='Monthly Standardized NDVI',
                                             description='Monthly Standardized NDVI',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    prod_ident_1monsndvi = functions.set_path_filename_no_date(prod, output_sprod,mapset, version, ext)
    subdir_1monsndvi = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    input_subprod_mondiff = "1mondiff"
    #output_sprod = proc_lists.proc_add_subprod("monndvi", "monthly_prod", False, True)

    in_prod_ident_mondiff = functions.set_path_filename_no_date(prod, input_subprod_mondiff,mapset, version, ext)

    input_dir_mondiff=es2_data_dir+ \
                       functions.set_path_sub_directory(prod, input_subprod_mondiff, 'Derived', version, mapset)

    starting_files_mondiff = input_dir_mondiff+"*"+in_prod_ident_mondiff


    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_mondiff
    formatter_out="{subpath[0][5]}"+os.path.sep+subdir_1monsndvi+"{YYYY[0]}{MMDD[0]}"+prod_ident_1monsndvi

    # formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
    # formatter_out = "{subpath[0][5]}"+os.path.sep+subdir_1mondiff+"{MMDD[0]}"+prod_ident_1mondiff

    ancillary_sprod = "1monstd"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+ "{MMDD[0]}" +ancillary_sprod_ident

    @active_if(group_monthly_anomalies, activate_1monsndvi)
    #@follows(vgt_ndvi_1mondiff, vgt_ndvi_1monstddev)
    @transform(starting_files_mondiff, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def vgt_ndvi_1monsndvi(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_division_perc(**args)


    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline
def processing_std_ndvi(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                        pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                        starting_dates_linearx2=None, update_stats=False, nrt_products=True, write2file=None, logfile=None,
                        touch_files_only=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_ndvi')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates_linearx2=starting_dates_linearx2, update_stats=update_stats,
                                 nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, touch_files_only=touch_files_only, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_'+prod+'_'+version+'.sqlite'),
                     checksum_level=0)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level) #, output_stream=fout)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True


def processing_std_ndvi_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, write2file=None,logfile=None,touch_files_only=False):

    result = processing_std_ndvi(res_queue, pipeline_run_level=pipeline_run_level,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates_linearx2=starting_dates,
                                                               nrt_products=False,
                                                               update_stats=True,
                                                               write2file=write2file,
                                                               logfile=logfile,
                                                               touch_files_only=touch_files_only)

    return result

def processing_std_ndvi_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None,touch_files_only=False):

    result = processing_std_ndvi(res_queue, pipeline_run_level=pipeline_run_level,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates_linearx2=starting_dates,
                                                               nrt_products=True,
                                                               update_stats=False,
                                                               write2file=write2file,
                                                               logfile=logfile,
                                                               touch_files_only=touch_files_only)

    return result

def processing_std_ndvi_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, logfile=None,touch_files_only=False):

    result = processing_std_ndvi(res_queue, pipeline_run_level=pipeline_run_level,
                                                               pipeline_printout_level=pipeline_printout_level,
                                                               pipeline_printout_graph_level=pipeline_printout_graph_level,
                                                               prod=prod,
                                                               starting_sprod=starting_sprod,
                                                               mapset=mapset,
                                                               version=version,
                                                               starting_dates_linearx2=starting_dates,
                                                               nrt_products=True,
                                                               update_stats=True,
                                                               logfile=logfile,
                                                               touch_files_only=touch_files_only)

    return result
