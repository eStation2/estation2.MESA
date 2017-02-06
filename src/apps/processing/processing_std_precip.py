#
#	purpose: Define a processing chain for 'precipitation-like' products (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products/implements processing chains
#	history: 1.0 Initial release
#            1.1 Oct. 2016: add the 3mon/6mon/1yrs cumulates and change stats computation to exclude current year
#
#   NOTE (to be included in doc): since 1.1 the stats are computed by excluding the current year
#

# Source generic modules
import os, time, sys
import glob, datetime

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

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

    activate_quarterly_comput=0         # quarterly cumulation
    activate_3monstats_comput=0         # quarterly stats
    activate_3monanomalies_comput=0     # quarterly anomalies

    activate_sixmonthly_comput=0        # sixmonthly cumulation
    activate_6monstats_comput=0         # sixmonthly stats
    activate_6monanomalies_comput=0     # sixmonthly anomalies

    activate_yearly_comput=0            # yearly cumulation
    activate_1yearstats_comput=0        # yearly stats
    activate_1yearanomalies_comput=0    # yearly anomalies

    #   switch wrt groups - according to options
    if nrt_products:
        activate_10danomalies_comput=1      # 10d anomalies

        activate_monthly_comput=1           # monthly cumulation
        activate_monanomalies_comput=1      # monthly anomalies

        activate_quarterly_comput=1         # quarterly cumulation
        activate_3monanomalies_comput=1     # quarterly anomalies

        activate_sixmonthly_comput=1        # sixmonthly cumulation
        activate_6monanomalies_comput=1     # sixmonthly anomalies

        activate_yearly_comput=1            # yearly cumulation
        activate_1yearanomalies_comput=1     # yearly anomalies

    if update_stats:
        activate_10dstats_comput=1          # 10d stats
        activate_monstats_comput=1          # monthly stats
        activate_3monstats_comput=1         # quarterly stats
        activate_6monstats_comput=1         # sixmonthly stats
        activate_1yearstats_comput=1        # yearly stats

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

    activate_3moncum_comput=1
    activate_3monavg_comput=1
    activate_3monmin_comput=1
    activate_3monmax_comput=1
    activate_3mondiff_comput=1
    activate_3monperc_comput=1

    activate_6moncum_comput=1
    activate_6monavg_comput=1
    activate_6monmin_comput=1
    activate_6monmax_comput=1
    activate_6mondiff_comput=1
    activate_6monperc_comput=1

    activate_1yearcum_comput=1
    activate_1yearavg_comput=1
    activate_1yearmin_comput=1
    activate_1yearmax_comput=1
    activate_1yeardiff_comput=1
    activate_1yearperc_comput=1

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

    #   ---------------------------------------------------------------------
    #   3moncum
    output_sprod_group=proc_lists.proc_add_subprod_group("quarterly")
    output_sprod_3moncum=proc_lists.proc_add_subprod("3moncum", "quarterly", final=False,
                                             descriptive_name='Quarterly Cumulate',
                                             description='Quarterly Cumulate Precipitation',
                                             frequency_id='e3month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_3moncum_ident = functions.set_path_filename_no_date(prod, output_sprod_3moncum, mapset, version, ext)
    output_3moncum_subdir  = functions.set_path_sub_directory   (prod, output_sprod_3moncum, 'Derived', version, mapset)

    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, '1moncum', 'Derived', version, mapset)
    moncum_prod_ident = functions.set_path_filename_no_date(prod, '1moncum', mapset, version, ext)


    def generate_parameters_3moncum():

        starting_files=input_dir+"*"+ moncum_prod_ident

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files)
        quarter_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            myquarter_nbr=functions.conv_date_2_quarter(mydate_yyyymmdd)
            if myquarter_nbr not in quarter_list:
              quarter_list.append(myquarter_nbr)

        quarter_list = sorted(quarter_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        quarter_now = functions.conv_date_2_quarter(today_str)

        for quarter in quarter_list:
            # Exclude the current dekad
            if quarter != quarter_now:
                file_list = []
                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    myquarter_nbr=functions.conv_date_2_quarter(mydate_yyyymmdd[0:8])

                    if myquarter_nbr == quarter:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+output_3moncum_subdir+os.path.sep+quarter+out_prod_3moncum_ident
                yield (file_list, output_file)

    @active_if(activate_quarterly_comput, activate_3moncum_comput)
    @files(generate_parameters_3moncum)
    def std_precip_3moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Quarterly Average
    new_input_subprod='3moncum'

    in_prod_ident = functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    in_prod_subdir= functions.set_path_sub_directory   (prod, new_input_subprod, 'Derived', version, mapset)
    starting_files= es2_data_dir+in_prod_subdir+"*"+ in_prod_ident

    output_sprod_group=proc_lists.proc_add_subprod_group("3monstat")
    output_sprod=proc_lists.proc_add_subprod('3monavg', "3monstat",final=False,
                                             descriptive_name='Quarter Average',
                                             description='Quarter Average Precipitation',
                                             frequency_id='e3month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_3moncum)
    @active_if(activate_3monstats_comput, activate_3monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_3monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Quarterly Minimum
    output_sprod=proc_lists.proc_add_subprod("3monmin", "3monstat",final=False,
                                             descriptive_name='Quarter Minimum',
                                             description='Quarter Minimum Precipitation',
                                             frequency_id='e3month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_3moncum)
    @active_if(activate_3monstats_comput, activate_3monmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_3monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Quarterly Maximum
    output_sprod=proc_lists.proc_add_subprod("3monmax", "3monstat",final=False,
                                             descriptive_name='Quarter Maximum',
                                             description='Quarter Maximum Precipitation',
                                             frequency_id='e3month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_3moncum)
    @active_if(activate_3monstats_comput, activate_3monmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_3monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   3monDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("3monanomalies")
    output_sprod=proc_lists.proc_add_subprod("3mondiff", "3monanomalies", final=False,
                                             descriptive_name='Quarter Absolute Difference',
                                             description='Quarter Absolute Difference Precipitation',
                                             frequency_id='e3month',
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

    ancillary_sprod = "3monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_3monavg)
    @active_if(activate_3monanomalies_comput, activate_3mondiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_3mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   3monperc
    output_sprod=proc_lists.proc_add_subprod("3monperc", "3monanomalies", final=False,
                                             descriptive_name='Quarter Percent Difference',
                                             description='Quarter Percent Difference Precipitation',
                                             frequency_id='e3month',
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

    ancillary_sprod = "3monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_3monavg)
    @active_if(activate_3monanomalies_comput, activate_3monperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_3monperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)


    #   ---------------------------------------------------------------------
    #   6moncum
    output_sprod_group=proc_lists.proc_add_subprod_group("sixmonth")
    output_sprod_6moncum=proc_lists.proc_add_subprod("6moncum", "sixmonth", final=False,
                                             descriptive_name='SixMonth Cumulate',
                                             description='SixMonth Cumulate Precipitation',
                                             frequency_id='e6month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_6moncum_ident = functions.set_path_filename_no_date(prod, output_sprod_6moncum, mapset, version, ext)
    output_6moncum_subdir  = functions.set_path_sub_directory   (prod, output_sprod_6moncum, 'Derived', version, mapset)

    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, '1moncum', 'Derived', version, mapset)
    moncum_prod_ident = functions.set_path_filename_no_date(prod, '1moncum', mapset, version, ext)


    def generate_parameters_6moncum():

        starting_files=input_dir+"*"+ moncum_prod_ident

        #   Look for all input files in input_dir, and sort them
        input_files = glob.glob(starting_files)
        semester_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mysemester_nbr=functions.conv_date_2_semester(mydate_yyyymmdd)
            if mysemester_nbr not in semester_list:
              semester_list.append(mysemester_nbr)

        semester_list = sorted(semester_list)
        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        semester_now = functions.conv_date_2_semester(today_str)

        for semester in semester_list:
            # Exclude the current dekad
            if semester != semester_now:
                file_list = []
                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mysemester_nbr=functions.conv_date_2_semester(mydate_yyyymmdd[0:8])

                    if mysemester_nbr == semester:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+output_6moncum_subdir+os.path.sep+semester+out_prod_6moncum_ident
                yield (file_list, output_file)

    @active_if(activate_sixmonthly_comput, activate_6moncum_comput)
    @files(generate_parameters_6moncum)
    def std_precip_6moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Six-Month Average
    new_input_subprod='6moncum'

    in_prod_ident = functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    in_prod_subdir= functions.set_path_sub_directory   (prod, new_input_subprod, 'Derived', version, mapset)
    starting_files= es2_data_dir+in_prod_subdir+"*"+ in_prod_ident

    output_sprod_group=proc_lists.proc_add_subprod_group("6monstat")
    output_sprod=proc_lists.proc_add_subprod('6monavg', "6monstat",final=False,
                                             descriptive_name='Six-Month Average',
                                             description='Six-Month Average Precipitation',
                                             frequency_id='e6month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_6moncum)
    @active_if(activate_6monstats_comput, activate_6monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_6monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Six-Month Minimum
    output_sprod=proc_lists.proc_add_subprod("6monmin", "6monstat",final=False,
                                             descriptive_name='Six-Month Minimum',
                                             description='Six-Month Minimum Precipitation',
                                             frequency_id='e6month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_6moncum)
    @active_if(activate_6monstats_comput, activate_6monmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_6monmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Six-Month Maximum
    output_sprod=proc_lists.proc_add_subprod("6monmax", "6monstat",final=False,
                                             descriptive_name='Six-Month Maximum',
                                             description='Six-Month Maximum Precipitation',
                                             frequency_id='e6month',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_6moncum)
    @active_if(activate_6monstats_comput, activate_6monmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_6monmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   6monDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("6monanomalies")
    output_sprod=proc_lists.proc_add_subprod("6mondiff", "6monanomalies", final=False,
                                             descriptive_name='Six-Month Absolute Difference',
                                             description='Six-Month Absolute Difference Precipitation',
                                             frequency_id='e6month',
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

    ancillary_sprod = "6monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_6monavg)
    @active_if(activate_6monanomalies_comput, activate_6mondiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_6mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   6monperc
    output_sprod=proc_lists.proc_add_subprod("6monperc", "6monanomalies", final=False,
                                             descriptive_name='Six-Month Percent Difference',
                                             description='Six-Month Percent Difference Precipitation',
                                             frequency_id='e6month',
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

    ancillary_sprod = "6monavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_6monavg)
    @active_if(activate_6monanomalies_comput, activate_6monperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_6monperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

    #   ---------------------------------------------------------------------
    #   1yearcum
    output_sprod_group=proc_lists.proc_add_subprod_group("yearly")
    output_sprod=proc_lists.proc_add_subprod("1yearcum", "yearly", final=False,
                                             descriptive_name='Yearly Cumulate',
                                             description='Yearly Cumulate Precipitation',
                                             frequency_id='e1year',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    # inputs: files from same months
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+out_prod_3moncum_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}"+'0101'+out_prod_ident

    starting_files_1yearcum = es2_data_dir+os.path.sep+output_3moncum_subdir+os.path.sep+'*'+out_prod_3moncum_ident

    @active_if(activate_yearly_comput, activate_1yearcum_comput)
    @collate(starting_files_1yearcum, formatter(formatter_in), formatter_out)
    def std_precip_1yearcum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file,"output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Yearly Average
    new_input_subprod='1yearcum'

    in_prod_ident = functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    in_prod_subdir= functions.set_path_sub_directory   (prod, new_input_subprod, 'Derived', version, mapset)
    starting_files= es2_data_dir+in_prod_subdir+"*"+ in_prod_ident

    output_sprod_group=proc_lists.proc_add_subprod_group("1yearstat")
    output_sprod=proc_lists.proc_add_subprod('1yearavg', "1yearstat",final=False,
                                             descriptive_name='Yearly Average',
                                             description='Yearly Average Precipitation',
                                             frequency_id='e1year',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1yearcum)
    @active_if(activate_1yearstats_comput, activate_1yearavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1yearavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

    #   ---------------------------------------------------------------------
    #   Yearly Minimum
    output_sprod=proc_lists.proc_add_subprod("1yearmin", "1yearstat",final=False,
                                             descriptive_name='Yearly Minimum',
                                             description='Yearly Minimum Precipitation',
                                             frequency_id='e1year',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1yearcum)
    @active_if(activate_1yearstats_comput, activate_1yearmin_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1yearmin(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_min_image(**args)

    #   ---------------------------------------------------------------------
    #   Yearly Maximum
    output_sprod=proc_lists.proc_add_subprod("1yearmax", "1yearstat",final=False,
                                             descriptive_name='Yearly Maximum',
                                             description='Yearly Maximum Precipitation',
                                             frequency_id='e1year',
                                             date_format='MMDD',
                                             masked=False,
                                             timeseries_role='10d',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    reg_ex_in="[0-9]{4}([0-9]{4})"+in_prod_ident

    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+in_prod_ident
    formatter_out=["{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident]

    @follows(std_precip_1yearcum)
    @active_if(activate_1yearstats_comput, activate_1yearmax_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def std_precip_1yearmax(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        reduced_list = exclude_current_year(input_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_max_image(**args)

    #   ---------------------------------------------------------------------
    #   1yearDiff
    output_sprod_group=proc_lists.proc_add_subprod_group("1yearanomalies")
    output_sprod=proc_lists.proc_add_subprod("1yeardiff", "1yearanomalies", final=False,
                                             descriptive_name='Yearly Absolute Difference',
                                             description='Yearly Absolute Difference Precipitation',
                                             frequency_id='e1year',
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

    ancillary_sprod = "1yearavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived', version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_1yearavg)
    @active_if(activate_1yearanomalies_comput, activate_1yeardiff_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_1yeardiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    #   ---------------------------------------------------------------------
    #   1yearperc
    output_sprod=proc_lists.proc_add_subprod("1yearperc", "1yearanomalies", final=False,
                                             descriptive_name='Yearly Percent Difference',
                                             description='Yearly Percent Difference Precipitation',
                                             frequency_id='e1year',
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

    ancillary_sprod = "1yearavg"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset, version, ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @follows(std_precip_1yearavg)
    @active_if(activate_1yearanomalies_comput, activate_1yearperc_comput)
    @transform(starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def std_precip_1yearperc(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)


    return proc_lists
#   ---------------------------------------------------------------------
#   Run the pipeline


def processing_std_precip(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, update_stats=False, nrt_products=True, write2file=None, logfile=None, touch_only=False):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_precip')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists, update_stats=update_stats, nrt_products=nrt_products)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_precip')
        pipeline_run(touch_files_only=touch_only, verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod,starting_sprod))
        tasks = pipeline_get_task_names()
        spec_logger.info("Run the pipeline %s" % tasks[0])
        spec_logger.info("After running the pipeline %s" % 'processing_std_precip')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id,  history_file='/eStation2/log/.ruffus_history_{0}_{1}.sqlite'.format(prod,starting_sprod))

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True

def processing_std_precip_stats_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

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
                          touch_only=touch_only)

    return result


def processing_std_precip_prods_only(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

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
                          touch_only=touch_only)

    return result


def processing_std_precip_all(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None,write2file=None, logfile=None, touch_only=False):

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
                          touch_only=touch_only)

    return result

