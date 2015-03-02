# -*- coding: utf-8 -*-

#
#   purpose: Test dataset functions
#   author:  Marco Beri marcoberi@gmail.com
#   date:    09.07.2014
#

from __future__ import absolute_import

import unittest
import datetime
import sys
from ..helpers import INTERVAL_TYPE
from ..datasets import Dataset
from ..exceptions import (WrongDateType, NoProductFound)

from lib.python import functions
from database import querydb
from database import connectdb
import json

class TestDatasets(unittest.TestCase):
    def setUp(self):
        setattr(querydb, 'db', connectdb.ConnectDB(use_sqlite=True).db)
        self.kwargs = {'product_code':"fewsnet_rfe", 'sub_product_code': "rfe", 'mapset': 'FEWSNET_Africa_8km'}
        self.files_dekad = [
                "20140101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140111_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140121_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140211_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140221_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140301_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140311_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140321_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140401_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140411_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140421_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140501_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140511_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140521_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140601_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.missing",
                "20140611_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.missing",
                "20140621_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.missing",
                "20140701_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140711_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140721_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                # Here 3 holes
                "20140901_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140911_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140921_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141001_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141011_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141021_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141111_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141121_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141211_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20141221_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                ]

    def test_class(self):
        self.assertIsInstance(Dataset(**self.kwargs), Dataset)

    def test_class_no_product(self):
        kwargs = {'product_code':"---prod---", 'sub_product_code': "---subprod---", 'mapset': '---mapset---'}
        self.assertRaisesRegexp(NoProductFound, "(?i).*found.*product.*", Dataset, **kwargs)

    def test_wrong_date(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': '2014-10-01'})
        self.assertRaisesRegexp(WrongDateType, "(?i).*wrong.*date.*type.*",
                Dataset, **kwargs)

    def test_intervals(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2014, 12, 31)})
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: self.files_dekad
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
        dataset.get_filenames = lambda: self.files_dekad
        number = dataset.get_number_files()
        self.assertEquals(number, number)

    def test_normalized_info(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'to_date': datetime.date(2014, 2, 1)})
        files_dekad = [
                "20140101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140111_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                # Here 1 hole
                "20140201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif"
                ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: files_dekad
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
            'to_date': datetime.datetime(2014, 2, 1),
            'product_code': "lsasaf_lst",
            'sub_product_code': "lst",
            'mapset': 'WGS84_Africa_1km'
        })
        files_15min = [
                "201307251200_lsasaf_lst_lst_WGS84_Africa_1km.tif",
                ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: files_15min
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['totfiles'], 18289)
        self.assertEquals(completeness['missingfiles'], 18288)
        self.assertEquals(completeness['intervals'][0]['intervalpercentage'], 1.0)

    def test_product_only_month_day(self):
        kwargs = self.kwargs.copy()
        kwargs.update({
            'from_date': datetime.date(2014, 1, 1),
            'to_date': datetime.date(2014, 12, 1),
            'product_code': "fewsnet_rfe",
            'sub_product_code': "1monmax",
            'mapset': 'WGS84_Africa_1km'
        })
        files = [
            "0101_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0201_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0301_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0401_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0501_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0601_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0701_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0801_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0901_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1001_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1101_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1201_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
        ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: files
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
            'to_date': datetime.datetime(2014, 11, 1),
            'product_code': "vgt_fapar",
            'sub_product_code': "fapar",
            'version': "V1.3",
            'mapset': 'WGS84_Africa_1km'
        })
        files = [
            "201406230000_vgt_fapar_fapar_WGS84_Africa_1km.tif",
                ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: files
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['totfiles'], 13)
        self.assertEquals(completeness['missingfiles'], 12)

    def test_get_dates(self):
        kwargs = self.kwargs.copy()
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: self.files_dekad
        dates = dataset.get_dates()
        last = None
        for date in dates:
            if last:
                self.assertTrue(last < date)
            last = date
        self.assertEquals(len(dates), 33)

    def test_with_xml(self):
        kwargs = self.kwargs.copy()
        kwargs.update({'from_date': datetime.date(2014, 1, 1),
                       'to_date': datetime.date(2014, 12, 31)})
        dataset = Dataset(**kwargs)
        files_dekad = sorted(self.files_dekad[:])
        files_dekad = [files_dekad[0][:-3] + 'xml'] + files_dekad + [files_dekad[-1][:-3] + 'xml']
        dataset.get_filenames = lambda: files_dekad
        completeness = dataset.get_dataset_normalized_info()
        self.assertEquals(completeness['missingfiles'], 3)

    def test_product_no_dates(self):
        kwargs = {
                'product_code':"fewsnet_rfe",
                'sub_product_code': "rfe",
                'sub_product_code': "1monmax",
                'mapset': 'WGS84_Africa_1km',
        }
        files = [
            "0101_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0201_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0301_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0401_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0501_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0601_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0701_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0801_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "0901_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1001_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1101_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
            "1201_fewsnet_rfe_1monmax_FEWSNET_Africa_8km.tif",
        ]
        dataset = Dataset(**kwargs)
        dataset.get_filenames = lambda: files
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
