#!/usr/bin/python

# ***********************************
# Example calls:
#
# GetCapabilities:
#       http://localhost:8888/webservices?SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCapabilities
#  GetCoverage:
#       http://localhost:8888/webservices?SERVICE=WCS&version=1.0.0&REQUEST=GetCoverage&FORMAT=GTiff&COVERAGE=layer_chirps-dekad_2.0_10d
#       http://localhost:8888/webservices?SERVICE=WCS&version=1.0.0&REQUEST=GetCoverage&FORMAT=GTiff&COVERAGE=layer_chirps-dekad_2.0_10d&DATE=20200111
#       http://localhost:8888/webservices?SERVICE=WCS&version=1.0.0&REQUEST=GetCoverage&FORMAT=GTiff&COVERAGE=layer_chirps-dekad_2.0_10d&DATE=20200111&BBOX=-26,-35,60,38&CRS=EPSG:4326&WIDTH=720&HEIGHT=720
#  DescribeCoverage
#       http://localhost:8888/webservices?SERVICE=WCS&VERSION=1.0.0&REQUEST=DescribeCoverage&COVERAGE=layer_chirps-dekad_2.0_10d

import mapscript
import locale
import glob

from config import es_constants
from database import querydb
# from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product
from lib.python import functions
from lib.python import es_logging as log

logger = log.my_logger(__name__)
locale.setlocale(locale.LC_NUMERIC, 'C')


