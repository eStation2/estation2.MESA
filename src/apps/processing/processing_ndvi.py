#
#	purpose: Define the processing chain for ndvi
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 25.06.2014
#   descr:	 Generate additional Derived products /implements processing chains
#	history: 1.0
#

# source my definitions
from config import es_constants

# Import std modules
import glob
import os

# Import eStation2 modules
from config import es_constants
from database import querydb
from lib.python import functions
from lib.python import metadata
from lib.python.image_proc import raster_image_math
from database import crud
from apps.processing.processing_switches import *
from lib.python import es_logging as log

# Import third-party modules
from ruffus import *

logger = log.my_logger(__name__)

#   Still to be done

#   General definitions for this processing chain
prod = "vgt_ndvi"
mapset = 'WGS84_Sahel_1km'
ext = '.tif'
version = 'undefined'

#
#   Rational for 'active' flags:
#   A flag is defined for each product, with name 'activate_'+ prodname, ans initialized to 1: it is
#   deactivated only for optimization  - for 'secondary' products
#   In working conditions, products are activated by groups (for simplicity-clarity)
#
#   A list of 'final' (i.e. User selected) output products are defined (now hard-coded)
#   According to the dependencies, if set, they force the various groups

#   switch wrt to groups
group_no_filter_stats = 1                  # 1.a
group_no_filter_anomalies = 1              # 1.b    -> To be done

group_filtered_prods = 1                   # 2.a
group_filtered_stats = 1                   # 2.b
group_filtered_masks = 1                   # 2.c
group_filtered_anomalies = 1               # 2.d

group_monthly_prods = 1                    # 3.a
group_monthly_stats = 1                    # 3.b
group_monthly_masks = 1                    # 3.c    -> To be Done
group_monthly_anomalies = 1                # 3.d    -> To be done

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

#   ---------------------------------------------------------------------
#   Define input files (NDV)
starting_sprod = 'ndv'
in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, ext)

logger.debug('Base data directory is: %s' % es_constants.processing_dir)
input_dir = es_constants.processing_dir+ \
            functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

logger.debug('Input data directory is: %s' % input_dir)
starting_files = input_dir+"*"+in_prod_ident
logger.debug('Starting files wild card is: %s' % starting_files)

#   ---------------------------------------------------------------------
#   1.a 10Day non-filtered Stats
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------
#   NDV avg x dekad (i.e. avg_dekad)
output_sprod = "10davg"
prod_ident_10davg = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10davg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10davg+"{MMDD[0]}"+prod_ident_10davg]

@active_if(group_no_filter_stats, activate_10davg_no_filter)
@collate(starting_files, formatter(formatter_in),formatter_out)
def vgt_ndvi_10davg_no_filter(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_avg_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   NDV min x dekad (i.e. min_dekad)
output_sprod = "10dmin"

prod_ident_10dmin = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmin = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmin+"{MMDD[0]}"+prod_ident_10dmin]

@active_if(group_no_filter_stats, activate_10dmin_no_filter)
@collate(starting_files, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_10davg_no_filter)
def vgt_ndvi_10dmin_no_filter(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_min_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   NDV max x dekad (i.e. max_dekad)
output_sprod = "10dmax"
prod_ident_10dmax = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmax = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmax+"{MMDD[0]}"+prod_ident_10dmax]

@active_if(group_no_filter_stats, activate_10dmax_no_filter)
@collate(starting_files, formatter(formatter_in), formatter_out)
@follows(vgt_ndvi_10dmin_no_filter)
def vgt_ndvi_10dmax_no_filter(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_max_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   NDV std x dekad (i.e. std_dekad)
output_sprod = "10DSTD"


#  ---------------------------------------------------------------------
#   NDV med x dekad (i.e. med_dekad)

output_sprod = "10dmed"

prod_ident_10dmed = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmed = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmed+"{MMDD[0]}"+prod_ident_10dmed]

