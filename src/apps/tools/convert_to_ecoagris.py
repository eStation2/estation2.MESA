from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

# purpose:  Generate timeseries values for a list of indicators over all geometries in the given vector layer
#           and convert these values to ECOAGRIS format (MySQL).
# author:   M.Clerici, Jurriaan van 't Klooster
# date:	    18.09.2018
# descr:    Loop over a list of indicators and for each indicator loop over all geometries in the input vector layer
#           and generate the time series value for each indicator's tif file (a date depending on the frequency of
#           the indicator). Save each value with corresponding info in a new table in the database.
#           Then generate a MySQL script to import all these records in the ECOAGRIS database.
# usage:    python convert_to_ecoagris.py $vector_layer_path $vector_layer_id_attribute
# history:  1.0
#

from builtins import dict
from builtins import round
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import range
from past.utils import old_div
import os
# import glob
import shutil
import argparse
import numpy.ma as ma
import math
import tempfile
import datetime

try:
    from osgeo import gdal
    from osgeo import gdal_array
    from osgeo import ogr, osr
    from osgeo import gdalconst
except ImportError:
    import gdal
    import gdal_array
    import ogr
    import osr
    import gdalconst

from config import es_constants
from database import querydb
from database import crud
from apps.productmanagement.products import Product
from apps.acquisition.ingestion import conv_data_type_to_gdal
from lib.python import es_logging as log
from lib.python import functions

logger = log.my_logger(__name__)


def convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel):

    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    productcode = productinfo['productcode']
    subproductcode = productinfo['subproductcode']
    version = productinfo['version']
    mapsetcode = productinfo['mapsetcode']

    product_info = querydb.get_product_out_info(productcode=productcode,
                                                subproductcode=subproductcode,
                                                version=version)
    if product_info.__len__() > 0:
        for row in product_info:
            product_descriptive_name = row.descriptive_name
            product_description = row.description
            product_dateformat = row.date_format
            product_provider = row.provider
    else:
        logger.error('Product does not exist: %s - %s - %s - %s' % productcode, version, subproductcode, mapsetcode)
        exit()

    from_date = datetime.datetime.strptime(startdate, '%Y-%m-%d').date()
    to_date = datetime.datetime.strptime(enddate, '%Y-%m-%d').date()

    filename, file_extension = os.path.splitext(vectorlayer)
    if file_extension == '.shp':
        driver = ogr.GetDriverByName('ESRI Shapefile')
    elif file_extension == '.geojson':
        driver = ogr.GetDriverByName('GeoJSON')
    else:
        logger.error('Vector layer file in a wrong format or has a wrong extention: %s' % vectorlayer)
        exit()

    vectorlayer = driver.Open(vectorlayer)

    # Get Projection from layer
    layer = vectorlayer.GetLayer()
    # spatialRef = layer.GetSpatialRef()

    # Get Shapefile Fields and Types
    layerDefinition = layer.GetLayerDefn()

    idattr_exists = False
    for i in range(layerDefinition.GetFieldCount()):
        fieldName = layerDefinition.GetFieldDefn(i).GetName()
        # fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
        # fieldType = layerDefinition.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
        # fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
        # GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()
        # print fieldName + " - " + fieldType + " " + str(fieldWidth) + " " + str(GetPrecision)
        if fieldName == regionidattr:
            idattr_exists = True

    if not idattr_exists:
        logger.error('ID Attribute does not exist in vector layer: %s' % regionidattr)
        return

    for feature in layer:
        geom = feature.GetGeometryRef()
        # wkt = geom.ExportToWkt()
        regionid = feature.GetField(regionidattr)

        delete_ecoagrisrec = {
            "productcode": productcode,
            "subproductcode": subproductcode,
            "version": version,
            "mapsetcode": mapsetcode,
            "regionid": regionid,
            'aggregation_type': aggregateinfo['aggregation_type'],
        }

        if crud_db.delete('ecoagris', **delete_ecoagrisrec):
            logger.info('ecoagris record deleted')
        else:
            logger.error('Error deleting ecoagris record')

        timeseries = getTimeseries(productcode, subproductcode, version, mapsetcode, geom, from_date, to_date, aggregateinfo)
        # Loop through the timeseries and get each date/value and create a record
        for timeserie in timeseries:
            if timeserie['meanvalue'] not in [None, '']:
                productdate = timeserie['date'].strftime("%Y%m%d")
                if product_dateformat == 'YYYYMMDDHHMM':
                    productdate = timeserie['date'].strftime("%Y%m%d%H%M")
                if product_dateformat == 'YYYYMMDD':
                    productdate = timeserie['date'].strftime("%Y%m%d")
                if product_dateformat == 'YYYYMM':
                    productdate = timeserie['date'].strftime("%Y%m")
                if product_dateformat == 'YYYY':
                    productdate = timeserie['date'].strftime("%Y")
                if product_dateformat == 'MMDD':
                    productdate = timeserie['date'].strftime("%m%d")

                ecoagris_record = {
                    "productcode": productcode,
                    "subproductcode": subproductcode,
                    "version": version,
                    "mapsetcode": mapsetcode,
                    "product_descriptive_name": product_descriptive_name,
                    "product_description": product_description,
                    "provider": product_provider,
                    "regionid": regionid,
                    "regionlevel": regionlevel,
                    'aggregation_type': aggregateinfo['aggregation_type'],
                    'aggregation_min': aggregateinfo['aggregation_min'],
                    'aggregation_max': aggregateinfo['aggregation_max'],
                    "product_dateformat": product_dateformat,
                    "product_date": productdate,
                    "tsvalue": timeserie['meanvalue']
                }
                # print ecoagris_record
                # Insert record in DB table ecoagris
                if crud_db.create('ecoagris', ecoagris_record):
                    logger.info('ecoagris record created')
                else:
                    logger.error('Error creating ecoagris record')

        # Return the latest computed record (M.C.)
        return ecoagris_record