def getRequest(params):
    # Set default values for the mandatory WCS parameters.
    if "SERVICE" not in params or params['SERVICE'].strip() != 'WCS':
        params['SERVICE'] = 'WCS'

    if "VERSION" not in params or params['VERSION'].strip() not in ['1.0.0', '1.1.0', '2.0.0']:
        params['VERSION'] = '1.0.0'

    if "REQUEST" not in params or params['REQUEST'].strip() not in ['GetCapabilities', 'GetCoverage', 'DescribeCoverage']:
        if "COVERAGE" not in params or params['COVERAGE'].strip() == '':
            params['REQUEST'] = 'GetCapabilities'
        else:
            params['REQUEST'] = 'GetCoverage'

    if "COVERAGE" not in params or params['COVERAGE'].strip() == '':
        params['COVERAGE'] = 'layer_chrips-dekad_2.0_10d'   # set default product layer

    projlib = es_constants.proj4_lib_dir
    errorfile = es_constants.log_dir+"/mapserver_wcs_layer_errors.log"
    imagepath = es_constants.base_dir+"/webservices/tmp/"
    fontsetfilenamepath = es_constants.apps_dir+'/webservices/fonts.txt'
    thisServerURL = 'http://localhost:8888/webservices'

    productmap = mapscript.mapObj(es_constants.apps_dir+'/webservices/MAP_main.map')
    productmap.setConfigOption("PROJ_LIB", projlib)
    productmap.setConfigOption("MS_ERRORFILE", errorfile)
    productmap.name = 'eStation_WCS_layers'
    productmap.maxsize = 100000
    productmap.debug = mapscript.MS_OFF
    productmap.status = mapscript.MS_ON
    # productmap.units = mapscript.MS_DD
    # productmap.setFontSet(fontsetfilenamepath)

    outputformat_jpg = mapscript.outputFormatObj('AGG/JPEG', 'jpg')
    outputformat_jpg.setOption("INTERLACE", "OFF")
    productmap.appendOutputFormat(outputformat_jpg)

    outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
    outputformat_png.setOption("INTERLACE", "OFF")
    productmap.appendOutputFormat(outputformat_png)

    outputformat = mapscript.outputFormatObj('GD/GIF', 'gif')
    productmap.appendOutputFormat(outputformat)

    outputformat = mapscript.outputFormatObj('GDAL/GTiff', 'tif')
    productmap.appendOutputFormat(outputformat)

    productmap.web.imagepath = imagepath
    productmap.web.imageurl = imagepath     # change this to URL

    # General web service information
    productmap.setMetaData("WCS_ONLINERESOURCE", thisServerURL)
    productmap.setMetaData("WCS_ABSTRACT", "A Web Coverage Time Service returning eStation products.")
    productmap.setMetaData("WCS_DESCRIPTION", "A Web Coverage Time Service returning eStation products.")
    productmap.setMetaData("WCS_LABEL", "eStation WCS Server")  # required
    productmap.setMetaData("WCS_NAME", "eStation WCS Server")
    productmap.setMetaData("WCS_KEYWORDLIST", "WCS,eStation2")
    productmap.setMetaData("WCS_KEYWORDS", "WCS,eStation2")
    productmap.setMetaData("WCS_ENABLE_REQUEST", "*")      # necessary!
    # productmap.setMetaData("WCS_TIMEFORMAT", "YYYYMMDD")   # necessary!

    products = querydb.get_products_webservices()

    for product in products:
        productcode = product['productcode']
        subproductcode = product['subproductcode']
        version = product['version']
        mapsetcode = product['mapsetcode']
        productid = product['productcode'] + '_' + product['version'] + '_' + product['subproductcode']
        frequency_id = product['frequency_id']
        date_format = product['date_format']
        descriptive_name = product['descriptive_name']
        description = product['description']
        provider = product['provider']
        data_type_id = product['data_type_id']

        if params['REQUEST'].strip() in ['GetCoverage', 'DescribeCoverage']:
            if params['COVERAGE'] != 'layer_' + productid:
                continue

        mapsetinfo = querydb.get_mapset_fullinfo(mapsetcode)
        p = Product(product_code=productcode, version=version)
        dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)

        if data_type_id.upper() == 'BYTE':
            productmap.selectOutputFormat('GEOTIFF_BYTE')
        elif data_type_id.upper() == 'INT16':
            productmap.selectOutputFormat('GEOTIFF_INT16')
        elif data_type_id.upper() == 'FLOAT32':
            productmap.selectOutputFormat('GEOTIFF_FLOAT')
        else:
            productmap.selectOutputFormat('tif')

        dataset.get_filenames()
        dates_available = dataset.get_dates()
        if not dates_available:
            continue    # No files available for product so skip and go to next product

        if 'DATE' in params:
            filedate = params['DATE']
            file_exists = False
            for date in dates_available:
                if date.strftime("%Y%m%d") == filedate:
                    file_exists = True

            if not file_exists:
                lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
                filedate = lastdate
        else:
            lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
            filedate = lastdate

        if dataset.no_year():
            filedate = dataset.strip_year(filedate)

        # Check the case of daily product, with time/minutes
        if frequency_id == 'e1day' and date_format == 'YYYYMMDD':
            regex = dataset.fullpath + filedate+'*'+'.tif'
            filename = glob.glob(regex)
            if len(filename) > 0:
                productfile = filename[0]
            else:
                filename = functions.set_path_filename(filedate,
                                                       productcode,
                                                       subproductcode,
                                                       mapsetcode,
                                                       version,
                                                       '.tif')
                productfile = dataset.fullpath + filename
        else:
            filename = functions.set_path_filename(filedate,
                                                   productcode,
                                                   subproductcode,
                                                   mapsetcode,
                                                   version,
                                                   '.tif')
            productfile = dataset.fullpath + filename

        if "BBOX" not in params or params['BBOX'].strip() == '':
            params['BBOX'] = str(mapsetinfo.upper_left_long) + ", " + str(mapsetinfo.lower_right_lat) + ", " + str(mapsetinfo.lower_right_long) + ", " + str(mapsetinfo.upper_left_lat)
        else:
            # Check if BBOX is within mapset BBOX
            coords = map(float, params['BBOX'].split(","))

        coords = map(float, params['BBOX'].split(","))
        lly = coords[0]
        llx = coords[1]
        ury = coords[2]
        urx = coords[3]
        productmap.setExtent(llx, lly, urx, ury)
        # Check that it is in the form: minx, miny, maxx, maxy

        if "WIDTH" not in params or params['WIDTH'].strip() == '':
            params['WIDTH'] = str(mapsetinfo.pixel_size_x)

        if "HEIGHT" not in params or params['HEIGHT'].strip() == '':
            params['HEIGHT'] = str(mapsetinfo.pixel_size_y)

        if "CRS" not in params or params['CRS'].strip() == '':
            params['CRS'] = mapsetinfo.proj_code

        if "RESX" not in params or params['RESX'].strip() == '':
            params['RESX'] = mapsetinfo.pixel_shift_lat

        if "RESY" not in params or params['RESY'].strip() == '':
            params['RESY'] = mapsetinfo.pixel_shift_long

        if "PROJECTION" not in params or params['PROJECTION'].strip() == '':
            params['PROJECTION'] = mapsetinfo.proj_code  # 'init=epsg:4326'

        # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
        epsg = params['CRS'].lower()   # CRS = "EPSG:4326"
        # productmap.setProjection(epsg)

        projection = params['PROJECTION'].lower()
        productmap.setProjection(projection)

        w = int(params['WIDTH'])
        h = int(params['HEIGHT'])
        productmap.setSize(w, h)

        resolution = mapsetinfo.pixel_shift_lat + ' ' + mapsetinfo.pixel_shift_long

        firstdate = dataset.get_dates()[0].strftime("%Y%m%d")
        lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
        timeextent = firstdate+'/'+lastdate+'/PT5M'

        if "DATE" not in params or params['DATE'].strip() == '':
            filename = params['COVERAGE'] + '_' + lastdate
            # params['TIME'] = lastdate
        else:
            filename = params['COVERAGE'] + '_' + params['DATE']

        filename = filename.replace('.', '_')

        layer = mapscript.layerObj(productmap)
        layer.setProjection(projection)
        layer.name = 'layer_'+productid
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON
        layer.dump = mapscript.MS_TRUE
        layer.debug = mapscript.MS_TRUE
        layer.data = productfile

        layer.setMetaData('wcs_name', 'layer_'+productid)
        layer.setMetaData('wcs_label', descriptive_name)
        # layer.setMetaData('ows_title', descriptive_name)
        layer.setMetaData('wcs_abstract', description)
        layer.setMetaData('wcs_description', description)
        layer.setMetaData('wcs_enable_request', '*')
        layer.setMetaData('wcs_srs', projection)
        layer.setMetaData('wcs_extent', str(llx) + " " + str(lly) + " " + str(urx) + " " + str(ury))
        # layer.setMetaData('wcs_size', str(w) + " " + str(h))    # required if "data" or "resolution" are not not set!
        layer.setMetaData('wcs_resolution', resolution)     # required if "data" is not set.
        layer.setMetaData('wcs_formats', "GEOTIFFBYTE GEOTIFF_FLOAT GEOTIFF_INT16")
        layer.setMetaData('wcs_nativeformat', 'GTiff')
        layer.setMetaData('wcs_rangeset_name', "layer_"+productid+"_Range")  # required to support DescribeCoverage request
        layer.setMetaData('wcs_rangeset_label', "layer_"+productid+"_Label")     # required to support DescribeCoverage request
        layer.setMetaData('wcs_timeextent', timeextent)

    mapscript.msIO_installStdoutToBuffer()

    ows_request = mapscript.OWSRequest()
    # Convert application request parameters
    for param, value in params.iteritems():
        ows_request.addParameter(param, str(value))  # setParam()

    # productmap.loadOWSParameters(ows_request)
    productmap.OWSDispatch(ows_request)
    content_type = mapscript.msIO_stripStdoutBufferContentType()
    content_type = content_type.split(';')[0]

    ms_mapfilename = es_constants.base_tmp_dir+'/'+filename+str(llx)+'_'+str(lly)+'_'+str(urx)+'_'+str(ury)+'.map'
    productmap.save(ms_mapfilename)

    if content_type == 'image/tiff':
        content = mapscript.msIO_getStdoutBufferBytes()
    else:
        content = mapscript.msIO_getStdoutBufferString()

    mapscript.msIO_resetHandlers()

    return content_type, content, filename + '.tif'



    # if hasattr(product_info, "__len__") and product_info.__len__() > 0:
    #     for row in product_info:
    #         descriptive_name = row.descriptive_name
    #         description = row.description
    #         provider = row.provider
    #         productid = row.productcode + '_' + row.version + '_' + row.subproductcode
    # else:
    #     errormsg = 'No product info found!'
    #     logger.error("WCS Web Service: Error!\n -> {}".format(errormsg))
    #     return '', errormsg

    # web.header('Content-type', 'image/png')
    # f = open(filename_png, 'rb')
    # while 1:
    #     buf = f.read(1024 * 8)
    #     if not buf:
    #         break
    #     yield buf
    # f.close()
    # os.remove(filename_png)

    # #print owsrequest.getValueByName('BBOX')
    # mapscript.msIO_installStdoutToBuffer()
    # contents = productmap.OWSDispatch(owsrequest)
    # content_type = mapscript.msIO_stripStdoutBufferContentType()
    # content = mapscript.msIO_getStdoutBufferBytes()
    # #web.header = "Content-Type","%s; charset=utf-8"%content_type
    # web.header('Content-type', 'image/png')
    # #web.header('Content-transfer-encoding', 'binary')
    # return content