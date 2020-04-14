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

from osgeo import gdal

# Overwrite Dirs
from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestIngestion(unittest.TestCase):

    def setUp(self):
        root_test_dir=es_constants.es2globals['test_data_dir']
        self.test_ingest_dir=os.path.join(root_test_dir,'native')
        self.proc_dir_bck = es_constants.processing_dir
        es_constants.processing_dir = es_constants.es2globals['base_tmp_dir']+os.path.sep
        self.ingest_out_dir = es_constants.processing_dir
        self.ref_out_dir = os.path.join(root_test_dir,'refs_output')

    def tearDown(self):
        es_constants.processing_dir = self.proc_dir_bck

    def checkIngestedFile(self, productcode='', subproductcode='', version='', mapsetcode='', date=''):
        # Given the all files keys (date, prod, sprod, ...) finds out:
        # -> the product just ingested in the tmp_dir (see setUp)
        # -> the product in refs_output
        # Assess if the products are equal/equivalent

        result = 0
        filename = functions.set_path_filename(date,productcode, subproductcode, mapsetcode, version, '.tif')
        sub_directory= functions.set_path_sub_directory(productcode,subproductcode,'Ingest',version,mapsetcode)

        ref_file = glob.glob(self.ref_out_dir+'**/*/*/'+filename, recursive=True)
        newly_computed_file = glob.glob(self.ingest_out_dir+sub_directory+filename,recursive=True)

        # Compare the files by using gdal_info objects
        if os.path.exists(ref_file[0]) and os.path.exists(newly_computed_file[0]):
            gdal_info_ref = md.GdalInfo()
            gdal_info_ref.get_gdalinfo(ref_file[0])
            gdal_info_new = md.GdalInfo()
            gdal_info_new.get_gdalinfo(newly_computed_file[0])
            equal = gdal_info_new.compare_gdalinfo(gdal_info_ref)

        return equal

    def TestDriveAll(self):
        dry_run = True
        ingestion.loop_ingestion(dry_run=dry_run)
        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - WSI CROP/PASTURE  \\tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_mars_wsi(self):

        date_fileslist = [os.path.join(self.test_ingest_dir,'wsi_hp_pasture_20200221.img'),
                          os.path.join(self.test_ingest_dir,'wsi_hp_pasture_20200221.hdr')]

        in_date = '20200221'
        productcode = 'wsi-hp'
        productversion = 'V1.0'
        subproductcode = 'pasture'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='JRC:MARS:WSI:PASTURE'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
                               version=productversion, mapsetcode=mapsetcode,date=in_date)
        self.assertEqual(status, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - DMP V1.0 \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_dmp(self):

        date_fileslist = ['/data/ingest/test/g2_BIOPAR_DMP_201406010000_AFRI_PROBAV_V1_0.ZIP']
        in_date = '201406010000'
        productcode = 'vgt-dmp'
        productversion = 'V1.0'
        subproductcode = 'dmp'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V:DMP'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - DMP V2.0.1 //Tested//
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_dmp_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for DMP)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/ingest/c_gls_DMP-RT0_202003200000_GLOBE_PROBAV_V2.0.1.nc')
        in_date = '20200320'
        productcode = 'vgt-dmp'
        productversion = 'V2.0'
        subproductcode = 'dmp'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='PDF:GLS:PROBA-V2.0:DMP_RT0'


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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FAPAR V1.4 \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_fapar(self):

        date_fileslist = ['/data/ingest.wrong/g2_BIOPAR_FAPAR_201510240000_AFRI_PROBAV_V1.4.zip']
        in_date = '201510240000'
        productcode = 'vgt-fapar'
        productversion = 'V1.4'
        subproductcode = 'fapar'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V:FAPAR'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FAPAR V2.0.1 \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_fapar_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for FAPAR)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/ingest/c_gls_FAPAR-RT0_202003100000_GLOBE_PROBAV_V2.0.1.nc*')
        in_date = '202003100000'
        productcode = 'vgt-fapar'
        productversion = 'V2.0'
        subproductcode = 'fapar'
        mapsetcode = 'SPOTV-Africa-1km'
        # datasource_descrID = 'EO:EUM:DAT:PROBA-V2.0:FAPAR'
        datasource_descrID='PDF:GLS:PROBA-V2.0:FAPAR'   #


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

        # datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                  source_id=datasource_descrID)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FCOVER V1.4  \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_fcover(self):

        date_fileslist = ['/data/ingest/g2_BIOPAR_FCOVER_201601130000_AFRI_PROBAV_V1.4.zip']
        in_date = '201601130000'
        productcode = 'vgt-fcover'
        productversion = 'V1.4'
        subproductcode = 'fcover'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V:FCOVER'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FCOVER V2.0.2 \\Made similar process test\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_fcover(self):

        date_fileslist = ['/data/ingest/c_gls_FCOVER_199901200000_GLOBE_VGT_V2.0.2.nc']
        in_date = '199901200000'
        productcode = 'vgt-fcover'
        productversion = 'V2.0'
        subproductcode = 'fcover'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='PDF:GLS:VGT-V2.0:FCOVER'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - LAI V1.4 \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_lai(self):

        date_fileslist = ['/data/ingest/test/g2_BIOPAR_LAI_201510240000_AFRI_PROBAV_V1.4.zip']
        in_date = '201510240000'
        productcode = 'vgt-lai'
        productversion = 'V1.4'
        subproductcode = 'lai'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V:LAI'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.1  \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_vgt_ndvi(self):

        date_fileslist = ['/data/temp/proba-v/g2_BIOPAR_NDVI_201601110000_AFRI_PROBAV_V2.1.zip']
        in_date = '201601110000'
        productcode = 'vgt-ndvi'
        productversion = 'proba-v2.1'
        subproductcode = 'ndv'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V2.1:NDVI'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.2.1 \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_2_2_netcdf(self):


        file = '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.nc'
        outputfile= '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.tif'

        # hdf = gdal.Open('HDF5:'+file+'://NDVI')
        hdf = gdal.Open(file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')

        # sdslist = in_ds.GetSubDatasets()
        # in_ds = gdal.Open('HDF5:'+file+'://NDVI')
        ingestion.write_ds_to_geotiff(hdf, outputfile)
        print (sdsdict)
        #
        #
        # date_fileslist = glob.glob('/data/native/DISK_MSG_MPE/MSG3*201609301200*gz')
        # in_date = '201609301200'
        # productcode = 'msg-mpe'
        # productversion = 'undefined'
        # subproductcode = 'mpe'
        # mapsetcode = 'MSG-satellite-3km'
        # datasource_descrID='EO:EUM:DAT:MSG:MPE-UMARF'
        #
        # product = {"productcode": productcode,
        #            "version": productversion}
        # args = {"productcode": productcode,
        #         "subproductcode": subproductcode,
        #         "datasource_descr_id": datasource_descrID,
        #         "version": productversion}
        #
        # product_in_info = querydb.get_product_in_info(**args)
        #
        # re_process = product_in_info.re_process
        # re_extract = product_in_info.re_extract
        #
        # sprod = {'subproduct': subproductcode,
        #                      'mapsetcode': mapsetcode,
        #                      're_extract': re_extract,
        #                      're_process': re_process}
        #
        # subproducts=[]
        # subproducts.append(sprod)
        #
        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
        #                                                                       source_id=datasource_descrID):
        #
        #     ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.2.1 \\Not tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_2_2(self):

        # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.zip*')
        in_date = '201401010000'
        productcode = 'vgt-ndvi'
        productversion = 'proba-v2.2'
        subproductcode = 'ndv'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V2.2:NDVI'


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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI 100m \\Not used \\
    #   ---------------------------------------------------------------------------
    def test_ingest_probav_ndvi_100(self):

        # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/ingest/PROBAV_S1_TOC_*20190611*')
        in_date = '20190611'
        productcode = 'vgt-ndvi'
        productversion = 'proba100-v1.0'
        subproductcode = 'ndv'
        mapsetcode = 'PROBAV-Africa-100m'
        datasource_descrID='PDF:VITO:PROBA-V1:NDVI100'


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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI 300m \\working\\
    #   ---------------------------------------------------------------------------
    def test_ingest_probav_ndvi_300(self):
        # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/ingest/PROBAV_S10_TOC_*20200201**')
        in_date = '20200201'
        productcode = 'vgt-ndvi'
        productversion = 'proba300-v1.0'
        subproductcode = 'ndv'
        mapsetcode = 'SENTINEL-Africa-300m'
        datasource_descrID = 'PDF:VITO:PROBA-V1:NDVI300'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                               echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.2.1  //not tested//
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_2_2_global(self):

        # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
        # Products released from VITO in March 2017

        #date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_201706*_GLOBE_PROBAV_V2.2.1.nc')
        # date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_19*_GLOBE_VGT_V2.2.1.nc')
        date_fileslist = glob.glob('/data/processing/exchange/c_gls_NDVI_201811010000_GLOBE_PROBAV_V2.2.1.nc')

        for one_file in date_fileslist:

            one_filename = os.path.basename(one_file)
            in_date = one_filename.split('_')[3]
            productcode = 'vgt-ndvi'
            productversion = 'proba-v2.2'
            subproductcode = 'ndv'
            mapsetcode = 'SPOTV-Africa-1km'
            datasource_descrID='PDF:GLS:PROBA-V2.2:NDVI'


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

            subproducts=[]
            subproducts.append(sprod)
            datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                            source_id=datasource_descrID)
            ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI GLOBAL 300m \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_300m_global(self):

        # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
        # Products released from VITO in March 2017
        date_fileslist = glob.glob('/data/ingest/c_gls_NDVI300_201901010000_GLOBE_PROBAV_V1.0.1.nc')

        for one_file in date_fileslist:

            one_filename = os.path.basename(one_file)
            in_date = '20190101'
            productcode = 'vgt-ndvi'
            productversion = 'proba300-v1.0'
            subproductcode = 'ndv'
            mapsetcode = 'SPOTV-Africa-300m'
            datasource_descrID='PDF:GLS:PROBA-V1.0:NDVI300'


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
                                 're_process': re_process }

            subproducts=[]
            subproducts.append(sprod)
            datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                            source_id=datasource_descrID)
            ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #   Rainfall - ARC2  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_arc2_rain(self):

        date_fileslist = glob.glob('/data/ingest/africa_arc.20200318.tif.zip')
        in_date = '20200318'
        productcode = 'arc2-rain'
        productversion = '2.0'
        subproductcode = '1day'
        mapsetcode = 'ARC2-Africa-11km'
        datasource_descrID='CPC:NOAA:RAIN:ARC2'

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
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #   Rainfall - CHIRPS  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_chirps(self):

        date_fileslist = ['/data/ingest/chirps-v2.0.2020.02.3.tif.gz']
        in_date = '2020.02.3'
        productcode = 'chirps-dekad'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'CHIRP-Africa-5km'
        datasource_descrID='UCSB:CHIRPS:DEKAD:2.0'

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
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   Rainfall - CHIRPS TIF  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_chirps_tif(self):

        date_fileslist = ['/data/ingest/chirps-v2.0.2020.03.1.tif']
        in_date = '2020.03.1'
        productcode = 'chirps-dekad'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'CHIRP-Africa-5km'
        datasource_descrID='UCSB:CHIRPS:PREL:DEKAD'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    Rainfall - Fewsnet 2  \\working\\
    #   ---------------------------------------------------------------------------
    def test_ingest_fewsnet_rfe(self):

        # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
        #date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180306T095629_20180306T095929_20180306T114727_0179_028_307_3420_MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/ingest/a20013rb.zip')
        in_date = '20013'
        productcode = 'fewsnet-rfe'
        productversion = '2.0'
        subproductcode = '10d'
        mapsetcode = 'FEWSNET-Africa-8km'
        datasource_descrID = 'USGS:EARLWRN:FEWSNET'

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


        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    Rainfall - TAMSAT 3  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_tamsat_rfe(self):

        date_fileslist = glob.glob('/data/ingest/rfe2020_01-dk3.v3.nc')
        in_date = '2020_01-dk3'
        productcode = 'tamsat-rfe'
        productversion = '3.0'
        subproductcode = '10d'
        mapsetcode = 'TAMSAT-Africa-4km'
        datasource_descrID = 'READINGS:TAMSAT:3.0:10D:NC'

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


        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)

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
    #   ---------------------------------------------------------------------------
    #    FIRE - MODIS FIRMS 6  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_firms(self):

        date_fileslist = glob.glob('/data/ingest/MODIS_C6_Global_MCD14DL_NRT_2020020.txt')
        in_date = '2020020'
        productcode = 'modis-firms'
        productversion = 'v6.0'
        subproductcode = '1day'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'MODAPS:EOSDIS:FIRMS:NASA:HTTP'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    FIRE - PROBA BA 300 NOT WORKING
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ba_300m_global(self):
        # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
        # Products released from VITO in March 2017
        date_fileslist = glob.glob('/data/ingest/c_gls_BA300_202003100000_GLOBE_PROBAV_V1.1.1.nc')

        for one_file in date_fileslist:

            one_filename = os.path.basename(one_file)
            in_date = '20200310'
            productcode = 'vgt-ba'
            productversion = 'V1.1'
            subproductcode = 'ba'
            mapsetcode = 'SENTINEL-Africa-300m'
            datasource_descrID='PDF:GLS:PROBA-V1.1:BA300'

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
                                 'nodata': product_in_info.no_data }

            subproducts=[]
            subproducts.append(sprod)
            datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                            source_id=datasource_descrID)
            ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS CHLA  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_chlor_netcdf(self):

        date_fileslist = ['/data/ingest/A2020078.L3m_DAY_CHL_chlor_a_4km.nc']
        in_date = '2020078'
        productcode = 'modis-chla'
        productversion = 'v2013.1'
        subproductcode = 'chla-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID='GSFC:CGI:MODIS:CHLA:1D'

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

        datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS KD490 \\Made similar process test\\
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_kd490_netcdf(self):

        date_fileslist = ['/data/ingest/A2018121.L3m_DAY_KD490_Kd_490_4km.nc']
        in_date = '2018121'
        productcode = 'modis-kd490'
        productversion = 'v2012.0'
        subproductcode = 'kd490-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID='GSFC:CGI:MODIS:KD490:1D'

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
        datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS PAR \\Made similar process test\\
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_par_netcdf(self):

        date_fileslist = ['/data/ingest/A2015189.L3m_DAY_PAR_par_4km.nc']
        in_date = '2015189'
        productcode = 'modis-par'
        productversion = 'v2012.0'
        subproductcode = 'par-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID='GSFC:CGI:MODIS:PAR:1D'

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
        datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS SST  \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_modis_sst_netcdf(self):

        date_fileslist = ['/data/ingest/AQUA_MODIS.20200320.L3m.DAY.SST.sst.4km.NRT.nc']
        in_date = '20200320'
        productcode = 'modis-sst'
        productversion = 'v2013.1'
        subproductcode = 'sst-day'
        mapsetcode = 'MODIS-Africa-4km'
        datasource_descrID='GSFC:CGI:MODIS:SST:1D'

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

        datasource_descr=querydb.get_datasource_descr(source_type='INTERNET',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - PML MODIS SST \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_pml_modis_sst(self):

        date_fileslist = ['/data/ingest/PML_Tanzania_MODIS_sst_3daycomp_20200312_20200314.nc.bz2']
        in_date = '20200314'
        productcode = 'pml-modis-sst'
        productversion = '3.0'
        subproductcode = 'sst-3day'
        mapsetcode = 'SPOTV-IOC-1km'
        datasource_descrID='EO:EUM:DAT:MULT:CPMAD:SST'

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
        datasource_descr=querydb.get_datasource_descr(source_type='EUMETCAST',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - PML MODIS CHL \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_pml_modis_oc(self):

        date_fileslist = ['/data/ingest/PML_Tanzania_MODIS_oc_3daycomp_20200312_20200314.nc.bz2']
        in_date = '20200314'
        productcode = 'pml-modis-chl'
        productversion = '3.0'
        subproductcode = 'chl-3day'
        mapsetcode = 'SPOTV-IOC-1km'
        datasource_descrID='EO:EUM:DAT:MULT:CPMAD:OC'

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

        datasource_descr=querydb.get_datasource_descr(source_type='EUMETCAST',
                                                      source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 OLCI WRR \\Not used anymore\\
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_olci_wrr(self):

        # Test the ingestion of the Sentinel-3/OLCI Level-2 WRR product (on d6-dev-vm19 !!!!!)
        #date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_OL_2_WRR/S3A_OL_2_WRR____20180306T092820_20180306T101211_20180306T115859_2631_028_307______MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/ingest/S3A_OL_2_WRR____*')
        single_date =  os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0] #+ '0000'
        productcode = 'olci-wrr'
        productversion = 'V02.0'
        subproductcode = 'chl-nn'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:SENTINEL-3:OL_2_WRR___NRT'


        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(echo=1, **args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract
        no_data = product_in_info.no_data

        sprod = {'subproduct': subproductcode,
                             'mapsetcode': mapsetcode,
                             're_extract': re_extract,
                             're_process': re_process,
                             'nodata': no_data}

        subproducts = [sprod]

        # datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                  source_id=datasource_descrID)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 OLCI WRR OC4ME \\Not working\\
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_olci_wrr_chl_oc4me(self):
        # Test the ingestion of the Sentinel-3/OLCI Level-2 WRR product (on d6-dev-vm19 !!!!!)
        date_fileslist = glob.glob('/data/ingest/S3A_OL_2_WRR_*')
        single_date =  os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0] #+ '0000'
        productcode = 'olci-wrr'
        productversion = 'V02.0'
        subproductcode = 'chl-oc4me'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:SENTINEL-3:OL_2_WRR___NRT'
        datasource_descrID='CODA:EUM:S3A:OLCI:WRR'

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

        # datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                  source_id=datasource_descrID)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 SLSTR WST \\Not working\\
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_slstr_sst(self):

        # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
        # date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180306T095629_20180306T095929_20180306T114727_0179_028_307_3420_MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/ingest/S3A_SL_2_WST__*.SEN3.tar')
        single_date = os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0]  # + '0000'
        # for one_file in date_fileslist:
        #
        #     one_filename = os.path.basename(one_file)
        #     in_date = one_filename.split('_')[7]
        #     day_data = functions.is_data_captured_during_day(in_date)
        #
        #     if day_data:
        #         date_fileslist_day.append(one_file)
        productcode = 'slstr-sst'
        productversion = '1.0'
        subproductcode = 'wst'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'EO:EUM:DAT:SENTINEL-3:SL_2_WST___NRT'
        # datasource_descrID = 'CODA:EUM:S3A:SLSTR:WST'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)
        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 SLSTR WST \\Not working\\
    #   ---------------------------------------------------------------------------
    def test_ingest_s3_slstr_sst_zipped(self):

        # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
        # date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180306T095629_20180306T095929_20180306T114727_0179_028_307_3420_MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/SLSTR/S3A_SL_2_WST____20190406T*.zip')
        single_date = os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0]  # + '0000'
        # for one_file in date_fileslist:
        #
        #     one_filename = os.path.basename(one_file)
        #     in_date = one_filename.split('_')[7]
        #     day_data = functions.is_data_captured_during_day(in_date)
        #
        #     if day_data:
        #         date_fileslist_day.append(one_file)
        productcode = 'slstr-sst'
        productversion = '1.0'
        subproductcode = 'wst'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'CODA:EUM:S3A:WST'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                                       source_id=datasource_descrID):
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

    #   ---------------------------------------------------------------------------
    #    Miscellaneous - CPC SM \\Tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_cpc_soilmoisture(self):

        filename='w30.202002.mon'
        # shutil.copy('/data/processing/exchange/'+filename,'/data/ingest/'+filename)
        date_fileslist = glob.glob('/data/ingest/w30.202002.mon')
        in_date = '202002'
        productcode = 'cpc-sm'
        productversion = '1.0'
        subproductcode = 'sm'
        mapsetcode = 'CPC-Africa-50km'
        #mapsetcode = 'CPC-Global-50km'
        datasource_descrID='CPC:NCEP:NOAA:SM'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    Miscellaneous - LSASAF ET \\Not yet tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_lsasaf_et_disk(self):

        date_fileslist = ['/data/ingest/test/S-LSA_-HDF5_LSASAF_MSG_ET_MSG-Disk_201905290900.bz2']
        os.system('cp /data/ingest/S-LSA_-HDF5_LSASAF_MSG_ET_MSG-Disk_201905290900.bz2 /data/ingest/test/')
        in_date = '201905290900'

        productcode = 'lsasaf-et'
        productversion = 'undefined'
        subproductcode = 'et'
        mapsetcode = 'MSG-satellite-3km'
        datasource_descrID='EO:EUM:DAT:MSG:ET-SEVIRI'

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
        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)
    #   ---------------------------------------------------------------------------
    #    Miscellaneous - LSASAF ET \\Not yet tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_lsasaf_et(self):

        date_fileslist = ['/data/TestIngestion/S-LSA_-HDF5_LSASAF_MSG_ET_SAfr_201511301000.bz2']
        in_date = '201511301000'
        productcode = 'lsasaf-et'
        productversion = 'undefined'
        subproductcode = 'et'
        mapsetcode = 'MSG-satellite-3km'
        datasource_descrID='EO:EUM:DAT:MSG:ET-SEVIRI'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

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

    #   ---------------------------------------------------------------------------
    #   INLAND WATER - WBD AVG \\Not yet tested\\
    #   ---------------------------------------------------------------------------

    def test_ingest_jrc_wbd_avg(self):

        date_fileslist = glob.glob('/data/ingest/JRC-WBD-AVG-ICPAC_1985-2015_1201*')
        #date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
        in_date = '1201'
        productcode = 'wd-gee'
        productversion = '1.0'
        subproductcode = 'avg'
        mapsetcode = 'WD-GEE-ECOWAS-AVG'
        datasource_descrID='JRC:WBD:GEE:AVG'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

    #   ---------------------------------------------------------------------------
    #   INLAND WATER - WBD AVG \\Not yet tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_jrc_wbd_avg_tarzip(self):

        date_fileslist = glob.glob('/data/ingest/MESA_JRC_wd-gee_avg_1201_WD-GEE-IGAD-AVG_1.0.tgz')
        # date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
        in_date = '1201'
        productcode = 'wd-gee'
        productversion = '1.0'
        subproductcode = 'avg'
        mapsetcode = 'WD-GEE-IGAD-AVG'
        datasource_descrID = 'EO:EUM:DAT:LANDSAT:MESA-JRC-WBD-GEE-AVG'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

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

    #   ---------------------------------------------------------------------------
    #   INLAND WATER - WBD OCC \\Not yet tested\\
    #   ---------------------------------------------------------------------------
    def test_ingest_jrc_wbd_occ(self):


        date_fileslist = glob.glob('/data/ingest/JRC-WBD_ICPAC_20181201*.tif')
        in_date = '20181201'
        productcode = 'wd-gee'
        productversion = '1.0'
        subproductcode = 'occurr'
        mapsetcode = 'WD-GEE-IGAD-AVG'
        datasource_descrID='JRC:WBD:GEE'

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

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

        self.assertEqual(1, 1)

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


suite_ingestion = unittest.TestLoader().loadTestsFromTestCase(TestIngestion)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_ingestion)