def getFilesList(productcode, subproductcode, version, mapsetcode, date_format, start_date, end_date):
    #    Generate a list of files (possibly with repetitions) for extracting timeseries
    #    It applies to a single dataset (prod/sprod/version/mapset) and between 2 dates
    #

    # Prepare for results
    list_files = []
    dates_list = []

    # print productcode
    # print subproductcode
    # print version
    # print mapsetcode
    # print date_format
    # print start_date
    # print end_date

    p = Product(product_code=productcode, version=version)
    dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)
    dataset.get_filenames()

    if date_format == 'YYYYMMDD':
        # Loop over dates
        for date in dataset._frequency.get_dates(start_date, end_date):
            if (date >= start_date) and (date <= end_date):
                filedate = date.strftime("%Y%m%d")
                productfilename = functions.set_path_filename(filedate, productcode, subproductcode, mapsetcode, version, '.tif')
                productfilepath = dataset.fullpath + productfilename
                dates_list.append(date)
                if os.path.isfile(productfilepath):
                    list_files.append(productfilepath)
                    # dates_list.append(date)
                else:
                    list_files.append('')

    if date_format == 'MMDD':
        # Extract MMDD
        mmdd_start = start_date.month*100+start_date.day
        mmdd_end = end_date.month*100+end_date.day

        # Case 1: same year
        if start_date.year == end_date.year:
            for mmdd in dataset.get_mmdd():
                if mmdd_start <= int(mmdd) <= mmdd_end:
                    # mmdd contains the list of existing 'mmdd' - sorted
                    productfilename = functions.set_path_filename(mmdd, productcode, subproductcode, mapsetcode, version, '.tif')
                    productfilepath = dataset.fullpath + productfilename
                    list_files.append(productfilepath)
                    dates_list.append(datetime.date(start_date.year, int(mmdd[:2]), int(mmdd[2:4])))
            # Debug only
            # logger.info(list_files)

        # Case 2: end_year > start_year
        if start_date.year < end_date.year:
            # list_mmdd contains the list of existing 'mmdd' - sorted
            list_mmdd = dataset.get_mmdd()
            # Put all dates from start_mmdd to end of the year
            for mmdd in list_mmdd:
                if int(mmdd) >= mmdd_start:
                    productfilename = functions.set_path_filename(mmdd, productcode, subproductcode, mapsetcode, version, '.tif')
                    productfilepath = dataset.fullpath + productfilename
                    list_files.append(productfilepath)
                    dates_list.append(datetime.date(start_date.year, int(mmdd[:2]), int(mmdd[2:4])))

            # Fill the list with 'full' years
            for n_years in range(end_date.year-start_date.year-1):
                for mmdd in list_mmdd:
                    productfilename = functions.set_path_filename(mmdd, productcode, subproductcode, mapsetcode, version, '.tif')
                    productfilepath = dataset.fullpath + productfilename
                    list_files.append(productfilepath)
                    dates_list.append(datetime.date(start_date.year+1+n_years, int(mmdd[:2]), int(mmdd[2:4])))

            # Put all dates from begin of the year to end_mmdd
            for mmdd in list_mmdd:
                if int(mmdd) <= mmdd_end:
                    # mmdd contains the list of existing 'mmdd' - sorted
                    productfilename = functions.set_path_filename(mmdd, productcode, subproductcode, mapsetcode, version, '.tif')
                    productfilepath = dataset.fullpath + productfilename
                    list_files.append(productfilepath)
                    dates_list.append(datetime.date(end_date.year, int(mmdd[:2]), int(mmdd[2:4])))

            # logger.info(list_files)

    return [list_files, dates_list]


