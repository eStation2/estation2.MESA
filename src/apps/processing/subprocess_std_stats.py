#
#	purpose: Define the sub processing chains
#	author:  Vijay Charan Venkatachalam
#	date:	 07.08.2019
#   descr:	 This class can be used to create basic stats which replaces the existing long create pipeline method.
#            The switches for the subproducts computation and ruffus syntax remain in the create pipline method
#            To use this class, intialize it with the product info and can change subproducts whenever needed
#	history: 1.0
#   List of processing chains uses this class:
#       1. processing_std_swi ---> Soil water index ASCAT
#       2. processing_std_vgt ---> FAPAR.FCOVER,LAI

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import object

# Import standard modules
import os
from future import standard_library

from config import es_constants
# Import eStation2 modules
from lib.python import functions
from lib.python.image_proc import raster_image_math

# Import third-party modules

_author__ = "Vijay Charan Venkatachalam"

standard_library.install_aliases()


class SubProcessStatsES2(object):
    def __init__(self, prod, starting_sprod, mapset, version, starting_dates=None, proc_lists=None, frequency=None,
                 product_type='Ingest'):

        self.prod = prod
        self.starting_sprod = starting_sprod
        self.mapset = mapset
        self.version = version
        self.starting_dates = starting_dates
        self.proc_lists = proc_lists
        self.frequency = frequency
        self.product_type = product_type
        # ES2-410 This should be used for creating the derived subproduct code dynamically
        self.subproduct_code = starting_sprod
        self.starting_files = []
        #   General definitions for this processing chain
        self.ext = es_constants.ES2_OUTFILE_EXTENSION

        self.es2_data_dir = es_constants.es2globals['processing_dir'] + os.path.sep

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
                # ES2 450 #+++++++ Check file exists before appending  +++++++++++++++
                if functions.is_file_exists_in_path(input_dir + my_date + self.in_prod_ident):
                    self.starting_files.append(input_dir + my_date + self.in_prod_ident)
        else:
            self.starting_files = input_dir + "*" + self.in_prod_ident

        #   ---------------------------------------------------------------------
        #   Initialize the monthly input prod
        #   ---------------------------------------------------------------------
        self.intialize_month_parameters()

    def intialize_month_parameters(self):
        #   ---------------------------------------------------------------------
        #   Initialize the monthly input prod
        #   ---------------------------------------------------------------------
        self.input_subprod_monthly = "mon" + self.subproduct_code

        self.in_prod_ident_monthly = functions.set_path_filename_no_date(self.prod, self.input_subprod_monthly,
                                                                         self.mapset, self.version, self.ext)

        input_dir_monthly = self.es2_data_dir + \
                            functions.set_path_sub_directory(self.prod, self.input_subprod_monthly, 'Derived',
                                                             self.version, self.mapset)

        self.starting_files_mon_prod = input_dir_monthly + "*" + self.in_prod_ident_monthly

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
                # ES2 450 #+++++++ Check file exists before appending  +++++++++++++++
                if functions.is_file_exists_in_path(input_dir + my_date + self.in_prod_ident):
                    self.starting_files.append(input_dir + my_date + self.in_prod_ident)
        else:
            self.starting_files = input_dir + "*" + self.in_prod_ident

    def change_frequency_params(self, frequency=None):
        self.frequency = frequency

    def do_average(self):

        if self.frequency == '10d':
            #   ---------------------------------------------------------------------
            #   Average
            output_sprod_group = self.proc_lists.proc_add_subprod_group("10dstats")
            output_sprod = self.proc_lists.proc_add_subprod("10davg", "10dstats", final=False,
                                                            descriptive_name='10d Average ' + self.subproduct_code,
                                                            description='Long Term Average for ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=2,
                                                            active_default=True)

            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                 self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                             self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]
        else:

            output_sprod_group = self.proc_lists.proc_add_subprod_group("monthly_stats")
            output_sprod = self.proc_lists.proc_add_subprod("1monavg", "monthly_stats", final=False,
                                                            descriptive_name='Monthly Average ' + self.subproduct_code,
                                                            description='Monthly Average ' + self.subproduct_code,
                                                            frequency_id='e1month',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.input_subprod_monthly,  # '10d',
                                                            # display_index=112,
                                                            active_default=True)

            prod_ident_1monavg = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                     self.ext)
            subdir_1monavg = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                              self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monavg + "{MMDD[0]}" + prod_ident_1monavg

    def do_minimum(self):
        #   ---------------------------------------------------------------------
        #   Minimum
        if self.frequency == '10d':
            output_sprod = self.proc_lists.proc_add_subprod("10dmin", "10dstats", final=False,
                                                            descriptive_name='10d Minimum ' + self.subproduct_code,
                                                            description='Long Term Minimum for ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=3,
                                                            active_default=True)

            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                 self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                             self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]

        else:
            output_sprod = self.proc_lists.proc_add_subprod("1monmin", "monthly_stats", final=False,
                                                            descriptive_name='Monthly Minimum ' + self.subproduct_code,
                                                            description='Monthly Minimum ' + self.subproduct_code,
                                                            frequency_id='e1month',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.input_subprod_monthly,  # '10d',
                                                            # display_index=113,
                                                            active_default=True)

            prod_ident_1monmin = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                     self.ext)
            subdir_1monmin = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                              self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monmin + "{MMDD[0]}" + prod_ident_1monmin

    def do_maximum(self):
        #   ---------------------------------------------------------------------
        #   Maximum
        if self.frequency == '10d':
            output_sprod = self.proc_lists.proc_add_subprod("10dmax", "10dstats", final=False,
                                                            descriptive_name='10d Maximum ' + self.subproduct_code,
                                                            description='Long Term Maximum for ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=4,
                                                            active_default=True)
            out_prod_ident = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                 self.ext)
            output_subdir = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                             self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = ["{subpath[0][5]}" + os.path.sep + output_subdir + "{MMDD[0]}" + out_prod_ident]
        else:
            output_sprod = self.proc_lists.proc_add_subprod("1monmax", "monthly_stats", final=False,
                                                            descriptive_name='Monthly Maximum ' + self.subproduct_code,
                                                            description='Monthly Maximum ' + self.subproduct_code,
                                                            frequency_id='e1month',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.input_subprod_monthly,  # '10d',
                                                            # display_index=114,
                                                            active_default=True)

            prod_ident_1monmax = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                     self.ext)
            subdir_1monmax = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                              self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1monmax + "{MMDD[0]}" + prod_ident_1monmax

    def do_standard_deviation(self):
        # #  ---------------------------------------------------------------------
        # #  standard deviation
        if self.frequency == '10d':

            output_sprod = self.proc_lists.proc_add_subprod("10dstd", "10dstats", final=False,
                                                            descriptive_name='10d Standard deviation ' + self.subproduct_code,
                                                            description='Standard deviation ' + self.subproduct_code,
                                                            frequency_id='e1dekad',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.starting_sprod,  # '10d',
                                                            # display_index=5,
                                                            active_default=True)

            prod_ident_10dstd = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                    self.ext)
            subdir_10dstd = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                             self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident
            self.formatter_out = ["{subpath[0][5]}" + os.path.sep + subdir_10dstd + "{MMDD[0]}" + prod_ident_10dstd]

            ancillary_sprod = "10davg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset,
                                                                        self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version,
                                                                self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

        else:

            output_sprod = self.proc_lists.proc_add_subprod("1monstd", "monthly_stats", final=False,
                                                            descriptive_name='Monthly Standard deviation ' + self.subproduct_code,
                                                            description='Monthly Standard deviation ' + self.subproduct_code,
                                                            frequency_id='e1month',
                                                            date_format='MMDD',
                                                            masked=False,
                                                            timeseries_role=self.input_subprod_monthly,  # '10d',
                                                            # display_index=115,
                                                            active_default=True)

            prod_ident_1mondev = functions.set_path_filename_no_date(self.prod, output_sprod, self.mapset, self.version,
                                                                     self.ext)
            subdir_1mondev = functions.set_path_sub_directory(self.prod, output_sprod, 'Derived', self.version,
                                                              self.mapset)

            self.formatter_in = "[0-9]{4}(?P<MMDD>[0-9]{4})" + self.in_prod_ident_monthly
            self.formatter_out = "{subpath[0][5]}" + os.path.sep + subdir_1mondev + "{MMDD[0]}" + prod_ident_1mondev

            ancillary_sprod = "1monavg"
            ancillary_sprod_ident = functions.set_path_filename_no_date(self.prod, ancillary_sprod, self.mapset,
                                                                        self.version, self.ext)
            ancillary_subdir = functions.set_path_sub_directory(self.prod, ancillary_sprod, 'Derived', self.version,
                                                                self.mapset)
            self.ancillary_input = "{subpath[0][5]}" + os.path.sep + ancillary_subdir + "{MMDD[0]}" + ancillary_sprod_ident

    def create_basic_stats_proclist(self, stats_type):

        if stats_type == 'Average':
            self.do_average()

        if stats_type == 'Minimum':
            self.do_minimum()

        if stats_type == 'Maximum':
            self.do_maximum()

        if stats_type == 'standard_deviation':
            self.do_standard_deviation()


def compute_maximum(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    reduced_list = functions.exclude_current_year(input_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress=lzw"}
    raster_image_math.do_max_image(**args)


def compute_average(input_file, output_file):
    reduced_list = functions.exclude_current_year(input_file)
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress=lzw"}
    raster_image_math.do_avg_image(**args)


def compute_minimum(input_file, output_file):
    output_file = functions.list_to_element(output_file)
    reduced_list = functions.exclude_current_year(input_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": reduced_list, "output_file": output_file, "output_format": 'GTIFF',
            "options": "compress=lzw"}
    raster_image_math.do_min_image(**args)


def compute_product_std_deviation(input_file, output_file):
    current_file = [i[0] for i in input_file]
    avg_file = [i[1] for i in input_file][0]
    output_file = functions.list_to_element(output_file)
    functions.check_output_dir(os.path.dirname(output_file))
    args = {"input_file": current_file, "avg_file": avg_file, "output_format": 'GTIFF',
            "options": "compress=lzw", "output_stddev": output_file}
    raster_image_math.do_stddev_image(**args)
