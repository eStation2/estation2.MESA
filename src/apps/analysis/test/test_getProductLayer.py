
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from builtins import round
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import str
from past.utils import old_div
import unittest
from datetime import date
from apps.productmanagement.datasets import Dataset
from apps.productmanagement.products import Product
from database import querydb
from lib.python import functions
from config import es_constants
from webpy_esapp_helpers import *

class TestGetProductLayer(unittest.TestCase):

    def test_get_productlayer(self):
        #import StringIO
        import mapscript
        # getparams = web.input()

        #getparams = {'STYLES': u'', 'productcode': u'vgt-ndvi', 'legendid': u'7', 'SERVICE': u'WMS', 'subproductcode': u'ndv', 'CRS': u'EPSG:4326', 'FORMAT': u'image/png', 'REQUEST': u'GetMap', 'HEIGHT': u'1010', 'WIDTH': u'998', 'VERSION': u'1.3.0', 'productversion': u'sv2-pv2.1', 'date': u'20130221', 'mapsetcode': u'SPOTV-Africa-1km', 'TRANSPARENT': u'false', 'BBOX': u'-16.17,16.17,-15.47,16.87'}
        # getparams = {'STYLES': u'',
        #              'productcode': u'vgt-fapar',
        #              'legendid': u'99',
        #              'SERVICE': u'WMS',
        #              'subproductcode': u'fapar',
        #              'CRS': u'EPSG:4326',
        #              'FORMAT': u'image/png',
        #              'REQUEST': u'GetMap',
        #              'HEIGHT': u'1010',
        #              'WIDTH': u'998',
        #              'VERSION': u'1.3.0',
        #              'productversion': u'V1.4',
        #              'date': u'20130221',
        #              'mapsetcode': u'SPOTV-Africa-1km',
        #              'TRANSPARENT': u'false',
        #              'BBOX': u'15.46875, -17.578125, 16.171875, -16.875'}
        getparams = {'STYLES': u'',
                     'productcode': u'modis-firms',
                     'legendid': u'235',
                     'SERVICE': u'WMS',
                     'subproductcode': u'1day',
                     'CRS': u'EPSG:4326',
                     'FORMAT': u'image/png',
                     'REQUEST': u'GetMap',
                     'HEIGHT': u'1010',
                     'WIDTH': u'998',
                     'VERSION': u'1.3.0',
                     'productversion': u'v6.0',
                     'date': u'20190918',
                     'mapsetcode': u'SPOTV-Africa-1km',
                     'TRANSPARENT': u'false',
                     'BBOX': u'15.46875, -17.578125, 16.171875, -16.875'}

        #getparams = {'STYLES': u'', 'productcode': u'vgt-ndvi', 'legendid': u'7', 'SERVICE': u'WMS', 'subproductcode': u'ndv', 'CRS': u'EPSG:4326', 'FORMAT': u'image/png', 'REQUEST': u'GetMap', 'HEIGHT': u'1091', 'WIDTH': u'998', 'VERSION': u'1.3.0', 'productversion': u'sv2-pv2.1', 'date': u'20130221', 'mapsetcode': u'SPOTV-Africa-1km', 'TRANSPARENT': u'false', 'BBOX': u'-25.70957541665903,9.276714800828785,-13.723491432284028,20.021343707078785'}
        # getparams = [
        #     SERVICE:'WMS',
        #     VERSION='1.3.0',
        #     REQUEST='GetMap',
        #     FORMAT='image/png',
        #     TRANSPARENT='false',
        #     productcode='vgt-ndvi',
        #     productversion='sv2-pv2.1',
        #     subproductcode='ndv',
        #     mapsetcode='SPOTV-Africa-1km',
        #     legendid='7',
        #     date='20130221',
        #     CRS='EPSG:4326'',
        #     STYLES=''
        #     WIDTH='998',
        #     HEIGHT='1010',
        #     BBOX='-26,-35,60,38'
        # ]
        p = Product(product_code=getparams['productcode'], version=getparams['productversion'])
        dataset = p.get_dataset(mapset=getparams['mapsetcode'], sub_product_code=getparams['subproductcode'])
        # print dataset.fullpath

        if hasattr(getparams, "date"):
            filedate = getparams['date']
        else:
            dataset.get_filenames()
            lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
            filedate = lastdate

        if dataset.no_year():
            filedate=dataset.strip_year(filedate)
        # lastdate = lastdate.replace("-", "")
        # mydate=lastdate.strftime("%Y%m%d")

        filename = functions.set_path_filename(filedate,
                                               getparams['productcode'],
                                               getparams['subproductcode'],
                                               getparams['mapsetcode'],
                                               getparams['productversion'],
                                               '.tif')
        productfile = dataset.fullpath + filename
        # print productfile

        #web.header('Content-type', 'image/png')
        #web.header('Content-transfer-encoding', 'binary')
        #buf = StringIO.StringIO()
        #mapscript.msIO_installStdoutToBuffer()
        #map = mapserver.getmap()
        ##map.save to a file fname.png
        ##web.header('Content-Disposition', 'attachment; filename="fname.png"')
        #contents = buf.getvalue()
        #return contents

        #logger.debug("MapServer: Installing stdout to buffer.")
        mapscript.msIO_installStdoutToBuffer()

        # projlib = "/usr/share/proj/"
        projlib = es_constants.proj4_lib_dir
        # errorfile = es_constants.apps_dir+"/analysis/ms_tmp/ms_errors.log"
        errorfile = es_constants.log_dir+"/mapserver_error.log"
        # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

        owsrequest = mapscript.OWSRequest()

        inputparams = getparams # web.input()
        for k, v in inputparams.items():
            print (k + ':' + v)
            owsrequest.setParameter(k.upper(), v)

        # print owsrequest

        filenamenoextention = functions.set_path_filename(filedate,
                                               getparams['productcode'],
                                               getparams['subproductcode'],
                                               getparams['mapsetcode'],
                                               getparams['productversion'],
                                               '')
        owsrequest.setParameter("LAYERS", filenamenoextention)

        productmap = mapscript.mapObj(es_constants.template_mapfile)
        productmap.setConfigOption("PROJ_LIB", projlib)
        productmap.setConfigOption("MS_ERRORFILE", errorfile)
        productmap.maxsize = 4096

        outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
        outputformat_png.setOption("INTERLACE", "OFF")
        productmap.appendOutputFormat(outputformat_png)
        #outputformat_gd = mapscript.outputFormatObj('GD/GIF', 'gif')
        #productmap.appendOutputFormat(outputformat_gd)
        productmap.selectOutputFormat('png')
        productmap.debug = mapscript.MS_TRUE
        productmap.status = mapscript.MS_ON
        productmap.units = mapscript.MS_DD

        coords = list(map(float, inputparams['BBOX'].split(",")))
        print (coords)
        llx = coords[0]
        lly = coords[1]
        urx = coords[2]
        ury = coords[3]
        print((llx, lly, urx, ury))

        productmap.setExtent(llx, lly, urx, ury)   # -26, -35, 60, 38
        # productmap.setExtent(-26, -35, 60, 38)

        # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
        # epsg = "+init=epsg:3857"
        # epsg = "+init=" + inputparams.CRS.lower()   # CRS = "EPSG:4326"
        epsg = inputparams['CRS'].lower()   # CRS = "EPSG:4326"
        productmap.setProjection(epsg)

        w = int(inputparams['WIDTH'])
        h = int(inputparams['HEIGHT'])
        productmap.setSize(w, h)

        # General web service information
        productmap.setMetaData("WMS_TITLE", "Product description")
        productmap.setMetaData("WMS_SRS", inputparams['CRS'].lower())
        # productmap.setMetaData("WMS_SRS", "epsg:3857")
        productmap.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 raster layers.")
        productmap.setMetaData("WMS_ENABLE_REQUEST", "*")   # necessary!!

        product_info = querydb.get_product_out_info(productcode=inputparams['productcode'],
                                                    subproductcode=inputparams['subproductcode'],
                                                    version=inputparams['productversion'])
        if hasattr(product_info, "__len__") and product_info.__len__() > 0:
            for row in product_info:
                scale_factor = row.scale_factor
                scale_offset = row.scale_offset
                nodata = row.nodata

        legend_info = querydb.get_legend_info(legendid=inputparams['legendid'])
        if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
            for row in legend_info:
                minstep = int(old_div((row.min_value - scale_offset),scale_factor))    #int(row.min_value*scale_factor+scale_offset)
                maxstep = int(old_div((row.max_value - scale_offset),scale_factor))    # int(row.max_value*scale_factor+scale_offset)
                realminstep = int(old_div((row.realminstep - scale_offset),scale_factor))
                realmaxstep = int(old_div((row.realmaxstep - scale_offset),scale_factor))
                minstepwidth = int(old_div((row.minstepwidth - scale_offset),scale_factor))
                maxstepwidth = int(old_div((row.maxstepwidth - scale_offset),scale_factor))
                totwidth = int(old_div((row.totwidth - scale_offset),scale_factor))
                totsteps = row.totsteps

            # maxstep = 255
            processing_scale = 'SCALE='+str(minstep)+','+str(maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

            minbuckets = 256
            maxbuckets = 10000
            num_buckets = maxbuckets
            if minstepwidth > 0:
                num_buckets = round(old_div(totwidth, minstepwidth), 0)

            if num_buckets < minbuckets:
                num_buckets = minbuckets
            elif num_buckets > maxbuckets:
                num_buckets = 0

            # num_buckets = 10000
            if num_buckets > 0:
                processing_buckets = 'SCALE_BUCKETS='+str(num_buckets)

            # nodata = -32768     # get this value from the table products.product
            processing_novalue = ''
            if nodata is not None and minstep <= nodata < maxstep:
                processing_novalue = 'NODATA='+str(nodata)

            layer = mapscript.layerObj(productmap)
            layer.name = filenamenoextention
            layer.type = mapscript.MS_LAYER_RASTER
            layer.status = mapscript.MS_ON     # MS_DEFAULT
            layer.data = productfile
            # layer.setProjection("+init=epsg:4326")
            layer.setProjection("epsg:4326")
            layer.dump = mapscript.MS_TRUE

            # scale & buckets
            if num_buckets > 0:
                layer.setProcessing(processing_scale)
                layer.setProcessing(processing_buckets)

            if processing_novalue != '':
                layer.setProcessing(processing_novalue)

            legend_steps = querydb.get_legend_steps(legendid=inputparams['legendid'])
            if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
                stepcount = 0
                for step in legend_steps:
                    stepcount += 1
                    min_step = int(old_div((step.from_step - scale_offset),scale_factor))
                    max_step = int(old_div((step.to_step - scale_offset),scale_factor))
                    colors = list(map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip())))

                    if stepcount == legend_steps.__len__():    # For the last step use <= max_step
                        expression_string = '([pixel] >= '+str(min_step)+' and [pixel] <= '+str(max_step)+')'
                    else:
                        expression_string = '([pixel] >= '+str(min_step)+' and [pixel] < '+str(max_step)+')'
                    # define class object and style
                    layerclass = mapscript.classObj(layer)
                    layerclass.name = layer.name+'_'+str(stepcount)
                    layerclass.setExpression(expression_string)
                    style = mapscript.styleObj(layerclass)
                    style.color.setRGB(colors[0], colors[1], colors[2])

        result_map_file = es_constants.apps_dir+'/analysis/MAP_result.map'
        # if os.path.isfile(result_map_file):
        #     os.remove(result_map_file)
        productmap.save(result_map_file)
        image = productmap.draw()
        image.save(es_constants.apps_dir+'/analysis/'+filenamenoextention+'.png')

        contents = productmap.OWSDispatch(owsrequest)
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        #web.header = "Content-Type","%s; charset=utf-8"%content_type
        # web.header('Content-type', 'image/png')
        #web.header('Content-transfer-encoding', 'binary')
        # return content

        self.assertEquals(True, True)

    def test_call_webpy_helpers(self):

        getparams = {'STYLES': u'',
                     'productcode': u'modis-firms',
                     'legendid': u'235',
                     'SERVICE': u'WMS',
                     'subproductcode': u'1day',
                     'CRS': u'EPSG:4326',
                     'FORMAT': u'image/png',
                     'REQUEST': u'GetMap',
                     'HEIGHT': u'1010',
                     'WIDTH': u'998',
                     'VERSION': u'1.3.0',
                     'productversion': u'v6.0',
                     'date': u'20190918',
                     'mapsetcode': u'SPOTV-Africa-1km',
                     'TRANSPARENT': u'false',
                     'BBOX': u'-16.0, 12.0, -9.0, 20.0'}       # Angola
                     # 'BBOX': u'-25.70957541665903,9.276714800828785,-13.723491432284028,20.021343707078785'}
        # getparams = {'STYLES': u'',
        #              'productcode': u'vgt-fapar',
        #              'legendid': u'99',
        #              'SERVICE': u'WMS',
        #              'subproductcode': u'fapar',
        #              'CRS': u'EPSG:4326',
        #              'FORMAT': u'image/png',
        #              'REQUEST': u'GetMap',
        #              'HEIGHT': u'1010',
        #              'WIDTH': u'998',
        #              'VERSION': u'1.3.0',
        #              'productversion': u'V1.4',
        #              'date': u'20130221',
        #              'mapsetcode': u'SPOTV-Africa-1km',
        #              'TRANSPARENT': u'false',
        #              'BBOX': u'15.46875, -17.578125, 16.171875, -16.875'}
        # getparams = {'STYLES': u'', 'productcode': u'vgt-ndvi', 'legendid': u'7', 'SERVICE': u'WMS', 'subproductcode': u'ndv', 'CRS': u'EPSG:4326', 'FORMAT': u'image/png', 'REQUEST': u'GetMap', 'HEIGHT': u'1091', 'WIDTH': u'998', 'VERSION': u'1.3.0', 'productversion': u'sv2-pv2.1', 'date': u'20130221', 'mapsetcode': u'SPOTV-Africa-1km', 'TRANSPARENT': u'false', 'BBOX': u'-25.70957541665903,9.276714800828785,-13.723491432284028,20.021343707078785'}

        getProductLayer(getparams)