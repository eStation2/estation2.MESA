from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define a processing chain for computing SPI indicator
#	author:  M.Clerici & Jurriaan van't Klooster
#	date:	 24.10.2016
#   descr:	 I computes the SPI for periods of 1/3/6/12 months, by generating the following sprods:
#
#            YYYYMM01_..._3moncum -> 3-mon cumulate until YYYYMM01 month
#            YYYYMM01_..._6moncum -> 6-mon cumulate until YYYYMM01 month
#            YYYYMM01_..._1yearcum -> 1-yr cumulate until YYYYMM01 month
#
#           which are intermediate outputs. Final outputs are:
#            YYYYMM01_..._spi-1m_
#            YYYYMM01_..._spi-3m_
#            YYYYMM01_..._spi-6m_
#            YYYYMM01_..._spi-1y_
#
#	history: 1.0
#

# Source generic modules
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import os
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
    activate_cumul_comput=1                 # cumulated products
    activate_spi_comput=1                   # spi indicators


    # Set DEFAULTS: all off
    activate_cumul_3mon_comput=1                 # cumulated product 3mon
    activate_cumul_6mon_comput=1                 # cumulated product 6mon
    activate_cumul_1year_comput=1                # cumulated product 1year

    activate_spi_1mon_comput=1                   # spi indicator 1mon
    activate_spi_3mon_comput=1                   # spi indicator 3mon
    activate_spi_6mon_comput=1                   # spi indicator 6mon
    activate_spi_1year_comput=1                  # spi indicator 1year

    #   switch wrt groups - according to options
    es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

    #   ---------------------------------------------------------------------
    #   Define input files from the starting_sprod and starting_dates arguments
    #   ---------------------------------------------------------------------

    in_prod_ident = functions.set_path_filename_no_date(prod, starting_sprod, mapset, version, ext)

    #logger.debug('Base data directory is: %s' % es2_data_dir)
    input_dir = es2_data_dir+ \
                functions.set_path_sub_directory(prod, starting_sprod, 'Derived', version, mapset)

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
    #   Cumulated products - 3mon
    #   ---------------------------------------------------------------------
    output_sprod_group=proc_lists.proc_add_subprod_group("cumul")
    output_sprod=proc_lists.proc_add_subprod("3mon", "cumul", final=False,
                                             descriptive_name='3-monthly Precipitation',
                                             description='Precipitation for 3 months',
                                             frequency_id='e3month',
                                             date_format='YYYYMMDD',
                                             masked=False,
                                             timeseries_role='',
                                             active_default=True)

    out_prod_ident_3moncum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    output_subdir_3moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)

    def generate_parameters_3moncum():

        # Number of months to consider
        n_mon = 3
        dates_list = []

        # Extract and sort all dates
        for input_file in input_files:
            basename=os.path.basename(input_file)
            mydate=functions.get_date_from_path_filename(basename)
            mydate_yyyymmdd=str(mydate)[0:8]
            dates_list.append(mydate_yyyymmdd)

        dates_list = sorted(dates_list)
        # loop from the 'n_mon'-1 date to the last date - this is the period end-limit
        for date_index in range(n_mon-1,len(dates_list)-1):

            mydate = dates_list[date_index]
            prev_date = dates_list[date_index-n_mon+1]
            file_list = []
            # Get month-date and
            m_1 = datetime.date(int(mydate[0:4]),int(mydate[4:6]),1)
            m_2 = datetime.date(int(prev_date[0:4]),int(prev_date[4:6]),1)
            delta = m_1 - m_2
            # Check there are no missing month, i.e. tot_delta < 155 days
            if delta.days <=(31*(n_mon-1)):
                for curr_index in range(0,n_mon):
                    curr_date = dates_list[date_index-curr_index]
                    if os.path.isfile(input_dir+curr_date+in_prod_ident):
                        file_list.append(input_dir+curr_date+in_prod_ident)

                output_file=es_constants.processing_dir+output_subdir_3moncum+os.path.sep+mydate+out_prod_ident_3moncum
                yield (file_list, output_file)
            else:
                print ('At least 1 month is missing for period ending {0}'.format(mydate))

    @active_if(activate_cumul_3mon_comput)
    @files(generate_parameters_3moncum)
    def std_precip_3moncum(input_file, output_file):

        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
        raster_image_math.do_cumulate(**args)

    # #   ---------------------------------------------------------------------
    # #   Cumulated products - 6mon
    # #   ---------------------------------------------------------------------
    #
    # output_sprod_group=proc_lists.proc_add_subprod_group("cumul")
    # output_sprod=proc_lists.proc_add_subprod("6mon", "cumul", final=False,
    #                                          descriptive_name='3-monthly Precipitation',
    #                                          description='Precipitation for 3 months',
    #                                          frequency_id='e3month',
    #                                          date_format='YYYYMMDD',
    #                                          masked=False,
    #                                          timeseries_role='',
    #                                          active_default=True)
    #
    # out_prod_ident_6moncum = functions.set_path_filename_no_date(prod, output_sprod, mapset, version, ext)
    # output_subdir_6moncum  = functions.set_path_sub_directory   (prod, output_sprod, 'Derived', version, mapset)
    #
    # def generate_parameters_6moncum():
    #
    #     # Number of months to consider
    #     n_mon = 6
    #     dates_list = []
    #
    #     # Extract and sort all dates
    #     for input_file in input_files:
    #         basename=os.path.basename(input_file)
    #         mydate=functions.get_date_from_path_filename(basename)
    #         mydate_yyyymmdd=str(mydate)[0:8]
    #         dates_list.append(mydate_yyyymmdd)
    #
    #     dates_list = sorted(dates_list)
    #     # loop from the 'n_mon'-1 date to the last date - this is the period end-limit
    #     for date_index in range(n_mon-1,len(dates_list)-1):
    #
    #         mydate = dates_list[date_index]
    #         prev_date = dates_list[date_index-n_mon+1]
    #         file_list = []
    #         # Get month-date and
    #         m_1 = datetime.date(int(mydate[0:4]),int(mydate[4:6]),1)
    #         m_2 = datetime.date(int(prev_date[0:4]),int(prev_date[4:6]),1)
    #         delta = m_1 - m_2
    #         # Check there are no missing month, i.e. tot_delta < 155 days
    #         if delta.days <=(31*(n_mon-1)):
    #             for curr_index in range(0,n_mon):
    #                 curr_date = dates_list[date_index-curr_index]
    #                 if os.path.isfile(input_dir+curr_date+in_prod_ident):
    #                     file_list.append(input_dir+curr_date+in_prod_ident)
    #
    #             output_file=es_constants.processing_dir+output_subdir_6moncum+os.path.sep+mydate+out_prod_ident_6moncum
    #             yield (file_list, output_file)
    #         else:
    #             print 'At least 1 month is missing for period ending {0}'.format(mydate)
    #
    # @active_if(activate_cumul_6mon_comput)
    # @files(generate_parameters_6moncum)
    # def std_precip_6moncum(input_file, output_file):
    #
    #     output_file = functions.list_to_element(output_file)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
    #     raster_image_math.do_cumulate(**args)

    # End of pipeline definition
    return proc_lists

