from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define a processing chain for 'precipitation-like' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0 Initial release
#            1.1 Oct. 2016: add the 3mon/6mon/1yrs cumulates and change stats computation to exclude current year
#            1.2 Apr. 2017: the 3mon/6mon/1year cumulates are removed (to be included in the SPI, so not to impact the Users at national level)
#
#   NOTE (to be included in doc): since 1.1 the stats are computed by excluding the current year
#

# Source generic modules
from builtins import open
from future import standard_library
standard_library.install_aliases()
import os, time, sys
import glob, datetime

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants
from database import querydb
# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def exclude_current_year(input_list):

    output_list = []
    today = datetime.date.today()
    current_year = today.strftime('%Y')

    for myfile in input_list:
        if os.path.basename(myfile)[0:4] != current_year:
            output_list.append(myfile)
    return output_list

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None,
                    update_stats=False, nrt_products=True):

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # Set DEFAULTS: all off
    activate_10dstats_comput=0          # 10d stats
    activate_10danomalies_comput=0      # 10d anomalies

    activate_monthly_comput=0           # monthly cumulation
    activate_monstats_comput=0          # monthly stats
    activate_monanomalies_comput=0      # monthly anomalies

    #   switch wrt groups - according to options
    if nrt_products:
        activate_10danomalies_comput=1      # 10d anomalies

        activate_monthly_comput=1           # monthly cumulation
        activate_monanomalies_comput=1      # monthly anomalies

    if update_stats:
        activate_10dstats_comput=1          # 10d stats
        activate_monstats_comput=1          # monthly stats

    #   switch wrt single products: not to be changed !!
    activate_10davg_comput=1
    activate_10dmin_comput=1
    activate_10dmax_comput=1
    activate_10ddiff_comput=1
    activate_10dperc_comput=1
    activate_10dnp_comput=1
    activate_10dratio_comput=1

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

    #logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    #   ---------------------------------------------------------------------
    #   Average
    output_sprod_group=proc_lists.proc_add_subprod_group("10dstats")
    output_sprod=proc_lists.proc_add_subprod("10davg", "10dstats", final=False,
                                             descriptive_name='10d Average',
                                             description='Average rainfall for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10davg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10davg(input_file, output_file):

        reduced_list = exclude_current_year(input_file)
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Minimum
    output_sprod=proc_lists.proc_add_subprod("10dmin", "10dstats", final=False,
                                             descriptive_name='10d Minimum',
                                             description='Minimum rainfall for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10dmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Maximum
    output_sprod=proc_lists.proc_add_subprod("10dmax", "10dstats", final=False,
                                             descriptive_name='10d Maximum',
                                             description='Maximum rainfall for dekad',
                                             frequency_id='e1dekad',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @active_if(activate_10dstats_comput, activate_10dmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_10dmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   10dDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("10anomalies")
    output_sprod=proc_lists.proc_add_subprod("10ddiff", "10anomalies", final=False,
                                             descriptive_name='10d Absolute Difference',
                                             description='10d Absolute Difference vs. LTA',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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
    output_sprod=proc_lists.proc_add_subprod("10dperc", "10anomalies",  final=False,
                                             descriptive_name='10d Percent Difference',
                                             description='10d Percent Difference vs. LTA',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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
    output_sprod=proc_lists.proc_add_subprod("10dnp", "10anomalies",  final=False,
                                             descriptive_name='10d Normalized Anomaly',
                                             description='10d Normalized Anomaly',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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
    #   10dratio
    output_sprod=proc_lists.proc_add_subprod("10dratio", "10anomalies",  final=False,
                                             descriptive_name='10d Ratio',
                                             description='10d Ratio (curr/avg)',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    #   Starting files + min + max
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident

    ancillary_sprod_1 = "10davg"
    ancillary_sprod_ident_1 = functions.set_path_filename_no_date(prod, ancillary_sprod_1, mapset, version, ext)
    ancillary_subdir_1      = functions.set_path_sub_directory(prod, ancillary_sprod_1, 'Derived',version, mapset)
    ancillary_input_1="{subpath[0][5]}"+os.path.sep+ancillary_subdir_1+"{MMDD[0]}"+ancillary_sprod_ident_1

    @follows(std_precip_10dmin, std_precip_10dmax)
    @active_if(activate_10danomalies_comput, activate_10dratio_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input_1), formatter_out)
    def std_precip_10dratio(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)

    #   ---------------------------------------------------------------------
    #   1moncum
    output_sprod_group=proc_lists.proc_add_subprod_group("monthly")
    output_sprod=proc_lists.proc_add_subprod("1moncum", "monthly", final=False,
                                             descriptive_name='Monthly Cumulate',
                                             description='Monthly Cumulate Precipitation',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs: files from same months
    formatter_in="(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+'01'+out_prod_ident

    # @follows(std_precip_10davg)
    @active_if(activate_monthly_comput, activate_1moncum_comput)
    @collate(starting_files, formatter(formatter_in), formatter_out)
    def std_precip_1moncum(input_file, output_file):
        #ES2- 235 Do not show temporary products like composite not complete (ex monthly composite available mid month...)
        # ex: monthly RFE in the middle of the month should not be available because incomplete and lead to wrong analysis...
        # Check current month  ---> yes  ---> skip
        #                      ----> NO   ---> Check No of days (10% tolerance)
        #                                       acceptable ---->
        #                                                   Yes ---> proceed
        #                                                   No ----> Skip
        input_file_date = functions.get_date_from_path_full(input_file[0])

        if len(input_file) == 3:
            if not functions.is_date_current_month(input_file_date):
                output_file = functions.list_to_element(output_file)
                functions.check_output_dir(os.path.dirname(output_file))
                args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
                raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Average
    new_input_subprod='1moncum'
    in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    in_prod_subdir= functions.set_path_sub_directory  (prod, new_input_subprod, 'Derived', version, mapset)
    starting_files= es2_data_dir+in_prod_subdir+"*"+ in_prod_ident

    output_sprod_group=proc_lists.proc_add_subprod_group("monstat")
    output_sprod=proc_lists.proc_add_subprod("1monavg", "monstat", final=False,
                                             descriptive_name='Monthly Average',
                                             description='Monthly Average Precipitation',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Minimum
    output_sprod=proc_lists.proc_add_subprod("1monmin", "monstat",final=False,
                                             descriptive_name='Monthly Minimum',
                                             description='Monthly Minimum Precipitation',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Monthly Maximum
    output_sprod=proc_lists.proc_add_subprod("1monmax", "monstat",final=False,
                                             descriptive_name='Monthly Maximum',
                                             description='Monthly Maximum Precipitation',
                                             frequency_id='e1month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1moncum)
    @active_if(activate_monstats_comput, activate_1monmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   1monDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("monanomalies")
    output_sprod=proc_lists.proc_add_subprod("1mondiff", "monanomalies", final=False,
                                             descriptive_name='Monthly Absolute Difference',
                                             description='Monthly Absolute Difference Precipitation',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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
    output_sprod=proc_lists.proc_add_subprod("1monperc", "monanomalies", final=False,
                                             descriptive_name='Monthly Percent Difference',
                                             description='Monthly Percent Difference Precipitation',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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
    output_sprod=proc_lists.proc_add_subprod("1monnp", "monanomalies", final=False,
                                             descriptive_name='Monthly Normalized Anomaly',
                                             description='Monthly Normalized Anomaly Precipitation',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
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

    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline


def processing_std_precip(res_queue, pipeline_run_level=0,pipeline_printout_level=0, upsert_db = False,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, update_stats=False, nrt_products=True, write2file=None, logfile=None,
                          touch_only=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_precip')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, update_stats=update_stats, nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if upsert_db:
        tasks = pipeline_get_task_names()
        spec_logger.info("Updating DB for the pipeline %s" % tasks[0])
        # Get input product info
        input_product_info=querydb.get_product_out_info(allrecs=False,
                                                        productcode=prod,
                                                        subproductcode=starting_sprod,
                                                        version=version)

        for my_sprod in proc_lists.list_subprods:
            # my_sprod.print_out()
            status = querydb.update_processing_chain_products(prod, version, my_sprod, input_product_info)

        spec_logger.info("Updating DB Done - Exit")
        return proc_lists

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_precip')
        pipeline_run(touch_files_only=touch_only, verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_{0}_{1}.sqlite').format(prod,starting_sprod))
        tasks = pipeline_get_task_names()
        spec_logger.info("Run the pipeline %s" % tasks[0])
        spec_logger.info("After running the pipeline %s" % 'processing_std_precip')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id,  history_file=os.path.join(es_constants.log_dir,'.ruffus_history_{0}_{1}.sqlite').format(prod,starting_sprod))

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    # Using the Queue here gives an error of 'broken pipe' in Queue.py
    # res_queue.put(proc_lists)
    return proc_lists

def processing_std_precip_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False,upsert_db = False):

    result = processing_std_precip(res_queue, pipeline_run_level=pipeline_run_level,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          nrt_products=False,
                          update_stats=True,
                          write2file=write2file,
                          logfile=logfile,
                          upsert_db=upsert_db,
                          touch_only=touch_only)

    return result


def processing_std_precip_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False,upsert_db = False):

    result = processing_std_precip(res_queue, pipeline_run_level=pipeline_run_level,
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
                          upsert_db=upsert_db,
                          touch_only=touch_only)

    return result


def processing_std_precip_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False,upsert_db = False):

    result = processing_std_precip(res_queue, pipeline_run_level=pipeline_run_level,
                          pipeline_printout_level=pipeline_printout_level,
                          pipeline_printout_graph_level=pipeline_printout_graph_level,
                          prod=prod,
                          starting_sprod=starting_sprod,
                          mapset=mapset,
                          version=version,
                          starting_dates=starting_dates,
                          nrt_products=True,
                          update_stats=True,
                          write2file=write2file,
                          logfile=logfile,
                          upsert_db=upsert_db,
                          touch_only=touch_only)

    return result

