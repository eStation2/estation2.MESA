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

# import config
from config import es_constants
# import locals
from database import querydb
from database import crud

from apps.acquisition import get_eumetcast
from apps.acquisition import acquisition
from apps.processing import processing
from apps.productmanagement.datasets import Dataset
from apps.es2system import es2system
# from apps.productmanagement.datasets import Frequency
from apps.productmanagement.products import Product
from apps.analysis import generateLegendHTML

from lib.python import functions
from lib.python import es_logging as log

logger = log.my_logger(__name__)


WEBPY_COOKIE_NAME = "webpy_session_id"

urls = (
    "/pa(.*)", "ProductAcquisition",
    "/product/update", "UpdateProduct",
    "/product/createproduct", "CreateProduct",
    "/product/updateproductinfo", "UpdateProductInfo",
    "/product/unassigndatasource", "UnassignProductDataSource",

    "/users", "Users",
    "/login", "Login",
    "/register", "Register",

    "/help", "GetHelp",
    "/help/getfile", "GetHelpFile",

    "/categories", "GetCategories",
    "/frequencies", "GetFrequencies",
    "/dateformats", "GetDateFormats",
    "/datatypes", "GetDataTypes",

    "/dashboard/getdashboard", "GetDashboard",
    "/dashboard/systemstatus", "GetSystemStatus",
    "/dashboard/setdataautosync", "SetDataAutoSync",
    "/dashboard/setdbautosync", "SetDBAutoSync",

    "/services/checkstatusall", "CheckStatusAllServices",
    "/services/execservicetask", "ExecuteServiceTask",

    "/ingestion", "Ingestion",
    "/ingestion/update", "UpdateIngestion",

    "/getlogfile", "GetLogFile",

    "/acquisition/setingestarchives", "setIngestArchives",
    "/dataacquisition", "DataAcquisition",
    "/dataacquisition/update", "UpdateDataAcquisition",

    "/eumetcastsource", "GetEumetcastSources",
    "/eumetcastsource/create", "CreateEumetcastSource",
    "/eumetcastsource/update", "UpdateEumetcastSource",
    "/eumetcastsource/delete", "DeleteEumetcastSource",
    "/eumetcastsource/assigntoproduct", "AssignEumetcastSource",

    "/internetsource", "GetInternetSources",
    "/internetsource/create", "CreateInternetSource",
    "/internetsource/update", "UpdateInternetSource",
    "/internetsource/delete", "DeleteInternetSource",
    "/internetsource/assigntoproduct", "AssignInternetSource",

    "/systemsettings", "UserSettings",
    "/systemsettings/update", "UpdateUserSettings",
    "/systemsettings/changerole", "ChangeRole",
    "/systemsettings/reset", "ResetUserSettings",
    "/systemsettings/systemreport", "SystemReport",
    "/systemsettings/installreport", "InstallReport",
    "/systemsettings/changemode", "ChangeMode",
    "/systemsettings/getversions", "GetAvailableVersions",
    "/systemsettings/changeversion", "ChangeVersion",
    "/systemsettings/getthemas", "GetThemas",
    "/systemsettings/changethema", "ChangeThema",
    "/systemsettings/changethemafromotherpc", "ChangeThemaFromOtherPC",
    "/systemsettings/changeloglevel", "ChangeLogLevel",
    "/systemsettings/ipsettings", "IPSettings",
    "/systemsettings/ipsettings/update", "UpdateIPSettings",

    "/processing", "Processing",
    "/processing/update", "UpdateProcessing",

    "/datasets", "DataSets",
    "/datamanagement/getrequest", "GetRequest",
    "/datamanagement/saverequest", "SaveRequest",

    "/analysis/getproductlayer", "GetProductLayer",
    "/analysis/getvectorlayer", "GetVectorLayer",
    "/analysis/getbackgroundlayer", "GetBackgroundLayer",
    "/analysis/productnavigator", "ProductNavigatorDataSets",
    "/analysis/getcolorschemes", "GetAllColorSchemes",
    "/analysis/getproductcolorschemes", "GetProductColorSchemes",
    "/analysis/gettimeline", "GetTimeLine",
    "/analysis/timeseriesproduct", "TimeseriesProducts",
    "/analysis/gettimeseries", "GetTimeseries",
    "/analysis/getchartproperties", "GetChartProperties",
    "/analysis/getchartproperties/update", "UpdateChartProperties",
    "/analysis/gettimeseriesdrawproperties", "GetTimeseriesDrawProperties",
    "/analysis/gettimeseriesdrawproperties/update", "UpdateTimeseriesDrawProperties",
    "/analysis/gettimeseriesdrawproperties/create", "CreateTimeseriesDrawProperties",
    "/analysis/updateyaxe", "UpdateYaxe",
    "/analysis/savemaptemplate", "SaveMapTemplate",
    "/analysis/usermaptemplates", "GetMapTemplates",
    "/analysis/usermaptemplates/delete", "DeleteMapTemplate",

    "/layers", "GetLayers",
    "/layers/create", "CreateLayer",
    "/layers/update", "UpdateLayer",
    "/layers/delete", "DeleteLayer",
    "/layers/import", "ImportLayer",
    "/layers/serverlayerfiles", "GetServerLayerFileList",
    "/layers/savedrawnlayer", "SaveDrawnVectorLayer",

    "/getmapsets", "GetMapsets",
    "/addingestmapset", "AddIngestMapset",
    "/deleteingestmapset", "DisableIngestMapset",

    "/getlanguages", "GetLanguages",
    "/geti18n", "GetI18n",

    # "/(.+)/(.+)", "EsApp",
    # "/(.+)/", "EsApp",
    "/", "EsApp")

app = web.application(urls, globals(), autoreload=True)
application = app.wsgifunc()
# session = web.session.Session(app, web.session.DiskStore('../logs/mstmp/webpySessions'))


class EsApp:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        #return web.ctx
        getparams = web.input()
        if hasattr(getparams, "lang"):
            # print getparams['lang']
            functions.setUserSetting('default_language', getparams['lang'])
            es_constants.es2globals['default_language'] = getparams['lang']

        render = web.template.render(es_constants.es2globals['base_dir']+'/apps/gui/esapp')

        return render.index()

        # # print 'default_language: ' + es_constants.es2globals['default_language']
        # if es_constants.es2globals['default_language'] == 'eng':
        #     # print 'rendering index'
        #     return render.index()
        # elif es_constants.es2globals['default_language'] == 'fra':
        #     # print 'rendering index_fr'
        #     return render.index_fr()
        # else:
        #     return render.index()


class GetMapTemplates:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        maptemplate_dict_all = []
        getparams = web.input()

        if 'userid' in getparams:
            usermaptemplates = querydb.get_user_map_templates(getparams['userid'])
            if hasattr(usermaptemplates, "__len__") and usermaptemplates.__len__() > 0:
                for row_dict in usermaptemplates:
                    # row_dict = functions.row2dict(row)

                    mapTemplate = {
                        'userid': row_dict['userid'],
                        'templatename': row_dict['templatename'],
                        'mapviewposition': row_dict['mapviewposition'],
                        'mapviewsize': row_dict['mapviewsize'],
                        'productcode': row_dict['productcode'],
                        'subproductcode': row_dict['subproductcode'],
                        'productversion': row_dict['productversion'],
                        'mapsetcode': row_dict['mapsetcode'],
                        'legendid': row_dict['legendid'],
                        'legendlayout': row_dict['legendlayout'],
                        'legendobjposition': row_dict['legendobjposition'],
                        'showlegend': row_dict['showlegend'],
                        'titleobjposition': row_dict['titleobjposition'],
                        'titleobjcontent': row_dict['titleobjcontent'],
                        'disclaimerobjposition': row_dict['disclaimerobjposition'],
                        'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                        'logosobjposition': row_dict['logosobjposition'],
                        'logosobjcontent': row_dict['logosobjcontent'],
                        'showobjects': row_dict['showobjects'],
                        'scalelineobjposition': row_dict['scalelineobjposition'],
                        'vectorlayers': row_dict['vectorlayers'],
                        'outmaskfeature': row_dict['outmaskfeature'],
                        'auto_open': row_dict['auto_open']
                    }

                    maptemplate_dict_all.append(mapTemplate)

                maptemplates_json = json.dumps(maptemplate_dict_all,
                                                  ensure_ascii=False,
                                                  encoding='utf-8',
                                                  sort_keys=True,
                                                  indent=4,
                                                  separators=(', ', ': '))

                maptemplates_json = '{"success":"true", "total":'\
                                       + str(usermaptemplates.__len__())\
                                       + ',"usermaptemplates":'+maptemplates_json+'}'

            else:
                maptemplates_json = '{"success":false, "error":"No Map Templates defined for user!"}'   # OR RETURN A DEFAULT MAP TEMPLATE?????

        else:
            maptemplates_json = '{"success":false, "error":"Userid not given!"}'

        return maptemplates_json


class DeleteMapTemplate:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'usermaptemplate' in getparams:      # hasattr(getparams, "layer")
            maptemplatePK = {
                'userid': getparams['usermaptemplate']['userid'],
                'templatename': getparams['usermaptemplate']['templatename'],
             }

            if self.crud_db.delete('map_templates', **maptemplatePK):
                status = '{"success":"true", "message":"Map Template deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the Map Template!"}'

        else:
            status = '{"success":false, "message":"No Map Template info passed!"}'

        return status


class SaveMapTemplate:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = web.input()
        # getparams = json.loads(web.data())  # get PUT data

        createstatus = '{"success":"false", "message":"An error occured while saving the Map Template!"}'

        if 'userid' in getparams and 'templatename' in getparams:
            legendid = getparams['legendid']
            if getparams['legendid'] == '':
                legendid = None

            mapTemplate = {
                'userid': getparams['userid'],
                'templatename': getparams['templatename'],
                'mapviewposition': getparams['mapviewPosition'],
                'mapviewsize': getparams['mapviewSize'],
                'productcode': getparams['productcode'],
                'subproductcode': getparams['subproductcode'],
                'productversion': getparams['productversion'],
                'mapsetcode': getparams['mapsetcode'],
                'legendid': legendid,
                'legendlayout': getparams['legendlayout'],
                'legendobjposition': getparams['legendObjPosition'],
                'showlegend': getparams['showlegend'],
                'titleobjposition': getparams['titleObjPosition'],
                'titleobjcontent': getparams['titleObjContent'],
                'disclaimerobjposition': getparams['disclaimerObjPosition'],
                'disclaimerobjcontent': getparams['disclaimerObjContent'],
                'logosobjposition': getparams['logosObjPosition'],
                'logosobjcontent': getparams['logosObjContent'],
                'showobjects': getparams['showObjects'],
                'scalelineobjposition': getparams['scalelineObjPosition'],
                'vectorlayers': getparams['vectorLayers'],
                'outmaskfeature': getparams['outmaskFeature'],
                'auto_open': getparams['auto_open']
            }

            # print getparams
            if getparams['newtemplate'] == 'true':
                if self.crud_db.create('map_templates', mapTemplate):
                    createstatus = '{"success":"true", "message":"Map Template created!"}'
            else:
                if self.crud_db.update('map_templates', mapTemplate):
                    createstatus = '{"success":"true", "message":"Map Template updated!"}'

        else:
            createstatus = '{"success":"false", "message":"No Map Template data given!"}'

        return createstatus


class Register:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = web.input()
        # getparams = json.loads(web.data())  # get PUT data

        createstatus = '{"success":"false", "message":"An error occured while registering the user!"}'

        if 'user' in getparams:
            user = {
                'username': getparams['fullname'],
                'password': getparams['pass'],
                'userid': getparams['user'],
                'userlevel': 1,
                'email': getparams['email']
            }

            if self.crud_db.create('users', user):
                createstatus = '{"success":"true", "message":"User created!"}'
        else:
            createstatus = '{"success":"false", "message":"No user data given!"}'

        return createstatus


class Users:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # inputObj = web.input()
        try:
            users = querydb.getusers()

            users_dict_all = []
            if hasattr(users, "__len__") and users.__len__() > 0:
                for row in users:
                    user_info = {
                        'username': row['username'],
                        'userid': row['userid'],
                        'userlevel': row['userlevel'],
                        'email': row['email']
                    }
                    users_dict_all.append(user_info)

                user_info_json = json.dumps(users_dict_all,
                                            ensure_ascii=False,
                                            encoding='utf-8',
                                            sort_keys=False,
                                            indent=4,
                                            separators=(', ', ': '))

                users_json = '{"success":true, "users":'+ user_info_json + '}'
            else:
                users_json = '{"success":true, "message":"No users defined in the DB!"}'

        except:
            users_json = '{"success":false, "error":"Error reading users data from DB!"}'

        return users_json


class Login:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        login = web.input()

        if 'username' in login:
            try:
                userinfo = querydb.checklogin(login)

                if hasattr(userinfo, "__len__") and userinfo.__len__() > 0:
                    for row in userinfo:
                        # row_dict = functions.row2dict(row)
                        row_dict = row
                        user_info = {
                            'username': row_dict['username'],
                            'password': row_dict['password'],
                            'userid': row_dict['userid'],
                            # 'userlevel': row_dict['userlevel'],
                            'email': row_dict['email']
                            # 'timestamp': row_dict['timestamp']
                        }

                    user_info_json = json.dumps(user_info,
                                                ensure_ascii=False,
                                                encoding='utf-8',
                                                sort_keys=True,
                                                indent=4,
                                                separators=(', ', ': '))
                    # print user_info_json
                    login_json = '{"success":true, "user":'+ user_info_json + '}'
                    # print login_json
                else:
                    login_json = '{"success":false, "error":"Username or password incorrect!"}'

            except:
                login_json = '{"success":false, "error":"Error reading login data in DB!"}'
        else:
            login_json = '{"success":false, "error":"No user name given!"}'

        return login_json


class UpdateYaxe:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        yaxe = web.input()

        if 'id' in yaxe: # to check if the file-object is created
            try:
                querydb.update_yaxe_timeseries_drawproperties(yaxe)
                yaxeproperties_json = '{"success":true, "message":"Yaxe updated"}'
            except:
                yaxeproperties_json = '{"success":false, "error":"Error saving the Yaxe properties in the database!"}'
        else:
            yaxeproperties_json = '{"success":false, "error":"No Yaxe properties given!"}'

        return yaxeproperties_json


class CreateTimeseriesDrawProperties:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        # getparams = web.input()
        getparams = json.loads(web.data())  # get PUT data

        createstatus = '{"success":"false", "message":"An error occured while creating the Timeseries Draw Properties!"}'

        # if hasattr(getparams['tsdrawproperties'], "yaxes_id"):
        if 'tsdrawproperties' in getparams:
            tsdrawproperties = getparams['tsdrawproperties']

            if self.crud_db.create('timeseries_drawproperties', tsdrawproperties):
                createstatus = '{"success":"true", "message":"Timeseries Draw Properties created!"}'
        else:
            createstatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

        return createstatus


class UpdateTimeseriesDrawProperties:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def PUT(self):
        # getparams = web.input()
        getparams = json.loads(web.data())  # get PUT data

        updatestatus = '{"success":"false", "message":"An error occured while updating the Timeseries Draw Properties!"}'

        if 'tsdrawproperties' in getparams:
            tsdrawproperties = getparams['tsdrawproperties']

            if self.crud_db.update('timeseries_drawproperties', tsdrawproperties):
                updatestatus = '{"success":"true", "message":"Timeseries Draw Properties updated!"}'
        else:
            createstatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

        return updatestatus


