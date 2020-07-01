from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import shutil
import unittest
import os

from lib.python.mapset import *
from config import es_constants


#   TODO-M.C.: complete and re-activate all tests. Implement for the MapSet() class a 'isEqual' method.
class TestMapSet(unittest.TestCase):

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

    def test_assign(self):
        mapsetcode = 'SPOTV-Africa-1km'
        my_mapset_from_db = MapSet()
        my_mapset_from_db.assigndb(mapsetcode)
        my_mapset_assign = MapSet()
        my_mapset_assign.assign(my_mapset_from_db.spatial_ref_wkt,
                                my_mapset_from_db.geo_transform,
                                my_mapset_from_db.size_x,
                                my_mapset_from_db.size_y,
                                my_mapset_from_db.short_name)
        self.assertEqual(my_mapset_assign.spatial_ref_wkt, my_mapset_from_db.spatial_ref_wkt)
        self.assertEqual(my_mapset_assign.geo_transform, my_mapset_from_db.geo_transform)
        self.assertEqual(my_mapset_assign.size_x, my_mapset_from_db.size_x)
        self.assertEqual(my_mapset_assign.size_y, my_mapset_from_db.size_y)
        self.assertEqual(my_mapset_assign.short_name, my_mapset_from_db.short_name)

    def test_assign_default(self):
        my_mapset = MapSet()
        my_mapset.assign_default()
        self.assertEqual(my_mapset.size_x, 9633)
        self.assertEqual(my_mapset.size_y, 8177)

    def test_assigndb(self):
        mapsetcode = 'SPOTV-Africa-1km'
        my_mapset = MapSet()
        my_mapset.assigndb(mapsetcode)
        self.assertEqual(my_mapset.short_name, mapsetcode)
        self.assertEqual(my_mapset.size_x, 9633)
        self.assertEqual(my_mapset.size_y, 8177)

    def test_compute_common_area(self):
        # Prepare ref mapset
        mapsetcode_afr = 'SPOTV-Africa-1km'
        mapset_Afr = MapSet()
        mapset_Afr.assigndb(mapsetcode_afr)

        # Test wrt SADC region, which is INCLUDED in mapset 1
        mapsetcode_sadc = 'SPOTV-SADC-1km'
        mapset_SADC = MapSet()
        mapset_SADC.assigndb(mapsetcode_sadc)
        common = mapset_Afr.compute_common_area(mapset_SADC)

        self.assertEqual(common['isCommon'], True)
        self.assertEqual(common['xSize'], mapset_SADC.size_x)
        self.assertEqual(common['ySize'], mapset_SADC.size_y)

        # Test wrt ECOWAS region, which is INCLUDED in mapset 1
        mapsetcode_ecow = 'SPOTV-ECOWAS-1km'
        mapset_ECOW = MapSet()
        mapset_ECOW.assigndb(mapsetcode_ecow)
        common = mapset_Afr.compute_common_area(mapset_ECOW)

        self.assertEqual(common['isCommon'], True)
        self.assertEqual(common['xSize'], mapset_ECOW.size_x)
        self.assertEqual(common['ySize'], mapset_ECOW.size_y)

        # Test SADC wrt ECOWAS region
        common = mapset_SADC.compute_common_area(mapset_ECOW)

        self.assertEqual(common['isCommon'], True)
        self.assertEqual(common['xSize'], 1569)
        self.assertEqual(common['ySize'], 225)

    def test_compute_pixel_area(self):
        n_line = 1000
        n_col = 1000
        mapsetcode = 'SPOTV-Africa-1km'

        my_mapset = MapSet()
        my_mapset.assigndb(mapsetcode)

        my_mapset.compute_pixel_area(n_line, n_col)
        self.assertEqual(my_mapset.pixel_area, 939119.6688635349)

    # def test_create_raster_surface(self):
    #     # Todo: Remove method? Method is not used anywhere in the code!
    #     mapsetcode = 'MODIS-IOC2-4km'  # 'CHIRP-Africa-5km'
    #     filename = self.testresultdir + os.path.sep + 'pixelsize.tif'
    #     my_mapset = MapSet()
    #     my_mapset.assigndb(mapsetcode)
    #     my_mapset.create_raster_surface(filename=filename)
    #     self.assertTrue(os.path.isfile(filename))

    def test_get_larger_mapset(self):
        mapsetcode = 'SPOTV-IGAD-1km'
        mapset = MapSet()
        mapset.assigndb(mapsetcode)
        larger = mapset.get_larger_mapset()
        self.assertEqual(larger, 'SPOTV-Africa-1km')

    def test_is_wbd(self):
        # Prepare ref mapset
        mapsetcode = 'WD-GEE-ECOWAS-AVG'
        mapset = MapSet()
        mapset.assigndb(mapsetcode)
        self.assertEqual(mapset.is_wbd(), True)

    def test_validate(self):
        # Prepare ref mapset
        mapsetcode = 'SPOTV-IGAD-1km'
        mapset = MapSet()
        mapset.assigndb(mapsetcode)
        result = mapset.validate()
        self.assertEqual(result, 0)


suite_mapset = unittest.TestLoader().loadTestsFromTestCase(TestMapSet)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_mapset)
