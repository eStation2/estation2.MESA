#!/usr/bin/python

# ***********************************
# Example calls:
#
#  GetCapabilities:
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetCapabilities
#  GetMap:
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_chirps-dekad_2.0_10d
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_chirps-dekad_2.0_10d&DATE=20200111
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=layer_chirps-dekad_2.0_10d&FORMAT=image%2Fjpg&TRANSPARENT=true&date=20200921&time_to_nocache=1622704629174&WIDTH=256&HEIGHT=256&CRS=EPSG%3A4326&STYLES=&BBOX=-45%2C45%2C-22.5%2C67.5
#  DescribeLayer
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=DescribeLayer&LAYERS=layer_chirps-dekad_2.0_10d
#
#  GetLegendGraphic
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetLegendGraphic&LAYERS=layer_chirps-dekad_2.0_10d
#
#  For Africa Platform
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_chirps-dekad_2.0_1mondiff
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_modis-firms_v6.0_10dcount10kdiff
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_modis-firms_v6.0_10dcount
#       http://mesa-proc.jrc.it/webservices?SERVICE=WMS&REQUEST=GetMap&FORMAT=image%2Fjpg&LAYERS=layer_modis-sst_v2013.1_monanom


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
    # Set default values for the mandatory WMS parameters.
    if "SERVICE" not in params or params['SERVICE'].strip() != 'WMS':
        params['SERVICE'] = 'WMS'

    if "VERSION" not in params or params['VERSION'].strip() not in ['1.1.1', '1.3.0']:
        params['VERSION'] = '1.1.1'

    if "REQUEST" not in params or params['REQUEST'].strip() not in ['GetCapabilities', 'GetMap', 'DescribeLayer', 'GetStyles', 'GetFeatureInfo', 'GetLegendGraphic']:
        if "LAYERS" not in params or params['LAYERS'].strip() == '':
            params['REQUEST'] = 'GetCapabilities'
        else:
            params['REQUEST'] = 'GetMap'

    if "LAYERS" not in params or params['LAYERS'].strip() == '':
        params['LAYERS'] = 'layer_chrips-dekad_2.0_10d'   # set default product layer

    if "STYLES" not in params:
        params['STYLES'] = ''

    if "SLD_VERSION" not in params or params['SLD_VERSION'].strip() not in ['1.0.0', '1.1.1', '1.3.0']:
        params['SLD_VERSION'] = '1.0.0'

    projlib = es_constants.proj4_lib_dir
    errorfile = es_constants.log_dir+"/mapserver_wms_layer_errors.log"
    imagepath = es_constants.base_dir+"/webservices/tmp/"
    fontsetfilenamepath = es_constants.apps_dir+'/webservices/fonts.txt'
    thisServerURL = 'http://mesa-proc.jrc.it/webservices'

    productmap = mapscript.mapObj(es_constants.apps_dir+'/webservices/MAP_main.map')
    productmap.setConfigOption("PROJ_LIB", projlib)
    productmap.setConfigOption("MS_ERRORFILE", errorfile)
    productmap.name = 'eStation_WMS_layers'
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
    productmap.setMetaData("WMS_ONLINERESOURCE", thisServerURL)
    productmap.setMetaData("WMS_ABSTRACT", "A Web Coverage Time Service returning eStation products.")
    # productmap.setMetaData("WMS_DESCRIPTION", "A Web Coverage Time Service returning eStation products.")
    productmap.setMetaData("WMS_TITLE", "eStation WMS Server")  # required
    productmap.setMetaData("WMS_NAME", "eStation WMS Server")
    productmap.setMetaData("WMS_KEYWORDLIST", "WMS, eStation2")
    productmap.setMetaData("WMS_KEYWORDS", "WMS, eStation2")
    productmap.setMetaData("WMS_ENABLE_REQUEST", "*")      # necessary!
    # productmap.setMetaData("WMS_TIMEFORMAT", "YYYYMMDD")   # necessary!

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
        scale_factor = product['scale_factor']
        scale_offset = product['scale_offset']
        nodata = product['nodata']
        default_legend_id = product['default_legend_id']

        if params['REQUEST'].strip() in ['GetMap', 'DescribeLayer', 'GetLegendGraphic']:
            if params['LAYERS'] != 'layer_' + productid:
                continue

        p = Product(product_code=productcode, version=version)
        # dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)

        if not mapsetcode or mapsetcode == '':
            all_prod_mapsets = p.mapsets
            dates_available = None
            if all_prod_mapsets.__len__() > 0:
                for mapset in all_prod_mapsets:
                    dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                    dataset.get_filenames()
                    dates_available = dataset.get_dates()
                    if not dates_available:
                        continue  # No files available for product with mapset so skip and go to next mapset
                    else:
                        mapsetcode = mapset
            else:
                continue
        else:
            dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)
            dataset.get_filenames()
            dates_available = dataset.get_dates()
            if not dates_available:
                continue  # No files available for product with mapset so skip and go to next mapset

        if not dates_available:
            continue    # No files available for product so skip and go to next product

        mapsetinfo = querydb.get_mapset_fullinfo(mapsetcode)

        fileextension = '.jpg'
        if "FORMAT" in params and params['FORMAT'].strip() != '':
            if params['FORMAT'] == 'image/png':
                productmap.selectOutputFormat('png')
                fileextension = '.png'
            elif params['FORMAT'] == 'image/jpg' or params['FORMAT'] == 'image/jpeg':
                params['FORMAT'] = 'image/jpeg'
                productmap.selectOutputFormat('jpg')
            elif params['FORMAT'] == 'image/gif':
                productmap.selectOutputFormat('gif')
                fileextension = '.gif'
            else:
                productmap.selectOutputFormat('jpg')
        else:
            params['FORMAT'] = 'image/jpeg'
            productmap.selectOutputFormat('jpg')

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

        if "SRS" not in params or params['SRS'].strip() == '':
            params['SRS'] = mapsetinfo.proj_code

        if "CRS" not in params or params['CRS'].strip() == '':
            params['CRS'] = mapsetinfo.proj_code

        # if "RESX" not in params or params['RESX'].strip() == '':
        #     params['RESX'] = mapsetinfo.pixel_shift_lat
        #
        # if "RESY" not in params or params['RESY'].strip() == '':
        #     params['RESY'] = mapsetinfo.pixel_shift_long

        if "PROJECTION" not in params or params['PROJECTION'].strip() == '':
            params['PROJECTION'] = mapsetinfo.proj_code  # 'init=epsg:4326'

        # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
        epsg = params['SRS'].lower()   # CRS = "EPSG:4326"
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
            filename = params['LAYERS'] + '_' + lastdate
            # params['TIME'] = lastdate
        else:
            filename = params['LAYERS'] + '_' + params['DATE']

        filename = filename.replace('.', '_')

        legend_info = querydb.get_legend_info(legendid=default_legend_id)
        if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
            for row in legend_info:
                totwidth = float((row.totwidth - scale_offset) / scale_factor)
                minstep = float((row.min_value - scale_offset) / scale_factor)  # int(row.min_value*scale_factor+scale_offset)
                maxstep = float((row.max_value - scale_offset) / scale_factor)  # int(row.max_value*scale_factor+scale_offset)
                minstepwidth = float((row.minstepwidth - scale_offset) / scale_factor)
                maxstepwidth = float((row.maxstepwidth - scale_offset) / scale_factor)
                realminstep = float((row.realminstep - scale_offset) / scale_factor)
                realmaxstep = float((row.realmaxstep - scale_offset) / scale_factor)
                totsteps = row.totsteps
                step_type = row.step_type

            processing_scale = 'SCALE=' + str(minstep) + ',' + str(maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

            if step_type == 'logarithmic':
                minbuckets = 32  # 256
                maxbuckets = 256  # 5000
            else:
                minbuckets = 32  # 256
                maxbuckets = 1024  # 5000

            num_buckets = maxbuckets
            if minstepwidth > 0:
                num_buckets = round(totwidth / minstepwidth, 0)

            if num_buckets < minbuckets:
                num_buckets = minbuckets
            elif num_buckets > maxbuckets:
                num_buckets = maxbuckets

            processing_buckets = ''
            if num_buckets > 0:
                processing_buckets = 'SCALE_BUCKETS=' + str(num_buckets)

            processing_novalue = ''
            if nodata is not None and minstep <= nodata < maxstep:
                processing_novalue = 'NODATA=' + str(nodata)

        layer = mapscript.layerObj(productmap)
        layer.setProjection(projection)
        layer.name = 'layer_'+productid
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON
        layer.dump = mapscript.MS_TRUE
        layer.debug = mapscript.MS_TRUE
        layer.data = productfile

        layer.setMetaData('ows_name', 'layer_'+productid)
        # layer.setMetaData('wms_label', descriptive_name)
        layer.setMetaData('ows_title', descriptive_name)
        # layer.setMetaData('ows_abstract', description)
        # layer.setMetaData('ows_description', description)
        layer.setMetaData('wms_enable_request', '*')
        layer.setMetaData('ows_srs', projection)
        layer.setMetaData('ows_extent', str(llx) + " " + str(lly) + " " + str(urx) + " " + str(ury))
        # layer.setMetaData('wms_size', str(w) + " " + str(h))    # required if "data" or "resolution" are not not set!
        # layer.setMetaData('wms_resolution', resolution)     # required if "data" is not set.
        layer.setMetaData('ows_format', params['FORMAT'])
        # layer.setMetaData('wms_nativeformat', 'GTiff')
        # layer.setMetaData('wms_rangeset_name', "layer_"+productid+"_Range")  # required to support DescribeCoverage request
        # layer.setMetaData('wms_rangeset_label', "layer_"+productid+"_Label")     # required to support DescribeCoverage request
        layer.setMetaData('ows_timeextent', timeextent)

        # scale & buckets
        if num_buckets > 0:
            layer.setProcessing(processing_scale)
            layer.setProcessing(processing_buckets)

        if processing_novalue != '':
            layer.setProcessing(processing_novalue)

        resample_processing = "RESAMPLE=AVERAGE"
        layer.setProcessing(resample_processing)

        closeconnection = "CLOSE_CONNECTION=DEFER"
        layer.setProcessing(closeconnection)

        legend_steps = querydb.get_legend_steps(legendid=default_legend_id)
        if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
            stepcount = 0
            for step in legend_steps:
                stepcount += 1
                min_step = float((step.from_step - scale_offset)/scale_factor)
                max_step = float((step.to_step - scale_offset)/scale_factor)
                # min_step = float(step.from_step)
                # max_step = float(step.to_step)
                colors = map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip()))

                if stepcount == legend_steps.__len__():    # For the last step use <= max_step
                    expression_string = '([pixel] >= '+str(min_step)+' and [pixel] <= '+str(max_step)+')'
                else:
                    expression_string = '([pixel] >= '+str(min_step)+' and [pixel] < '+str(max_step)+')'
                # define class object and style
                layerclass = mapscript.classObj(layer)
                layerclass.name = str(step.to_step)
                layerclass.setExpression(expression_string)
                style = mapscript.styleObj(layerclass)
                style.color.setRGB(colors[0], colors[1], colors[2])

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

    if content_type.find('image') != -1:
        content = mapscript.msIO_getStdoutBufferBytes()
    else:
        content = mapscript.msIO_getStdoutBufferString()

    mapscript.msIO_resetHandlers()
    return content_type, content, filename + fileextension