def getTimeseries(productcode, subproductcode, version, mapsetcode, geom, start_date, end_date, aggregate):

    #    Extract timeseries from a list of files and return as JSON object
    #    It applies to a single dataset (prod/sprod/version/mapset) and between 2 dates
    #    Several types of aggregation foreseen:
    #
    #       mean :      Sum(Xi)/N(Xi)        -> min/max not considered          e.g. Rain
    #       cumulate:   Sum(Xi)              -> min/max not considered          e.g. Fire
    #
    #       count:      N(Xi where min < Xi < max)                              e.g. Vegetation anomalies
    #       surface:    count * PixelArea                                       e.g. Water Bodies
    #       percent:    count/Ntot                                              e.g. Vegetation anomalies
    #       precip:     compute the precipitation volume in m3*1E6              Rain (only)
    #
    #   History: 1.0 :  Initial release - since 2.0.1 -> now renamed '_green' from greenwich package
    #            1.1 :  Since Feb. 2017, it is based on a different approach (gdal.RasterizeLayer instead of greenwich)
    #                   in order to solve the issue with MULTIPOLYGON
    #

    ogr.UseExceptions()

    # Get Mapset Info
    mapset_info = querydb.get_mapset(mapsetcode=mapsetcode)

    # Prepare for computing conversion to area: the pixel size at Lat=0 is computed
    # The correction to the actual latitude (on AVERAGE value - will be computed below)
    const_d2km = 12364.35
    area_km_equator = abs(float(mapset_info.pixel_shift_lat)) * abs(float(mapset_info.pixel_shift_long)) * const_d2km

    # Get Product Info
    product_info = querydb.get_product_out_info(productcode=productcode,
                                                subproductcode=subproductcode,
                                                version=version)
    if product_info.__len__() > 0:
        # Get info from product_info
        scale_factor = 0
        scale_offset = 0
        nodata = 0
        date_format = ''
        for row in product_info:
            scale_factor = row.scale_factor
            scale_offset = row.scale_offset
            nodata = row.nodata
            date_format = row.date_format
            date_type = row.data_type_id

        # Create an output/temp shapefile, for managing the output layer (really mandatory ?? Can be simplified ???)
        try:
            tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_getTimeseries',
                                      dir=es_constants.base_tmp_dir)
        except:
            logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
            raise NameError('Error in creating tmpdir')

        out_shape = tmpdir+os.path.sep+"output_shape.shp"
        outDriver = ogr.GetDriverByName('ESRI Shapefile')

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(out_shape)
        dest_srs = ogr.osr.SpatialReference()
        dest_srs.ImportFromEPSG(4326)

        outLayer = outDataSource.CreateLayer("Layer", dest_srs)
        # outLayer = outDataSource.CreateLayer("Layer")
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        outLayer.CreateField(idField)

        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(geom)
        # area = geom.GetArea()
        feature.SetField("id", 1)
        outLayer.CreateFeature(feature)
        feature = None

        [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, start_date, end_date)

        # Built a dictionary with filenames/dates
        dates_to_files_dict = dict(list(zip(dates_list, list_files)))

        # Generate unique list of files
        unique_list = set(list_files)
        uniqueFilesValues = []

        geo_mask_created = False
        for infile in unique_list:
            single_result = {'filename': '', 'meanvalue_noscaling': nodata, 'meanvalue': None}

            if infile.strip() != '' and os.path.isfile(infile):
                # try:

                    # Open input file
                    orig_ds = gdal.Open(infile, gdal.GA_ReadOnly)
                    orig_cs = osr.SpatialReference()
                    orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
                    orig_geoT = orig_ds.GetGeoTransform()
                    x_origin = orig_geoT[0]
                    y_origin = orig_geoT[3]
                    pixel_size_x = orig_geoT[1]
                    pixel_size_y = -orig_geoT[5]

                    in_data_type_gdal = conv_data_type_to_gdal(date_type)

                    # Create a mask from the geometry, with the same georef as the input file[s]
                    if not geo_mask_created:

                        # Read polygon extent and round to raster resolution
                        x_min, x_max, y_min, y_max = outLayer.GetExtent()
                        x_min_round = int(old_div((x_min-x_origin),pixel_size_x))*pixel_size_x+x_origin
                        x_max_round = (int(old_div((x_max-x_origin),(pixel_size_x)))+1)*pixel_size_x+x_origin
                        y_min_round = (int(old_div((y_min-y_origin),(pixel_size_y)))-1)*pixel_size_y+y_origin
                        y_max_round = int(old_div((y_max-y_origin),(pixel_size_y)))*pixel_size_y+y_origin
                    #
                    #     # Create the destination data source
                        x_res = int(round(old_div((x_max_round - x_min_round), pixel_size_x)))
                        y_res = int(round(old_div((y_max_round - y_min_round), pixel_size_y)))
                    #
                    #     # Create mask in memory
                        mem_driver = gdal.GetDriverByName('MEM')
                        mem_ds = mem_driver.Create('', x_res, y_res, 1, in_data_type_gdal)
                        mask_geoT = [x_min_round, pixel_size_x, 0, y_max_round, 0, -pixel_size_y]
                        mem_ds.SetGeoTransform(mask_geoT)
                        mem_ds.SetProjection(orig_cs.ExportToWkt())
                    #
                    #     # Create a Layer with '1' for the pixels to be selected
                        gdal.RasterizeLayer(mem_ds, [1], outLayer, burn_values=[1])
                        # gdal.RasterizeLayer(mem_ds, [1], outLayer, None, None, [1])

                        # Read the polygon-mask
                        band = mem_ds.GetRasterBand(1)
                        geo_values = mem_ds.ReadAsArray()

                        # Create a mask from geo_values (mask-out the '0's)
                        geo_mask = ma.make_mask(geo_values == 0)
                        geo_mask_created = True
                    #
                    #     # Clean/Close objects
                        mem_ds = None
                        mem_driver = None
                        outDriver = None
                        outLayer = None

                    # Read data from input file
                    x_offset = int(old_div((x_min-x_origin),pixel_size_x))
                    y_offset = int(old_div((y_origin-y_max),pixel_size_y))

                    band_in = orig_ds.GetRasterBand(1)
                    data = band_in.ReadAsArray(x_offset, y_offset, x_res, y_res)
                    #   Catch the Error ES2-105 (polygon not included in Mapset)
                    if data is None:
                        logger.error('ERROR: polygon extends out of file mapset for file: %s' % infile)
                        return []

                    # Create a masked array from the data (considering Nodata)
                    masked_data = ma.masked_equal(data, nodata)

                    # Apply on top of it the geo mask
                    mxnodata = ma.masked_where(geo_mask, masked_data)

                    # Test ONLY
                    # write_ds_to_geotiff(mem_ds, '/data/processing/exchange/Tests/mem_ds.tif')

                    if aggregate['aggregation_type'] == 'count' or aggregate['aggregation_type'] == 'percent' or aggregate['aggregation_type'] == 'surface' or aggregate['aggregation_type'] == 'precip':

                        if mxnodata.count() == 0:
                            meanResult = None
                        else:
                            mxrange = mxnodata
                            min_val = aggregate['aggregation_min']
                            max_val = aggregate['aggregation_max']

                            if min_val is not None:
                                min_val_scaled = old_div((min_val - scale_offset), scale_factor)
                                mxrange = ma.masked_less(mxnodata, min_val_scaled)

                                # See ES2-271
                                if max_val is not None:
                                    # Scale threshold from physical to digital value
                                    max_val_scaled = old_div((max_val - scale_offset), scale_factor)
                                    mxrange = ma.masked_greater(mxrange, max_val_scaled)

                            elif max_val is not None:
                                # Scale threshold from physical to digital value
                                max_val_scaled = old_div((max_val - scale_offset), scale_factor)
                                mxrange = ma.masked_greater(mxnodata, max_val_scaled)

                            if aggregate['aggregation_type'] == 'percent':
                                # 'percent'
                                meanResult = float(mxrange.count())/float(mxnodata.count()) * 100

                            elif aggregate['aggregation_type'] == 'surface':
                                # 'surface'
                                # Estimate 'average' Latitude
                                y_avg = (y_min + y_max)/2.0
                                pixelAvgArea = area_km_equator * math.cos(old_div(y_avg, 180) * math.pi)
                                meanResult = float(mxrange.count()) * pixelAvgArea
                            elif aggregate['aggregation_type'] == 'precip':
                                # 'surface'
                                # Estimate 'average' Latitude
                                y_avg = (y_min + y_max) / 2.0
                                pixelAvgArea = area_km_equator * math.cos(old_div(y_avg, 180) * math.pi)
                                n_pixels = mxnodata.count()
                                avg_precip = mxnodata.mean()
                                # Result is in km * km * mmm i.e. 1E3 m*m*m -> we divide by 1E3 to get 1E6 m*m*m
                                meanResult = float(n_pixels) * pixelAvgArea* avg_precip * 0.001
                            else:
                                # 'count'
                                meanResult = float(mxrange.count())

                        # Both results are equal
                        finalvalue = meanResult

                    else:   # if aggregate['type'] == 'mean' or if aggregate['type'] == 'cumulate':
                        if mxnodata.count() == 0:
                            finalvalue = None
                            meanResult = None
                        else:
                            if aggregate['aggregation_type'] == 'mean':
                                # 'mean'
                                meanResult = mxnodata.mean()
                            else:
                                # 'cumulate'
                                meanResult = mxnodata.sum()

                            finalvalue = (meanResult*scale_factor+scale_offset)

                    # Assign results
                    single_result['filename'] = infile
                    single_result['meanvalue_noscaling'] = meanResult
                    single_result['meanvalue'] = finalvalue

            else:
                logger.debug('ERROR: raster file does not exist - %s' % infile)

            uniqueFilesValues.append(single_result)

        # Define a dictionary to associate filenames/values
        files_to_values_dict = dict((x['filename'], x['meanvalue']) for x in uniqueFilesValues)

        # Prepare array for result
        resultDatesValues = []

        # Returns a list of 'filenames', 'dates', 'values'
        for mydate in dates_list:

            my_result = {'date': datetime.date.today(), 'meanvalue':nodata}

            # Assign the date
            my_result['date'] = mydate
            # Assign the filename
            my_filename = dates_to_files_dict[mydate]

            # Map from array of Values
            my_result['meanvalue'] = files_to_values_dict[my_filename]

            # Map from array of dates
            resultDatesValues.append(my_result)

        try:
            shutil.rmtree(tmpdir)
        except:
            logger.debug('ERROR: Error in deleting tmpdir. Exit')

        # Return result
        return resultDatesValues
    else:
        logger.debug('ERROR: product not registered in the products table! - %s %s %s' % (productcode, subproductcode, version))
        return []


