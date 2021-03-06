 #-*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:     27.10.2014
#

from __future__ import absolute_import

import unittest
import os
import datetime
import glob
import sys

from apps.productmanagement.products import Product
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.exceptions import (NoProductFound, MissingMapset)

from config import es_constants
from lib.python import functions
from database import connectdb
from database import querydb
from lib.python import es_logging as log

logger = log.my_logger(__name__)
python_version = sys.version_info[0]

def glob_monkey(path):
    return []


class TestProducts(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB().db)
        self.kwargs = {'product_code': "vgt-ndvi",
                       'version': "sv2-pv2.2"}
        self.mapsets = ('SPOTV-Africa-1km', 'SPOTV-Africa-1km')
        self.subproducts = ('sm', 'ndv')
        self.files_mapsets = [os.path.join(es_constants.es2globals['data_dir'],
                                           self.kwargs['product_code'], mapset) for mapset in self.mapsets]
        self.files_subproducts = [os.path.join(file_mapset, subproduct_type, subproduct)
                                  for file_mapset in self.files_mapsets
                                  for subproduct_type in list(functions.dict_subprod_type_2_dir.values())
                                  for subproduct in self.subproducts]
        self.old_glob = glob.glob
        glob.glob = glob_monkey

    def tearDown(self):
        glob.glob = self.old_glob

    def get_product(self):
        product = Product(**self.kwargs)
        product._get_full_mapsets = lambda: self.files_mapsets
        product._get_full_subproducts = lambda mapset='*': self.files_subproducts
        return product

    def test_class(self):
        self.assertIsInstance(Product(**self.kwargs), Product)

    # ES2-596 -> does not rise exception ???
    def test_class_no_product(self):

        kwargs = {'product_code': "---prod--"}
        self.assertRaisesRegexp(NoProductFound, "(?i).*found.*product.*", Product, **kwargs)

    def test_class_mapsets(self):
        product = self.get_product()
        self.assertEqual(len(product.mapsets), len(self.mapsets))
        self.assertEqual(set(product.mapsets), set(self.mapsets))

    def test_class_subproduct(self):
        product = self.get_product()
        self.assertEqual(len(product.subproducts), len(self.subproducts))
        self.assertEqual(set(product.subproducts), set(self.subproducts))

    def test_class_get_subproduct(self):
        product = self.get_product()
        subproducts = product.get_subproducts(mapset=product.mapsets[0])
        self.assertEqual(len(subproducts), len(self.subproducts))
        self.assertEqual(set(subproducts), set(self.subproducts))

    def test_class_dataset(self):
        product = self.get_product()
        self.assertIsInstance(product.get_dataset(sub_product_code=product.subproducts[-1],
                                                  mapset=self.mapsets[0]), Dataset)

    def test_all_products_to_json(self):
        def row2dict(row):
            d = {}
            for column_name in list(row.c.keys()):  # all_cols:
                d[column_name] = str(getattr(row, column_name))
            return d

        # get full distinct list of products (native only)
        db_products = querydb.get_products()
        try:
            db_products.__len__()
        except AttributeError:
            db_products = querydb.get_product_native(allrecs=True)
        self.assertTrue(db_products.__len__() > 0)
        products_dict_all = []
        # loop the products list
        for product in db_products:
            if python_version == 2:
                prod_dict = row2dict(product)
            if python_version == 3:
                prod_dict = product
            productcode = prod_dict['productcode']
            version = prod_dict['version']
            p = Product(product_code=productcode, version=version)

            # does the product have mapsets AND subproducts?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    mapset_dict = row2dict(mapset_info)
                    mapset_dict['mapsetdatasets'] = []
                    all_mapset_datasets = p.get_subproducts(mapset=mapset)
                    for subproductcode in all_mapset_datasets:
                        dataset_info = querydb.get_subproduct(productcode=productcode,
                                                              version=version,
                                                              subproductcode=subproductcode)

                        dataset_dict = row2dict(dataset_info)
                        dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                        completeness = dataset.get_dataset_normalized_info()
                        dataset_dict['datasetcompleteness'] = completeness

                        mapset_dict['mapsetdatasets'].append(dataset_dict)
                    prod_dict['productmapsets'].append(mapset_dict)
            products_dict_all.append(prod_dict)

        # See ES2-596
        self.assertEqual(len(db_products), len(products_dict_all))

    def test_get_missing(self):
        product = self.get_product()
        mapsets = product.mapsets
        subproducts = product.subproducts
        self.assertEqual(len(product.get_missing_datasets(mapset=mapsets[0], sub_product_code=subproducts[0])), 1)
        missing = product.get_missing_datasets(mapset=mapsets[0])
        self.assertEqual(len(missing), 2)
        # self.assertEqual(missing[0]['info']['missingfiles'], 1)
        self.assertEqual(len(product.get_missing_datasets()), 4)

        # ES2-596: 'assertRaisesRegex' not in python 2.7
        if python_version == 2:
            self.assertRaisesRegexp(MissingMapset, "(?i).*mapset.*%s*" % subproducts[0], product.get_missing_datasets,
                                    **{'sub_product_code': subproducts[0]})

        if python_version == 3:
            self.assertRaisesRegex(MissingMapset, "(?i).*mapset.*%s*" % subproducts[0], product.get_missing_datasets,
                                    **{'sub_product_code': subproducts[0]})

    @unittest.skipIf(True, 'Unstable (??)')
    def test_get_missing_from_date_to_date(self):
        product = self.get_product()

        mapsets = product.mapsets
        sub_product = product.subproducts[0]
        from_date = datetime.date(2000, 1, 1)
        to_date = datetime.date(2040, 1, 1)
        missing = product.get_missing_datasets(mapset=mapsets[0], sub_product_code=sub_product, from_date=from_date,
                                               to_date=to_date)
        self.assertEqual(missing[0]['info']['missingfiles'], 1441)

    def test_get_missing_all(self):
        product = self.get_product()
        mapsets = product.mapsets
        missing = product.get_missing_datasets(mapset=mapsets[0])
        self.assertEqual(missing[0]['from_start'], True)
        self.assertEqual(missing[0]['to_end'], True)

    def test_missing_dates(self):
        today = datetime.date.today().strftime("%Y-%m-%d")
        missing = [{
            'info': {
                'missingfiles': 1,
                'totfiles': 1,
                'intervals': [{
                    'todate': today,
                    'totfiles': 1,
                    'missing': True,
                    'intervaltype': 'missing',
                    'intervalpercentage': 100.0,
                    'fromdate': today,
                }],
                'lastdate': today,
                'firstdate': today,
            },
            'product': 'vgt-ndvi',
            'to_end': True,
            'mapset_data': {
                'rotation_factor_long': 0.0,
                'description': u'Original Spot VGT 1km mapset',
                'pixel_shift_lat': -0.008928571428571,
                'defined_by': u'JRC',
                'pixel_shift_long': 0.008928571428571,
                'upper_left_lat': 38.004464285714285,
                'upper_left_long': -26.004464285714285,
                'mapsetcode': u'SPOTV-Africa-1km',
                'pixel_size_y': 8177,
                'pixel_size_x': 9633,
                'srs_wkt': u'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY['
                           u'"EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
                           u'AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],'
                           u'AUTHORITY["EPSG","4326"]]',
                'rotation_factor_lat': 0.0},
            'subproduct': 'sm',
            'version': 'sv2-pv2.2',
            'from_start': True,
            'mapset': 'SPOTV-Africa-1km'}]
        product = self.get_product()
        dates = product.get_missing_filenames(missing[0])
        self.assertIsInstance(dates, list)


suite_products = unittest.TestLoader().loadTestsFromTestCase(TestProducts)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_products)
