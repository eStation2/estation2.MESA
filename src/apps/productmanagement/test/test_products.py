# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Marco Beri marcoberi@gmail.com
#    date:     27.10.2014
#

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import str
import unittest
import os
import datetime
import glob
import shutil
from apps.productmanagement.products import Product
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.exceptions import (NoProductFound, MissingMapset)

from config import es_constants
from lib.python import functions
from database import connectdb
from database import querydb
from lib.python import es_logging as log
from lib.python import metadata
logger = log.my_logger(__name__)


def glob_monkey(path):
    return []


class TestProducts(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB(use_sqlite=True).db)
        self.kwargs = {'product_code':"vgt_ndvi"}
        self.mapsets = ('WGS84_Africa_1km', 'WGS84_Sahel_1km')
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

    def test_class_no_product(self):
        kwargs = {'product_code':"---prod---"}
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
            prod_dict = row2dict(product)
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
        self.assertEquals(len(db_products), 31)

    def test_get_missing(self):
        product = self.get_product()
        mapsets = product.mapsets
        subproducts = product.subproducts
        self.assertEqual(len(product.get_missing_datasets(mapset=mapsets[0], sub_product_code=subproducts[0])), 1)
        missing = product.get_missing_datasets(mapset=mapsets[0])
        self.assertEqual(len(missing), 2)
        self.assertEqual(missing[0]['info']['missingfiles'], 1)
        self.assertEqual(len(product.get_missing_datasets()), 4)
        self.assertRaisesRegexp(MissingMapset, "(?i).*mapset.*%s*" % subproducts[0], product.get_missing_datasets,
                **{'sub_product_code': subproducts[0]})

    def test_get_missing_from_date_to_date(self):
        product = self.get_product()
        mapsets = product.mapsets
        from_date=datetime.date(2000, 1, 1)
        to_date=datetime.date(2040, 1, 1)
        missing = product.get_missing_datasets(mapset=mapsets[0], from_date=from_date, to_date=to_date)
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
            'product': 'vgt_ndvi',
            'to_end': True,
            'mapset_data': {
                'rotation_factor_long': 0.0,
                'description': u'Original Spot VGT 1km mapset',
                'pixel_shift_lat': -0.008928571428571,
                'defined_by': u'JRC',
                'pixel_shift_long': 0.008928571428571,
                'upper_left_lat': 38.004464285714285,
                'upper_left_long': -26.004464285714285,
                'mapsetcode': u'WGS84_Africa_1km',
                'pixel_size_y': 8177,
                'pixel_size_x': 9633,
                'srs_wkt': u'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],AUTHORITY["EPSG","4326"]]',
                'rotation_factor_lat': 0.0},
            'subproduct': 'sm',
            'version': None,
            'from_start': True,
            'mapset': 'WGS84_Africa_1km'}]
        product = self.get_product()
        dates = product.get_missing_filenames(missing[0])
        self.assertIsInstance(dates, list)


