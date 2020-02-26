# -*- coding: utf-8 -*-

#
#   purpose: Test dataset functions
#   author:  Marco Beri marcoberi@gmail.com
#   date:    09.07.2014
#

from __future__ import absolute_import

import unittest
import datetime
import time
from apps.productmanagement.helpers import INTERVAL_TYPE
from apps.productmanagement.datasets import Dataset, Frequency
from apps.productmanagement.exceptions import (WrongDateType, NoProductFound)
from apps.productmanagement.products import *

from lib.python import functions
from database import querydb
from database import connectdb
import json

class TestDatasets(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB().db)
        self.kwargs = {'version': '2.0', 'product_code':"fewsnet-rfe", 'sub_product_code': "10d", 'mapset': 'FEWSNET-Africa-8km'}
        self.files_dekad = [
                "20180101_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180111_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180121_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180201_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180211_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                # Here 2 missings
                "20180221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.missing",
                "20180301_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.missing",
                "20180311_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180321_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180401_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180411_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180421_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180501_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180511_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180521_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180601_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180611_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180621_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                # Here 3 holes - July
                "20180801_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180811_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180821_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180921_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181001_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181011_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181021_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181101_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181111_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181121_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181201_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181211_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20181221_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif"
                ]

    def test_class(self):
        self.assertIsInstance(Dataset(**self.kwargs), Dataset)

    def test_class_no_product(self):
        kwargs = {'product_code':"---prod---", 'sub_product_code': "---subprod---", 'mapset': '---mapset---'}
        # The dataset class was modified not to raise an exception, rather returning boject with empty fields.
        # self.assertRaisesRegexp(NoProductFound, "(?i).*found.*product.*", Dataset, **kwargs)
        dataset = Dataset(**kwargs)
        self.assertEqual(dataset.frequency_id,'undefined')

    def test_wrong_date(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': '2014-10-01'})
        self.assertRaisesRegexp(WrongDateType, "(?i).*wrong.*date.*type.*",
                Dataset, **kwargs)

    def test_frequency_8days(self):
        freq8 = Frequency(1, '8days', 'e', dateformat=None)
        print freq8.today()
        print freq8.get_next_date(freq8.today(),'8days',1)

    def test_intervals(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2018, 12, 31)})
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs : self.files_dekad
        intervals = dataset.intervals
        self.assertEquals(len(intervals), 5)
        self.assertEquals(intervals[0].interval_type, INTERVAL_TYPE.PRESENT)
        self.assertEquals(intervals[1].interval_type, INTERVAL_TYPE.PERMANENT_MISSING)
        self.assertEquals(intervals[2].interval_type, INTERVAL_TYPE.PRESENT)
        self.assertEquals(intervals[3].interval_type, INTERVAL_TYPE.MISSING)
        self.assertEquals(intervals[4].interval_type, INTERVAL_TYPE.PRESENT)

    def test_number_files(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2014, 12, 31)})
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs : self.files_dekad
        number = dataset.get_number_files()
        self.assertEquals(number, number)

    def test_normalized_info(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2018, 2, 1)})
        files_dekad = [
                "20180101_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                "20180101_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.xml",
                "20180111_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                # Here 1 hole
                "20180201_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif",
                ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs : files_dekad
        segments = dataset.get_dataset_normalized_info()['intervals']
        total = 0
        for segment in segments:
            total += segment['intervalpercentage']
        self.assertEquals(int(total), 100)
        self.assertEquals(segments[0]['intervalpercentage'], 50.0)
        self.assertEquals(segments[1]['intervalpercentage'], 25.0)
        self.assertEquals(segments[2]['intervalpercentage'], 25.0)

    def test_normalized_info_15_minutes(self):
        kwargs = self.kwargs.copy()
        kwargs.update({
            #'from_date': datetime.datetime(2016, 2, 1),
            'to_date': datetime.datetime(2016, 2, 20),
            'product_code': "lsasaf-et",
            'version':'undefined',
            'sub_product_code': "et",
            'mapset': 'MSG-satellite-3km'
        })
        dataset = Dataset(**kwargs)
        completeness = dataset.get_dataset_normalized_info()
        pass
        #self.assertEquals(completeness['totfiles'], 18289)
        #self.assertEquals(completeness['missingfiles'], 18288)
        #self.assertEquals(completeness['intervals'][0]['intervalpercentage'], 1.0)

    def test_product_only_month_day(self):
        kwargs = self.kwargs.copy()
        kwargs.update({
            # Note: it goes wrong with the definition of the dates ...
            # 'from_date': datetime.date(2014, 1, 1),
            # 'to_date': datetime.date(2014, 12, 1),
            'product_code': "fewsnet-rfe",
            'sub_product_code': "1monmax",
            'mapset': 'FEWSNET-Africa-8km'
        })
        files = [
            "0101_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0201_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0301_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0401_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0501_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0601_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0701_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0801_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "0901_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "1001_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "1101_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
            "1201_fewsnet-rfe_1monmax_FEWSNET-Africa-8km_2.0.tif",
        ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs : files
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['totfiles'], 12)
        self.assertEquals(completeness['missingfiles'], 0)
        self.assertEquals(completeness['intervals'][0]['todate'], '12-01')
        self.assertEquals(completeness['intervals'][0]['fromdate'], '01-01')
        self.assertEquals(completeness['firstdate'], '01-01')
        self.assertEquals(completeness['lastdate'], '12-01')
        current_date = datetime.date(2014, 1, 1)
        last_date = datetime.date(2015, 1, 1)
        for i in range(12):
            current_date = dataset.next_date(current_date)
        self.assertEquals(last_date, current_date)

    def test_product_vgt_fapar(self):
        kwargs = self.kwargs.copy()
        kwargs.update({
            'from_date': datetime.date(2014, 1, 1),
            'to_date': datetime.date(2014, 12, 21),
            'product_code': "vgt-fapar",
            'sub_product_code': "fapar",
            'version': "V2.0",
            'mapset': 'SPOTV-Africa-1km'
        })
        files = [
            "20140621_vgt-fapar_fapar_SPOTV-Africa-1km_V2.0.tif",
                ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs : files
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['totfiles'], 36)
        self.assertEquals(completeness['missingfiles'], 35)

    def test_get_dates(self):
        kwargs = {'product_code':"vgt-ndvi",
                  'version':'sv2-pv2.2',
                  'sub_product_code': "ndvi-linearx2",
                  'mapset': 'SPOTV-Africa-1km'
                  }
        dataset = Dataset(**kwargs)
        if dataset._db_product.frequency_id == 'singlefile':
            dates = 'nodate'
        else:
            dates = dataset._frequency.get_dates(datetime.date(2018,1,1),datetime.date(2018,12,21))
            last = None
            for date in dates:
                if last:
                    self.assertTrue(last < date)
                last = date

        self.assertEquals(len(dates), 36)

    def test_with_xml(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': datetime.date(2018, 1, 1),
                       'to_date': datetime.date(2018, 12, 31)})
        dataset = Dataset(**kwargs)
        files_dekad = sorted(self.files_dekad[:])
        # Add and .xml at the begin and at the end
        files_dekad = [files_dekad[0][:-3] + 'xml'] + files_dekad + [files_dekad[-1][:-3] + 'xml']
        dataset.get_filenames = lambda **my_kwargs : files_dekad
        dataset._clean_cache()

        # Note: the .missing (permanent missing) are not counted as 'missing'
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['missingfiles'], 3)

    def test_find_gaps(self):
        start_time = time.time()
        from_date = datetime.date(2020, 1, 1)
        to_date = datetime.date(2020, 12, 31)

        kwargs = {
                'product_code':"modis-pp",
                'version': "v2013.1",
                'sub_product_code': "8daysmax",      #  "lst"
                'mapset': 'MODIS-Africa-4km',
                'from_date': from_date,
                'to_date': to_date
                 }
        # kwargs = {
        #         'product_code': "vgt-ndvi",
        #         'version': "sv2-pv2.1",
        #         'sub_product_code': "10davg-linearx2",
        #         'mapset': 'SPOTV-Africa-1km'
        #          }
        # kwargs = {
        #         'product_code':"arc2-rain",
        #         'version': "2.0",
        #         'sub_product_code': "1year",
        #         'mapset': 'ARC2-Africa-11km'
        #          }
        dataset = Dataset(**kwargs)
        info = dataset.get_dataset_normalized_info()
        print ("--- %s seconds ---" % (time.time() - start_time))

