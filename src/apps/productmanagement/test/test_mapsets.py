# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:     27.10.2014
#

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from future import standard_library

import unittest
from ..mapsets import Mapset
from ..exceptions import NoMapsetFound

from database import querydb
from database import connectdb

standard_library.install_aliases()


class TestMapsets(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB().db)

    def test_mapset_not_existent(self):
        kwargs = {'mapset_code': "---mapset---"}
        self.assertRaisesRegex(NoMapsetFound, "(?i).*found.*mapset.*", Mapset, **kwargs)

    def test_mapset(self):
        kwargs = {'mapset_code': "SPOTV-Africa-1km"}
        mapset = Mapset(**kwargs)
        self.assertIsInstance(mapset, Mapset)


suite_mapsets = unittest.TestLoader().loadTestsFromTestCase(TestMapsets)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_mapsets)
