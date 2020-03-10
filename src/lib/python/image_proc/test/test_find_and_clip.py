from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase
from lib.python.image_proc.find_and_clip_file import *

import os

__author__ = "Marco Clerici"

class TestClip(TestCase):

    output_dir = '/eStation2/mydata/Tests/clip/'
    # output_dir = '/data/processing/exchange/Tests/clip/'

    def test_spotv_africa_to_sadc(self):

        requested_file = '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-SADC-1km/tif/ndv/20180111_vgt-ndvi_ndv_SPOTV-SADC-1km_sv2-pv2.2.tif'
        # The following fields are taken from a 'request' generated on mesa-proc

        output_mapset = {
            "description": "SADC definition",
            "mapsetcode": "SPOTV-SADC-1km",
            "pixel_shift_lat": -0.008928571428571,
            "pixel_shift_long": 0.008928571428571,
            "pixel_size_x": 5489,
            "pixel_size_y": 4593,
            "rotation_factor_lat": 0.0,
            "rotation_factor_long": 0.0,
            "srs_wkt": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
            "upper_left_lat": 6.0044642857143,
            "upper_left_long": 10.99553571
        }

        output_file = self.output_dir+os.path.basename(requested_file)

        if os.path.exists(requested_file):
            print ('Requested file exists, no need to clip. Exit')
            exit()

        larger_file = do_find_larger(requested_file, output_mapset)
        if larger_file is not '':
            do_clip(larger_file, output_file, output_mapset)
        else:
            print ('ERROR: No any file found. Exit')
            exit()

        # Copy input file to output dir (for checking)
        command='cp '+larger_file+' '+self.output_dir
        os.system(command)

    def test_spotv_africa_to_igad(self):

        requested_file='/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-IGAD-1km/tif/ndv/20180101_vgt-ndvi_ndv_SPOTV-IGAD-1km_sv2-pv2.1.tif'
        # The following fields are taken from a 'request' generated on mesa-proc

        output_mapset={"description": "IGAD definition",
                       "mapsetcode": "SPOTV-IGAD-1km",
                       "pixel_shift_lat": -0.008928571428571,
                       "pixel_shift_long": 0.008928571428571,
                       "pixel_size_x": 3473,
                       "pixel_size_y": 4050,
                       "rotation_factor_lat": 0.0,
                       "rotation_factor_long": 0.0,
                       "srs_wkt": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
                       "upper_left_lat": 24.0044642857143,
                       "upper_left_long": 20.99553571}

        output_file=self.output_dir+os.path.basename(requested_file)

        if os.path.exists(requested_file):
            print ('Requested file exists, no need to clip. Exit')
            exit()

        larger_file = do_find_larger(requested_file, output_mapset)
        if larger_file is not '':
            do_clip(larger_file, output_file, output_mapset)
        else:
            print ('ERROR: No any file found. Exit')
            exit()

        # Copy input file to output dir (for checking)
        command='cp '+larger_file+' '+self.output_dir
        os.system(command)

    def test_modis_africa_to_ioc(self):

        requested_file='/data/processing/modis-sst/v2013.1/MODIS-IOC-4km/tif/sst-day/20160629_modis-sst_sst-day_MODIS-IOC-4km_v2013.1.tif'
        # The following fields are taken from a 'request' generated on mesa-proc

        output_mapset={"description": "IOC 4km (MODIS)",
                       "mapsetcode": "MODIS-IOC-4km",
                       "pixel_shift_lat": -0.0416666666666667,
                       "pixel_shift_long": 0.0416666666666667,
                       "pixel_size_x": 1032,
                       "pixel_size_y": 792,
                       "rotation_factor_lat": 0.0,
                       "rotation_factor_long": 0.0,
                       "srs_wkt": "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9108\"]],AUTHORITY[\"EPSG\",\"4326\"]]",
                       "upper_left_lat": 5.0,
                       "upper_left_long": 32.0}

        output_file=self.output_dir+os.path.basename(requested_file)

        if os.path.exists(requested_file):
            print ('Requested file exists, no need to clip. Exit')
            exit()

        larger_file = do_find_larger(requested_file, output_mapset)
        if larger_file is not '':
            do_clip(larger_file, output_file, output_mapset)
        else:
            print ('ERROR: No any file found. Exit')
            exit()

        # Copy input file to output dir (for checking)
        command='cp '+larger_file+' '+self.output_dir
        os.system(command)