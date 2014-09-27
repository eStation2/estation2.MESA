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
from ..helpers import find_gaps, add_years, add_months, add_days, add_dekads, add_pentads, cast_to_int, INTERVAL_TYPE
from ..exceptions import WrongDateParameter


class TestCasters(unittest.TestCase):
    def test_cast_1_0(self):
        self.assertEquals(1, cast_to_int("1"))
        self.assertEquals(1, cast_to_int("1.0"))
        self.assertEquals(1, cast_to_int("1."))
        self.assertEquals(1, cast_to_int(1))
        self.assertEquals(1, cast_to_int(1.0))
        self.assertEquals(1, cast_to_int("1.1"))
        self.assertEquals(1, cast_to_int(1.1))
        self.assertEquals(1, cast_to_int(u"1.1"))
        self.assertEquals("a", cast_to_int(u"a"))


class TestHelpersDate(unittest.TestCase):
    def test_add_years(self):
        self.assertEquals(add_years(datetime.date(2000, 3, 4), 4), datetime.date(2004, 3, 4))

    def test_add_years_to_leap_year_1(self):
        self.assertEquals(add_years(datetime.date(2000, 2, 29), 4), datetime.date(2004, 2, 29))

    def test_add_years_to_leap_year_2(self):
        self.assertEquals(add_years(datetime.date(2000, 2, 29), 3), datetime.date(2003, 2, 28))

    def test_add_months_1(self):
        self.assertEquals(add_months(datetime.date(2000, 3, 4), 4), datetime.date(2000, 7, 4))

    def test_add_months_2(self):
        self.assertEquals(add_months(datetime.date(2000, 3, 4), 26), datetime.date(2002, 5, 4))

    def test_add_months_3(self):
        self.assertEquals(add_months(datetime.date(2000, 3, 31), 13), datetime.date(2001, 4, 30))

    def test_add_months_4(self):
        self.assertEquals(add_months(datetime.date(2000, 1, 1), 11), datetime.date(2000, 12, 1))

    def test_add_dekad_1(self):
        self.assertEquals(add_dekads(datetime.date(2000, 1, 1), 2), datetime.date(2000, 1, 21))

    def test_add_dekad_2(self):
        self.assertEquals(add_dekads(datetime.date(2000, 1, 28), 1), datetime.date(2000, 2, 8))

    def test_add_dekad_3(self):
        self.assertEquals(add_dekads(datetime.date(2000, 1, 30), 3), datetime.date(2000, 3, 10))

    def test_add_pentad_1(self):
        self.assertEquals(add_pentads(datetime.date(2000, 1, 1), 2), datetime.date(2000, 1, 11))

    def test_add_pentad_2(self):
        self.assertEquals(add_pentads(datetime.date(2000, 1, 28), 1), datetime.date(2000, 2, 3))

    def test_add_pentad_3(self):
        self.assertEquals(add_pentads(datetime.date(2000, 1, 30), 3), datetime.date(2000, 2, 15))

    def test_add_days8_1(self):
        self.assertEquals(add_days(datetime.date(2000, 1, 1), 2, 8), datetime.date(2000, 1, 17))

    def test_add_days8_2(self):
        self.assertEquals(add_days(datetime.date(2000, 2, 26), 1, 8), datetime.date(2000, 3, 5))

    def test_add_days8_3(self):
        self.assertEquals(add_days(datetime.date(2001, 2, 26), 1, 8), datetime.date(2001, 3, 6))

    def test_add_days8_4(self):
        self.assertEquals(add_days(datetime.date(2000, 12, 25), 1, 8), datetime.date(2001, 1, 1))

    def test_add_days16_1(self):
        self.assertEquals(add_days(datetime.date(2000, 12, 25), 1, 16), datetime.date(2001, 1, 1))


