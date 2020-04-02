# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in database
#   author:  Jurriaan van 't Klooster jurvtk@gmail.com
#   date:    31.03.2020
#
import unittest
from apps.analysis.test import test_gettimeseries
from apps.analysis.test import test_generatelegendhtml

suite_list = [test_gettimeseries.suite_gettimeseries, test_generatelegendhtml.suite_generatelegendhtml]

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)
