import unittest

from apps.es2system.test import test_system
from apps.es2system.test import test_spirits

suite_list = []
suite_list.append(test_system.suite_system)
suite_list.append(test_spirits.suite_spirits)

suite_combo_es2system = unittest.TestSuite(suite_list)
unittest.TextTestRunner(verbosity=2).run(suite_combo_es2system)