@active_if(group_no_filter_stats, activate_10dmed_no_filter)
@collate(starting_files, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_10dmax_no_filter)
def vgt_ndvi_10dmed_no_filter(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_med_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   1.b 10Day non-filtered Anomalies
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------
#   2.a NDVI linearx1/x2
#   ---------------------------------------------------------------------

output_sprod = "ndvi_linearx1"
prod_ident_linearx1 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_linearx1 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

def generate_parameters_ndvi_linearx1():

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files)
        input_files.sort()

        for file_t0 in input_files:
            # Get current date
            date_t0 = functions.get_date_from_path_full(file_t0)
            output_file = es_constants.processing_dir+subdir_linearx1+str(date_t0)+prod_ident_linearx1

            # Get files at t-1 and t+1
            adjac_files = functions.files_temp_ajacent(file_t0)

            if len(adjac_files) == 2:

                # Prepare and return arguments
                three_files_in_a_row = [adjac_files[0], file_t0, adjac_files[1]]
                yield (three_files_in_a_row, output_file)

@files(generate_parameters_ndvi_linearx1)
@follows(vgt_ndvi_10dmed_no_filter)
@active_if(group_filtered_prods, activate_ndvi_linearx1)
def vgt_ndvi_linearx1(input_files, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_files[1], "before_file":input_files[0], "after_file": input_files[2], "output_file": output_file,
             "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
    print args
    raster_image_math.do_ts_linear_filter(**args)


output_sprod = "ndvi_linearx2"
prod_ident_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

def generate_parameters_ndvi_linearx2():

        wild_card_linearx1 = es_constants.processing_dir+subdir_linearx1+'*'+prod_ident_linearx1
        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(wild_card_linearx1)
        input_files.sort()

        for file_t0 in input_files:
            # Get current date
            date_t0 = functions.get_date_from_path_full(file_t0)
            output_file = es_constants.processing_dir+subdir_linearx2+str(date_t0)+prod_ident_linearx2

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
in_prod_ident_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_linearx2, mapset, ext)

input_dir_linearx2 = es_constants.processing_dir+ \
                   functions.set_path_sub_directory(prod, input_subprod_linearx2, 'Derived', version, mapset)

starting_files_linearx2 = input_dir_linearx2+"*"+in_prod_ident_linearx2

#   ---------------------------------------------------------------------
#   Linearx2 avg x dekad
output_sprod = "10davg_linearx2"
prod_ident_10davg_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10davg_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

@active_if(group_filtered_stats, activate_10davg_linearx2)
@collate(starting_files_linearx2,
         formatter("[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2),
         ["{subpath[0][4]}"+os.path.sep+subdir_10davg_linearx2+"{MMDD[0]}"+prod_ident_10davg_linearx2])
@follows(vgt_ndvi_linearx2)
def vgt_ndvi_10davg_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_avg_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   Linearx2 min x dekad
output_sprod = "10dmin_linearx2"

prod_ident_10dmin_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmin_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmin_linearx2+"{MMDD[0]}"+prod_ident_10dmin_linearx2]

@active_if(group_filtered_stats, activate_10dmin_linearx2)
@collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_linearx2)
def vgt_ndvi_10dmin_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_min_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   Linearx2 max x dekad
output_sprod = "10dmax_linearx2"
prod_ident_10dmax_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmax_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmax_linearx2+"{MMDD[0]}"+prod_ident_10dmax_linearx2]

@active_if(group_filtered_stats, activate_10dmax_linearx2)
@collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_linearx2)
def vgt_ndvi_10dmax_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_max_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   Linearx2 std x dekad
output_sprod = "10dstd"


#  ---------------------------------------------------------------------
#   Linearx2 med x dekad

output_sprod = "10dmed_linearx2"

prod_ident_10dmed_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_10dmed_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_10dmed_linearx2+"{MMDD[0]}"+prod_ident_10dmed_linearx2]

@active_if(group_filtered_stats, activate_10dmed_linearx2)
@collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_linearx2)
def vgt_ndvi_10dmed_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_med_image(**args)
    #upsert_processed_ruffus(output_file)

#  ---------------------------------------------------------------------
#   Linearx2 min x year

output_sprod = "year_min_linearx2"

prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_year_min_linearx2   = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_year_min_linearx2+"{YYYY[0]}"+prod_ident_year_min_linearx2]

@active_if(group_filtered_stats, activate_year_min_linearx2)
@collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_10dmin_linearx2)
def vgt_ndvi_year_min_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_min_image(**args)
    #upsert_processed_ruffus(output_file)

#  ---------------------------------------------------------------------
#   Linearx2 max x year

output_sprod = "year_max_linearx2"

prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_year_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})[0-9]{4}"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_year_max_linearx2+"{YYYY[0]}"+prod_ident_year_max_linearx2]

