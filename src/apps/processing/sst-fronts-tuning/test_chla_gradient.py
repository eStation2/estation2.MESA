from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici"

import unittest
import os
import shutil

import lib.python.functions as functions
from lib.python.image_proc import raster_image_math

class TestFunctions(unittest.TestCase):


    def test_chla_gradient(self):

        # Static Definitions
        base_input_dir  = '/data/processing/'
        output_base_dir = '/data/processing/test_OTJT/'

        # ============ Select the product ========================
        product = 'olci-wrr'

        if product == 'pml-modis-sst':
            version='3.0'
            subproduct='sst-3day'
            type='tif'
            region='SPOTV-IOC-1km'
            date='20161017'

        if product == 'olci-wrr':
            version='V02.0'
            subproduct='chl-oc4me'
            type='tif'
            region='SPOTV-Africa-1km'
            date='20180722'

        # ============ Assignements: DO NOT modify   ========================
        input_dir = base_input_dir + \
                    product + os.path.sep + \
                    version + os.path.sep + \
                    region + os.path.sep + \
                    type + os.path.sep + \
                    subproduct + \
                    os.path.sep

        filename = '{0}_{1}_{2}_{3}_{4}{5}'.format(date, product, subproduct, region, version, '.tif')
        input_file = input_dir + filename

        output_id = '_Gradient_nearest_nodata_nan_1'

        output_dir = output_base_dir + \
                     product + os.path.sep + \
                     version + os.path.sep + \
                     region + os.path.sep + \
                     subproduct + os.path.sep+\
                     date+ os.path.sep

        functions.check_output_dir(output_dir)

        output_filename = '{0}_{1}_{2}_{3}_{4}{5}{6}'.format(date, product, subproduct, region, version, output_id,'.tif')

        output_file=output_dir+output_filename

        args = {"chla_file": input_file, "chla_nodata": 1000, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}

        # ============ Run the algo   ========================

        raster_image_math.do_compute_chla_gradient(**args)

        # ============ Copy input in output   ================

        shutil.copy(input_file,output_dir)
