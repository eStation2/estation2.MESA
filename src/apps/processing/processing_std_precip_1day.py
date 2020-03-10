from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define a processing chain for cumulating the 1day product to 10day (ARC2)
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 20.10.2016
#   descr:	 Generate additional derived products/implements processing chains
#            Computation rules:
#               10dcum -> only 1 missing file accepted
#               1moncum -> up to 3 missing file accepted
#               3moncum -> up to 9 missing file accepted
#               6moncum -> up to 18 missing file accepted
#               1yearcum-> up to 35 missing file accepted
#
#	history: 1.0
#

# Source generic modules
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
# import sys
import glob, datetime
from dateutil.relativedelta import relativedelta

# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math
from lib.python import es_logging as log
from config import es_constants

# Import third-party modules
from ruffus import *

#   General definitions for this processing chain
ext=es_constants.ES2_OUTFILE_EXTENSION

def create_pipeline(prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None):

    #   ---------------------------------------------------------------------
    #   Create lists to store definition of the derived products, and their
    #   groups
    #   ---------------------------------------------------------------------

    if proc_lists is None:
        proc_lists = functions.ProcLists()

    #   ---------------------------------------------------------------------
    #   Define and assign the flags to control the individual derived products
    #   and the groups. NOT to be changed by the User
    #   ---------------------------------------------------------------------

    # Set DEFAULTS: all off
    activate_10dcumul_comput=1              # 10d cumul
    activate_1moncum_comput=1               # 1mon cumul
    activate_3moncum_comput=1               # 3mon cumul
    activate_6moncum_comput=1               # 6mon cumul
    activate_1yearcum_comput=1              # 1year cumul

    # Conversion scale factor (from 0.01 of daily to 1.0 of all other products)
    scale_factor_conv = 0.01

    #   switch wrt groups - according to options
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files from the starting_sprod and starting_dates arguments
    #   ---------------------------------------------------------------------

    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    #logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Ingest', version, mapset)

    if starting_dates is not None:
        starting_files = []
        for my_date in starting_dates:
            if os.path.isfile(input_dir+my_date+in_prod_ident):
                starting_files.append(input_dir+my_date+in_prod_ident)
    else:
        starting_files=input_dir+"*"+in_prod_ident

    #   Look for all input files in input_dir, and sort them
    if starting_dates is not None:
        input_files = starting_files
    else:
        input_files = glob.glob(starting_files)

    #   ---------------------------------------------------------------------
    #   Derived product: 10dcumul
    #   ---------------------------------------------------------------------

    output_sprod_group=proc_lists.proc_add_subprod_group("cumul")
    output_sprod=proc_lists.proc_add_subprod("10d", "cumul", final=False,
                                             descriptive_name='10d Precipitation',
                                             description='Precipitation for dekad',
                                             frequency_id='e1dekad',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='Initial',
                                             active_default=True)

    out_prod_ident_10dcount = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_10dcount  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_10dcumul():

        dekad_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd)
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
                expected_days = functions.day_per_dekad(my_dekad_str)

                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+output_subdir_10dcount+os.path.sep+my_dekad_str+out_prod_ident_10dcount
                if len(file_list) >= expected_days-1:
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for dekad {0}'.format(my_dekad_str))

    @active_if(activate_10dcumul_comput)
    @files(generate_parameters_10dcumul)
    def std_precip_10dcumul(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",\
                "scale_factor":scale_factor_conv}

        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 1moncum
    #   ---------------------------------------------------------------------

    output_sprod=proc_lists.proc_add_subprod("1mon", "cumul", final=False,
                                             descriptive_name='Monthly Precipitation',
                                             description='Precipitation for a month',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='Initial',
                                             active_default=True)

    out_prod_ident_1moncum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_1moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_1moncum():

        month_list = []

        # Create unique list of all months (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mymonth_yyyymm=str(mydate)[0:6]
            if mymonth_yyyymm not in month_list:
              month_list.append(mymonth_yyyymm)

        month_list = sorted(month_list)

        # Compute the 'julian' dakad for the current day
        today = datetime.date.today()
        today_mon = today.strftime('%Y%m')

        for month in month_list:
            # Exclude the current dekad
             if month != today_mon:
                file_list = []
                exp_days_last_dk = functions.day_per_dekad(month+'21')
                expected_days = int(exp_days_last_dk)+20

                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydate_yyyymm=mydate_yyyymmdd[0:6]

                    if mydate_yyyymm == month:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+output_subdir_1moncum+os.path.sep+month+'01'+out_prod_ident_1moncum
                if len(file_list) >= expected_days-3:
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for month {0}'.format(month))

    @active_if(activate_1moncum_comput)
    @files(generate_parameters_1moncum)
    def std_precip_1moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",\
                "scale_factor":scale_factor_conv}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 3moncum
    #   ---------------------------------------------------------------------

    output_sprod=proc_lists.proc_add_subprod("3mon", "cumul", final=False,
                                             descriptive_name='3 Months Precipitation',
                                             description='Precipitation for 3 months',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='Initial',
                                             active_default=True)

    out_prod_ident_3moncum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_3moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_3moncum():

        n_mon = 3
        max_missing = 9
        month_list = []

        # Create unique list of all months (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mymonth_yyyymm=str(mydate)[0:6]
            if mymonth_yyyymm not in month_list:
              month_list.append(mymonth_yyyymm)

        month_list = sorted(month_list)

        # Compute the current month
        today = datetime.date.today()
        today_mon = today.strftime('%Y%m')

        for month in month_list:
            # Exclude the current dekad
             if month != today_mon:

                file_list = []

                # Compute first - last date for current interval

                first_day_this_month = datetime.date(int(month[0:4]),int(month[4:6]),1)
                first_day_next_month = first_day_this_month + relativedelta(months=+1)
                first_day_2_month_before = first_day_this_month + relativedelta(months=-n_mon+1)

                delta_3mon = first_day_next_month - first_day_2_month_before
                expected_days = delta_3mon.days

                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydate = datetime.date(int(mydate_yyyymmdd[0:4]),int(mydate_yyyymmdd[4:6]),int(mydate_yyyymmdd[6:8]))

                    if first_day_2_month_before <= mydate < first_day_next_month:
                        file_list.append(input_file)

                if len(file_list) >= expected_days-max_missing:
                    output_file=es_constants.processing_dir+output_subdir_3moncum+os.path.sep+month+'01'+out_prod_ident_3moncum
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for 3moncum, period until: {0}'.format(month))

    @active_if(activate_3moncum_comput)
    @files(generate_parameters_3moncum)
    def std_precip_3moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",\
                "scale_factor":scale_factor_conv}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 6moncum
    #   ---------------------------------------------------------------------

    output_sprod=proc_lists.proc_add_subprod("6mon", "cumul", final=False,
                                             descriptive_name='6 Months Precipitation',
                                             description='Precipitation for 6 months',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='Initial',
                                             active_default=True)

    out_prod_ident_6moncum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_6moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_6moncum():

        n_mon = 6
        max_missing = 18
        month_list = []

        # Create unique list of all months (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mymonth_yyyymm=str(mydate)[0:6]
            if mymonth_yyyymm not in month_list:
              month_list.append(mymonth_yyyymm)

        month_list = sorted(month_list)

        # Compute the current month
        today = datetime.date.today()
        today_mon = today.strftime('%Y%m')

        for month in month_list:
            # Exclude the current dekad
             if month != today_mon:

                file_list = []

                # Compute first - last date for current interval

                first_day_this_month = datetime.date(int(month[0:4]),int(month[4:6]),1)
                first_day_next_month = first_day_this_month + relativedelta(months=+1)
                first_day_2_month_before = first_day_this_month + relativedelta(months=-n_mon+1)

                delta_3mon = first_day_next_month - first_day_2_month_before
                expected_days = delta_3mon.days

                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydate = datetime.date(int(mydate_yyyymmdd[0:4]),int(mydate_yyyymmdd[4:6]),int(mydate_yyyymmdd[6:8]))

                    if first_day_2_month_before <= mydate < first_day_next_month:
                        file_list.append(input_file)

                if len(file_list) >= expected_days-max_missing:
                    output_file=es_constants.processing_dir+output_subdir_6moncum+os.path.sep+month+'01'+out_prod_ident_6moncum
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for 6moncum, period until: {0}'.format(month))

    @active_if(activate_6moncum_comput)
    @files(generate_parameters_6moncum)
    def std_precip_6moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",\
                "scale_factor":scale_factor_conv}
        raster_image_math.do_cumulate(**args)

    #   ---------------------------------------------------------------------
    #   Derived product: 1yearcum
    #   ---------------------------------------------------------------------

    output_sprod=proc_lists.proc_add_subprod("1year", "cumul", final=False,
                                             descriptive_name='Yearly Precipitation',
                                             description='Precipitation for 1 year',
                                             frequency_id='e1month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='Initial',
                                             active_default=True)

    out_prod_ident_1yearcum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_1yearcum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_1yearcum():

        n_mon = 12
        max_missing = 35
        month_list = []

        # Create unique list of all months (as 'Julian' number)
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mymonth_yyyymm=str(mydate)[0:6]
            if mymonth_yyyymm not in month_list:
              month_list.append(mymonth_yyyymm)

        month_list = sorted(month_list)

        # Compute the current month
        today = datetime.date.today()
        today_mon = today.strftime('%Y%m')

        for month in month_list:
            # Exclude the current dekad
             if month != today_mon:

                file_list = []

                # Compute first - last date for current interval

                first_day_this_month = datetime.date(int(month[0:4]),int(month[4:6]),1)
                first_day_next_month = first_day_this_month + relativedelta(months=+1)
                first_day_2_month_before = first_day_this_month + relativedelta(months=-n_mon+1)

                delta_3mon = first_day_next_month - first_day_2_month_before
                expected_days = delta_3mon.days

                for input_file in input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydate = datetime.date(int(mydate_yyyymmdd[0:4]),int(mydate_yyyymmdd[4:6]),int(mydate_yyyymmdd[6:8]))

                    if first_day_2_month_before <= mydate < first_day_next_month:
                        file_list.append(input_file)

                if len(file_list) >= expected_days-max_missing:
                    output_file=es_constants.processing_dir+output_subdir_1yearcum+os.path.sep+month+'01'+out_prod_ident_1yearcum
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for 1yearcum, period until: {0}'.format(month))

    @active_if(activate_1yearcum_comput)
    @files(generate_parameters_1yearcum)
    def std_precip_1yearcum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",\
                "scale_factor":scale_factor_conv}
        raster_image_math.do_cumulate(**args)

    # End of pipeline definition
    return proc_lists

#   ---------------------------------------------------------------------
#   Drive the pipeline: 1 function only is defined, a main one:
#
#       processing_std_precip_1day -> create and run the pipeline
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
#              IN:  write2file              -> name of the file where to report the tasks to be executed
#                                              Used only by pipeline_printout (dry-run)
#              IN:  logfile                 -> Name of the logfile
#
#   ---------------------------------------------------------------------

def processing_std_precip_1day(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_precip_1day')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_precip_1day')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_precip_1day.sqlite'),\
                     checksum_level=0)
        spec_logger.info("After running the pipeline %s" % 'processing_precip_1day')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_precip_1day.sqlite'),\
                     checksum_level=0)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True
