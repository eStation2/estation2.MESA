from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define a processing chain for 'modis-firms' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 05.05.2016
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0
#

# Source generic modules
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import glob, datetime
import tempfile
import shutil

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from apps.processing import proc_functions

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext = es_constants.ES2_OUTFILE_EXTENSION


def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None,
                    starting_dates_stats=None, update_stats=False, nrt_products=True):
    #   ---------------------------------------------------------------------
    #   Create lists to store definition of the derived products, and their
    #   groups.
    #   Two starting dates ranges are passed:
    #
    #       starting_dates: range - 1d frequency - for 1day -> 10dcount
    #                       Normally not used: only for tests (the number of 1day files i large!)
    #
    #       starting_dates_stats: range - 10d frequency - for 10dcount -> 10dcountmin/max/avg
    #                             Used to define a specific range for stats, normally 20030101 -> <prev-year>1221
    #
    #   For the 10d products anomalies (both 1km and 10km) ALL available files are used for anomaly computation
    #
    #   ---------------------------------------------------------------------

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    #   ---------------------------------------------------------------------
    #   Define and assign the flags to control the individual derived products
    #   and the groups. NOT to be changed by the User
    #   ---------------------------------------------------------------------

    # Set DEFAULTS: all off
    activate_10dcount_comput = 0  # 2.a - 10d count
    activate_10dstats_comput = 0  # 2.b - 10d stats
    activate_10danomalies_comput = 0  # 2.c - 10d anomalies
    activate_10d_10k_comput = 0  # 3.a - 10d on 10km cells
    activate_10d_10k_stats_comput = 0  # 3.b - 10d on 10km statistics
    activate_10d_10k_anom_comput = 0  # 3.c - 10d on 10km anomalies

    #   switch wrt groups - according to options
    if nrt_products:
        activate_10dcount_comput = 1  # 10d count
        activate_10danomalies_comput = 1  # 10d anomalies
        activate_10d_10k_comput = 1  # 10d on 10k
        activate_10d_10k_anom_comput = 1  # 10d on 10km anomalies

    if update_stats:
        activate_10dstats_comput = 1  # 10d stats
        activate_10d_10k_stats_comput = 1  # 10d on 10km statistics

    #   Switch wrt single products: not to be changed !!

    # 2.b -> 10d stats
    activate_10dcountavg_comput = 1
    activate_10dcountmin_comput = 1
    activate_10dcountmax_comput = 1

    # 2.c -> 10d anomalies
    activate_10ddiff_comput = 1

    # 3.a -> 10d on 10 km
    activate_10dcount10k_comput = 1

    # 3.b -> 10d on 10 km stats
    activate_10dcount10kavg_comput = 1
    activate_10dcount10kmin_comput = 1
    activate_10dcount10kmax_comput = 1

    # 3.c -> 10d on 10 km anomalies
    activate_10dcount10kdiff_comput = 1
    activate_10dcount10kperc_comput = 1
    activate_10dcount10kratio_comput = 1

    #   ---------------------------------------------------------------------
    #   Define the 'grid' file for the 10k count conversion
    #   If it does not exists, disable computation
    #   ---------------------------------------------------------------------

    grid_mapset_name = 'SPOTV-Africa-1km'
    # grid_file='/eStation2/layers/Mask_Africa_SPOTV_10km.tif'
    grid_file = es_constants.es2globals['estation2_layers_dir'] + os.path.sep + 'Mask_Africa_SPOTV_10km.tif'

    if not os.path.isfile(grid_file):
        activate_10d_10k_comput = 0  # 10d on 10km
        activate_10d_10k_anom_comput = 0  # 10d on 10km anomalies
        activate_10d_10k_stats_comput = 0  # 10d on 10km statistics

    es2_data_dir = es_constants.es2globals['processing_dir'] + os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files from the starting_sprod and starting_dates arguments
    #   ---------------------------------------------------------------------

    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    # logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir + \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    # starting_dates -> 1 day
    if starting_dates is not None:
        starting_files_1day = []
        for my_date in starting_dates:
            starting_files_1day.append(input_dir + my_date + in_prod_ident)
    else:
        starting_files_1day = glob.glob(input_dir + "*" + in_prod_ident)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount")
    output_sprod = proc_lists.proc_add_subprod("10dcount", "10dcount", final=False,
                                               descriptive_name='10d Count',
                                               description='Fire Count for dekad',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident_10dcount = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_10dcount = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_10dcount():

        #   Look for all input files in input_dir, and sort them
        input_files = starting_files_1day
        dekad_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename = os.path.basename(input_file)
            mydate = functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd = str(mydate)[0:8]
            mydekad_nbr = functions.conv_date_2_dekad(mydate_yyyymmdd)
            if mydekad_nbr not in dekad_list:
                dekad_list.append(mydekad_nbr)

        dekad_list = sorted(dekad_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        dekad_now = functions.conv_date_2_dekad(today_str)

        for dekad in dekad_list:
            # Exclude the current dekad
            if dekad != dekad_now:
                file_list = []
                my_dekad_str = functions.conv_dekad_2_date(dekad)
                for input_file in input_files:

                    basename = os.path.basename(input_file)
                    mydate_yyyymmdd = functions.get_date_from_path_filename(basename)
                    mydekad_nbr = functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(input_file)

                    output_file = es_constants.processing_dir + output_subdir_10dcount + os.path.sep + my_dekad_str + out_prod_ident_10dcount

                yield (file_list, output_file)

    @active_if(activate_10dcount_comput)
    @files(generate_parameters_10dcount)
    def std_fire_10dcount(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcountavg
    #   ---------------------------------------------------------------------

    if starting_dates_stats is not None:
        files_10dcount_4stats = []
        for my_date in starting_dates_stats:
            files_10dcount_4stats.append(es2_data_dir + output_subdir_10dcount + my_date + out_prod_ident_10dcount)
    else:
        files_10dcount_4stats = es2_data_dir + output_subdir_10dcount + "*" + out_prod_ident_10dcount

    output_sprod_group = proc_lists.proc_add_subprod_group("10dstats")
    output_sprod = proc_lists.proc_add_subprod("10dcountavg", "10dstats", final=False,
                                               descriptive_name='10d Fire Average',
                                               description='Average fire for dekad',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount
    formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountavg_comput)
    @collate(files_10dcount_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcount)
    def std_fire_10dcountavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768}
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':0}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcountmin
    #   ---------------------------------------------------------------------

    output_sprod = proc_lists.proc_add_subprod("10dcountmin", "10dstats", final=False,
                                               descriptive_name='10d Fire Minimum',
                                               description='Minimum Fire for dekad',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount
    formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountmin_comput)
    @collate(files_10dcount_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcountavg)
    def std_fire_10dcountmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        # The coded value (nodata=0) leads to the wrong result
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", "input_nodata": -32768}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcountmax
    #   ---------------------------------------------------------------------
    output_sprod = proc_lists.proc_add_subprod("10dcountmax", "10dstats", final=False,
                                               descriptive_name='10d Maximum',
                                               description='Maximum rainfall for dekad',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount
    formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dcountmax_comput)
    @collate(files_10dcount_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcountmin)
    def std_fire_10dcountmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dDiff
    #   ---------------------------------------------------------------------

    #   Define the input files for conversion to 10k on the basis of the 'starting_dates' (not 'starting_dates_stats')
    if starting_dates is not None:
        files_10dcount_4anom = []
        use_dates_10dcount = proc_functions.get_list_dates_for_dataset(prod, '10dcount', version,
                                                                       start_date=starting_dates[0],
                                                                       end_date=starting_dates[-1])

        for my_date in use_dates_10dcount:
            files_10dcount_4anom.append(es2_data_dir + output_subdir_10dcount + my_date + out_prod_ident_10dcount)
    else:
        files_10dcount_4anom = glob.glob(es2_data_dir + output_subdir_10dcount + "*" + out_prod_ident_10dcount)

    output_sprod_group = proc_lists.proc_add_subprod_group("10danomalies")
    output_sprod = proc_lists.proc_add_subprod("10dcountdiff", "10danomalies", final=False,
                                               descriptive_name='10d Absolute Difference',
                                               description='10d Absolute Difference vs. LTA',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

    ancillary_sprod = "10dcountavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    # @follows(std_fire_10dcountavg)
    @active_if(activate_10danomalies_comput, activate_10ddiff_comput)
    @transform(files_10dcount_4anom, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(std_fire_10dcountmax)
    def std_fire_10dcountdiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768, 'output_nodata': -32768}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10km
    #   ---------------------------------------------------------------------
    #
    target_mapset_name = 'SPOTV-Africa-10km'

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10k")
    output_sprod_10dcount10k = proc_lists.proc_add_subprod("10dcount10k", "10dcount10k", final=False,
                                                           descriptive_name='10d Gridded at 10 km',
                                                           description='10d Count Gridded at 10 km',
                                                           frequency_id='e1dekad',
                                                           date_format='YYYYMMDD',
                                                           masked=False,
                                                           timeseries_role='10d',
                                                           active_default=True)

    out_prod_ident_10dcount10k = functions.set_path_filename_no_date(prod, output_sprod_10dcount10k, target_mapset_name,
                                                                     version, ext)
    output_subdir_10dcount10k = functions.set_path_sub_directory(prod, output_sprod_10dcount10k, 'Derived', version,
                                                                 target_mapset_name)

    #   Starting files + avg
    formatter_in = "(?P<YYYYMMDD>[0-9]{8})" + out_prod_ident_10dcount
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir_10dcount10k + "{YYYYMMDD[0]}" + out_prod_ident_10dcount10k

    @active_if(activate_10d_10k_comput, activate_10dcount10k_comput)
    @transform(files_10dcount_4anom, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcountdiff)
    def std_fire_10dcount10k(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir + os.path.sep + os.path.basename(output_file)
        input_mapset_name = mapset

        operation = 'sum'
        args = {"input_file": input_file, "grid_file": grid_file, "output_file": output_file_temp,
                "operation": operation, "input_mapset_name": input_mapset_name, "grid_mapset_name": grid_mapset_name,
                "output_format": None, 'nodata': -32768, "options": "compress=lzw", "output_type": 'Int16'}

        raster_image_math.do_stats_4_raster(**args)

        args = {"inputfile": output_file_temp, "output_file": output_file, "native_mapset_name": grid_mapset_name,
                "target_mapset_name": target_mapset_name}

        raster_image_math.do_reproject(**args)

        shutil.rmtree(tmpdir)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kavg
    #   ---------------------------------------------------------------------

    if starting_dates_stats is not None:
        files_10dcount10k_4stats = []
        for my_date in starting_dates_stats:
            files_10dcount10k_4stats.append(
                es2_data_dir + output_subdir_10dcount10k + my_date + out_prod_ident_10dcount10k)
    else:
        files_10dcount10k_4stats = es2_data_dir + output_subdir_10dcount10k + "*" + out_prod_ident_10dcount10k

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kstats")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kavg", "10dcount10kstats", final=False,
                                               descriptive_name='10d Fire count 10km Average',
                                               description='10d Fire count 10km Average',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

    @active_if(activate_10d_10k_stats_comput, activate_10dcount10kavg_comput)
    @collate(files_10dcount10k_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcount10k)
    def std_fire_10dcount10kavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768}
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': 0}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kmin
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kstats")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kmin", "10dcount10kstats", final=False,
                                               descriptive_name='10d Fire count 10km minimum',
                                               description='10d Fire count 10km minimum',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

    @active_if(activate_10d_10k_stats_comput, activate_10dcount10kmin_comput)
    @collate(files_10dcount10k_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcount10kavg)
    def std_fire_10dcount10kmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Int16', 'input_nodata': -32768}
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type': 'Int16', 'input_nodata': 0}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kmax
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kstats")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kmax", "10dcount10kstats", final=False,
                                               descriptive_name='10d Fire count 10km maximum',
                                               description='10d Fire count 10km maximum',
                                               frequency_id='e1dekad',
                                               date_format='MMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident

    @active_if(activate_10d_10k_stats_comput, activate_10dcount10kmax_comput)
    @collate(files_10dcount10k_4stats, formatter(formatter_in), formatter_out)
    @follows(std_fire_10dcount10kmin)
    def std_fire_10dcount10kmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Int16', 'input_nodata': -32768}
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type': 'Int16', 'input_nodata': 0}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kdiff
    #   ---------------------------------------------------------------------

    #   Define the input files for conversion to 10k on the basis of the 'starting_dates' (not 'starting_dates_stats')
    if starting_dates is not None:
        files_10dcount10k_4anom = []
        use_dates_10dcount10k = proc_functions.get_list_dates_for_dataset(prod, '10dcount10k', version,
                                                                          start_date=starting_dates[0],
                                                                          end_date=starting_dates[-1])

        for my_date in use_dates_10dcount10k:
            files_10dcount10k_4anom.append(
                es2_data_dir + output_subdir_10dcount10k + my_date + out_prod_ident_10dcount10k)
    else:
        files_10dcount10k_4anom = glob.glob(es2_data_dir + output_subdir_10dcount10k + "*" + out_prod_ident_10dcount10k)

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kanomalies")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kdiff", "10dcount10kanomalies", final=False,
                                               descriptive_name='10d 10 km Absolute Difference',
                                               description='10d 10 km Absolute Difference vs. LTA',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

    ancillary_sprod = "10dcount10kavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, target_mapset_name, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, target_mapset_name)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @active_if(activate_10d_10k_anom_comput, activate_10dcount10kdiff_comput)
    @transform(files_10dcount10k_4anom, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(std_fire_10dcount10kmax)
    def std_fire_10dcount10kdiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768, 'output_nodata': -32768}
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':-32768}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kperc
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kanomalies")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kperc", "10dcount10kanomalies", final=False,
                                               descriptive_name='10d 10 km Percent Difference',
                                               description='10d 10 km Percent Difference vs. LTA',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

    ancillary_sprod = "10dcount10kavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, target_mapset_name, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, target_mapset_name)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @active_if(activate_10d_10k_anom_comput, activate_10dcount10kperc_comput)
    @transform(files_10dcount10k_4anom, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(std_fire_10dcount10kdiff)
    def std_fire_10dcount10kperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        # args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':-32768}
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file,
                "output_format": 'GTIFF', "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768,
                'output_nodata': -32768}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcount10kratio
    #   ---------------------------------------------------------------------

    output_sprod_group = proc_lists.proc_add_subprod_group("10dcount10kanomalies")
    output_sprod = proc_lists.proc_add_subprod("10dcount10kratio", "10dcount10kanomalies", final=False,
                                               descriptive_name='10d 10 km Ratio with AVG',
                                               description='10d 10 km Ratio with LTA AVG',
                                               frequency_id='e1dekad',
                                               date_format='YYYYMMDD',
                                               masked=False,
                                               timeseries_role='10d',
                                               active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, target_mapset_name, version, ext)
    output_subdir = functions.set_path_sub_directory(prod, output_sprod, 'Derived', version, target_mapset_name)

    #   Starting files + avg
    formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + out_prod_ident_10dcount10k
    formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

    ancillary_sprod = "10dcount10kavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, target_mapset_name, version, ext)
    ancillary_subdir = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, target_mapset_name)
    ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    @active_if(activate_10d_10k_anom_comput, activate_10dcount10kratio_comput)
    @transform(files_10dcount10k_4anom, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    @follows(std_fire_10dcount10kperc)
    def std_fire_10dcount10kratio(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", 'output_type':'Float32', 'input_nodata':-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768, 'output_nodata': -32768}
        raster_image_math.do_oper_division_perc(**args)

    #
    # End of pipeline definition
    return proc_lists


#   ---------------------------------------------------------------------
#   Drive the pipeline: 4 functions are defined, a main one:
#
#       processing_std_modis_firms -> create and run the pipeline
#
#   and 3 'wrappers' to call it with specific options:
#
#   processing_std_modis_firms_stats_only: -> compute/updates only 10dcount 'stats' (avg/min/max)
#   processing_std_modis_firms_prods_only: -> compute/updates only 10dcount and anomalies (10dcountdiff)
#   processing_std_modis_firms_all: -> compute/updates all derived products
#
#   NOTE: the rational for the 3 wrappers is to have a function for direct call from the 'Processing' Service
#         In development/debug calling one of the wrapper or the main function (with the options set) is equivalent.
#
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------
#
#   Function:   processing_std_modis_firms
#   Purpose:    create and run the pipeline
#   Arguments: OUT: res_queue -> returns the list of derived products and their groups
#              IN:  pipeline_run_level      -> set to >=1 to have the chain executed, with increasing level of verbosity
#              IN:  pipeline_printout_level -> set to >=1 to have the 'dry-run' the chain, with increasing level of verbosity
#              IN:  pipeline_printout_graph_level -> not used
#              IN:  prod                    -> name of the product (modis-firms)
#              IN:  mapset                  -> name of the mapset (e.g. SPOTV-Africa-1km)
#              IN:  version                 -> name of the product-version (e.g. v5.0)
#              IN:  starting_dates          -> list of dates to be considered for the input sub-product.
#                                              If empty, all existing dates in the filesystem are considered
#              IN:  update_stats            -> option (True/False) to update 10dcount stats (min/max/avg)
#              IN:  nrt_products            -> option (True/False) to update the near-real time products (10dcount and 10dcountdiff)
#              IN:  write2file              -> name of the file where to report the tasks to be executed
#                                              Used only by pipeline_printout (dry-run)
#              IN:  logfile                 -> Name of the logfile
#
#   ---------------------------------------------------------------------


def processing_std_modis_firms(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                               pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                               starting_dates=None, starting_dates_stats=None, update_stats=False, nrt_products=True,
                               write2file=None,
                               logfile=None, touch_files_only=False):
    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_modis_firms')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates_stats=starting_dates_stats, starting_dates=starting_dates,
                                 proc_lists=proc_lists,
                                 update_stats=update_stats, nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id = open(write2file, 'w')
    else:
        fwrite_id = None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_modis_firms')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger,
                     history_file=os.path.join(es_constants.log_dir, '.ruffus_history_modis_firms.sqlite'), \
                     checksum_level=0, touch_files_only=touch_files_only)
        spec_logger.info("After running the pipeline %s" % 'processing_modis_firms')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id,
                          history_file=os.path.join(es_constants.log_dir, '.ruffus_history_modis_firms.sqlite'), \
                          checksum_level=0)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    # res_queue.put(proc_lists)
    return True


#   ---------------------------------------------------------------------
#
#   Function:   processing_std_modis_firms_stats_only
#   Purpose:    call the processing chain with the options:
#
#               update_stats -> True
#               nrt_products -> False
#
#   Arguments: see processing_std_modis_firms
#
#   ---------------------------------------------------------------------
def processing_std_modis_firms_stats_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='',
                                          version='',
                                          starting_dates_stats=None, write2file=None, logfile=None,
                                          touch_files_only=False):
    result = processing_std_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
                                        pipeline_printout_level=pipeline_printout_level,
                                        pipeline_printout_graph_level=pipeline_printout_graph_level,
                                        prod=prod,
                                        starting_sprod=starting_sprod,
                                        mapset=mapset,
                                        version=version,
                                        starting_dates_stats=starting_dates_stats,
                                        nrt_products=False,
                                        update_stats=True,
                                        write2file=write2file,
                                        logfile=logfile,
                                        touch_files_only=touch_files_only)

    return result


