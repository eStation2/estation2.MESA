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
import h5py
from lib.python import functions

from osgeo import gdal

# Overwrite Dirs
from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestIngestion(unittest.TestCase):

    def TestDriveAll(self):
        ingestion.drive_ingestion()
        self.assertEqual(1, 1)

    def test_ingest_modis_firms_nasa(self):

        # This is for MCD14DL format from ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global
        # having columns as: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp

        # Definitions
        myfile='Global_MCD14DL_2015042.txt'
        file_mcd14dl = es_constants.es2globals['ingest_dir'] + myfile
        shutil.copy('/data/processing/modis-firms/v5.0/archive/'+myfile, file_mcd14dl)
        pix_size = '0.008928571428571'
        # Create a temporary working dir
        tmpdir='/tmp/eStation2/test_ingest_firms_nasa/'
        file_vrt=tmpdir+"firms_file.vrt"
        file_csv=tmpdir+"firms_file.csv"
        file_tif=tmpdir+"firms_file.tif"
        out_layer="firms_file"
        file_shp=tmpdir+out_layer+".shp"

        # Write the 'vrt' file
        with open(file_vrt,'w') as outFile:
            outFile.write('<OGRVRTDataSource>\n')
            outFile.write('    <OGRVRTLayer name="firms_file">\n')
            outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
            outFile.write('        <OGRVRTLayer name="firms_file" />\n')
            outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
            outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
            outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
            outFile.write('    </OGRVRTLayer>\n')
            outFile.write('</OGRVRTDataSource>\n')

        # Generate the csv file with header
        with open(file_csv,'w') as outFile:
            #outFile.write('latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp')
            with open(file_mcd14dl, 'r') as input_file:
                outFile.write(input_file.read())

        # Execute the ogr2ogr command
        command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
        #print('['+command+']')
        os.system(command)

        # Convert from shapefile to rasterfile
        command = 'gdal_rasterize  -l ' + out_layer + ' -burn 1 '\
                  + ' -tr ' + str(pix_size) + ' ' + str(pix_size) \
                  + ' -co "compress=LZW" -of GTiff -ot Byte '     \
                  +file_shp+' '+file_tif

        #print('['+command+']')
        os.system(command)

    def test_ingest_modis_firms_nasa_6(self):

        # This is for MCD14DL format from ftp://nrt3.modaps.eosdis.nasa.gov/FIRMS/c6/Global
        # having columns as: latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp

        # Definitions
        myfile='MODIS_C6_Global_MCD14DL_NRT_2016024.txt'
        file_mcd14dl = es_constants.es2globals['ingest_dir'] + myfile
        # shutil.copy('/data/processing/modis-firms/v5.0/archive/'+myfile, file_mcd14dl)
        pix_size = '0.008928571428571'
        # Create a temporary working dir
        tmpdir='/tmp/eStation2/test_ingest_firms_nasa/'
        file_vrt=tmpdir+"firms_file.vrt"
        file_csv=tmpdir+"firms_file.csv"
        file_tif=tmpdir+"firms_file.tif"
        out_layer="firms_file"
        file_shp=tmpdir+out_layer+".shp"

        # Write the 'vrt' file
        with open(file_vrt,'w') as outFile:
            outFile.write('<OGRVRTDataSource>\n')
            outFile.write('    <OGRVRTLayer name="firms_file">\n')
            outFile.write('        <SrcDataSource>'+file_csv+'</SrcDataSource>\n')
            outFile.write('        <OGRVRTLayer name="firms_file" />\n')
            outFile.write('        <GeometryType>wkbPoint</GeometryType>\n')
            outFile.write('        <LayerSRS>WGS84</LayerSRS>\n')
            outFile.write('        <GeometryField encoding="PointFromColumns" x="longitude" y="latitude" />\n')
            outFile.write('    </OGRVRTLayer>\n')
            outFile.write('</OGRVRTDataSource>\n')

        # Generate the csv file with header
        with open(file_csv,'w') as outFile:
            #outFile.write('latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp')
            with open(file_mcd14dl, 'r') as input_file:
                outFile.write(input_file.read())

        # Execute the ogr2ogr command
        command = 'ogr2ogr -f "ESRI Shapefile" ' + file_shp + ' '+file_vrt
        #print('['+command+']')
        os.system(command)

        # Convert from shapefile to rasterfile
        command = 'gdal_rasterize  -l ' + out_layer + ' -burn 1 '\
                  + ' -tr ' + str(pix_size) + ' ' + str(pix_size) \
                  + ' -co "compress=LZW" -of GTiff -ot Byte '     \
                  +file_shp+' '+file_tif

        #print('['+command+']')
        os.system(command)

    def test_ingest_modis_sst_netcdf(self):

        date_fileslist = ['/data/ingest/A2017218.L3m_DAY_SST_sst_4km.nc']
        in_date = '2017218'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

    def test_ingest_modis_chlor_netcdf(self):

        date_fileslist = ['/data/ingest/A2016225.L3m_DAY_CHL_chlor_a_4km.nc']
        in_date = '2016207'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

    def test_ingest_pml_modis_sst(self):

        date_fileslist = ['/data/ingest/PML_Tanzania_MODIS_sst_3daycomp_20160118_20160120.nc.bz2']
        in_date = '20160118'
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

        sprod = {'subproduct': subproductcode,
                             'mapsetcode': mapsetcode,
                             're_extract': re_extract,
                             're_process': re_process}

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1, nodata_value=-999)

            self.assertEqual(1, 1)

    def test_ingest_pml_modis_oc(self):

        date_fileslist = ['/data/ingest/PML_CapeVerde_MODIS_oc_3daycomp_20160228_20160301.nc.bz2']
        in_date = '20160228'
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

        sprod = {'subproduct': subproductcode,
                             'mapsetcode': mapsetcode,
                             're_extract': re_extract,
                             're_process': re_process}

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1, nodata_value=-999)

            self.assertEqual(1, 1)

    def test_ingest_lsasaf_et(self):

        date_fileslist = ['/data/ingest/test/S-LSA_-HDF5_LSASAF_MSG_ET_NAfr_201511040900.bz2','/data/ingest/test/S-LSA_-HDF5_LSASAF_MSG_ET_SAfr_201511040900.bz2']
        in_date = '201511040900'
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

        subproducts=[]
        subproducts.append(sprod)

    def test_ingest_lsasaf_et_disk(self):

        date_fileslist = ['/data/temp/lsasaf-et/HDF5_LSASAF_MSG_ET_MSG-Disk_201601010000.bz2']
        in_date = '201601011200'

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_chirps(self):

        date_fileslist = ['/data/ingest/test/chirps-v2.0.2016.02.1.tif.gz']
        in_date = '2016.02.1'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            #self.assertEqual(1, 1)

    def test_ingest_chirps_tif(self):

        date_fileslist = ['/data/ingest/chirps-v2.0.2017.02.1.tif']
        in_date = '2017.02.1'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            #self.assertEqual(1, 1)

    def test_ingest_jrc_wbd(self):

        date_fileslist = glob.glob('/data/processing/wd-gee/1.0/for_ingest/JRC-WBD_20161101*')
        #date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
        in_date = '20161101'
        productcode = 'wd-gee'
        productversion = '1.0'
        subproductcode = 'occurr'
        mapsetcode = 'WD-GEE-ECOWAS-AVG'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            self.assertEqual(1, 1)

    def test_preprocess_ecmwf_mars(self):

        date_fileslist = ['/data/temp/ope_africa_rain_20160221.zip']
        in_date = '20160221'
        tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(date_fileslist[0]),
                                  dir=es_constants.base_tmp_dir)

        ingestion.pre_process_ecmwf_mars(tmpdir, date_fileslist, logger)

        self.assertEqual(1, 1)

    def test_ingest_ecmwf_rain(self):

        date_fileslist = ['/data/ingest/test/ope_africa_rain_20160221.zip']
        in_date = '20160221'
        productcode = 'ecmwf-rain'
        productversion = 'OPE'
        subproductcode = '10d'
        mapsetcode = 'ECMWF-Africa-25km'
        datasource_descrID='ECMWF:MARS:RAIN:OPE'

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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

            #self.assertEqual(1, 1)

    def test_ingest_eumetcast(self):

        # input_file='/data/archives/MESA_JRC_vgt-ndvi_ndv_20020421_SPOTV-Africa-1km_spot-v1.tif'
        # # target_mapset='SPOTV-Africa-1km'
        # target_mapset='SPOTV-ECOWAS-1km'
        # ingestion.ingest_file_archive(input_file, target_mapset, echo_query=False)()

        ingestion.ingest_archives_eumetcast()

    # def test_ingest_jrc_wbd(self):
    #
    #     date_fileslist = glob.glob('/data/ingest/JRC-WBD_*')
    #     #date_fileslist = ['/data/ingest/test/JRC_WBD/JRC-WBD_20151201-0000000000-0000000000.tif']
    #     in_date = '20160101'
    #     productcode = 'wd-gee'
    #     productversion = '1.0'
    #     subproductcode = 'occurr'
    #     mapsetcode = 'WD-GEE-ECOWAS-AVG'
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
    #     subproducts=[]
    #     subproducts.append(sprod)
    #
    #     for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
    #                                                                           source_id=datasource_descrID):
    #
    #         ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)
    #
            #self.assertEqual(1, 1)

    def test_ingest_ecmwf_evtp(self):

        date_fileslist = ['/data/ingest/ope_africa_evpt_20170401.zip']
        in_date = '20170401'
        productcode = 'ecmwf-evpt'
        productversion = 'OPE'
        subproductcode = '10d'
        mapsetcode = 'ECMWF-Africa-25km'
        datasource_descrID='ECMWF:MARS:EVPT:OPE'

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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_msg_mpe(self):

        date_fileslist = glob.glob('/data/ingest/L-000-MSG3__-MPEF________-MPEG_____-000002___-201711*')
        in_date = '201711282230'
        productcode = 'msg-mpe'
        productversion = 'undefined'
        subproductcode = 'mpe'
        mapsetcode = 'MSG-satellite-3km'
        datasource_descrID='EO:EUM:DAT:MSG:MPE-GRIB'

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

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        #for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
         #                                                                     source_id=datasource_descrID):

        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

    def test_ingest_arc2_rain(self):

        date_fileslist = glob.glob('/data/ingest/africa_arc.20160501.tif.zip')
        in_date = '20160501'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

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

    def test_ingest_gsod_rain(self):

        filename='*-99999-2016.op.gz'
        os.system('cp /data/temp/Data/GSOD/'+filename+' /data/ingest/')
        date_fileslist = glob.glob('/data/ingest/'+filename)
        in_date='20160501'
        productcode = 'gsod-rain'
        productversion = '1.0'
        subproductcode = '1dmeas'
        mapsetcode = 'SPOTV-SADC-1km'
        datasource_descrID='NOAA:GSOD'

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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, '20160503', product, subproducts, datasource_descr, logger, echo_query=1)
            ingestion.ingestion(date_fileslist, '20160504', product, subproducts, datasource_descr, logger, echo_query=1)
            ingestion.ingestion(date_fileslist, '20160505', product, subproducts, datasource_descr, logger, echo_query=1)
            ingestion.ingestion(date_fileslist, '20160506', product, subproducts, datasource_descr, logger, echo_query=1)
            ingestion.ingestion(date_fileslist, '20160507', product, subproducts, datasource_descr, logger, echo_query=1)
            ingestion.ingestion(date_fileslist, '20160508', product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_cpc_soilmoisture(self):

        filename='w.201609.mon'
        shutil.copy('/data/processing/exchange/'+filename,'/data/ingest/'+filename)
        date_fileslist = glob.glob('/data/ingest/w.201609.mon')
        in_date = '201201'
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_sadc_wrsi(self):

        filename='WRSI2016*'
        os.system('cp /data/processing/exchange/WRSI/'+filename+' /data/ingest/')
        date_fileslist = glob.glob('/data/ingest/'+filename+'.bil')
        in_date = '201632'
        productcode = 'wrsi-sadc'
        productversion = '1.0'
        subproductcode = 'wrsi'
        mapsetcode = 'GEOWRSI-SADC-11km'
        datasource_descrID='BDMS:SADC:GEOWRSI:WRSI'

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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_mpe_umarf(self):

        date_fileslist = glob.glob('/data/native/DISK_MSG_MPE/MSG3*201609301200*gz')
        in_date = '201609301200'
        productcode = 'msg-mpe'
        productversion = 'undefined'
        subproductcode = 'mpe'
        mapsetcode = 'MSG-satellite-3km'
        datasource_descrID='EO:EUM:DAT:MSG:MPE-UMARF'

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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                              source_id=datasource_descrID):

            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_g_cls_ndvi_2_2_netcdf(self):


        file = '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.nc'
        outputfile= '/data/TestIngestion/c_gls_NDVI_201401010000_AFRI_PROBAV_V2.2.1.tif'

        # hdf = gdal.Open('HDF5:'+file+'://NDVI')
        hdf = gdal.Open(file)
        sdsdict = hdf.GetMetadata('SUBDATASETS')

        # sdslist = in_ds.GetSubDatasets()
        # in_ds = gdal.Open('HDF5:'+file+'://NDVI')
        ingestion.write_ds_to_geotiff(hdf, outputfile)
        print sdsdict
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

        subproducts=[]
        subproducts.append(sprod)

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):
            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_g_cls_ndvi_2_2_global(self):


        # Similar to the test above, but specific to the products made available for Long Term Statistics by T. Jacobs
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_201706*_GLOBE_PROBAV_V2.2.1.nc')
        # date_fileslist = glob.glob('/spatial_data/data/native/GLOBAL_NDVI_2.2/c_gls_NDVI_19*_GLOBE_VGT_V2.2.1.nc')
        date_fileslist = glob.glob('/data/ingest/c_gls_NDVI_201706*_GLOBE_PROBAV_V2.2.1.*')

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

            for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='INTERNET',
                                                                                  source_id=datasource_descrID):
                ingestion.ingestion(one_file, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_g_cls_fapar_2_0_1(self):

        # Test Copernicus Products version 2.0.1 (for FAPAR)
        # Products released from VITO in March 2017

        date_fileslist = glob.glob('/data/TestIngestion/c_gls_FAPAR-RT0_201704100000_AFRI_PROBAV_V2.0.1.zip*')
        in_date = '201704100000'
        productcode = 'vgt-fapar'
        productversion = 'V2.0'
        subproductcode = 'fapar'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:PROBA-V2.0:FAPAR'


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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):
            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_sadc_vci_v1(self):

        # Test VCI product disseminated by BDMS

        date_fileslist = glob.glob('/data/TestIngestion/AMESD_SADC_VCI________20171111_SAfri_v2.zip')
        in_date = '20171111'
        productcode = 'sadc-vci'
        productversion = 'v1'
        subproductcode = 'sadc-vci'
        mapsetcode = 'SPOTV-SADC-1km'
        datasource_descrID='EO:EUM:DAT:MULT:VCI'


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

        for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
                                                                              source_id=datasource_descrID):
            ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, logger, echo_query=1)

    def test_ingest_s3_olci_wrr(self):

        # Test the ingestion of the Sentinel-3/OLCI Level-2 WRR product (on d6-dev-vm19 !!!!!)
        #date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_OL_2_WRR/S3A_OL_2_WRR____20180306T092820_20180306T101211_20180306T115859_2631_028_307______MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_OL_2_WRR/march08/S3A_OL_2_WRR____*.SEN3.tar')
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

        subproducts=[]
        subproducts.append(sprod)

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

    def test_ingest_s3_olci_wrr_chl_oc4me(self):

        # Test the ingestion of the Sentinel-3/OLCI Level-2 WRR product (on d6-dev-vm19 !!!!!)
        date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_OL_2_WRR/march08/S3A_OL_2_WRR____*.SEN3.tar')
        single_date =  os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0] #+ '0000'
        productcode = 'olci-wrr'
        productversion = 'V02.0'
        subproductcode = 'chl-oc4me'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID='EO:EUM:DAT:SENTINEL-3:OL_2_WRR___NRT'


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

        subproducts=[]
        subproducts.append(sprod)

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                                       source_id=datasource_descrID):
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)

    def test_ingest_s3_slstr_sst(self):

        # Test the ingestion of the Sentinel-3/SLSTR Level-2 WST product (on d6-dev-vm19 !!!!!)
        #date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/S3A_SL_2_WST____20180306T095629_20180306T095929_20180306T114727_0179_028_307_3420_MAR_O_NR_002.SEN3.tar')
        date_fileslist = glob.glob('/data/processing/exchange/Sentinel-3/S3A_SL_2_WST/march06/S3A_SL_2_WST____20180306T08*.SEN3.tar')
        single_date =  os.path.basename(date_fileslist[0])
        in_date = single_date.split('_')[7]
        in_date = in_date.split('T')[0] #+ '0000'
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

        subproducts = []
        subproducts.append(sprod)


        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                         source_id=datasource_descrID)
        # for internet_filter, datasource_descr in querydb.get_datasource_descr(source_type='EUMETCAST',
        #                                                                       source_id=datasource_descrID):
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger, echo_query=1)



