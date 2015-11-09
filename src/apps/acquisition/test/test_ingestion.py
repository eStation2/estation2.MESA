_author__ = "Marco Clerici"


from config import es_constants
from apps.acquisition import ingestion
from database import querydb
import unittest
import os
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
        file_mcd14dl = es_constants.es2globals['ingest_dir'] + 'Global_MCD14DL_2015042.txt'
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

        date_fileslist = ['/data/ingest/A2015189.L3m_DAY_SST_sst_4km.nc']
        in_date = '2015189'
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

        product_in_info = querydb.get_product_in_info(echo=1, **args)

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

        date_fileslist = ['/data/ingest/A2015189.L3m_DAY_CHL_chlor_a_4km.nc']
        in_date = '2015189'
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

        product_in_info = querydb.get_product_in_info(echo=1, **args)

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

        date_fileslist = ['/data/ingest/A2015189.L3m_DAY_KD490_Kd_490_4km.nc']
        in_date = '2015189'
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

        product_in_info = querydb.get_product_in_info(echo=1, **args)

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

        product_in_info = querydb.get_product_in_info(echo=1, **args)

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

        product_in_info = querydb.get_product_in_info(echo=1, **args)

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

    def test_ingest_eumetcast(self):

        # input_file='/data/archives/MESA_JRC_vgt-ndvi_ndv_20020421_SPOTV-Africa-1km_spot-v1.tif'
        # # target_mapset='SPOTV-Africa-1km'
        # target_mapset='SPOTV-ECOWAS-1km'
        # ingestion.ingest_file_archive(input_file, target_mapset, echo_query=False)()

        ingestion.ingest_archives_eumetcast()