class GetTimeseriesDrawProperties:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        tsdrawproperties_dict_all = []
        tsdrawproperties = querydb.get_timeseries_drawproperties()

        if hasattr(tsdrawproperties, "__len__") and tsdrawproperties.__len__() > 0:
            for row in tsdrawproperties:
                # row_dict = functions.row2dict(row)
                row_dict = row

                tsdrawproperty = {
                                  'productcode': row_dict['productcode'],
                                  'subproductcode': row_dict['subproductcode'],
                                  'version': row_dict['version'],
                                  'title': row_dict['title'],
                                  'unit': row_dict['unit'],
                                  'min': row_dict['min'],
                                  'max': row_dict['max'],
                                  'oposite': row_dict['oposite'],
                                  'tsname_in_legend': row_dict['tsname_in_legend'],
                                  'charttype': row_dict['charttype'],
                                  'linestyle': row_dict['linestyle'],
                                  'linewidth': row_dict['linewidth'],
                                  'color': row_dict['color'],
                                  'yaxes_id': row_dict['yaxes_id'],
                                  'title_color': row_dict['title_color'],
                                  'aggregation_type': row_dict['aggregation_type'],
                                  'aggregation_min': row_dict['aggregation_min'],
                                  'aggregation_max': row_dict['aggregation_max']
                                }

                tsdrawproperties_dict_all.append(tsdrawproperty)

            tsdrawproperties_json = json.dumps(tsdrawproperties_dict_all,
                                              ensure_ascii=False,
                                              encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            tsdrawproperties_json = '{"success":"true", "total":'\
                                   + str(tsdrawproperties.__len__())\
                                   + ',"tsdrawproperties":'+tsdrawproperties_json+'}'

        else:
            tsdrawproperties_json = '{"success":false, "error":"No timeseries draw properties defined!"}'

        return tsdrawproperties_json


class GetChartProperties:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        charttype = 'default'
        if hasattr(getparams, "charttype") and getparams['charttype'] != '':
            charttype = getparams['charttype']

        chartproperties_dict_all = []
        chartproperties = querydb.get_chart_drawproperties(charttype)

        if hasattr(chartproperties, "__len__") and chartproperties.__len__() > 0:
            for row in chartproperties:
                row_dict = functions.row2dict(row)

                chartproperty = { 'chart_type': row_dict['chart_type'],
                                  'chart_width': row_dict['chart_width'],
                                  'chart_height': row_dict['chart_height'],
                                  'chart_title_font_size': row_dict['chart_title_font_size'],
                                  'chart_title_font_color': row_dict['chart_title_font_color'],
                                  'chart_subtitle_font_size': row_dict['chart_subtitle_font_size'],
                                  'chart_subtitle_font_color': row_dict['chart_subtitle_font_color'],
                                  'yaxe1_font_size': row_dict['yaxe1_font_size'],
                                  'yaxe2_font_size': row_dict['yaxe2_font_size'],
                                  'yaxe3_font_size': row_dict['yaxe3_font_size'],
                                  'legend_font_size': row_dict['legend_font_size'],
                                  'legend_font_color': row_dict['legend_font_color'],
                                  'xaxe_font_size': row_dict['xaxe_font_size'],
                                  'xaxe_font_color': row_dict['xaxe_font_color']
                                }

                chartproperties_dict_all.append(chartproperty)

            chartproperties_json = json.dumps(chartproperties_dict_all,
                                              ensure_ascii=False,
                                              encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            chartproperties_json = '{"success":"true", "total":'\
                                   + str(chartproperties.__len__())\
                                   + ',"chartproperties":'+chartproperties_json+'}'

        else:
            chartproperties_json = '{"success":false, "error":"No chart properties defined!"}'

        return chartproperties_json


class UpdateChartProperties:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'chartproperty' in getparams:      # hasattr(getparams, "chartproperty")
            chartdrawprobs = {  'chart_type': getparams['chartproperty']['chart_type'],
                                'chart_width': getparams['chartproperty']['chart_width'],
                                'chart_height': getparams['chartproperty']['chart_height'],
                                'chart_title_font_size': getparams['chartproperty']['chart_title_font_size'],
                                'chart_title_font_color': getparams['chartproperty']['chart_title_font_color'],
                                'chart_subtitle_font_size': getparams['chartproperty']['chart_subtitle_font_size'],
                                'chart_subtitle_font_color': getparams['chartproperty']['chart_subtitle_font_color'],
                                'yaxe1_font_size': getparams['chartproperty']['yaxe1_font_size'],
                                'yaxe2_font_size': getparams['chartproperty']['yaxe2_font_size'],
                                'legend_font_size': getparams['chartproperty']['legend_font_size'],
                                'legend_font_color': getparams['chartproperty']['legend_font_color'],
                                'xaxe_font_size': getparams['chartproperty']['xaxe_font_size'],
                                'xaxe_font_color': getparams['chartproperty']['xaxe_font_color'],
                                'yaxe3_font_size': getparams['chartproperty']['yaxe3_font_size']
                                }


            if self.crud_db.update('chart_drawproperties', chartdrawprobs):
                updatestatus = '{"success":"true", "message":"Chart draw properties updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the chart draw properties!"}'

        else:
            updatestatus = '{"success":false, "message":"No chart properties passed!"}'

        return updatestatus


class GetHelpFile:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        if getparams['lang'] == 'eng':
            lang_dir = 'EN/'
        elif getparams['lang'] == 'fra':
            lang_dir = 'FR/'
        elif getparams['lang'] == 'por':
            lang_dir = 'POR/'
        else:
            lang_dir = 'EN/'

        docs_dir = es_constants.es2globals['docs_dir']
        if not os.path.isdir(es_constants.es2globals['docs_dir']):
            docs_dir = es_constants.es2globals['base_dir'] + '/apps/help/userdocs/'

        docfile = docs_dir + lang_dir + getparams['file']

        filename, file_extension = os.path.splitext(docfile)
        if file_extension == '.pdf':
            contenttype = 'application/pdf'
            content_disposition_type = 'inline;'
        elif file_extension == '.docx' or file_extension == '.doc':
            # contenttype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            contenttype = 'application/force-download'
            content_disposition_type = 'attachment;'
        else:
            contenttype = 'text/html'
            content_disposition_type = 'inline;'

        web.header('Content-Type', contenttype)   # 'text/html'   'application/x-compressed'  'application/force-download' 'application/pdf'
        web.header('Content-transfer-encoding', 'binary')
        # web.header('Content-Disposition', 'attachment; filename=' + getparams['file'])  # force browser to autodownload or show "Save as" dialog.
        web.header('Content-Disposition', content_disposition_type + ' filename= "' + getparams['file'] + '"')  # force browser to show "Save as" dialog.

        f = open(docfile, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf


class GetHelp:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        docs_dir = es_constants.es2globals['docs_dir']
        if not os.path.isdir(es_constants.es2globals['docs_dir']):
            docs_dir = es_constants.es2globals['base_dir'] + '/apps/help/userdocs/'

        if getparams['lang'] == '':
            getparams['lang'] = es_constants.es2globals['default_language'];

        if getparams['lang'] == 'eng':
            lang_dir = 'EN/'
        elif getparams['lang'] == 'fra':
            lang_dir = 'FR/'
        elif getparams['lang'] == 'por':
            lang_dir = 'POR/'
        else:
            lang_dir = 'EN/'

        jsonfile = docs_dir+lang_dir + getparams['type'] + '_data_'+getparams['lang']+'.json'

        # print jsonfile

        if os.path.isfile(jsonfile):
            jsonfile = open(jsonfile, 'r')
            filecontent_json = jsonfile.read()
            jsonfile.close()
        else:
            docs_dir = es_constants.es2globals['base_dir'] + '/apps/help/userdocs/'
            jsonfile = docs_dir+lang_dir + getparams['type'] + '_data_'+getparams['lang']+'.json'
            if os.path.isfile(jsonfile):
                jsonfile = open(jsonfile, 'r')
                filecontent_json = jsonfile.read()
                jsonfile.close()
            else:
                filecontent_json = ''

        return filecontent_json


class GetRequest:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        from apps.productmanagement import requests
        getparams = web.input()
        productcode = None
        version = None
        mapsetcode = None
        subproductcode = None
        if hasattr(getparams, "level"):
            if getparams['level'] == 'product':
                productcode = getparams['productcode']
                version = getparams['version']
            elif getparams['level'] == 'mapset':
                productcode = getparams['productcode']
                version = getparams['version']
                mapsetcode = getparams['mapsetcode']
            elif getparams['level'] == 'dataset':
                productcode = getparams['productcode']
                version = getparams['version']
                mapsetcode = getparams['mapsetcode']
                subproductcode = getparams['subproductcode']

            request = requests.create_request(productcode=productcode, version=version, mapsetcode=mapsetcode, subproductcode=subproductcode)
            request_json = json.dumps(request,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            request_json = '{"success":"true", "request":'+request_json+'}'
        else:
            request_json = '{"success":false, "error":"No parameters passed for request!"}'

        return request_json


class SaveRequest:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        from apps.productmanagement import requests
        getparams = web.input()
        productcode = None
        version = None
        mapsetcode = None
        subproductcode = None
        requestfilename = 'error'
        if hasattr(getparams, "level"):
            if getparams['level'] == 'product':
                productcode = getparams['productcode']
                version = getparams['version']
                requestfilename = getparams['productcode'] + '_' + getparams['version'] + '_all_enabled_mapsets'
            elif getparams['level'] == 'mapset':
                productcode = getparams['productcode']
                version = getparams['version']
                mapsetcode = getparams['mapsetcode']
                requestfilename = getparams['productcode'] + '_' + getparams['version'] + '_' + getparams['mapsetcode'] + '_all_enabled_datasets'
            elif getparams['level'] == 'dataset':
                productcode = getparams['productcode']
                version = getparams['version']
                mapsetcode = getparams['mapsetcode']
                subproductcode = getparams['subproductcode']
                requestfilename = getparams['productcode'] + '_' + getparams['version'] + '_' + getparams['mapsetcode'] + '_' + getparams['subproductcode']

            request = requests.create_request(productcode, version, mapsetcode=mapsetcode, subproductcode=subproductcode)
            request_json = json.dumps(request,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M')

            requestfilename = requestfilename + '_' + st + '.req'
            with open(es_constants.es2globals['requests_dir']+requestfilename, 'w+') as f:
                f.write(request_json)
            f.close()

            web.header('Content-Type', 'text/html')   # 'application/x-compressed'  'application/force-download'
            web.header('Content-transfer-encoding', 'binary')
            web.header('Content-Disposition', 'attachment; filename=' + requestfilename)  # force browser to show "Save as" dialog.
            f = open(es_constants.es2globals['requests_dir']+requestfilename, 'rb')
            while 1:
                buf = f.read(1024 * 8)
                if not buf:
                    break
                yield buf


class GetCategories:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        categories_dict_all = []
        categories = querydb.get_categories()

        if hasattr(categories, "__len__") and categories.__len__() > 0:
            for row in categories:
                row_dict = functions.row2dict(row)
                categories_dict = {'category_id': row_dict['category_id'],
                                  'descriptive_name': row_dict['descriptive_name']}

                categories_dict_all.append(categories_dict)

            categories_json = json.dumps(categories_dict_all,
                                         ensure_ascii=False,
                                         encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            categories_json = '{"success":"true", "total":'\
                                   + str(categories.__len__())\
                                   + ',"categories":'+categories_json+'}'

        else:
            categories_json = '{"success":false, "error":"No Categories defined!"}'

        return categories_json


class GetFrequencies:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        frequencies_dict_all = []
        frequencies = querydb.get_frequencies()

        if hasattr(frequencies, "__len__") and frequencies.__len__() > 0:
            for row in frequencies:
                row_dict = functions.row2dict(row)
                # internetsource = {'category_id': row_dict['category_id'],
                #                   'descriptive_name': row_dict['descriptive_name']}
                frequencies_dict_all.append(row_dict)

            frequencies_json = json.dumps(frequencies_dict_all,
                                         ensure_ascii=False,
                                         encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            frequencies_json = '{"success":"true", "total":'\
                                   + str(frequencies.__len__())\
                                   + ',"frequencies":'+frequencies_json+'}'

        else:
            frequencies_json = '{"success":false, "error":"No Frequencies defined!"}'

        return frequencies_json


class GetDateFormats:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        dateformats_dict_all = []
        dateformats = querydb.get_dateformats()

        if hasattr(dateformats, "__len__") and dateformats.__len__() > 0:
            for row in dateformats:
                row_dict = functions.row2dict(row)

                dateformats_dict_all.append(row_dict)

            dateformats_json = json.dumps(dateformats_dict_all,
                                         ensure_ascii=False,
                                         encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            dateformats_json = '{"success":"true", "total":'\
                                   + str(dateformats.__len__())\
                                   + ',"dateformats":'+dateformats_json+'}'

        else:
            dateformats_json = '{"success":false, "error":"No Date Formats defined!"}'

        return dateformats_json


class GetDataTypes:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        datatypes_dict_all = []
        datatypes = querydb.get_datatypes()

        if hasattr(datatypes, "__len__") and datatypes.__len__() > 0:
            for row in datatypes:
                row_dict = functions.row2dict(row)

                datatypes_dict_all.append(row_dict)

            datatypes_json = json.dumps(datatypes_dict_all,
                                         ensure_ascii=False,
                                         encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            datatypes_json = '{"success":"true", "total":'\
                                   + str(datatypes.__len__())\
                                   + ',"datatypes":'+datatypes_json+'}'

        else:
            datatypes_json = '{"success":false, "error":"No Data Types defined!"}'

        return datatypes_json


class AssignInternetSource:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        # getparams = json.loads(web.data())
        getparams = web.input()
        if getparams['version'] == '':
            version = 'undefined'
        else:
            version = getparams['version']

        productinfo = {
            'productcode': getparams['productcode'],
            'subproductcode': getparams['subproductcode'],
            'version': version,
            'data_source_id': getparams['data_source_id'],
            'defined_by': 'USER',
            'type': 'INTERNET'
        }

        # datasourceinserted = querydb.insert_product_acquisition_datasource(productinfo, echo=False)

        if self.crud_db.create('product_acquisition_data_source', productinfo):
            insertstatus = '{"success":"true", "message":"Internet source assigned!"}'
        else:
            insertstatus = '{"success":false, "message":"An error occured while assigning the internet source!"}'

        return insertstatus


class AssignEumetcastSource:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        # getparams = json.loads(web.data())
        getparams = web.input()

        if getparams['version'] == '':
            version = 'undefined'
        else:
            version = getparams['version']

        productinfo = {
            'productcode': getparams['productcode'],
            'subproductcode': getparams['subproductcode'],
            'version': version,
            'data_source_id': getparams['data_source_id'],
            'defined_by': 'USER',
            'type': 'EUMETCAST'
        }

        if self.crud_db.create('product_acquisition_data_source', productinfo):
            insertstatus = '{"success":"true", "message":"Internet source assigned!"}'
        else:
            insertstatus = '{"success":false, "message":"An error occured while assigning the internet source!"}'

        return insertstatus


class UnassignProductDataSource:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        # getparams = json.loads(web.data())
        getparams = web.input()

        productinfo = {
            'productcode': getparams['productcode'],
            'subproductcode': getparams['subproductcode'],
            'version': getparams['version'],
            'data_source_id': getparams['data_source_id']
        }

        if self.crud_db.delete('product_acquisition_data_source', **productinfo):
            unassignstatus = '{"success":"true", "message":"Data source unassigned!"}'
        else:
            unassignstatus = '{"success":false, "message":"An error occured while assigning the internet source!"}'

        return unassignstatus


class GetEumetcastSources:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        eumetcastsources_dict_all = []
        eumetcastsources = querydb.get_eumetcastsources()

        if hasattr(eumetcastsources, "__len__") and eumetcastsources.__len__() > 0:
            for row in eumetcastsources:
                row_dict = functions.row2dict(row)
                eumetcastsource = {'eumetcast_id': row_dict['eumetcast_id'],
                                   'collection_name': row_dict['collection_name'],
                                   'filter_expression_jrc': row_dict['filter_expression_jrc'],
                                   'description': row_dict['description'],
                                   'typical_file_name': row_dict['typical_file_name'],
                                   'keywords_theme': row_dict['keywords_theme'],
                                   'keywords_societal_benefit_area': row_dict['keywords_societal_benefit_area'],
                                   'datasource_descr_id': row_dict['datasource_descr_id'],
                                   'format_type': row_dict['format_type'],
                                   'file_extension': row_dict['file_extension'],
                                   'delimiter': row_dict['delimiter'],
                                   'date_format': row_dict['date_format'],
                                   'date_position': row_dict['date_position'],
                                   'product_identifier': row_dict['product_identifier'],
                                   'prod_id_position': row_dict['prod_id_position'],
                                   'prod_id_length': row_dict['prod_id_length'],
                                   'area_type': row_dict['area_type'],
                                   'area_position': row_dict['area_position'],
                                   'area_length': row_dict['area_length'],
                                   'preproc_type': row_dict['preproc_type'],
                                   'product_release': row_dict['product_release'],
                                   'release_position': row_dict['release_position'],
                                   'release_length': row_dict['release_length'],
                                   'native_mapset': row_dict['native_mapset']}

                eumetcastsources_dict_all.append(eumetcastsource)

            eumetcastsources_json = json.dumps(eumetcastsources_dict_all,
                                              ensure_ascii=False,
                                              encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            eumetcastsources_json = '{"success":"true", "total":'\
                                   + str(eumetcastsources.__len__())\
                                   + ',"eumetcastsources":'+eumetcastsources_json+'}'

        else:
            eumetcastsources_json = '{"success":false, "error":"No Internet Sources defined!"}'

        return eumetcastsources_json


class UpdateEumetcastSource:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'eumetcastsources' in getparams:

            prod_id_position = None
            if getparams['eumetcastsources']['prod_id_position'].isdigit():
                prod_id_position = int(getparams['eumetcastsources']['prod_id_position'])

            prod_id_length = None
            if getparams['eumetcastsources']['prod_id_length'].isdigit():
                prod_id_length = int(getparams['eumetcastsources']['prod_id_length'])

            area_length = None
            if getparams['eumetcastsources']['area_length'].isdigit():
                area_length = int(getparams['eumetcastsources']['area_length'])

            release_length = None
            if getparams['eumetcastsources']['release_length'].isdigit():
                release_length = int(getparams['eumetcastsources']['release_length'])

            eumetcastsourceinfo = {'eumetcast_id': getparams['eumetcastsources']['eumetcast_id'],
                                   'filter_expression_jrc': getparams['eumetcastsources']['filter_expression_jrc']}

            datasourcedescrinfo = {'datasource_descr_id': getparams['eumetcastsources']['eumetcast_id'],
                                  'format_type': getparams['eumetcastsources']['format_type'],
                                  'file_extension': getparams['eumetcastsources']['file_extension'],
                                  'delimiter': getparams['eumetcastsources']['delimiter'],
                                  'date_format': getparams['eumetcastsources']['date_format'],
                                  'date_position': getparams['eumetcastsources']['date_position'],
                                  'product_identifier': getparams['eumetcastsources']['product_identifier'],
                                  'prod_id_position': prod_id_position,
                                  'prod_id_length': prod_id_length,
                                  'area_type': getparams['eumetcastsources']['area_type'],
                                  'area_position': getparams['eumetcastsources']['area_position'],
                                  'area_length': area_length,
                                  'preproc_type': getparams['eumetcastsources']['preproc_type'],
                                  'product_release': getparams['eumetcastsources']['product_release'],
                                  'release_position': getparams['eumetcastsources']['release_position'],
                                  'release_length': release_length,
                                  'native_mapset': getparams['eumetcastsources']['native_mapset']}

            if self.crud_db.update('eumetcast_source', eumetcastsourceinfo):
                if self.crud_db.update('datasource_description', datasourcedescrinfo):
                    updatestatus = '{"success":"true", "message":"Eumetcast data source and description updated!"}'
                else:
                    updatestatus = '{"success":"true", "message":"Eumetcast data source updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the Eumetcast data source!"}'

        else:
            updatestatus = '{"success":false, "message":"No Eumetcast data source passed!"}'

        return updatestatus


class GetInternetSources:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        internetsources_dict_all = []
        internetsources = querydb.get_internetsources()

        if hasattr(internetsources, "__len__") and internetsources.__len__() > 0:
            for row in internetsources:
                row_dict = functions.row2dict(row)
                internetsource = {'internet_id': row_dict['internet_id'],
                                  'defined_by': row_dict['defined_by'],
                                  'descriptive_name': row_dict['descriptive_name'],
                                  'description': row_dict['description'],
                                  'modified_by': row_dict['modified_by'],
                                  'update_datetime': row_dict['update_datetime'],
                                  'url': row_dict['url'],
                                  'user_name': row_dict['user_name'],
                                  'password': row_dict['password'],
                                  'type': row_dict['type'],
                                  'include_files_expression': row_dict['include_files_expression'],
                                  'files_filter_expression': row_dict['files_filter_expression'],
                                  'status': row_dict['status'],
                                  'pull_frequency': row_dict['pull_frequency'],
                                  'frequency_id': row_dict['frequency_id'],
                                  'start_date': row_dict['start_date'],
                                  'end_date': row_dict['end_date'],
                                  'datasource_descr_id': row_dict['datasource_descr_id'],
                                  'format_type': row_dict['format_type'],
                                  'file_extension': row_dict['file_extension'],
                                  'delimiter': row_dict['delimiter'],
                                  'date_format': row_dict['date_format'],
                                  'date_position': row_dict['date_position'],
                                  'product_identifier': row_dict['product_identifier'],
                                  'prod_id_position': row_dict['prod_id_position'],
                                  'prod_id_length': row_dict['prod_id_length'],
                                  'area_type': row_dict['area_type'],
                                  'area_position': row_dict['area_position'],
                                  'area_length': row_dict['area_length'],
                                  'preproc_type': row_dict['preproc_type'],
                                  'product_release': row_dict['product_release'],
                                  'release_position': row_dict['release_position'],
                                  'release_length': row_dict['release_length'],
                                  'native_mapset': row_dict['native_mapset']}

                internetsources_dict_all.append(internetsource)

            internetsources_json = json.dumps(internetsources_dict_all,
                                              ensure_ascii=False,
                                              encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            internetsources_json = '{"success":"true", "total":'\
                                   + str(internetsources.__len__())\
                                   + ',"internetsources":'+internetsources_json+'}'

        else:
            internetsources_json = '{"success":false, "error":"No Internet Sources defined!"}'

        return internetsources_json


class UpdateInternetSource:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'internetsources' in getparams:

            startdate = None
            if isinstance(getparams['internetsources']['start_date'],int):
                startdate = getparams['internetsources']['start_date']
            elif isinstance(getparams['internetsources']['start_date'],str) and getparams['internetsources']['start_date'].isdigit():
                startdate = int(getparams['internetsources']['start_date'])

            enddate = None
            if isinstance(getparams['internetsources']['end_date'],int):
                enddate = getparams['internetsources']['end_date']
            elif isinstance(getparams['internetsources']['end_date'],str) and getparams['internetsources']['end_date'].isdigit():
                enddate = int(getparams['internetsources']['end_date'])

            prod_id_position = None
            if getparams['internetsources']['prod_id_position'].isdigit():
                prod_id_position = int(getparams['internetsources']['prod_id_position'])

            prod_id_length = None
            if getparams['internetsources']['prod_id_length'].isdigit():
                prod_id_length = int(getparams['internetsources']['prod_id_length'])

            area_length = None
            if getparams['internetsources']['area_length'].isdigit():
                area_length = int(getparams['internetsources']['area_length'])

            release_length = None
            if getparams['internetsources']['release_length'].isdigit():
                release_length = int(getparams['internetsources']['release_length'])

            internetsourceinfo = {'internet_id': getparams['internetsources']['internet_id'],
                                  'defined_by': getparams['internetsources']['defined_by'],
                                  'descriptive_name': getparams['internetsources']['descriptive_name'],
                                  'description': getparams['internetsources']['description'],
                                  'modified_by': getparams['internetsources']['modified_by'],
                                  # 'update_datetime': getparams['internetsources']['update_datetime'],
                                  'url': getparams['internetsources']['url'],
                                  'user_name': getparams['internetsources']['user_name'],
                                  'password': getparams['internetsources']['password'],
                                  'type': getparams['internetsources']['type'],
                                  'include_files_expression': getparams['internetsources']['include_files_expression'],
                                  'files_filter_expression': getparams['internetsources']['files_filter_expression'],
                                  'status': getparams['internetsources']['status'],
                                  'pull_frequency': getparams['internetsources']['pull_frequency'],
                                  'frequency_id': getparams['internetsources']['frequency_id'],
                                  'start_date': startdate,
                                  'end_date': enddate,
                                  'datasource_descr_id': getparams['internetsources']['internet_id']}

            datasourcedescrinfo = {'datasource_descr_id': getparams['internetsources']['internet_id'],
                                  'format_type': getparams['internetsources']['format_type'],
                                  'file_extension': getparams['internetsources']['file_extension'],
                                  'delimiter': getparams['internetsources']['delimiter'],
                                  'date_format': getparams['internetsources']['date_format'],
                                  'date_position': getparams['internetsources']['date_position'],
                                  'product_identifier': getparams['internetsources']['product_identifier'],
                                  'prod_id_position': prod_id_position,
                                  'prod_id_length': prod_id_length,
                                  'area_type': getparams['internetsources']['area_type'],
                                  'area_position': getparams['internetsources']['area_position'],
                                  'area_length': area_length,
                                  'preproc_type': getparams['internetsources']['preproc_type'],
                                  'product_release': getparams['internetsources']['product_release'],
                                  'release_position': getparams['internetsources']['release_position'],
                                  'release_length': release_length,
                                  'native_mapset': getparams['internetsources']['native_mapset']}

            if self.crud_db.update('internet_source', internetsourceinfo):
                if self.crud_db.update('datasource_description', datasourcedescrinfo):
                    updatestatus = '{"success":"true", "message":"Internet data source and description updated!"}'
                else:
                    updatestatus = '{"success":"true", "message":"Internet data source updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the internet data source!"}'

        else:
            updatestatus = '{"success":false, "message":"No internet data source passed!"}'

        return updatestatus


class GetSystemStatus:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # pickle_filename = functions.system_status_filename()
        # info = functions.load_obj_from_pickle(pickle_filename)
        info = es2system.get_status_local_machine()
        status_local_machine = {'get_eumetcast_status': info['get_eumetcast_status'],
                                'get_internet_status': info['get_internet_status'],
                                'ingestion_status': info['ingestion_status'],
                                'processing_status': info['processing_status'],
                                'system_status': info['system_status'],
                                'system_execution_time': info['system_execution_time'],
                                'postgresql_status': info['postgresql_status'],
                                'internet_connection_status': info['internet_connection_status'],
                                'active_version': info['active_version'],
                                'mode': info['mode'],
                                'disk_status': info['disk_status']}

        return status_local_machine


class GetDashboard:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # getparams = web.input()

        PC1_connection = False
        PC23_connection = False

        PC2_mode = ''   # 'nominal' 'recovery'
        PC2_disk_status = True
        PC2_version = ''
        PC2_DBAutoSync = None
        PC2_DataAutoSync = None
        PC2_postgresql_status = None
        PC2_internet_status = None
        PC2_service_eumetcast = None
        PC2_service_internet = None
        PC2_service_ingest = None
        PC2_service_processing = None
        PC2_service_system = None

        PC3_mode = ''   # 'nominal' 'recovery'
        PC3_version = ''
        PC3_disk_status = True
        PC3_DBAutoSync = None
        PC3_DataAutoSync = None
        PC3_postgresql_status = None
        PC3_internet_status = None
        PC3_service_eumetcast = None
        PC3_service_internet = None
        PC3_service_ingest = None
        PC3_service_processing = None
        PC3_service_system = None

        systemsettings = functions.getSystemSettings()
        status_services = functions.getStatusAllServices()

        # T o D o: Use port 80?
        # IP_port = ':22'
        # PC1_connection = functions.check_connection(systemsettings['ip_pc1'] + IP_port)
        PC1_connection = functions.check_connection('mesa-pc1')

        status_PC1 = []
        if PC1_connection:
            status_PC1 = functions.get_status_PC1()

        if len(status_PC1) == 0:
            PC1_dvb_status = None
            PC1_tellicast_status = None
            PC1_fts_status = None
        else:
            dvb_status = status_PC1['services']['acquisition']['dvb']['status']
            fts_status = status_PC1['services']['acquisition']['fts']['status']
            tellicast_status = status_PC1['services']['acquisition']['tellicast']['status']

            if dvb_status == 'unknown':
                PC1_dvb_status = None
            elif dvb_status == 'not running' or dvb_status == 'unlock':
                PC1_dvb_status = False
            else:
                PC1_dvb_status = True

            if tellicast_status == 'unknown':
                PC1_tellicast_status = None
            elif tellicast_status == 'running':
                PC1_tellicast_status = True
            else:
                PC1_tellicast_status = False

            if fts_status == 'unknown':
                PC1_fts_status = None
            elif fts_status == 'running':
                PC1_fts_status = True
            else:
                PC1_fts_status = False


        if systemsettings['type_installation'].lower() == 'full':
            if systemsettings['role'].lower() == 'pc1':
                PC1_mode = systemsettings['mode'].lower()

            elif systemsettings['role'].lower() == 'pc2':
                PC2_mode = systemsettings['mode'].lower()
                PC2_version = systemsettings['active_version']
                PC2_DBAutoSync = systemsettings['db_sync']
                PC2_DataAutoSync = systemsettings['data_sync']
                PC2_postgresql_status = functions.getStatusPostgreSQL()
                PC2_internet_status = functions.internet_on()
                PC2_service_eumetcast = status_services['eumetcast']
                PC2_service_internet = status_services['internet']
                PC2_service_ingest = status_services['ingest']
                PC2_service_processing = status_services['process']
                PC2_service_system = status_services['system']

                # if role is PC2 and type_installation is Full and there is a connection to PC3, then on PC3 get the file
                # /srv/www/eStation2/src/apps/es2system/system_status.pkl and read its content:
                #       role, version, mode, postgresql status, internet status (status services if in degradation mode?)

                # Check connection to PC3
                # PC23_connection = functions.check_connection(systemsettings['ip_pc3'] + IP_port)
                PC23_connection = functions.check_connection('mesa-pc3')
                # print "PC23_connection: " + str(PC23_connection)

                if PC23_connection:
                    # status_PC3 = functions.get_remote_system_status(systemsettings['ip_pc3'])
                    status_PC3 = functions.get_remote_system_status('mesa-pc3')
                    if 'mode' in status_PC3:
                        PC3_mode = status_PC3['mode']
                        PC3_disk_status = status_PC3['disk_status']
                        PC3_version = status_PC3['active_version']
                        PC3_DBAutoSync = False  # status_PC3['db_sync']
                        PC3_DataAutoSync = False  # status_PC3['data_sync']
                        PC3_postgresql_status = status_PC3['postgresql_status']
                        PC3_internet_status = status_PC3['internet_connection_status']
                        PC3_service_eumetcast = status_PC3['get_eumetcast_status']
                        PC3_service_internet = status_PC3['get_internet_status']
                        PC3_service_ingest = status_PC3['ingestion_status']
                        PC3_service_processing = status_PC3['processing_status']
                        PC3_service_system = status_PC3['system_status']
                        PC3_system_execution_time = status_PC3['system_execution_time']
                    else:
                        PC3_Webserver_Status = False

            elif systemsettings['role'].lower() == 'pc3':
                # ToDo: check disk status!
                # PC3_disk_status = checkDiskStatus()
                PC3_mode = systemsettings['mode'].lower()
                PC3_version = systemsettings['active_version']
                PC3_DBAutoSync = systemsettings['db_sync']
                PC3_DataAutoSync = systemsettings['data_sync']
                PC3_postgresql_status = functions.getStatusPostgreSQL()
                PC3_internet_status = functions.internet_on()
                PC3_service_eumetcast = status_services['eumetcast']
                PC3_service_internet = status_services['internet']
                PC3_service_ingest = status_services['ingest']
                PC3_service_processing = status_services['process']
                PC3_service_system = status_services['system']

                # if role is PC3 and type_installation is Full and there is a connection to PC2, then on PC2 get the file
                # /srv/www/eStation2/src/apps/es2system/system_status.pkl and read its content:
                #       role, version, mode, postgresql status, internet status, status services if in nominal mode
                # /sbin/service postgresql status    or     /etc/init.d/postgresql status

                # Check connection to PC2
                # PC23_connection = functions.check_connection(systemsettings['ip_pc2'] + IP_port)
                PC23_connection = functions.check_connection('mesa-pc2')
                if PC23_connection:
                    # status_PC2 = functions.get_remote_system_status(systemsettings['ip_pc2'])
                    status_PC2 = functions.get_remote_system_status('mesa-pc2')
                    if 'mode' in status_PC2:
                        PC2_mode = status_PC2['mode']
                        PC2_disk_status = status_PC2['disk_status']
                        PC2_version = status_PC2['active_version']
                        PC2_DBAutoSync = False  # status_PC2['db_sync']
                        PC2_DataAutoSync = False  # status_PC2['data_sync']
                        PC2_postgresql_status = status_PC2['postgresql_status']
                        PC2_internet_status = status_PC2['internet_connection_status']
                        PC2_service_eumetcast = status_PC2['get_eumetcast_status']
                        PC2_service_internet = status_PC2['get_internet_status']
                        PC2_service_ingest = status_PC2['ingestion_status']
                        PC2_service_processing = status_PC2['processing_status']
                        PC2_service_system = status_PC2['system_status']
                        PC2_system_execution_time = status_PC2['system_execution_time']
                    else:
                        PC2_Webserver_Status = False


        if systemsettings['type_installation'].lower() in ['singlepc', 'server']:
            if systemsettings['role'].lower() == 'pc1':
                PC1_mode = systemsettings['mode'].lower()

            elif systemsettings['role'].lower() == 'pc2':
                PC2_mode = systemsettings['mode'].lower()
                PC2_version = systemsettings['active_version']
                PC2_DBAutoSync = systemsettings['db_sync']
                PC2_DataAutoSync = systemsettings['data_sync']
                PC2_postgresql_status = functions.getStatusPostgreSQL()
                PC2_internet_status = functions.internet_on()
                # PC2_internet_status = functions.is_connected()
                PC2_service_eumetcast = status_services['eumetcast']
                PC2_service_internet = status_services['internet']
                PC2_service_ingest = status_services['ingest']
                PC2_service_processing = status_services['process']
                PC2_service_system = status_services['system']


        if PC2_DBAutoSync in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            PC2_DBAutoSync = True
        else:
            PC2_DBAutoSync = False

        if PC2_DataAutoSync in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            PC2_DataAutoSync = True
        else:
            PC2_DataAutoSync = False

        if PC3_DBAutoSync in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            PC3_DBAutoSync = True
        else:
            PC3_DBAutoSync = False

        if PC3_DataAutoSync in ['True', 'true', '1', 't', 'y', 'Y', 'yes', 'Yes']:
            PC3_DataAutoSync = True
        else:
            PC3_DataAutoSync = False

        dashboard_dict = {'type_installation': systemsettings['type_installation'].lower(),
                          'activePC': systemsettings['role'].lower(),
                          'PC1_connection': PC1_connection,
                          'PC1_dvb_status': PC1_dvb_status,
                          'PC1_tellicast_status': PC1_tellicast_status,
                          'PC1_fts_status': PC1_fts_status,

                          'PC23_connection': PC23_connection,

                          'PC2_service_eumetcast': PC2_service_eumetcast,
                          'PC2_service_internet': PC2_service_internet,
                          'PC2_service_ingest': PC2_service_ingest,
                          'PC2_service_processing': PC2_service_processing,
                          'PC2_service_system': PC2_service_system,
                          'PC2_version': PC2_version,
                          'PC2_DBAutoSync': PC2_DBAutoSync,
                          'PC2_DataAutoSync': PC2_DataAutoSync,
                          'PC2_mode': PC2_mode,
                          'PC2_postgresql_status': PC2_postgresql_status,
                          'PC2_internet_status': PC2_internet_status,
                          'PC2_disk_status': PC2_disk_status,

                          'PC3_service_eumetcast': PC3_service_eumetcast,
                          'PC3_service_internet': PC3_service_internet,
                          'PC3_service_ingest': PC3_service_ingest,
                          'PC3_service_processing': PC3_service_processing,
                          'PC3_service_system': PC3_service_system,
                          'PC3_version': PC3_version,
                          'PC3_DBAutoSync': PC3_DBAutoSync,
                          'PC3_DataAutoSync': PC3_DataAutoSync,
                          'PC3_mode': PC3_mode,
                          'PC3_postgresql_status': PC3_postgresql_status,
                          'PC3_internet_status': PC3_internet_status,
                          'PC3_disk_status': PC3_disk_status}

        # dashboard_dict = {
        #     "PC1_connection": True,
        #     "PC1_dvb_status": True,
        #     "PC1_fts_status": True,
        #     "PC1_tellicast_status": True,
        #     "PC23_connection": True,
        #     "PC2_DBAutoSync": True,
        #     "PC2_DataAutoSync": True,
        #     "PC2_disk_status": True,
        #     "PC2_internet_status": True,
        #     "PC2_mode": "nominal",
        #     "PC2_postgresql_status": True,
        #     "PC2_service_eumetcast": "true",
        #     "PC2_service_ingest": "true",
        #     "PC2_service_internet": "true",
        #     "PC2_service_processing": "true",
        #     "PC2_service_system": "true",
        #     "PC2_version": "2.0.4",
        #     "PC3_DBAutoSync": False,
        #     "PC3_DataAutoSync": False,
        #     "PC3_disk_status": "true",
        #     "PC3_internet_status": "true",
        #     "PC3_mode": "nominal",
        #     "PC3_postgresql_status": "true",
        #     "PC3_service_eumetcast": "false",
        #     "PC3_service_ingest": "false",
        #     "PC3_service_internet": "false",
        #     "PC3_service_processing": "false",
        #     "PC3_service_system": "true",
        #     "PC3_version": "2.0.4",
        #     "activePC": "pc3",
        #     "type_installation": "full"
        # }

        # print dashboard_dict
        dashboard_json = json.dumps(dashboard_dict,
                                    ensure_ascii=False,
                                    encoding='utf-8',
                                    sort_keys=True,
                                    indent=4,
                                    separators=(', ', ': '))

        dashboard_json = '{"success":"true", "dashboard":'+dashboard_json + '}'

        return dashboard_json


class SetDataAutoSync:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        getparams = web.input()
        if hasattr(getparams, "dataautosync"):

            functions.setSystemSetting('data_sync', getparams['dataautosync'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            from lib.python import reloadmodules
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"Data Auto Sync changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class SetDBAutoSync:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        getparams = web.input()
        if hasattr(getparams, "dbautosync"):

            functions.setSystemSetting('db_sync', getparams['dbautosync'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            from lib.python import reloadmodules
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"DB Auto Sync changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class GetI18n:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "lang"):
            lang = getparams['lang']
        else:
            lang = es_constants.es2globals['default_language']

        translations_dict_all = []
        i18n = querydb.get_i18n(lang=lang)

        if hasattr(i18n, "__len__") and i18n.__len__() > 0:
            for label, langtranslation in i18n:
                translation_dict = {'label': label,
                                    'langtranslation': langtranslation}  # .encode('utf-8')
                translations_dict_all.append(translation_dict)

            translations_json = json.dumps(translations_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            translations_json = '{"success":"true", "total":'\
                                + str(i18n.__len__())\
                                + ',"translations":'+translations_json+'}'

        else:
            translations_json = '{"success":false, "error":"No translations defined!"}'

        return translations_json


class AddIngestMapset:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "selectedmapset"):

            mapsetingest = {'productcode': getparams['productcode'],
                            'subproductcode': getparams['subproductcode'],
                            'version': getparams['version'],
                            'mapsetcode': getparams['selectedmapset']}

            if self.crud_db.read('ingestion', **mapsetingest):

                mapsetingest = {'productcode': getparams['productcode'],
                                'subproductcode': getparams['subproductcode'],
                                'version': getparams['version'],
                                'mapsetcode': getparams['selectedmapset'],
                                'enabled': True
                                }

                if self.crud_db.update('ingestion', mapsetingest):
                    insertstatus = '{"success":"true", "message":"Ingest mapset enabled!"}'
                else:
                    insertstatus = '{"success":false, "message":"An error occured while enabling the mapset for ingest!"}'
            else:
                mapsetingest = {'productcode': getparams['productcode'],
                                'subproductcode': getparams['subproductcode'],
                                'version': getparams['version'],
                                'mapsetcode': getparams['selectedmapset'],
                                'defined_by': 'USER',
                                'activated': True,
                                'wait_for_all_files': False,
                                'input_to_process_re': '',
                                'enabled': True
                                }

                if self.crud_db.create('ingestion', mapsetingest):
                    insertstatus = '{"success":"true", "message":"Ingest mapset inserted!"}'
                else:
                    insertstatus = '{"success":false, "message":"An error occured while inserting the mapset for ingest!"}'
        else:
            insertstatus = '{"success":false, "error":"No mapset given!"}'

        return insertstatus


class DisableIngestMapset:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "mapsetcode"):

            mapsetingest = {'productcode': getparams['productcode'],
                            'subproductcode': getparams['subproductcode'],
                            'version': getparams['version'],
                            'mapsetcode': getparams['mapsetcode'],
                            'enabled': False
                            }

            if self.crud_db.update('ingestion', mapsetingest):
                deletestatus = '{"success":"true", "message":"Ingest mapset deleted!"}'
            else:
                deletestatus = '{"success":false, "message":"An error occured while deleting the mapset for ingest!"}'
        else:
            deletestatus = '{"success":false, "error":"No mapset given!"}'

        return deletestatus


class GetMapsets:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        mapsets_dict_all = []
        mapsets = querydb.get_mapsets_for_ingest(productcode=getparams['productcode'], version=getparams['version'], subproductcode=getparams['subproductcode'])

        if hasattr(mapsets, "__len__") and mapsets.__len__() > 0:
            for mapset in mapsets:
                mapset_dict = functions.row2dict(mapset)
                mapsets_dict_all.append(mapset_dict)

            mapsets_json = json.dumps(mapsets_dict_all,
                                   ensure_ascii=False,
                                   encoding='utf-8',
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            mapsets_json = '{"success":"true", "total":'\
                                  + str(mapsets.__len__())\
                                  + ',"mapsets":'+mapsets_json+'}'

        else:
            mapsets_json = '{"success":false, "error":"No Mapsets defined!"}'

        return mapsets_json


class GetLanguages:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        languages_dict_all = []
        languages = querydb.get_languages()

        if hasattr(languages, "__len__") and languages.__len__() > 0:
            usersettings = functions.getUserSettings()

            for lang in languages:
                # Sometimes es_constants.es2globals['default_language'] does not change well so take
                # usersettings['default_language'] which is safer.
                if usersettings['default_language'] == lang.langcode:
                    selected = True
                else:
                    selected = False
                lang_dict = {'langcode': lang.langcode,
                             'langdescription': lang.langdescription,
                             'selected': selected
                             }  # .encode('utf-8')
                # lang_dict = functions.row2dict(lang)
                languages_dict_all.append(lang_dict)

            lang_json = json.dumps(languages_dict_all,
                                   ensure_ascii=False,
                                   encoding='utf-8',
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            languages_json = '{"success":"true", "total":'\
                                  + str(languages.__len__())\
                                  + ',"languages":'+lang_json+'}'

        else:
            languages_json = '{"success":false, "error":"No languages defined!"}'

        return languages_json


class GetTimeseries:
    def __init__(self):
        self.lang = "eng"


    def POST(self):
        getparams = web.input()
        if getparams.charttype == 'ranking':
            return self.rankTimeseries()
        else:
            return self.classicTimeseries()


    def rankTimeseries(self):
        from apps.analysis.getTimeseries import getTimeseries

        getparams = web.input()
        yearts = getparams.yearTS
        wkt = getparams.WKT
        requestedtimeseries = json.loads(getparams.selectedTimeseries)
        tsFromPeriod = getparams.tsFromPeriod
        tsToPeriod = getparams.tsToPeriod
        yearsToCompare = json.loads(getparams.yearsToCompare)
        tsFromSeason = getparams.tsFromSeason
        tsToSeason = getparams.tsToSeason
        showYearInTicks = True
        data_available = False

        timeseries = []
        for timeserie in requestedtimeseries:
            productcode = timeserie['productcode']
            subproductcode = timeserie['subproductcode']
            version = timeserie['version']
            mapsetcode = timeserie['mapsetcode']
            date_format = timeserie['date_format']

            product = {"productcode": productcode,
                       "subproductcode": subproductcode,
                       "version": version}

            # Set defaults in case no entry exists in the DB
            aggregate = { 'aggregation_type': 'mean',
                          'aggregation_min': None,
                          'aggregation_max': None }
            timeseries_drawproperties = querydb.get_product_timeseries_drawproperties(product)
            for ts_drawprops in timeseries_drawproperties:
                aggregate = { 'aggregation_type': ts_drawprops.aggregation_type,
                              'aggregation_min': ts_drawprops.aggregation_min,
                              'aggregation_max': ts_drawprops.aggregation_max}
                tscolor = ts_drawprops.color

            if date_format == 'MMDD' and len(yearsToCompare) > 1:
                year = yearsToCompare[0]
                showYearInTicks = False
                from_date = datetime.date(year, 01, 01)
                to_date = datetime.date(year, 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)
                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(list_values) > 1:
                    data_available = True

                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'column',
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True
                      }
                for ts_drawprops in timeseries_drawproperties:
                    ts = {'name': ts_drawprops.tsname_in_legend,
                          'type': 'column',     # ts_drawprops.charttype,
                          'color': ts_drawprops.color,
                          'yAxis': ts_drawprops.yaxes_id,
                          'data': data,
                          'visible': True
                          }
                timeseries.append(ts)

            elif len(yearsToCompare) > 1:
                data = []
                print yearsToCompare
                for year in yearsToCompare:
                    showYearInTicks = False
                    print year
                    from_date = datetime.date(int(year), 01, 01)
                    to_date = datetime.date(int(year), 12, 31)

                    if tsFromSeason != '' and tsToSeason != '':
                        from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                        to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                        if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                            to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                    list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

                    if len(list_values) > 1:
                        data_available = True

                    cumulatedValue = 0
                    for val in list_values:
                        cumulatedValue += val['meanvalue']

                    yearData = {
                        'name': str(year),
                        'color': tscolor,   # '#0065a2',
                        'y': cumulatedValue
                    }
                    data.append(yearData)

                data = sorted(data, key=lambda k:k['y'], reverse=False)
                data[0]['color'] = '#ff0000'
                # from operator import itemgetter, attrgetter
                # data = sorted(data, key=attrgetter('y'), reverse=False)
                # data = sorted(data, key=itemgetter(2), reverse=False)


                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'column',
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True
                      }
                for ts_drawprops in timeseries_drawproperties:
                    ts = {'name': ts_drawprops.tsname_in_legend,
                          'type': 'column', # ts_drawprops.charttype,
                          'color': ts_drawprops.color,
                          'yAxis': ts_drawprops.yaxes_id,
                          'data': data,
                          'visible': True
                          }
                timeseries.append(ts)


        yaxes = []
        count = 0
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries)
        axes = len(timeseries_yaxes)
        for yaxe in timeseries_yaxes:
            count += 1
            opposite = "false"
            # if axes >= 2 and count % 2 == 0:   # and yaxe.oposite == "f"
            #     opposite = "false"
            # if axes >= 2 and count % 2 != 0:   # and yaxe.oposite == "t"
            #     opposite = "true"
            if axes >= 2:
                if yaxe.oposite:
                    opposite = "true"
            if axes == 1:
                opposite = "false"

            min = ''    # yaxe.min
            max = ''    # yaxe.max

            yaxe = {'id': yaxe.yaxes_id, 'title': yaxe.title, 'title_color': yaxe.title_color, 'unit': yaxe.unit, 'opposite': opposite,
                    'min': min, 'max': max, 'aggregation_type': yaxe.aggregation_type, 'aggregation_min': yaxe.aggregation_min, 'aggregation_max': yaxe.aggregation_max}
            yaxes.append(yaxe)


        ts_json = {"data_available": data_available,
                   "showYearInTicks": showYearInTicks,
                   "showYearInToolTip": "true",
                   "yaxes": yaxes,
                   "timeseries": timeseries}

        ts_json = json.dumps(ts_json,
                             ensure_ascii=False,
                             sort_keys=True,
                             separators=(', ', ': '))
        return ts_json


    def classicTimeseries(self):
        from apps.analysis.getTimeseries import getTimeseries

        getparams = web.input()
        yearts = getparams.yearTS
        wkt = getparams.WKT
        requestedtimeseries = json.loads(getparams.selectedTimeseries)
        tsFromPeriod = getparams.tsFromPeriod
        tsToPeriod = getparams.tsToPeriod
        yearsToCompare = getparams.yearsToCompare
        tsFromSeason = getparams.tsFromSeason
        tsToSeason = getparams.tsToSeason
        showYearInTicks = True
        data_available = False

        # if isinstance(yearsToCompare, basestring):  # One year passed but is not a list so make it a list.
        #     # yearsToCompare = list(yearsToCompare)
        #     yearsToCompare = []
        #     yearsToCompare.append(getparams.yearsToCompare)

        if tsFromSeason != '' and tsToSeason != '' and yearsToCompare != '':
            yearsToCompare = json.loads(yearsToCompare)
            showYearInTicks = False
            if len(yearsToCompare) == 1:
                for year in yearsToCompare:
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

        elif yearsToCompare != '':
            yearsToCompare = json.loads(yearsToCompare)
            showYearInTicks = False
            if len(yearsToCompare) == 1:
                for year in yearsToCompare:
                    from_date = datetime.date(int(year), 01, 01)
                    to_date = datetime.date(int(year), 12, 31)

        elif getparams.yearTS != '':
            if tsFromSeason != '' and tsToSeason != '':
                if tsToSeason != '':
                    from_date = datetime.date(int(getparams.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                    to_date = datetime.date(int(getparams.yearTS), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(getparams.yearTS)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))
                else:
                    from_date = datetime.date(int(getparams.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                    to_date = datetime.date(int(getparams.yearTS), 12, 31)
            else:
                from_date = datetime.date(int(getparams.yearTS), 01, 01)
                to_date = datetime.date(int(getparams.yearTS), 12, 31)
            showYearInTicks = False

        elif tsFromPeriod != '' and tsToPeriod != '':
            from_date = datetime.datetime.strptime(tsFromPeriod, '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(tsToPeriod, '%Y-%m-%d').date()



        cum_yaxe = []
        timeseries = []
        for timeserie in requestedtimeseries:
            productcode = timeserie['productcode']
            subproductcode = timeserie['subproductcode']
            version = timeserie['version']
            mapsetcode = timeserie['mapsetcode']
            date_format = timeserie['date_format']

            product = {"productcode": productcode,
                       "subproductcode": subproductcode,
                       "version": version}

            # Set defaults in case no entry exists in the DB
            aggregate = { 'aggregation_type': 'mean',
                          'aggregation_min': None,
                          'aggregation_max': None }
            timeseries_drawproperties = querydb.get_product_timeseries_drawproperties(product)
            for ts_drawprops in timeseries_drawproperties:
                aggregate = { 'aggregation_type': ts_drawprops.aggregation_type,
                              'aggregation_min': ts_drawprops.aggregation_min,
                              'aggregation_max': ts_drawprops.aggregation_max}

                if timeserie['cumulative']:
                    cum_yaxe.append(ts_drawprops.yaxes_id)


            if date_format == 'MMDD' and len(yearsToCompare) > 1:
                year = yearsToCompare[0]
                showYearInTicks = False
                from_date = datetime.date(year, 01, 01)
                to_date = datetime.date(year, 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)
                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(list_values) > 1:
                    data_available = True

                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      # 'xAxis': str(year),
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True,
                      'cumulative': timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
                for ts_drawprops in timeseries_drawproperties:
                    ts = {'name': ts_drawprops.tsname_in_legend,
                          'type': ts_drawprops.charttype,
                          'dashStyle': ts_drawprops.linestyle,
                          'lineWidth': ts_drawprops.linewidth,
                          'color': ts_drawprops.color,
                          # 'xAxis': str(year),
                          'yAxis': ts_drawprops.yaxes_id,
                          'data': data,
                          'visible': True,
                          'cumulative': timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)

            elif len(yearsToCompare) > 1:     # yearsToCompare != '' or
                # yearsToCompare = json.loads(yearsToCompare)
                colorAdd = 0
                colorSubstract = 0
                for year in yearsToCompare:
                    showYearInTicks = False
                    from_date = datetime.date(int(year), 01, 01)
                    to_date = datetime.date(int(year), 12, 31)

                    if tsFromSeason != '' and tsToSeason != '':
                        from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                        to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                        if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                            to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                    if ts_drawprops.color[0] == '#':        # Transform HTML HEX color code to RGB
                        h = ts_drawprops.color.lstrip('#')
                        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
                        rgb = list(rgb)
                    else:
                        rgb = ts_drawprops.color.split(' ')
                    rgb = map(int,rgb)
                    rgb[-1] = rgb[-1]+colorAdd
                    rgb[-2] = rgb[-2]+colorAdd
                    rgb[-3] = rgb[-3]-colorSubstract
                    tsColor = ' '.join([str(i) for i in rgb])
                    colorAdd += 65
                    colorSubstract += 50

                    list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)
                    data = []
                    for val in list_values:
                        value = []
                        # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                        valdate = functions.unix_time_millis(val['date'])
                        # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                        value.append(valdate)
                        value.append(val['meanvalue'])
                        data.append(value)
                    if len(list_values) > 1:
                        data_available = True

                    # Set defaults in case no entry exists in the DB
                    ts = {'name': str(year) + ' ' + productcode + '-' + version + '-' + subproductcode,
                          'type': 'line',
                          'dashStyle': 'Solid',
                          'lineWidth': 2,
                          'color': '#000000',
                          'xAxis': str(year),
                          'yAxis': productcode + ' - ' + version,
                          'data': data,
                          'visible': True,
                          'cumulative': timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                    for ts_drawprops in timeseries_drawproperties:
                        ts = {'name': str(year) + ' ' + ts_drawprops.tsname_in_legend,
                              'type': ts_drawprops.charttype,
                              'dashStyle': ts_drawprops.linestyle,
                              'lineWidth': ts_drawprops.linewidth,
                              'color': tsColor,
                              'xAxis': str(year),
                              'yAxis': ts_drawprops.yaxes_id,
                              'data': data,
                              'visible': True,
                              'cumulative': timeserie['cumulative'],
                              'difference': timeserie['difference'],
                              'reference': timeserie['reference']
                              }
                    timeseries.append(ts)

            else:
                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)
                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)

                if len(list_values) > 1:
                    data_available = True

                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'cumulative': timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
                for ts_drawprops in timeseries_drawproperties:
                    ts = {'name': ts_drawprops.tsname_in_legend,
                          'type': ts_drawprops.charttype,
                          'dashStyle': ts_drawprops.linestyle,
                          'lineWidth': ts_drawprops.linewidth,
                          'color': ts_drawprops.color,
                          'yAxis': ts_drawprops.yaxes_id,
                          'data': data,
                          'cumulative': timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)


        yaxes = []
        count = 0
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries)
        axes = len(timeseries_yaxes)
        for yaxe in timeseries_yaxes:
            count += 1
            opposite = "false"
            # if axes >= 2 and count % 2 == 0:   # and yaxe.oposite == "f"
            #     opposite = "false"
            # if axes >= 2 and count % 2 != 0:   # and yaxe.oposite == "t"
            #     opposite = "true"
            if axes >= 2:
                if yaxe.oposite:
                    opposite = "true"
            if axes == 1:
                opposite = "false"

            if yaxe.yaxes_id in cum_yaxe:
                min = ''
                max = ''
            else:
                min = yaxe.min
                max = yaxe.max
            yaxe = {'id': yaxe.yaxes_id, 'title': yaxe.title, 'title_color': yaxe.title_color, 'unit': yaxe.unit, 'opposite': opposite,
                    'min': min, 'max': max, 'aggregation_type': yaxe.aggregation_type, 'aggregation_min': yaxe.aggregation_min, 'aggregation_max': yaxe.aggregation_max}
            yaxes.append(yaxe)



        ts_json = {"data_available": data_available,
                   "showYearInTicks": showYearInTicks,
                   "showYearInToolTip": "true",
                   "yaxes": yaxes,
                   "timeseries": timeseries}

        ts_json = json.dumps(ts_json,
                             ensure_ascii=False,
                             sort_keys=True,
                             # indent=4,
                             separators=(', ', ': '))

        # print ts_json
        # timeseries_json = '{"success":"true", "total":' + str(timeline.__len__()) + ',"timeline":'+timeline_json+'}'
        # timeline_json = '{"success":"true"}'
        return ts_json


class TimeseriesProducts:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import copy
        # import time
        # t0 = time.time()
        db_products = querydb.get_timeseries_products()
        # totalget_dataset = 0
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
                prod_dict['productid'] = prod_record['productid']
                prod_dict['productcode'] = prod_record['productcode']
                prod_dict['version'] = prod_record['version']
                prod_dict['subproductcode'] = prod_record['subproductcode']
                # prod_dict['mapsetcode'] = ""
                # prod_dict['mapset_name'] = ""
                prod_dict['group_product_descriptive_name'] = prod_record['descriptive_name']
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
                p = Product(product_code=productcode, version=version)
                all_prod_mapsets = p.mapsets
                if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                    for mapset in all_prod_mapsets:
                        mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                        if mapset_info:
                            mapset_record = functions.row2dict(mapset_info)

                            prod_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_record['mapsetcode']
                            prod_dict['mapsetcode'] = mapset_record['mapsetcode']
                            prod_dict['mapset_name'] = mapset_record['descriptive_name']

                            # t4 = time.time()

                            dataset = p.get_dataset(mapset=mapset, sub_product_code=prod_dict['subproductcode'])
                            dataset.get_filenames()
                            all_present_product_dates = dataset.get_dates()

                            # t5 = time.time()
                            # tot_get_dataset = t5-t4
                            # totalget_dataset = totalget_dataset + tot_get_dataset
                            # print 'get_dataset: ' + str(total)


                            # t6 = time.time()

                            distinctyears = []
                            for product_date in all_present_product_dates:
                                if product_date.year not in distinctyears:
                                    distinctyears.append(product_date.year)
                            prod_dict['years'] = distinctyears

                            if prod_dict['years'].__len__() > 0:
                                tmp_prod_dict = copy.deepcopy(prod_dict)

                                products_dict_all.append(tmp_prod_dict)
                                tmp_prod_dict = []

                            # t7 = time.time()
                            # total = t7-t6
                            # print 'years: ' + str(total)

                            timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                            version=version,
                                                                                            subproductcode=subproductcode)
                            # t8 = time.time()
                            for subproduct in timeseries_mapset_datasets:
                                if subproduct is not None:

                                    dataset_record = functions.row2dict(subproduct)
                                    dataset = p.get_dataset(mapset=mapset, sub_product_code=dataset_record['subproductcode'])
                                    dataset.get_filenames()
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
                                    dataset_dict['mapsetcode'] = mapset_record['mapsetcode']
                                    dataset_dict['mapset_name'] = mapset_record['descriptive_name']
                                    dataset_dict['group_product_descriptive_name'] = prod_record['descriptive_name']
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
                                        # tmp_prod_dict = prod_dict.copy()
                                        tmp_prod_dict = copy.deepcopy(dataset_dict)

                                        products_dict_all.append(tmp_prod_dict)
                                        tmp_prod_dict = []

            #                 t9 = time.time()
            #                 totals_subproduct = t9-t8
            #         print 'totals subproduct: ' + str(totals_subproduct)
            # print 'get_dataset: ' + str(totalget_dataset)

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

        # t1 = time.time()
        # total = t1-t0
        # print 'Total time: ' + str(total)

        return datamanagement_json


class __TimeseriesProductsTree:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import copy

        db_products = querydb.get_timeseries_products()

        if hasattr(db_products, "__len__") and db_products.__len__() > 0:
            products_dict_all = []
            # loop the products list
            for row in db_products:
                prod_dict = {}
                prod_record = functions.row2dict(row)
                productcode = prod_record['productcode']
                subproductcode = prod_record['subproductcode']
                version = prod_record['version']

                # prod_dict['itemtype'] = "TimeseriesProduct"
                prod_dict['cat_descr_name'] = prod_record['cat_descr_name']
                prod_dict['category_id'] = prod_record['category_id']
                prod_dict['order_index'] = prod_record['order_index']
                prod_dict['productid'] = prod_record['productid']
                prod_dict['productcode'] = prod_record['productcode']
                prod_dict['version'] = prod_record['version']
                prod_dict['subproductcode'] = prod_record['subproductcode']
                # prod_dict['mapsetcode'] = ""
                prod_dict['descriptive_name'] = prod_record['descriptive_name']
                prod_dict['description'] = prod_record['description']
                # prod_dict['years'] = []
                # prod_dict['parentId'] = 'root'
                # prod_dict['leaf'] = False

                # does the product have mapsets?
                p = Product(product_code=productcode, version=version)
                all_prod_mapsets = p.mapsets
                # print all_prod_mapsets

                if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                    prod_dict['productmapsets'] = []
                    # prod_dict['children'] = []
                    for mapset in all_prod_mapsets:
                        mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                        if mapset_info:
                            mapset_record = functions.row2dict(mapset_info)
                            # print mapset_record
                            mapset_dict = {}
                            # mapset_dict['itemtype'] = "TimeseriesMapset"
                            # mapset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                            # mapset_dict['category_id'] = prod_record['category_id']
                            # mapset_dict['order_index'] = prod_record['order_index']
                            # mapset_dict['productid'] = prod_record['productid']
                            # mapset_dict['productcode'] = prod_record['productcode']
                            # mapset_dict['version'] = prod_record['version']
                            # mapset_dict['subproductcode'] = prod_record['subproductcode']
                            mapset_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_record['mapsetcode']
                            mapset_dict['mapsetcode'] = mapset_record['mapsetcode']
                            mapset_dict['descriptive_name'] = mapset_record['descriptive_name']
                            mapset_dict['description'] = mapset_record['description']
                            mapset_dict['timeseriesmapsetdatasets'] = []
                            # mapset_dict['years'] = []
                            # mapset_dict['parentId'] = prod_record['productid']
                            # mapset_dict['leaf'] = False
                            # mapset_dict['children'] = []
                            timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                            version=version,
                                                                                            subproductcode=subproductcode)
                            for subproduct in timeseries_mapset_datasets:
                                if subproduct is not None:
                                    dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                    dataset.get_filenames()
                                    all_present_product_dates = dataset.get_dates()

                                    distinctyears = []
                                    for product_date in all_present_product_dates:
                                        if product_date.year not in distinctyears:
                                            distinctyears.append(product_date.year)

                                    dataset_record = functions.row2dict(subproduct)
                                    dataset_dict = {}
                                    # dataset_dict['itemtype'] = "TimeseriesSubproduct"
                                    # dataset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                                    # dataset_dict['category_id'] = prod_record['category_id']
                                    # dataset_dict['order_index'] = prod_record['order_index']
                                    dataset_dict['subproductid'] = dataset_record['productid']
                                    dataset_dict['productcode'] = dataset_record['productcode']
                                    dataset_dict['version'] = dataset_record['version']
                                    dataset_dict['subproductcode'] = dataset_record['subproductcode']
                                    dataset_dict['mapsetcode'] = mapset_record['mapsetcode']
                                    dataset_dict['descriptive_name'] = dataset_record['descriptive_name']
                                    dataset_dict['description'] = dataset_record['description']
                                    dataset_dict['years'] = distinctyears
                                    # dataset_dict['leaf'] = True
                                    # dataset_dict['checked'] = False
                                    # dataset_dict['parentId'] = mapset_dict['productmapsetid']

                                    # dataset_dict['mapsetcode'] = mapset
                                    mapset_dict['timeseriesmapsetdatasets'].append(dataset_dict)
                                    # mapset_dict['children'].append(dataset_dict)

                            if dataset_dict['years'].__len__() > 0:
                                # tmp_prod_dict = prod_dict.copy()
                                tmp_prod_dict = copy.deepcopy(prod_dict)

                                tmp_prod_dict['productmapsets'].append(mapset_dict)
                                # tmp_prod_dict['children'].append(mapset_dict)
                                products_dict_all.append(tmp_prod_dict)
                                tmp_prod_dict = []

            prod_json = json.dumps(products_dict_all,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            # datamanagement_json = '{"products":'+prod_json+'}'
            # datamanagement_json = '{"descriptive_name": "", "productid": "root", "parentId": null, "leaf": false, "children": '+prod_json+'}'

            datamanagement_json = '{"success":"true", "total":'\
                                  + str(db_products.__len__())\
                                  + ',"products":'+prod_json+'}'

        else:
            datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

        return datamanagement_json


class __TimeseriesProducts:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import copy

        db_products = querydb.get_timeseries_products()

        if hasattr(db_products, "__len__") and db_products.__len__() > 0:
            products_dict_all = []
            # loop the products list
            for row in db_products:
                prod_dict = functions.row2dict(row)
                productcode = prod_dict['productcode']
                subproductcode = prod_dict['subproductcode']
                version = prod_dict['version']

                p = Product(product_code=productcode, version=version)

                # does the product have mapsets?
                all_prod_mapsets = p.mapsets
                # print productcode
                # print all_prod_mapsets
                if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                    prod_dict['productmapsets'] = []
                    for mapset in all_prod_mapsets:
                        mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False, echo=False)
                        mapset_dict = functions.row2dict(mapset_info)
                        mapset_dict['timeseriesmapsetdatasets'] = []
                        timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                        version=version,
                                                                                        subproductcode=subproductcode)
                        for subproduct in timeseries_mapset_datasets:
                            if subproduct is not None:
                                dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                dataset.get_filenames()
                                all_present_product_dates = dataset.get_dates()

                                distinctyears = []
                                for product_date in all_present_product_dates:
                                    if product_date.year not in distinctyears:
                                        distinctyears.append(product_date.year)

                                dataset_dict = functions.row2dict(subproduct)

                                # if productcode == 'vgt-ndvi':
                                #     print dataset.get_filenames()
                                #     print all_present_product_dates
                                #     print distinctyears

                                dataset_dict['years'] = distinctyears
                                dataset_dict['mapsetcode'] = mapset
                                mapset_dict['timeseriesmapsetdatasets'].append(dataset_dict)

                        if dataset_dict['years'].__len__() > 0:
                            # tmp_prod_dict = prod_dict.copy()
                            tmp_prod_dict = copy.deepcopy(prod_dict)

                            tmp_prod_dict['productmapsets'].append(mapset_dict)
                            products_dict_all.append(tmp_prod_dict)
                            tmp_prod_dict = []

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


class GetTimeLine:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        p = Product(product_code=getparams['productcode'], version=getparams['productversion'])
        dataset = p.get_dataset(mapset=getparams['mapsetcode'], sub_product_code=getparams['subproductcode'])
        dataset.get_filenames()
        all_present_product_dates = dataset.get_dates()
        # completeness = dataset.get_dataset_normalized_info()
        firstdate = dataset.get_first_date()
        lastdate = all_present_product_dates[-1]

        kwargs = {'productcode': getparams['productcode'],
                  'version': getparams['productversion'],
                  'subproductcode': getparams['subproductcode'].lower() if getparams['subproductcode'] else None}
        db_product = querydb.get_product_out_info(**kwargs)
        if isinstance(db_product, list):
            db_product = db_product[0]

        frequency = Dataset.get_frequency(db_product.frequency_id, db_product.date_format)
        # frequency = dataset._frequency # se questo property non era protetto, la query sopra non serve
        alldates = frequency.get_dates(firstdate, lastdate)

        timeline = []
        for productdate in alldates:
            if productdate in all_present_product_dates:
                present = "true"
            else:
                present = "false"
            dateinmilisecond = functions.unix_time_millis(productdate)
            date_dict = {'datetime': dateinmilisecond, 'date': productdate.strftime("%Y%m%d"), 'present': present}
            timeline.append(date_dict)

        # missingdate = datetime.date(2003, 2, 1)
        # dateinmilisecond = functions.unix_time_millis(missingdate)
        # date_dict = {'datetime': dateinmilisecond, 'date': missingdate.strftime("%Y%m%d"), 'present': "false"}
        # timeline.append(date_dict)

        timeline_json = json.dumps(timeline,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        timeline_json = '{"success":"true", "total":' + str(timeline.__len__()) + ',"timeline":'+timeline_json+'}'

        # print timeline_json
        return timeline_json

class GetAllColorSchemes:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

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


class GetProductColorSchemes:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        product_legends = querydb.get_product_legends(productcode=getparams['productcode'],
                                                      subproductcode=getparams['subproductcode'],
                                                      version=getparams['productversion'])

        if hasattr(product_legends, "__len__") and product_legends.__len__() > 0:
            legends_dict_all = []
            for legend in product_legends:
                # legend_dict = functions.row2dict(legend)
                # legend_dict = legend.__dict__
                legend_dict = {}
                legend_id = legend['legend_id']
                legend_name = legend['legend_name']
                # legend_name = legend['colorbar']
                default_legend = legend['default_legend']

                if default_legend == True:
                    defaultlegend = 'true'
                else:
                    defaultlegend = 'false'

                # if there is only 1 legend defined, this is the default legend (even if not defined as default legend).
                if product_legends.__len__() == 1:
                    defaultlegend = 'true'

                if defaultlegend == 'true':
                    defaulticon = 'x-grid3-radio-col-on'
                else:
                    defaulticon = 'x-grid3-radio-col'

                # $legendHTML = generateLegendHTML($db, $legend_id, $Language);
                # $legendHTML = str_replace('"', "'", $legendHTML);

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
                legend_dict['default_legend'] = defaultlegend
                legend_dict['defaulticon'] = defaulticon
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

            colorschemes = '{"success":"true", "total":' + str(product_legends.__len__()) + ',"legends":'+legends_json+'}'
        else:
            colorschemes = '{"success":"true", "message":"No legends defined for this product!"}'

        return colorschemes


class ProductNavigatorDataSets:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
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


class GetLogFile:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        logfilename = ''
        if getparams['logtype'] == 'get':
            if getparams['gettype'] == 'EUMETCAST':
                logfilename = es_constants.es2globals['log_dir']+'apps.get_eumetcast.' + getparams['data_source_id'] + '.log'
            else:
                logfilename = es_constants.es2globals['log_dir']+'apps.get_internet.' + getparams['data_source_id'] + '.log'
        elif getparams['logtype'] == 'ingest':
            logfilename = es_constants.es2globals['log_dir']+'apps.ingestion.' + getparams['productcode'] + '.' + getparams['version'] + '.log'
        elif getparams['logtype'] == 'processing':
            # apps.processing.ID=6_PROD=tamsat-rfe_METHOD=std_precip_prods_only_ALGO=std_precip.log
            logfilename = es_constants.es2globals['log_dir']+'apps.processing.' \
                                        + 'ID=' + getparams['process_id'] + '_' \
                                        + 'PROD=' + getparams['productcode'] + '_' \
                                        + 'METHOD=' + getparams['derivation_method'] + '_' \
                                        + 'ALGO=' + getparams['algorithm'] + '.log'
        elif getparams['logtype'] == 'service':
            if getparams['service'] == 'eumetcast':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.get_eumetcast.log'
            if getparams['service'] == 'internet':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.get_internet.log'
            if getparams['service'] == 'ingest':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.ingestion.log'
            if getparams['service'] == 'processing':
                logfilename = es_constants.es2globals['log_dir']+'apps.processing.processing.log'
            if getparams['service'] == 'system':
                logfilename = es_constants.es2globals['log_dir']+'apps.es2system.es2system.log'
            if getparams['service'] == 'dbsync':
                logfilename = '/var/log/bucardo/log.bucardo'
            if getparams['service'] == 'datasync':
                # logfilename = '/var/log/rsyncd.log'
                logfilename = es_constants.es2globals['log_dir']+'rsync.log'

        # logfilepath = es_constants.es2globals['log_dir']+logfilename
        # Display only latest (most recent file) - see #69-1
        logfilenames = sorted(glob.glob(logfilename + "*"), key=str, reverse=False)

        # print sorted(logfilenames, key=str, reverse=False)
        if len(logfilenames) > 0:
            logfilecontent = ''
            for logfilepath in logfilenames:
                if os.path.isfile(logfilepath):
                    # logfile = open(logfilepath, 'r')
                    # logfilecontent = logfile.read()
                    for line in reversed(open(logfilepath).readlines()):
                        logfilecontent += line

            # logfilecontent = logfilecontent.replace('\'', '')
            # logfilecontent = logfilecontent.replace(chr(10), '<br />')
            # logfilecontent = logfilecontent.replace(' TRACE ', '<b style="color:gray"> TRACE </b>')
            # logfilecontent = logfilecontent.replace(' DEBUG ', '<b style="color:gray"> DEBUG </b>')
            # logfilecontent = logfilecontent.replace(' INFO ', '<b style="color:green"> INFO </b>')
            # logfilecontent = logfilecontent.replace(' WARNING ', '<b style="color:orange"> WARN </b>')
            # logfilecontent = logfilecontent.replace(' WARN ', '<b style="color:orange"> WARN </b>')
            # logfilecontent = logfilecontent.replace(' ERROR ', '<b style="color:red"> ERROR </b>')
            # logfilecontent = logfilecontent.replace(' CRITICAL ', '<b style="color:red"> FATAL </b>')
            # logfilecontent = logfilecontent.replace(' FATAL ', '<b style="color:red"> FATAL </b>')
            # logfilecontent = logfilecontent.replace(' CLOSED ', '<b style="color:brown"> CLOSED </b>')

            logfilecontent = logfilecontent.replace('\'', '')
            logfilecontent = logfilecontent.replace(chr(10), '<br />')
            logfilecontent = logfilecontent.replace(' TRACE ', "<b style='color:gray'> TRACE </b>")
            logfilecontent = logfilecontent.replace(' DEBUG ', "<b style='color:gray'> DEBUG </b>")
            logfilecontent = logfilecontent.replace(' INFO ', "<b style='color:green'> INFO </b>")
            logfilecontent = logfilecontent.replace(' WARNING ', "<b style='color:orange'> WARN </b>")
            logfilecontent = logfilecontent.replace(' WARN ', "<b style='color:orange'> WARN </b>")
            logfilecontent = logfilecontent.replace(' ERROR ', "<b style='color:red'> ERROR </b>")
            logfilecontent = logfilecontent.replace(' CRITICAL ', "<b style='color:red'> FATAL </b>")
            logfilecontent = logfilecontent.replace(' FATAL ', "<b style='color:red'> FATAL </b>")
            logfilecontent = logfilecontent.replace(' CLOSED ', "<b style='color:brown'> CLOSED </b>")

        else:
            logfilecontent = 'NO LOG FILE PRESENT'

        logfilecontent_json = json.dumps(logfilecontent,
                                         ensure_ascii=False,
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

        # logfile_json = '{"success":"true", "filename":\'' + logfilename + '\',"logfilecontent":\''+logfilecontent+'\'}'
        logfile_json = '{"success":"true","filename":"' + logfilename + '","logfilecontent":"'+logfilecontent+'"}'

        return logfile_json


class setIngestArchives:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "setingestarchives"):

            functions.setSystemSetting('ingest_archive_eum', getparams['setingestarchives'])

            # Todo: call system service to change the mode

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            from lib.python import reloadmodules
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"Setting Ingest Archives from Eumetcast changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class ChangeRole:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "role"):

            functions.setSystemSetting('role', getparams['role'])

            # Todo: call system service to change the mode

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            from lib.python import reloadmodules
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            changerole_json = '{"success":"true", "message":"Role changed!"}'
        else:
            changerole_json = '{"success":false, "error":"No role given!"}'

        return changerole_json


class ChangeMode:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "mode"):
            newmode = getparams['mode']
            systemsettings = functions.getSystemSettings()
            This_PC_mode = systemsettings['mode'].lower()
            PC23_connection = False
            Other_PC_mode = None
            IP_other_PC = None
            permitChangeMode = False
            message = 'Changing to Mode NOT possible!'

            # TODO: Use port 80?
            IP_port = ':22'

            if systemsettings['type_installation'].lower() == 'full':
                # Check if other PC is reachable and in which mode it is!
                if systemsettings['role'].lower() == 'pc2':
                    # Check connection to PC3
                    # PC23_connection = functions.check_connection(systemsettings['ip_pc3'] + IP_port)
                    PC23_connection = functions.check_connection('mesa-pc3')
                    IP_other_PC = systemsettings['ip_pc3']

                    if PC23_connection:
                        # status_PC3 = functions.get_remote_system_status(systemsettings['ip_pc3'])
                        status_PC3 = functions.get_remote_system_status('mesa-pc3')
                        if 'mode' in status_PC3:
                            Other_PC_mode = status_PC3['mode']
                        else:
                            PC3_Webserver_Status = False

                elif systemsettings['role'].lower() == 'pc3':
                    This_PC_mode = systemsettings['mode'].lower()

                    # Check connection to PC2
                    # PC23_connection = functions.check_connection(systemsettings['ip_pc2'] + IP_port)
                    PC23_connection = functions.check_connection('mesa-pc2')
                    IP_other_PC = systemsettings['ip_pc2']

                    if PC23_connection:
                        # status_PC2 = functions.get_remote_system_status(systemsettings['ip_pc2'])
                        status_PC2 = functions.get_remote_system_status('mesa-pc2')
                        if 'mode' in status_PC2:
                            Other_PC_mode = status_PC2['mode']
                        else:
                            PC2_Webserver_Status = False

            if This_PC_mode == 'nominal' and newmode == 'recovery':
                if PC23_connection:
                    if Other_PC_mode == 'nominal':
                        permitChangeMode = False
                    if Other_PC_mode == 'recovery':
                        permitChangeMode = False
                    if Other_PC_mode == 'maintenance':
                        permitChangeMode = True
                else:
                    permitChangeMode = True

            elif This_PC_mode == 'nominal' and newmode == 'maintenance':
                permitChangeMode = True

            elif This_PC_mode == 'recovery' and newmode == 'nominal':
                if PC23_connection:
                    if Other_PC_mode == 'nominal':
                        permitChangeMode = False
                    if Other_PC_mode == 'recovery':
                        permitChangeMode = False
                    if Other_PC_mode == 'maintenance':
                        permitChangeMode = True
                else:
                    permitChangeMode = False

            elif This_PC_mode == 'recovery' and newmode == 'maintenance':
                permitChangeMode = False

            elif This_PC_mode == 'maintenance' and newmode == 'nominal':
                if PC23_connection:
                    if Other_PC_mode == 'nominal':
                        permitChangeMode = True
                    if Other_PC_mode == 'recovery':
                        permitChangeMode = False
                    if Other_PC_mode == 'maintenance':
                        permitChangeMode = False
                else:
                    permitChangeMode = True

            elif This_PC_mode == 'maintenance' and newmode == 'recovery':
                permitChangeMode = False

            else:
                permitChangeMode = False

            if permitChangeMode:
                functions.setSystemSetting('mode', getparams['mode'])
                message = 'Mode changed!'

                # Set Data and DB sync.
                if newmode == 'recovery':
                    functions.setSystemSetting('data_sync', 'false')
                    functions.setSystemSetting('db_sync', 'false')
                elif newmode == 'nominal':
                    functions.setSystemSetting('data_sync', 'true')
                    functions.setSystemSetting('db_sync', 'true')
                elif newmode == 'maintenance':
                    functions.setSystemSetting('data_sync', 'false')
                    functions.setSystemSetting('db_sync', 'false')

                # Specific transition actions
                if This_PC_mode == 'recovery' and newmode == 'nominal':
                    source = es_constants.es2globals['processing_dir']
                    target = IP_other_PC+'::products'+es_constants.es2globals['processing_dir']

                    statusdatasync = es2system.system_data_sync(source, target)

                    statusdbsync = es2system.system_db_sync_full(systemsettings['role'].lower())

                    message = 'Data and Settings Synchronized to the other PC. You must now put the other PC in Nominal mode!'

                # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
                from lib.python import reloadmodules
                reloadmodules.reloadallmodules()
                # Reloading the settings does not work well so set manually

                changemode_json = '{"success":"true", "message":"'+message+'"}'
            else:
                changemode_json = '{"success":false, "message":"'+message+'"}'

        else:
            changemode_json = '{"success":false, "error":"No mode given!"}'

        return changemode_json


class GetAvailableVersions:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # getparams = web.input()

        versions_dict = functions.getListVersions()
        versions_json = json.dumps(versions_dict,
                                   ensure_ascii=False,
                                   encoding='utf-8',
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        versions_json = '{"success":"true", "versions":'+versions_json+'}'

        # versions_json = '{"success":false, "error":"No versions available!"}'

        return versions_json


class ChangeVersion:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "version"):

            functions.setSystemSetting('active_version', getparams['version'])

            # Todo: call system service to change the version! PROBLEMS: answer back to browser?
            base = es_constants.es2globals['base_dir']  # +"-"

            if os.path.exists(base):
                if os.path.islink(base):
                    os.unlink(base)
                    # print base+"-"+getparams['version']
                    os.symlink(base+"-"+getparams['version'], base)
                elif os.path.isdir(base):
                    error = 'The base is a directory and should be a symbolic link!'

            changeversion_json = '{"success":"true", "message":"Version changed!"}'
        else:
            changeversion_json = '{"success":false, "error":"No version given!"}'

        return changeversion_json


class GetThemas:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        themas_dict_all = []
        themas = querydb.get_themas()

        if hasattr(themas, "__len__") and themas.__len__() > 0:
            for thema_id, description in themas:
                thema_dict = {'thema_id': thema_id,
                              'thema_description': description}  # .encode('utf-8')
                themas_dict_all.append(thema_dict)

            themas_json = json.dumps(themas_dict_all,
                                     ensure_ascii=False,
                                     encoding='utf-8',
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))

            themas_json = '{"success":"true", "total":' + str(themas.__len__()) + ',"themas":' + themas_json + '}'

        else:
            themas_json = '{"success":false, "error":"No themas defined!"}'

        return themas_json


class ChangeThema:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "thema"):

            functions.setSystemSetting('thema', getparams['thema'])

            # Set thema in database by activating the thema products, ingestion and processes.
            themaset = querydb.set_thema(getparams['thema'])

            message = 'Thema changed also on other pc!'
            setThemaOtherPC = False
            systemsettings = functions.getSystemSettings()
            if systemsettings['type_installation'].lower() == 'full':
                if systemsettings['role'].lower() == 'pc2':
                    otherPC = 'mesa-pc3'
                elif systemsettings['role'].lower() == 'pc3':
                    otherPC = 'mesa-pc2'
                else:
                    otherPC = 'mesa-pc1'

                PC23_connection = functions.check_connection(otherPC)
                if PC23_connection:
                    setThemaOtherPC = functions.setThemaOtherPC(otherPC, getparams['thema'])
                    if not setThemaOtherPC:
                        message = '<B>Thema NOT set on other pc</B>, ' + otherPC + ' because of an error on the other pc. Please set the Thema manually on the other pc!'
                else:
                    message = '<B>Thema NOT set on other pc</B>, ' + otherPC + ' because there is no connection. Please set the Thema manually on the other pc!'

            # print 'setThemaOtherPC: ' + str(setThemaOtherPC)
            if themaset:
                # print "thema changed"
                changethema_json = '{"success":"true", "message":"Thema changed on this PC!</BR>' + message + '"}'
            else:
                changethema_json = '{"success":false, "error":"Changing thema in database error!"}'
        else:
            changethema_json = '{"success":false, "error":"No thema given!"}'

        return changethema_json


class ChangeThemaFromOtherPC:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "thema"):

            functions.setSystemSetting('thema', getparams['thema'])

            # Set thema in database by activating the thema products, ingestion and processes.
            themaset = querydb.set_thema(getparams['thema'])
            # print themaset
            if themaset:
                changethema = True
            else:
                changethema = False
        else:
            changethema = False

        return changethema


class ChangeLogLevel:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "loglevel"):

            functions.setUserSetting('log_general_level', getparams['loglevel'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            from lib.python import reloadmodules
            reloadmodules.reloadallmodules()

            # ToDo: Query thema products and activate them.

            changethema_json = '{"success":"true", "message":"Thema changed!"}'
        else:
            changethema_json = '{"success":false, "error":"No log level given!"}'

        return changethema_json


class GetLayers:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        layers_dict_all = []
        layers = querydb.get_layers()

        if hasattr(layers, "__len__") and layers.__len__() > 0:
            for row in layers:
                row_dict = functions.row2dict(row)

                layer = { 'layerid': row_dict['layerid'],
                          'layerlevel': row_dict['layerlevel'],
                          'layername': row_dict['layername'],
                          'description': row_dict['description'],
                          'filename': row_dict['filename'],
                          'layerorderidx': row_dict['layerorderidx'],
                          'layertype': row_dict['layertype'],
                          'polygon_outlinecolor': row_dict['polygon_outlinecolor'],
                          'polygon_outlinewidth': row_dict['polygon_outlinewidth'],
                          'polygon_fillcolor': row_dict['polygon_fillcolor'],
                          'polygon_fillopacity': row_dict['polygon_fillopacity'],
                          'feature_display_column': row_dict['feature_display_column'],
                          'feature_highlight_outlinecolor': row_dict['feature_highlight_outlinecolor'],
                          'feature_highlight_outlinewidth': row_dict['feature_highlight_outlinewidth'],
                          'feature_highlight_fillcolor': row_dict['feature_highlight_fillcolor'],
                          'feature_highlight_fillopacity': row_dict['feature_highlight_fillopacity'],
                          'feature_selected_outlinecolor': row_dict['feature_selected_outlinecolor'],
                          'feature_selected_outlinewidth': row_dict['feature_selected_outlinewidth'],
                          'enabled': row_dict['enabled'],
                          'deletable': row_dict['deletable'],
                          'background_legend_image_filename': row_dict['background_legend_image_filename'],
                          'projection': row_dict['projection'],
                          'submenu': row_dict['submenu'],
                          'menu': row_dict['menu'],
                          'defined_by': row_dict['defined_by'],
                          'open_in_mapview': row_dict['open_in_mapview'],
                          'provider': row_dict['provider']
                        }

                layers_dict_all.append(layer)

            layers_json = json.dumps(layers_dict_all,
                                              ensure_ascii=False,
                                              encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            layers_json = '{"success":"true", "total":'\
                                   + str(layers.__len__())\
                                   + ',"layers":'+layers_json+'}'

        else:
            layers_json = '{"success":false, "error":"No Layers defined!"}'

        return layers_json


class GetServerLayerFileList:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        layerfiledir = '/eStation2/layers/'
        layers_json = ''
        layerfiles_dict = []
        pattern = ""
        alist_filter = ['geojson']
        layerfiles_json = '{"success":false, "error":"No Layers defined!"}'

        # Walk through all files in the directory that contains the files
        for root, dirs, files in os.walk(layerfiledir):
            for filename in files:
                if filename[-7:] in alist_filter and pattern in filename:
                    # print os.path.join(root,filename).replace(layerfiledir, "")
                    layerfile = {'layerfilename': os.path.join(root,filename).replace(layerfiledir, ""),
                                 'filesize': os.path.getsize(os.path.join(root,filename))}
                    layerfiles_dict.append(layerfile)

            layers_json = json.dumps(layerfiles_dict,
                                     ensure_ascii=False,
                                     encoding='utf-8',
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))

            layerfiles_json = '{"success":"true",'\
                                   + '"layerfiles":'+layers_json+'}'

        return layerfiles_json


class SaveDrawnVectorLayer:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def GET(self):
        getparams = web.input()

        # layerfiledir = '/eStation2/layers/' # change this to the directory you want to store the file in.
        layerfiledir = es_constants.es2globals['estation2_layers_dir']
        if 'layerfilename' in getparams: # to check if the file-object is created
            try:
                filepath=getparams.layerfilename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)

                # Separate base from extension
                base, extension = os.path.splitext(filename)

                # Initial new name
                new_name = os.path.join(layerfiledir, filename)

                if not os.path.exists(new_name):  # file does not exist in <layerfiledir>
                    fout = open(new_name,'w') # creates the file where the uploaded file should be stored
                    fout.write(getparams.drawnlayerfeaturesGEOSON) # .read()  writes the uploaded file to the newly created file.
                    fout.close() # closes the file, upload complete.
                else:  # file exists in <layerfiledir>
                    ii = 1
                    while True:
                        new_name = os.path.join(layerfiledir, base + "_" + str(ii) + extension)
                        if not os.path.exists(new_name):
                            fout = open(new_name,'w') # creates the file where the uploaded file should be stored
                            fout.write(getparams.drawnlayerfeaturesGEOSON) # .read()  writes the uploaded file to the newly created file.
                            fout.close() # closes the file, upload complete.
                            break
                        ii += 1

                finalfilename = new_name.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                success = True
            except:
                success = False
        else:
            success = False

        if success:
            layerdrawprobs = {
                                # 'layerid': getparams['layer']['layerid'],
                                # 'layerlevel': getparams['layer']['layerlevel'],
                                'layername': finalfilename,
                                'description': '',
                                'filename': finalfilename,
                                'layerorderidx': 1,
                                'layertype': 'polygon',
                                'polygon_outlinecolor': '#0000FF',
                                'polygon_outlinewidth': 1,
                                'polygon_fillcolor': 'Transparent',
                                # 'polygon_fillopacity': '',
                                'feature_display_column': 'NAME',
                                'feature_highlight_fillcolor': '#FF9900',
                                'feature_highlight_fillopacity': 10,
                                'feature_highlight_outlinecolor': '#33CCCC',
                                'feature_highlight_outlinewidth': 2,
                                'feature_selected_outlinecolor': '#FF0000',
                                'feature_selected_outlinewidth': 2,
                                'enabled': True,
                                'deletable': True,
                                'background_legend_image_filename': '',
                                # 'projection': '',
                                'submenu': '',
                                'menu': 'other',
                                'defined_by': 'USER',
                                # 'open_in_mapview': '',
                                'provider': 'User'}


            if self.crud_db.create('layers', layerdrawprobs):
                status = '{"success":"true", "message":"Layer created!"}'
            else:
                status = '{"success":false, "message":"An error occured while saving the settings in the database for the drawn layer!"}'


            web.header('Content-Type', 'text/html')   # 'application/x-compressed'  'application/force-download'
            web.header('Content-transfer-encoding', 'binary')
            web.header('Content-Disposition', 'attachment; filename=' + finalfilename)  # force browser to show "Save as" dialog.
            f = open(layerfiledir+'/'+finalfilename, 'rb')
            while 1:
                buf = f.read(1024 * 8)
                if not buf:
                    break
                yield buf
        else:
            status = '{"success":false, "message":"An error occured while saving the drawn layer!"}'
            # return status


class ImportLayer:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # getparams = json.loads(web.data())  # get PUT data
        getparams = web.input() # get POST data

        # layerfiledir = '/eStation2/layers/' # change this to the directory you want to store the file in.
        layerfiledir = es_constants.es2globals['estation2_layers_dir']
        if 'layerfilename' in getparams: # to check if the file-object is created
            try:
                filepath=getparams.layerfilename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)

                # Separate base from extension
                base, extension = os.path.splitext(filename)

                # Initial new name
                new_name = os.path.join(layerfiledir, filename)

                if not os.path.exists(new_name):  # file does not exist in <layerfiledir>
                    fout = open(new_name,'w') # creates the file where the uploaded file should be stored
                    fout.write(getparams.layerfile) # .read()  writes the uploaded file to the newly created file.
                    fout.close() # closes the file, upload complete.
                else:  # file exists in <layerfiledir>
                    ii = 1
                    while True:
                        new_name = os.path.join(layerfiledir, base + "_" + str(ii) + extension)
                        if not os.path.exists(new_name):
                            fout = open(new_name,'w') # creates the file where the uploaded file should be stored
                            fout.write(getparams.layerfile) # .read()  writes the uploaded file to the newly created file.
                            fout.close() # closes the file, upload complete.
                            break
                        ii += 1

                finalfilename = new_name.split('/')[-1] # splits the and chooses the last part (the filename with extension)
                success = True
            except:
                success = False
        else:
            success = False

        if success:
            status = '{"success":"true", "filename":"'+ finalfilename + '","message":"Layer imported!"}'
        else:
            status = '{"success":false, "message":"An error occured while importing the layer!"}'

        return status


class DeleteLayer:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'layer' in getparams:      # hasattr(getparams, "layer")
            layerdrawprobs = {
                                'layerid': getparams['layer']['layerid'],
                             }


            if self.crud_db.delete('layers', **layerdrawprobs):
                status = '{"success":"true", "message":"Layer deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the layer!"}'

        else:
            status = '{"success":false, "message":"No layer info passed!"}'

        return status


class CreateLayer:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'layer' in getparams:      # hasattr(getparams, "layer")
            layerdrawprobs = {
                                # 'layerid': getparams['layer']['layerid'],
                                # 'layerlevel': getparams['layer']['layerlevel'],
                                'layername': getparams['layer']['layername'],
                                'description': getparams['layer']['description'],
                                'filename': getparams['layer']['filename'],
                                'layerorderidx': getparams['layer']['layerorderidx'],
                                'layertype': getparams['layer']['layertype'],
                                'polygon_outlinecolor': getparams['layer']['polygon_outlinecolor'],
                                'polygon_outlinewidth': getparams['layer']['polygon_outlinewidth'],
                                # 'polygon_fillcolor': getparams['layer']['polygon_fillcolor'],
                                # 'polygon_fillopacity': getparams['layer']['polygon_fillopacity'],
                                'feature_display_column': getparams['layer']['feature_display_column'],
                                'feature_highlight_fillcolor': getparams['layer']['feature_highlight_fillcolor'],
                                'feature_highlight_fillopacity': getparams['layer']['feature_highlight_fillopacity'],
                                'feature_highlight_outlinecolor': getparams['layer']['feature_highlight_outlinecolor'],
                                'feature_highlight_outlinewidth': getparams['layer']['feature_highlight_outlinewidth'],
                                'feature_selected_outlinecolor': getparams['layer']['feature_selected_outlinecolor'],
                                'feature_selected_outlinewidth': getparams['layer']['feature_selected_outlinewidth'],
                                'enabled': getparams['layer']['enabled'],
                                'deletable': True,
                                'background_legend_image_filename': '',
                                # 'projection': getparams['layer']['projection'],
                                'submenu': getparams['layer']['submenu'],
                                'menu': getparams['layer']['menu'],
                                'defined_by': 'USER',
                                # 'open_in_mapview': getparams['layer']['open_in_mapview'],
                                'provider': getparams['layer']['provider'] }


            if self.crud_db.create('layers', layerdrawprobs):
                status = '{"success":"true", "message":"Layer created!"}'
            else:
                status = '{"success":false, "message":"An error occured while creating the new layer!"}'

        else:
            status = '{"success":false, "message":"No layer info passed!"}'

        return status


class UpdateLayer:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'layer' in getparams:      # hasattr(getparams, "layer")
            layerdrawprobs = {  'layerid': getparams['layer']['layerid'],
                                # 'layerlevel': getparams['layer']['layerlevel'],
                                'layername': getparams['layer']['layername'],
                                'description': getparams['layer']['description'],
                                'filename': getparams['layer']['filename'],
                                'layerorderidx': getparams['layer']['layerorderidx'],
                                'layertype': getparams['layer']['layertype'],
                                'polygon_outlinecolor': getparams['layer']['polygon_outlinecolor'],
                                'polygon_outlinewidth': getparams['layer']['polygon_outlinewidth'],
                                # 'polygon_fillcolor': getparams['layer']['polygon_fillcolor'],
                                # 'polygon_fillopacity': getparams['layer']['polygon_fillopacity'],
                                'feature_display_column': getparams['layer']['feature_display_column'],
                                'feature_highlight_fillcolor': getparams['layer']['feature_highlight_fillcolor'],
                                'feature_highlight_fillopacity': getparams['layer']['feature_highlight_fillopacity'],
                                'feature_highlight_outlinecolor': getparams['layer']['feature_highlight_outlinecolor'],
                                'feature_highlight_outlinewidth': getparams['layer']['feature_highlight_outlinewidth'],
                                'feature_selected_outlinecolor': getparams['layer']['feature_selected_outlinecolor'],
                                'feature_selected_outlinewidth': getparams['layer']['feature_selected_outlinewidth'],
                                'enabled': getparams['layer']['enabled'],
                                # 'deletable': getparams['layer']['deletable'],
                                # 'background_legend_image_filename': getparams['layer']['background_legend_image_filename'],
                                # 'projection': getparams['layer']['projection'],
                                'submenu': getparams['layer']['submenu'],
                                'menu': getparams['layer']['menu'],
                                'defined_by': getparams['layer']['defined_by'],
                                'open_in_mapview': getparams['layer']['open_in_mapview'],
                                'provider': getparams['layer']['provider'] }


            if self.crud_db.update('layers', layerdrawprobs):
                updatestatus = '{"success":"true", "message":"Layer updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the layer!"}'

        else:
            updatestatus = '{"success":false, "message":"No layer info passed!"}'

        return updatestatus


class GetVectorLayer:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        filename = getparams['file']
        # layerfilepath = '/srv/www/eStation2_Layers/'+filename
        layerfilepath = es_constants.estation2_layers_dir + os.path.sep + filename
        # if isFile(layerfilepath):
        layerfile = open(layerfilepath, 'r')
        layerfilecontent = layerfile.read()
        # else:
        #   layerfilecontent = '{"success":false, "message":"Layerfile not found!"}'
        return layerfilecontent


class SystemReport:
    def __init__(self):
        self.lang = "eng"

    def POST(self):

        filename = es2system.system_create_report()
        web.header('Content-Type', 'application/force-download')   # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition', 'attachment; filename=' + os.path.basename(filename))  # force browser to show "Save as" dialog.
        f = open(filename, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        os.remove(filename)


class InstallReport:
    def __init__(self):
        self.lang = "eng"

    def POST(self):

        filename = es2system.system_install_report()
        web.header('Content-Type', 'application/force-download')   # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition', 'attachment; filename=' + os.path.basename(filename))  # force browser to show "Save as" dialog.
        f = open(filename, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        os.remove(filename)


class ResetUserSettings:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import ConfigParser
        usersettingsinifile = es_constants.es2globals['settings_dir']+'/user_settings.ini'
        # usersettingsinifile = '/eStation2/settings/user_settings.ini'

        config_usersettings = ConfigParser.ConfigParser()
        config_usersettings.read(['user_settings.ini', usersettingsinifile])

        for option in config_usersettings.options('USER_SETTINGS'):
            config_usersettings.set('USER_SETTINGS', option, '')

        # Writing our configuration file to 'example.cfg' - COMMENTS ARE NOT PRESERVED!
        with open(usersettingsinifile, 'wb') as configfile:
            config_usersettings.write(configfile)
            configfile.close()

        # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
        from lib.python import reloadmodules
        reloadmodules.reloadallmodules()

        # from config import es_constants as constantsreloaded
        updatestatus = '{"success":"true", "message":"System settings reset to factory settings!"}'

        return updatestatus


class UpdateUserSettings:
    def __init__(self):
        self.lang = "eng"

    def PUT(self):
        import ConfigParser
        config_factorysettings = ConfigParser.ConfigParser()
        config_factorysettings.read(['factory_settings.ini',
                                     es_constants.es2globals['config_dir'] + '/factory_settings.ini'])

        usersettingsfilepath = es_constants.es2globals['settings_dir']+'/user_settings.ini'
        # usersettingsfilepath = '/eStation2/settings/user_settings.ini'
        config_usersettings = ConfigParser.ConfigParser()
        config_usersettings.read(['user_settings.ini', usersettingsfilepath])

        getparams = json.loads(web.data())
        for setting in getparams['systemsettings']:
            if setting not in ('log_general_level', 'active_version', 'current_mode', 'thema', 'role', 'type_installation', 'default_language'):
                if config_factorysettings.has_option('FACTORY_SETTINGS', setting) \
                   and config_factorysettings.get('FACTORY_SETTINGS', setting, 0) == getparams['systemsettings'][setting]:
                    config_usersettings.set('USER_SETTINGS', setting, '')
                elif config_usersettings.has_option('USER_SETTINGS', setting):
                    config_usersettings.set('USER_SETTINGS', setting, getparams['systemsettings'][setting])

        # Writing our configuration file to 'example.cfg' - COMMENTS ARE NOT PRESERVED!
        with open(usersettingsfilepath, 'wb') as configfile:
            config_usersettings.write(configfile)
            configfile.close()

        # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
        from lib.python import reloadmodules
        reloadmodules.reloadallmodules()

        updatestatus = '{"success":"true", "message":"System settings updated!"}'

        return updatestatus


class UserSettings:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import ConfigParser
        config_usersettings = ConfigParser.ConfigParser()
        config_usersettings.read(['user_settings.ini',
                                  es_constants.es2globals['settings_dir']+'/user_settings.ini'])

        config_factorysettings = ConfigParser.ConfigParser()
        config_factorysettings.read(['factory_settings.ini',
                                     es_constants.es2globals['config_dir'] + '/factory_settings.ini'])

        settings = {}
        usersettings = config_usersettings.items('USER_SETTINGS')
        for setting, value in usersettings:
            if value is not None and value != "":
                settings[setting] = value
            else:
                settings[setting] = config_factorysettings.get('FACTORY_SETTINGS', setting, 0)

        systemsettings = functions.getSystemSettings()
        settings['id'] = 0
        # settings['ip_pc1'] = systemsettings['ip_pc1']
        # settings['ip_pc2'] = systemsettings['ip_pc2']
        # settings['ip_pc3'] = systemsettings['ip_pc3']
        # settings['dns_ip'] = systemsettings['dns_ip']
        # settings['gateway_ip'] = systemsettings['gateway_ip']
        # settings['lan_access_ip'] = systemsettings['lan_access_ip']
        settings['type_installation'] = systemsettings['type_installation'].title()
        settings['role'] = systemsettings['role'].upper()
        settings['current_mode'] = systemsettings['mode'].title()
        settings['active_version'] = systemsettings['active_version'].lower()
        settings['thema'] = systemsettings['thema'].upper()
        settings['loglevel'] = es_constants.es2globals['log_general_level'].upper()

        settings_json = json.dumps(settings,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        settings_json = '{"success":"true", "systemsettings":'+settings_json+'}'

        #systemsettings_json = '{"success":false, "error":"No ingestions defined!"}'

        return settings_json


class IPSettings:
    def __init__(self):
        self.lang = "eng"

    def GET(self):

        settings = {}
        systemsettings = functions.getSystemSettings()
        settings['id'] = 0
        settings['ip_pc1'] = systemsettings['ip_pc1']
        settings['ip_pc2'] = systemsettings['ip_pc2']
        settings['ip_pc3'] = systemsettings['ip_pc3']
        settings['dns_ip'] = systemsettings['dns_ip']
        settings['gateway_ip'] = systemsettings['gateway_ip']
        settings['lan_access_ip'] = systemsettings['lan_access_ip']
        settings['type_installation'] = systemsettings['type_installation'].title()
        settings['role'] = systemsettings['role'].upper()

        settings_json = json.dumps(settings,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        settings_json = '{"success":"true", "ipsettings":'+settings_json+'}'

        #systemsettings_json = '{"success":false, "error":"No ingestions defined!"}'

        return settings_json


class UpdateIPSettings:
    def __init__(self):
        self.lang = "eng"

    def PUT(self):
        import ConfigParser

        systemsettingsfilepath = es_constants.es2globals['settings_dir']+'/system_settings.ini'
        # usersettingsfilepath = '/eStation2/settings/system_settings.ini'
        config_systemsettings = ConfigParser.ConfigParser()
        config_systemsettings.read(['system_settings.ini', systemsettingsfilepath])

        getparams = json.loads(web.data())
        for setting in getparams['ipsettings']:
            if config_systemsettings.has_option('SYSTEM_SETTINGS', setting):
                config_systemsettings.set('SYSTEM_SETTINGS', setting, getparams['ipsettings'][setting])

        with open(systemsettingsfilepath, 'wb') as configfile:
            config_systemsettings.write(configfile)
            configfile.close()

        # Call bash script to set IP address of local machine!
        sudo_psw = 'mesadmin'
        command = es_constants.es2globals['base_dir']+'/apps/es2system/network_config_1.0.sh ' + \
                  getparams['ipsettings']['ip_pc1'] + ' ' + \
                  getparams['ipsettings']['ip_pc2'] + ' ' + \
                  getparams['ipsettings']['ip_pc3'] + ' ' + \
                  getparams['ipsettings']['dns_ip'] + ' ' + \
                  getparams['ipsettings']['gateway_ip'] + ' ' + \
                  getparams['ipsettings']['lan_access_ip']

        # print command
        # ToDO: uncomment below line!
        status = os.system('echo %s | sudo -S %s' % (sudo_psw, command))

        updatestatus = '{"success":"true", "message":"IP settings updated!"}'

        return updatestatus


class GetProductLayer:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        filename_png = self.getProductLayer(getparams)

        web.header('Content-type', 'image/png')
        f = open(filename_png, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        os.remove(filename_png)

    def POST(self):
        getparams = web.input()
        filename_png = self.getProductLayer(getparams)

        web.header('Content-type', 'image/png')
        f = open(filename_png, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        os.remove(filename_png)


    def getProductLayer(self, getparams):
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

        inputparams = web.input()

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

        coords = map(float, inputparams.BBOX.split(","))
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
        epsg = inputparams.CRS.lower()   # CRS = "EPSG:4326"
        productmap.setProjection(epsg)

        w = int(inputparams.WIDTH)
        h = int(inputparams.HEIGHT)
        productmap.setSize(w, h)

        # General web service information
        productmap.setMetaData("WMS_TITLE", "Product description")
        productmap.setMetaData("WMS_SRS", inputparams.CRS.lower())
        # productmap.setMetaData("WMS_SRS", "epsg:3857")
        productmap.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 raster layers.")
        productmap.setMetaData("WMS_ENABLE_REQUEST", "*")   # necessary!!

        product_info = querydb.get_product_out_info(productcode=inputparams.productcode,
                                                    subproductcode=inputparams.subproductcode,
                                                    version=inputparams.productversion)
        if hasattr(product_info, "__len__") and product_info.__len__() > 0:
            for row in product_info:
                scale_factor = row.scale_factor
                scale_offset = row.scale_offset
                nodata = row.nodata

        legend_info = querydb.get_legend_info(legendid=inputparams.legendid)
        if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
            for row in legend_info:
                minstep = int((row.min_value - scale_offset)/scale_factor)    #int(row.min_value*scale_factor+scale_offset)
                maxstep = int((row.max_value - scale_offset)/scale_factor)    # int(row.max_value*scale_factor+scale_offset)
                realminstep = int((row.realminstep - scale_offset)/scale_factor)
                realmaxstep = int((row.realmaxstep - scale_offset)/scale_factor)
                minstepwidth = int((row.minstepwidth - scale_offset)/scale_factor)
                maxstepwidth = int((row.maxstepwidth - scale_offset)/scale_factor)
                totwidth = int((row.totwidth - scale_offset)/scale_factor)
                totsteps = row.totsteps

            # maxstep = 255
            processing_scale = 'SCALE='+str(minstep)+','+str(maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

            minbuckets = 256
            maxbuckets = 10000
            num_buckets = maxbuckets
            if minstepwidth > 0:
                num_buckets = round(totwidth / minstepwidth, 0)

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

            legend_steps = querydb.get_legend_steps(legendid=inputparams.legendid)
            if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
                stepcount = 0
                for step in legend_steps:
                    stepcount += 1
                    min_step = float((step.from_step - scale_offset)/scale_factor)
                    max_step = float((step.to_step - scale_offset)/scale_factor)
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


class GetBackgroundLayer:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import mapscript
        getparams = web.input()

        # filename = '/srv/www/eStation2_Layers/HYP_HR_SR_OB_DR/HYP_HR_SR_OB_DR.tif'
        filename = es_constants.estation2_layers_dir + '/HYP_HR_SR_OB_DR/HYP_HR_SR_OB_DR.tif'

        mapscript.msIO_installStdoutToBuffer()

        # projlib = "/usr/share/proj/"
        projlib = es_constants.proj4_lib_dir
        # errorfile = es_constants.apps_dir+"/analysis/ms_tmp/ms_errors.log"
        errorfile = es_constants.log_dir+"/mapserver_error.log"

        # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

        owsrequest = mapscript.OWSRequest()

        inputparams = web.input()
        for k, v in inputparams.iteritems():
            #print k + ':' + v
            owsrequest.setParameter(k.upper(), v)

        owsrequest.setParameter("LAYERS", getparams['layername'])

        backgroundlayer = mapscript.mapObj(es_constants.template_mapfile)
        backgroundlayer.setConfigOption("PROJ_LIB", projlib)
        backgroundlayer.setConfigOption("MS_ERRORFILE", errorfile)
        backgroundlayer.maxsize = 4096

        outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
        outputformat_png.setOption("INTERLACE", "OFF")
        backgroundlayer.appendOutputFormat(outputformat_png)
        #outputformat_gd = mapscript.outputFormatObj('GD/GIF', 'gif')
        #backgroundlayer.appendOutputFormat(outputformat_gd)
        backgroundlayer.selectOutputFormat('png')
        backgroundlayer.debug = mapscript.MS_TRUE
        backgroundlayer.status = mapscript.MS_ON
        backgroundlayer.units = mapscript.MS_DD

        coords = map(float, inputparams.BBOX.split(","))
        llx = coords[0]
        lly = coords[1]
        urx = coords[2]
        ury = coords[3]
        backgroundlayer.setExtent(llx, lly, urx, ury)   # -26, -35, 60, 38

        # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
        #epsg = "+init=epsg:3857"
        #epsg = "+init=" + inputparams.CRS.lower()   # CRS = "EPSG:4326"
        epsg = inputparams.CRS.lower()   # CRS = "EPSG:4326"
        backgroundlayer.setProjection(epsg)

        w = int(inputparams.WIDTH)
        h = int(inputparams.HEIGHT)
        backgroundlayer.setSize(w, h)

        # General web service information
        backgroundlayer.setMetaData("WMS_TITLE", "Background layer description")
        backgroundlayer.setMetaData("WMS_SRS", inputparams.CRS.lower())
        # backgroundlayer.setMetaData("WMS_SRS", "epsg:3857")
        backgroundlayer.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 background layers.")
        backgroundlayer.setMetaData("WMS_ENABLE_REQUEST", "*")   # necessary!!

        layer = mapscript.layerObj(backgroundlayer)
        layer.name = getparams['layername']
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON     # MS_DEFAULT
        layer.data = filename
        # layer.setProjection("+init=epsg:4326")
        layer.setProjection("epsg:4326")
        layer.dump = mapscript.MS_TRUE

        result_map_file = es_constants.apps_dir+'/analysis/Backgroundlayer_result.map'
        if os.path.isfile(result_map_file):
            os.remove(result_map_file)
        # backgroundlayer.save(result_map_file)
        image = backgroundlayer.draw()

        contents = backgroundlayer.OWSDispatch(owsrequest)
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        #web.header = "Content-Type","%s; charset=utf-8"%content_type
        web.header('Content-type', 'image/png')
        #web.header('Content-transfer-encoding', 'binary')
        return content


class Processing:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
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

                processing_chains_json = '{"success":"true", "total":'\
                                         + str(processing_chains.__len__())\
                                         + ',"processes":'+processes_json+'}'

        return processing_chains_json


class UpdateProcessing:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'processes' in getparams:      # hasattr(getparams, "processes")
            processinfo = {'process_id': getparams['processes']['process_id'],
                           'activated': getparams['processes']['process_activated']}

            if self.crud_db.update('processing', processinfo):
                updatestatus = '{"success":"true", "message":"Process updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the process!"}'

        else:
            updatestatus = '{"success":false, "message":"No process info passed!"}'

        return updatestatus

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'processoutputproduct' in getparams:    # hasattr(getparams, "processoutputproduct")
            for outputproduct in getparams['processoutputproduct']:
                if 'subactivated' in outputproduct:
                    processproductinfo = {'process_id': outputproduct['process_id'],
                                          'productcode': outputproduct['productcode'],
                                          'subproductcode': outputproduct['subproductcode'],
                                          'version': outputproduct['version'],
                                          'mapsetcode': outputproduct['mapsetcode'],
                                          'activated': outputproduct['subactivated']}

                    if self.crud_db.update('process_product', processproductinfo):
                        updatestatus = '{"success":"true", "message":"Process output product updated!"}'
                    else:
                        updatestatus = '{"success":false, "message":"An error occured while updating the process output product!"}'

        else:
            updatestatus = '{"success":false, "message":"No process info passed!"}'

        return updatestatus


class DataSets:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # return web.ctx
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
                        # if mapset_info.__len__() > 0:
                        mapset_dict = functions.row2dict(mapset_info)
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
                                if hasattr(dataset_info,'frequency_id'):
                                    if dataset_info.frequency_id == 'e15minute' or dataset_info.frequency_id == 'e30minute':
                                        dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # To be implemented in dataset.py
                                    elif dataset_info.frequency_id == 'e1year':
                                        dataset_dict['nodisplay'] = 'no_minutes_display'
                                    else:
                                        dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
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

            datamanagement_json = '{"success":"true", "total":'\
                                  + str(db_products.__len__())\
                                  + ',"products":'+prod_json+'}'

        else:
            datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

        return datamanagement_json


class CheckStatusAllServices:
    def __init__(self):
        self.lang = "eng"

    def POST(self):

        status_services = functions.getStatusAllServices()

        systemsettings = functions.getSystemSettings()

        servicesstatus_json = '{"success": true, "eumetcast": ' + status_services['eumetcast'] + \
                              ', "internet": ' + status_services['internet'] + \
                              ', "ingest": ' + status_services['ingest'] + \
                              ', "processing": ' + status_services['process'] + \
                              ', "system": ' + status_services['system'] + \
                              ', "ingest_archive_eum": ' + systemsettings['ingest_archive_eum'] + '}'

        return servicesstatus_json


class ExecuteServiceTask:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # return web.ctx
        # from apps.acquisition import acquisition
        message = ''
        dryrun = False
        getparams = web.input()

        if getparams.service == 'eumetcast':
            # Define pid file and create daemon
            pid_file = es_constants.get_eumetcast_pid_filename
            eumetcast_daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=dryrun)
            eumetcast_service_script = es_constants.es2globals['acq_service_dir']+os.sep+'service_get_eumetcast.py'
            status = eumetcast_daemon.status()

            logger.info(getparams.service)
            logger.info('status: ' + str(status))

            if getparams.task == 'stop':
                if status:
                    os.system("python " + eumetcast_service_script + " stop")
                    message = 'Get_eumetcast service stopped'
                else:
                    message = 'Get_eumetcast service is already down'

            elif getparams.task == 'run':
                if not status:
                    os.system("python " + eumetcast_service_script + " start")
                    message = 'Get_eumetcast service started'
                else:
                    message = 'Get_eumetcast service was already up'

            elif getparams.task == 'restart':
                os.system("python " + eumetcast_service_script + " stop")
                os.system("python " + eumetcast_service_script + " start")
                message = 'Get_eumetcast service restarted'

        if getparams.service == 'internet':
            # Define pid file and create daemon
            pid_file = es_constants.get_internet_pid_filename
            internet_daemon = acquisition.GetInternetDaemon(pid_file, dry_run=dryrun)
            internet_service_script = es_constants.es2globals['acq_service_dir']+os.sep+'service_get_internet.py'
            status = internet_daemon.status()

            if getparams.task == 'stop':
                if status:
                    os.system("python " + internet_service_script + " stop")
                    message = 'Get_internet service stopped'
                else:
                    message = 'Get_internet service is already down'
            elif getparams.task == 'run':
                if not status:
                    os.system("python " + internet_service_script + " start")
                    message = 'Get_internet service started'
                else:
                    message = 'Get_internet service was already up'

            elif getparams.task == 'restart':
                os.system("python " + internet_service_script + " stop")
                os.system("python " + internet_service_script + " start")
                message = 'Get_internet service restarted'

        if getparams.service == 'ingest':
            # Define pid file and create daemon
            pid_file = es_constants.ingestion_pid_filename
            ingest_daemon = acquisition.IngestionDaemon(pid_file, dry_run=dryrun)
            status = ingest_daemon.status()
            ingest_service_script = es_constants.es2globals['acq_service_dir']+os.sep+'service_ingestion.py'
            if getparams.task == 'stop':
                if status:
                    os.system("python " + ingest_service_script + " stop")
                    message = 'Ingestion service stopped'
                else:
                    message = 'Ingestion service is already down'

            elif getparams.task == 'run':
                if not status:
                    os.system("python " + ingest_service_script + " start")
                    message = 'Ingestion service started'
                else:
                    message = 'Ingestion service was already up'

            elif getparams.task == 'restart':
                os.system("python " + ingest_service_script + " stop")
                os.system("python " + ingest_service_script + " start")
                message = 'ingest service restarted'

        if getparams.service == 'processing':
            # Define pid file and create daemon
            pid_file = es_constants.processing_pid_filename
            processing_daemon = processing.ProcessingDaemon(pid_file, dry_run=dryrun)

            status = processing_daemon.status()
            processing_service_script = es_constants.es2globals['proc_service_dir']+os.sep+'service_processing.py'
            if getparams.task == 'stop':
                if status:
                    os.system("python " + processing_service_script + " stop")
                    message = 'Processing service stopped'
                else:
                    message = 'Processing service is already down'

            elif getparams.task == 'run':
                if not status:
                    os.system("python " + processing_service_script + " start")
                    message = 'Processing service started'
                else:
                    message = 'Processing service was already up'

            elif getparams.task == 'restart':
                os.system("python " + processing_service_script + " stop")
                os.system("python " + processing_service_script + " start")
                message = 'Processing service restarted'

        if getparams.service == 'system':
            # Define pid file and create daemon
            pid_file = es_constants.system_pid_filename
            system_daemon = es2system.SystemDaemon(pid_file, dry_run=dryrun)
            #
            status = system_daemon.status()
            system_service_script = es_constants.es2globals['system_service_dir']+os.sep+'service_system.py'
            if getparams.task == 'stop':
                if status:
                    os.system("python " + system_service_script + " stop")
                    message = 'System service stopped'
                else:
                    message = 'System service is already down'
            #
            elif getparams.task == 'run':
                if not status:
                    os.system("python " + system_service_script + " start")
                    message = 'System service started'
                else:
                    message = 'System service was already up'

            elif getparams.task == 'restart':
                os.system("python " + system_service_script + " stop")
                os.system("python " + system_service_script + " start")
                message = 'System service restarted'

        logger.info(message)
        servicesstatus_json = '{"success": true, "message": "' + message + '"}'
        return servicesstatus_json


class UpdateProductInfo:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # getparams = json.loads(web.data())
        getparams = web.input()

        productinfo = {
            'orig_productcode': getparams['orig_productcode'],
            'orig_version': getparams['orig_version'],
            'productcode': getparams['productcode'],
            'subproductcode': getparams['productcode']+'_native',
            'version': getparams['version'],
            'provider': getparams['provider'],
            'descriptive_name': getparams['prod_descriptive_name'],
            'description': getparams['description'],
            'category_id': getparams['category_id']}

        productupdated = querydb.update_product_info(productinfo, echo=False)

        if productupdated:
            updatestatus = '{"success":"true", "message":"Product updated!"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the product!"}'

        return updatestatus


class CreateProduct:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        getparams = web.input()
        if getparams['version'] == '':
            version = 'undefined'
        else:
            version = getparams['version']

        productinfo = {'productcode': getparams['productcode'],
                       'subproductcode': getparams['productcode']+'_native',
                       'version': version,
                       'product_type': 'Native',
                       'defined_by': 'USER',
                       'activated': 'f',
                       'provider': getparams['provider'],
                       'descriptive_name': getparams['prod_descriptive_name'],
                       'description': getparams['description'],
                       'category_id': getparams['category_id'],
                       'frequency_id': 'undefined',
                       'date_format': 'undefined',
                       'data_type_id': 'undefined',
                       'masked': 'f'
                       }

        if self.crud_db.create('product', productinfo):
            createstatus = '{"success":"true", "message":"Product created!"}'
        else:
            createstatus = '{"success":"false", "message":"An error occured while creating the product!"}'

        return createstatus


class UpdateProduct:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())
        productinfo = {'productcode': getparams['products']['productcode'],
                       'subproductcode': getparams['products']['subproductcode'],
                       'version': getparams['products']['version'],
                       'product_type': getparams['products']['product_type'],
                       'defined_by': getparams['products']['defined_by'],
                       'activated': getparams['products']['activated']}

        if self.crud_db.update('product', productinfo):
            updatestatus = '{"success":"true", "message":"Product updated!"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the product!"}'

        return updatestatus


class UpdateDataAcquisition:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())
        dataacquisitioninfo = {'productcode': getparams['dataacquisitions']['productcode'],
                               'subproductcode': getparams['dataacquisitions']['subproductcode'],
                               'version': getparams['dataacquisitions']['version'],
                               'data_source_id': getparams['dataacquisitions']['data_source_id'],
                               'defined_by': getparams['dataacquisitions']['defined_by'],
                               'activated': getparams['dataacquisitions']['activated'],
                               'store_original_data': getparams['dataacquisitions']['store_original_data']}

        # ToDO: distinguish upodate of activated and store_original_data! Different queries?
        if self.crud_db.update('product_acquisition_data_source', dataacquisitioninfo):
            if getparams['dataacquisitions']['store_original_data']:
                message = '<b>Activated</b> Store Native for data source <b>' + getparams['dataacquisitions']['data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'
            elif not getparams['dataacquisitions']['store_original_data']:
                message = '<b>Deactivated</b> Store Native for data source <b>' + getparams['dataacquisitions']['data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'

            if getparams['dataacquisitions']['activated']:
                message = '<b>Activated</b> data source <b>' + getparams['dataacquisitions']['data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'
            elif not getparams['dataacquisitions']['activated']:
                message = '<b>Deactivated</b> data source <b>' + getparams['dataacquisitions']['data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'

            updatestatus = '{"success":"true", "message":"' + message + '"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the Get!"}'

        return updatestatus


class UpdateIngestion:
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        # return web.ctx
        getparams = json.loads(web.data())
        ingestioninfo = {'productcode': getparams['ingestions']['productcode'],
                         'subproductcode': getparams['ingestions']['subproductcode'],
                         'version': getparams['ingestions']['version'],
                         'mapsetcode': getparams['ingestions']['mapsetcode'],
                         'defined_by': getparams['ingestions']['defined_by'],
                         'activated': getparams['ingestions']['activated']}

        if self.crud_db.update('ingestion', ingestioninfo):
            message = 'Ingestion for: </br>' + \
                      'Productcode: <b>' + getparams['ingestions']['productcode'] + '</b></br>'\
                      'Mapsetcode: <b>' + getparams['ingestions']['mapsetcode'] + '</b></br>'\
                      'Subproductcode: <b>' + getparams['ingestions']['subproductcode'] + '</b>'
            if getparams['ingestions']['activated']:
                message = '<b>Activated</b> ' + message
            else:
                message = '<b>Deactivated</b> '  + message
            updatestatus = '{"success":"true", "message":"' + message + '"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the Ingestion!"}'

        return updatestatus


class Ingestion:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # return web.ctx
        ingestions = querydb.get_ingestions(echo=False)
        # print ingestions

        if hasattr(ingestions, "__len__") and ingestions.__len__() > 0:
            ingest_dict_all = []
            for row in ingestions:
                ingest_dict = functions.row2dict(row)

                if row.mapsetcode != None and row.mapsetcode != '':
                    if row.frequency_id == 'e15minute' or row.frequency_id == 'e30minute':
                        ingest_dict['nodisplay'] = 'no_minutes_display'
                        # today = datetime.date.today()
                        # # week_ago = today - datetime.timedelta(days=7)
                        # week_ago = datetime.datetime(2015, 8, 27, 00, 00)   # .strftime('%Y%m%d%H%S')
                        # # kwargs.update({'from_date': week_ago})  # datetime.date(2015, 08, 27)
                        # kwargs = {'product_code': row.productcode,
                        #           'sub_product_code': row.subproductcode,
                        #           'version': row.version,
                        #           'mapset': row.mapsetcode,
                        #           'from_date': week_ago}
                        # dataset = Dataset(**kwargs)
                        # completeness = dataset.get_dataset_normalized_info()
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
            ingestions_json = '{"success":"true", "total":'+str(ingestions.__len__())+',"ingestions":'+ingestions_json+'}'
        else:
            ingestions_json = '{"success":false, "error":"No ingestions defined!"}'

        return ingestions_json


class DataAcquisition:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # return web.ctx

        dataacquisitions = querydb.get_dataacquisitions(echo=False)

        if hasattr(dataacquisitions, "__len__") and dataacquisitions.__len__() > 0:
            # dataacquisitions_json = tojson(dataacquisitions)

            acq_dict_all = []
            for row in dataacquisitions:
                acq_dict = functions.row2dict(row)
                # Retrieve datetime of latest acquired file and lastest datetime
                # the acquisition was active of a specific eumetcast id
                acq_dates = get_eumetcast.get_eumetcast_info(row.data_source_id)
                if acq_dates:
                    for key in acq_dates.keys():
                        # acq_info += '"%s": "%s", ' % (key, acq_dates[key])
                        if isinstance(acq_dates[key], datetime.date):
                            datetostring = acq_dates[key].strftime("%y-%m-%d %H:%M")
                            acq_dict[key] = datetostring
                        else:
                            acq_dict[key] = acq_dates[key]
                else:
                    acq_dict['time_latest_copy'] = ''   # datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['time_latest_exec'] = ''   # datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['length_proc_list'] = ''   # datetime.datetime.now().strftime("%y-%m-%d %H:%M")

                acq_dict_all.append(acq_dict)
                acq_json = json.dumps(acq_dict_all,
                                      ensure_ascii=False,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))
                dataacquisitions_json = '{"success":"true", "total":'\
                                        + str(dataacquisitions.__len__())\
                                        + ',"dataacquisitions":'+acq_json+'}'
        else:
            dataacquisitions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        return dataacquisitions_json


class ProductAcquisition:
    def __init__(self):
        self.lang = "eng"

    def GET(self, params):
        # return web.ctx
        getparams = web.input()
        products = querydb.get_products_acquisition(echo=False, activated=getparams.activated)
        products_json = functions.tojson(products)
        products_json = '{"success":"true", "total":'+str(products.__len__())+',"products":['+products_json+']}'
        return products_json


if __name__ == "__main__":
    app.run()
