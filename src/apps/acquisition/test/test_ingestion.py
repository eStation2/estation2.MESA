from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
_author__ = "Marco Clerici"


from config import es_constants
from apps.acquisition import ingestion
from database import querydb
import unittest
import os
import glob
import tempfile
import shutil
import csv
import numpy as np
# import h5py
from lib.python import functions
from lib.python import metadata as md
from lib.python.image_proc import raster_image_math

from osgeo import gdal

# Overwrite Dirs
from lib.python import es_logging as log

logger = log.my_logger(__name__)


class TestIngestion(unittest.TestCase):

    def setUp(self):
        root_test_dir = es_constants.es2globals['test_data_dir']
        self.test_ingest_dir = root_test_dir  # os.path.join(root_test_dir,'native')
        self.proc_dir_bck = es_constants.processing_dir
        es_constants.processing_dir = es_constants.es2globals['base_tmp_dir'] + os.path.sep
        self.ingest_out_dir = es_constants.processing_dir
        self.ref_out_dir = root_test_dir  # os.path.join(root_test_dir,'refs_output')
        self.native_dir = 'native'

    def tearDown(self):
        es_constants.processing_dir = self.proc_dir_bck

    def checkIngestedFile(self, productcode='', subproductcode='', version='', mapsetcode='', date='', fast=False):
        # Given the all files keys (date, prod, sprod, ...) finds out:
        # -> the product just ingested in the tmp_dir (see setUp)
        # -> the product in refs_output
        # Assess if the products are equal/equivalent

        result = 0
        filename = functions.set_path_filename(date, productcode, subproductcode, mapsetcode, version, '.tif')
        sub_directory = functions.set_path_sub_directory(productcode, subproductcode, 'Ingest', version, mapsetcode)

        ref_file = glob.glob(self.ref_out_dir + '**/*/*/' + filename, recursive=True)
        if not len(ref_file) > 0:  # os.path.isfile(ref_file[0]):
            print("Error reference file does not exist: " + filename)
            return result
        newly_computed_file = glob.glob(self.ingest_out_dir + sub_directory + filename, recursive=True)
        if not len(newly_computed_file) > 0:  # os.path.isfile(newly_computed_file[0]):
            print("Error reference file does not exist: " + filename)
            return result

        # Compare the files by using gdal_info objects
        if len(ref_file) > 0 and len(newly_computed_file) > 0 and os.path.exists(ref_file[0]) and os.path.exists(
                newly_computed_file[0]):
            gdal_info_ref = md.GdalInfo()
            gdal_info_ref.get_gdalinfo(ref_file[0])
            gdal_info_new = md.GdalInfo()
            gdal_info_new.get_gdalinfo(newly_computed_file[0])
            equal = gdal_info_new.compare_gdalinfo(gdal_info_ref)

            if not equal:
                print("Warning: the files metadata are different")
            # Check the raster array compare
            array_equal = raster_image_math.compare_two_raster_array(ref_file[0], newly_computed_file[0], fast=fast)
            if not array_equal:
                print("Warning: the files contents are different")

            if array_equal is True:
                result = 1

        return result

    def remove_output_file(self, productcode, subproductcode, version, mapset_id, out_date):
        # Define output directory and make sure it exists
        output_directory = self.ingest_out_dir + functions.set_path_sub_directory(productcode,
                                                                                  subproductcode,
                                                                                  'Ingest',
                                                                                  version,
                                                                                  mapset_id)

        # Define output filename
        output_filename = output_directory + functions.set_path_filename(out_date,
                                                                         productcode,
                                                                         subproductcode,
                                                                         mapset_id,
                                                                         version,
                                                                         '.tif')

        try:
            if os.path.exists(output_filename):
                os.remove(output_filename)
        except:
            # my_logger.error('Cannot create output directory: ' + output_directory)
            return 1

    # Commented -> not relevant here
    # def TestDriveAll(self):
    #     dry_run = True
    #     ingestion.loop_ingestion(dry_run=dry_run)
    #     self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - WSI CROP/PASTURE //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 2m 31s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_mars_wsi(self):
        productcode = 'wsi-hp'
        productversion = 'V1.0'
        subproductcode = 'pasture'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'JRC:MARS:WSI:PASTURE'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'wsi_hp_pasture_20200221.img'),
                          os.path.join(input_dir, 'wsi_hp_pasture_20200221.hdr')]

        in_date = '20200221'
        out_date = '20200221'

        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]

        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - DMP V2.0.1 //Ok 30-04-2020 Vijay// - 3m 7s
    #   Tested ok (metadata diff) 4.5.20 -> 3m 7s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_dmp_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for DMP)
        # Products released from VITO in March 2017
        productcode = 'vgt-dmp'
        productversion = 'V2.0'
        subproductcode = 'dmp'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'PDF:GLS:PROBA-V2.0:DMP_RT0'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'c_gls_DMP-RT0_202003200000_GLOBE_PROBAV_V2.0.1.nc')]

        in_date = '20200320'
        out_date = '20200311'
        product = {"productcode": productcode,
                   "version": productversion}

        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FAPAR V2.0.1 AFRI (EumetCast source)
    #   Tested ok (metadata diff) 4.5.20 -> 35s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_fapar_afri_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for FAPAR)
        # Products released from VITO in March 2017
        productcode = 'vgt-fapar'
        productversion = 'V2.0'
        subproductcode = 'fapar'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'EO:EUM:DAT:PROBA-V2.0:FAPAR'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'c_gls_FAPAR-RT0_202004100000_AFRI_PROBAV_V2.0.1.zip')]

        in_date = '202004010000'
        out_date = '20200401'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FAPAR V2.0.1 Global (Internet source)//Ok 30-04-2020 Vijay//
    #   Tested ok (metadata diff) 4.5.20 -> 2m 2s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_fapar_global_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for FAPAR)
        # Products released from VITO in March 2017
        productcode = 'vgt-fapar'
        productversion = 'V2.0'
        subproductcode = 'fapar'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'PDF:GLS:PROBA-V2.0:FAPAR'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'c_gls_FAPAR-RT0_202003310000_GLOBE_PROBAV_V2.0.1.nc')]
        in_date = '202003310000'
        out_date = '20200321'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.2.1 //Ok 30-04-2020 Vijay//
    #   Tested ok (metadata diff) 24.6.20 -> 25s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_2_2(self):

        # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
        productcode = 'vgt-ndvi'
        productversion = 'proba-v2.2'
        subproductcode = 'ndv'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'EO:EUM:DAT:PROBA-V2.2:NDVI'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'c_gls_NDVI_202003010000_AFRI_PROBAV_V2.2.1.zip')]
        # date_fileslist = glob.glob('/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.zip*')
        in_date = '202003010000'
        out_date = '20200301'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI 300m
    #   Tested ok 4.5.20 - 5m 47s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_probav_ndvi_300(self):

        productcode = 'vgt-ndvi'
        productversion = 'proba300-v1.0'
        subproductcode = 'ndv'
        mapsetcode = 'SENTINEL-Africa-300m'
        datasource_descrID = 'PDF:VITO:PROBA-V1:NDVI300'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        # date_fileslist = [os.path.join(self.test_ingest_dir,'PROBAV_S10_TOC_*20200201**')]
        date_fileslist = glob.glob(input_dir + '/PROBAV_S10_TOC_*20200201**')
        in_date = '20200201'
        out_date = '20200201'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        nodata = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': nodata}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - ARC2 //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 1.7s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_arc2_rain(self):
        productcode = 'arc2-rain'
        productversion = '2.0'
        subproductcode = '1day'
        mapsetcode = 'ARC2-Africa-11km'
        datasource_descrID = 'CPC:NOAA:RAIN:ARC2'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'africa_arc.20200318.tif.zip')]
        # date_fileslist = glob.glob('/data/ingest/africa_arc.20200318.tif.zip')
        in_date = '20200318'
        out_date = '20200318'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - CHIRPS  //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 5.3s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_chirps(self):
        productcode = 'chirps-dekad'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'CHIRP-Africa-5km'
        datasource_descrID = 'UCSB:CHIRPS:DEKAD:2.0'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'chirps-v2.0.2020.02.3.tif.gz')]
        # date_fileslist = ['/data/ingest/chirps-v2.0.2020.02.3.tif.gz']
        in_date = '2020.02.3'
        out_date = '20200221'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - CHIRPS TIF //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 9.37s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_chirps_tif(self):
        productcode = 'chirps-dekad'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'CHIRP-Africa-5km'
        datasource_descrID = 'UCSB:CHIRPS:PREL:DEKAD'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'chirps-v2.0.2020.03.1.tif')]
        # date_fileslist = ['/data/ingest/chirps-v2.0.2020.03.1.tif']
        in_date = '2020.03.1'
        out_date = '20200301'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - Fewsnet 2  //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 2.48s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_fewsnet_rfe(self):
        productcode = 'fewsnet-rfe'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'FEWSNET-Africa-8km'
        datasource_descrID = 'USGS:EARLWRN:FEWSNET'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
        date_fileslist = [os.path.join(input_dir, 'a20013rb.zip')]
        # date_fileslist = glob.glob('/data/ingest/a20013rb.zip')
        in_date = '20013'
        out_date = '20200121'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - TAMSAT 3  //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 3.9s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_tamsat_rfe(self):
        productcode = 'tamsat-rfe'
        productversion = '3.0'
        subproductcode = '10d'
        mapsetcode = 'TAMSAT-Africa-4km'
        datasource_descrID = 'READINGS:TAMSAT:3.0:10D:NC'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'rfe2020_01-dk3.v3.nc')]
        # date_fileslist = glob.glob('/data/ingest/rfe2020_01-dk3.v3.nc')
        in_date = '2020_01-dk3'
        out_date = '20200121'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   FIRE - MODIS FIRMS 6  //Ok 30-04-2020 Vijay//
    #   Tested ok 4.5.20 -> 1m 7s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_firms(self):
        productcode = 'modis-firms'
        productversion = 'v6.0'
        subproductcode = '1day'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'MODAPS:EOSDIS:FIRMS:NASA:HTTP'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'MODIS_C6_Global_MCD14DL_NRT_2020020.txt')]
        # date_fileslist = glob.glob('/data/ingest/MODIS_C6_Global_MCD14DL_NRT_2020020.txt')
        in_date = '2020020'
        out_date = '20200120'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   FIRE - PROBA BA 300
    #   Tested ok 8.5.2020  -> 8m 40s for Check alone (40k*30k pixels) PyCh
    #                       -> 22s for Check with 'fast' procedure
    #                       -> 6m 8s for Ingestion + Check-fast
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ba_300m_global(self):
        # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
        # Products released from VITO in March 2017
        # date_fileslist = glob.glob('/data/ingest/c_gls_BA300_202003100000_GLOBE_PROBAV_V1.1.1.nc')
        productcode = 'vgt-ba'
        productversion = 'V1.1'
        subproductcode = 'ba'
        mapsetcode = 'SENTINEL-Africa-300m'
        datasource_descrID = 'PDF:GLS:PROBA-V1.1:BA300'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'c_gls_BA300_202003100000_GLOBE_PROBAV_V1.1.1.nc')]
        # for one_file in date_fileslist:

        one_filename = os.path.basename(date_fileslist[0])
        in_date = '20200310'
        out_date = '20200301'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': product_in_info.no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist[0], in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date,
                                        fast=True)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   OCEANOGRAPHY - MODIS CHLA //Ok 30-04-2020 Vijay//
    #   Tested ok 5.5.20 ->  13s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_chlor_netcdf(self):
        productcode = 'modis-chla'
        productversion = 'v2013.1'
        subproductcode = 'chla-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID = 'GSFC:CGI:MODIS:CHLA:1D'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'A2020078.L3m_DAY_CHL_chlor_a_4km.nc')]
        # date_fileslist = ['/data/ingest/A2020078.L3m_DAY_CHL_chlor_a_4km.nc']
        in_date = '2020078'
        out_date = '20200318'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   OCEANOGRAPHY - MODIS SST  //Ok 30-04-2020 Vijay//
    #   Tested ok 5.5.20 ->  7s PyCh - the warning below is raised (TBC)
    #   ---------------------------------------------------------------------------
    #   web          | /opt/project/src/apps/acquisition/ingestion.py:3535:
    #       -> ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/eStation2/apps.acquisition.ingestiond0mdd_10_AQUA_MODIS.20200320.L3m.DAY.SST.sst.4km.NRT.nc/scaling.txt' mode='r' encoding='UTF-8'>
    #   [in_scale_factor, in_offset] = functions.read_netcdf_scaling(intermFile)
    #   ResourceWarning: Enable tracemalloc to get the object allocation traceback
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_sst_netcdf(self):
        productcode = 'modis-sst'
        productversion = 'v2013.1'
        subproductcode = 'sst-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID = 'GSFC:CGI:MODIS:SST:1D:NEW'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'AQUA_MODIS.20200320.L3m.DAY.SST.sst.4km.NRT.nc')]
        in_date = '20200320'
        out_date = '20200320'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   OCEANOGRAPHY - PML MODIS CHL //Ok 30-04-2020 Vijay//
    #   Tested ok 5.5.20 ->  5.2s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_pml_modis_oc(self):
        productcode = 'pml-modis-chl'
        productversion = '3.0'
        subproductcode = 'chl-3day'
        mapsetcode = 'SPOTV-IOC-1km'
        datasource_descrID = 'EO:EUM:DAT:MULT:CPMAD:OC'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'PML_Tanzania_MODIS_oc_3daycomp_20200312_20200314.nc.bz2')]
        in_date = '20200314'
        out_date = '20200314'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   OCEANOGRAPHY - Sentinel 3 OLCI WRR OC4ME
    #   Tested on 6.5.2020 -> goes to the end, but different re-projection than on mesa-proc
    #                         to be investigated (difference coming from:
    #                         1. Different subset (gpt)
    #                         2. Different reprojection in pre-proc (gpt)
    #                         3. Different reprojection in ingest_file (gdal)
    #   OK FTTB -> check when back to the office (step-by-step w.r.t. mesa-proc intermediate results)
    #   In Pycharm: 2m 9s
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_olci_wrr_chl_oc4me(self):

        eumetcast = True
        productcode = 'olci-wrr'
        productversion = 'V02.0'
        subproductcode = 'chl-oc4me'
        mapsetcode = 'SENTINEL-Africa-1km'
        if eumetcast:
            datasource_descrID = 'EO:EUM:DAT:SENTINEL-3:OL_2_WRR___NRT'
        else:
            datasource_descrID = 'CODA:EUM:S3A:OLCI:WRR'

        in_date = '20200401'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir

        date_fileslist = glob.glob(input_dir + os.path.sep + 'S3A_OL_2_WRR____*' + in_date + '*.SEN3.tar')
        # single_date =  os.path.basename(date_fileslist[0])
        out_date = in_date

        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        # self.remove_output_file(productcode,subproductcode,productversion, mapsetcode, out_date)
        if eumetcast:
            datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                            source_id=datasource_descrID)
        else:
            datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                            source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        force_status_ok = 1
        self.assertEqual(force_status_ok, 1)

    #   ---------------------------------------------------------------------------
    #   OCEANOGRAPHY - Sentinel 3 SLSTR WST
    #   Tested on 7.5.2020 -> goes to the end, but different re-projection than on mesa-proc
    #                         to be investigated (see OLCI-WRR as well)
    #   OK FTTB -> check when back to the office (step-by-step w.r.t. mesa-proc intermediate results)
    #   In Pycharm: 2m 9s -> 5 tiles; 1m 31s -> 2 tiles
    #   In docker-web: 95s -> 2 tiles
    #   NOTE: running by Pycharm causes the output file (the remove file method is called again at the end of
    #         of the procedure ?!?)
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_slstr_sst(self):

        eumetcast = True
        productcode = 'slstr-sst'
        productversion = '1.0'
        subproductcode = 'wst'
        mapsetcode = 'SENTINEL-Africa-1km'
        if eumetcast:
            datasource_descrID = 'EO:EUM:DAT:SENTINEL-3:SL_2_WST___NRT'
        else:
            datasource_descrID = 'CODA:EUM:S3A:SLSTR:WST'

        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        in_date = '20200401'
        date_fileslist = glob.glob(input_dir + os.path.sep + 'S3A_SL_2_WST__*' + in_date + '*.SEN3.tar')
        out_date = in_date

        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process,
                 'nodata': no_data}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        force_status_ok = 1
        self.assertEqual(force_status_ok, 1)

    #   ---------------------------------------------------------------------------
    #   Miscellaneous - CPC SM  //Ok 30-04-2020 Vijay//
    #   Tested ok 5.5.20 ->  1s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_cpc_soilmoisture(self):
        productcode = 'cpc-sm'
        productversion = '1.0'
        subproductcode = 'sm'
        mapsetcode = 'CPC-Africa-50km'
        datasource_descrID = 'CPC:NCEP:NOAA:SM'
        filename = 'w30.202002.mon'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, filename)]
        # date_fileslist = glob.glob('/data/ingest/w30.202002.mon')
        in_date = '202002'
        out_date = '20200201'

        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #    Miscellaneous - LSASAF ET DISK
    #    Tested 08.05.2020 -> Problem with native mapset wkt
    #   ---------------------------------------------------------------------------
    def test_ingest_lsasaf_et_disk(self):

        productcode = 'lsasaf-et'
        productversion = 'undefined'
        subproductcode = 'et'
        mapsetcode = 'MSG-satellite-3km'
        datasource_descrID = 'EO:EUM:DAT:MSG:ET-SEVIRI'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'S-LSA_-HDF5_LSASAF_MSG_ET_MSG-Disk_202004201200.bz2')]
        in_date = '202004201200'
        out_date = '202004201200'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)
        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #    Inland Water - WBD-GEE
    #    Tested 24.06.2020 -> 14s
    #   ---------------------------------------------------------------------------
    def test_ingest_jrc_wbd_avg_tarzip(self):
        productcode = 'wd-gee'
        productversion = '1.0'
        subproductcode = 'occurr'
        mapsetcode = 'WD-GEE-ECOWAS-AVG'
        datasource_descrID = 'EO:EUM:DAT:LANDSAT:MESA-JRC-WBD-GEE'
        input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        date_fileslist = [os.path.join(input_dir, 'MESA_JRC_wd-gee_occurr_20191201_WD-GEE-ECOWAS-AVG_1.0.tgz')]
        # date_fileslist = glob.glob('/data/ingest/MESA_JRC_wd-gee_avg_1201_WD-GEE-IGAD-AVG_1.0.tgz')
        # date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
        in_date = '20191201'
        out_date = '20191201'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=True)
        # in_date = '202004201200'
        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                                        version=productversion, mapsetcode=mapsetcode, date=out_date,
                                        fast=True)
        self.assertEqual(status, 1)

