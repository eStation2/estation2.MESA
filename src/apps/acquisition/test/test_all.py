# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in productmanagement
#   author:  Marco Clerici clerici.marco@gmail.com
#   date:    24.02.2020
#
import unittest
from apps.acquisition.test import test_ingestion
from apps.acquisition.test import test_get_eumetcast
from apps.acquisition.test import test_get_internet

suite_list = []
suite_list.append(test_ingestion.suite_ingestion_fast)
suite_list.append(test_get_eumetcast.suite_get_eumetcast)
suite_list.append(test_get_internet.suite_get_internet)

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)