# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in productmanagement
#   author:  Marco Clerici clerici.marco@gmail.com
#   date:    24.02.2020
#
import unittest
# from apps.acquisition.test import test_all_acquisition
from apps.analysis.test import test_all_analysis
from apps.productmanagement.test import test_all_productmanagement
from database.test import test_all_database
from lib.python.test import test_all_python

suite_list = []
# suite_list.append(test_all_acquisition.suite_combo_acquisition)
suite_list.append(test_all_analysis.suite_combo_analysis)
suite_list.append(test_all_productmanagement.suite_combo_pm)
suite_list.append(test_all_database.suite_combo_database)
suite_list.append(test_all_python.suite_combo_python)

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)