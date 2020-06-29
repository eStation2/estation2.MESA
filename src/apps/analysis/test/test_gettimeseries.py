from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library

import unittest, time
import gdal, ogr, osr, os
from datetime import date
from multiprocessing import *
from config import es_constants

from apps.analysis.getTimeseries import getTimeseries, getFilesList

standard_library.install_aliases()


class TestGetTimeseries(unittest.TestCase):

    def setUp(self):

        es_constants.es2globals['processing_dir'] = es_constants.es2globals['test_data_dir']

        # Small square for WBD - see ES2-271/288
        self.x_min = ' -1.875'
        self.x_max = ' -1.865'
        self.y_max = ' 12.19'
        self.y_min = ' 12.18'

        self.wkt_test_ES2_271 = 'POLYGON((' + self.x_min + self.y_min + ',' + self.x_min + self.y_max + ',' + \
                                self.x_max + self.y_max + ',' + self.x_max + self.y_min + ',' + \
                                self.x_min + self.y_min + '))'

        # Define poly, point, line
        self.wkt_poly = 'POLYGON((30.0  -15.0, 34.0  -19.0, 38.0 -15.0 , 34.0 -11.0, 30.0  -15.0))'
        self.wkt_point = 'POINT(30.00 -15.0)'
        self.wkt_line = 'LINESTRING(30.0 -15.0, 30.1 -15.1, 30.3 -15.2)'

        # Define polygon out of TAMSAT Africa mapset
        self.wkt_out_of_mapset = 'POLYGON((51.0  -15.0, 52.0  -19.0, 53.0 -15.0 , 52.0 -11.0, 51.0  -15.0))'

        # Compare polygon, line and point
        self.wkt_test_polygon = 'POLYGON((17.6117 -8.6655, 17.620 -8.6655, 17.620 -8.674, ' \
                                '17.6117 -8.674, 17.6117 -8.6655))'
        self.wkt_test_point = 'POINT(17.61749383509286 -8.669792916188465)'
        self.wkt_test_line = 'LINESTRING(17.620332195396873 -8.670385805073723,' \
                             '17.62050129082339 -8.673658667869148,17.61364114174842 -8.673261732805757,' \
                             '17.611898679860804 -8.670246408122715)'

        self.wkt = self.wkt_test_ES2_271

        self.aggregate = {'aggregation_type': 'mean',
                          'aggregation_min': 0.0,
                          'aggregation_max': 0.0}

    # Extract values over wkt_rectangle for 36 decads (TAMSAT-RFE/3.0/10d)
    def test_wkt_rectangle(self):

        productcode = "tamsat-rfe"
        subproductcode = "10d"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2019, 1, 1)
        to_date = date(2019, 12, 31)
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode,
                                    self.wkt_poly, from_date, to_date, self.aggregate)
        print(list_values)

        # Check number of values
        self.assertEqual(len(list_values), 36)

        # Check value for 2019.01.01
        first_value = list_values[0]
        self.assertAlmostEqual(85.7455916064186,first_value['meanvalue'])

    # As above, but on a point (TAMSAT-RFE/3.0/10d)
    def test_wkt_point(self):

        productcode = "tamsat-rfe"
        subproductcode = "10d"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2019, 1, 1)
        to_date = date(2019, 12, 31)

        date_format = 'YYYYMMDD'
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_point, from_date,
                                    to_date, self.aggregate)
        print(list_values)

        # Check number of values
        self.assertEqual(len(list_values), 36)

        # Check value for 2019.01.01 - read in QGIS
        first_value = list_values[0]
        self.assertAlmostEqual(104,first_value['meanvalue'])

    # As above, but on a line (TAMSAT-RFE/3.0/10d)
    def test_wkt_line(self):

        productcode = "tamsat-rfe"
        subproductcode = "10d"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2019, 1, 1)
        to_date = date(2019, 12, 31)

        date_format = 'YYYYMMDD'
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_line, from_date,
                                    to_date, self.aggregate)
        print(list_values)

        # Check number of values
        self.assertEqual(len(list_values), 36)

        # Check value for 2019.01.01 - quickly looked at in QGIS
        first_value = list_values[0]
        self.assertAlmostEqual(100.333333333,first_value['meanvalue'])

    # Check on a MMDD prod within 1 year
    def test_tamsat_10davg_case1(self):

        productcode = "tamsat-rfe"
        subproductcode = "10davg"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"
        from_date = date(2014, 1, 1)
        to_date = date(2014, 12, 31)
        date_format = 'MMDD'

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_poly, from_date,
                                    to_date, self.aggregate)

        # Check number of values
        self.assertEqual(len(list_values), 36)

        # Check value for 2014.01.01
        first_value = list_values[0]
        self.assertAlmostEqual(70.203138776,first_value['meanvalue'])

    # Check on a MMDD prod across years
    def test_tamsat_10davg_case2(self):

        productcode = "tamsat-rfe"
        subproductcode = "10davg"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2012, 9, 1)
        to_date = date(2015, 6, 21)

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_poly, from_date,
                                    to_date, self.aggregate)

        # Check number of values
        self.assertEqual(len(list_values), 102)

        # Check first value
        first_value = list_values[0]
        self.assertAlmostEqual(0.08217245635690354,first_value['meanvalue'])

    # Check by using a polygon which extend beyond AOI
    def test_tamsat_10davg_es105(self):

        productcode = "tamsat-rfe"
        subproductcode = "10d"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2019, 1, 1)
        to_date = date(2019, 1, 11)

        try:
            failed = False
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_out_of_mapset, from_date,
                                    to_date, self.aggregate)
        except:
            failed = True
        # Check does not stop
        self.assertEqual(failed, False)

        # Check list empty
        self.assertEqual(len(list_values),0)


