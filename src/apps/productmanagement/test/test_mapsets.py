# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:     27.10.2014
#

from __future__ import absolute_import

import unittest
import sys
from apps.productmanagement.mapsets import Mapset
from apps.productmanagement.exceptions import NoMapsetFound

from database import querydb
from database import connectdb
version = sys.version_info[0]

class TestMapsets(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB().db)

    def test_mapset_not_existent(self):
        kwargs = {'mapset_code': "---mapset---"}
        # ES2-596: 'assertRaisesRegex' not in python 2.7
        if version == 2:
            self.assertRaisesRegexp(NoMapsetFound, "(?i).*found.*mapset.*", Mapset, **kwargs)

        if version == 3:
            self.assertRaisesRegex(NoMapsetFound, "(?i).*found.*mapset.*", Mapset, **kwargs)

    def test_mapset(self):
        kwargs = {'mapset_code': "SPOTV-Africa-1km"}
        mapset = Mapset(**kwargs)
        self.assertIsInstance(mapset, Mapset)


suite_mapsets = unittest.TestLoader().loadTestsFromTestCase(TestMapsets)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_mapsets)