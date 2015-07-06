from __future__ import absolute_import
__author__ = "Marco Clerici"


from unittest import TestCase
from lib.python import es_logging as log

# Trivial change
logger = log.my_logger(__name__)

from apps.processing import proc_functions

class TestProcessing(TestCase):

    def Test_create_permanent_missing_files(self):
        args = {"product_code":"tamsat-rfe", "version":"2.0", "sub_product_code":"10d", "mapset_code":"TAMSAT-Africa-8km"}

        # proc_functions.create_permanently_missing_for_dataset(**args)
        self.assertEqual(1, 1)
