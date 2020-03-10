from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase

__author__ = 'clerima'

import os
from lib.python import functions
sep=os.path.sep

class TestFunctionsPath(TestCase):

    #   -----------------------------------------------------------------------------------
    #   Extract info from dir/filename/fullpath


    def test_get_all_from_filename(self):

        my_full_path = '20151001_lsasaf-et_10daycum_SPOTV-CEMAC-1km_undefined.tif'
        my_date, my_product_code, my_sub_product_code, my_mapset , my_version= functions.get_all_from_filename(my_full_path)

        print((my_date, my_product_code, my_sub_product_code, my_mapset , my_version))