#   Additional test to mimic/replicate what happens in webpy_esapp (M.C.)
# class TestDatasets4UI(unittest.TestCase):
#
#     def test_datasets_visualization_webpy(self):
#     # Re-produce what done in webpy_esapp for the Data Management page
#         # return web.ctx
#         db_products = querydb.get_products()
#
#         if db_products.__len__() > 0:
#             products_dict_all = []
#             # loop the products list
#             for row in db_products:
#                 prod_dict = functions.row2dict(row)
#                 productcode = prod_dict['productcode']
#                 version = prod_dict['version']
#
#                 p = Product(product_code=productcode, version=version)
#                 # print productcode
#                 # does the product have mapsets AND subproducts?
#                 all_prod_mapsets = p.mapsets
#                 all_prod_subproducts = p.subproducts
#                 if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
#                     prod_dict['productmapsets'] = []
#                     for mapset in all_prod_mapsets:
#                         mapset_dict = []
#                         # print mapset
#                         mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
#                         # if mapset_info.__len__() > 0:
#                         mapset_dict = functions.row2dict(mapset_info)
#                         # else:
#                         #   mapset_dict['mapsetcode'] = mapset
#                         mapset_dict['mapsetdatasets'] = []
#                         all_mapset_datasets = p.get_subproducts(mapset=mapset)
#                         for subproductcode in all_mapset_datasets:
#                             # print 'productcode: ' + productcode
#                             # print 'version: ' + version
#                             # print 'subproductcode: ' + subproductcode
#                             dataset_info = querydb.get_subproduct(productcode=productcode,
#                                                                   version=version,
#                                                                   subproductcode=subproductcode)
#                             # print dataset_info
#                             # dataset_info = querydb.db.product.get(productcode, version, subproductcode)
#                             # dataset_dict = {}
#                             if dataset_info is not None:
#                                 dataset_dict = functions.row2dict(dataset_info)
#                                 # dataset_dict = dataset_info.__dict__
#                                 # del dataset_dict['_labels']
#                                 if hasattr(dataset_info,'frequency_id'):
#                                     if dataset_info.frequency_id == 'e15minute' or dataset_info.frequency_id == 'e30minute':
#                                         dataset_dict['nodisplay'] = 'no_minutes_display'
#                                     else:
#                                         dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
#                                         completeness = dataset.get_dataset_normalized_info()
#                                         dataset_dict['datasetcompleteness'] = completeness
#                                         dataset_dict['nodisplay'] = 'false'
#
#                                     dataset_dict['mapsetcode'] = mapset_dict['mapsetcode']
#                                     dataset_dict['mapset_descriptive_name'] = mapset_dict['descriptive_name']
#
#                                     mapset_dict['mapsetdatasets'].append(dataset_dict)
#                                 else:
#                                     pass
#                         prod_dict['productmapsets'].append(mapset_dict)
#                 products_dict_all.append(prod_dict)
#
#             prod_json = json.dumps(products_dict_all,
#                                    ensure_ascii=False,
#                                    sort_keys=True,
#                                    indent=4,
#                                    separators=(', ', ': '))
#
#             datamanagement_json = '{"success":"true", "total":'\
#                                   + str(db_products.__len__())\
#                                   + ',"products":'+prod_json+'}'
#
#         else:
#             datamanagement_json = '{"success":false, "error":"No data sets defined!"}'
#
#         return datamanagement_json
#
#     def test_normalized_info_vgt_ndvi_1(self):
#         dataset=Dataset('vgt-ndvi','10dmax-linearx2', 'SPOTV-Africa-1km', version='sv2-pv2.1')
#         filenames=dataset.get_filenames()
#         info = dataset.get_dataset_normalized_info()
#         self.assertEquals(info['missingfiles'], 0)
#
#     def test_normalized_info_vgt_ndvi_2(self):
#         dataset=Dataset('vgt-ndvi','year_min_linearx2', 'SPOTV-Africa-1km', version='sv2-pv2.1')
#         filenames=dataset.get_filenames()
#         print filenames
#         info = dataset.get_dataset_normalized_info()
#         print info
#         self.assertEquals(info['missingfiles'], 1)


suite_datasets = unittest.TestLoader().loadTestsFromTestCase(TestDatasets)
# if __name__ == '__main__':
#     unittest.TextTestRunner(verbosity=2).run(suite_datasets)