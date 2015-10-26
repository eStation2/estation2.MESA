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

    # def test_assign_ecowas(self):
    #     self.fail()
    #
    # def test_assign_ioc_pml(self):
    #     self.fail()
    #
    # def test_assign_vgt4africa(self):
    #     self.fail()
    #
    # def test_assign_vgt4africa_500m(self):
    #     self.fail()
    #
    # def test_assign_msg_disk(self):
    #     self.fail()
    #
    # def test_assign_fewsnet_africa(self):
    #     self.fail()
    #
    # def test_assign_tamsat_africa(self):
    #     self.fail()
    #
    # def test_assign_modis_global(self):
    #     self.fail()
    #
    # def test_print_out(self):
    #     self.fail()
    #
    # def test_validate(self):
    #     self.fail()