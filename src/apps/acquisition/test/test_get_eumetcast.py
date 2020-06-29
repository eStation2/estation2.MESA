from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import str
import unittest
import pycurl
import io
import io
from apps.acquisition.get_eumetcast import *
from database import querydb
import glob
#
class TestGetEumetcast(unittest.TestCase):

    # Check the eumetcast dir exists, is accessible and not empty
    def test_GetEumetcast_dir(self):

        error_in_reading_vars = False
        try:
            input_dir = es_constants.eumetcast_files_dir
            output_dir = es_constants.get_eumetcast_output_dir
            user_def_sleep = es_constants.get_eumetcast_sleep_time_sec
        except:
            error_in_reading_vars = True

        dir_exists = os.path.exists(input_dir)
        list_files = glob.glob(input_dir+'*')
        files_exists = len(list_files)

        self.assertEqual(error_in_reading_vars, False)
        self.assertEqual(dir_exists, True)
        self.assertGreater(files_exists,0)

    # Check reading sources from DB is ok
    def test_GetEumetcast_sources(self):

        error_in_db = False
        try:
            eumetcast_sources_list = querydb.get_eumetcast_sources()
        except:
            error_in_db = True

        self.assertEqual(error_in_db, False)

suite_get_eumetcast = unittest.TestLoader().loadTestsFromTestCase(TestGetEumetcast)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_get_eumetcast)
