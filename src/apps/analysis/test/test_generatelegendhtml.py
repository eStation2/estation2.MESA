from __future__ import absolute_import

import unittest

from apps.analysis.generateLegendHTML import generateLegendHTML


class TestGenerateLegendHTML(unittest.TestCase):

    def test_generatelegendhtml(self):
        legend_id = 1
        result = generateLegendHTML(legend_id)
        self.assertEqual(result.__len__(), 2)


suite_generatelegendhtml = unittest.TestLoader().loadTestsFromTestCase(TestGenerateLegendHTML)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_generatelegendhtml)