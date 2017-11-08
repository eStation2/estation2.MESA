_author__ = "Jurriaan van 't Klooster"

from config import es_constants
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product
from lib.python import functions
from database import querydb
import unittest
import datetime
import webpy_esapp_helpers

from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestWebpy(unittest.TestCase):

    def test_ProductNavigatorDataSets(self):
        products = webpy_esapp_helpers.ProductNavigatorDataSets()
        print products
        self.assertEqual(1, 1)

    def test_DataSets(self):
        datasets = webpy_esapp_helpers.DataSets()
        print datasets
        self.assertEqual(1, 1)

    def test_TimeseriesProducts(self):
        tsproducts = webpy_esapp_helpers.TimeseriesProducts()
        # print tsproducts
        self.assertEqual(1, 1)

    def test_getAllColorSchemes(self):
        result = webpy_esapp_helpers.getAllColorSchemes()
        self.assertEqual(1, 1)


    def test_getProcessing(self):
        result = webpy_esapp_helpers.getProcessing(False)
        self.assertEqual(1, 1)


    def test_GetLegends(self):
        result = webpy_esapp_helpers.GetLegends()
        self.assertEqual(1, 1)


    def test_SaveLegend(self):
        params = {
            'legendid': -1,
            'legend_descriptive_name': 'TESTING CREATE NEW LEGEND',
            'title_in_legend': 'TEST',
            'minvalue': 0,
            'maxvalue': 3,
            'legendClasses': [{"legend_id":-1,"from_step":0,"to_step":1,"color_rgb":"255 0 0","color_label":"1","group_label":"","id":-1},
                              {"legend_id":-1,"from_step":1,"to_step":2,"color_rgb":"255 0 100","color_label":"2","group_label":"","id":-2},
                              {"legend_id":-1,"from_step":2,"to_step":3,"color_rgb":"255 0 255","color_label":"3","group_label":"","id":-3}]
        }
        result = webpy_esapp_helpers.SaveLegend(params)
        self.assertEqual(1, 1)


    def test_DeleteLegend(self):
        params = {
            'legend': {
                       'colourscheme': "JUR <table cellspacing=0 cellpadding=0 width=100%><tr></tr></table>",
                       'id': -223,
                       'legend_descriptive_name': "JUR Test legend",
                       'legendid': 232,
                       'legendname': "JUR",
                       'maxvalue': 3,
                       'minvalue': 0
                    }
        }
        result = webpy_esapp_helpers.DeleteLegend(params)
        self.assertEqual(1, 1)


    def test_CopyLegend(self):
        params = {
            'legendid': 237,
            'legendname': "test legend"
        }
        result = webpy_esapp_helpers.copyLegend(params)
        self.assertEqual(1, 1)


    def test_AssignLegends(self):
        params = {
            'productcode': 'vgt-ndvi',
            'productversion': 'sv2-pv2.1',
            'subproductcode': 'ndvi-linearx2',
            'legendids': [81, 144]
        }
        result = webpy_esapp_helpers.AssignLegends(params)
        self.assertEqual(1, 1)


    def test_GetAssignedDatasets(self):
        params = {
            'legendid': 111
        }
        assigneddatasets_json = webpy_esapp_helpers.GetAssignedDatasets(params['legendid'])
        self.assertEqual(1, 1)