suite_gettimeseries = unittest.TestLoader().loadTestsFromTestCase(TestGetTimeseries)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_gettimeseries)

# The following test cases have not (yet) been updated to run with the new criteria, i.e.
# - working on test_data dir
# - compare the numeric results

    # def test_files_rfe_10d(self):
    #     productcode = "fewsnet-rfe"
    #     subproductcode = "10d"
    #     version = "2.0"
    #     mapsetcode = "FEWSNET-Africa-8km"
    #     from_date = date(2013, 0o1, 0o1)
    #     to_date = date(2015, 12, 21)
    #     date_format = 'YYYYMMDD'
    #
    #     [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
    #                                             from_date, to_date)
    #     self.assertEqual(len(list_files), 108)

    # def test_values_rfe_10d(self):
    #     productcode = "fewsnet-rfe"
    #     subproductcode = "10d"
    #     version = "2.0"
    #     mapsetcode = "FEWSNET-Africa-8km"
    #     from_date = date(2013, 0o1, 0o1)
    #     to_date = date(2015, 12, 21)
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date,
    #                                 to_date, self.aggregate)
    #     self.assertEquals(len(list_values), 108)


    # def test_values_rfe_10davg(self):
    #     productcode = "fewsnet-rfe"
    #     subproductcode = "10davg"
    #     version = "2.0"
    #     mapsetcode = "FEWSNET-Africa-8km"
    #     from_date = date(2015, 0o1, 0o1)
    #     to_date = date(2015, 0o1, 11)
    #     aggregate = {'aggregation_type': 'mean',
    #                  'aggregation_min': None,
    #                  'aggregation_max': None}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date,
    #                                 to_date, aggregate)
    #     print(list_values)
    #     self.assertEquals(len(list_values), 2)


    # def test_values_sst(self):
    #     productcode = "modis-sst"
    #     subproductcode = "monavg"
    #     version = "v2013.1"
    #     mapsetcode = "MODIS-Africa-4km"
    #     from_date = date(2015, 0o1, 0o1)
    #     to_date = date(2015, 0o2, 11)
    #     aggregate = {'aggregation_type': 'mean',
    #                  'aggregation_min': None,
    #                  'aggregation_max': None}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date,
    #                                 to_date,
    #                                 aggregate)
    #     print(list_values)
    #     self.assertEquals(len(list_values), 2)


    # def test_values_chirps_10d(self):
    #     productcode = "chirps-dekad"
    #     subproductcode = "10d"
    #     version = "2.0"
    #     mapsetcode = "CHIRP-Africa-5km"
    #     from_date = date(2015, 0o1, 0o1)
    #     to_date = date(2015, 0o2, 21)
    #     # Type can be 'none' -> average
    #     #             'count' -> number of pixels in min-max range
    #     #             'percent' -> (number of pixels in min-max range) / (number of valid pixels) * 100
    #
    #     aggregate = {'aggregation_type': 'mean',
    #                  'aggregation_min': 20.0,
    #                  'aggregation_max': 40.0}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple,
    #                                 from_date, to_date, aggregate)
    #     print(list_values)
    #     self.assertEquals(len(list_values), 6)


    # def test_chla_values_ES2_105(self):
    #     productcode = "modis-chla"
    #     subproductcode = "chla-day"
    #     version = "v2013.1"
    #     mapsetcode = "MODIS-Africa-4km"
    #
    #     from_date = date(2015, 1, 1)
    #     to_date = date(2015, 1, 11)
    #
    #     # Type can be 'none' -> average
    #     #             'count' -> number of pixels in min-max range
    #     #             'percent' -> (number of pixels in min-max range) / (number of valid pixels) * 100
    #
    #     aggregate = {'aggregation_type': 'mean',
    #                  'aggregation_min': 0.0,
    #                  'aggregation_max': 40.0}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_test_ES2_271, from_date,
    #                                 to_date, aggregate)
    #     print(list_values)
    #     self.assertEquals(len(list_values), 11)


    # def test_values_wd_gee(self):
    #     productcode = "wd-gee"
    #     subproductcode = "avg"
    #     version = "1.0"
    #     mapsetcode = "WD-GEE-ECOWAS-AVG"
    #     from_date = date(2018, 1, 1)
    #     to_date = date(2018, 1, 1)
    #     aggregate = {'aggregation_type': 'surface',
    #                  'aggregation_min': 1,
    #                  'aggregation_max': 100}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date,
    #                                 aggregate)
    #     print(list_values)
    #
    #     self.assertEquals(len(list_values), 1)


    # def test_values_chirps_precip(self):
    #     productcode = "chirps-dekad"
    #     subproductcode = "10d"
    #     version = "2.0"
    #     mapsetcode = "WD-GEE-ECOWAS-AVG"
    #     from_date = date(2018, 1, 1)
    #     to_date = date(2018, 1, 1)
    #     aggregate = {'aggregation_type': 'surface',
    #                  'aggregation_min': 1,
    #                  'aggregation_max': 100}
    #
    #     list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date,
    #                                 aggregate)
    #     print(list_values)
    #
    #     self.assertEqual(len(list_values), 1)
    # def test_files_rfe_10davg_case3(self):
    #     productcode = "fewsnet-rfe"
    #     subproductcode = "10davg"
    #     version = "2.0"
    #     mapsetcode = "FEWSNET-Africa-8km"
    #     from_date = date(2013, 1, 1)
    #     to_date = date(2015, 6, 21)
    #     date_format = 'MMDD'
    #
    #     [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
    #                                             from_date, to_date)
    #     self.assertEquals(len(list_files), 90)
