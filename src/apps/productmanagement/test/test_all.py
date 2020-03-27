# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in productmanagement
#   author:  Marco Clerici clerici.marco@gmail.com
#   date:    24.02.2020
#
import unittest
from apps.productmanagement.test import test_helpers
from apps.productmanagement.test import test_frequency
from apps.productmanagement.test import test_datasets
from apps.productmanagement.test import test_mapsets
from apps.productmanagement.test import test_products
from apps.productmanagement.test import test_requests

suite_list = []
suite_list.append(test_helpers.suite_helpers)
suite_list.append(test_frequency.suite_frequency)
suite_list.append(test_datasets.suite_datasets)
suite_list.append(test_mapsets.suite_mapsets)
suite_list.append(test_products.suite_products)
suite_list.append(test_requests.suite_requests)

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)