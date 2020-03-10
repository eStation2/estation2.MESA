from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#   Test metadata reading/writing
#

from future import standard_library
standard_library.install_aliases()
from unittest import TestCase

__author__ = 'clerima'

from osgeo import gdal
from osgeo.gdalconst import *
from lib.python.metadata import *
import tempfile
import shutil
from config import es_constants

#input_dir = es_constants.es2globals['test_data_refs_dir']+'Metadata/'
# Put here an existing 2.0 file with correct metadata
input_dir = es_constants.es2globals['data_dir']+'/data/processing/vgt_ndvi/WGS84_Africa_1km/tif/ndv/'
file=input_dir+'20130701_vgt_ndvi_ndv_WGS84_Africa_1km.tif'
file_eStation2='/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20110111_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif'

class TestMapSet(TestCase):

    def create_temp_file(self):
        tf = tempfile.NamedTemporaryFile()
        filename = tf.name
        tf.close()
        return filename

    def test_writing_reading_an_item(self):

        my_item='Test_Metadata_Item'
        my_value='Test_Metadata_Value'

        # Create a tmp Tiff file
        #try:
        #    tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_test_writing_an_item', dir=locals.es2globals['temp_dir'])
        #except IOError:
        #    logger.error('Cannot create temporary dir ' + es_constants.es2globals['temp_dir'] + '. Exit')
        #    return 1
        #filename = tmpdir+'/temp_target.tif'

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

    def test_writing_meta_to_estation2_file(self):

        sds_meta = SdsMetadata()

        # Create a dummy output File

        sds_meta.write_to_file(file_eStation2)

        self.assertTrue(os.path.isfile(file_eStation2))

    def test_reading_nodata_value(self):

        myfile='/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20000811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'

        sds_meta = SdsMetadata()

        if os.path.exists(myfile):
            nodata=sds_meta.get_nodata_value(myfile)
            self.assertEqual(float(nodata), -32768)

        else:
            logger.info('Test file not existing: skip test')

    def test_reading_meta_items_from_file(self):

        if os.path.exists(file):
             sds_meta = SdsMetadata()
             # Read from a reference file
             sds_meta.read_from_file(file)
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

    def test_reading_meta_items_from_file(self):

        if os.path.exists(file):
             sds_meta = SdsMetadata()
             # Read from a reference file
             sds_meta.read_from_file(file)
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

    def test_assign_from_product(self):


        first_input = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/tif/ndv/19990101_vgt-ndvi_ndv_SPOTV-Africa-1km_sv2-pv2.1.tif'
        sds_meta = SdsMetadata()
        output_file='/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx1/19981221_vgt-ndvi_ndvi-linearx1_SPOTV-Africa-1km_sv2-pv2.1.tif'
        # Open and read data
        sds_meta.read_from_file(first_input)

        # Modify/Assign some to the ingested file
        sds_meta.assign_comput_time_now()
        str_date, productcode, subproductcode, mapset, version = functions.get_all_from_filename(os.path.basename(output_file))

        #productcode='vgt-ndvi'
        #subproductcode='ndvi_linearx1'
        #version='sv2-pv2.1'
        sds_meta.assign_from_product(productcode, subproductcode, version)
        sds_meta.print_out()
