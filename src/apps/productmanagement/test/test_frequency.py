# -*- coding: utf-8 -*-

#
#	purpose: Test dataset functions
#	author:  Marco Beri marcoberi@gmail.com
#	date:	 09.07.2014
#

from __future__ import absolute_import

import unittest
import datetime

from ..datasets import Frequency
from ..exceptions import (WrongFrequencyValue, WrongFrequencyUnit,
        WrongFrequencyType, WrongFrequencyDateFormat )


class TestFrequency(unittest.TestCase):
    def test_class(self):
        self.assertIsInstance(Frequency(1, Frequency.UNIT.DEKAD, Frequency.TYPE.PER), Frequency)

    def test_wrong_value_1(self):
        self.assertRaises(WrongFrequencyValue, Frequency, *('a', Frequency.UNIT.DEKAD, Frequency.TYPE.PER))

    def test_wrong_unit(self):
        self.assertRaises(WrongFrequencyUnit, Frequency, *(1, '-' + Frequency.UNIT.DEKAD, Frequency.TYPE.PER))

    def test_wrong_type(self):
        self.assertRaises(WrongFrequencyType, Frequency, *(1, Frequency.UNIT.DEKAD, '-' + Frequency.TYPE.PER))

    def test_dataformat_default_1(self):
        frequency =  Frequency(1, Frequency.UNIT.DEKAD, Frequency.TYPE.PER)
        self.assertEqual(frequency.dateformat, Frequency.DATEFORMAT.DATE)

    def test_dataformat_default_2(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER)
        self.assertEqual(frequency.dateformat, Frequency.DATEFORMAT.DATETIME)

    def test_wrong_dataformat(self):
        self.assertRaises(WrongFrequencyDateFormat, Frequency, *(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, '-' + Frequency.DATEFORMAT.DATETIME))

    def test_today_datetime(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.DATETIME)
        self.assertEqual(type(frequency.today()), type(datetime.datetime.today()))

    def test_today_date(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.DATE)
        self.assertEqual(type(frequency.today()), type(datetime.date.today()))

    def test_today_monthday(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.MONTHDAY)
        self.assertEqual(type(frequency.today()), type(datetime.date.today()))

    def test_wrong_date(self):
        frequency =  Frequency(4, Frequency.UNIT.HOUR, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.MONTHDAY)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 12, 31)
        self.assertRaises(Exception, frequency.get_dates, *(to_date, from_date))

    def test_count_dates(self):
        frequency =  Frequency(1, Frequency.UNIT.MONTH, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.MONTHDAY)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 12, 31)
        self.assertEqual(frequency.count_dates(from_date, to_date), 12)

    def test_get_dates(self):
        frequency =  Frequency(1, Frequency.UNIT.MONTH, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.MONTHDAY)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 12, 31)
        self.assertEqual(len(frequency.get_dates(from_date, to_date)), 12)

    def test_get_internet_dates(self):
        frequency =  Frequency(1, Frequency.UNIT.MONTH, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.MONTHDAY)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 12, 31)
        dates = frequency.get_dates(from_date, to_date)
        templates = frequency.get_internet_dates(dates, "/Modis_%Y%m/mcd14dl.%Y-%m-%d.tif")
        self.assertEqual(templates[0], '/Modis_201401/mcd14dl.2014-01-01.tif')

    def test_get_internet_dates_dekad(self):
        #%{dkm}
        frequency =  Frequency(1, Frequency.UNIT.DEKAD, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.DATE)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 12, 31)
        dates = frequency.get_dates(from_date, to_date)
        templates = frequency.get_internet_dates(dates, "/Modis_%{dkm}_%Y%m%d/mcd14dl.%Y-%m-%d.tif")
        self.assertEqual(templates[0], '/Modis_1_20140101/mcd14dl.2014-01-01.tif')
        self.assertEqual(templates[1], '/Modis_2_20140111/mcd14dl.2014-01-11.tif')

    def test_get_internet_dates_add_days(self):
        #%{+/-<Nt><strftime>} = +/- N delta days/hours/
        frequency =  Frequency(1, Frequency.UNIT.DAY, Frequency.TYPE.PER, dateformat=Frequency.DATEFORMAT.DATE)
        from_date = datetime.date(2014, 1, 1)
        to_date = datetime.date(2014, 1, 31)
        dates = frequency.get_dates(from_date, to_date)
        templates = frequency.get_internet_dates(dates, "/Modis_%{+8dY-m-d}_%Y%m/mcd14dl.%Y-%m-%d.tif")
        self.assertEqual(templates[0], '/Modis_2014-01-09_201401/mcd14dl.2014-01-01.tif')
        self.assertEqual(templates[1], '/Modis_2014-01-10_201401/mcd14dl.2014-01-02.tif')