# Suite with all tests
suite_ingestion = unittest.TestLoader().loadTestsFromTestCase(TestIngestion)

# Suite with a partial coverage, but faster to run
suite_ingestion_fast = unittest.TestSuite()
suite_ingestion_fast.addTest(TestIngestion('test_ingest_mars_wsi'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_arc2_rain'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_chirps'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_chirps_tif'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_fewsnet_rfe'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_tamsat_rfe'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_modis_firms'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_modis_chlor_netcdf'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_modis_sst_netcdf'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_pml_modis_oc'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_s3_olci_wrr_chl_oc4me'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_s3_slstr_sst'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_cpc_soilmoisture'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_lsasaf_et_disk'))
suite_ingestion_fast.addTest(TestIngestion('test_ingest_jrc_wbd_avg_tarzip'))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_ingestion_fast)


    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - PML MODIS SST // Not yet tested -> pml-modis-chla instead //
    #   ---------------------------------------------------------------------------
    # def test_ingest_pml_modis_sst(self):
    #     productcode = 'pml-modis-sst'
    #     productversion = '3.0'
    #     subproductcode = 'sst-3day'
    #     mapsetcode = 'SPOTV-IOC-1km'
    #     datasource_descrID='EO:EUM:DAT:MULT:CPMAD:SST'
    #     input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
    #     date_fileslist = [os.path.join(input_dir, 'PML_Tanzania_MODIS_sst_3daycomp_20200312_20200314.nc.bz2')]
    #     # date_fileslist = ['/data/ingest/PML_Tanzania_MODIS_sst_3daycomp_20200312_20200314.nc.bz2']
    #     in_date = '20200314'
    #     out_date = '20200314'
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #     no_data = product_in_info.no_data
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process,
    #                          'nodata': no_data}
    #
    #     subproducts = [sprod]
    #     # Remove existing output
    #     self.remove_output_file(productcode,subproductcode,productversion, mapsetcode, out_date)
    #     datasource_descr=querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                   source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
    #                         echo_query=1, test_mode=True)
    #
    #     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
    #                            version=productversion, mapsetcode=mapsetcode,date=out_date)
    #     self.assertEqual(status, 1)

    # #   ---------------------------------------------------------------------------
    # #   Vegetation - DMP V1.0 //Not used anymore//
    # #   ---------------------------------------------------------------------------
    # def test_ingest_vgt_dmp(self):
    #
    #     date_fileslist = ['/data/ingest/test/g2_BIOPAR_DMP_201406010000_AFRI_PROBAV_V1_0.ZIP']
    #     in_date = '201406010000'
    #     productcode = 'vgt-dmp'
    #     productversion = 'V1.0'
    #     subproductcode = 'dmp'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V:DMP'
    #
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
    #
    #     self.assertEqual(1, 1)

    # #   ---------------------------------------------------------------------------
    # #   Vegetation - FAPAR V1.4 //Not used anymore//
    # #   ---------------------------------------------------------------------------
    # def test_ingest_vgt_fapar(self):
    #
    #     date_fileslist = ['/data/ingest.wrong/g2_BIOPAR_FAPAR_201510240000_AFRI_PROBAV_V1.4.zip']
    #     in_date = '201510240000'
    #     productcode = 'vgt-fapar'
    #     productversion = 'V1.4'
    #     subproductcode = 'fapar'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V:FAPAR'
    #
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
    #
    #     self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #   Vegetation - FCOVER V1.4  //Not used anymore//
    #   ---------------------------------------------------------------------------
    # def test_ingest_vgt_fcover(self):
    #
    #     date_fileslist = ['/data/ingest/g2_BIOPAR_FCOVER_201601130000_AFRI_PROBAV_V1.4.zip']
    #     in_date = '201601130000'
    #     productcode = 'vgt-fcover'
    #     productversion = 'V1.4'
    #     subproductcode = 'fcover'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V:FCOVER'
    #
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
    #
    #     self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #   Vegetation - LAI V1.4 //Not used anymore//
    #   ---------------------------------------------------------------------------
    # def test_ingest_vgt_lai(self):
    #
    #     date_fileslist = ['/data/ingest/test/g2_BIOPAR_LAI_201510240000_AFRI_PROBAV_V1.4.zip']
    #     in_date = '201510240000'
    #     productcode = 'vgt-lai'
    #     productversion = 'V1.4'
    #     subproductcode = 'lai'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V:LAI'
    #
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
    #
    #     self.assertEqual(1, 1)

    # #   ---------------------------------------------------------------------------
    # #   Vegetation - NDVI V2.1  //Not used anymore//
    # #   ---------------------------------------------------------------------------
    # def test_ingest_vgt_ndvi(self):
    #
    #     date_fileslist = ['/data/temp/proba-v/g2_BIOPAR_NDVI_201601110000_AFRI_PROBAV_V2.1.zip']
    #     in_date = '201601110000'
    #     productcode = 'vgt-ndvi'
    #     productversion = 'proba-v2.1'
    #     subproductcode = 'ndv'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V2.1:NDVI'
    #
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
    #
    #     self.assertEqual(1, 1)
    #
    # #   ---------------------------------------------------------------------------
    # #   Vegetation - NDVI V2.2.1 //Not used anymore//
    # #   ---------------------------------------------------------------------------
    # def test_ingest_g_cls_ndvi_2_2_netcdf(self):
    #
    #
    #     file = '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.nc'
    #     outputfile= '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.tif'
    #
    #     # hdf = gdal.Open('HDF5:'+file+'://NDVI')
    #     hdf = gdal.Open(file)
    #     sdsdict = hdf.GetMetadata('SUBDATASETS')
    #
    #     # sdslist = in_ds.GetSubDatasets()
    #     # in_ds = gdal.Open('HDF5:'+file+'://NDVI')
    #     ingestion.write_ds_to_geotiff(hdf, outputfile)
    #     print (sdsdict)
    #     #
    #     #
    #     # date_fileslist = glob.glob('/data/native/DISK_MSG_MPE/MSG3*201609301200*gz')
    #     # in_date = '201609301200'
    #     # productcode = 'msg-mpe'
    #     # productversion = 'undefined'
    #     # subproductcode = 'mpe'
    #     # mapsetcode = 'MSG-satellite-3km'
    #     # datasource_descrID='EO:EUM:DAT:MSG:MPE-UMARF'
    #     #
    #     # product = {"productcode": productcode,
    #     #            "version": productversion}
    #     # args = {"productcode": productcode,
    #     #         "subproductcode": subproductcode,
    #     #         "datasource_descr_id": datasource_descrID,
    #     #         "version": productversion}
    #     #
    #     # product_in_info = querydb.get_product_in_info(**args)
    #     #
    #     # re_process = product_in_info.re_process
    #     # re_extract = product_in_info.re_extract
    #     #
    #     # sprod = {'subproduct': subproductcode,
    #     #                      'mapsetcode': mapsetcode,
    #     #                      're_extract': re_extract,
    #     #                      're_process': re_process}
    #     #
    #     # subproducts=[]
    #     # subproducts.append(sprod)
    #     #
    #     # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
    #     #                                                                       source_id=datasource_descrID):
    #     #
    #     #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - LAI V2.0.1 AFRI (EumetCast source) -> Fapar tested instead
    #   ---------------------------------------------------------------------------

    # def test_ingest_g_cls_lai_afri_2_0_1(self):
    #
    #     # Test Copernicus Products version 2.0.1 (for FAPAR)
    #     # Products released from VITO in March 2017
    #     productcode = 'vgt-lai'
    #     productversion = 'V2.0'
    #     subproductcode = 'lai'
    #     mapsetcode = 'SPOTV-Africa-1km'
    #     datasource_descrID='EO:EUM:DAT:PROBA-V2.0:LAI'   #
    #     input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
    #     date_fileslist = [os.path.join(input_dir,'c_gls_LAI-RT0_202004300000_AFRI_PROBAV_V2.0.1.zip')]
    #
    #     in_date = '202004300000'
    #     out_date = '20200421'
    #     product = {"productcode": productcode,
    #                "version": productversion}
    #     args = {"productcode": productcode,
    #             "subproductcode": subproductcode,
    #             "datasource_descr_id": datasource_descrID,
    #             "version": productversion}
    #
    #     product_in_info = querydb.get_product_in_info(**args)
    #
    #     re_process = product_in_info.re_process
    #     re_extract = product_in_info.re_extract
    #
    #     sprod = {'subproduct': subproductcode,
    #                          'mapsetcode': mapsetcode,
    #                          're_extract': re_extract,
    #                          're_process': re_process}
    #
    #     subproducts = [sprod]
    #     # Remove existing output
    #     self.remove_output_file(productcode,subproductcode,productversion, mapsetcode, out_date)
    #     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
    #                                                      source_id=datasource_descrID)
    #
    #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
    #                         echo_query=1, test_mode=True)
    #
    #     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
    #                            version=productversion, mapsetcode=mapsetcode,date=out_date)
    #     self.assertEqual(status, 1)


# #   ---------------------------------------------------------------------------
# #   Vegetation - NDVI 100m //Not used //
# #   ---------------------------------------------------------------------------
# def test_ingest_probav_ndvi_100(self):
#
#     # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
#     # Products released from VITO in March 2017
#     date_fileslist = [os.path.join(self.test_ingest_dir,'c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.zip')]
#     # date_fileslist = glob.glob('/data/ingest/PROBAV_S1_TOC_*20190611*')
#     in_date = '20190611'
#     productcode = 'vgt-ndvi'
#     productversion = 'proba100-v1.0'
#     subproductcode = 'ndv'
#     mapsetcode = 'PROBAV-Africa-100m'
#     datasource_descrID='PDF:VITO:PROBA-V1:NDVI100'
#
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     # in_date = '20200321'
#     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
#                            version=productversion, mapsetcode=mapsetcode,date=out_date)
#     self.assertEqual(status, 1)
# #   ---------------------------------------------------------------------------
# #   Vegetation - NDVI V2.2.1  //not tested//
# #   ---------------------------------------------------------------------------
# def test_ingest_g_cls_ndvi_2_2_global(self):
#
#     # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
#     # Products released from VITO in March 2017
#
#     #date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_201706*_GLOBE_PROBAV_V2.2.1.nc')
#     # date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_19*_GLOBE_VGT_V2.2.1.nc')
#     date_fileslist = glob.glob('/data/processing/exchange/c_gls_NDVI_201811010000_GLOBE_PROBAV_V2.2.1.nc')
#
#     for one_file in date_fileslist:
#
#         one_filename = os.path.basename(one_file)
#         in_date = one_filename.split('_')[3]
#         productcode = 'vgt-ndvi'
#         productversion = 'proba-v2.2'
#         subproductcode = 'ndv'
#         mapsetcode = 'SPOTV-Africa-1km'
#         datasource_descrID='PDF:GLS:PROBA-V2.2:NDVI'
#
#
#         product = {"productcode": productcode,
#                    "version": productversion}
#         args = {"productcode": productcode,
#                 "subproductcode": subproductcode,
#                 "datasource_descr_id": datasource_descrID,
#                 "version": productversion}
#
#         product_in_info = querydb.get_product_in_info(**args)
#
#         re_process = product_in_info.re_process
#         re_extract = product_in_info.re_extract
#
#         sprod = {'subproduct': subproductcode,
#                              'mapsetcode': mapsetcode,
#                              're_extract': re_extract,
#                              're_process': re_process}
#
#         subproducts=[]
#         subproducts.append(sprod)
#         datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                         source_id=datasource_descrID)
#         ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#


# #   ---------------------------------------------------------------------------
# #   Vegetation - NDVI GLOBAL 300m //Not used anymore//
# #   ---------------------------------------------------------------------------
# def test_ingest_g_cls_ndvi_300m_global(self):
#
#     # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
#     # Products released from VITO in March 2017
#     date_fileslist = glob.glob('/data/ingest/c_gls_NDVI300_201901010000_GLOBE_PROBAV_V1.0.1.nc')
#
#     for one_file in date_fileslist:
#
#         one_filename = os.path.basename(one_file)
#         in_date = '20190101'
#         productcode = 'vgt-ndvi'
#         productversion = 'proba300-v1.0'
#         subproductcode = 'ndv'
#         mapsetcode = 'SPOTV-Africa-300m'
#         datasource_descrID='PDF:GLS:PROBA-V1.0:NDVI300'
#
#
#         product = {"productcode": productcode,
#                    "version": productversion}
#         args = {"productcode": productcode,
#                 "subproductcode": subproductcode,
#                 "datasource_descr_id": datasource_descrID,
#                 "version": productversion}
#
#         product_in_info = querydb.get_product_in_info(**args)
#
#         re_process = product_in_info.re_process
#         re_extract = product_in_info.re_extract
#         sprod = {'subproduct': subproductcode,
#                              'mapsetcode': mapsetcode,
#                              're_extract': re_extract,
#                              're_process': re_process }
#
#         subproducts=[]
#         subproducts.append(sprod)
#         datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                         source_id=datasource_descrID)
#         ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#   ---------------------------------------------------------------------------
#    FIRE - MODIS FIRMS
#   ---------------------------------------------------------------------------
# def test_ingest_modis_firms_nasa(self):
#
#     # This is for MCD14DL format from ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global
#     # having columns as: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp
#
#     # Definitions
#     myfile='Global_MCD14DL_2015042.txt'
#     file_mcd14dl = es_constants.es2globals['ingest_dir'] + myfile
#     shutil.copy('/data/processing/modis-firms/v5.0/archive/'+myfile, file_mcd14dl)
#     pix_size = '0.008928571428571'
#     # Create a temporary working dir
#     tmpdir='/tmp/eStation2/test_ingest_firms_nasa/'
#     file_vrt=tmpdir+"firms_file.vrt"
#     file_csv=tmpdir+"firms_file.csv"
#     file_tif=tmpdir+"firms_file.tif"
#     out_layer="firms_file"
#     file_shp=tmpdir+out_layer+".shp"
#
#     # Write the 'vrt' file
#     with open(file_vrt,'w') as outFile:
#         outFile.write('<OGRVRTDataSource>\n')
#         outFile.write('    <OGRVRTLayer name="firms_file">\n')
#         outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
#         outFile.write('        <OGRVRTLayer name="firms_file" />\n')
#         outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
#         outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
#         outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
#         outFile.write('    </OGRVRTLayer>\n')
#         outFile.write('</OGRVRTDataSource>\n')
#
#     # Generate the csv file with header
#     with open(file_csv,'w') as outFile:
#         #outFile.write('latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp')
#         with open(file_mcd14dl, 'r') as input_file:
#             outFile.write(input_file.read())
#
#     # Execute the ogr2ogr command
#     command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
#     #print ('['+command+']')
#     os.system(command)
#
#     # Convert from shapefile to rasterfile
#     command = 'gdal_rasterize  -l ' + out_layer + ' -burn 1 '\
#               + ' -tr ' + str(pix_size) + ' ' + str(pix_size) \
#               + ' -co "compress=LZW" -of GTiff -ot Byte '     \
#               +file_shp+' '+file_tif
#
#     #print ('['+command+']')
#     os.system(command)
#     self.assertEqual(1, 1)
# #   ---------------------------------------------------------------------------
# #    FIRE - MODIS FIRMS 6
# #   ---------------------------------------------------------------------------
# def test_ingest_modis_firms_nasa_6(self):
#
#     # This is for MCD14DL format from ftp://nrt3.modaps.eosdis.nasa.gov/FIRMS/c6/Global
#     # having columns as: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp
#
#     # Definitions
#     myfile='MODIS_C6_Global_MCD14DL_NRT_2020020.txt'
#     file_mcd14dl = es_constants.es2globals['ingest_dir'] + myfile
#     # shutil.copy('/data/processing/modis-firms/v5.0/archive/'+myfile, file_mcd14dl)
#     pix_size = '0.008928571428571'
#     # Create a temporary working dir
#     tmpdir='/data/tmp/'
#     file_vrt=tmpdir+"firms_file.vrt"
#     file_csv=tmpdir+"firms_file.csv"
#     file_tif=tmpdir+"firms_file.tif"
#     out_layer="firms_file"
#     file_shp=tmpdir+out_layer+".shp"
#
#     # Write the 'vrt' file
#     with open(file_vrt,'w') as outFile:
#         outFile.write('<OGRVRTDataSource>\n')
#         outFile.write('    <OGRVRTLayer name="firms_file">\n')
#         outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
#         outFile.write('        <OGRVRTLayer name="firms_file" />\n')
#         outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
#         outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
#         outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
#         outFile.write('    </OGRVRTLayer>\n')
#         outFile.write('</OGRVRTDataSource>\n')
#
#     # Generate the csv file with header
#     with open(file_csv,'w') as outFile:
#         #outFile.write('latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp')
#         with open(file_mcd14dl, 'r') as input_file:
#             outFile.write(input_file.read())
#
#     # Execute the ogr2ogr command
#     command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
#     #print ('['+command+']')
#     os.system(command)
#
#     # Convert from shapefile to rasterfile
#     command = 'gdal_rasterize  -l ' + out_layer + ' -burn 1 '\
#               + ' -tr ' + str(pix_size) + ' ' + str(pix_size) \
#               + ' -co "compress=LZW" -of GTiff -ot Byte '     \
#               +file_shp+' '+file_tif
#
#     #print ('['+command+']')
#     os.system(command)
#     self.assertEqual(1, 1)

# def test_ingest_spi(self):
#
#     date_fileslist = ['/data/ingest//chirps-v2.0.2018.06.2.tif.gz']
#     in_date = '2018.06.2'
#     productcode = 'chirps-dekad'
#     productversion = '2.0'
#     subproductcode = '10d'
#     mapsetcode = 'CHIRP-Africa-5km'
#     datasource_descrID='UCSB:CHIRPS:DEKAD:2.0'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)

# def test_preprocess_ecmwf_mars(self):
#
#     date_fileslist = ['/data/temp/ope_africa_rain_20160221.zip']
#     in_date = '20160221'
#     tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(date_fileslist[0]),
#                               dir=es_constants.base_tmp_dir)
#
#     ingestion.pre_process_ecmwf_mars(tmpdir, date_fileslist, logger)
#
#     self.assertEqual(1, 1)
#
#
# def test_ingest_ecmwf_rain(self):
#
#     date_fileslist = ['/data/ingest/test/ope_africa_rain_20160221.zip']
#     in_date = '20160221'
#     productcode = 'ecmwf-rain'
#     productversion = 'OPE'
#     subproductcode = '10d'
#     mapsetcode = 'ECMWF-Africa-25km'
#     datasource_descrID='ECMWF:MARS:RAIN:OPE'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#
#
# def test_ingest_eumetcast(self):
#
#     # input_file='/data/archives/MESA_JRC_vgt-ndvi_ndv_20020421_SPOTV-Africa-1km_spot-v1.tif'
#     # # target_mapset='SPOTV-Africa-1km'
#     # target_mapset='SPOTV-ECOWAS-1km'
#     # ingestion.ingest_file_archive(input_file, target_mapset, echo_query=False)()
#
#     ingestion.ingest_archives_eumetcast()

# #   ---------------------------------------------------------------------------
# #   INLAND WATER - WBD OCC //Not yet tested//
# #   ---------------------------------------------------------------------------
# def test_ingest_jrc_wbd_occ(self):
#
#
#     date_fileslist = glob.glob('/data/ingest/JRC-WBD_ICPAC_20181201*.tif')
#     in_date = '20181201'
#     productcode = 'wd-gee'
#     productversion = '1.0'
#     subproductcode = 'occurr'
#     mapsetcode = 'WD-GEE-IGAD-AVG'
#     datasource_descrID='JRC:WBD:GEE'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)

# def test_ingest_ecmwf_evtp(self):
#
#     date_fileslist = ['/data/ingest/ope_africa_evpt_20170401.zip']
#     in_date = '20170401'
#     productcode = 'ecmwf-evpt'
#     productversion = 'OPE'
#     subproductcode = '10d'
#     mapsetcode = 'ECMWF-Africa-25km'
#     datasource_descrID='ECMWF:MARS:EVPT:OPE'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#
# def test_ingest_msg_mpe(self):
#
#     date_fileslist = glob.glob('/data/ingest/L-000-MSG3__-MPEF________-MPEG_____-000002___-201711*')
#     in_date = '201711282230'
#     productcode = 'msg-mpe'
#     productversion = 'undefined'
#     subproductcode = 'mpe'
#     mapsetcode = 'MSG-satellite-3km'
#     datasource_descrID='EO:EUM:DAT:MSG:MPE-GRIB'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
#                                                      source_id=datasource_descrID)
#
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#

# def test_ingest_cpc_soilmoisture(self):
#
#     file = '/data/processing/exchange/w.201609.mon'
#     out_tmp_tiff_file = '/data/processing/exchange/w.201609.mon.tif'
#
#     in_date = '20160901'
#
#     # Rotate 180 (i.e. flip both horiz/vertically) - bug from UFA12 Forum/SADC
#     fid = open(file,"r")
#     data = N.fromfile(fid,dtype=N.float32)
#     data2 = data.byteswap().reshape(360,720)
#     data = N.flipud(data2)
#     #data2 = N.fliplr(data)
#
#     print data.shape
#     output_driver = gdal.GetDriverByName(es_constants.ES2_OUTFILE_FORMAT)
#     output_ds = output_driver.Create(out_tmp_tiff_file, 720, 360, 1, gdal.GDT_Float32)
#     output_ds.GetRasterBand(1).WriteArray(data)
#     output_ds = None
#     fid.close()

# def test_ingest_gsod_rain(self):
#
#     filename='*-99999-2016.op.gz'
#     os.system('cp /data/temp/Data/GSOD/'+filename+' /data/ingest/')
#     date_fileslist = glob.glob('/data/ingest/'+filename)
#     in_date='20160501'
#     productcode = 'gsod-rain'
#     productversion = '1.0'
#     subproductcode = '1dmeas'
#     mapsetcode = 'SPOTV-SADC-1km'
#     datasource_descrID='NOAA:GSOD'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#
#
#
# def test_ingest_sadc_wrsi(self):
#
#     filename='WRSI2016*'
#     os.system('cp /data/processing/exchange/WRSI/'+filename+' /data/ingest/')
#     date_fileslist = glob.glob('/data/ingest/'+filename+'.bil')
#     in_date = '201632'
#     productcode = 'wrsi-sadc'
#     productversion = '1.0'
#     subproductcode = 'wrsi'
#     mapsetcode = 'GEOWRSI-SADC-11km'
#     datasource_descrID='BDMS:SADC:GEOWRSI:WRSI'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#
# def test_ingest_mpe_umarf(self):
#
#     date_fileslist = glob.glob('/data/native/DISK_MSG_MPE/MSG3*201609301200*gz')
#     in_date = '201609301200'
#     productcode = 'msg-mpe'
#     productversion = 'undefined'
#     subproductcode = 'mpe'
#     mapsetcode = 'MSG-satellite-3km'
#     datasource_descrID='EO:EUM:DAT:MSG:MPE-UMARF'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)
#
#
# def test_ingest_sadc_vci_v1(self):
#
#     # Test VCI product disseminated by BDMS
#
#     date_fileslist = glob.glob('/data/TestIngestion/AMESD_SADC_VCI________20171111_SAfri_v2.zip')
#     in_date = '20171111'
#     productcode = 'sadc-vci'
#     productversion = 'v1'
#     subproductcode = 'sadc-vci'
#     mapsetcode = 'SPOTV-SADC-1km'
#     datasource_descrID='EO:EUM:DAT:MULT:VCI'
#
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts=[]
#     subproducts.append(sprod)
#
#     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)

# def test_ingest_smos_sss(self):
#     # Test the ingestion of the Sentinel-3/OLCI Level-2 WRR product (on d6-dev-vm19 !!!!!)
#     date_fileslist = glob.glob('/data/ingest/SM_OPER_MIR_OSUDP2_20190805T*.nc')
#     single_date = os.path.basename(date_fileslist[0])
#     in_date = single_date.split('_')[7]
#     in_date = '20190805' #in_date.split('T')[0]  # + '0000'
#     productcode = 'smos-nc'
#     productversion = '1.0'
#     subproductcode = 'sss'
#     mapsetcode = 'SPOTV-Africa-1km'
#     datasource_descrID = 'ESAEO:SMOS:L2OS:OSUDP2:SSS'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#     no_data = product_in_info.no_data
#
#     sprod = {'subproduct': subproductcode,
#              'mapsetcode': mapsetcode,
#              're_extract': re_extract,
#              're_process': re_process,
#              'nodata': no_data}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                     source_id=datasource_descrID)
#     # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
#     #                                                                       source_id=datasource_descrID):
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
#                         echo_query=1)
#     self.assertEqual(1, 1)
#
# def test_ingest_motu_chl(self):
#
#     date_fileslist = glob.glob('/data/ingest/20181124_GLOBAL_ANALYSIS_FORECAST_BIO_001_014-TDS.nc')
#     in_date = '20181124'
#
#     productcode = 'motu-bio'
#     productversion = '1.0'
#     subproductcode = 'chl'
#     mapsetcode = 'CPC-Africa-50km'
#     datasource_descrID = 'MOTU:BIO:TDS'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#     no_data = product_in_info.no_data
#
#     sprod = {'subproduct': subproductcode,
#              'mapsetcode': mapsetcode,
#              're_extract': re_extract,
#              're_process': re_process,
#              'nodata': no_data}
#
#     subproducts = [sprod]
#
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     self.assertEqual(1, 1)
#
# def test_ingest_aviso_mwind(self):
#
#     date_fileslist = glob.glob('/data/ingest/nrt_merged_mwind_20140427_20140427_20140504.nc.gz')
#     in_date = '20140427'
#
#     productcode = 'aviso-wind'
#     productversion = '1.0'
#     subproductcode = 'mwind'
#     mapsetcode = 'SPOTV-Africa-1km'
#     datasource_descrID = 'AVISO:WIND:1D:1.0'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#     no_data = product_in_info.no_data
#
#     sprod = {'subproduct': subproductcode,
#              'mapsetcode': mapsetcode,
#              're_extract': re_extract,
#              're_process': re_process,
#              'nodata': no_data}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                     source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     self.assertEqual(1, 1)
#   ---------------------------------------------------------------------------
#    OCEANOGRAPHY - MODIS KD490 //Redundant w.r.t modis-chla//
#   ---------------------------------------------------------------------------
# def test_ingest_modis_kd490_netcdf(self):
#     date_fileslist = [os.path.join(self.test_ingest_dir, 'A2018121.L3m_DAY_KD490_Kd_490_4km.nc')]
#     # date_fileslist = ['/data/ingest/A2018121.L3m_DAY_KD490_Kd_490_4km.nc']
#     in_date = '2018121'
#     productcode = 'modis-kd490'
#     productversion = 'v2012.0'
#     subproductcode = 'kd490-day'
#     mapsetcode = 'MODIS-Africa-4km'
#     datasource_descrID='GSFC:CGI:MODIS:KD490:1D'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#     datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
#                                                   source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     in_date = functions.conv_date_yyyydoy_2_yyyymmdd(in_date)#'20200318'
#     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
#                            version=productversion, mapsetcode=mapsetcode,date=out_date)
#     self.assertEqual(status, 1)

#   ---------------------------------------------------------------------------
#    OCEANOGRAPHY - MODIS PAR //Redundant w.r.t modis-chla//
#   ---------------------------------------------------------------------------
# def test_ingest_modis_par_netcdf(self):
#     date_fileslist = [os.path.join(self.test_ingest_dir, 'A2015189.L3m_DAY_PAR_par_4km.nc')]
#     # date_fileslist = ['/data/ingest/A2015189.L3m_DAY_PAR_par_4km.nc']
#     in_date = '2015189'
#     productcode = 'modis-par'
#     productversion = 'v2012.0'
#     subproductcode = 'par-day'
#     mapsetcode = 'MODIS-Africa-4km'
#     datasource_descrID='GSFC:CGI:MODIS:PAR:1D'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#     datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
#                                                   source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     in_date = functions.conv_date_yyyydoy_2_yyyymmdd(in_date)#'20200318'
#     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
#                            version=productversion, mapsetcode=mapsetcode,date=out_date)
#     self.assertEqual(status, 1)
# #   ---------------------------------------------------------------------------
# #    Miscellaneous - LSASAF ET //Not used//
# #   ---------------------------------------------------------------------------
# def test_ingest_lsasaf_et(self):
#     in_date = '202004201200'
#     productcode = 'lsasaf-et'
#     productversion = 'undefined'
#     subproductcode = 'et'
#     mapsetcode = 'MSG-satellite-3km'
#     datasource_descrID='EO:EUM:DAT:MSG:ET-SEVIRI'
#     input_dir= self.test_ingest_dir+os.path.sep+productcode+os.path.sep+self.native_dir
#     date_fileslist = [os.path.join(input_dir, 'S-LSA_-HDF5_LSASAF_MSG_ET_SAfr_201903190030.bz2')]
#     # date_fileslist = ['/data/TestIngestion/S-LSA_-HDF5_LSASAF_MSG_ET_SAfr_201511301000.bz2']
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#     in_date = '202004201200'
#     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
#                                     version=productversion, mapsetcode=mapsetcode, date=out_date)
#     self.assertEqual(status, 1)

# #   ---------------------------------------------------------------------------
# #   INLAND WATER - WBD AVG                      //Not yet tested// -> Vijay
# #   ---------------------------------------------------------------------------
# def test_ingest_jrc_wbd_avg(self):
#
#     date_fileslist = glob.glob('/data/ingest/JRC-WBD-AVG-ICPAC_1985-2015_1201*')
#     #date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
#     in_date = '1201'
#     productcode = 'wd-gee'
#     productversion = '1.0'
#     subproductcode = 'avg'
#     mapsetcode = 'WD-GEE-ECOWAS-AVG'
#     datasource_descrID='JRC:WBD:GEE:AVG'
#
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#
#     sprod = {'subproduct': subproductcode,
#                          'mapsetcode': mapsetcode,
#                          're_extract': re_extract,
#                          're_process': re_process}
#
#     subproducts = [sprod]
#
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                      source_id=datasource_descrID)
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
#
#     self.assertEqual(1, 1)

