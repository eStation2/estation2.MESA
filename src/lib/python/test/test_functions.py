from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
from builtins import int

import os
import sys
import shutil
import datetime
import unittest
from datetime import date

import lib.python.functions as functions
from lib.python import es_logging as log
from config import es_constants
from database import querydb

logger = log.my_logger(__name__)
standard_library.install_aliases()

systemsettings = functions.getSystemSettings()
install_type = systemsettings['type_installation'].lower()


class TestFunctions(unittest.TestCase):

    def setUp(self):

        self.str_yyyy = '2011'
        self.str_month = '05'
        self.str_day = '01'
        self.str_hh = '13'
        self.str_mm = '30'
        self.str_doy = '121'
        self.str_dkx = 'dk1'
        self.str_dkn = '1'

        self.julian_dekad = 1129
        self.julian_month = 377

        self.string_mmdd = self.str_month + self.str_day
        self.string_yyyymmdd = self.str_yyyy + self.str_month + self.str_day
        self.string_yyyymmddhhmm = self.string_yyyymmdd + self.str_hh + self.str_mm
        self.string_yyyydoy = self.str_yyyy + self.str_doy
        self.string_yymmk = self.str_yyyy[2:4] + self.str_month + self.str_dkn
        self.string_yyyy_mm_dkx = self.str_yyyy + '_' + self.str_month + '_' + self.str_dkx

        # Common definitions
        self.str_date = '201401011200'
        self.str_version = 'my-version'
        self.str_prod = str('my-prod-code')
        self.str_sprod = str('my-subprod-code')
        self.str_mapset = 'my-mapset'
        self.str_extension = '.tif'
        self.product_type = 'Ingest'
        self.str_type_subdir = functions.dict_subprod_type_2_dir[self.product_type]

        # Rule for sub_dir is: <prod_code>/<mapset>/<type>/<sprod_code>

        self.sep = os.path.sep
        self.sub_dir = self.str_prod + self.sep + \
                       self.str_version + self.sep + \
                       self.str_mapset + self.sep + \
                       self.str_type_subdir + self.sep + \
                       self.str_sprod + self.sep

        self.dir_name = self.sep + 'base' + self.sep + 'dir' + self.sep + 'some' + \
                        self.sep + 'where' + self.sep + self.sub_dir

        # Rule for filename is: <datetime>_<prod_code>_<sprod_code>_<mapset>_<version>.<ext>
        self.filename = self.str_date + '_' + self.str_prod + '_' + self.str_sprod + '_' + \
                        self.str_mapset + '_' + self.str_version + self.str_extension

        # Rule for filename_eumetcast is: MESA_JRC_<prod_code>_<sprod_code>_<datetime>_<mapset>_<version>.<ext>
        self.filename_eumetcast = 'MESA_JRC_' + self.str_prod + '_' + self.str_sprod + '_' + \
                                  self.str_date + '_' + self.str_mapset + '_' + self.str_version + self.str_extension

        self.fullpath = self.dir_name + self.filename

        self.processed_info_filename = es_constants.get_eumetcast_processed_list_prefix + 'Test_info'
        self.processed_info = {'length_proc_list': 0,
                               'time_latest_exec': datetime.datetime.now(),
                               'time_latest_copy': datetime.datetime.now()}

        self.testdatadir = es_constants.es2globals['test_data_dir']
        self.testresultdir = es_constants.es2globals['base_tmp_dir'] + os.path.sep + 'testresults'
        if not os.path.isdir(self.testresultdir):
            os.mkdir(self.testresultdir)
            os.chmod(self.testresultdir, 0o755)
        else:
            shutil.rmtree(self.testresultdir)
            os.mkdir(self.testresultdir)
            os.chmod(self.testresultdir, 0o755)

        # File should be there
        self.src_file = self.testdatadir + '/tamsat-rfe/native/rfe2020_01-dk3.v3.nc'

    def test_check_output_dir(self):
        output_dir = '/tmp/eStation2'
        self.assertTrue(functions.check_output_dir(output_dir))

    @unittest.skip("Remove function? This function is not used anywhere in the code!")
    def test_check_polygons_intersects(self):
        # TODO: Remove function? This function is not used anywhere in the code!
        # poly1 = []
        # poly2 = []
        # self.assertTrue(functions.check_polygons_intersects(poly1, poly2))
        self.assertTrue(True)

    @unittest.skip("Remove function? This function is not used anywhere in the code and is not working!")
    def test_checkDateFormat(self):
        # TODO: Remove function? This function is not used anywhere in the code and is not working!
        myString = '05061967'
        result = functions.checkDateFormat(myString)
        self.assertEqual(result, None)

    def test_checkIP(self):
        self.assertIsInstance(functions.checkIP(), str)

    def test_conv_date_2_semester(self):
        testdate = '20200120'
        self.assertEqual(functions.conv_date_2_semester(testdate), '20200101')

    def test_conv_list_2_string(self):
        inlist = ['01012019', '11012019', '21012019', '01022019', '11022019', '21022019']
        self.assertIsInstance(functions.conv_list_2_string(inlist), str)

    def test_conv_list_2_unique_value(self):
        # List of 6 values, of which 4 are unique
        inlist = ['01012019', '01012019', '21012019', '01022019', '01022019', '21022019']
        self.assertIs(len(functions.conv_list_2_unique_value(inlist)), 4)

    def test_conv_yyyydmmdk_2_yyyymmdd(self):
        yymmk = '2020.03.1'
        self.assertEqual(functions.conv_yyyydmmdk_2_yyyymmdd(yymmk), '20200301')

    def test_convert_name_from_archive(self):
        my_input_file = '20181201_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        result = 'vgt-ndvi/sv2-pv2.2/SPOTV-IGAD-1km/tif/ndvi-linearx2/20181201_vgt-ndvi_ndvi-linearx2_SPOTV-IGAD-1km_sv2-pv2.2.tif'
        product_type = 'Ingest'
        target_mapsetid = 'SPOTV-IGAD-1km'
        self.assertEqual(functions.convert_name_from_archive(my_input_file,
                                                             product_type,
                                                             with_dir=True,
                                                             new_mapset=target_mapsetid), result)

    def test_create_sym_link(self):
        src_file = self.src_file
        fake_file = self.testdatadir + '/tif/fakefile.tif'
        trg_file = self.testresultdir + '/link_to_rfe2020_01-dk3.v3.nc'

        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=False), 0)  # SYM LINK CREATED
        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=False), 1)  # SYM LINK ALREADY CREATED
        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=True), 0)  # SYM LINK RECREATED
        self.assertEqual(functions.create_sym_link(fake_file, trg_file, force=True), 1)  # SOURCE FILE DOES'T EXIST

    def test_day_per_dekad(self):
        yyyymmdd = '20200121'
        # myvar = functions.day_per_dekad(yyyymmdd)
        self.assertEqual(functions.day_per_dekad(yyyymmdd), 11)
        yyyymmdd = '20200101'
        # myvar = functions.day_per_dekad(yyyymmdd)
        self.assertEqual(functions.day_per_dekad(yyyymmdd), 10)

    def test_dotdict(self):
        testdict = {'a': 1, 'b': 2}
        myvar = functions.dotdict(testdict)
        # print(myvar.a)
        self.assertEqual(myvar.a, 1)
        self.assertEqual(myvar.b, 2)

    def test_element_to_list(self):
        input_list = [1, 2, 3, 4]
        result1 = functions.element_to_list(input_list)
        self.assertIsInstance(result1, list)
        input_tuple = (1, 2, 3, 4)
        result2 = functions.element_to_list(input_tuple)
        self.assertIsInstance(result2, tuple)
        input_arg = 1
        result3 = functions.element_to_list(input_arg)
        self.assertIsInstance(result3, list)

    def test_ensure_sep_present(self):
        pathbegin = 'path/does/not/begin/with/seperator'
        pathend = '/path/does/not/end/with/seperator'
        position = 'begin'
        # myvar = functions.ensure_sep_present(pathbegin, position)
        self.assertTrue(functions.ensure_sep_present(pathbegin, position).startswith("/"))
        position = 'end'
        # myvar2 = functions.ensure_sep_present(pathend, position)
        self.assertTrue(functions.ensure_sep_present(pathend, position).endswith("/"))

    def test_exclude_current_year(self):
        today = datetime.date.today()
        current_year = today.strftime('%Y')
        input_file_list = ['20180101_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif',
                           '20180111_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif',
                           '20180121_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif',
                           current_year + '0101_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif',
                           current_year + '0111_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif',
                           current_year + '0121_chirps-dekad_10d_CHIRP-Africa-5km_2.0.tif'
                           ]
        myvar = functions.exclude_current_year(input_file_list)
        self.assertEqual(len(myvar), 3)

    def test_extract_from_date(self):
        str_date = '202001200924'
        [str_year, str_month, str_day, str_hour] = functions.extract_from_date(str_date)
        self.assertEqual(str_year, '2020')
        self.assertEqual(str_month, '01')
        self.assertEqual(str_day, '20')
        self.assertEqual(str_hour, '0924')

        str_date = '20200120'
        [str_year, str_month, str_day, str_hour] = functions.extract_from_date(str_date)
        self.assertEqual(str_year, '2020')
        self.assertEqual(str_month, '01')
        self.assertEqual(str_day, '20')
        self.assertEqual(str_hour, '0000')

        str_date = '0120'
        [str_year, str_month, str_day, str_hour] = functions.extract_from_date(str_date)
        self.assertEqual(str_year, '')
        self.assertEqual(str_month, '01')
        self.assertEqual(str_day, '20')
        self.assertEqual(str_hour, '0000')

    def test_files_temp_ajacent(self):

        file_t0 = '/data/test_data/tamsat-rfe/3.0/TAMSAT-Africa-4km/tif/10d/20190101_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'
        file_t1 = '/data/test_data/tamsat-rfe/3.0/TAMSAT-Africa-4km/tif/10d/20190111_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'

        adjacent_file_list = functions.files_temp_ajacent(file_t0)
        self.assertEqual(adjacent_file_list[0],file_t1)

    def test_previous_files(self):

        file_t0 = '/data/test_data/tamsat-rfe/3.0/TAMSAT-Africa-4km/tif/10d/20190101_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'
        file_t1 = '/data/test_data/tamsat-rfe/3.0/TAMSAT-Africa-4km/tif/10d/20190111_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'

        previous_file_list = functions.previous_files(file_t1)
        self.assertEqual(previous_file_list[0],file_t0)

    def test_get_eumetcast_info(self):
        # TODO: REMOVE function?  NOT used anywhere in the code!
        eumetcast_id = 'EO/EUM/DAT/MSG/RFE'
        result = functions.get_eumetcast_info(eumetcast_id)
        self.assertEqual(result, None)

    def test_get_machine_mac_address(self):
        machine_mac_address = functions.get_machine_mac_address()
        self.assertIsInstance(machine_mac_address, str)

    def test_get_modified_time_from_file(self):
        file_path = self.src_file
        modified_time_sec = functions.get_modified_time_from_file(file_path)
        self.assertIsInstance(modified_time_sec, float)

    @unittest.skip("Remove function? NOT used anywhere in the code and function is incomplete!")
    def test_get_modis_tiles_list(self):
        # TODO: Remove function? NOT used anywhere in the code and function is incomplete!
        mapset = ''
        tiles_list = functions.get_modis_tiles_list(mapset)

    def test_get_product_type_from_subdir(self):
        subdir = 'vgt-ndvi/spot-v1/WGS84-Africa-1km/tif/ndv)'
        product_type = functions.get_product_type_from_subdir(subdir)
        self.assertEqual(product_type, 'Ingest')

    @unittest.skipUnless(sys.platform.startswith("win"), "Requires Windows!")
    def test_getStatusAllServicesWin(self):
        # TODO: Finish test on the windows version!
        services_status = functions.getStatusAllServicesWin()
        # self.assertIsInstance(services_status, list)

    def test_getStatusPostgreSQL(self):
        postgres_status = functions.getStatusPostgreSQL()
        self.assertIsInstance(postgres_status, bool)

    def test_getSystemSettings(self):
        # systemsettings = functions.getSystemSettings()
        result = False
        if 'type_installation' in systemsettings.keys():
            result = True
        self.assertIsInstance(systemsettings, dict)
        self.assertTrue(result)

    def test_getUserSettings(self):
        usersettings = functions.getUserSettings()
        result = False
        if 'host' in usersettings.keys():
            result = True
        self.assertIsInstance(usersettings, dict)
        self.assertTrue(result)

    def test_getJRCRefSettings(self):
        jrc_ref_ettings = functions.getJRCRefSettings()
        result = False
        if 'version' in jrc_ref_ettings.keys():
            result = True
        self.assertIsInstance(jrc_ref_ettings, dict)
        self.assertTrue(result)

    def test_setJRCRefSetting(self):
        setting = 'update'
        value = 'false'
        result = functions.setJRCRefSetting(setting, value)
        self.assertTrue(result)
        jrc_refsettings = functions.getJRCRefSettings()
        if 'update' in jrc_refsettings.keys():
            self.assertEqual(jrc_refsettings[setting], value)
        else:
            self.assertTrue(False)

    def test_is_data_captured_during_day(self):
        in_date = '20180428T163216'
        day_data = functions.is_data_captured_during_day(in_date)
        self.assertTrue(day_data)

    def test_is_date_current_month(self):
        today = datetime.date.today()
        YYYYMM = today.strftime('%Y%m')
        year_month_day = str(YYYYMM)[0:4] + str(YYYYMM)[4:6] + '01'
        current_month = functions.is_date_current_month(year_month_day)
        self.assertTrue(current_month)

    def test_is_file_exists_in_path(self):
        file_path = '/data/test_data/tamsat-rfe/3.0/TAMSAT-Africa-4km/tif/10d/20190101_tamsat-rfe_10d_TAMSAT-Africa-4km_3.0.tif'
        is_file_exists = functions.is_file_exists_in_path(file_path)
        self.assertTrue(is_file_exists)

    def test_is_float(self):
        floatvar = '2020.2001'
        result = functions.str_is_float(floatvar)
        self.assertTrue(result)
        floatvar = ''
        result = functions.str_is_float(floatvar)
        self.assertFalse(result)

    def test_is_int(self):
        floatvar = '2020'
        result = functions.str_is_int(floatvar)
        self.assertTrue(result)
        floatvar = ''
        result = functions.str_is_int(floatvar)
        self.assertFalse(result)

    def test_is_S3_OL_data_captured_during_day(self):
        filename = 'S3A_OL_2_WRR____20180428T163216_20180428T171635_20180428T191407_2659_030_297______MAR_O_NR_002'
        result = functions.is_S3_OL_data_captured_during_day(filename)
        self.assertTrue(result)
        filename = 'S3A_OL_2_WRR____20180428T013216_20180428T171635_20180428T191407_2659_030_297______MAR_O_NR_002'
        result = functions.is_S3_OL_data_captured_during_day(filename)
        self.assertFalse(result)

    def test_isValidRGB(self):
        rgb = '250 250 250'
        result = functions.isValidRGB(rgb)
        self.assertTrue(result)
        rgb = '250, 250, 250'
        result = functions.isValidRGB(rgb)
        self.assertFalse(result)

    def test_list_to_element(self):
        input_list = [1, 2, 3, 4]
        result = functions.list_to_element(input_list)
        self.assertEqual(result, 1)
        input_tuple = (1, 2, 3, 4)
        result = functions.list_to_element(input_tuple)
        self.assertEqual(result, 1)

    def test_dump_obj_to_pickle(self):
        # logger.info('Pickle filename is: %s', self.processed_info_filename)
        functions.dump_obj_to_pickle(self.processed_info, self.processed_info_filename)
        result = functions.load_obj_from_pickle(self.processed_info_filename)
        self.assertEqual(result, self.processed_info)

    def test_load_obj_from_pickle(self):
        functions.dump_obj_to_pickle(self.processed_info, self.processed_info_filename)
        result = functions.load_obj_from_pickle(self.processed_info_filename)
        self.assertEqual(result, self.processed_info)

    def test_restore_obj_from_pickle(self):
        functions.dump_obj_to_pickle(self.processed_info, self.processed_info_filename)
        result = functions.restore_obj_from_pickle(self.processed_info, self.processed_info_filename)
        self.assertEqual(result, self.processed_info)

    def test_modis_latlon_to_hv_tile(self):
        # TODO: REMOVE function?  NOT used anywhere in the code!
        lat = 20
        long = 20
        [h1, v1] = functions.modis_latlon_to_hv_tile(lat, long)
        self.assertEqual(h1, 19)
        self.assertEqual(v1, 6)

    def test_ProcLists(self):
        # Create 'manually' an empty proc_list (normally done by pipeline)
        proc_lists = functions.ProcLists()
        self.assertEqual(type(proc_lists).__name__,'ProcLists')

    def test_rgb2html(self):
        rgb = [250, 250, 250]
        hexhtml = functions.rgb2html(rgb)
        self.assertEqual(hexhtml, '#fafafa')

    def test_row2dict(self):
        categories_dict_all = []
        categories = querydb.get_categories(allrecs=True)

        if hasattr(categories, "__len__") and categories.__len__() > 0:
            for row in categories:
                row_dict = functions.row2dict(row)
                self.assertIsInstance(row_dict, dict)
                categories_dict = {'category_id': row_dict['category_id'],
                                   'descriptive_name': row_dict['descriptive_name']}
                categories_dict_all.append(categories_dict)
            self.assertEqual(len(categories_dict_all), 8)

    @unittest.skip("Remove function? NOT used anywhere in the code!")
    def test_sentinel_get_footprint(self):
        # TODO: REMOVE function?  NOT used anywhere in the code!
        # TODO: TEST DATA NEEDED
        datadir = ''
        functions.sentinel_get_footprint(datadir)
        self.assertFalse(True)  # Test fails for now!

    def test_set_path_filename_no_date(self):
        params = {
            'productcode': 'vgt-ndvi',
            'subproductcode': 'ndvi-linearx2',
            'version': 'sv2-pv2.2',
            'mapsetcode': 'SPOTV-Africa-1km'
        }
        filename_nodate = functions.set_path_filename_no_date(params['productcode'],
                                                              params['subproductcode'],
                                                              params['version'],
                                                              params['mapsetcode'], '.tif')
        self.assertEqual(filename_nodate, '_vgt-ndvi_ndvi-linearx2_sv2-pv2.2_SPOTV-Africa-1km.tif')

    def test_setSystemSetting(self):
        setting = 'ingest_archive_eum'
        value = 'true'
        result = functions.setSystemSetting(setting, value)
        self.assertTrue(result)
        systemsettings = functions.getSystemSettings()
        if 'ingest_archive_eum' in systemsettings.keys():
            self.assertEqual(systemsettings['ingest_archive_eum'], 'true')
        else:
            self.assertTrue(False)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_setThemaOtherPC(self):
        server_address = 'mesa-pc3'
        thema = 'JRC'
        thema_is_changed = functions.setThemaOtherPC(server_address, thema)
        self.assertTrue(thema_is_changed)  # Test fails on non MESA station!

    def test_setUserSetting(self):
        setting = 'log_general_level'
        value = 'DEBUG'
        result = functions.setUserSetting(setting, value)
        self.assertTrue(result)
        usersettings = functions.getUserSettings()
        if 'log_general_level' in usersettings.keys():
            self.assertEqual(usersettings['log_general_level'], 'DEBUG')
        else:
            self.assertTrue(False)

    def test_str_to_bool(self):
        string_to_convert = 'yes'
        self.assertTrue(functions.str_to_bool(string_to_convert))
        string_to_convert = 'no'
        self.assertFalse(functions.str_to_bool(string_to_convert))

    @unittest.skip("Remove function? NOT used anywhere in the code and does not make any sense!")
    def test_system_status_filename(self):
        # TODO: REMOVE function?  NOT used anywhere in the code and does not make any sense!
        result = functions.system_status_filename()
        self.assertIsInstance(result, str)  # Fails: es_constants.es2globals['status_system_pickle'] not present!

    def test_tojson(self):
        categories = querydb.get_categories(allrecs=True)
        if hasattr(categories, "__len__") and categories.__len__() > 0:
            categories_json = functions.tojson(categories)
            self.assertIsNot(categories_json.find('category_id'), -1)
        else:
            self.assertFalse(True)  # Fails because there are no categories defined in the database!

    def test_unix_time(self):
        date_to_convert = date.today()
        dt = datetime.datetime.combine(date_to_convert, datetime.time.min)
        result = functions.unix_time(dt)
        self.assertIsInstance(result, float)

    def test_unix_time_millis(self):
        date_to_convert = date.today()
        result = functions.unix_time_millis(date_to_convert)
        self.assertIsInstance(result, float)

    def test_write_graph_xml_reproject(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        nodata_value = -99999
        functions.write_graph_xml_reproject(output_dir, nodata_value)
        file_xml = output_dir + os.path.sep + 'graph_xml_reproject.xml'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_write_graph_xml_subset(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        bandname = 'TEST'
        if not os.path.exists(output_dir + os.path.sep + bandname):
            os.mkdir(output_dir + os.path.sep + bandname)
        input_file = 'inputfilename'
        functions.write_graph_xml_subset(input_file, output_dir, bandname)
        file_xml = output_dir + os.path.sep + bandname + os.path.sep + 'graph_xml_subset.xml'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_write_graph_xml_terrain_correction_oilspill(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        bandname = 'TEST'
        if not os.path.exists(output_dir + os.path.sep + bandname):
            os.mkdir(output_dir + os.path.sep + bandname)
        input_file = 'inputfilename'
        output_file = 'outputfilename'
        functions.write_graph_xml_terrain_correction_oilspill(output_dir, input_file, bandname, output_file)
        file_xml = output_dir + os.path.sep + bandname + os.path.sep + 'graph_xml_terrain_correction_oilspill.xml'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_write_graph_xml_wd_gee(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        bandname = 'TEST'
        if not os.path.exists(output_dir + os.path.sep + bandname):
            os.mkdir(output_dir + os.path.sep + bandname)
        input_file = 'inputfilename'
        output_file = 'outputfilename'
        functions.write_graph_xml_wd_gee(output_dir, input_file, bandname, output_file)
        file_xml = output_dir + os.path.sep + bandname + os.path.sep + 'graph_xml_wd_gee.xml'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_write_vrt_georef(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        band_file = 'band_file'
        functions.write_vrt_georef(output_dir, band_file, n_lines=None, n_cols=None, lat_file=None, long_file=None)
        file_xml = output_dir + os.path.sep + 'reflectance.vrt'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_write_graph_xml_band_math_subset(self):
        output_dir = '/tmp/tests'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        bandname = 'TEST'
        if not os.path.exists(output_dir + os.path.sep + bandname):
            os.mkdir(output_dir + os.path.sep + bandname)
        expression = 'expression'
        functions.write_graph_xml_band_math_subset(output_dir, bandname, expression)
        file_xml = output_dir + os.path.sep + bandname + os.path.sep + 'graph_xml_subset.xml'
        if os.path.exists(file_xml):
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_check_connection(self):
        # mesaproc = "139.191.147.79:22"
        # mesaproc = 'mesa-proc.ies.jrc.it'
        google = 'www.google.com'
        result = functions.check_connection(google)
        self.assertTrue(result)

    def test_get_remote_system_status(self):
        # server_address = '10.191.231.90'  # vm19
        # server_address = "h05-dev-vm19.ies.jrc.it"
        server_address = 'estation.jrc.ec.europa.eu/eStation2/'
        status_remote_machine = functions.get_remote_system_status(server_address)
        if "mode" in status_remote_machine:
            PC2_mode = status_remote_machine['mode']
            PC2_disk_status = status_remote_machine['disk_status']
            PC2_version = status_remote_machine['active_version']
            PC2_postgresql_status = status_remote_machine['postgresql_status']
            PC2_internet_status = status_remote_machine['internet_connection_status']
            PC2_service_eumetcast = status_remote_machine['get_eumetcast_status']
            PC2_service_internet = status_remote_machine['get_internet_status']
            PC2_service_ingest = status_remote_machine['ingestion_status']
            PC2_service_processing = status_remote_machine['processing_status']
            PC2_service_system = status_remote_machine['system_status']
            PC2_system_execution_time = status_remote_machine['system_execution_time']
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    @unittest.skipIf(install_type != 'full', "Test only on MESA Station - Full install")
    def test_get_status_PC1(self):
        # TODO: Test and finish writing this test on Full station!
        status_PC1 = functions.get_status_PC1()
        self.assertTrue(True)

    @unittest.skipIf(install_type == 'server', "Test only on MESA Station - Full install")
    def test_internet_on(self):
        # TODO: System setting type_installation must NOT be Server!
        status = functions.internet_on()
        self.assertTrue(status)

    def test_save_read_netcdf_scaling(self):

        nc_file = '/data/test_data/modis-sst/native/AQUA_MODIS.20200320.L3m.DAY.SST.sst.4km.NRT.nc'

        sds = 'NETCDF:'+nc_file+':sst'
        status = functions.save_netcdf_scaling(sds, nc_file)
        self.assertFalse(status)  # Test fails for now!

        [fact, off] = functions.read_netcdf_scaling(nc_file)
        self.assertTrue(isinstance(fact,float))
        self.assertTrue(isinstance(off, float))

    def test_getStatusAllServices(self):
        services_status = functions.getStatusAllServices()
        # print(services_status)
        self.assertIsInstance(services_status, dict)

    def test_is_date_yyyymmdd(self):
        self.assertTrue(functions.is_date_yyyymmdd(self.string_yyyymmdd))

    def test_is_date_mmdd(self):
        self.assertTrue(functions.is_date_mmdd(self.string_mmdd))

    def test_is_date_yyyymmddhhmm(self):
        self.assertTrue(functions.is_date_yyyymmddhhmm(self.string_yyyymmddhhmm))

    def test_is_date_yyyydoy(self):
        self.assertTrue(functions.is_date_yyyydoy(self.string_yyyydoy))

    def test_conv_date_2_dekad(self):
        self.assertEqual(functions.conv_date_2_dekad(self.string_yyyymmdd), self.julian_dekad)

    def test_conv_date_2_month(self):
        self.assertEqual(functions.conv_date_2_month(self.string_yyyymmdd), self.julian_month)

    def test_conv_dekad_2_date(self):
        self.assertEqual(functions.conv_dekad_2_date(self.julian_dekad), self.string_yyyymmdd)

    def test_conv_month_2_date(self):
        self.assertEqual(functions.conv_month_2_date(self.julian_month), self.string_yyyymmdd)

    def test_conv_date_yyyydoy_2_yyyymmdd(self):
        self.assertEqual(functions.conv_date_yyyydoy_2_yyyymmdd(self.string_yyyydoy), self.string_yyyymmdd)

    def test_conv_date_yyyymmdd_2_doy(self):
        self.assertEqual(functions.conv_date_yyyymmdd_2_doy(self.string_yyyymmdd), int(self.str_doy))

    def test_conv_yyyy_mm_dkx_2_yyyymmdd(self):
        self.assertEqual(functions.conv_yyyy_mm_dkx_2_yyyymmdd(self.string_yyyy_mm_dkx), self.string_yyyymmdd)

    def test_conv_yymmk_2_yyyymmdd(self):
        self.assertEqual(functions.conv_yymmk_2_yyyymmdd(self.string_yymmk), self.string_yyyymmdd)

    def test_conv_yyyymmdd_g2_2_yyyymmdd(self):
        self.assertEqual(functions.conv_yyyymmdd_g2_2_yyyymmdd('20151103'), '20151101')
        self.assertEqual(functions.conv_yyyymmdd_g2_2_yyyymmdd('20151110'), '20151101')
        self.assertEqual(functions.conv_yyyymmdd_g2_2_yyyymmdd('20151131'), '20151121')
        self.assertEqual(functions.conv_yyyymmdd_g2_2_yyyymmdd('20151105'), '20151101')
        self.assertEqual(functions.conv_yyyymmdd_g2_2_yyyymmdd('20151109'), '20151101')

    def test_conv_date_2_quarter(self):
        self.assertEqual(functions.conv_date_2_quarter('20150123'), '20150101')
        self.assertEqual(functions.conv_date_2_quarter('20150323'), '20150101')

        self.assertEqual(functions.conv_date_2_quarter('20150423'), '20150401')
        self.assertEqual(functions.conv_date_2_quarter('20150629'), '20150401')

        self.assertEqual(functions.conv_date_2_quarter('20150723'), '20150701')
        self.assertEqual(functions.conv_date_2_quarter('20150930'), '20150701')

        self.assertEqual(functions.conv_date_2_quarter('20151029'), '20151001')
        self.assertEqual(functions.conv_date_2_quarter('20151229'), '20151001')

    def test_conv_date_2_8days(self):
        # Non-leap year
        self.assertEqual(functions.conv_date_2_8days('20110101'), 1)
        self.assertEqual(functions.conv_date_2_8days('20110108'), 1)
        self.assertEqual(functions.conv_date_2_8days('20110109'), 2)
        self.assertEqual(functions.conv_date_2_8days('20110225'), 7)
        self.assertEqual(functions.conv_date_2_8days('20110226'), 8)
        self.assertEqual(functions.conv_date_2_8days('20110305'), 8)
        self.assertEqual(functions.conv_date_2_8days('20110306'), 9)

        self.assertEqual(functions.conv_date_2_8days('20111226'), 45)
        self.assertEqual(functions.conv_date_2_8days('20111227'), 46)
        self.assertEqual(functions.conv_date_2_8days('20111231'), 46)

        # Leap year
        self.assertEqual(functions.conv_date_2_8days('20120304'), 8)
        self.assertEqual(functions.conv_date_2_8days('20120305'), 9)
        self.assertEqual(functions.conv_date_2_8days('20121225'), 45)
        self.assertEqual(functions.conv_date_2_8days('20121226'), 46)
        self.assertEqual(functions.conv_date_2_8days('20121231'), 46)

    def test_dekad_nbr_in_season(self):
        start = '0101'
        self.assertEqual(functions.dekad_nbr_in_season('0101', start), 1)
        self.assertEqual(functions.dekad_nbr_in_season('0401', start), 10)
        self.assertEqual(functions.dekad_nbr_in_season('1221', start), 36)

        start = '0901'
        self.assertEqual(functions.dekad_nbr_in_season('0901', start), 1)
        self.assertEqual(functions.dekad_nbr_in_season('1201', start), 10)
        self.assertEqual(functions.dekad_nbr_in_season('0101', start), 13)
        self.assertEqual(functions.dekad_nbr_in_season('0401', start), 22)

    def test_get_number_days_month(self):
        self.assertEqual(functions.get_number_days_month('20180201'), 28)

    def test_day_length(self):
        # TODO: Remove function? This function is not used anywhere in the code!
        day = 31
        latitude = 40.0
        dl = functions.day_length(day, latitude)
        self.assertEqual(dl, 73.63579020749116)

    def test_get_from_path_dir(self):
        [my_product_code, my_sub_product_code, my_version, my_mapset] = functions.get_from_path_dir(self.dir_name)

        self.assertEqual(my_product_code, self.str_prod)
        self.assertEqual(my_sub_product_code, self.str_sprod)
        self.assertEqual(my_mapset, self.str_mapset)
        self.assertEqual(my_version, self.str_version)

    def test_get_date_from_path_filename(self):
        my_date = functions.get_date_from_path_filename(self.filename)

        self.assertEqual(my_date, self.str_date)
        # self.assertEqual(my_mapset,self.str_mapset)

    def test_get_date_from_path_full(self):
        my_date = functions.get_date_from_path_full(self.fullpath)

        self.assertEqual(my_date, self.str_date)

    def test_get_all_from_path_full(self):
        full_path = self.dir_name + self.filename

        my_product_code, my_sub_product_code, my_version, my_date, my_mapset = functions.get_all_from_path_full(
            full_path)

        self.assertEqual(my_product_code, self.str_prod)
        self.assertEqual(my_sub_product_code, self.str_sprod)
        self.assertEqual(my_date, self.str_date)
        self.assertEqual(my_mapset, self.str_mapset)
        self.assertEqual(my_version, self.str_version)

    def test_get_all_from_filename(self):
        # my_full_path = '20151001_lsasaf-et_10daycum_SPOTV-CEMAC-1km_undefined.tif'
        my_date, my_product_code, my_sub_product_code, my_mapset, my_version = functions.get_all_from_filename(
            self.fullpath)

        self.assertEqual(my_product_code, self.str_prod)
        self.assertEqual(my_sub_product_code, self.str_sprod)
        self.assertEqual(my_date, self.str_date)
        self.assertEqual(my_mapset, self.str_mapset)
        self.assertEqual(my_version, self.str_version)

        [str_date, product_code, sub_product_code, mapset, version] = functions.get_all_from_filename(self.filename)

        self.assertEqual(str_date, self.str_date)
        self.assertEqual(product_code, self.str_prod)
        self.assertEqual(sub_product_code, self.str_sprod)
        self.assertEqual(mapset, self.str_mapset)
        self.assertEqual(version, self.str_version)

    def test_get_subdir_from_path_full(self):
        full_path = self.dir_name + self.filename

        my_subdir = functions.get_subdir_from_path_full(full_path)

        self.assertEqual(my_subdir, self.sub_dir)

    def test_set_path_filename(self):
        my_filename = functions.set_path_filename(self.str_date, self.str_prod, self.str_sprod,
                                                  self.str_mapset, self.str_version, self.str_extension)

        logger.info('Filename is: %s' % my_filename)
        self.assertEqual(self.filename, my_filename)

    def test_set_path_filename_eumetcast(self):
        my_filename = functions.set_path_filename_eumetcast(self.str_date, self.str_prod, self.str_sprod,
                                                            self.str_mapset, self.str_version, self.str_extension)

        logger.info('Filename is: %s' % my_filename)
        self.assertEqual(self.filename_eumetcast, my_filename)

    def test_set_path_sub_directory(self):
        my_sub_directory = functions.set_path_sub_directory(self.str_prod, self.str_sprod, self.product_type,
                                                            self.str_version, self.str_mapset)
        logger.info('Subdirectory is: %s' % my_sub_directory)

        self.assertEqual(self.sub_dir, my_sub_directory)

    def test_getListVersions(self):
        versions = functions.getListVersions()
        print(versions)

    def test_get_all_from_filename_eumetcast(self):
        [str_date, product_code, sub_product_code, mapset, version] = functions.get_all_from_filename_eumetcast(
            self.filename_eumetcast)

        self.assertEqual(str_date, self.str_date)
        self.assertEqual(product_code, self.str_prod)
        self.assertEqual(sub_product_code, self.str_sprod)
        self.assertEqual(mapset, self.str_mapset)
        self.assertEqual(version, self.str_version)

    def test_convert_name_to_eumetcast(self):
        filename_eumetcast = functions.convert_name_to_eumetcast(self.filename)

        self.assertEqual(self.filename_eumetcast, filename_eumetcast)

    def test_convert_name_from_eumetcast(self):
        filename = functions.convert_name_from_eumetcast(self.filename_eumetcast, self.product_type)
        self.assertEqual(self.filename, filename)

        fullpath = functions.convert_name_from_eumetcast(self.filename_eumetcast, self.product_type, with_dir=True)
        self.assertEqual(self.sub_dir+filename, fullpath)


suite_functions = unittest.TestLoader().loadTestsFromTestCase(TestFunctions)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_functions)
