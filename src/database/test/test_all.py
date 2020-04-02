# -*- coding: utf-8 -*-

#
#   purpose: Call all test functions in database
#   author:  Jurriaan van 't Klooster jurvtk@gmail.com
#   date:    31.03.2020
#
import unittest
from database.test import test_connectdb
from database.test import test_querydb
from database.test import test_crud

suite_list = [test_connectdb.suite_connectdb, test_querydb.suite_querydb, test_crud.suite_crud]

suite_combo = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo)