@active_if(group_filtered_stats, activate_year_max_linearx2)
@collate(starting_files_linearx2, formatter(formatter_in),formatter_out)
@follows(vgt_ndvi_10dmax_linearx2)
def vgt_ndvi_year_max_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_max_image(**args)
    #upsert_processed_ruffus(output_file)

#  ---------------------------------------------------------------------
#   Linearx2 absolute min: Starting files re-initialized to year-min
#   ---------------------------------------------------------------------

input_subprod_year_min_linearx2 = "year_min_linearx2"
in_prod_ident_year_min_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_min_linearx2, mapset, ext)

input_dir_year_min_linearx2 = es_constants.processing_dir+ \
                   functions.set_path_sub_directory(prod, input_subprod_year_min_linearx2, 'Derived', version, mapset)

starting_files_year_min_linearx2 = input_dir_year_min_linearx2+"*"+in_prod_ident_year_min_linearx2

#  ---------------------------------------------------------------------
output_sprod = "absol_min_linearx2"
prod_ident_absol_min_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_absol_min_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}"+in_prod_ident_year_min_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_absol_min_linearx2+'Overall'+prod_ident_absol_min_linearx2]

@active_if(group_filtered_stats, activate_absol_min_linearx2)
@collate(starting_files_year_min_linearx2, formatter(formatter_in), formatter_out)
@follows(vgt_ndvi_year_min_linearx2)
def vgt_ndvi_absol_min_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_min_image(**args)
    #upsert_processed_ruffus(output_file)

#  ---------------------------------------------------------------------
#   Linearx2 absolute max

input_subprod_year_max_linearx2 = "year_max_linearx2"
in_prod_ident_year_max_linearx2 = functions.set_path_filename_no_date(prod, input_subprod_year_max_linearx2, mapset, ext)

input_dir_year_max_linearx2 = es_constants.processing_dir+ \
                   functions.set_path_sub_directory(prod, input_subprod_year_max_linearx2, 'Derived', version, mapset)

starting_files_year_max_linearx2 = input_dir_year_max_linearx2+"*"+in_prod_ident_year_max_linearx2

#  ---------------------------------------------------------------------
output_sprod = "absol_max_linearx2"
prod_ident_absol_max_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_absol_max_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}"+in_prod_ident_year_max_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_absol_max_linearx2+'Overall'+prod_ident_absol_max_linearx2]

@active_if(group_filtered_stats, activate_absol_max_linearx2)
@collate(starting_files_year_max_linearx2, formatter(formatter_in), formatter_out)
@follows(vgt_ndvi_year_max_linearx2)
def vgt_ndvi_absol_max_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_max_image(**args)
    #upsert_processed_ruffus(output_file)

#   ---------------------------------------------------------------------
#   2.b NDVI_baresoil mask
#       TODO-M.C.: FTTB does not use min/max ... to be changed ??
#   ---------------------------------------------------------------------
#   ---------------------------------------------------------------------
#
output_sprod = "baresoil_linearx2"
prod_ident_baresoil_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_baresoil_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYYMMDD>[0-9]{8})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_baresoil_linearx2+"{YYYYMMDD[0]}"+prod_ident_baresoil_linearx2]

@active_if(group_filtered_masks, activate_baresoil_linearx2)
@transform(starting_files_linearx2, formatter(formatter_in), formatter_out)
@follows(vgt_ndvi_absol_max_linearx2)
def vgt_ndvi_baresoil_linearx2(input_file, output_file):

    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    print args
    raster_image_math.do_make_baresoil(**args)

#   ---------------------------------------------------------------------
#   2.c NDVI_linearx2 anomalies
#   ---------------------------------------------------------------------

#  ---------------------------------------------------------------------
#   'diff' vs. avg_filtered (NDV - avg_dekad_filtered)

output_sprod = "diff_linearx2"
prod_ident_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_diff_linearx2]

ancillary_sprod = "10davg_linearx2"
ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
ancillary_input = "{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident


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

output_sprod = "linearx2diff_linearx2"
prod_ident_linearx2_diff_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_linearx2_diff_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_linearx2_diff_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_linearx2_diff_linearx2]

