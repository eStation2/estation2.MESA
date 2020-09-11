#
#   Test metadata reading/writing
#

from unittest import TestCase

__author__ = 'clerima'

from osgeo import gdal
from osgeo.gdalconst import *
from lib.python.metadata import *
import tempfile
import shutil
from config import es_constants


class TestMetaData(TestCase):

    # Put here an existing 2.0 file with correct metadata - nodata = -32768
    root_test_dir = es_constants.es2globals['test_data_dir']
    test_file = root_test_dir + os.path.sep + 'tamsat-rfe/10d/20200121_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'

    def create_temp_file(self):
        tf = tempfile.NamedTemporaryFile()
        filename = tf.name
        tf.close()
        return filename

    def test_writing_reading_an_item(self):

        my_item='Test_Metadata_Item'
        my_value='Test_Metadata_Value'

        filename = self.create_temp_file()

        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(filename, 1, 1, 1, 1)

        out_ds.SetMetadataItem(my_item, my_value)

        # Close the file and remove temp dir
        out_ds = None

        # Open the file for reading
        in_ds = gdal.Open(filename, GA_ReadOnly)
        read_value=in_ds.GetMetadataItem(my_item)

        self.assertEqual(my_value, read_value)

    def test_writing_meta_to_new_file(self):

        sds_meta = SdsMetadata()

        # Dummy output File
        filename = self.create_temp_file()
        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(filename, 1, 1, 1, 1)

        sds_meta.write_to_ds(out_ds)

        # Close the file
        out_ds = None
        gtiff_driver = None

        self.assertTrue(os.path.isfile(filename))

    def test_writing_meta_to_existing_file(self):

        sds_meta = SdsMetadata()

        # Create a dummy output File
        filename = self.create_temp_file()
        logger.info('Create a file %s: ' % filename)

        gtiff_driver = gdal.GetDriverByName('GTiff')
        out_ds = gtiff_driver.Create(filename, 1, 1, 1, 1)

        # Close the file
        out_ds = None
        gtiff_driver = None

        sds_meta.write_to_file(filename)

        self.assertTrue(os.path.isfile(filename))

    def test_reading_nodata_value(self):

        sds_meta = SdsMetadata()

        if os.path.exists(self.test_file):
            nodata=sds_meta.get_nodata_value(self.test_file)
            self.assertEqual(float(nodata), -32768)

        else:
            logger.info('Test file not existing: skip test')

    def test_reading_meta_items_from_file(self):

        if os.path.exists(self.test_file):
             sds_meta = SdsMetadata()
             # Read from a reference file
             sds_meta.read_from_file(self.test_file)
             sds_meta.print_out()

             value = sds_meta.get_item('eStation2_mapset')
             self.assertEqual(value, 'TAMSAT-Africa-4km')

             value = sds_meta.get_item('eStation2_nodata')
             self.assertEqual(value, '-32768')

             value = sds_meta.get_item('eStation2_conversion')
             self.assertEqual(value, 'Phys = DN * scaling_factor + scaling_offset')

             value = sds_meta.get_item('eStation2_input_files')
             self.assertEqual(value, 'rfe2020_01-dk3.v3.nc;')

             value = sds_meta.get_item('eStation2_subProduct')
             self.assertEqual(value, '10d')

             value = sds_meta.get_item('eStation2_product')
             self.assertEqual(value, 'tamsat-rfe')

             value = sds_meta.get_item('eStation2_scaling_factor')
             self.assertEqual(value, '1.0')

             value = sds_meta.get_item('eStation2_unit')
             self.assertEqual(value, 'mm')

        else:
            logger.info('Test file not existing: skip test')

