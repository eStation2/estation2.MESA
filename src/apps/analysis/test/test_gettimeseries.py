from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library

import unittest, time
import gdal, ogr, osr, os
from datetime import date
from multiprocessing import *

from apps.analysis.getTimeseries import getTimeseries, getFilesList

standard_library.install_aliases()


class TestGetTimeseries(unittest.TestCase):

    def setUp(self):
        # ES2-271/288
        self.x_min = ' -1.875'
        self.x_max = ' -1.865'
        self.y_max = ' 12.19'
        self.y_min = ' 12.18'

        # x_min = ' -2.095'
        # x_max = ' -2.092'
        # y_max = ' 12.04'
        # y_min = ' 12.03'

        self.wkt_test_ES2_271 = 'POLYGON((' + self.x_min + self.y_min + ',' + self.x_min + self.y_max + ',' + \
                                self.x_max + self.y_max + ',' + self.x_max + self.y_min + ',' + \
                                self.x_min + self.y_min + '))'

        # Democratic Republic of the Congo
        self.wkt_simple = 'POLYGON((30.0  -15.0, 34.0  -19.0, 38.0 -15.0 , 34.0 -11.0, 30.0  -15.0))'
        self.wkt_point = 'POINT(30.001 -14.998)'

        # Compare polygon, line and point
        self.wkt_test_polygon = 'POLYGON((17.6117 -8.6655, 17.620 -8.6655, 17.620 -8.674, ' \
                                '17.6117 -8.674, 17.6117 -8.6655))'
        self.wkt_test_point = 'POINT(17.61749383509286 -8.669792916188465)'
        self.wkt_test_line = 'LINESTRING(17.620332195396873 -8.670385805073723,' \
                             '17.62050129082339 -8.673658667869148,17.61364114174842 -8.673261732805757,' \
                             '17.611898679860804 -8.670246408122715)'

        self.wkt_line = 'LINESTRING(21.466286229428963 -0.6593739797435525, ' \
                        '23.883990821821985 0.8791653063247331, 25.78884898552558 -0.5128464286894285)'

        self.wkt = self.wkt_test_ES2_271

        self.aggregate = {'aggregation_type': 'mean',
                          'aggregation_min': 0.0,
                          'aggregation_max': 0.0}

    def test_africa(self):

        productcode = "vgt-ndvi"
        subproductcode = "ndvi-linearx2"
        version = "sv2-pv2.2"
        mapsetcode = "SPOTV-Africa-1km"

        productcode = "tamsat-rfe"
        subproductcode = "10d"
        version = "3.0"
        mapsetcode = "TAMSAT-Africa-4km"

        from_date = date(2019, 0o1, 0o1)
        to_date = date(2019, 12, 31)
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode,
                                    self.wkt_simple, from_date, to_date, self.aggregate)
        print(list_values)

        self.assertEquals(len(list_values), 36)

    def test_point_line_poly_vgt_ndvi_ndv(self):

        productcode = "vgt-ndvi"
        subproductcode = "ndv"
        version = "sv2-pv2.1"
        mapsetcode = "SPOTV-Africa-1km"
        from_date = date(2016, 0o1, 0o1)
        to_date = date(2016, 12, 31)
        date_format = 'YYYYMMDD'
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_test_polygon, from_date,
                                    to_date, self.aggregate)
        print(list_values)
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_test_polygon, from_date,
                                    to_date, self.aggregate)

        print(list_values)

        self.assertEquals(len(list_values), 36)

    def test_files_vgt_ndvi_ndv(self):
        productcode = "vgt-ndvi"
        subproductcode = "ndv"
        version = "spot-v1"
        mapsetcode = "SPOTV-Africa-1km"

        from_date = date(2002, 0o1, 0o1)
        to_date = date(2002, 12, 31)
        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt,
                                    from_date, to_date, self.aggregate)
        self.assertEquals(len(list_values), 36)

    def test_files_rfe_10d(self):
        productcode = "fewsnet-rfe"
        subproductcode = "10d"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"
        from_date = date(2013, 0o1, 0o1)
        to_date = date(2015, 12, 21)
        date_format = 'YYYYMMDD'

        [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
                                                from_date, to_date)
        self.assertEquals(len(list_files), 108)

    def test_files_rfe_10davg_case1(self):
        productcode = "fewsnet-rfe"
        subproductcode = "10davg"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"
        from_date = date(2014, 0o1, 0o1)
        to_date = date(2014, 12, 31)
        date_format = 'MMDD'

        [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
                                                from_date, to_date)
        self.assertEquals(len(list_files), 36)

    def test_files_rfe_10davg_case2(self):
        productcode = "fewsnet-rfe"
        subproductcode = "10davg"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"

        from_date = date(2012, 9, 1)
        to_date = date(2015, 6, 21)
        date_format = 'MMDD'

        [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
                                                from_date, to_date)
        self.assertEquals(len(list_files), 102)

    def test_files_rfe_10davg_case3(self):
        productcode = "fewsnet-rfe"
        subproductcode = "10davg"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"
        from_date = date(2013, 1, 1)
        to_date = date(2015, 6, 21)
        date_format = 'MMDD'

        [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format,
                                                from_date, to_date)
        self.assertEquals(len(list_files), 90)

    def test_values_rfe_10d(self):
        productcode = "fewsnet-rfe"
        subproductcode = "10d"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"
        from_date = date(2013, 0o1, 0o1)
        to_date = date(2015, 12, 21)

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date,
                                    to_date, self.aggregate)
        self.assertEquals(len(list_values), 108)

    def test_values_rfe_10davg(self):

        productcode = "fewsnet-rfe"
        subproductcode = "10davg"
        version = "2.0"
        mapsetcode = "FEWSNET-Africa-8km"
        from_date = date(2015, 0o1, 0o1)
        to_date = date(2015, 0o1, 11)
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date,
                                    to_date, aggregate)
        print(list_values)
        self.assertEquals(len(list_values), 2)

    def test_values_sst(self):
        productcode = "modis-sst"
        subproductcode = "monavg"
        version = "v2013.1"
        mapsetcode = "MODIS-Africa-4km"
        from_date = date(2015, 0o1, 0o1)
        to_date = date(2015, 0o2, 11)
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple, from_date, to_date,
                                    aggregate)
        print(list_values)
        self.assertEquals(len(list_values), 2)

    def test_values_chirps_10d(self):

        productcode = "chirps-dekad"
        subproductcode = "10d"
        version = "2.0"
        mapsetcode = "CHIRP-Africa-5km"
        from_date = date(2015, 0o1, 0o1)
        to_date = date(2015, 0o2, 21)
        # Type can be 'none' -> average
        #             'count' -> number of pixels in min-max range
        #             'percent' -> (number of pixels in min-max range) / (number of valid pixels) * 100

        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': 20.0,
                     'aggregation_max': 40.0}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_simple,
                                    from_date, to_date, aggregate)
        print(list_values)
        self.assertEquals(len(list_values), 6)

    def test_chla_values_ES2_105(self):

        productcode = "modis-chla"
        subproductcode = "chla-day"
        version = "v2013.1"
        mapsetcode = "MODIS-Africa-4km"

        from_date = date(2015, 0o1, 0o1)
        to_date = date(2015, 0o1, 11)

        # Type can be 'none' -> average
        #             'count' -> number of pixels in min-max range
        #             'percent' -> (number of pixels in min-max range) / (number of valid pixels) * 100

        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': 0.0,
                     'aggregation_max': 40.0}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt_test_ES2_271, from_date,
                                    to_date, aggregate)
        print(list_values)
        self.assertEquals(len(list_values), 11)

    def test_values_wd_gee(self):

        productcode = "wd-gee"
        subproductcode = "avg"
        version = "1.0"
        mapsetcode = "WD-GEE-ECOWAS-AVG"
        from_date = date(2018, 0o1, 0o1)
        to_date = date(2018, 0o1, 0o1)
        aggregate = {'aggregation_type': 'surface',
                     'aggregation_min': 1,
                     'aggregation_max': 100}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date,
                                    aggregate)
        print(list_values)

        self.assertEquals(len(list_values), 1)

    def test_values_chirps_precip(self):

        productcode = "chirps-dekad"
        subproductcode = "10d"
        version = "2.0"
        mapsetcode = "WD-GEE-ECOWAS-AVG"
        from_date = date(2018, 0o1, 0o1)
        to_date = date(2018, 0o1, 0o1)
        aggregate = {'aggregation_type': 'surface',
                     'aggregation_min': 1,
                     'aggregation_max': 100}

        list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date,
                                    aggregate)
        print(list_values)

        self.assertEquals(len(list_values), 1)

    # def test_values_chirps_10d_green(self):
    #     productcode = "chirps-dekad"
    #     subproductcode = "10d"
    #     version = "2.0"
    #     mapsetcode = "CHIRP-Africa-5km"
    #     from_date = date(2015, 0o1, 0o1)
    #     to_date = date(2015, 12, 21)
    #
    #     # Type can be 'none'   -> average
    #     #             'count'  -> number of pixels in min-max range
    #     #             'percent'-> (number of pixels in min-max range)/(number of valid pixels) * 100
    #
    #     aggregate = {'aggregation_type': 'mean',
    #                  'aggregation_min': 0.0,
    #                  'aggregation_max': 0.0}
    #
    #     module_name = 'getTimeseries'
    #     function_name = 'getTimeseries'
    #     proc_dir = __import__("apps.analysis")
    #     proc_pck = getattr(proc_dir, "analysis")
    #     proc_mod = getattr(proc_pck, module_name)
    #     proc_func = getattr(proc_mod, function_name)
    #     out_queue = Queue()
    #     # out_queue.put(returnVal=None)
    #
    #     args = [out_queue, productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date, aggregate]
    #     from_date = date(2016, 0o1, 0o1)
    #     to_date = date(2016, 12, 21)
    #     args2 = [out_queue, productcode, subproductcode, version, mapsetcode, self.wkt, from_date, to_date, aggregate]
    #
    #     # print args
    #     try:
    #         from apps.analysis.getTimeseries import getTimeseries
    #         start_time = time.time()
    #
    #         p = Process(target=getTimeseries, args=args)
    #         p.start()
    #         p.join()
    #         list_values_new = out_queue.get()
    #
    #         p2 = Process(target=getTimeseries, args=args2)
    #         p2.start()
    #         p2.join()
    #         list_values_new2 = out_queue.get()
    #
    #         exec_time = start_time - time.time()
    #         print("--- %s seconds ---" % exec_time)
    #         print(list_values_new)
    #         print(list_values_new2)
    #
    #     except:
    #         raise NameError('Error in getTimeseries')
    #
    #     self.assertEquals(len(list_values_new), 36)


suite_gettimeseries = unittest.TestLoader().loadTestsFromTestCase(TestGetTimeseries)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_gettimeseries)