class TestHelpersGap(unittest.TestCase):
    def setUp(self):
        self.files_dekad = [
                "20131021_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131111_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131121_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131211_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131221_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
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
                "20140601_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                ]
        self.files_day_gap = self.files_dekad[:3]
        self.from_date = datetime.date(2013, 12, 24)
        self.to_date = datetime.date(2014, 1, 5)
        self.files_day = [
                "20131227_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131228_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131229_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131230_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131231_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140102_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                ]
        self.files_15minutes = [
                "201310212200_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212215_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212230_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212245_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212300_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212315_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212330_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310212345_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310220000_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310220015_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "201310220030_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                ]
        self.files_months = [
                "20131001_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20131201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140101_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140201_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                "20140301_FEWSNET_RFE_RFE_FEWSNET_Africa_8km.tif",
                ]

    def test_find_gap_dekad_intervals_no_gap(self):
        intervals = find_gaps(self.files_dekad, 
            frequency=Frequency(dateformat='YYYYMMDD', value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.EVERY),
            only_intervals=True)
        self.assertEqual(len(intervals), 1)
        self.assertEqual(intervals[0][2], INTERVAL_TYPE.PRESENT)

    def test_find_gap_dekad_intervals_no_gap_to_date(self):
        intervals = find_gaps(self.files_dekad, frequency=Frequency(dateformat='YYYYMMDD', value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.EVERY),
                only_intervals=True, to_date=datetime.date(2014, 06, 10))
        self.assertEqual(len(intervals), 1)
        self.assertEqual(intervals[0][2], INTERVAL_TYPE.PRESENT)

    def test_find_gap_dekad_no_gap(self):
        self.assertEqual([], find_gaps(self.files_dekad, 
            frequency=Frequency(dateformat='YYYYMMDD', value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.EVERY)))

    def test_find_gap_dekad_no_gap_per(self):
        self.assertEqual([], find_gaps(self.files_dekad, 
            frequency=Frequency(dateformat='YYYYMMDD', value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.PER)))

    def test_find_gap_dekad_with_gap(self):
        gap = find_gaps(self.files_dekad[:10] + self.files_dekad[12:], 
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.EVERY))
        self.assertEqual(len(gap), 2)
        self.assertEqual(gap[0], self.files_dekad[10])
        self.assertEqual(gap[1], self.files_dekad[11])

    def test_find_gap_dekad_intervals_with_gap(self):
        frequency=Frequency(value=1, unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.EVERY)
        intervals = find_gaps(self.files_dekad[:10] + self.files_dekad[14:], 
            frequency=frequency, only_intervals=True)
        self.assertEqual(len(intervals), 3)
        self.assertEqual(intervals[0][2], INTERVAL_TYPE.PRESENT)
        self.assertEqual(intervals[1][0], frequency.extract_date(self.files_dekad[10]))
        self.assertEqual(intervals[1][1], frequency.extract_date(self.files_dekad[13]))
        self.assertEqual(intervals[2][2], INTERVAL_TYPE.PRESENT)

    def test_find_gap_dekad_with_gap_per(self):
        gap = find_gaps(self.files_dekad[:10] + self.files_dekad[12:], 
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DEKAD, frequency_type=Frequency.TYPE.PER))
        self.assertEqual(len(gap), 2)
        self.assertEqual(gap[0], self.files_dekad[10])
        self.assertEqual(gap[1], self.files_dekad[11])

    def test_find_gap_day(self):
        gap = find_gaps(self.files_day_gap,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY))
        self.assertEqual(len(gap), 19)

    def test_find_gap_intervals_day(self):
        frequency=Frequency(value=1, unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY)
        intervals = find_gaps(self.files_day_gap,
            frequency=frequency,
            only_intervals=True)
        self.assertEqual(len(intervals), 5)
        self.assertEqual(intervals[0][2], INTERVAL_TYPE.PRESENT) 
        self.assertEqual(intervals[0][0], frequency.extract_date(self.files_day_gap[0]))
        self.assertEqual(intervals[0][1], frequency.extract_date(self.files_day_gap[0]))
        self.assertEqual(intervals[1][2], INTERVAL_TYPE.MISSING) 
        self.assertEqual(intervals[2][2], INTERVAL_TYPE.PRESENT) 
        self.assertEqual(intervals[3][2], INTERVAL_TYPE.MISSING) 
        self.assertEqual(intervals[4][2], INTERVAL_TYPE.PRESENT) 
        self.assertEqual(intervals[4][0], frequency.extract_date(self.files_day_gap[-1]))
        self.assertEqual(intervals[4][1], frequency.extract_date(self.files_day_gap[-1]))

    def test_find_gap_day_per(self):
        gap = find_gaps(self.files_day_gap,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.PER))
        self.assertEqual(len(gap), 19)

    def test_find_gap_minutes(self):
        self.assertEqual([], find_gaps(self.files_15minutes, 
            frequency=Frequency(value=4,
                unit=Frequency.UNIT.HOUR, frequency_type=Frequency.TYPE.PER)))

    def test_find_gap_minutes_with_gap(self):
        gap = find_gaps(self.files_15minutes[:3] + self.files_15minutes[5:], 
            frequency=Frequency(value=4,
                unit=Frequency.UNIT.HOUR, frequency_type=Frequency.TYPE.PER))
        self.assertEqual(len(gap), 2)
        self.assertEqual(gap[0], self.files_15minutes[3])
        self.assertEqual(gap[1], self.files_15minutes[4])

    def test_find_gap_months(self):
        self.assertEqual([], find_gaps(self.files_months, 
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.MONTH, frequency_type=Frequency.TYPE.EVERY)))

    def test_find_gap_months_per(self):
        self.assertEqual([], find_gaps(self.files_months, 
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.MONTH, frequency_type=Frequency.TYPE.PER)))

    def test_find_gap_day_no_gap(self):
        self.assertEqual([], find_gaps(self.files_day,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY)))

    def test_find_gap_day_from(self):
        gap = find_gaps(self.files_day,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY),
            from_date=self.from_date)
        self.assertEqual(len(gap), 3)

    def test_find_gap_day_to(self):
        gap = find_gaps(self.files_day,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY),
            to_date=self.to_date)
        self.assertEqual(len(gap), 3)

    def test_find_gap_day_from_to(self):
        gap = find_gaps(self.files_day,
            frequency=Frequency(value=1,
                unit=Frequency.UNIT.DAY, frequency_type=Frequency.TYPE.EVERY),
            to_date=self.to_date,
            from_date=self.from_date)
        self.assertEqual(len(gap), 6)

    def test_find_gap_wrong_parameters(self):
        self.assertRaises(WrongDateParameter, find_gaps,
            *([], Frequency(value=1, unit=Frequency.UNIT.HOUR, frequency_type=Frequency.TYPE.EVERY),),
            **{'to_date': datetime.date(2014, 10, 10)})
