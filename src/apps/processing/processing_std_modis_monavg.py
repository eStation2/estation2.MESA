from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: Define the processing service (by using ruffus)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 11.06.2014
#   descr:	 Generate additional derived products / implements processing chains
#	history: 1.0 - Initial Version
#            1.1 - Modify monavg computation to skip current month (MOI request)
#

# Source my definitions
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import datetime
import glob
import calendar
import fnmatch

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, logger=None):

    my_date=None

    #   ---------------------------------------------------------------------
    #   Create lists
    if proc_lists is None:
        proc_lists = functions.ProcLists()

    # 8d cumul
    activate_8dayavg_comput=1

    # monthly
    activate_monavg_comput=1
    activate_monclim_comput=0
    activate_monanom_comput=1

    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files
    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    input_dir = es2_data_dir+ functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)
                
    if my_date is not None:
        starting_files = input_dir+my_date+"*"+in_prod_ident
    else:
        starting_files = input_dir+"*"+in_prod_ident

   #   ---------------------------------------------------------------------
   #   8-days Average

    output_sprod_group_8day=proc_lists.proc_add_subprod_group("8days")
    output_sprod_8day=proc_lists.proc_add_subprod("8daysavg", "8days", final=False,
                                             descriptive_name='8Day average',
                                             description='8Day average',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    out_prod_ident_8day = functions.set_path_filename_no_date(prod, output_sprod_8day, mapset, version, ext)
    output_subdir_8day  = functions.set_path_sub_directory   (prod, output_sprod_8day, 'Derived', version, mapset)

    def generate_parameters_8days():

        years_periods_list = []

        #   Look for all input files in input_dir
        input_files = glob.glob(starting_files)
        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydate_year    =str(mydate)[0:4]

            period_nbr=functions.conv_date_2_8days(mydate_yyyymmdd)

            if (mydate_year,period_nbr) not in years_periods_list:
              years_periods_list.append((mydate_year,period_nbr))

        periods_sorted = sorted(years_periods_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_str = today.strftime('%Y%m%d')
        year_now = today.strftime('%Y')
        period_now = functions.conv_date_2_8days(today_str)

        # Generate the list of 30 min time in a day
        for year, period in periods_sorted:
            # Exclude the current dekad
            if period != period_now or year != year_now:
                file_list = []
                jdoy_period = "{0:03d}".format(1+8*(int(period)-1))
                mmdd_period = functions.conv_date_yyyydoy_2_yyyymmdd(year+jdoy_period)
                output_file=es_constants.processing_dir+output_subdir_8day+os.path.sep+mmdd_period+out_prod_ident_8day

                for myfile in input_files:
                    basename=os.path.basename(myfile)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydate_year=mydate_yyyymmdd[0:4]

                    period_nbr=functions.conv_date_2_8days(mydate_yyyymmdd[0:8])
                    if period_nbr == period and mydate_year == year:
                        file_list.append(myfile)

                # Special case of last period of the year: add few days of next year
                if period == 46:
                    next_year = "{0:04d}".format(int(year)+1)
                    if calendar.isleap(int(year)):
                        add_days = ('0101','0102','0103')
                    else:
                        add_days = ('0101','0102','0103','0104')
                    for day in add_days:
                        date = next_year+day
                        matches=[x for x in input_files if fnmatch.fnmatch(x,'*{0}*'.format(date))]
                        # Fixes ES2-35 (see YouTrack)
                        if len(matches) > 0:
                            file_list.append(matches[0])

                yield (sorted(file_list), output_file)

    @active_if(activate_8dayavg_comput)
    @files(generate_parameters_8days)
    def modis_8dayavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        out_filename=os.path.basename(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

   #   ---------------------------------------------------------------------
   #   Monthly Average for a given month

    output_sprod_group=proc_lists.proc_add_subprod_group("monstats")
    output_sprod=proc_lists.proc_add_subprod("monavg", "monstats", final=False,
                                             descriptive_name='Monthly average',
                                             description='Monthly average',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)
    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="(?P<YYYYMM>[0-9]{6})[0-9]{2}"+in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYYMM[0]}"+'01'+out_prod_ident
   
    @active_if(activate_monavg_comput)
    @collate(starting_files, formatter(formatter_in),formatter_out)
    def modis_monavg(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        out_filename=os.path.basename(output_file)
        functions.check_output_dir(os.path.dirname(output_file))

        str_date=out_filename[0:6]
        today = datetime.date.today()
        today_yyyymm = today.strftime('%Y%m')

        #expected_ndays=functions.get_number_days_month(str_date)
        #current_ndays=len(input_file)
        if str_date == today_yyyymm:
             logger.info('Do not perform computation for current month {0}. Skip'.format(str_date))
        else:
            args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
            raster_image_math.do_avg_image(**args)
 
    #   ---------------------------------------------------------------------
    #   Monthly Climatology for all years

    output_sprod=proc_lists.proc_add_subprod("monclim", "monstats", final=False,
                                             descriptive_name='Monthly climatology',
                                             description='Monthly climatology',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    new_input_subprod='monavg'
    new_in_prod_ident= functions.set_path_filename_no_date(prod, new_input_subprod, mapset, version, ext)
    new_input_dir = es2_data_dir+functions.set_path_sub_directory(prod, new_input_subprod, 'Derived', version, mapset)

    new_starting_files = new_input_dir+"*"+new_in_prod_ident

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    
    formatter_in="[0-9]{4}(?P<MMDD>[0-9]{4})"+new_in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{MMDD[0]}"+out_prod_ident

    @active_if(activate_monclim_comput)
    @collate(new_starting_files, formatter(formatter_in),formatter_out)
    def modis_chla_monclim(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', \
	    "options": "compress=lzw"}
        raster_image_math.do_avg_image(**args)

   #   ---------------------------------------------------------------------
   #   Monthly Anomaly for a given monthly    
    output_sprod=proc_lists.proc_add_subprod("monanom", "monstats", final=False,
                                             descriptive_name='Monthly anomaly',
                                             description='Monthly anomaly',
                                             frequency_id='',
                                             date_format='YYYMMMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident = functions.set_path_filename_no_date(prod, output_sprod, mapset,version, ext)
    output_subdir  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)    
    
    #   Starting files + avg
    formatter_in="(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})"+new_in_prod_ident
    formatter_out="{subpath[0][5]}"+os.path.sep+output_subdir+"{YYYY[0]}{MMDD[0]}"+out_prod_ident
        
    ancillary_sprod = "monclim"
    ancillary_sprod_ident = functions.set_path_filename_no_date(prod, ancillary_sprod, mapset,version,ext)
    ancillary_subdir      = functions.set_path_sub_directory(prod, ancillary_sprod, 'Derived',version, mapset)
    ancillary_input="{subpath[0][5]}"+os.path.sep+ancillary_subdir+"{MMDD[0]}"+ancillary_sprod_ident

    @active_if(activate_monanom_comput)
    @transform(new_starting_files, formatter(formatter_in), add_inputs(ancillary_input), formatter_out)
    def modis_chla_mondiff(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_oper_subtraction(**args)

    return proc_lists

#   ---------------------------------------------------------------------
#   Run the pipeline

def processing_std_modis_monavg(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                           pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                           starting_dates=None, write2file=None, logfile=None):


    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_modis_monavg')

    history_file = os.path.join(es_constants.log_dir,'.ruffus_history_{0}_{1}.sqlite').format(prod,starting_sprod)
    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, logger=spec_logger)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    spec_logger.info("Entering routine %s" % 'processing_modis')
    if pipeline_run_level > 0:
        spec_logger.info("Now calling pipeline_run")
    # Option to be added to pipeline_run to force files to appear up-to-date: touch_files_only = True
        pipeline_run(verbose=pipeline_run_level,history_file=history_file, checksum_level=0, touch_files_only = False)
    
    if pipeline_printout_level > 0:
        
        pipeline_printout(verbose=pipeline_printout_level)
    
    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')
