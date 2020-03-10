
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from future import standard_library
standard_library.install_aliases()
import unittest
from datetime import date
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product
from database import querydb
from lib.python import functions

class TestAnalysisFunctionality(unittest.TestCase):

    def test_get_years(self):
        # productcode="fewsnet-rfe"
        # subproductcode="10d"
        # version="2.0"
        # mapsetcode="FEWSNET-Africa-8km"
        productcode = "vgt-ndvi"
        subproductcode = "ndv"
        version = "spot-v1"
        mapsetcode = "SPOTV-Africa-1km"

        p = Product(product_code=productcode, version=version)
        dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)
        dataset.get_filenames()
        all_present_product_dates = dataset.get_dates()
        print (all_present_product_dates)
        distinctyears = []
        for product_date in all_present_product_dates:
            if product_date.year not in distinctyears:
                distinctyears.append(product_date.year)
        print (distinctyears)

        self.assertEquals(True, True)




