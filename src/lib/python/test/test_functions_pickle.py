from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase

__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as f
from config import es_constants
import datetime
from lib.python import es_logging as log

class TestFunctionsPickle(TestCase):

    logger = log.my_logger(__name__)
    processed_info_filename = es_constants.get_eumetcast_processed_list_prefix+'Test_info'
    processed_info = {'length_proc_list': 0,
                      'time_latest_exec': datetime.datetime.now(),
                      'time_latest_copy': datetime.datetime.now()}


    def test_write_pickle(self):

        self.logger.info('Pickle filename is: %s',  self.processed_info_filename)
        f.dump_obj_to_pickle(self.processed_info, self.processed_info_filename)


#
