#
#   Test metadata reading/writing
#
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library

standard_library.install_aliases()

import unittest
from osgeo.gdalconst import *
# from osgeo import gdal
import shutil
import tempfile

from lib.python.metadata import *
from config import es_constants


def create_temp_file(gtiff=True):
    tf = tempfile.NamedTemporaryFile()
    filename = tf.name
    tf.close()
    if gtiff:
        logger.info('Create a file %s: ' % filename)
        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(filename, 1, 1, 1, 1)
        # Close the file
        out_ds = None
        gtiff_driver = None
    return filename


class TestMetaData(unittest.TestCase):

    def setUp(self):
        self.testdatadir = es_constants.es2globals['test_data_dir']
        self.testresultdir = es_constants.es2globals['base_tmp_dir'] + os.path.sep + 'testresults'
        if not os.path.isdir(self.testresultdir):
            os.mkdir(self.testresultdir)
            os.chmod(self.testresultdir, 0o755)
        else:
            shutil.rmtree(self.testresultdir)
            os.mkdir(self.testresultdir)
            os.chmod(self.testresultdir, 0o755)

        self.testfile_fewsnet = self.testdatadir + os.path.sep + 'tif/20110111_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif '
        self.testfile_ndvi = self.testdatadir + os.path.sep + 'tif/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

    def test_assign_compute_time_now(self):
        sds_meta = SdsMetadata()
        # Create a dummy output File
        filename = create_temp_file()
        sds_meta.assign_compute_time_now()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value1 = sds_meta.get_item('eStation2_comp_time')
        value2 = sds_meta_tmp.get_item('eStation2_comp_time')
        self.assertEqual(value1, value2)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_date(self):
        sds_meta = SdsMetadata()
        # Create a dummy output File
        filename = create_temp_file()
        sds_meta.assign_date('20200120')
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value1 = sds_meta.get_item('eStation2_date')
        value2 = sds_meta_tmp.get_item('eStation2_date')
        self.assertEqual(value2, value2)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_es2_version(self):
        sds_meta = SdsMetadata()
        # Create a dummy output File
        filename = create_temp_file()
        sds_meta.assign_es2_version()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_es2_version')
        self.assertEqual(value, es_constants.es2_sw_version)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_from_product(self):
        sds_meta = SdsMetadata()
        sds_meta.read_from_file(self.testfile_ndvi)
        sds_meta.assign_compute_time_now()
        str_date, productcode, subproductcode, mapset, version = functions.get_all_from_filename(
            os.path.basename(self.testfile_ndvi))

        sds_meta_from_product = SdsMetadata()
        sds_meta_from_product.assign_from_product(productcode, subproductcode, version)
        sds_meta_from_product.print_out()
        self.assertEqual(sds_meta.get_item('eStation2_product'), sds_meta_from_product.get_item('eStation2_product'))

    def test_assign_input_files(self):
        sds_meta_ndvi = SdsMetadata()
        sds_meta_ndvi.read_from_file(self.testfile_ndvi)
        input_files = sds_meta_ndvi.get_item('eStation2_input_files')
        sds_meta = SdsMetadata()
        sds_meta.assign_input_files(input_files)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value1 = sds_meta.get_item('eStation2_input_files')
        value2 = sds_meta_tmp.get_item('eStation2_input_files')
        self.assertEqual(value1, value2)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_mapset(self):
        sds_meta_ndvi = SdsMetadata()
        sds_meta_ndvi.read_from_file(self.testfile_ndvi)
        mapsetcode = sds_meta_ndvi.get_item('eStation2_mapset')
        sds_meta = SdsMetadata()
        sds_meta.assign_mapset(mapsetcode)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_mapset')
        self.assertEqual(value, mapsetcode)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_nodata(self):
        sds_meta_ndvi = SdsMetadata()
        sds_meta_ndvi.read_from_file(self.testfile_ndvi)
        nodatavalue = sds_meta_ndvi.get_item('eStation2_nodata')
        sds_meta = SdsMetadata()
        sds_meta.assign_nodata(nodatavalue)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_nodata')
        self.assertEqual(value, nodatavalue)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_parameters(self):
        parameters = {'a': 12, 'b': 0.75}
        sds_meta = SdsMetadata()
        sds_meta.assign_parameters(parameters)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_parameters')
        self.assertEqual(value, 'a=12; b=0.75; ')
        self.assertTrue(os.path.isfile(filename))

    def test_assign_product_elements(self):
        productcode = 'test-productcode'
        subproductcode = 'test-productcode'
        version = None
        sds_meta = SdsMetadata()
        sds_meta.assign_product_elements(productcode, subproductcode, version)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value1 = sds_meta_tmp.get_item('eStation2_product')
        value2 = sds_meta_tmp.get_item('eStation2_subProduct')
        value3 = sds_meta_tmp.get_item('eStation2_product_version')
        self.assertEqual(value1, productcode)
        self.assertEqual(value2, subproductcode)
        self.assertEqual(value3, 'undefined')
        self.assertTrue(os.path.isfile(filename))

    def test_assign_scaling(self):
        scaling_factor = 1
        scaling_offset = 0
        nodata = -39999
        unit = 'mm'
        sds_meta = SdsMetadata()
        sds_meta.assign_scaling(scaling_factor, scaling_offset, nodata, unit)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value1 = sds_meta_tmp.get_item('eStation2_scaling_factor')
        value2 = sds_meta_tmp.get_item('eStation2_scaling_offset')
        value3 = sds_meta_tmp.get_item('eStation2_nodata')
        value4 = sds_meta_tmp.get_item('eStation2_unit')
        self.assertEqual(value1, str(scaling_factor))
        self.assertEqual(value2, str(scaling_offset))
        self.assertEqual(value3, str(nodata))
        self.assertEqual(value4, unit)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_scl_factor(self):
        scaling_factor = 99
        sds_meta = SdsMetadata()
        sds_meta.assign_scl_factor(scaling_factor)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_scaling_factor')
        self.assertEqual(value, str(scaling_factor))
        self.assertTrue(os.path.isfile(filename))

    def test_assign_single_paramater(self):
        parameter_key = 'testparameter'
        parameter_value = 'testvalue'
        sds_meta = SdsMetadata()
        sds_meta.assign_single_paramater(parameter_key, parameter_value)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        # The new parameter does not exist in list sds_metadata so is not read by read_from_file
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        gdalfile = gdal.Open(filename)
        value = gdalfile.GetMetadataItem(parameter_key)
        sds_meta_tmp.sds_metadata[parameter_key] = value
        value = sds_meta_tmp.get_item(parameter_key)
        self.assertEqual(value, parameter_value)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_subdir(self):
        subdirectory = self.testdatadir
        sds_meta = SdsMetadata()
        sds_meta.assign_subdir(subdirectory)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_subdir')
        self.assertEqual(value, subdirectory)
        self.assertTrue(os.path.isfile(filename))

    def test_assign_subdir_from_fullpath(self):
        fullpath = '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-IGAD-1km/tif/ndvi-linearx2/dummyfile.tif'
        subdirectory = 'vgt-ndvi/sv2-pv2.2/SPOTV-IGAD-1km/tif/ndvi-linearx2/'
        sds_meta = SdsMetadata()
        sds_meta.assign_subdir_from_fullpath(fullpath)
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        sds_meta_tmp = SdsMetadata()
        sds_meta_tmp.read_from_file(filename)
        value = sds_meta_tmp.get_item('eStation2_subdir')
        self.assertEqual(value, subdirectory)
        self.assertTrue(os.path.isfile(filename))

    def test_get_item(self):
        if os.path.exists(self.testfile_fewsnet):
            sds_meta = SdsMetadata()
            # Read from a reference file
            sds_meta.read_from_file(self.testfile_fewsnet)
            sds_meta.print_out()

            value = sds_meta.get_item('eStation2_mapset')
            self.assertEqual(value, 'FEWSNET_Africa_8km')

            value = sds_meta.get_item('eStation2_nodata')
            self.assertEqual(value, '-32768')

            value = sds_meta.get_item('eStation2_es2_version')
            self.assertEqual(value, 'my_eStation2_sw_release')

            value = sds_meta.get_item('eStation2_conversion')
            self.assertEqual(value, 'Phys = DN * scaling_factor + scaling_offset')

            value = sds_meta.get_item('eStation2_input_files')
            self.assertEqual(value, '/data/Archives/FewsNET/a14061rb.zip;')

            value = sds_meta.get_item('eStation2_subProduct')
            self.assertEqual(value, 'rfe')

            value = sds_meta.get_item('eStation2_product')
            self.assertEqual(value, 'fewsnet_rfe')

            value = sds_meta.get_item('eStation2_scaling_factor')
            self.assertEqual(value, '1.0')

            value = sds_meta.get_item('eStation2_unit')
            self.assertEqual(value, None)
        else:
            logger.info('Test file not existing: skip test')

    def test_get_nodata_value(self):
        sds_meta = SdsMetadata()
        if os.path.exists(self.testfile_ndvi):
            nodata = sds_meta.get_nodata_value(self.testfile_ndvi)
            self.assertEqual(float(nodata), -32768)
        else:
            logger.info('Test file not existing: skip test')

    def test_get_scaling_values(self):
        sds_meta = SdsMetadata()
        if os.path.exists(self.testfile_ndvi):
            nodata = sds_meta.get_nodata_value(self.testfile_ndvi)
            self.assertEqual(float(nodata), -32768)
        else:
            logger.info('Test file not existing: skip test')

    def test_get_target_filepath(self):
        sds_meta = SdsMetadata()
        if os.path.exists(self.testfile_ndvi):
            target_filepath = sds_meta.get_target_filepath(self.testfile_ndvi)
            self.assertEqual(target_filepath, '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi'
                                              '-linearx2/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2'
                                              '.tif')
        else:
            logger.info('Test file not existing: skip test')

    def test_merge_input_file_lists(self):
        old_list = 'file1.tif;file2.tif;file3.tif;file4.tif'
        input_files = ['file1.tif', 'file2.tif', 'file5.tif', 'file6.tif']
        sds_meta = SdsMetadata()
        merged_list = sds_meta.merge_input_file_lists(old_list, input_files)
        self.assertEqual(merged_list, ['file1.tif', 'file2.tif', 'file3.tif', 'file4.tif', 'file5.tif', 'file6.tif'])

    def test_read_from_ds(self):
        sds_meta = SdsMetadata()
        # Dummy output File
        gtiff_file = create_temp_file()
        sds_meta.write_to_ds(gtiff_file)

        sds_meta_read = SdsMetadata()
        sds_meta_read.read_from_ds(gtiff_file)
        value1 = sds_meta.get_item('eStation2_product')
        value2 = sds_meta_read.get_item('eStation2_product')
        self.assertEqual(value1, value2)

    def test_read_from_file(self):
        if os.path.exists(self.testfile_fewsnet):
            sds_meta = SdsMetadata()
            # Read from a reference file
            sds_meta.read_from_file(self.testfile_fewsnet)
            sds_meta.print_out()

            value = sds_meta.get_item('eStation2_mapset')
            self.assertEqual(value, 'FEWSNET_Africa_8km')

            value = sds_meta.get_item('eStation2_nodata')
            self.assertEqual(value, '-32768')

            value = sds_meta.get_item('eStation2_es2_version')
            self.assertEqual(value, 'my_eStation2_sw_release')

            value = sds_meta.get_item('eStation2_conversion')
            self.assertEqual(value, 'Phys = DN * scaling_factor + scaling_offset')

            value = sds_meta.get_item('eStation2_input_files')
            self.assertEqual(value, '/data/Archives/FewsNET/a14061rb.zip;')

            value = sds_meta.get_item('eStation2_subProduct')
            self.assertEqual(value, 'rfe')

            value = sds_meta.get_item('eStation2_product')
            self.assertEqual(value, 'fewsnet_rfe')

            value = sds_meta.get_item('eStation2_scaling_factor')
            self.assertEqual(value, '1.0')

            value = sds_meta.get_item('eStation2_unit')
            self.assertEqual(value, None)

        else:
            logger.info('Test file not existing: skip test')

    def test_write_to_ds(self):
        sds_meta = SdsMetadata()
        # Dummy output File
        gtiff_file = create_temp_file()
        sds_meta.write_to_ds(gtiff_file)
        self.assertTrue(os.path.isfile(gtiff_file))

    def test_write_to_file(self):
        sds_meta = SdsMetadata()
        filename = create_temp_file()
        sds_meta.write_to_file(filename)
        self.assertTrue(os.path.isfile(filename))

    def test_writing_reading_an_item(self):
        my_item = 'Test_Metadata_Item'
        my_value = 'Test_Metadata_Value'

        filename = create_temp_file()

        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(filename, 1, 1, 1, 1)

        out_ds.SetMetadataItem(my_item, my_value)

        # Close the file and remove temp dir
        out_ds = None

        # Open the file for reading
        in_ds = gdal.Open(filename, GA_ReadOnly)
        read_value = in_ds.GetMetadataItem(my_item)

        self.assertEqual(my_value, read_value)

    def test_get_gdalinfo(self):
        my_file = '/data/test_data/refs_output/wsi-hp/pasture/20200221_wsi-hp_pasture_SPOTV-Africa-1km_V1.0.tif'
        gdal_info = GdalInfo()
        status = gdal_info.get_gdalinfo(my_file, print_out=True)
        self.assertEqual(status, 1)

    def test_compare_gdalinfo(self):
        my_file1 = '/data/test_data/refs_output/wsi-hp/pasture/20200221_wsi-hp_pasture_SPOTV-Africa-1km_V1.0.tif'
        my_file2 = '/data/test_data/refs_output/wsi-hp/pasture/20200221_wsi-hp_pasture_SPOTV-Africa-1km_V1.0.tif'
        gdal_info1 = GdalInfo()
        gdal_info2 = GdalInfo()
        status = gdal_info1.get_gdalinfo(my_file1, print_out=True)
        status = gdal_info2.get_gdalinfo(my_file2, print_out=True)
        equal = gdal_info1.compare_gdalinfo(gdal_info2)

        self.assertEqual(equal, 1)


suite_metadata = unittest.TestLoader().loadTestsFromTestCase(TestMetaData)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_metadata)
