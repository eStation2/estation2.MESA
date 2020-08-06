from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Jurriaan van 't Klooster"

import unittest
import os
import shutil

import lib.python.functions as functions
from lib.python.image_proc import raster_image_math

class TestFunctions(unittest.TestCase):


    def test_fronts(self):
        # See: https: // code.env.duke.edu / projects / mget / export / HEAD / MGET / Trunk / PythonPackage / dist / TracOnlineDocumentation / Documentation / ArcGISReference / CayulaCornillonEdgeDetection.DetectEdgesInBinaryRaster.html

        # Static Definitions
        base_input_dir  = '/data/processing/'
        output_base_dir = '/data/processing/exchange/Tests/Fronts/'

        # ============ Select the product ========================
        product = 'pml-modis-sst'

        if product == 'pml-modis-sst':
            version='3.0'
            subproduct='sst-3day'
            type='tif'
            region='SPOTV-IOC-1km'
            date='20161017'

            # Best found so far ...

            # parameters = {'histogramWindowStride': 4,
            #               'histogramWindowSize': 32,
            #               'minTheta': 0.76,
            #               'minPopProp': 0.25,
            #               'minPopMeanDifference': 45,  # Temperature: 0.45 deg (multiply by 100 !!)
            #               'minSinglePopCohesion': 0.60,
            #               'minImageValue': 1,
            #               'minThreshold': 2}

        if product == 'pml-modis-chl':
            version='3.0'
            subproduct='chl-3day'
            type='tif'
            region='SPOTV-IOC-1km'
            date='20161017'

        if product == 'modis-sst':
            version='v2013.1'
            subproduct='monavg'
            type='derived'
            region='MODIS-IOC-4km'
            date='20161001'

        # ============ Define parameters ========================

        parameters = {'histogramWindowStride': 16,
                      'histogramWindowSize': 32,
                      'minTheta': 0.76,
                      'minPopProp': 0.25,
                      'minPopMeanDifference': 25,       # Temperature: 0.45 deg (multiply by 100 !!)
                      'minSinglePopCohesion': 0.90,
                      'minImageValue': 1,
                      'minThreshold': 1}

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

        output_id = '_WSz={0}_WStr={1}_MDif={2}_Thr={3}_mTh={4}_mPopCo={5}'\
                                                         .format(parameters['histogramWindowSize'],
                                                                 parameters['histogramWindowStride'],
                                                                 parameters['minPopMeanDifference'],
                                                                 parameters['minThreshold'],
                                                                 parameters['minTheta'],
                                                                 parameters['minSinglePopCohesion'])

        output_dir = output_base_dir + \
                     product + os.path.sep + \
                     version + os.path.sep + \
                     region + os.path.sep + \
                     subproduct + os.path.sep+\
                     date+ os.path.sep

        functions.check_output_dir(output_dir)

        output_filename = '{0}_{1}_{2}_{3}_{4}{5}{6}'.format(date, product, subproduct, region, version, output_id,'.tif')

        output_file=output_dir+output_filename

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw",
                "parameters": parameters}

        # ============ Run the algo   ========================

        raster_image_math.do_detect_sst_fronts(**args)

        # ============ Copy input in output   ================

        shutil.copy(input_file,output_dir)