#   ---------------------------------------------------------------------
#   Drive the pipeline: 1 function only is defined, a main one:
#
#       processing_std_spi_monthly -> create and run the pipeline
#
#   ---------------------------------------------------------------------

#   ---------------------------------------------------------------------

#   Function:   processing_std_spi_monthly
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

def processing_std_spi_monthly(res_queue, pipeline_run_level=0,pipeline_printout_level=0,
                          pipeline_printout_graph_level=0, prod='', starting_sprod='', mapset='', version='',
                          starting_dates=None, write2file=None, logfile=None):

    spec_logger = log.my_logger(logfile)
    spec_logger.info("Entering routine %s" % 'processing_std_spi_monthly')

    proc_lists = None
    proc_lists = create_pipeline(prod=prod, starting_sprod=starting_sprod, mapset=mapset, version=version,
                                 starting_dates=starting_dates, proc_lists=proc_lists)

    if write2file is not None:
        fwrite_id=open(write2file,'w')
    else:
        fwrite_id=None

    if pipeline_run_level > 0:
        spec_logger.info("Run the pipeline %s" % 'processing_std_spi_monthly')
        pipeline_run(verbose=pipeline_run_level, logger=spec_logger, log_exceptions=spec_logger, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_spi_monthly.sqlite'),\
                     checksum_level=0)
        spec_logger.info("After running the pipeline %s" % 'processing_std_precip_spi_monthly')

    if pipeline_printout_level > 0:
        pipeline_printout(verbose=pipeline_printout_level, output_stream=fwrite_id, history_file=os.path.join(es_constants.log_dir,'.ruffus_history_spi_monthly.sqlite'),\
                     checksum_level=0)

    if pipeline_printout_graph_level > 0:
        pipeline_printout_graph('flowchart.jpg')

    if write2file is not None:
        fwrite_id.close()

    #res_queue.put(proc_lists)
    return True