if __name__ == '__main__':
    debug = 1
    # productinfo = {
    #     "productcode": 'tamsat-rfe',
    #     "version": '2.0',
    #     "subproductcode": '1moncum',
    #     "mapsetcode": 'TAMSAT-Africa-4km'
    # }
    productinfo = {
        "productcode": 'vgt-ndvi',
        "version": 'sv2-pv2.2',
        "subproductcode": 'monndvi',
        "mapsetcode": 'SPOTV-Africa-1km'
    }

    startdate = '2017-01-01'
    enddate = '2018-09-19'

    aggregateinfo = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

    vectorlayer = '/eStation2/layers/BEN_adm/BEN_adm1.shp'
    regionidattr = 'HASC_1'

    # vectorlayer = '/eStation2/layers/sst_boxes.geojson'
    # regionidattr = 'NAME'
    # vectorlayer_file = '/eStation2/layers/RIC_CRA_0_g2015_2014.geojson'
    # regionidattr = 'ADM0_NAME'

    regionlevel = 'admin1'

    aggregate = {"aggregation_type": "mean","aggregation_min": "", "aggregation_max": ""}

    if not debug:
        # Parse the input
        parser = argparse.ArgumentParser(description='Generate time series and convert to ECOAGRIS format')
        parser.add_argument('--productinfo', dest='productinfo', type=str, action="store", default="",
                            help='The product info. An object like {"productcode": "vgt-ndvi", "version": "sv2-pv2.2", "subproductcode": "monndvi", "mapsetcode": "SPOTV-Africa-1km"}')
        parser.add_argument('--startdate', dest='startdate', type=str, action="store", default="",
                            help='Start date from where to start to generate the time series values')
        parser.add_argument('--enddate', dest='enddate', type=str, action="store", default="",
                            help='End date from where to stop to generate the time series values')
        parser.add_argument('--aggregateinfo', dest='aggregateinfo', type=str, action="store", default="",
                            help='The aggregate info. An object like {"aggregation_type": "mean","aggregation_min": "", "aggregation_max": ""}')
        parser.add_argument('--vectorlayer', dest='vectorlayer', type=str, action="store", default="",
                            help='The name of the vectorlayer file/dir to process')
        parser.add_argument('--regionidattr', dest='regionidattr', type=str, action="store", default="",
                            help='The attribute name in the vectorlayer that contains the id of the geometry')
        parser.add_argument('--regionlevel', dest='regionlevel', type=str, action="store", default="",
                            help='The region level. For example "admin0", "admin1", "admin2"')
        args = parser.parse_args()
        productinfo = args.productinfo
        startdate = args.startdate
        enddate = args.enddate
        aggregateinfo = args.aggregateinfo
        vectorlayer = args.vectorlayer
        regionidattr = args.regionidattr
        regionlevel = args.regionlevel

        if os.path.isfile(vectorlayer):
            convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel)
        else:
            logger.error('Vector layer file does not exist: %s' % vectorlayer)
        exit()
    else:
        # For debugging
        if os.path.isfile(vectorlayer):
            convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel)
        else:
            logger.error('Vector layer file does not exist: %s' % vectorlayer)

        exit()
