from __future__ import absolute_import
__author__ = "Marco Clerici"


from unittest import TestCase
from lib.python import es_logging as log

# Trivial change
logger = log.my_logger(__name__)

from apps.processing import proc_functions

class TestProcFunctions(TestCase):

    def Test_reproject_output(self):

        input_file = '/data/processing/lsasaf-et/undefined/MSG-satellite-3km/derived/10d30min/201510010000_lsasaf-et_10d30min_MSG-satellite-3km_undefined.tif'
        # input_file = '/data/processing/lsasaf-lst/undefined/MSG-satellite-3km/tif/lst/201510011230_lsasaf-lst_lst_MSG-satellite-3km_undefined.tif'
        # input_file = '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20010221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif'

        target_mapset_id = 'SPOTV-ECOWAS-1km'
        orig_mapset_id = 'MSG-satellite-3km'
        # orig_mapset_id = 'FEWSNET-Africa-8km'

        proc_functions.reproject_output(input_file, orig_mapset_id, target_mapset_id, logger)

        self.assertEqual(1, 1)

    def Test_remove_old_files(self):

        productcode='lsasaf-lst'
        subprod='lst'
        version='undefined'
        type='Ingest'
        nmonths=6
        mapset = 'MSG-satellite-3km'

        proc_functions.remove_old_files(productcode, subprod, version, mapset, type, nmonths)

        self.assertEqual(1, 1)

