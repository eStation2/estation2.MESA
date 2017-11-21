#!/usr/bin/python

#if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import sys
import os

os.umask(0000)

cur_dir = os.path.dirname(__file__)
if cur_dir not in sys.path:
    sys.path.append(cur_dir)

import web
import datetime
import json
import glob
import time
import calendar
import numpy as NP

from config import es_constants
from database import querydb
from database import crud

from apps.acquisition import get_eumetcast
from apps.acquisition import acquisition
from apps.processing import processing      # Comment in WINDOWS version!
from apps.productmanagement.datasets import Dataset
from apps.es2system import es2system
# from apps.productmanagement.datasets import Frequency
from apps.productmanagement.products import Product
from apps.analysis import generateLegendHTML
from apps.analysis.getTimeseries import (getTimeseries, getFilesList)
from multiprocessing import (Process, Queue)

from lib.python import functions
from lib.python import es_logging as log

logger = log.my_logger(__name__)


WEBPY_COOKIE_NAME = "webpy_session_id"


def getProductLayer(getparams):
    #import StringIO
    import mapscript
    # To solve issue with Chla Legends (Tuleap ticket #10905 - see http://trac.osgeo.org/mapserver/ticket/1762)
    import locale
    locale.setlocale(locale.LC_NUMERIC,'C')

    # getparams = web.input()
    # print getparams

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

    # Check the case of daily product, with time/minutes
    frequency_id = dataset._db_product.frequency_id
    date_format = dataset._db_product.date_format


    if frequency_id=='e1day' and date_format=='YYYYMMDD':
        regex = dataset.fullpath + filedate+'*'+'.tif'
        filename = glob.glob(regex)
        # print filename
        productfile = filename[0]
    # lastdate = lastdate.replace("-", "")
    # mydate=lastdate.strftime("%Y%m%d")
    else:
        filename = functions.set_path_filename(filedate,
                                               getparams['productcode'],
                                               getparams['subproductcode'],
                                               getparams['mapsetcode'],
                                               getparams['productversion'],
                                               '.tif')
        productfile = dataset.fullpath + filename
    # print productfile

    if (hasattr(getparams, "outmask") and getparams['outmask'] == 'true'):
        # print productfile
        # print es_constants.base_tmp_dir
        from greenwich import Raster, Geometry

        # try:
        #     from osgeo import gdal
        #     from osgeo import gdal_array
        #     from osgeo import ogr, osr
        #     from osgeo import gdalconst
        # except ImportError:
        #     import gdal
        #     import gdal_array
        #     import ogr
        #     import osr
        #     import gdalconst

        # try:

        # ogr.UseExceptions()
        wkt = getparams['selectedfeature']
        theGeomWkt = ' '.join(wkt.strip().split())
        # print wkt
        geom = Geometry(wkt=str(theGeomWkt), srs=4326)
        # print "wearehere"
        with Raster(productfile) as img:
            # Assign nodata from prod_info
            # img._nodata = nodata
            # print "nowwearehere"
            with img.clip(geom) as clipped:
                # Save clipped image (for debug only)
                productfile = es_constants.base_tmp_dir + '/clipped_'+filename
                # print productfile
                clipped.save(productfile)

        # except:
        #     print 'errorrrrrrrrr!!!!!!'

    #web.header('Content-type', 'image/png')
    #web.header('Content-transfer-encoding', 'binary')
    #buf = StringIO.StringIO()
    #mapscript.msIO_installStdoutToBuffer()
    #map = mapserver.getmap()
    ##map.save to a file fname.png
    ##web.header('Content-Disposition', 'attachment; filename="fname.png"')
    #contents = buf.getvalue()
    #return contents

    # #logger.debug("MapServer: Installing stdout to buffer.")
    # mapscript.msIO_installStdoutToBuffer()
    #
    # owsrequest = mapscript.OWSRequest()
    #
    # inputparams = web.input()
    # for k, v in inputparams.iteritems():
    #     print k + ':' + v
    #     if k not in ('productcode', 'subproductcode', 'mapsetcode', 'productversion', 'legendid', 'date' 'TRANSPARENT'):
    #         # if k == 'CRS':
    #         #     owsrequest.setParameter('SRS', v)
    #         owsrequest.setParameter(k.upper(), v)
    #
    # #owsrequest.setParameter(k.upper(), v)


    # projlib = "/usr/share/proj/"
    projlib = es_constants.proj4_lib_dir
    # errorfile = es_constants.apps_dir+"/analysis/ms_tmp/ms_errors.log"
    errorfile = es_constants.log_dir+"/mapserver_error.log"
    # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

    # TEST ????
    inputparams = getparams

    filenamenoextention = functions.set_path_filename(filedate,
                                           getparams['productcode'],
                                           getparams['subproductcode'],
                                           getparams['mapsetcode'],
                                           getparams['productversion'],
                                           '')
    # owsrequest.setParameter("LAYERS", filenamenoextention)
    # owsrequest.setParameter("UNIT", mapscript.MS_METERS)

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
    #productmap.debug = mapscript.MS_TRUE
    productmap.debug = 5
    productmap.status = mapscript.MS_ON
    productmap.units = mapscript.MS_DD

    coords = map(float, inputparams['BBOX'].split(","))
    lly = coords[0]
    llx = coords[1]
    ury = coords[2]
    urx = coords[3]
    productmap.setExtent(llx, lly, urx, ury)   # -26, -35, 60, 38
    # productmap.setExtent(lly, llx, ury, urx)   # -26, -35, 60, 38
    # print llx, lly, urx, ury

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
            minstep = float((row.min_value - scale_offset)/scale_factor)    #int(row.min_value*scale_factor+scale_offset)
            maxstep = float((row.max_value - scale_offset)/scale_factor)    # int(row.max_value*scale_factor+scale_offset)
            realminstep = float((row.realminstep - scale_offset)/scale_factor)
            realmaxstep = float((row.realmaxstep - scale_offset)/scale_factor)
            minstepwidth = float((row.minstepwidth - scale_offset)/scale_factor)
            maxstepwidth = float((row.maxstepwidth - scale_offset)/scale_factor)
            totwidth = float((row.totwidth - scale_offset)/scale_factor)
            totsteps = row.totsteps

        # maxstep = 255
        processing_scale = 'SCALE='+str(minstep)+','+str(maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

        minbuckets = 256
        maxbuckets = 5000
        num_buckets = maxbuckets
        if minstepwidth > 0:
            num_buckets = round(totwidth / minstepwidth, 0)

        if num_buckets < minbuckets:
            num_buckets = minbuckets
        elif num_buckets > maxbuckets:
            num_buckets = maxbuckets

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
        layer.units = mapscript.MS_METERS
        # layer.setProjection("+init=epsg:4326")
        layer.setProjection("epsg:4326")
        layer.dump = mapscript.MS_TRUE

        # scale & buckets
        if num_buckets > 0:
            layer.setProcessing(processing_scale)
            layer.setProcessing(processing_buckets)

        if processing_novalue != '':
            layer.setProcessing(processing_novalue)

        resample_processing = "RESAMPLE=AVERAGE"
        layer.setProcessing(resample_processing)

        legend_steps = querydb.get_legend_steps(legendid=inputparams['legendid'])
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
                layerclass.name = layer.name+'_'+str(stepcount)
                layerclass.setExpression(expression_string)
                style = mapscript.styleObj(layerclass)
                style.color.setRGB(colors[0], colors[1], colors[2])

    # result_map_file = '/tmp/eStation2/MAP_result.map'
    # if os.path.isfile(result_map_file):
    #     os.remove(result_map_file)
    # productmap.save(result_map_file)

    image = productmap.draw()
    filename_png = es_constants.base_tmp_dir+filenamenoextention+str(llx)+'_'+str(lly)+'_'+str(urx)+'_'+str(ury)+'.png'
    image.save(filename_png)

    return filename_png

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


def GetAssignedDatasets(legendid):
    assigned_datasets_dict_all = []
    legend_assigned_datasets = querydb.get_legend_assigned_datasets(legendid=legendid)

    if hasattr(legend_assigned_datasets, "__len__") and legend_assigned_datasets.__len__() > 0:
        for assigned_dataset in legend_assigned_datasets:
            # row_dict = functions.row2dict(assigned_dataset)
            row_dict = assigned_dataset

            assigned_dataset_dict = {'legend_id': row_dict['legend_id'],
                                     'productcode': row_dict['productcode'],
                                     'subproductcode': row_dict['subproductcode'],
                                     'version': row_dict['version'],
                                     'default_legend': row_dict['default_legend'],
                                     'descriptive_name': row_dict['descriptive_name'],
                                     'description': row_dict['description']
                                    }

            assigned_datasets_dict_all.append(assigned_dataset_dict)

        assigned_datasets_json = json.dumps(assigned_datasets_dict_all,
                                            ensure_ascii=False,
                                            encoding='utf-8',
                                            sort_keys=True,
                                            indent=4,
                                            separators=(', ', ': '))

        assigned_datasets_json = '{"success":true, "total":' + str(legend_assigned_datasets.__len__()) + ',"assigneddatasets":' + assigned_datasets_json + '}'

    else:
        assigned_datasets_json = '{"success":true, "message":"No products assigned!"}'

    return assigned_datasets_json


def UnassignLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legendid' in params:

        productlegend = {
            'productcode': params['productcode'],
            'subproductcode': params['subproductcode'],
            'version': params['productversion'],
            'legend_id': params['legendid']
        }

        if crud_db.delete('product_legend', **productlegend):
            message = '{"success":true, "message":"Legend unassigned from product!"}'
        else:
            message = '{"success":false, "message":"Error unassigning legend!"}'

    else:
        message = '{"success":false, "message":"No legendid given!"}'

    return message


def AssignLegends(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legendids' in params:
        legendIDS = json.loads(params['legendids'])
        # legendIDS = params['legendids']

        message = '{"success":false, "message":"Error assigning legends!"}'
        if len(legendIDS) > 0:
            for legendid in legendIDS:
                productlegend = {
                    'productcode': params['productcode'],
                    'subproductcode': params['subproductcode'],
                    'version': params['productversion'],
                    'legend_id': legendid,
                    'default_legend': False
                }

                if crud_db.create('product_legend', productlegend):
                    message = '{"success":true, "message":"Legends assigned!"}'
                else:
                    message = '{"success":false, "message":"Error assigning legends!"}'
                    break
        else:
            message = '{"success":false, "message":"No legend ids given!"}'
    else:
        message = '{"success":false, "message":"No legend ids given!"}'

    return message


def copyLegend(params):

    if 'legendid' in params:
        newlegendname = params['legend_descriptive_name'] + ' - copy'
        newlegendid = querydb.copylegend(legendid=params['legendid'], legend_descriptive_name=newlegendname)

        if newlegendid != -1:
            message = '{"success":true, "legendid": ' + str(newlegendid) + ', "legend_descriptive_name": "' + newlegendname + '","message":"Legend copied!"}'
        else:
            message = '{"success":false, "message":"Error copying the legend!"}'
    else:
        message = '{"success":false, "message":"No legend id given!"}'

    return message


def DeleteLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legend' in params:
        legend = {
            'legend_id': params['legend']['legendid']
        }

        if crud_db.delete('legend', **legend):
            message = '{"success":true, "legendid": ' + str(params['legend']['legendid']) + ',"message":"Legend deleted!"}'
        else:
            message = '{"success":false, "message":"Error deleting the legend!"}'
    else:
        message = '{"success":false, "message":"No legend id given!"}'

    return message


def SaveLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    # if hasattr(params, 'legendid'):
    if 'legendid' in params:
        legend = {
            'legend_id': params['legendid'],
            'colorbar': params['legend_descriptive_name'],
            'legend_name': params['title_in_legend'],
            'min_value': params['minvalue'],
            'max_value': params['maxvalue']
        }
        legendClasses = json.loads(params['legendClasses'])

        if int(params['legendid']) == -1:
            newlegendid = querydb.createlegend(legend)
            # if crud_db.create('legend', legend):
            if newlegendid != -1:
                message = '{"success":true, "legendid": ' + str(newlegendid) + ',"message":"Legend created!"}'
                for legendstep in legendClasses:
                    legendstep_dict = {'legend_id': newlegendid,
                                       'from_step': float(legendstep['from_step']),
                                       'to_step': float(legendstep['to_step']),
                                       'color_rgb': legendstep['color_rgb'],
                                       'color_label': legendstep['color_label'],
                                       'group_label': legendstep['group_label']
                                       }
                    if not crud_db.create('legend_step', legendstep_dict):
                        message = '{"success":false, "message":"Error saving a legend class of the new legend!"}'
                        break
            else:
                message = '{"success":false, "message":"Error saving the new legend!"}'
        else:
            if crud_db.update('legend', legend):
                if querydb.deletelegendsteps(params['legendid']):

                    message = '{"success":true, "legendid": ' + params['legendid'] + ',"message":"Legend updated!"}'
                    for legendstep in legendClasses:
                        legendstep_dict = {'legend_id': int(params['legendid']),
                                           'from_step': float(legendstep['from_step']),
                                           'to_step': float(legendstep['to_step']),
                                           'color_rgb': legendstep['color_rgb'],
                                           'color_label': legendstep['color_label'],
                                           'group_label': legendstep['group_label']
                                           }
                        if not crud_db.create('legend_step', legendstep_dict):
                            message = '{"success":false, "message":"Error creating for updating a legend class of the legend!"}'
                            break
                else:
                    message = '{"success":false, "message":"Error deleting the legend steps!"}'
            else:
                message = '{"success":false, "message":"Error updating the legend!"}'
    else:
        message = '{"success":false, "message":"No legend data given!"}'

    return message


def GetLegendClasses(legendid):
    legendsteps_dict_all = []
    legend_steps = querydb.get_legend_steps(legendid=legendid)

    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        for legendstep in legend_steps:
            row_dict = functions.row2dict(legendstep)
            # row_dict = legendstep

            legendstep_dict = {'legend_id': row_dict['legend_id'],
                               'from_step': row_dict['from_step'],
                               'to_step': row_dict['to_step'],
                               'color_rgb': row_dict['color_rgb'],
                               'color_label': row_dict['color_label'],
                               'group_label': row_dict['group_label']
                              }

            legendsteps_dict_all.append(legendstep_dict)

        legendsteps_json = json.dumps(legendsteps_dict_all,
                                 ensure_ascii=False,
                                 encoding='utf-8',
                                 sort_keys=True,
                                 indent=4,
                                 separators=(', ', ': '))

        legendsteps_json = '{"success":"true", "total":' + str(legend_steps.__len__()) + ',"legendclasses":' + legendsteps_json + '}'

    else:
        legendsteps_json = '{"success":false, "error":"No Legends defined!"}'

    return legendsteps_json


def GetLegends():
    legends_dict_all = []
    legends = querydb.get_all_legends()

    if hasattr(legends, "__len__") and legends.__len__() > 0:
        for legend in legends:
            # row_dict = functions.row2dict(legend)
            row_dict = legend

            legend_steps = querydb.get_legend_steps(legendid=row_dict['legend_id'])

            legendname = row_dict['legend_name']
            # print legendname.encode('utf-8')
            legendname = legendname.replace('<BR>', ' ')
            legendname = legendname.replace('</BR>', ' ')
            legendname = legendname.replace('<br>', ' ')
            legendname = legendname.replace('</br>', ' ')
            legendname = legendname.replace('<div>', ' ')
            legendname = legendname.replace('</div>', ' ')
            legendname = legendname.replace('<DIV>', ' ')
            legendname = legendname.replace('</DIV>', ' ')

            # colorschemeHTML = '<table cellspacing=0 cellpadding=0 width=100%><tr><th colspan='+str(len(legend_steps))+'>'+legendname+'</th></tr><tr>'
            colorschemeHTML = legendname+'<table cellspacing=0 cellpadding=0 width=100%><tr>'

            for step in legend_steps:
                # convert step['color_rgb'] from RGB to html color
                color_rgb = step.color_rgb.split(' ')
                color_html = functions.rgb2html(color_rgb)
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = 'rgb('+r+','+g+','+b+')'
                colorschemeHTML += "<td height=15 style='padding:0; margin:0; background-color: " + color_html + ";'></td>"
            colorschemeHTML += '</tr></table>'

            legend_dict = {'legendid': row_dict['legend_id'],
                           'colourscheme': colorschemeHTML,
                           'legendname': row_dict['legend_name'],
                           'minvalue': row_dict['min_value'],
                           'maxvalue': row_dict['max_value'],
                           'legend_descriptive_name': row_dict['colorbar'],
                           'defined_by': row_dict['defined_by']
                           }

            legends_dict_all.append(legend_dict)

        legends_json = json.dumps(legends_dict_all,
                                 ensure_ascii=False,
                                 encoding='utf-8',
                                 sort_keys=True,
                                 indent=4,
                                 separators=(', ', ': '))

        legends_json = '{"success":"true", "total":' + str(legends.__len__()) + ',"legends":' + legends_json + '}'

    else:
        legends_json = '{"success":false, "error":"No Legends defined!"}'

    return legends_json


def getAllColorSchemes():
    # import time
    colorschemes_file = es_constants.base_tmp_dir + os.path.sep + 'colorschemes.json'
    if os.path.isfile(colorschemes_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(colorschemes_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            colorschemes_json = ColorSchemes().encode('utf-8')
            try:
                with open(colorschemes_file, "w") as text_file:
                    text_file.write(colorschemes_json)
            except IOError:
                try:
                    os.remove(colorschemes_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(colorschemes_file) as text_file:
                    colorschemes_json = text_file.read()
            except IOError:
                colorschemes_json = ColorSchemes().encode('utf-8')
                try:
                    os.remove(colorschemes_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        colorschemes_json = ColorSchemes().encode('utf-8')
        try:
            with open(colorschemes_file, "w") as text_file:
                text_file.write(colorschemes_json)
        except IOError:
            try:
                os.remove(colorschemes_file)  # remove file and recreate next call
            except OSError:
                pass
    return colorschemes_json


def ColorSchemes():
    all_legends = querydb.get_all_legends()

    if hasattr(all_legends, "__len__") and all_legends.__len__() > 0:
        legends_dict_all = []
        for legend in all_legends:
            # legend_dict = functions.row2dict(legend)
            # legend_dict = legend.__dict__
            legend_dict = {}
            legend_id = legend['legend_id']
            legend_name = legend['legend_name']
            # legend_name = legend['colorbar']

            legend_steps = querydb.get_legend_steps(legendid=legend_id)

            colorschemeHTML = '<table cellspacing=0 cellpadding=0 width=100%><tr>'
            for step in legend_steps:
                # convert step['color_rgb'] from RGB to html color
                color_rgb = step.color_rgb.split(' ')
                color_html = functions.rgb2html(color_rgb)
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = 'rgb('+r+','+g+','+b+')'
                colorschemeHTML = colorschemeHTML + \
                                  "<td height=15 style='padding:0; margin:0; background-color: " + \
                                  color_html + ";'></td>"
            colorschemeHTML = colorschemeHTML + '</tr></table>'

            legend_dict['legend_id'] = legend_id
            legend_dict['legend_name'] = legend_name
            legend_dict['colorbar'] = legend['colorbar']
            legend_dict['colorschemeHTML'] = colorschemeHTML
            legendsHTML = generateLegendHTML.generateLegendHTML(legend_id)
            # print legendsHTML['legendHTML']
            legend_dict['legendHTML'] = legendsHTML['legendHTML']
            legend_dict['legendHTMLVertical'] = legendsHTML['legendHTMLVertical']

            legends_dict_all.append(legend_dict)

        legends_json = json.dumps(legends_dict_all,
                                  ensure_ascii=False,
                                  sort_keys=True,
                                  indent=4,
                                  separators=(', ', ': '))

        colorschemes = '{"success":"true", "total":' + str(all_legends.__len__()) + ',"legends":'+legends_json+'}'
    else:
        colorschemes = '{"success":"true", "message":"No legends defined!"}'

    return colorschemes


def ProductNavigatorDataSets():
    db_products = querydb.get_products(echo=False, activated=None, masked=False)

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = functions.row2dict(row)
            productcode = prod_dict['productcode']
            version = prod_dict['version']

            p = Product(product_code=productcode, version=version)

            # does the product have mapsets AND subproducts?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                    if mapset_info != []:
                        mapset_dict = functions.row2dict(mapset_info)
                        mapset_dict['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print productcode + ' - ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode,
                                                                  echo=False,
                                                                  masked=True)

                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                dataset_dict['mapsetcode'] = mapset

                                # dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                # completeness = dataset.get_dataset_normalized_info()
                                # dataset_dict['datasetcompleteness'] = completeness

                                mapset_dict['mapsetdatasets'].append(dataset_dict)
                        if mapset_dict['mapsetdatasets'].__len__() > 0:
                            prod_dict['productmapsets'].append(mapset_dict)
                products_dict_all.append(prod_dict)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        datamanagement_json = '{"success":"true", "total":'\
                              + str(db_products.__len__())\
                              + ',"products":'+prod_json+'}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    return datamanagement_json


def getDataSets(forse):
    # import time
    datasetsinfo_file = es_constants.base_tmp_dir + os.path.sep + 'datasets_info.json'
    if forse:
        datamanagement_json = DataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(datamanagement_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(datasetsinfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(datasetsinfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            datamanagement_json = DataSets().encode('utf-8')
            try:
                with open(datasetsinfo_file, "w") as text_file:
                    text_file.write(datamanagement_json)
            except IOError:
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(datasetsinfo_file) as text_file:
                    datamanagement_json = text_file.read()
            except IOError:
                datamanagement_json = DataSets().encode('utf-8')
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        datamanagement_json = DataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(datamanagement_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return datamanagement_json


def DataSets():
    from dateutil.relativedelta import relativedelta

    db_products = querydb.get_products(activated=True)

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = functions.row2dict(row)
            productcode = prod_dict['productcode']
            version = prod_dict['version']

            p = Product(product_code=productcode, version=version)
            # print productcode
            # does the product have mapsets AND subproducts?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_dict = []
                    # print mapset
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                    if mapset_info != []:
                        mapset_dict = functions.row2dict(mapset_info)
                        # print mapset_dict
                        mapset_dict['productcode'] = productcode
                        mapset_dict['version'] = version
                        # else:
                        #   mapset_dict['mapsetcode'] = mapset
                        mapset_dict['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print 'productcode: ' + productcode
                            # print 'version: ' + version
                            # print 'subproductcode: ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode,
                                                                  echo=False)
                            # print dataset_info
                            # dataset_info = querydb.db.product.get(productcode, version, subproductcode)
                            # dataset_dict = {}
                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                # dataset_dict = dataset_info.__dict__
                                # del dataset_dict['_labels']
                                if hasattr(dataset_info, 'frequency_id'):
                                    if dataset_info.frequency_id == 'e15minute':
                                        # dataset_dict['nodisplay'] = 'no_minutes_display'
                                        today = datetime.date.today()
                                        from_date = today - datetime.timedelta(days=3)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    elif dataset_info.frequency_id == 'e30minute':
                                        # dataset_dict['nodisplay'] = 'no_minutes_display'
                                        today = datetime.date.today()
                                        from_date = today - datetime.timedelta(days=6)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    # elif dataset_info.frequency_id == 'e1year':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'

                                    elif dataset_info.frequency_id == 'e1day':
                                        today = datetime.date.today()
                                        from_date = today - relativedelta(years=1)
                                        # if sys.platform != 'win32':
                                        #     from_date = today - relativedelta(years=1)
                                        # else:
                                        #     from_date = today - datetime.timedelta(days=365)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    else:
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode}

                                    # if dataset_info.frequency_id == 'e15minute' or dataset_info.frequency_id == 'e30minute':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # # To be implemented in dataset.py
                                    # elif dataset_info.frequency_id == 'e1year':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # else:
                                    #     dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                    dataset = p.get_dataset(**kwargs)
                                    completeness = dataset.get_dataset_normalized_info()
                                    dataset_dict['datasetcompleteness'] = completeness
                                    dataset_dict['nodisplay'] = 'false'

                                    dataset_dict['mapsetcode'] = mapset_dict['mapsetcode']
                                    dataset_dict['mapset_descriptive_name'] = mapset_dict['descriptive_name']

                                    mapset_dict['mapsetdatasets'].append(dataset_dict)
                                else:
                                    pass
                    prod_dict['productmapsets'].append(mapset_dict)
            products_dict_all.append(prod_dict)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        datamanagement_json = '{"success":"true", "total":' \
                              + str(db_products.__len__()) \
                              + ',"products":' + prod_json + '}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    datamanagement_json = datamanagement_json.replace('\\r\\n', ' ')
    datamanagement_json = datamanagement_json.replace("'", "\'")
    datamanagement_json = datamanagement_json.replace(', ', ',')
    return datamanagement_json


def getTimeseriesProducts(forse):
    # import time
    timeseriesproducts_file = es_constants.base_tmp_dir + os.path.sep + 'timeseries_products.json'

    if forse:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
        try:
            with open(timeseriesproducts_file, "w") as text_file:
                text_file.write(timeseriesproducts_json)
        except IOError:
            try:
                os.remove(timeseriesproducts_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(timeseriesproducts_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(timeseriesproducts_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5  hours
            timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
            try:
                with open(timeseriesproducts_file, "w") as text_file:
                    text_file.write(timeseriesproducts_json)
            except IOError:
                try:
                    os.remove(timeseriesproducts_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(timeseriesproducts_file) as text_file:
                    timeseriesproducts_json = text_file.read()
            except IOError:
                timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
                try:
                    os.remove(timeseriesproducts_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
        try:
            with open(timeseriesproducts_file, "w") as text_file:
                text_file.write(timeseriesproducts_json)
        except IOError:
            try:
                os.remove(timeseriesproducts_file)  # remove file and recreate next call
            except OSError:
                pass

    return timeseriesproducts_json


def TimeseriesProducts():
    # import copy
    # import time
    # t0 = time.time()
    # print 'START: ' + str(t0)

    db_products = querydb.get_timeseries_products()
    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        for row in db_products:
            prod_dict = {}
            prod_record = functions.row2dict(row)
            productcode = prod_record['productcode']
            subproductcode = prod_record['subproductcode']
            version = prod_record['version']

            prod_dict['category_id'] = prod_record['category_id']
            prod_dict['cat_descr_name'] = prod_record['cat_descr_name']
            prod_dict['order_index'] = prod_record['order_index']
            prod_dict['display_index'] = prod_record['display_index']
            prod_dict['productid'] = prod_record['productid']
            prod_dict['productcode'] = prod_record['productcode']
            prod_dict['version'] = prod_record['version']
            prod_dict['subproductcode'] = prod_record['subproductcode']
            # prod_dict['mapsetcode'] = ""
            # prod_dict['mapset_name'] = ""
            prod_dict['group_product_descriptive_name'] = prod_record['group_product_descriptive_name']
            prod_dict['product_descriptive_name'] = prod_record['descriptive_name']
            prod_dict['product_description'] = prod_record['description']
            prod_dict['frequency_id'] = prod_record['frequency_id']
            prod_dict['date_format'] = prod_record['date_format']
            prod_dict['timeseries_role'] = prod_record['timeseries_role']
            prod_dict['selected'] = False
            prod_dict['cumulative'] = False
            prod_dict['difference'] = False
            prod_dict['reference'] = False
            # prod_dict['years'] = []

            # does the product have mapsets?
            # t1 = time.time()
            # print 'before calling Product(): ' + str(t1)
            p = Product(product_code=productcode, version=version)
            # t2 = time.time()
            # print 'after calling Product(): ' + str(t2-t1)

            all_prod_mapsets = p.mapsets
            if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                    if mapset_info != []:
                        mapset_record = functions.row2dict(mapset_info)

                        prod_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_record['mapsetcode']
                        prod_dict['mapsetcode'] = mapset_record['mapsetcode']
                        prod_dict['mapset_name'] = mapset_record['descriptive_name']

                        # t3 = time.time()
                        # print 'before getting dataset info: ' + str(t3)

                        dataset = p.get_dataset(mapset=mapset, sub_product_code=prod_dict['subproductcode'])
                        # dataset.get_filenames()
                        all_present_product_dates = dataset.get_dates()

                        # t4 = time.time()
                        # tot_get_dataset = t4-t3
                        # print 'after getting dataset info: ' + str(tot_get_dataset)


                        # t5 = time.time()
                        # print 'before getting years: ' + str(t5)

                        distinctyears = []
                        for product_date in all_present_product_dates:
                            if product_date.year not in distinctyears:
                                distinctyears.append(product_date.year)
                        prod_dict['years'] = distinctyears

                        if prod_dict['years'].__len__() > 0:
                            products_dict_all.append(prod_dict)
                            # tmp_prod_dict = copy.deepcopy(prod_dict)
                            #
                            # products_dict_all.append(tmp_prod_dict)
                            # tmp_prod_dict = []

                        # t6 = time.time()
                        # total = t6-t5
                        # print 'after getting years: ' + str(total)

                        timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                        version=version,
                                                                                        subproductcode=subproductcode)
                        # t7 = time.time()
                        # print 'before getting subproduct info: ' + str(t7)

                        for subproduct in timeseries_mapset_datasets:
                            if subproduct is not None:
                                # t7 = time.time()
                                dataset_record = functions.row2dict(subproduct)
                                dataset = p.get_dataset(mapset=mapset,
                                                        sub_product_code=dataset_record['subproductcode'])
                                # t8 = time.time()
                                # totals_subproduct = t8 - t7
                                # print 'after getting subproduct dataset: ' + str(totals_subproduct)

                                # dataset.get_filenames()
                                all_present_product_dates = dataset.get_dates()

                                distinctyears = []
                                for product_date in all_present_product_dates:
                                    if product_date.year not in distinctyears:
                                        distinctyears.append(product_date.year)

                                dataset_dict = {}
                                dataset_dict['category_id'] = prod_record['category_id']
                                dataset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                                dataset_dict['order_index'] = prod_record['order_index']
                                dataset_dict['productid'] = dataset_record['productid']
                                dataset_dict['productcode'] = dataset_record['productcode']
                                dataset_dict['version'] = dataset_record['version']
                                dataset_dict['subproductcode'] = dataset_record['subproductcode']
                                dataset_dict['productmapsetid'] = prod_dict['productmapsetid']
                                dataset_dict['display_index'] = dataset_record['display_index']
                                dataset_dict['mapsetcode'] = mapset_record['mapsetcode']
                                dataset_dict['mapset_name'] = mapset_record['descriptive_name']
                                dataset_dict['group_product_descriptive_name'] = prod_record['group_product_descriptive_name']
                                dataset_dict['product_descriptive_name'] = dataset_record['descriptive_name']
                                dataset_dict['product_description'] = dataset_record['description']
                                dataset_dict['frequency_id'] = dataset_record['frequency_id']
                                dataset_dict['date_format'] = dataset_record['date_format']
                                dataset_dict['timeseries_role'] = dataset_record['timeseries_role']
                                dataset_dict['years'] = distinctyears
                                dataset_dict['selected'] = False
                                dataset_dict['cumulative'] = False
                                dataset_dict['difference'] = False
                                dataset_dict['reference'] = False

                                if dataset_dict['years'].__len__() > 0:
                                    products_dict_all.append(dataset_dict)
                                    # # tmp_prod_dict = prod_dict.copy()
                                    # tmp_prod_dict = copy.deepcopy(dataset_dict)
                                    #
                                    # products_dict_all.append(tmp_prod_dict)
                                    # tmp_prod_dict = []

                        # t8 = time.time()
                        # totals_subproduct = t8-t7
                        # print 'after getting subproduct info: ' + str(totals_subproduct)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        timeseriesproducts_json = '{"success":"true", "total":' \
                                  + str(db_products.__len__()) \
                                  + ',"products":' + prod_json + '}'

    else:
        timeseriesproducts_json = '{"success":false, "error":"No data sets defined!"}'

    # t9 = time.time()
    # total = t9-t0
    # print 'Total time: ' + str(total)

    timeseriesproducts_json = timeseriesproducts_json.replace('\\r\\n', ' ')
    timeseriesproducts_json = timeseriesproducts_json.replace("'", "\'")
    timeseriesproducts_json = timeseriesproducts_json.replace(', ', ',')
    return timeseriesproducts_json


def getIngestion(forse):
    # import time
    ingestioninfo_file = es_constants.base_tmp_dir + os.path.sep + 'ingestion_info.json'
    if forse:
        ingestions_json = Ingestion().encode('utf-8')
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
        except IOError:
            try:
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(ingestioninfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(ingestioninfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            ingestions_json = Ingestion().encode('utf-8')
            try:
                with open(ingestioninfo_file, "w") as text_file:
                    text_file.write(ingestions_json)
            except IOError:
                try:
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(ingestioninfo_file) as text_file:
                    ingestions_json = text_file.read()
            except IOError:
                ingestions_json = Ingestion().encode('utf-8')
                try:
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        ingestions_json = Ingestion().encode('utf-8')
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
        except IOError:
            try:
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return ingestions_json


def Ingestion():
    from dateutil.relativedelta import relativedelta

    # return web.ctx
    ingestions = querydb.get_ingestions(echo=False)
    # print ingestions

    if hasattr(ingestions, "__len__") and ingestions.__len__() > 0:
        ingest_dict_all = []
        for row in ingestions:
            ingest_dict = functions.row2dict(row)

            if row.mapsetcode != None and row.mapsetcode != '':
                if row.frequency_id == 'e15minute':
                    # ingest_dict['nodisplay'] = 'no_minutes_display'
                    today = datetime.date.today()
                    from_date = today - datetime.timedelta(days=3)
                    # week_ago = datetime.datetime(2015, 8, 27, 00, 00)   # .strftime('%Y%m%d%H%S')
                    # kwargs.update({'from_date': week_ago})  # datetime.date(2015, 08, 27)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                    # dataset = Dataset(**kwargs)
                    # completeness = dataset.get_dataset_normalized_info()
                elif row.frequency_id == 'e30minute':
                    today = datetime.date.today()
                    from_date = today - datetime.timedelta(days=6)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                elif row.frequency_id == 'e1day':
                    today = datetime.date.today()
                    from_date = today - relativedelta(years=1)

                    # if sys.platform != 'win32':
                    #     from_date = today - relativedelta(years=1)
                    # else:
                    #     from_date = today - datetime.timedelta(days=365)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                else:
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode}
                # print kwargs
                dataset = Dataset(**kwargs)
                completeness = dataset.get_dataset_normalized_info()
                ingest_dict['completeness'] = completeness
                ingest_dict['nodisplay'] = 'false'
            else:
                ingest_dict['completeness'] = {}
                ingest_dict['nodisplay'] = 'false'

            ingest_dict_all.append(ingest_dict)

        # ingestions_json = tojson(ingestions)
        ingestions_json = json.dumps(ingest_dict_all,
                                     ensure_ascii=False,
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))
        ingestions_json = '{"success":"true", "total":' + str(
            ingestions.__len__()) + ',"ingestions":' + ingestions_json + '}'
    else:
        ingestions_json = '{"success":false, "error":"No ingestions defined!"}'

    ingestions_json = ingestions_json.replace('\\r\\n', ' ')
    ingestions_json = ingestions_json.replace("'", "\'")
    ingestions_json = ingestions_json.replace(', ', ',')
    return ingestions_json


def getProcessing(forse):
    # import time
    forse = True
    processinginfo_file = es_constants.base_tmp_dir + os.path.sep + 'processing_info.json'
    if forse:
        processing_chains_json = Processing().encode('utf-8')
        try:
            with open(processinginfo_file, "w") as text_file:
                text_file.write(processing_chains_json)
        except IOError:
            try:
                os.remove(processinginfo_file)  # remove file and recreate next call
            except OSError:
                pass
        finally:
            text_file.close()

    elif os.path.isfile(processinginfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(processinginfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            processing_chains_json = Processing().encode('utf-8')
            try:
                with open(processinginfo_file, "w") as text_file:
                    text_file.write(processing_chains_json)
            except IOError:
                try:
                    os.remove(processinginfo_file)  # remove file and recreate next call
                except OSError:
                    pass
            finally:
                text_file.close()
        else:
            try:
                with open(processinginfo_file) as text_file:
                    processing_chains_json = text_file.read()
                    # processing_chains_json = json.loads(processing_chains_json)
            except IOError:
                processing_chains_json = Processing().encode('utf-8')
                try:
                    os.remove(processinginfo_file)  # remove file and recreate next call
                except OSError:
                    pass
            finally:
                text_file.close()

    else:
        processing_chains_json = Processing().encode('utf-8')
        try:
            with open(processinginfo_file, "w") as text_file:
                text_file.write(processing_chains_json)
        except IOError:
            try:
                os.remove(processinginfo_file)  # remove file and recreate next call
            except OSError:
                pass
        finally:
            text_file.close()

    return processing_chains_json


def Processing():
    #   Todo JURVTK: on each call of a processing chain for a product, get the list of output (sub)products from the
    #   Todo JURVTK: processing chain algorithm using processing_std_precip . get_subprods_std_precip () and loop
    #   Todo JURVTK: this list to check the existance of the output product in the table product.process_product
    #   Todo JURVTK: Insert the output product in the table product.process_product if no record exists.
    #   Todo JURVTK:  Use: from apps . processing import processing_std_precip
    #   Todo JURVTK:       brachet l1, l2 brachet = processing_std_precip . get_subprods_std_precip ()

    processing_chains_json = '{"success":true, "message":"No processing chains defined!"}'

    processing_chains = querydb.get_processing_chains()

    if hasattr(processing_chains, "__len__") and processing_chains.__len__() > 0:
        processing_chains_dict_all = []

        for process in processing_chains:
            process_id = process.process_id
            process_dict = functions.row2dict(process)

            db_process_input_products = querydb.get_processingchains_input_products(process_id)
            process_dict['inputproducts'] = []
            if hasattr(db_process_input_products, "__len__") and db_process_input_products.__len__() > 0:

                for input_product in db_process_input_products:
                    # process_id = input_product.process_id
                    input_mapsetcode = input_product.mapsetcode
                    process_dict['category_id'] = input_product.category_id
                    process_dict['cat_descr_name'] = input_product.cat_descr_name
                    process_dict['order_index'] = input_product.order_index

                    input_prod_dict = functions.row2dict(input_product)
                    # prod_dict = input_product.__dict__
                    # del prod_dict['_labels']
                    # input_prod_dict['inputproductmapset'] = []
                    # mapset_info = querydb.get_mapset(mapsetcode=input_mapsetcode)
                    # mapset_dict = functions.row2dict(mapset_info)
                    # input_prod_dict['inputproductmapset'].append(mapset_dict)
                    process_dict['inputproducts'].append(input_prod_dict)

            db_process_output_products = querydb.get_processingchain_output_products(process_id)
            process_dict['outputproducts'] = []
            if hasattr(db_process_output_products, "__len__") and db_process_output_products.__len__() > 0:
                for outputproduct in db_process_output_products:
                    output_mapsetcode = outputproduct.mapsetcode
                    output_product_dict = functions.row2dict(outputproduct)
                    # output_product_dict = outputproduct.__dict__
                    # del outputproduct_dict['_labels']

                    # output_product_dict['outputproductmapset'] = []
                    # mapset_info = querydb.get_mapset(mapsetcode=output_mapsetcode)
                    # mapset_dict = functions.row2dict(mapset_info)
                    # output_product_dict['outputproductmapset'].append(mapset_dict)
                    process_dict['outputproducts'].append(output_product_dict)

            processing_chains_dict_all.append(process_dict)

            processes_json = json.dumps(processing_chains_dict_all,
                                        ensure_ascii=False,
                                        sort_keys=True,
                                        indent=4,
                                        separators=(', ', ': '))

            processing_chains_json = '{"success":"true", "total":' \
                                     + str(processing_chains.__len__()) \
                                     + ',"processes":' + processes_json + '}'

    processing_chains_json = processing_chains_json.replace('\\r\\n', ' ')
    processing_chains_json = processing_chains_json.replace('\\n', ' ')
    processing_chains_json = processing_chains_json.replace("'", "\'")
    processing_chains_json = processing_chains_json.replace(', ', ',')
    return processing_chains_json