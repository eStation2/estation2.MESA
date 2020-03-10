from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
_author__ = "Vijay Charan Venkatachalam"
#
#	purpose: Define the sub processing chains
#	author:  Vijay Charan Venkatachalam
#	date:	 07.08.2019
#   descr:	 This class can be used to create basic prods and anomaly which replaces the existing long create pipeline method.
#            The switches for the subproducts computation and ruffus syntax remain in the create pipline method
#            To use this class, intialize it with the product info and can change subproducts whenever needed
#	history: 1.0
#   List of processing chains uses this class:
#       1. processing_std_swi ---> Soil water index ASCAT
#       2. processing_std_vgt ---> FAPAR.FCOVER,LAI

# import standard modules
import os, sys

import glob, datetime
from multiprocessing import *

# import eStation2 modules

from lib.python import functions
from lib.python.image_proc import raster_image_math
from config import es_constants

# Import third-party modules
from ruffus import *


class SubProcessProdsES2(object):
    def __init__(self, prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, frequency=None, product_type='Ingest'):

        self.prod = prod
        self.starting_sprod = starting_sprod
        self.mapset = mapset
        self.version = version
        self.starting_dates = starting_dates
        self.proc_lists = proc_lists
        self.frequency = frequency
        self.product_type = product_type
        self.starting_files = []
        # ES2-410 This should be used for creating the derived subproduct code dynamically
        self.subproduct_code = starting_sprod
        #   General definitions for this processing chain
        self.ext = es_constants.ES2_OUTFILE_EXTENSION

        self.es2_data_dir = es_constants.es2globals['processing_dir']+os.path.sep

        #   ---------------------------------------------------------------------
        #   Define input files
        self.in_prod_ident = functions.set_path_filename_no_date(self.prod, self.starting_sprod, self.mapset, self.version, self.ext)

        #logger.debug('Base data directory is: %s' % es2_data_dir)
        input_dir = self.es2_data_dir+ \
                    functions.set_path_sub_directory(self.prod, self.starting_sprod, self.product_type, self.version, self.mapset)

        if self.starting_dates is not None:
            # starting_files = []
            for my_date in self.starting_dates:
                #ES2 450 #+++++++ Check file exists before appending  +++++++++++++++
                if functions.is_file_exists_in_path(input_dir+my_date+self.in_prod_ident):
                    self.starting_files.append(input_dir+my_date+self.in_prod_ident)
        else:
            self.starting_files=input_dir+"*"+self.in_prod_ident

        #   Look for all input files in input_dir, and sort them
        if self.starting_dates is not None:
            self.input_files = self.starting_files
        else:
            self.input_files = glob.glob(self.starting_files)

        # self.input_files = glob.glob(self.starting_files)

        # #   ---------------------------------------------------------------------
        # #   Initialize the monthly input prod
        # #   ---------------------------------------------------------------------
        self.intialize_month_parameters()

    def change_subProds_params(self, starting_sprod, frequency=None, product_type='Ingest'):
        self.starting_sprod = starting_sprod
        self.change_frequency_params(frequency)
        self.product_type = product_type
        self.starting_files = []

        #   ---------------------------------------------------------------------
        #   Define input files
        self.in_prod_ident = functions.set_path_filename_no_date(self.prod, self.starting_sprod, self.mapset,
                                                                 self.version, self.ext)

        # logger.debug('Base data directory is: %s' % es2_data_dir)
        input_dir = self.es2_data_dir + \
                    functions.set_path_sub_directory(self.prod, self.starting_sprod, self.product_type, self.version,
                                                     self.mapset)

        if self.starting_dates is not None:
            # starting_files = []
            for my_date in self.starting_dates:
                #ES2 450 #+++++++ Check file exists before appending  +++++++++++++++
                if functions.is_file_exists_in_path(input_dir+my_date+self.in_prod_ident):
                    self.starting_files.append(input_dir + my_date + self.in_prod_ident)
        else:
            self.starting_files = input_dir + "*" + self.in_prod_ident

    def change_frequency_params(self, frequency=None):
        self.frequency = frequency

    def generate_parameters_1d_to_10d(self):

        dekad_list = []

        # Create unique list of all dekads (as 'Julian' number)
        for input_file in self.input_files:
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

                for input_file in self.input_files:

                    basename=os.path.basename(input_file)
                    mydate_yyyymmdd=functions.get_date_from_path_filename(basename)
                    mydekad_nbr=functions.conv_date_2_dekad(mydate_yyyymmdd[0:8])
                    if mydekad_nbr == dekad:
                        file_list.append(input_file)

                    output_file=es_constants.processing_dir+self.output_subdir_10d+os.path.sep+my_dekad_str+self.out_prod_ident_10d
                if len(file_list) >= expected_days-1:
                    yield (file_list, output_file)
                else:
                    print ('Too many missing filed for dekad {0}'.format(my_dekad_str))

    def do_10d_from_1d(self):
        #   ---------------------------------------------------------------------
        #   Derived product: 10dcumul
        #   ---------------------------------------------------------------------

        output_sprod_group = self.proc_lists.proc_add_subprod_group("10d_prod")
        output_sprod = self.proc_lists.proc_add_subprod("10d", "10d_prod", final=False,
                                                   descriptive_name='10d '+ self.subproduct_code,
                                                   description=self.subproduct_code+' for dekad',
                                                   frequency_id='e1dekad',
                                                   date_format='YYYYMMDD',
                                                   masked=False,
                                                   timeseries_role='Initial',
                                                   active_default=True)

        self.out_prod_ident_10d = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
        self.output_subdir_10d = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

    def create_basic_anomaly_proclist(self, anomaly_type):
        # #   ---------------------------------------------------------------------
        # #   Create lists
        # if self.proc_lists is None:
        #     proc_lists = functions.ProcLists()

        if anomaly_type == '10dDiff':
            self.do_absolute_difference()

        if anomaly_type == '10dperc':
            self.do_percent_difference()

        if anomaly_type == '10dna':
            self.do_normalized_anomaly()

        if anomaly_type == '10dratio':
            self.do_ratio()

        if anomaly_type == '10standardized':
            self.do_standardized_prod()

    def do_absolute_difference(self):
        #   ---------------------------------------------------------------------
        #   10dDiff
        if self.frequency == '10d':

            output_sprod_group = self.proc_lists.proc_add_subprod_group("10anomalies")
            output_sprod = self.proc_lists.proc_add_subprod("10ddiff", "10anomalies", final=False,
                                                            descriptive_name='10d Absolute Difference ' + self.subproduct_code,
                                                            description='10d Absolute Difference vs. LTA',
                                                            frequency_id='e1dekad',
                                                            date_format='YYYYMMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod, #'10d',
                                                            # display_index=6,
                                                            active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            #   Starting files + avg
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

            ancillary_sprod = "10davg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version,
                                                                        self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version,
                                                                self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

        else:
            output_sprod = self.proc_lists.proc_add_subprod("1mondiff", "filtered_anomalies", final=False,
                                                       descriptive_name='Monthly Absolute Difference ' + self.subproduct_code,
                                                       description='Monthly Absolute Difference ' + self.subproduct_code,
                                                       frequency_id='e1month',
                                                       date_format='YYYYMMDD',
                                                       masked=False,
                                                        timeseries_role=self.input_subprod_monthly,  # '10d',
                                                        # display_index=116,
                                                       active_default=True)

            prod_ident_1mondiff = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            subdir_1mondiff = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1mondiff + "{YYYY[0]}{MMDD[0]}" + prod_ident_1mondiff

            ancillary_sprod = "1monavg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident


    def do_percent_difference(self):
        # Percent Difference
        if self.frequency == '10d':
            output_sprod = self.proc_lists.proc_add_subprod("10dperc", "10anomalies", final=False,
                                                            descriptive_name='10d Percent Difference ' + self.subproduct_code,
                                                            description='10d Percent Difference vs. LTA',
                                                            frequency_id='e1dekad',
                                                            date_format='YYYYMMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=7,
                                                            active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            #   Starting files + avg
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

            ancillary_sprod = "10davg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident
        else:

            output_sprod = self.proc_lists.proc_add_subprod("1monperc", "filtered_anomalies", final=False,
                                                       descriptive_name='Monthly Percent Difference',
                                                       description='Monthly Percent Difference',
                                                       frequency_id='e1month',
                                                       date_format='YYYYMMDD',
                                                       masked=False,
                                                        timeseries_role=self.input_subprod_monthly,  # '10d',
                                                        # display_index=117,
                                                       active_default=True)
            prod_ident_1monperc = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            subdir_1monperc = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            # inputs
            #   Starting files + avg
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monperc + "{YYYY[0]}{MMDD[0]}" + prod_ident_1monperc

            ancillary_sprod = "1monavg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    def do_normalized_anomaly(self):
        #   ---------------------------------------------------------------------
        #   Normalized Anomaly
        if self.frequency == '10d':

            output_sprod = self.proc_lists.proc_add_subprod("10dna", "10anomalies", final=False,
                                                            descriptive_name='10d Normalized Anomaly ' + self.subproduct_code,
                                                            description='10d Normalized Anomaly ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='YYYYMMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod, #'10d',
                                                            # display_index=9,
                                                            active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                 self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            #   Starting files + min + max
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

            ancillary_sprod_1 = "10dmin"
            ancillary_sprod_ident_1 = functions.set_path_filename_no_date(self.prod, ancillary_sprod_1, self.mapset,
                                                                          self.version, self.ext)
            ancillary_subdir_1 = functions.set_path_sub_directory(self.prod, ancillary_sprod_1, 'Derived', self.version,
                                                                  self.mapset)
            self.ancillary_input_1 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_1 + "{MMDD[0]}" + ancillary_sprod_ident_1

            ancillary_sprod_2 = "10dmax"
            ancillary_sprod_ident_2 = functions.set_path_filename_no_date(self.prod, ancillary_sprod_2, self.mapset,
                                                                          self.version, self.ext)
            ancillary_subdir_2 = functions.set_path_sub_directory(self.prod, ancillary_sprod_2, 'Derived', self.version,
                                                                  self.mapset)
            self.ancillary_input_2 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_2 + "{MMDD[0]}" + ancillary_sprod_ident_2

        else:
            output_sprod = self.proc_lists.proc_add_subprod("1monna", "monanomalies", final=False,
                                                       descriptive_name='Monthly Normalized Anomaly ' + self.subproduct_code,
                                                       description='Monthly Normalized Anomaly ' + self.subproduct_code,
                                                       frequency_id='e1month',
                                                       date_format='YYYYMMDD',
                                                       masked=False,
                                                        timeseries_role=self.input_subprod_monthly,  # '10d',
                                                        # display_index=119,
                                                       active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            #   Starting files + min + max
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

            ancillary_sprod_1 = "1monmin"
            ancillary_sprod_ident_1 = functions.set_path_filename_no_date(self.prod, ancillary_sprod_1, self.mapset, self.version, self.ext)
            ancillary_subdir_1 = functions.set_path_sub_directory(self.prod, ancillary_sprod_1, 'Derived', self.version, self.mapset)
            self.ancillary_input_1 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_1 + "{MMDD[0]}" + ancillary_sprod_ident_1

            ancillary_sprod_2 = "1monmax"
            ancillary_sprod_ident_2 = functions.set_path_filename_no_date(self.prod, ancillary_sprod_2, self.mapset, self.version, self.ext)
            ancillary_subdir_2 = functions.set_path_sub_directory(self.prod, ancillary_sprod_2, 'Derived', self.version, self.mapset)
            self.ancillary_input_2 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_2 + "{MMDD[0]}" + ancillary_sprod_ident_2

    def do_ratio(self):
        # ---------------------------------------------------------------------
        #   10dratio
        if self.frequency == '10d':

            output_sprod = self.proc_lists.proc_add_subprod("10dratio", "10anomalies", final=False,
                                                            descriptive_name='10d Ratio ' + self.subproduct_code,
                                                            description='10d Ratio (curr/avg) ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='YYYYMMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod, #'10d',
                                                            # display_index=8,
                                                            active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                 self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            #   Starting files + min + max
            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + output_subdir + "{YYYY[0]}{MMDD[0]}" + out_prod_ident

            ancillary_sprod_1 = "10davg"
            ancillary_sprod_ident_1 = functions.set_path_filename_no_date(self.prod, ancillary_sprod_1, self.mapset,
                                                                          self.version, self.ext)
            ancillary_subdir_1 = functions.set_path_sub_directory(self.prod, ancillary_sprod_1, 'Derived', self.version,
                                                                  self.mapset)
            self.ancillary_input_1 = "{subpath[0][5]}" + os.path.sep + ancillary_subdir_1 + "{MMDD[0]}" + ancillary_sprod_ident_1

        else:
            output_sprod = self.proc_lists.proc_add_subprod("1monratio", "filtered_anomalies", final=False,
                                                       descriptive_name='Monthly Ratio',
                                                       description='Monthly Ratio (curr/avg)',
                                                       frequency_id='e1month',
                                                       date_format='YYYYMMDD',
                                                       masked=False,
                                                       timeseries_role=self.input_subprod_monthly,  # '10d',
                                                        # display_index=118,
                                                       active_default=True)

            prod_ident_ratio_linearx2 = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            subdir_ratio_linearx2 = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = [
                "{subpath[0][5]}" + os.path.sep + subdir_ratio_linearx2 + "{YYYY[0]}{MMDD[0]}" + prod_ident_ratio_linearx2]

            ancillary_sprod = "1monavg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    def do_standardized_prod(self):
        #   ---------------------------------------------------------------------
        #   Standardized 10d product
        if self.frequency=='10d':

            output_sprod = self.proc_lists.proc_add_subprod("10dzscore", "filtered_anomalies", final=False,
                                                            descriptive_name='10d Standardized ' + self.subproduct_code,
                                                            description='Z Score, Standardized ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='YYYYMMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=10,
                                                            active_default=True)

            prod_ident_10dsndvi = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            subdir_10dsndvi = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            input_subprod_10diff = "10ddiff"
            in_prod_ident_10diff = functions.set_path_filename_no_date(self.prod, input_subprod_10diff, self.mapset, self.version, self.ext)
            input_dir_10diff = self.es2_data_dir + \
                               functions.set_path_sub_directory(self.prod, input_subprod_10diff, 'Derived', self.version, self.mapset)
            self.starting_files_10ddiff = input_dir_10diff + "*" + in_prod_ident_10diff

            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_10diff
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_10dsndvi + "{YYYY[0]}{MMDD[0]}" + prod_ident_10dsndvi

            ancillary_sprod = "10dstd"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident
        else:
            output_sprod = self.proc_lists.proc_add_subprod("1monzscore", "filtered_anomalies", final=False,
                                                       descriptive_name='Monthly Standardized ' + self.subproduct_code,
                                                       description='Z Score, Monthly Standardized ' + self.subproduct_code,
                                                       frequency_id='e1month',
                                                       date_format='YYYYMMDD',
                                                       masked=False,
                                                        timeseries_role=self.input_subprod_monthly,  # '10d',
                                                        # display_index=120,
                                                       active_default=True)

            prod_ident_1monstdprod = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
            subdir_1monstdprod = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

            input_subprod_mondiff = "1mondiff"
            in_prod_ident_mondiff = functions.set_path_filename_no_date(self.prod, input_subprod_mondiff, self.mapset, self.version,
                                                                        self.ext)

            input_dir_mondiff = self.es2_data_dir + \
                                functions.set_path_sub_directory(self.prod, input_subprod_mondiff, 'Derived', self.version,
                                                                 self.mapset)

            self.starting_files_mondiff = input_dir_mondiff + "*" + in_prod_ident_mondiff

            self.formatter_in = "(?P<YYYY>[0-9]{4})(?P<MMDD>[0-9]{4})" + in_prod_ident_mondiff
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monstdprod + "{YYYY[0]}{MMDD[0]}" + prod_ident_1monstdprod

            ancillary_sprod = "1monstd"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset, self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version, self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    def do_monthly_prod(self):
        #   ---------------------------------------------------------------------
        #   3.a monthly product (avg)
        #   ---------------------------------------------------------------------
        output_sprod_group = self.proc_lists.proc_add_subprod_group("monthly_prod")
        output_sprod = self.proc_lists.proc_add_subprod("mon" + self.subproduct_code, "monthly_prod", final=False,
                                                   descriptive_name='Monthly Product ' + self.subproduct_code,
                                                   description='Monthly Product ' + self.subproduct_code,
                                                   frequency_id='e1month',
                                                   date_format='YYYYMMDD',
                                                   masked=False,
                                                   timeseries_role='',
                                                   active_default=True)

        prod_ident_mon = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version, self.ext)
        subdir_mon = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version, self.mapset)

        self.formatter_in = "(?P<YYYYMM>[0-9]{6})(?P<DD>[0-9]{2})" + self.in_prod_ident
        self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_mon + "{YYYYMM[0]}" + '01' + prod_ident_mon

        # To initialize the monthly parameters (check if ruffus initiate this)
        self.intialize_month_parameters()

    def intialize_month_parameters(self):
        #   ---------------------------------------------------------------------
        #   Initialize the monthly input prod
        #   ---------------------------------------------------------------------
        self.input_subprod_monthly = "mon" + self.subproduct_code

        self.in_prod_ident_monthly = functions.set_path_filename_no_date(self.prod, self.input_subprod_monthly, self.mapset, self.version, self.ext)

        input_dir_monthly = self.es2_data_dir + \
                            functions.set_path_sub_directory(self.prod, self.input_subprod_monthly, 'Derived', self.version, self.mapset)

        self.starting_files_mon_prod = input_dir_monthly + "*" + self.in_prod_ident_monthly

#######################################
### List of processing chain methods
########################################

def compute_standardized_products(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress=lzw"}
    raster_image_math.do_oper_division_perc(**args)

def compute_product_ratio(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))

    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
    raster_image_math.do_oper_division_perc(**args)

def compute_percentage_diff_vs_avg(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file[0], "avg_file": input_file[1], "output_file": output_file,
            "output_format": 'GTIFF', "options": "compress=lzw"}
    raster_image_math.do_compute_perc_diff_vs_avg(**args)

def compute_absolute_diff(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress=lzw"}
    raster_image_math.do_oper_subtraction(**args)

def compute_product_std_deviation(input_file, output_file):
    current_file = [i[0] for i in input_file]
    avg_file = [i[1] for i in input_file][0]
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": current_file, "output_file": avg_file, "output_format": 'GTIFF', "options": "compress=lzw", "output_stddev":output_file}
    raster_image_math.do_stddev_image(**args)

def compute_normalized_anomaly(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file[0], "min_file": input_file[1],"max_file": input_file[2], "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw"}
    raster_image_math.do_make_vci(**args)

def compute_monthly_prod_from_10d(input_file, output_file):
    # ES2- 235 Do not show temporary products like composite not complete (ex monthly composite available mid month...)
    input_file_date = functions.get_date_from_path_full(input_file[0])
    if len(input_file) == 3:
        if not functions.is_date_current_month(input_file_date):
            output_file = functions.list_to_element(output_file)
            functions.check_output_dir(os.path.dirname(output_file))
            args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
                    "options": "compress = lzw"}
            raster_image_math.do_avg_image(**args)


def compute_10d_from_1d(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress = lzw"}
    raster_image_math.do_avg_image(**args)