ancillary_sprod = "10davg_linearx2"
ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, ext)
ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
ancillary_input = "{subpath[0][4]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident


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
# prod_ident_stddiff2avg_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
# subdir_stddiff2avg_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)
#
# formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
# formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_stddiff2avg_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_stddiff2avg_linearx2]
#
# ancillary_sprod_1 = "10DAVG_LINEARX2"
# ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
# ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
# ancillary_input_1  = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1
#
# ancillary_sprod_2 = "10DSTD_LINEARX2"
# ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
# ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
# ancillary_input_2 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2
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

output_sprod = "vci"
prod_ident_vci = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_vci = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_vci+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci]

ancillary_sprod_1 = "10dmax_linearx2"
ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
ancillary_input_1 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

ancillary_sprod_2 = "10dmin_linearx2"
ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
ancillary_input_2 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

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

output_sprod = "icn"
prod_ident_icn = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_icn = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_icn+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn]

ancillary_sprod_1 = "absol_max_linearx2"
ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
ancillary_input_1  = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

ancillary_sprod_2 = "absol_min_linearx2"
ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
ancillary_input_2 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

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

output_sprod = "vci_linearx2"
prod_ident_vci_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_vci_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_vci_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_vci_linearx2]

ancillary_sprod_1 = "10dmax_linearx2"
ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
ancillary_input_1  = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

ancillary_sprod_2 = "10dmin_linearx2"
ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
ancillary_subdir_2     = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
ancillary_input_2 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"{MMDD[0]}"+ancillary_sprod_ident_2

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

output_sprod = "icn_linearx2"
prod_ident_icn_linearx2 = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_icn_linearx2 = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident_linearx2
formatter_out = ["{subpath[0][4]}"+os.path.sep+subdir_icn_linearx2+"{YYYY[0]}{MMDD[0]}"+prod_ident_icn_linearx2]

ancillary_sprod_1 = "absol_max_linearx2"
ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, ext)
ancillary_subdir_1 = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived', version, mapset)
ancillary_input_1 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_1+"Overall"+ancillary_sprod_ident_1

ancillary_sprod_2 = "absol_min_linearx2"
ancillary_sprod_ident_2 = functions.set_path_filename_no_date(prod, ancillary_sprod_2, mapset, ext)
ancillary_subdir_2 = functions.set_path_sub_directory(prod, ancillary_sprod_2, 'Derived', version, mapset)
ancillary_input_2 = "{subpath[0][4]}"+os.path.sep+ancillary_subdir_2+"Overall"+ancillary_sprod_ident_2

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
output_sprod = "monndvi"
prod_ident_mon_ndvi = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_mon_ndvi = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident_linearx2
formatter_out = "{subpath[0][4]}"+os.path.sep+subdir_mon_ndvi+"{YYYYMM[0]}"+'01'+prod_ident_mon_ndvi

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
in_prod_ident_monndvi = functions.set_path_filename_no_date(prod, input_subprod_monndvi, mapset, ext)

input_dir_monndvi = es_constants.processing_dir+ \
                   functions.set_path_sub_directory(prod, input_subprod_monndvi, 'Derived', version, mapset)

starting_files_monndvi = input_dir_monndvi+"*"+in_prod_ident_monndvi

#   ---------------------------------------------------------------------
#   3.c NDVI monthly stats
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------
#   NDV  avg x month
output_sprod = "1monavg"
prod_ident_1monavg = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_1monavg = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
formatter_out = "{subpath[0][4]}"+os.path.sep+subdir_1monavg+"{MMDD[0]}"+prod_ident_1monavg

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
output_sprod = "1monmin"
prod_ident_1monmin = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_1monmin = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
formatter_out = "{subpath[0][4]}"+os.path.sep+subdir_1monmin+"{MMDD[0]}"+prod_ident_1monmin

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
output_sprod = "1monmax"
prod_ident_1monmax = functions.set_path_filename_no_date(prod, output_sprod, mapset, ext)
subdir_1monmax = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident_monndvi
formatter_out = "{subpath[0][4]}"+os.path.sep+subdir_1monmax+"{MMDD[0]}"+prod_ident_1monmax

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
def processing_ndvi(pipeline_run_level=0, pipeline_run_touch_only=0, pipeline_printout_level=0,
                           pipeline_printout_graph_level=0):

    logger.info("Entering routine %s" % 'processing_vgt_ndvi')
    if pipeline_run_level > 0:
        pipeline_run(verbose=pipeline_run_level, touch_files_only=pipeline_run_touch_only, multiprocess=4)

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