#   Additional test to mimic/replicate what happens in webpy_esapp.py (M.C.)
class TestProducts4UI(unittest.TestCase):

    def hide_some_files(self, productcode, version, subproductcode, type, mapset, dates):
    # Move to /tmp/eStation2/test/ some products - for generating a product request

        source_dir = es_constants.es2globals['processing_dir'] + \
                     functions.set_path_sub_directory(productcode, subproductcode, type, version, mapset)
        target_dir = es_constants.es2globals['base_tmp_dir']

        for date in dates:
            filename = date + functions.set_path_filename_no_date(productcode,subproductcode, mapset, version,'.tif')

            fullpath=source_dir+os.path.sep+filename
            fullpath_dest=target_dir+os.path.sep+filename

            try:
                os.rename(source_dir+filename, fullpath_dest)
            except:
                logger.error('Error in moving file %s' % fullpath)

    def move_back_files(self, tmp_dir):

        # Create Metadata class to get target fullpath
        meta = metadata.SdsMetadata()

        # Get list of files in tmp dir
        files = glob.glob(tmp_dir+'*.tif')

        for my_file in files:
            fullpath_dest=meta.get_target_filepath(my_file)
            try:
                os.rename(my_file, fullpath_dest)
            except:
                logger.error('Error in moving file %s' % fullpath_dest)


    # This is to test the data completeness for a single product/version
    def test_product_data_management(self):
        def row2dict(row):
            d = {}
            for column_name in list(row.c.keys()):  # all_cols:
                d[column_name] = str(getattr(row, column_name))
            return d

        # Select prod/vers
        productcode = 'vgt-fapar'
        version = 'V2.0'
        product = Product(product_code=productcode, version=version)
        # does the product have mapsets AND subproducts?
        all_prod_mapsets = product.mapsets
        all_prod_subproducts = product.subproducts
        if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    mapset_dict = row2dict(mapset_info)
                    mapset_dict['mapsetdatasets'] = []
                    all_mapset_datasets = product.get_subproducts(mapset=mapset)
                    for subproductcode in all_mapset_datasets:
                        dataset_info = querydb.get_subproduct(productcode=productcode,
                                                              version=version,
                                                              subproductcode=subproductcode)

                        dataset_dict = row2dict(dataset_info)
                        dataset = product.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                        completeness = dataset.get_dataset_normalized_info()
                        dataset_dict['datasetcompleteness'] = completeness

                        mapset_dict['mapsetdatasets'].append(dataset_dict)

    def test_missing_product_request_product_1(self):

        # Test the mechanism of creating 'missing' reports on a specific 'product'
        productcode = 'fewsnet-rfe'
        version='2.0'
        product = Product(product_code=productcode, version=version)
        mapsets = product.mapsets
        subproductcode = '10d'
        type = 'Ingest'
        to_date=datetime.date(2015,4,30)

        # Create an initial list
        # missing = product.get_missing_datasets(mapset=mapsets[0],sub_product_code=subproductcode, from_date=None, to_date=to_date)

        # Move away some files
        dates = []
        dates.append('20150101')
        dates.append('20150111')
        dates.append('20150121')
        #self.hide_some_files(productcode, version, subproductcode, type, mapsets[0], dates)

        # Create the 'missing' list
        missing = product.get_missing_datasets(mapset=mapsets[0],sub_product_code=subproductcode, from_date=None, to_date=to_date)

        # Move back the files (to create .tar)
        self.move_back_files('/tmp/eStation2/')
        # Create the tar file with files 'missing'
        [file_tar, result] = product.create_tar(missing, filetar=None, tgz=True)

        # Move away the files again files
        self.hide_some_files(productcode, version, subproductcode, type, mapsets[0], dates)

        # Import the files from archive
        result = product.import_tar(file_tar, tgz=True)

        # Re-create the 'missing' list
        missing = product.get_missing_datasets(mapset=mapsets[0],sub_product_code=subproductcode, from_date=None, to_date=to_date)

        a=1

    def test_rename_file_eumetcast(self):

        input_file='/data/processing//vgt-ndvi/spot-v1/SPOTV-Africa-1km/tif/ndv/20020421_vgt-ndvi_ndv_SPOTV-Africa-1km_spot-v1.tif'
        new_name=functions.convert_name_to_eumetcast(input_file)
        output_dir='/data/archives/'
        shutil.copyfile(input_file,output_dir+new_name)
        print (output_dir+new_name)

    def test_list_my_subproducts(self):

        productcode='vgt-ndvi'
        version='sv2-pv2.1'
        #productcode='fewsnet-rfe'
        #version='2.0'
        product = Product(product_code=productcode, version=version)
        my_list = product.list_all_ingested_and_derived_subproducts_mapsets()
        for sprod in my_list:
            print (sprod)

    def test_data_management(self):
        import json

        db_products = querydb.get_products(activated=True)

        if db_products.__len__() > 0:
            products_dict_all = []
            # loop the products list
            for row in db_products:
                prod_dict = functions.row2dict(row)
                productcode = prod_dict['productcode']
                version = prod_dict['version']

                p = Product(product_code=productcode, version=version)
                # print productcode
                # does the product have mapsets AND subproducts?
                all_prod_mapsets = p.mapsets
                all_prod_subproducts = p.subproducts
                if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                    prod_dict['productmapsets'] = []
                    for mapset in all_prod_mapsets:
                        mapset_dict = []
                        # print mapset
                        mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                        # if mapset_info.__len__() > 0:
                        mapset_dict = functions.row2dict(mapset_info)
                        # else:
                        #   mapset_dict['mapsetcode'] = mapset
                        mapset_dict['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print 'productcode: ' + productcode
                            # print 'version: ' + version
                            # print 'subproductcode: ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode)
                            # print dataset_info
                            # dataset_info = querydb.db.product.get(productcode, version, subproductcode)
                            # dataset_dict = {}
                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                # dataset_dict = dataset_info.__dict__
                                # del dataset_dict['_labels']
                                if hasattr(dataset_info,'frequency_id'):
                                    if dataset_info.frequency_id == 'e15minute' or dataset_info.frequency_id == 'e30minute':
                                        dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # To be implemented in dataset.py
                                    elif dataset_info.frequency_id == 'e1year':
                                        dataset_dict['nodisplay'] = 'no_minutes_display'
                                    else:
                                        dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                        completeness = dataset.get_dataset_normalized_info()
                                        dataset_dict['datasetcompleteness'] = completeness
                                        dataset_dict['nodisplay'] = 'false'

                                    dataset_dict['mapsetcode'] = mapset_dict['mapsetcode']
                                    dataset_dict['mapset_descriptive_name'] = mapset_dict['descriptive_name']

                                    mapset_dict['mapsetdatasets'].append(dataset_dict)
                                else:
                                    pass
                        prod_dict['productmapsets'].append(mapset_dict)
                products_dict_all.append(prod_dict)

            prod_json = json.dumps(products_dict_all,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            datamanagement_json = '{"success":"true", "total":'\
                                  + str(db_products.__len__())\
                                  + ',"products":'+prod_json+'}'

        else:
            datamanagement_json = '{"success":false, "error":"No data sets defined!"}'