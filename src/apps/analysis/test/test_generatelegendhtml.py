from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library

import unittest

from apps.analysis.generateLegendHTML import generateLegendHTML

standard_library.install_aliases()


class TestGenerateLegendHTML(unittest.TestCase):

    def test_generatelegendhtml(self):
        legend_id = 1
        result = generateLegendHTML(legend_id)
        self.assertEqual(result.__len__(), 2)


suite_generatelegendhtml = unittest.TestLoader().loadTestsFromTestCase(TestGenerateLegendHTML)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_generatelegendhtml)