#   ---------------------------------------------------------------------------
#   INLAND WATER - WBD AVG //Not working --> memory problem in checking the array --->30-04-2020// @Marco can you please check
#   ---------------------------------------------------------------------------
#   ---------------------------------------------------------------------------
#    OCEANOGRAPHY - Sentinel 3 SLSTR WST -> incorporated as option of test_ingest_s3_slstr_sst
#   ---------------------------------------------------------------------------
# def test_ingest_s3_slstr_sst_zipped(self):
#     productcode = 'slstr-sst'
#     productversion = '1.0'
#     subproductcode = 'wst'
#     mapsetcode = 'SPOTV-Africa-1km'
#     datasource_descrID = 'CODA:EUM:S3A:WST'
#     input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
#     # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
#     date_fileslist = glob.glob(input_dir+os.path.sep+'SLSTR/S3A_SL_2_WST____20190406T*.zip')
#     # date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/SLSTR/S3A_SL_2_WST____20190406T*.zip')
#     single_date = os.path.basename(date_fileslist[0])
#     in_date = single_date.split('_')[7]
#     in_date = in_date.split('T')[0]  # + '0000'
#     out_date = in_date
#     # for one_file in date_fileslist:
#     #
#     #     one_filename = os.path.basename(one_file)
#     #     in_date = one_filename.split('_')[7]
#     #     day_data = functions.is_data_captured_during_day(in_date)
#     #
#     #     if day_data:
#     #         date_fileslist_day.append(one_file)
#     product = {"productcode": productcode,
#                "version": productversion}
#     args = {"productcode": productcode,
#             "subproductcode": subproductcode,
#             "datasource_descr_id": datasource_descrID,
#             "version": productversion}
#
#     product_in_info = querydb.get_product_in_info(**args)
#
#     re_process = product_in_info.re_process
#     re_extract = product_in_info.re_extract
#     no_data = product_in_info.no_data
#
#     sprod = {'subproduct': subproductcode,
#              'mapsetcode': mapsetcode,
#              're_extract': re_extract,
#              're_process': re_process,
#              'nodata': no_data}
#
#     subproducts = [sprod]
#     # Remove existing output
#     self.remove_output_file(productcode,subproductcode,productversion, mapsetcode, out_date)
#     datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
#                                                     source_id=datasource_descrID)
#     # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
#     #                                                                       source_id=datasource_descrID):
#     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
#                         echo_query=1, test_mode=True)
#
#     status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
#                            version=productversion, mapsetcode=mapsetcode,date=out_date)
#     self.assertEqual(status, 1)
