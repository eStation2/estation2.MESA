from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
from builtins import int

import os
import shutil
import datetime
import unittest

import lib.python.functions as functions
from lib.python import es_logging as log
from config import es_constants

logger = log.my_logger(__name__)
standard_library.install_aliases()


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

    def test_check_output_dir(self):
        output_dir = '/tmp/eStation2'
        self.assertTrue(functions.check_output_dir(output_dir))

    def test_check_polygons_intersects(self):
        poly1 = []
        poly2 = []
        self.assertTrue(functions.check_polygons_intersects(poly1, poly2))

    def test_checkDateFormat(self):
        myString = '05061967'
        self.assertTrue(functions.checkDateFormat(myString))

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
        testdir = '/data/processing/test/'
        if not os.path.isdir(testdir):
            os.mkdir(testdir, 777)

        src_file = '/data/processing/vgt-dmp/V2.0/SPOTV-Africa-1km/tif/dmp/20181201_vgt-dmp_dmp_SPOTV-Africa-1km_V2.0.tif'
        fake_file = '/data/processing/vgt-dmp/V2.0/SPOTV-Africa-1km/tif/dmp/fakefile.tif'
        trg_file = testdir + '20181201_vgt-dmp_dmp_SPOTV-Africa-1km_V2.0.tif'

        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=False), 0)  # SYM LINK CREATED
        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=False), 1)  # SYM LINK ALREADY CREATED
        self.assertEqual(functions.create_sym_link(src_file, trg_file, force=True), 0)   # SYM LINK RECREATED
        self.assertEqual(functions.create_sym_link(fake_file, trg_file, force=True), 1)  # SOURCE FILE DOES'T EXIST

        # CLEANUP
        # os.rmdir(testdir)
        shutil.rmtree(testdir)

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
        # myvar = functions.element_to_list(input_list)
        self.assertIsInstance(functions.element_to_list(input_list), list)
        input_tuple = (1, 2, 3, 4)
        # myvar = functions.element_to_list(input_tuple)
        self.assertIsInstance(functions.element_to_list(input_tuple), list)

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
        functions.exclude_current_year()

    def test_extract_from_date(self):
        functions.extract_from_date()

    def test_files_temp_ajacent(self):
        functions.files_temp_ajacent()

    def test_get_eumetcast_info(self):
        functions.get_eumetcast_info()

    def test_get_machine_mac_address(self):
        functions.get_machine_mac_address()

    def test_get_modified_time_from_file(self):
        functions.get_modified_time_from_file()

    def test_get_modis_tiles_list(self):
        functions.get_modis_tiles_list()

    def test_get_product_type_from_subdir(self):
        functions.get_product_type_from_subdir()

    def test_getStatusAllServicesWin(self):
        functions.getStatusAllServicesWin()

    def test_getStatusPostgreSQL(self):
        functions.getStatusPostgreSQL()

    def test_getSystemSettings(self):
        functions.getSystemSettings()

    def test_getUserSettings(self):
        functions.getUserSettings()

    def test_is_data_captured_during_day(self):
        functions.is_data_captured_during_day()

    def test_is_date_current_month(self):
        functions.is_date_current_month()

    def test_is_file_exists_in_path(self):
        functions.is_file_exists_in_path()

    def test_is_float(self):
        functions.is_float()

    def test_is_int(self):
        functions.is_int()

    def test_is_S3_OL_data_captured_during_day(self):
        functions.is_S3_OL_data_captured_during_day()

    def test_isValidRGB(self):
        functions.isValidRGB()

    def test_list_to_element(self):
        functions.list_to_element()

    def test_load_obj_from_pickle(self):
        functions.load_obj_from_pickle()

    def test_modis_latlon_to_hv_tile(self):
        functions.modis_latlon_to_hv_tile()

    def test_previous_files(self):
        functions.previous_files()

    def test_ProcLists(self):
        functions.ProcLists()

    def test_ProcSubprod(self):
        functions.ProcSubprod()

    def test_ProcSubprodGroup(self):
        functions.ProcSubprodGroup()

    def test_restore_obj_from_pickle(self):
        functions.restore_obj_from_pickle()

    def test_rgb2html(self):
        functions.rgb2html()

    def test_row2dict(self):
        functions.row2dict()

    def test_sentinel_get_footprint(self):
        functions.sentinel_get_footprint()

    def test_set_path_filename_no_date(self):
        functions.set_path_filename_no_date()

    def test_setSystemSetting(self):
        functions.setSystemSetting()

    def test_setThemaOtherPC(self):
        functions.setThemaOtherPC()

    def test_setUserSetting(self):
        functions.setUserSetting()

    def test_str_to_bool(self):
        functions.str_to_bool()

    def test_system_status_filename(self):
        functions.system_status_filename()

    def test_tojson(self):
        functions.tojson()

    def test_unix_time(self):
        functions.unix_time()

    def test_unix_time_millis(self):
        functions.unix_time_millis()

    def test_write_graph_xml_reproject(self):
        functions.write_graph_xml_reproject()

    def test_write_graph_xml_subset(self):
        functions.write_graph_xml_subset()

    def test_write_graph_xml_terrain_correction_oilspill(self):
        functions.write_graph_xml_terrain_correction_oilspill()

    def test_write_graph_xml_wd_gee(self):
        functions.write_graph_xml_wd_gee()

    def test_write_vrt_georef(self):
        functions.write_vrt_georef()

    def test_dump_obj_to_pickle(self):
        logger.info('Pickle filename is: %s', self.processed_info_filename)
        myvar = functions.dump_obj_to_pickle(self.processed_info, self.processed_info_filename)
        print(myvar)

    def test_write_graph_xml_band_math_subset(self):
        param = ''
        self.assertTrue(functions.write_graph_xml_band_math_subset(param))

    def test_check_connection(self):
        mesaproc = "139.191.147.79:22"
        mesaproc = 'mesa-proc.ies.jrc.it'
        self.assertTrue(functions.check_connection(mesaproc))
        pc3 = "192.168.0.15:22"
        pc3 = "h05-dev-vm19.ies.jrc.it"
        self.assertTrue(functions.check_connection(pc3))

    def test_get_remote_system_status(self):
        server_address = '10.191.231.90'  # vm19
        server_address = "h05-dev-vm19.ies.jrc.it"
        status_remote_machine = functions.get_remote_system_status(server_address)
        print(status_remote_machine)
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

        print("Done")

    def test_get_status_PC1(self):
        status_PC1 = functions.get_status_PC1()
        print(status_PC1)

    def test_internet_on(self):
        status = functions.internet_on()
        print(status)

    def test_save_netcdf_scaling(self):
        preproc_file = '/tmp/eStation2/apps.acquisition.ingestion4Losxu_A2016201.L3m_DAY_SST_sst_4km.nc/A2016201.L3m_DAY_SST_sst_4km.nc.geotiff'
        sds = 'NETCDF:/data/ingest/A2016201.L3m_DAY_SST_sst_4km.nc:sst'
        status = functions.save_netcdf_scaling(sds, preproc_file)
        print(status)

    def test_read_netcdf_scaling(self):
        preproc_file = '/tmp/eStation2/apps.acquisition.ingestion4Losxu_A2016201.L3m_DAY_SST_sst_4km.nc/A2016201.L3m_DAY_SST_sst_4km.nc.geotiff'
        [fact, off] = functions.read_netcdf_scaling(preproc_file)
        print((fact, off))

    def test_getStatusAllServices(self):
        services_status = functions.getStatusAllServices()
        print(services_status)

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
        day = 31
        latitude = 40.0
        dl = functions.day_length(day, latitude)
        print('Day lenght is: {0}'.format(dl))

    #   -----------------------------------------------------------------------------------
    #   Extract info from dir/filename/fullpath

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
        my_full_path = '20151001_lsasaf-et_10daycum_SPOTV-CEMAC-1km_undefined.tif'
        my_date, my_product_code, my_sub_product_code, my_mapset, my_version = functions.get_all_from_filename(
            my_full_path)

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

    #   -----------------------------------------------------------------------------------
    #   Compose dir/filename/fullpath from attributes

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

        self.assertEqual(self.filename, filename)


suite_functions = unittest.TestLoader().loadTestsFromTestCase(TestFunctions)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_functions)
