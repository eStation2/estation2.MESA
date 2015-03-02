_author__ = "Marco Clerici"


from config import es_constants
from apps.acquisition import ingestion

import unittest
import os
# Overwrite Dirs

class TestIngestion(unittest.TestCase):

    def TestDriveAll(self):
        ingestion.drive_ingestion()
        self.assertEqual(1, 1)


    def test_ingest_vgt_ndvi(self):
        
        productcode = 'vgt_ndvi'
        productversion = 'undefined'
        subproductcode = 'ndvi_native'
        mapsetcode = 'WGS84_Africa_1km'
        
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": '',
                "version": productversion}
        
        product_in_info = querydb.get_product_in_info(echo=echo_query, **args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': ingest.subproductcode,
                             'mapsetcode': ingest.mapsetcode,
                             're_extract': re_extract,
                             're_process': re_process}

        subproducts.append(sprod)
        
        ingestion(date_fileslist, in_date, product, subproducts, datasource_descr, echo_query=echo_query)

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
