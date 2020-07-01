# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in productmanagement
#   author:  Marco Clerici clerici.marco@gmail.com
#   date:    24.02.2020
#
import unittest
from lib.python.test import test_functions
from lib.python.test import test_metadata
from lib.python.test import test_mapset

suite_list = []
suite_list.append(test_functions.suite_functions)
suite_list.append(test_metadata.suite_metadata)
suite_list.append(test_mapset.suite_mapset)

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)