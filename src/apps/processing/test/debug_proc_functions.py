from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici"


from unittest import TestCase
import os
import glob
from lib.python import es_logging as log
from lib.python import functions
from config import es_constants
from lib.python.image_proc import raster_image_math
from lib.python import metadata as md
# Trivial change
logger = log.my_logger(__name__)

from apps.processing import proc_functions

class TestProcFunctions(TestCase):

    def setUp(self):
        root_test_dir=es_constants.es2globals['test_data_dir']
        self.test_procfunc_dir=root_test_dir #os.path.join(root_test_dir,'native')
        self.proc_dir_bck = es_constants.processing_dir
        es_constants.processing_dir = es_constants.es2globals['base_tmp_dir']+os.path.sep
        self.ingest_out_dir = es_constants.processing_dir
        self.ref_out_dir = root_test_dir #os.path.join(root_test_dir,'refs_output')

    def tearDown(self):
        es_constants.processing_dir = self.proc_dir_bck

    # def checkFile(self, productcode='', subproductcode='', version='', mapsetcode='', date=''):
    #     # Given the all files keys (date, prod, sprod, ...) finds out:
    #     # -> the product just ingested in the tmp_dir (see setUp)
    #     # -> the product in refs_output
    #     # Assess if the products are equal/equivalent
    #
    #     result = 0
    #     filename = functions.set_path_filename(date,productcode, subproductcode, mapsetcode, version, '.tif')
    #     sub_directory= functions.set_path_sub_directory(productcode,subproductcode,'Ingest',version,mapsetcode)
    #
    #     ref_file = glob.glob(self.ref_out_dir+'**/*/*/'+filename, recursive=True)
    #     if not len(ref_file)>0: #os.path.isfile(ref_file[0]):
    #         print("Error reference file does not exist: "+filename)
    #         return result
    #     newly_computed_file = glob.glob(self.ingest_out_dir+sub_directory+filename,recursive=True)
    #     if not len(newly_computed_file)>0: #os.path.isfile(newly_computed_file[0]):
    #         print("Error reference file does not exist: "+filename)
    #         return result
    #
    #     # Compare the files by using gdal_info objects
    #     if len(ref_file)>0 and len(newly_computed_file)>0 and os.path.exists(ref_file[0]) and os.path.exists(newly_computed_file[0]):
    #         gdal_info_ref = md.GdalInfo()
    #         gdal_info_ref.get_gdalinfo(ref_file[0])
    #         gdal_info_new = md.GdalInfo()
    #         gdal_info_new.get_gdalinfo(newly_computed_file[0])
    #         equal = gdal_info_new.compare_gdalinfo(gdal_info_ref)
    #
    #         if not equal:
    #             print("Warning: the files metadata are different")
    #         # Check the raster array compare
    #         array_equal = raster_image_math.compare_two_raster_array(ref_file[0], newly_computed_file[0])
    #         if not array_equal:
    #             print("Warning: the files contents are different")
    #
    #         if array_equal is True:
    #             result = 1
    #
    #     return result

    def test_get_list_dates_for_dataset(self):
        productcode = 'lsasaf-et'
        productversion = 'undefined'
        subproductcode = '10d30min'
        input_file = self.test_procfunc_dir+os.path.sep+productcode+os.path.sep+subproductcode+os.path.sep+'202004010000_lsasaf-et_10d30min_MSG-satellite-3km_undefined.tif'
        start_date = 202004010000
        end_date = 202004010120
        proc_functions.get_list_dates_for_dataset(productcode, subproductcode, productversion,start_date, end_date)

        self.assertEqual(1, 1)


    # def test_reproject_output(self):
    #     productcode = 'lsasaf-et'
    #     subproductcode = '10d30min'
    #     input_file = self.test_procfunc_dir+os.path.sep+productcode+os.path.sep+subproductcode+os.path.sep+'202004010000_lsasaf-et_10d30min_MSG-satellite-3km_undefined.tif'
    #
    #     target_mapset_id = 'SPOTV-ECOWAS-1km'
    #     orig_mapset_id = 'MSG-satellite-3km'
    #     # orig_mapset_id = 'FEWSNET-Africa-8km'
    #
    #     proc_functions.reproject_output(input_file, orig_mapset_id, target_mapset_id, logger)
    #
    #     self.assertEqual(1, 1)

    def test_remove_old_files(self):

        productcode='lsasaf-lst'
        subprod='lst'
        version='undefined'
        type='Ingest'
        nmonths=6
        mapset = 'MSG-satellite-3km'

        proc_functions.remove_old_files(productcode, subprod, version, mapset, type, nmonths)

        self.assertEqual(1, 1)


    def Test_clean_corrupted_files(self):
        productcode = 'lsasaf-lst'
        version = 'undefined'

        subprod = '10dmax'
        type = 'Derived'
        mapset = 'MSG-satellite-3km'
        mapset = 'SPOTV-Africa-1km'

        # Define the subdir to start from
        prod_subdir = functions.set_path_sub_directory(productcode, subprod, type, version, mapset)
        prod_dir = es_constants.es2globals['processing_dir'] + os.path.sep + prod_subdir

        proc_functions.clean_corrupted_files(prod_dir,dry_run=False)

        self.assertEqual(1, 1)
