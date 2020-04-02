# -*- coding: utf-8 -*-

#
#   purpose: Test dataset functions
#   author:  Marco Beri marcoberi@gmail.com
#   date:    09.07.2014
#

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
from builtins import int
from builtins import str
from builtins import range

import unittest
import datetime
# import time
# import json

# from lib.python import functions
from apps.productmanagement.helpers import INTERVAL_TYPE
from apps.productmanagement.datasets import Dataset, Frequency
from apps.productmanagement.exceptions import (WrongDateType, NoProductFound)
from apps.productmanagement.products import *
from database import querydb
from database import connectdb

standard_library.install_aliases()


class TestDatasets(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB().db)
        self.kwargs = {'version': '2.0', 'product_code': "fewsnet-rfe", 'sub_product_code': "10d",
                       'mapset': 'FEWSNET-Africa-8km'}
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
        kwargs = {'product_code': "---prod---", 'sub_product_code': "---subprod---", 'mapset': '---mapset---'}
        # The dataset class was modified not to raise an exception, rather returning object with empty fields.
        # self.assertRaisesRegexp(NoProductFound, "(?i).*found.*product.*", Dataset, **kwargs)
        dataset = Dataset(**kwargs)
        self.assertEqual(dataset.frequency_id, 'undefined')

    def test_wrong_date(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': '2014-10-01'})
        self.assertRaisesRegex(WrongDateType, "(?i).*wrong.*date.*type.*",
                               Dataset, **kwargs)

    def test_frequency_8days(self):
        freq8 = Frequency(1, '8days', 'e', dateformat=None)
        print(freq8.today())
        print(freq8.get_next_date(freq8.today(), '8days', 1))
        self.assertEqual(freq8.dateformat, 'YYYYMMDD')

    def test_intervals(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2018, 12, 31)})
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs: self.files_dekad
        intervals = dataset.intervals
        self.assertEqual(len(intervals), 5)
        self.assertEqual(intervals[0].interval_type, INTERVAL_TYPE.PRESENT)
        self.assertEqual(intervals[1].interval_type, INTERVAL_TYPE.PERMANENT_MISSING)
        self.assertEqual(intervals[2].interval_type, INTERVAL_TYPE.PRESENT)
        self.assertEqual(intervals[3].interval_type, INTERVAL_TYPE.MISSING)
        self.assertEqual(intervals[4].interval_type, INTERVAL_TYPE.PRESENT)

    def test_number_files(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2014, 12, 31)})
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda **my_kwargs: self.files_dekad
        number = dataset.get_number_files()
        self.assertEqual(number, number)

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
        dataset.get_filenames = lambda **my_kwargs: files_dekad
        segments = dataset.get_dataset_normalized_info()['intervals']
        total = 0
        for segment in segments:
            total += segment['intervalpercentage']
        self.assertEqual(int(total), 100)
        self.assertEqual(segments[0]['intervalpercentage'], 50.0)
        self.assertEqual(segments[1]['intervalpercentage'], 25.0)
        self.assertEqual(segments[2]['intervalpercentage'], 25.0)

    def test_normalized_info_15_minutes(self):
        kwargs = self.kwargs.copy()
        kwargs.update({
            'from_date': datetime.datetime(2016, 2, 1),
            'to_date': datetime.datetime(2016, 2, 20),
            'product_code': "lsasaf-et",
            'version': 'undefined',
            'sub_product_code': "et",
            'mapset': 'MSG-satellite-3km'
        })
        dataset = Dataset(**kwargs)
        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['totfiles'], 913)
        self.assertEqual(completeness['missingfiles'], 913)

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
        dataset.get_filenames = lambda **my_kwargs: files
        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['totfiles'], 12)
        self.assertEqual(completeness['missingfiles'], 0)
        self.assertEqual(completeness['intervals'][0]['todate'], '12-01')
        self.assertEqual(completeness['intervals'][0]['fromdate'], '01-01')
        self.assertEqual(completeness['firstdate'], '01-01')
        self.assertEqual(completeness['lastdate'], '12-01')
        current_date = datetime.date(2014, 1, 1)
        last_date = datetime.date(2015, 1, 1)
        for i in range(12):
            current_date = dataset.next_date(current_date)
        self.assertEqual(last_date, current_date)

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
        dataset.get_filenames = lambda **my_kwargs: files
        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['totfiles'], 36)
        self.assertEqual(completeness['missingfiles'], 35)

    def test_get_dates(self):
        kwargs = {'product_code': "vgt-ndvi",
                  'version': 'sv2-pv2.2',
                  'sub_product_code': "ndvi-linearx2",
                  'mapset': 'SPOTV-Africa-1km'
                  }
        dataset = Dataset(**kwargs)
        if dataset._db_product.frequency_id == 'singlefile':
            dates = 'nodate'
        else:
            dates = dataset._frequency.get_dates(datetime.date(2018, 1, 1), datetime.date(2018, 12, 21))
            last = None
            for date in dates:
                if last:
                    self.assertTrue(last < date)
                last = date

        self.assertEqual(len(dates), 36)

    def test_with_xml(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': datetime.date(2018, 1, 1),
                       'to_date': datetime.date(2018, 12, 31)})
        dataset = Dataset(**kwargs)
        files_dekad = sorted(self.files_dekad[:])
        # Add and .xml at the begin and at the end
        files_dekad = [files_dekad[0][:-3] + 'xml'] + files_dekad + [files_dekad[-1][:-3] + 'xml']
        dataset.get_filenames = lambda **my_kwargs: files_dekad
        dataset._clean_cache()

        # Note: the .missing (permanent missing) are not counted as 'missing'
        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['missingfiles'], 3)

    def test_product_no_dates(self):
        kwargs = {
            'product_code': "fewsnet-rfe",
            'version': "2.0",
            'sub_product_code': "1monmax",
            'mapset': 'FEWSNET-Africa-8km',
        }
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
        dataset.get_filenames = lambda **my_kwargs: files
        dataset._clean_cache()

        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['totfiles'], 12)
        self.assertEqual(completeness['missingfiles'], 0)
        self.assertEqual(completeness['intervals'][0]['todate'], '12-01')
        self.assertEqual(completeness['intervals'][0]['fromdate'], '01-01')
        self.assertEqual(completeness['firstdate'], '01-01')
        self.assertEqual(completeness['lastdate'], '12-01')
        current_date = datetime.date(2014, 1, 1)
        last_date = datetime.date(2015, 1, 1)
        for i in range(12):
            current_date = dataset.next_date(current_date)
        self.assertEqual(last_date, current_date)

    def test_find_gaps(self):
        from_date = datetime.date(2020, 1, 1)
        to_date = datetime.date(2020, 12, 31)

        kwargs = {
            'product_code': "modis-pp",
            'version': "v2013.1",
            'sub_product_code': "8daysmax",  # "lst"
            'mapset': 'MODIS-Africa-4km',
            'from_date': from_date,
            'to_date': to_date
        }
        dataset = Dataset(**kwargs)
        completeness = dataset.get_dataset_normalized_info()
        self.assertEqual(completeness['totfiles'], 46)
        self.assertEqual(completeness['missingfiles'], 46)


suite_datasets = unittest.TestLoader().loadTestsFromTestCase(TestDatasets)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_datasets)