#   ---------------------------------------------------------------------
#
#   Function:   processing_std_modis_firms_prods_only
#   Purpose:    call the processing chain with the options:
#
#               update_stats -> False
#               nrt_products -> True
#
#   Arguments: see processing_std_modis_firms
#
#   ---------------------------------------------------------------------
def processing_modis_firms_prods_only(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                      pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='',
                                      version='',
                                      starting_dates=None, write2file=None, logfile=None, touch_files_only=False):
    result = processing_std_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
                                        pipeline_printout_level=pipeline_printout_level,
                                        pipeline_printout_graph_level=pipeline_printout_graph_level,
                                        prod=prod,
                                        starting_sprod=starting_sprod,
                                        mapset=mapset,
                                        version=version,
                                        starting_dates=starting_dates,
                                        nrt_products=True,
                                        update_stats=False,
                                        write2file=write2file,
                                        logfile=logfile,
                                        touch_files_only=touch_files_only)

    return result


#   ---------------------------------------------------------------------
#
#   Function:   processing_std_modis_firms_all
#   Purpose:    call the processing chain with the options:
#
#               update_stats -> True
#               nrt_products -> True
#
#   Arguments: see processing_std_modis_firms
#
#   ---------------------------------------------------------------------
def processing_std_modis_firms_all(res_queue, pipeline_run_level=0, pipeline_printout_level=0,
                                   pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                                   starting_dates=None, starting_dates_stats=None, write2file=None, logfile=None,
                                   touch_files_only=False):
    result = processing_std_modis_firms(res_queue, pipeline_run_level=pipeline_run_level,
                                        pipeline_printout_level=pipeline_printout_level,
                                        pipeline_printout_graph_level=pipeline_printout_graph_level,
                                        prod=prod,
                                        starting_sprod=starting_sprod,
                                        mapset=mapset,
                                        version=version,
                                        starting_dates=starting_dates,
                                        starting_dates_stats=starting_dates_stats,
                                        nrt_products=True,
                                        update_stats=True,
                                        write2file=write2file,
                                        logfile=logfile,
                                        touch_files_only=touch_files_only)

    return result
