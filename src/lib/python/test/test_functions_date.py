from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import int
from future import standard_library
standard_library.install_aliases()
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

    def test_convert_date_g2(self):
        import lib.python.functions as f
        self.assertEqual(f.conv_yyyymmdd_g2_2_yyyymmdd('20151103'), '20151101')
        self.assertEqual(f.conv_yyyymmdd_g2_2_yyyymmdd('20151110'), '20151101')
        self.assertEqual(f.conv_yyyymmdd_g2_2_yyyymmdd('20151131'), '20151121')
        self.assertEqual(f.conv_yyyymmdd_g2_2_yyyymmdd('20151105'), '20151101')
        self.assertEqual(f.conv_yyyymmdd_g2_2_yyyymmdd('20151109'), '20151101')

    def test_convert_date_2_quarter(self):
        self.assertEqual(f.conv_date_2_quarter('20150123'), '20150101')
        self.assertEqual(f.conv_date_2_quarter('20150323'), '20150101')

        self.assertEqual(f.conv_date_2_quarter('20150423'), '20150401')
        self.assertEqual(f.conv_date_2_quarter('20150629'), '20150401')

        self.assertEqual(f.conv_date_2_quarter('20150723'), '20150701')
        self.assertEqual(f.conv_date_2_quarter('20150930'), '20150701')

        self.assertEqual(f.conv_date_2_quarter('20151029'), '20151001')
        self.assertEqual(f.conv_date_2_quarter('20151229'), '20151001')

    def test_convert_date_8days(self):

        # Non-leap year
        self.assertEqual(f.conv_date_2_8days('20110101'),1)
        self.assertEqual(f.conv_date_2_8days('20110108'),1)
        self.assertEqual(f.conv_date_2_8days('20110109'),2)
        self.assertEqual(f.conv_date_2_8days('20110225'),7)
        self.assertEqual(f.conv_date_2_8days('20110226'),8)
        self.assertEqual(f.conv_date_2_8days('20110305'),8)
        self.assertEqual(f.conv_date_2_8days('20110306'),9)

        self.assertEqual(f.conv_date_2_8days('20111226'),45)
        self.assertEqual(f.conv_date_2_8days('20111227'),46)
        self.assertEqual(f.conv_date_2_8days('20111231'),46)


        # Leap year
        self.assertEqual(f.conv_date_2_8days('20120304'),8)
        self.assertEqual(f.conv_date_2_8days('20120305'),9)
        self.assertEqual(f.conv_date_2_8days('20121225'),45)
        self.assertEqual(f.conv_date_2_8days('20121226'),46)
        self.assertEqual(f.conv_date_2_8days('20121231'),46)


    def test_dekad_nbr_in_season(self):

        start ='0101'
        self.assertEqual(f.dekad_nbr_in_season('0101',start), 1)
        self.assertEqual(f.dekad_nbr_in_season('0401',start), 10)
        self.assertEqual(f.dekad_nbr_in_season('1221',start), 36)

        start ='0901'
        self.assertEqual(f.dekad_nbr_in_season('0901',start), 1)
        self.assertEqual(f.dekad_nbr_in_season('1201',start), 10)
        self.assertEqual(f.dekad_nbr_in_season('0101',start), 13)
        self.assertEqual(f.dekad_nbr_in_season('0401', start),22)

    def test_convert_date_get_number_days_month(self):
        import lib.python.functions as f
        self.assertEqual(f.get_number_days_month('20180201'), 28)

    def test_day_lenght(self):
        day = 31
        latitude = 40.0
        dl = f.day_length(day,latitude)
        print ('Day lenght is: {0}'.format(dl))
