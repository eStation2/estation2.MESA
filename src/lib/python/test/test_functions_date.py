from unittest import TestCase

__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as f


class TestFunctionsDate(TestCase):

    str_yyyy = '2011'
    str_month = '05'
    str_day = '01'
    str_hh = '13'
    str_mm = '30'
    str_doy = '121'
    str_dkx = 'dk1'
    str_dkn = '1'

    julian_dekad = 1129
    julian_month = 377

    string_mmdd = str_month+str_day
    string_yyyymmdd = str_yyyy+str_month+str_day
    string_yyyymmddhhmm = string_yyyymmdd+str_hh+str_mm
    string_yyyydoy = str_yyyy+str_doy
    string_yymmk = str_yyyy[2:4]+str_month+str_dkn
    string_yyyy_mm_dkx = str_yyyy+'_'+str_month+'_'+str_dkx

    def test_is_date_time(self):

        self.assertTrue(f.is_date_yyyymmdd(self.string_yyyymmdd))
        self.assertTrue(f.is_date_mmdd(self.string_mmdd))
        self.assertTrue(f.is_date_yyyymmddhhmm(self.string_yyyymmddhhmm))
        self.assertTrue(f.is_date_yyyydoy(self.string_yyyydoy))


    def test_convert_date_time(self):

        self.assertEqual(f.conv_date_2_dekad(self.string_yyyymmdd), self.julian_dekad)
        self.assertEqual(f.conv_date_2_month(self.string_yyyymmdd), self.julian_month)

        self.assertEqual(f.conv_dekad_2_date(self.julian_dekad), self.string_yyyymmdd)
        self.assertEqual(f.conv_month_2_date(self.julian_month), self.string_yyyymmdd)

        self.assertEqual(f.conv_date_yyyydoy_2_yyyymmdd(self.string_yyyydoy),self.string_yyyymmdd)
        self.assertEqual(f.conv_date_yyyymmdd_2_doy(self.string_yyyymmdd), int(self.str_doy))

        self.assertEqual(f.conv_yyyy_mm_dkx_2_yyyymmdd(self.string_yyyy_mm_dkx), self.string_yyyymmdd)
        self.assertEqual(f.conv_yymmk_2_yyyymmdd(self.string_yymmk), self.string_yyyymmdd)

#
