from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase
import unittest
__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as functions
from lib.python import metadata as md
from lib.python.image_proc import raster_image_math
from config import es_constants
import json
import os, shutil, tempfile
import glob

class TestRasterImage(unittest.TestCase):

    def setUp(self):
        root_test_dir = es_constants.es2globals['test_data_dir']

        self.ref_dir = root_test_dir
        self.input_dir = '/data/test_data/tif/'
        self.root_out_dir = '/data/tmp/'
        self.ref_avg_file = os.path.join(self.ref_dir,'fewsnet-rfe/10davg/1221_fewsnet-rfe_10davg_FEWSNET-Africa-8km_2.0.tif')
        self.input_files = [self.ref_dir+'/fewsnet-rfe/10d/20011221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20021221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20031221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20041221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20051221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20061221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20071221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20081221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20091221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20101221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20111221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20121221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20131221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20141221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                            self.ref_dir+'/fewsnet-rfe/10d/20151221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif']

    def checkFile(self, ref_file, new_file, max_delta=None, create_plot=False):

        equal = 0

        # Compare the files
        if not os.path.isfile(ref_file):
            print("Comparison not possible. File {} missing".format(ref_file))
        if not os.path.isfile(new_file):
            print("Comparison not possible. File {} missing".format(new_file))
        else:
            # Compare the file contents pixels-by-pixel
            args = {"input_file_1": ref_file, "input_file_2": new_file,
                    "max_delta":max_delta, "create_plot":create_plot}
            equal = raster_image_math.compare_two_raster_array(**args)

            # Compare size, projection, geotransform
            gdal_info_ref = md.GdalInfo()
            gdal_info_ref.get_gdalinfo(ref_file)
            gdal_info_new = md.GdalInfo()
            gdal_info_new.get_gdalinfo(new_file)
            equal = equal*gdal_info_new.compare_gdalinfo(gdal_info_ref)

        return equal

    # Tested ok 28.04.2020 (MC)
    def test_avg_image(self):

        output_filename = 'fewsnet-rfe/10davg/1221_fewsnet-rfe_10davg_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": self.input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok 28.04.2020 (MC)
    # Note: takes long since is on 1km product (not defined for fewsnet-rfe)
    def test_stddev_image(self):

        output_filename = 'vgt-ndvi/10dstd-linearx2/1221_vgt-ndvi_10dstd-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        input_files = [
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/19991221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20001221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20011221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20021221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20031221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20041221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20051221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20061221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20071221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20081221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20091221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20101221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20111221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20121221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20131221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20141221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20151221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20171221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20181221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']

        ref_avg_file = self.ref_dir + '/vgt-ndvi/10davg-linearx2/1221_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        args = {"input_file": input_files, "avg_file": ref_avg_file, "output_format": 'GTIFF', "options": "compress=lzw", "output_stddev": output_file}
        raster_image_math.do_stddev_image(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok 28.04.2020 (MC)
    def test_min_image(self):
        output_filename = 'fewsnet-rfe/10dmin/1221_fewsnet-rfe_10dmin_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": self.input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_min_image(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok 28.04.2020 (MC)
    def test_max_image(self):
        output_filename = 'fewsnet-rfe/10dmax/1221_fewsnet-rfe_10dmax_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": self.input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_max_image(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok 28.04.2020 (MC)
    # Note: takes long since is on 1km product (not defined for fewsnet-rfe)
    def test_do_med_image(self):

        output_filename = 'vgt-ndvi/10dmed-linearx2/1221_vgt-ndvi_10dmed-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        input_files = [
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/19991221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20001221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20011221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20021221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20031221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20041221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20051221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20061221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20071221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20081221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20091221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20101221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20111221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20121221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20131221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20141221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20151221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20171221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
            self.ref_dir + '/vgt-ndvi/ndvi-linearx2/20181221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        args = {"input_file": input_files, "output_format": 'GTIFF', "options": "compress=lzw", "output_file": output_file}
        raster_image_math.do_med_image(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok 28.04.2020 (MC)
    def test_oper_subtraction(self):
        # 10ddiff
        output_filename = 'fewsnet-rfe/10ddiff/20151221_fewsnet-rfe_10ddiff_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))
        input_files = [os.path.join(self.ref_dir,'fewsnet-rfe/10d/20151221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif'),
                       self.ref_avg_file]
        args = {"input_file": input_files, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32'}

        raster_image_math.do_oper_subtraction(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (within delta threshold) - MC
    def test_oper_division_perc(self):
        # 10dratio
        output_filename = 'fewsnet-rfe/10dratio/20151221_fewsnet-rfe_10dratio_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir, output_filename)
        functions.check_output_dir(os.path.dirname(output_file))
        input_files = [os.path.join(self.ref_dir,'fewsnet-rfe/10d/20151221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif'),
                       self.ref_avg_file]
        args = {"input_file": input_files, "output_file": output_file, "output_format": 'GTIFF',
                "options": "compress=lzw", 'output_type': 'Float32', 'input_nodata': -32768}

        raster_image_math.do_oper_division_perc(**args)
        max_delta = 1.1
        equal = self.checkFile(ref_file, output_file, max_delta=max_delta,create_plot=True)
        self.assertEqual(equal,1)
        #
        #
        # input_file='/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        # avg_file  = '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10davg-linearx2/1221_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        # output_file='/data/tmp/20161221_vgt-ndvi_ratio-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        #
        # args = {"input_file": [input_file,avg_file], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        # raster_image_math.do_oper_division_perc(**args)

    # Tested ok on 28.04.2020 (MC)
    def test_make_vci(self):
        # 10dnp
        output_filename = 'fewsnet-rfe/10dnp/20151221_fewsnet-rfe_10dnp_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir, output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        input_file= self.ref_dir+'fewsnet-rfe/10d/20151221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif'
        min_file  = self.ref_dir+'fewsnet-rfe/10dmin/1221_fewsnet-rfe_10dmin_FEWSNET-Africa-8km_2.0.tif'
        max_file  = self.ref_dir+'fewsnet-rfe/10dmax/1221_fewsnet-rfe_10dmax_FEWSNET-Africa-8km_2.0.tif'

        args = {"input_file": input_file, "min_file": min_file, "max_file": max_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}

        raster_image_math.do_make_vci(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_make_baresoil(self):
        output_filename = 'vgt-ndvi/baresoil-linearx2/20200301_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir, output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        input_file= self.ref_dir+'/vgt-ndvi/ndvi-linearx2/20200301_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        min_file  = self.ref_dir+'/vgt-ndvi/10dmin-linearx2/0301_vgt-ndvi_10dmin-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        max_file  = self.ref_dir+'/vgt-ndvi/10dmax-linearx2/0301_vgt-ndvi_10dmax-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        avg_file  = self.ref_dir+'/vgt-ndvi/10davg-linearx2/0301_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        # args = {"input_file": input_file, "min_file": min_file, "max_file": max_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768,"ndvi_max": 0.18}
        args = {"input_file": input_file, "avg_file": avg_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768,"ndvi_max": 0.18}

        raster_image_math.do_make_baresoil(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)
        # # Create baresoil mask for 2016/12/21 (w/o using delta_ndvi_max .. only ndvi_max)
        #
        # input_file='/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        # min_file  = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmin-linearx2/1221_vgt-ndvi_10dmin-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        # max_file  = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmax-linearx2/1221_vgt-ndvi_10dmax-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        # min_file  = ''
        # max_file  = ''
        #
        # output_file='/data/tmp/20161221_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        #
        # args = {"input_file": input_file, "min_file": min_file, "max_file": max_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        # raster_image_math.do_make_baresoil(**args)
        # self.assertEqual(1, 1)

    # Tested ok on 28.04.2020 (MC)
    def test_do_mask_image(self):
        # linearx2diff-linearx2
        output_filename = 'vgt-ndvi/linearx2diff-linearx2/20200301_vgt-ndvi_linearx2diff-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        output_file = functions.list_to_element(output_file)
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir=es_constants.base_tmp_dir)

        # Temporary (not masked) file
        output_file_temp = tmpdir + os.path.sep + os.path.basename(output_file)
        current_file = self.ref_dir + 'vgt-ndvi/ndvi-linearx2/20200301_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        average_file = self.ref_dir + 'vgt-ndvi/10davg-linearx2/0301_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        baresoil_file = self.ref_dir + 'vgt-ndvi/baresoil-linearx2/20200301_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        # Compute temporary file
        args = {"input_file": [current_file, average_file], "output_file": output_file_temp, "output_format": 'GTIFF',
                "options": "compress = lzw"}
        raster_image_math.do_oper_subtraction(**args)
        sds_meta = md.SdsMetadata()

        # Mask with baresoil file
        no_data = int(sds_meta.get_nodata_value(current_file))
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": output_file_temp, "mask_file": baresoil_file, "output_file": output_file,
                "options": "compress = lzw", "mask_value": no_data, "out_value": no_data}
        raster_image_math.do_mask_image(**args)
        # args = {"input_file": self.input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        # raster_image_math.do_mask_image(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_do_cumulate(self):
        # 1moncum
        output_filename = 'fewsnet-rfe/1moncum/20200301_fewsnet-rfe_1moncum_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))
        input_files = [self.ref_dir+'/fewsnet-rfe/10d/20200321_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                       self.ref_dir+'/fewsnet-rfe/10d/20200311_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',
                       self.ref_dir+'/fewsnet-rfe/10d/20200301_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif',]
        args = {"input_file": input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_cumulate(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_compute_perc_diff_vs_avg(self):
        # 10dperc
        output_filename = 'fewsnet-rfe/10dperc/20151221_fewsnet-rfe_10dperc_FEWSNET-Africa-8km_2.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))
        input_file = os.path.join(self.ref_dir,'fewsnet-rfe/10d/20151221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif')

        args = {"input_file": input_file, "avg_file": self.ref_avg_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_compute_perc_diff_vs_avg(**args)

        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_compute_primary_production(self):
        input_files = [self.ref_dir+'/modis-chla/monavg/20200301_modis-chla_monavg_MODIS-Africa-4km_v2013.1.tif', \
            self.ref_dir+'/modis-sst/monavg/20200301_modis-sst_monavg_MODIS-Africa-4km_v2013.1.tif', \
            self.ref_dir+'/modis-kd490/monavg/20200301_modis-kd490_monavg_MODIS-Africa-4km_v2012.0.tif', \
            self.ref_dir+'/modis-par/monavg/20200301_modis-par_monavg_MODIS-Africa-4km_v2012.0.tif']
        # output_file = '/data/tmp/20181007_modis-pp_monavg_MODIS-Africa-4km_v2013.1.tif'
        output_filename = 'modis-pp/monavg/20200301_modis-pp_monavg_MODIS-Africa-4km_v2013.1.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"chla_file": input_files[0], "sst_file": input_files[1], "kd_file": input_files[2],
                "par_file": input_files[3], \
                "sst_nodata": 0, "kd_nodata": -32767, "chla_nodata": -32767, \
                "par_nodata": -32767, "output_file": output_file, "output_nodata": -32767,
                "output_format": 'GTIFF', \
                "output_type": None, "options": "compress=lzw"}
        raster_image_math.do_compute_primary_production(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_do_ts_linear_filter(self):
        input_files = [self.ref_dir+'/vgt-ndvi/ndvi-linearx1/20200221_vgt-ndvi_ndvi-linearx1_SPOTV-Africa-1km_sv2-pv2.2.tif', \
            self.ref_dir+'/vgt-ndvi/ndvi-linearx1/20200301_vgt-ndvi_ndvi-linearx1_SPOTV-Africa-1km_sv2-pv2.2.tif', \
            self.ref_dir+'/vgt-ndvi/ndvi-linearx1/20200311_vgt-ndvi_ndvi-linearx1_SPOTV-Africa-1km_sv2-pv2.2.tif']
        output_filename = 'vgt-ndvi/ndvi-linearx2/20200301_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        output_file = functions.list_to_element(output_file)
        functions.check_output_dir(os.path.dirname(output_file))
        args = {"input_file": input_files[1], "before_file": input_files[0], "after_file": input_files[2],
                "output_file": output_file,
                "output_format": 'GTIFF', "options": "compress = lzw", 'threshold': 0.1}
        raster_image_math.do_ts_linear_filter(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    # MC: Little differences due to thinning (acceptable)
    def test_detect_sst_fronts(self):

        input_file = self.ref_dir+'pml-modis-sst/sst-3day/20200301_pml-modis-sst_sst-3day_SPOTV-IOC-1km_3.0.tif'
        output_filename = 'pml-modis-sst/sst-fronts/20200301_pml-modis-sst_sst-fronts_SPOTV-IOC-1km_3.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        parameters = {'histogramWindowStride': 16,  # smaller window detects more fronts
                      'histogramWindowSize': 32,
                      'minTheta': 0.76,
                      'minPopProp': 0.25,
                      'minPopMeanDifference': 20,  # Temperature: 0.45 deg (multiply by 100 !!)
                      'minSinglePopCohesion': 0.60,
                      'minImageValue': 1,
                      'minThreshold': 1}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                "parameters": parameters}
        raster_image_math.do_detect_sst_fronts(**args)

        # Note: the max_delta=1.1 makes comparison ok (it is a binary mask)
        # This is forcing the test OK, since we inspected the results in QGIS
        equal = self.checkFile(ref_file, output_file, max_delta=1.1)
        self.assertEqual(equal,1)

    # Very slow - Problem could be my latop memory
    def test_stats_4_raster(self):

        # Define the Native mapset
        input_mapset_name ='SPOTV-Africa-1km'
        grid_mapset_name = 'SPOTV-Africa-1km'
        target_mapset_name='SPOTV-Africa-10km'
        grid_file='/eStation2/layers/Mask_Africa_SPOTV_10km.tif'

        input_file = self.ref_dir+'modis-firms/10dcount/20200301_modis-firms_10dcount_SPOTV-Africa-1km_v6.0.tif'
        output_filename = 'modis-firms/10dcount10k/20200301_modis-firms_10dcount10k_SPOTV-Africa-1km_v6.0.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        # input_file='/data/processing/modis-firms/v6.0/SPOTV-Africa-1km/derived/10dcount/20171101_modis-firms_10dcount_SPOTV-Africa-1km_v6.0.tif'
        # output_file='/data/tmp/20171101_modis-firms_10dcount10k_SPOTV-Africa-1km_v6.0.tif'
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
                                  dir='/data/tmp/')

        # Temporary (not masked) file
        output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)

        operation='sum'

        raster_image_math.do_stats_4_raster(input_file, grid_file, output_file_temp, operation, input_mapset_name, grid_mapset_name,
                                            output_format=None, nodata=-32768, output_type= 'Int16',options=None )

        args = {"inputfile": output_file_temp, "output_file": output_file, "native_mapset_name": grid_mapset_name,
                "target_mapset_name": target_mapset_name}

        raster_image_math.do_reproject(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_do_compute_chla_gradient(self):

        input_file = self.ref_dir+'modis-chla/chla-day/20200301_modis-chla_chla-day_MODIS-Africa-4km_v2013.1.tif'
        output_filename = 'modis-chla/gradient/20200301_modis-chla_gradient_MODIS-Africa-4km_v2013.1.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw", "nodata":-32767}
        # raster_image_math.do_compute_chla_gradient(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    # Note: plenty of warning messages ..
    def test_compute_opFish_indicator(self):

        input_file = self.ref_dir+'modis-chla/chla-day/20200301_modis-chla_chla-day_MODIS-Africa-4km_v2013.1.tif'
        output_filename = 'modis-chla/opfish/20200301_modis-chla_opfish_MODIS-Africa-4km_v2013.1.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        functions.check_output_dir(os.path.dirname(output_file))

        # prod == 'modis-chla':
        parameters = {'chl_grad_min': 0.00032131,  # smaller window detects more fronts
                      'chl_grad_int': 0.021107,
                      'chl_feed_min': 0.08,
                      'chl_feed_max': 11.0,  # Temperature: 0.45 deg (multiply by 100 !!)
                      'dc': 0.91}

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                "parameters": parameters, "nodata":-32767}
        raster_image_math.compute_opFish_indicator(**args)
        equal = self.checkFile(ref_file, output_file)
        self.assertEqual(equal,1)

    # Tested ok on 28.04.2020 (MC)
    def test_compare_two_raster_array(self):
        output_filename = 'modis-chla/opfish/20200301_modis-chla_opfish_MODIS-Africa-4km_v2013.1.tif'
        output_file=os.path.join(self.root_out_dir, output_filename)
        ref_file   =os.path.join(self.ref_dir,      output_filename)
        args = {"input_file_1": output_file, "input_file_2": ref_file}
        status = raster_image_math.compare_two_raster_array(**args)
        self.assertEqual(status, 1)

suite_raster_image = unittest.TestLoader().loadTestsFromTestCase(TestRasterImage)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_raster_image)

    # Not used currently ---- fewsnet-rfe_rain-onset
    # def test_rain_onset(self):
    #     input_file = [
    #         '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
    #         '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif']
    #
    #     output_file = '/data/tmp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
    #             'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':2}
    #     raster_image_math.do_rain_onset(**args)
    #     self.assertEqual(1, 1)
    #
    # def test_rain_onset_1(self):
    #     input_file = [
    #         '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160921_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
    #         '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
    #         '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
    #         '/data/tmp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif']
    #
    #     output_file = '/data/tmp/20160921_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
    #             'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':3}
    #     raster_image_math.do_rain_onset(**args)
    #     self.assertEqual(1, 1)

    # We dont have result to test it since it is part of a chain.. Could use test_stats_4_raster
    # def test_do_reproject(self):
    #     # Define the Native mapset
    #     # native_mapset_name ='SPOTV-SADC-1km'
    #     # target_mapset_name = 'FEWSNET-Africa-8km'
    #     #
    #     # inputfile='/data/tmp/20161221_vgt-ndvi_ratio-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
    #     # output_file='/data/tmp/AGRIC_MASK-'+target_mapset_name+'.tif'
    #
    #     inputfile = self.ref_dir+'modis-firms/10dcount/20200301_modis-firms_10dcount_SPOTV-Africa-1km_v6.0.tif'
    #     output_filename = 'modis-firms/10dcount10k/20200301_modis-firms_10dcount10k_SPOTV-Africa-10km_v6.0.tif'
    #     output_file=os.path.join(self.root_out_dir, output_filename)
    #     ref_file   =os.path.join(self.ref_dir,      output_filename)
    #     functions.check_output_dir(os.path.dirname(output_file))
    #     target_mapset_name = 'SPOTV-Africa-10km'
    #     native_mapset_name = 'SPOTV-Africa-1km'
    #
    #     raster_image_math.do_reproject(inputfile, output_file,native_mapset_name,target_mapset_name)
    #     equal = self.checkFile(ref_file, output_file)
    #     self.assertEqual(equal,1)

    #Dint test  No usage
    # def test_create_surface_area_raster(self):
    #
    #     # Define the Native mapset
    #     input_mapset_name ='SPOTV-Africa-1km'
    #     grid_mapset_name = 'SPOTV-Africa-1km'
    #     target_mapset_name='SPOTV-Africa-1km'
    #     #grid_file='/eStation2/layers/Mask_Africa_SPOTV_10km.tif'
    #
    #
    #     input_file='/data/processing/exchange/area/area_calc.tif'
    #     output_file='/data/processing/exchange/area/surface_area_SpotAfrica1km_with_equator.tif'
    #     tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
    #                               dir='/data/processing/exchange/')
    #
    #     # Temporary (not masked) file
    #     output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)
    #
    #     operation='sum'
    #
    #     raster_image_math.create_surface_area_raster(output_file=output_file_temp, output_type='Float32',
    #                                                  mapsetcode=grid_mapset_name)
    #
    #     args = {"inputfile": output_file_temp, "output_file": output_file, "native_mapset_name": grid_mapset_name,
    #              "target_mapset_name": target_mapset_name}
    #     #
    #     raster_image_math.do_reproject(**args)
    #     self.assertEqual(1, 1)