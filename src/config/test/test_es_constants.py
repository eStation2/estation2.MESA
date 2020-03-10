# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = "Jurriaan van 't Klooster"

import site

site.addsitedir('/var/www/eStation2', known_paths=None)

from unittest import TestCase
from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestConstants(TestCase):

    def Test_es_constants(self):
        from config import es_constants

        for setting in es_constants.es2globals:
            print (setting)

        self.assertEqual(1, 1)


