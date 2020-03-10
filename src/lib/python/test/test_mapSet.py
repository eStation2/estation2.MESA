from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase

__author__ = 'tklooju'

from lib.python.mapset import *

#   TODO-M.C.: complete and re-activate all tests. Implement for the MapSet() class a 'isEqual' method.

class TestMapSet(TestCase):

    # def test_assigndb(self):
    #     my_mapset = MapSet()
    #
    # def test_assign(self):
    #     self.fail()

    def test_assign_default(self):

        my_mapset = MapSet()
        my_mapset.assign_default()
        self.assertEqual(my_mapset.size_x, 9633)
        self.assertEqual(my_mapset.size_y, 8177)

    def test_get_larger(self):

        mapsetcode = 'SPOTV-IGAD-1km'
        mapset = MapSet()
        mapset.assigndb(mapsetcode)
        larger = mapset.get_larger_mapset()

        self.assertEqual(larger,'SPOTV-Africa-1km')

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

        self.assertEqual(common['isCommon'],True)
        self.assertEqual(common['xSize'],mapset_SADC.size_x)
        self.assertEqual(common['ySize'],mapset_SADC.size_y)

        # Test wrt ECOWAS region, which is INCLUDED in mapset 1
        mapsetcode_ecow = 'SPOTV-ECOWAS-1km'
        mapset_ECOW = MapSet()
        mapset_ECOW.assigndb(mapsetcode_ecow)
        common =  mapset_Afr.compute_common_area(mapset_ECOW)

        self.assertEqual(common['isCommon'],True)
        self.assertEqual(common['xSize'],mapset_ECOW.size_x)
        self.assertEqual(common['ySize'],mapset_ECOW.size_y)

        # Test SADC wrt ECOWAS region
        common =  mapset_SADC.compute_common_area(mapset_ECOW)

        self.assertEqual(common['isCommon'],True)
        self.assertEqual(common['xSize'],1570)
        self.assertEqual(common['ySize'],225)

    def test_is_wbd(self):

        # Prepare ref mapset
        mapsetcode_1 = 'WD-GEE-ECOWAS-AVG'
        mapset_Afr = MapSet()
        mapset_Afr.assigndb(mapsetcode_1)

        self.assertEqual(mapset_Afr.is_wbd(),True)

    def test_compute_pixel_area(self):

        n_line = 1000
        n_col  = 1000
        mapsetcode = 'SPOTV-Africa-1km'

        my_mapset = MapSet()
        my_mapset.assigndb(mapsetcode)

        my_mapset.compute_pixel_area(n_line, n_col)


    def test_create_raster_surface(self):

        mapsetcode = 'CHIRP-Africa-5km'

        my_mapset = MapSet()
        my_mapset.assigndb(mapsetcode)

        my_mapset.create_raster_surface()

