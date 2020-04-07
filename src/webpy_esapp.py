#!/usr/bin/python
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from builtins import int
from builtins import open
from future import standard_library
from builtins import map
from builtins import chr
from builtins import str
from builtins import range
from builtins import object
import sys
import os
import web
import datetime
import json
import glob
import time

import webpy_esapp_helpers
from config import es_constants
from database import querydb
from database import crud
from apps.acquisition import get_eumetcast
from apps.productmanagement.datasets import Dataset
from apps.es2system import es2system
from apps.productmanagement.products import Product
from apps.analysis import generateLegendHTML
from lib.python import functions
from lib.python import es_logging as log
from lib.python import reloadmodules
# from apps.productmanagement.datasets import Frequency
# from apps.analysis.getTimeseries import (getTimeseries, getFilesList)
# from multiprocessing import (Process, Queue)
# from apps.acquisition import acquisition
# from apps.processing import processing      # Comment in WINDOWS version!

# if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

os.umask(0000)

cur_dir = os.path.dirname(__file__)
if cur_dir not in sys.path:
    sys.path.append(cur_dir)

standard_library.install_aliases()

logger = log.my_logger(__name__)

WEBPY_COOKIE_NAME = "webpy_session_id"

urls = (
    "/pa(.*)", "ProductAcquisition",
    "/product/update", "UpdateProduct",
    "/product/delete", "DeleteProduct",
    "/product/createproduct", "CreateProduct",
    "/product/updateproductinfo", "UpdateProductInfo",
    "/product/unassigndatasource", "UnassignProductDataSource",

    "/typeinstallation", "GetInstallationType",

    "/users", "Users",
    "/login", "Login",
    "/register", "Register",
    "/checkECASlogin", "checkECASlogin",

    "/help", "GetHelp",
    "/help/getfile", "GetHelpFile",

    "/categories", "GetCategories",
    "/frequencies", "GetFrequencies",
    "/dateformats", "GetDateFormats",
    "/datatypes", "GetDataTypes",
    "/projections", "GetProjections",
    "/resolutions", "GetResolutions",
    "/bboxes", "GetPredefinedBboxes",

    "/dashboard/getdashboard", "GetDashboard",
    "/dashboard/systemstatus", "GetSystemStatus",
    "/dashboard/setdataautosync", "SetDataAutoSync",
    "/dashboard/setdbautosync", "SetDBAutoSync",

    "/services/checkstatusall", "CheckStatusAllServices",
    "/services/execservicetask", "ExecuteServiceTask",

    "/ingestion", "Ingestion",
    "/ingestion/update", "UpdateIngestion",

    "/ingestsubproduct", "getIngestSubProducts",
    "/ingestsubproduct/create", "CreateIngestSubProduct",
    "/ingestsubproduct/update", "UpdateIngestSubProduct",
    "/ingestsubproduct/delete", "DeleteIngestSubProduct",

    "/subdatasourcedescription", "getSubDatasourceDescriptions",
    "/subdatasourcedescription/create", "CreateSubDatasourceDescription",
    "/subdatasourcedescription/update", "UpdateSubDatasourceDescription",
    "/subdatasourcedescription/delete", "DeleteSubDatasourceDescription",

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
    "/systemsettings/ingestarchive", "IngestArchive",

    "/processing", "Processing",
    "/processing/update", "UpdateProcessing",

    "/datasets", "DataSets",
    "/datamanagement/getrequest", "GetRequest",
    "/datamanagement/saverequest", "SaveRequest",
    "/datamanagement/createrequestjob", "createRequestJob",
    "/datamanagement/deleterequestjob", "deleteRequestJob",
    "/datamanagement/requests", "getRequestsList",
    "/datamanagement/runpauserequest", "runPauseRequest",

    "/analysis/getproductlayer", "GetProductLayer",
    "/analysis/getvectorlayer", "GetVectorLayer",
    "/analysis/getbackgroundlayer", "GetBackgroundLayer",
    "/analysis/productnavigator", "ProductNavigatorDataSets",
    "/analysis/getcolorschemes", "GetAllColorSchemes",
    "/analysis/getproductcolorschemes", "GetProductColorSchemes",
    "/analysis/gettimeline", "GetTimeLine",
    "/analysis/timeseriesproduct", "TimeseriesProducts",
    "/analysis/gettimeseries", "GetTimeseries",
    "/analysis/getgraphproperties", "GetGraphProperties",
    "/analysis/getgraphproperties/update", "UpdateGraphProperties",
    "/analysis/gettimeseriesdrawproperties", "GetTimeseriesDrawProperties",
    "/analysis/gettimeseriesdrawproperties/update", "UpdateTimeseriesDrawProperties",
    "/analysis/gettimeseriesdrawproperties/create", "CreateTimeseriesDrawProperties",
    "/analysis/updateyaxe", "UpdateYaxe",
    "/analysis/savemaptemplate", "SaveMapTemplate",
    "/analysis/usermaptemplates", "GetMapTemplates",
    "/analysis/usermaptemplates/delete", "DeleteMapTemplate",
    "/analysis/savegraphtemplate", "saveGraphTemplate",
    "/analysis/usergraphtemplates", "getGraphTemplates",
    "/analysis/usergraphtemplates/delete", "DeleteGraphTemplate",
    "/analysis/saveworkspace", "SaveWorkspace",

    "/analysis/saveworkspacepin", "SaveWorkspacePin",
    "/analysis/saveworkspacename", "SaveWorkspaceName",

    "/analysis/userworkspaces", "getUserWorkspaces",
    "/analysis/userworkspaces/delete", "DeleteWorkspace",
    "/analysis/userworkspaces/update", "saveWorkspaceInDefaultWS",
    "/analysis/exportworkspaces", "exportWorkspaces",
    "/analysis/importworkspaces", "importWorkspaces",

    "/analysis/refworkspaces", "getRefWorkspaces",
    "/analysis/refworkspaces/update", "saveWorkspaceInDefaultWS",

    "/analysis/workspacemapsgraphs", "getWorkspaceMapsAndGraphs",

    "/logos", "GetLogos",
    "/logos/create", "CreateLogo",
    "/logos/update", "UpdateLogo",
    "/logos/delete", "DeleteLogo",
    "/logos/import", "ImportLogo",

    "/layers", "GetLayers",
    "/layers/create", "CreateLayer",
    "/layers/update", "UpdateLayer",
    "/layers/delete", "DeleteLayer",
    "/layers/import", "ImportLayer",
    "/layers/serverlayerfiles", "GetServerLayerFileList",
    "/layers/savedrawnlayer", "SaveDrawnVectorLayer",
    "/layers/downloadvectorlayer", "DownloadVectorLayer",

    "/legends", "GetLegends",
    "/legends/savelegend", "SaveLegend",
    "/legends/update", "UpdateLegend",
    "/legends/delete", "DeleteLegend",
    "/legends/copylegend", "copyLegend",
    "/legends/import", "ImportLegend",
    "/legends/exportlegend", "ExportLegend",
    "/legends/legendclasses", "GetLegendClasses",
    "/legends/assignlegends", "AssignLegends",
    "/legends/unassignlegend", "UnassignLegend",
    "/legends/assigneddatasets", "GetAssignedDatasets",

    "/getmapsetsforingest", "GetMapsetsForIngest",
    "/addingestmapset", "AddIngestMapset",
    "/deleteingestmapset", "DisableIngestMapset",

    "/mapsets/getmapsetsall", "GetMapsets",
    "/mapsets/create", "CreateMapset",
    "/mapsets/update", "UpdateMapset",
    "/mapsets/delete", "DeleteMapset",

    "/getlanguages", "GetLanguages",
    "/geti18n", "GetI18n",

    # "/(.+)/(.+)", "EsApp",
    # "/(.+)/", "EsApp",
    "/", "EsApp")

app = web.application(urls, globals(), autoreload=True)
application = app.wsgifunc()


# session = web.session.Session(app, web.session.DiskStore('../logs/mstmp/webpySessions'))


class EsApp(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # return web.ctx
        getparams = web.input()
        if hasattr(getparams, "lang"):
            # print getparams['lang']
            # functions.setUserSetting('default_language', getparams['lang'])
            # es_constants.es2globals['default_language'] = getparams['lang']
            if hasattr(getparams, "usr"):
                crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
                user_info = {'userid': getparams['usr'],
                             'prefered_language': getparams['lang']}
                crud_db.update('users', user_info)

        # render = web.template.render(es_constants.es2globals['base_dir']+'/apps/gui/esapp')
        render = web.template.render(es_constants.es2globals['base_dir'] + '/apps/gui/esapp/build/production/esapp')

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


class Register(object):
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
                'userlevel': 2,
                'email': getparams['email']
            }

            if self.crud_db.create('users', user):
                createstatus = '{"success":"true", "message":"User created!"}'
        else:
            createstatus = '{"success":"false", "message":"No user data given!"}'

        return createstatus


class Users(object):
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
                        'email': row['email'],
                        'prefered_language': row['prefered_language']
                    }
                    users_dict_all.append(user_info)

                user_info_json = json.dumps(users_dict_all,
                                            ensure_ascii=False,
                                            # encoding='utf-8',
                                            sort_keys=False,
                                            indent=4,
                                            separators=(', ', ': '))

                users_json = '{"success":true, "users":' + user_info_json + '}'
            else:
                users_json = '{"success":true, "message":"No users defined in the DB!"}'

        except:
            users_json = '{"success":false, "error":"Error reading users data from DB!"}'

        return users_json


class Login(object):
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
                            'userlevel': row_dict['userlevel'],
                            'email': row_dict['email'],
                            'prefered_language': row_dict['prefered_language']
                            # 'timestamp': row_dict['timestamp']
                        }

                    user_info_json = json.dumps(user_info,
                                                ensure_ascii=False,
                                                # encoding='utf-8',
                                                sort_keys=True,
                                                indent=4,
                                                separators=(', ', ': '))
                    # print user_info_json
                    login_json = '{"success":true, "user":' + user_info_json + '}'
                    # print login_json
                else:
                    login_json = '{"success":false, "error":"Username or password incorrect!"}'

            except:
                login_json = '{"success":false, "error":"Error reading login data in DB!"}'
        else:
            login_json = '{"success":false, "error":"No user name given!"}'

        return login_json


class checkECASlogin(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        import pycurl
        import io
        import xml.etree.ElementTree as ET
        userInfoDict = {}

        params = web.input()

        ECAS_ticketPage = 'https://webgate.ec.europa.eu/cas/laxValidate?ticket=' + str(
            params.ticket) + '&userDetails=true&service=' + str(params.strCall)

        try:
            c = pycurl.Curl()
            # c.setopt(c.VERBOSE, True)
            c.setopt(pycurl.URL, ECAS_ticketPage)
            b = io.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.perform()

            c.close()
            data = b.getvalue()
            root = ET.fromstring(data)

            arrayValues = ['{https://ecas.ec.europa.eu/cas/schemas}uid',
                           '{https://ecas.ec.europa.eu/cas/schemas}user',
                           '{https://ecas.ec.europa.eu/cas/schemas}moniker',
                           '{https://ecas.ec.europa.eu/cas/schemas}lastName',
                           '{https://ecas.ec.europa.eu/cas/schemas}firstName',
                           '{https://ecas.ec.europa.eu/cas/schemas}domain',
                           '{https://ecas.ec.europa.eu/cas/schemas}email',
                           '{https://ecas.ec.europa.eu/cas/schemas}departmentNumber']
            for xx in range(0, len(arrayValues)):
                strNode = arrayValues[xx]
                strNodeValue = strNode[strNode.index("}") + 1:]
                strValue = ''
                for node in root.iter(arrayValues[xx]):
                    try:
                        strValue = node.text
                    except:
                        strValue = ''
                userInfoDict[strNodeValue] = strValue

        except:
            exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
            # Exit the script and print an error telling what happened.
            logger.error("checkECASlogin: Error!\n -> {}".format(exceptionvalue))
            login_json = '{"success":false, "error":"ECAS login error!"}'

        if 'uid' not in userInfoDict:
            login_json = '{"success":false, "error":"No user name given!"}'
        else:
            try:
                user_info = {
                    'userid': userInfoDict.get('uid'),
                    'username': userInfoDict.get('firstName', 'User name') + ' ' + userInfoDict.get('lastName',
                                                                                                    'User lastname'),
                    'password': userInfoDict.get('uid'),
                    'userlevel': 2,
                    'email': userInfoDict.get('email', 'User email'),
                    'prefered_language': 'eng'
                }

                userFromDB = querydb.checkUser(user_info)
                if userFromDB is None:
                    userFromDB = querydb.checkUser(user_info)

                message = ',"message":"User exists!"'
                if userFromDB is None:
                    if self.crud_db.create('users', user_info):
                        message = ',"message":"User created!"'
                else:
                    for row in userFromDB:
                        user_info['userlevel'] = row['userlevel']

                user_info_json = json.dumps(user_info,
                                            ensure_ascii=False,
                                            # encoding='utf-8',
                                            sort_keys=True,
                                            indent=4,
                                            separators=(', ', ': '))

                login_json = '{"success":true, "user":' + user_info_json + message + '}'
            except:
                login_json = '{"success":false, "error":"Error reading login data!"}'

        return login_json


class GetLogos(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # getparams = web.input()
        logos_json = webpy_esapp_helpers.GetLogos()
        return logos_json


class ImportLogo(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # getparams = json.loads(web.data())  # get PUT data
        getparams = web.input()  # get POST data

        logosfiledir = es_constants.es2globals['estation2_logos_dir']
        if 'logofilename' in getparams:  # to check if the file-object is created
            try:
                filepath = getparams.logofilename.replace('\\',
                                                          '/')  # replaces the windows-style slashes with linux ones.
                filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)

                # Separate base from extension
                base, extension = os.path.splitext(filename)

                # Initial new name
                new_name = os.path.join(logosfiledir, filename).encode('utf-8').decode()
                new_name_final = logosfiledir + '/' + filename

                if not os.path.exists(new_name):  # file does not exist in <layerfiledir>
                    fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                    fout.write(getparams.logofile)  # .read()  writes the uploaded file to the newly created file.
                    fout.close()  # closes the file, upload complete.
                else:  # file exists in <logosfiledir>
                    ii = 1
                    while True:
                        new_name = os.path.join(logosfiledir, base + "_" + str(ii) + extension).encode('utf-8').decode()
                        new_name_final = os.path.join(logosfiledir, base + "_" + str(ii) + extension)
                        if not os.path.exists(new_name):
                            fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                            fout.write(
                                getparams.logofile)  # .read()  writes the uploaded file to the newly created file.
                            fout.close()  # closes the file, upload complete.
                            break
                        ii += 1

                # splits the and chooses the last part (the filename with extension)
                finalfilename = new_name_final.split('/')[-1]
                success = True
            except:
                success = False
        else:
            success = False

        if success:
            status = '{"success":"true", "filename":"' + finalfilename + '","message":"Logo imported!"}'
        else:
            status = '{"success":false, "message":"An error occured while importing the logo!"}'

        return status


class DeleteLogo(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'logo' in getparams:
            logo = {
                'logo_id': getparams['logo']['logo_id'],
            }

            if self.crud_db.delete('logos', **logo):
                status = '{"success":"true", "message":"Logo deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the logo!"}'

        else:
            status = '{"success":false, "message":"No logo info passed!"}'

        return status


class CreateLogo(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'logo' in getparams:
            logo = {
                # 'logo_id': getparams['logo']['logo_id'],
                'logo_filename': getparams['logo']['logo_filename'],
                'logo_description': getparams['logo']['logo_description'],
                'active': getparams['logo']['active'],
                'deletable': functions.str_to_bool(getparams['logo']['deletable']),
                'defined_by': getparams['logo']['defined_by'],
                'isdefault': functions.str_to_bool(getparams['logo']['isdefault']),
                'orderindex_defaults': getparams['logo']['orderindex_defaults']
            }

            if self.crud_db.create('logos', logo):
                status = '{"success":"true", "message":"Logo created!"}'
            else:
                status = '{"success":false, "message":"An error occured while creating the new logo!"}'

        else:
            status = '{"success":false, "message":"No logo info passed!"}'

        return status


class UpdateLogo(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'logo' in getparams:
            logo = {
                'logo_id': getparams['logo']['logo_id'],
                'logo_filename': getparams['logo']['logo_filename'],
                'logo_description': getparams['logo']['logo_description'],
                'active': functions.str_to_bool(getparams['logo']['active']),
                'deletable': functions.str_to_bool(getparams['logo']['deletable']),
                'defined_by': getparams['logo']['defined_by'],
                'isdefault': functions.str_to_bool(getparams['logo']['isdefault']),
                'orderindex_defaults': getparams['logo']['orderindex_defaults']
            }

            if self.crud_db.update('logos', logo):
                updatestatus = '{"success":"true", "message":"Logo updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the logo!"}'

        else:
            updatestatus = '{"success":false, "message":"No logo info passed!"}'

        return updatestatus


class GetAssignedDatasets(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        if hasattr(params, "legendid") and params['legendid'] != '':
            assigneddatasets_json = webpy_esapp_helpers.GetAssignedDatasets(params['legendid'])
        else:
            assigneddatasets_json = '{"success":false, "error":"No Legend ID passed!"}'

        return assigneddatasets_json


class UnassignLegend(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.UnassignLegend(params)


class AssignLegends(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.AssignLegends(params)


class copyLegend(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.copyLegend(params)


class DeleteLegend(object):
    def __init__(self):
        self.lang = "eng"

    def DELETE(self):
        params = json.loads(web.data())
        return webpy_esapp_helpers.DeleteLegend(params)


class SaveLegend(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.SaveLegend(params)


class ExportLegend(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        filename = webpy_esapp_helpers.ExportLegend(params)
        web.header('Content-Type', 'application/force-download')  # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition',
                   'attachment; filename=' + os.path.basename(filename))  # force browser to show "Save as" dialog.
        f = open(filename, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()
        os.remove(filename)


class GetLegends(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        return webpy_esapp_helpers.GetLegends()


class GetLegendClasses(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "legendid") and getparams['legendid'] != '':
            legendclasses_json = webpy_esapp_helpers.GetLegendClasses(getparams['legendid'])
        else:
            legendclasses_json = '{"success":false, "error":"No Legend ID passed!"}'

        return legendclasses_json


class GetInstallationType(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # return web.ctx
        getparams = web.input()
        systemsettings = functions.getSystemSettings()

        typeinstallation_json = '{"success":"true", "typeinstallation":"' + systemsettings[
            'type_installation'].lower() + \
                                '", "role":"' + systemsettings['role'].lower() + '", "mode":"' + systemsettings[
                                    'mode'].lower() + '"}'

        return typeinstallation_json


class GetTimeseries(object):

    def __init__(self):
        self.lang = "eng"
        # self.out_queue = Queue()

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.getGraphTimeseries(params)


class TimeseriesProducts(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        force = False
        if 'force' in getparams:
            force = getparams.force
        return webpy_esapp_helpers.getTimeseriesProducts(force)


class getUserWorkspaces(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getUserWorkspaces(params)


class getRefWorkspaces(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getRefWorkspaces(params)


class exportWorkspaces(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        workspaces_dict_all = []

        # print (params)
        if hasattr(params, "workspaces"):
            # print (params['workspaces'])
            workspaces = json.loads(params['workspaces'])

            # print (isinstance(workspaces, dict))
            # print (type(workspaces))
            for workspace in workspaces:
                workspace['maps'] = webpy_esapp_helpers.getWorkspaceMaps(workspace['workspaceid'], workspace['userid'],
                                                                         True)
                workspace['graphs'] = webpy_esapp_helpers.getWorkspaceGraphs(workspace['workspaceid'],
                                                                             workspace['userid'], True)
                workspace['userid'] = ''

                workspaces_dict_all.append(workspace)

            workspaces_json = json.dumps(workspaces_dict_all,
                                         ensure_ascii=True,
                                         # encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            workspaces_json = '{"workspaces":' + workspaces_json + '}'
            # print (workspaces_json)

            filename = 'exported_workspaces.json'
            with open(es_constants.es2globals['base_tmp_dir'] + filename, 'w+') as f:
                f.write(workspaces_json)
            f.close()

            web.header('Content-Type', 'text/html')  # 'application/x-compressed'  'application/force-download'
            web.header('Content-transfer-encoding', 'binary')
            web.header('Content-Disposition',
                       'attachment; filename=' + filename)  # force browser to show "Save as" dialog.
            f = open(es_constants.es2globals['base_tmp_dir'] + filename, 'rb')
            while 1:
                buf = f.read(1024 * 8)
                if not buf:
                    break
                yield buf
            f.close()


class importWorkspaces(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.importWorkspaces(params)


class getWorkspaceMapsAndGraphs(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.getWorkspaceMapsAndGraphs(params)


class SaveWorkspacePin(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.saveWorkspacePin(params)


class SaveWorkspaceName(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.saveWorkspaceName(params)


class saveWorkspaceInDefaultWS(object):
    def __init__(self):
        self.lang = "eng"

    def PUT(self):
        # params = web.input()
        params = json.loads(web.data())  # get PUT data
        return webpy_esapp_helpers.saveWorkspaceInDefaultWS(params)


class SaveWorkspace(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.saveWorkspace(params)


class DeleteWorkspace(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        params = json.loads(web.data())  # get PUT data
        status = '{"success":false, "message":"An error occured while deleting the Workspace!"}'

        if 'workspaceid' in params:

            workspacePK = {
                'userid': params['userid'],
                'workspaceid': params['workspaceid']
            }

            if self.crud_db.delete('user_workspaces', **workspacePK):
                status = '{"success":"true", "message":"Workspace deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the Workspace!"}'

        else:
            status = '{"success":false, "message":"No Workspace info passed!"}'

        return status


class GetMapTemplates(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getMapTemplates(params)


class DeleteMapTemplate(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        params = json.loads(web.data())  # get PUT data
        status = '{"success":false, "message":"An error occured while deleting the Map Template!"}'

        if 'usermaptemplate' in params:
            defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['usermaptemplate']['userid'])
            if not defaultworkspaceid:
                return status

            maptemplatePK = {
                'userid': params['usermaptemplate']['userid'],
                'workspaceid': defaultworkspaceid,
                'map_tpl_id': params['usermaptemplate']['map_tpl_id']
            }

            if self.crud_db.delete('user_map_templates', **maptemplatePK):
                status = '{"success":"true", "message":"Map Template deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the Map Template!"}'

        else:
            status = '{"success":false, "message":"No Map Template info passed!"}'

        return status


class __DeleteMapTemplate(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'usermaptemplate' in getparams:  # hasattr(getparams, "layer")
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


class SaveMapTemplate(object):
    def __init__(self):
        self.lang = "eng"
        # self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.saveMapTemplate(params)


class __SaveMapTemplate(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = web.input()
        # getparams = json.loads(web.data())  # get PUT data

        createstatus = '{"success":false, "message":"An error occured while saving the Map Template!"}'

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
                'outmask': getparams['outmask'],
                'outmaskfeature': getparams['outmaskFeature'],
                'auto_open': getparams['auto_open'],
                'zoomextent': getparams['zoomextent'],
                'mapsize': getparams['mapsize'],
                'mapcenter': getparams['mapcenter']
            }

            # print getparams
            if getparams['newtemplate'] == 'true':
                if self.crud_db.create('map_templates', mapTemplate):
                    createstatus = '{"success":true, "message":"Map Template created!"}'
                else:
                    createstatus = '{"success":false, "message":"Error saving the Map Template! Name already exists!"}'
            else:
                if self.crud_db.update('map_templates', mapTemplate):
                    createstatus = '{"success":true, "message":"Map Template updated!"}'

        else:
            createstatus = '{"success":false, "message":"No Map Template data given!"}'

        return createstatus


class getGraphTemplates(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getGraphTemplates(params)


class DeleteGraphTemplate(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        params = json.loads(web.data())  # get PUT data
        status = '{"success":false, "message":"An error occured while deleting the Graph template!"}'

        if 'usergraphtemplate' in params:
            defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['usergraphtemplate']['userid'])
            if not defaultworkspaceid:
                return status

            graphtemplatePK = {
                'userid': params['usergraphtemplate']['userid'],
                'workspaceid': defaultworkspaceid,
                'graph_tpl_id': params['usergraphtemplate']['graph_tpl_id'],
            }

            if self.crud_db.delete('user_graph_templates', **graphtemplatePK):
                status = '{"success":"true", "message":"Graph template deleted!"}'
            else:
                status = '{"success":false, "message":"An error occured while deleting the Graph template!"}'

        else:
            status = '{"success":false, "message":"No Graph template info passed!"}'

        return status


class saveGraphTemplate(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.saveGraphTemplate(params)


class UpdateYaxe(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        yaxe = web.input()
        if 'id' in yaxe and 'userid' in yaxe and yaxe['userid'] != '':
            try:
                if querydb.update_yaxe(yaxe):
                    yaxeproperties_json = '{"success":true, "message":"Yaxe updated"}'
                else:
                    yaxeproperties_json = '{"success":false, "error":"Error saving the Yaxe properties in the database!"}'
            except:
                yaxeproperties_json = '{"success":false, "error":"Error saving the Yaxe properties in the database!"}'
        else:
            yaxeproperties_json = '{"success":false, "error":"No Yaxe properties given!"}'

        return yaxeproperties_json


class GetTimeseriesDrawProperties(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getTimeseriesDrawProperties(params)


class CreateTimeseriesDrawProperties(object):
    def __init__(self):
        self.lang = "eng"
        # self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        params = json.loads(web.data())  # get PUT data
        return webpy_esapp_helpers.createTimeseriesDrawProperties(params)


class UpdateTimeseriesDrawProperties(object):
    def __init__(self):
        self.lang = "eng"
        # self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        params = web.input()
        return webpy_esapp_helpers.updateTimeseriesDrawProperties(params)


class GetGraphProperties(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        return webpy_esapp_helpers.getGraphProperties(params)


class UpdateGraphProperties(object):
    def __init__(self):
        self.lang = "eng"
        # self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def PUT(self):
        params = json.loads(web.data())  # get PUT data
        extraparams = web.input()  # get userid, graph_tpl_id, graph_tpl_name and isTemplate parameters from GET data
        # params['graphproperty']['userid'] = extraparams.userid
        # params['graphproperty']['graph_tpl_name'] = extraparams.graph_tpl_name
        return webpy_esapp_helpers.updateGraphProperties(params, extraparams)


class GetHelpFile(object):
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

        web.header('Content-Type',
                   contenttype)  # 'text/html'   'application/x-compressed'  'application/force-download' 'application/pdf'
        web.header('Content-transfer-encoding', 'binary')
        # web.header('Content-Disposition', 'attachment; filename=' + getparams['file'])  # force browser to autodownload or show "Save as" dialog.
        web.header('Content-Disposition', content_disposition_type + ' filename= "' + getparams[
            'file'] + '"')  # force browser to show "Save as" dialog.

        f = open(docfile, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()


class GetHelp(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        docs_dir = es_constants.es2globals['docs_dir']
        if not os.path.isdir(es_constants.es2globals['docs_dir']):
            docs_dir = es_constants.es2globals['base_dir'] + '/apps/help/userdocs/'

        if getparams['lang'] == '':
            getparams['lang'] = es_constants.es2globals['default_language']

        if getparams['lang'] == 'eng':
            lang_dir = 'EN/'
        elif getparams['lang'] == 'fra':
            lang_dir = 'FR/'
        elif getparams['lang'] == 'por':
            lang_dir = 'POR/'
        else:
            lang_dir = 'EN/'

        jsonfile = docs_dir + lang_dir + getparams['type'] + '_data_' + getparams['lang'] + '.json'

        # print jsonfile

        if os.path.isfile(jsonfile):
            jsonfile = open(jsonfile, 'r')
            filecontent_json = jsonfile.read()
            jsonfile.close()
        else:
            docs_dir = es_constants.es2globals['base_dir'] + '/apps/help/userdocs/'
            jsonfile = docs_dir + lang_dir + getparams['type'] + '_data_' + getparams['lang'] + '.json'
            if os.path.isfile(jsonfile):
                jsonfile = open(jsonfile, 'r')
                filecontent_json = jsonfile.read()
                jsonfile.close()
            else:
                filecontent_json = ''

        return filecontent_json


class GetRequest(object):
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

            request = requests.create_request(productcode=productcode,
                                              version=version,
                                              mapsetcode=mapsetcode,
                                              subproductcode=subproductcode,
                                              dekad_frequency=int(getparams['dekad_frequency']),
                                              daily_frequency=int(getparams['daily_frequency']),
                                              high_frequency=int(getparams['high_frequency'])
                                              )
            request_json = json.dumps(request,
                                      ensure_ascii=False,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

            request_json = '{"success":"true", "request":' + request_json + '}'
        else:
            request_json = '{"success":false, "error":"No parameters passed for request!"}'

        return request_json


class getRequestsList(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        response_json = webpy_esapp_helpers.getRunningRequestJobs()
        return response_json


class runPauseRequest(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "requestid") and getparams['requestid'] != '':
            requestid = getparams['requestid']
            if getparams['task'] == 'pause':
                response_json = webpy_esapp_helpers.pauseRequestJob(requestid)
            else:
                response_json = webpy_esapp_helpers.restartRequestJob(requestid)
        else:
            response = {"success": False, "error": "No request info passed!"}
            response_json = json.dumps(response,
                                       ensure_ascii=False,
                                       sort_keys=True,
                                       indent=4,
                                       separators=(', ', ': '))

        return response_json


class createRequestJob(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "productcode") and getparams['productcode'] != '':
            response_json = webpy_esapp_helpers.createRequestJob(getparams)
        else:
            response_json = '{"success":false, "error":"No request info passed!"}'

        return response_json


class deleteRequestJob(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "requestid") and getparams['requestid'] != '':
            requestid = getparams['requestid']
            response_json = webpy_esapp_helpers.deleteRequestJob(requestid)
        else:
            response_json = '{"success":false, "error":"No request info passed!"}'

        return response_json


class SaveRequest(object):
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
                requestfilename = getparams['productcode'] + '_' + getparams['version'] + '_' + getparams[
                    'mapsetcode'] + '_all_enabled_datasets'
            elif getparams['level'] == 'dataset':
                productcode = getparams['productcode']
                version = getparams['version']
                mapsetcode = getparams['mapsetcode']
                subproductcode = getparams['subproductcode']
                requestfilename = getparams['productcode'] + '_' + getparams['version'] + '_' + getparams[
                    'mapsetcode'] + '_' + getparams['subproductcode']

            request = requests.create_request(productcode,
                                              version,
                                              mapsetcode=mapsetcode,
                                              subproductcode=subproductcode,
                                              dekad_frequency=int(getparams['dekad_frequency']),
                                              daily_frequency=int(getparams['daily_frequency']),
                                              high_frequency=int(getparams['high_frequency'])
                                              )
            request_json = json.dumps(request,
                                      ensure_ascii=False,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M')

            requestfilename = requestfilename + '_' + st + '.req'
            with open(es_constants.es2globals['requests_dir'] + requestfilename, 'w+') as f:
                f.write(request_json)
            f.close()

            web.header('Content-Type', 'text/html')  # 'application/x-compressed'  'application/force-download'
            web.header('Content-transfer-encoding', 'binary')
            web.header('Content-Disposition',
                       'attachment; filename=' + requestfilename)  # force browser to show "Save as" dialog.
            f = open(es_constants.es2globals['requests_dir'] + requestfilename, 'rb')
            while 1:
                buf = f.read(1024 * 8)
                if not buf:
                    break
                yield buf
            f.close()


class GetProjections(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        projections_dict_all = []
        projections = querydb.get_projections()

        if hasattr(projections, "__len__") and projections.__len__() > 0:
            for row in projections:
                row_dict = functions.row2dict(row)

                projections_dict_all.append(row_dict)

                projections_json = json.dumps(projections_dict_all,
                                              ensure_ascii=False,
                                              # encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

                projections_json = '{"success":"true", "total":' \
                                   + str(projections.__len__()) \
                                   + ',"projections":' + projections_json + '}'

        else:
            projections_json = '{"success":false, "error":"No Projections defined!"}'

        return projections_json


class GetResolutions(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        resolutions_dict_all = []
        resolutions = querydb.get_resolutions()

        if hasattr(resolutions, "__len__") and resolutions.__len__() > 0:
            for row in resolutions:
                row_dict = functions.row2dict(row)

                resolutions_dict_all.append(row_dict)

                resolutions_json = json.dumps(resolutions_dict_all,
                                              ensure_ascii=False,
                                              # encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

                resolutions_json = '{"success":"true", "total":' \
                                   + str(resolutions.__len__()) \
                                   + ',"resolutions":' + resolutions_json + '}'

        else:
            resolutions_json = '{"success":false, "error":"No resolutions defined!"}'

        return resolutions_json


class GetPredefinedBboxes(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        bboxes_dict_all = []
        bboxes = querydb.get_predefined_bboxes()

        if hasattr(bboxes, "__len__") and bboxes.__len__() > 0:
            for row in bboxes:
                row_dict = functions.row2dict(row)

                bboxes_dict_all.append(row_dict)

                bboxes_json = json.dumps(bboxes_dict_all,
                                         ensure_ascii=False,
                                         # encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

                bboxes_json = '{"success":"true", "total":' \
                              + str(bboxes.__len__()) \
                              + ',"bboxes":' + bboxes_json + '}'

        else:
            bboxes_json = '{"success":false, "error":"No predefined bounding boxes defined!"}'

        return bboxes_json


class GetCategories(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        params = web.input()
        allrecs = False
        if params['all'] == 'true':
            allrecs = True
        categories_dict_all = []
        categories = querydb.get_categories(allrecs=allrecs)

        if hasattr(categories, "__len__") and categories.__len__() > 0:
            for row in categories:
                row_dict = functions.row2dict(row)
                categories_dict = {'category_id': row_dict['category_id'],
                                   'descriptive_name': row_dict['descriptive_name']}

                categories_dict_all.append(categories_dict)

            categories_json = json.dumps(categories_dict_all,
                                         ensure_ascii=False,
                                         # encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            categories_json = '{"success":"true", "total":' \
                              + str(categories.__len__()) \
                              + ',"categories":' + categories_json + '}'

        else:
            categories_json = '{"success":false, "error":"No Categories defined!"}'

        return categories_json


class GetFrequencies(object):
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
                                          # encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

            frequencies_json = '{"success":"true", "total":' \
                               + str(frequencies.__len__()) \
                               + ',"frequencies":' + frequencies_json + '}'

        else:
            frequencies_json = '{"success":false, "error":"No Frequencies defined!"}'

        return frequencies_json


class GetDateFormats(object):
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
                                          # encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

            dateformats_json = '{"success":"true", "total":' \
                               + str(dateformats.__len__()) \
                               + ',"dateformats":' + dateformats_json + '}'

        else:
            dateformats_json = '{"success":false, "error":"No Date Formats defined!"}'

        return dateformats_json


class GetDataTypes(object):
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
                                        # encoding='utf-8',
                                        sort_keys=True,
                                        indent=4,
                                        separators=(', ', ': '))

            datatypes_json = '{"success":"true", "total":' \
                             + str(datatypes.__len__()) \
                             + ',"datatypes":' + datatypes_json + '}'

        else:
            datatypes_json = '{"success":false, "error":"No Data Types defined!"}'

        return datatypes_json


class AssignInternetSource(object):
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
            'defined_by': getparams['defined_by'],
            'type': 'INTERNET'
        }

        if self.crud_db.create('product_acquisition_data_source', productinfo):
            insertstatus = '{"success":"true", "message":"Internet source assigned!"}'
        else:
            insertstatus = '{"success":false, "message":"An error occured while assigning the internet source!"}'

        return insertstatus


class AssignEumetcastSource(object):
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
            'defined_by': getparams['defined_by'],
            'type': 'EUMETCAST'
        }

        if self.crud_db.create('product_acquisition_data_source', productinfo):
            insertstatus = '{"success":"true", "message":"Internet source assigned!"}'
        else:
            insertstatus = '{"success":false, "message":"An error occured while assigning the internet source!"}'

        return insertstatus


class UnassignProductDataSource(object):
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


class GetEumetcastSources(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        eumetcastsources_dict_all = []
        eumetcastsources = querydb.get_eumetcastsources()

        if hasattr(eumetcastsources, "__len__") and eumetcastsources.__len__() > 0:
            for row in eumetcastsources:
                row_dict = functions.row2dict(row)
                eumetcastsource = {'eumetcast_id': row_dict['eumetcast_id'],
                                   'orig_eumetcast_id': row_dict['eumetcast_id'],
                                   'collection_name': row_dict['collection_name'],
                                   'filter_expression_jrc': row_dict['filter_expression_jrc'],
                                   'description': row_dict['description'],
                                   'typical_file_name': row_dict['typical_file_name'],
                                   'frequency': row_dict['frequency'],
                                   'keywords_theme': row_dict['keywords_theme'],
                                   'keywords_societal_benefit_area': row_dict['keywords_societal_benefit_area'],
                                   'defined_by': row_dict['defined_by'],
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
                                               # encoding='utf-8',
                                               sort_keys=True,
                                               indent=4,
                                               separators=(', ', ': '))

            eumetcastsources_json = '{"success":"true", "total":' \
                                    + str(eumetcastsources.__len__()) \
                                    + ',"eumetcastsources":' + eumetcastsources_json + '}'

        else:
            eumetcastsources_json = '{"success":false, "error":"No Internet Sources defined!"}'

        return eumetcastsources_json


class UpdateEumetcastSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'eumetcastsources' in getparams:

            prod_id_position = None
            if getparams['eumetcastsources']['prod_id_position'] != None:
                try:
                    prod_id_position = int(getparams['eumetcastsources']['prod_id_position'])
                except ValueError:
                    prod_id_position = None

            prod_id_length = None
            if getparams['eumetcastsources']['prod_id_length'] != None:
                try:
                    prod_id_length = int(getparams['eumetcastsources']['prod_id_length'])
                except ValueError:
                    prod_id_length = None

            area_length = None
            if getparams['eumetcastsources']['area_length'] != None:
                try:
                    area_length = int(getparams['eumetcastsources']['area_length'])
                except ValueError:
                    area_length = None

            release_length = None
            if getparams['eumetcastsources']['release_length'] != None:
                try:
                    release_length = int(getparams['eumetcastsources']['release_length'])
                except ValueError:
                    release_length = None

            eumetcastsourceinfo = {'eumetcast_id': getparams['eumetcastsources']['eumetcast_id'],
                                   'filter_expression_jrc': getparams['eumetcastsources']['filter_expression_jrc'],
                                   'description': getparams['eumetcastsources']['description'],
                                   'typical_file_name': getparams['eumetcastsources']['typical_file_name'],
                                   'frequency': getparams['eumetcastsources']['frequency'],
                                   'datasource_descr_id': getparams['eumetcastsources']['eumetcast_id'],
                                   'defined_by': getparams['eumetcastsources']['defined_by']
                                   }

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

            if getparams['eumetcastsources']['eumetcast_id'] != getparams['eumetcastsources']['orig_eumetcast_id']:
                eumetcastsourceinfo['orig_eumetcast_id'] = getparams['eumetcastsources']['orig_eumetcast_id']

                # if self.crud_db.update('datasource_description', datasourcedescrinfo):
                if querydb.update_eumetcast_source_info(eumetcastsourceinfo, datasourcedescrinfo):
                    updatestatus = '{"success":"true", "message":"Eumetcast data source and description updated!"}'
                else:
                    updatestatus = '{"success":false, "message":"An error occured while updating the Eumetcast data source!"}'
                # else:
                #     updatestatus = '{"success":false, "message":"An error occured while updating the Eumetcast data source description!"}'

            else:
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


class CreateEumetcastSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'eumetcastsources' in getparams:

            prod_id_position = None
            if getparams['eumetcastsources']['prod_id_position'] != None:
                try:
                    prod_id_position = int(getparams['eumetcastsources']['prod_id_position'])
                except ValueError:
                    prod_id_position = None

            prod_id_length = None
            if getparams['eumetcastsources']['prod_id_length'] != None:
                try:
                    prod_id_length = int(getparams['eumetcastsources']['prod_id_length'])
                except ValueError:
                    prod_id_length = None

            area_length = None
            if getparams['eumetcastsources']['area_length'] != None:
                try:
                    area_length = int(getparams['eumetcastsources']['area_length'])
                except ValueError:
                    area_length = None

            release_length = None
            if getparams['eumetcastsources']['release_length'] != None:
                try:
                    release_length = int(getparams['eumetcastsources']['release_length'])
                except ValueError:
                    release_length = None

            eumetcastsourceinfo = {'eumetcast_id': getparams['eumetcastsources']['eumetcast_id'],
                                   'filter_expression_jrc': getparams['eumetcastsources']['filter_expression_jrc'],
                                   'description': getparams['eumetcastsources']['description'],
                                   'typical_file_name': getparams['eumetcastsources']['typical_file_name'],
                                   'frequency': getparams['eumetcastsources']['frequency'],
                                   'datasource_descr_id': getparams['eumetcastsources']['eumetcast_id'],
                                   'defined_by': getparams['eumetcastsources']['defined_by'],
                                   # 'update_datetime': getparams['internetsources']['update_datetime']
                                   }

            datasourcedescrinfo = {'datasource_descr_id': getparams['eumetcastsources']['internet_id'],
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

            if self.crud_db.create('eumetcast_source', eumetcastsourceinfo):
                if self.crud_db.create('datasource_description', datasourcedescrinfo):
                    createstatus = '{"success":"true", "message":"Eumetcast data source and description created!"}'
                else:
                    createstatus = '{"success":"true", "message":"Eumetcast data source created!"}'
            else:
                createstatus = '{"success":false, "message":"An error occured while creating the Eumetcast data source!"}'

        else:
            createstatus = '{"success":false, "message":"No Eumetcast data source passed!"}'

        return createstatus


class DeleteEumetcastSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'eumetcastsources' in getparams:

            eumetcastsourceinfo = {'eumetcast_id': getparams['eumetcastsources']['eumetcast_id']}
            datasourcedescrinfo = {'datasource_descr_id': getparams['eumetcastsources']['eumetcast_id']}

            if self.crud_db.delete('eumetcast_source', **eumetcastsourceinfo):
                if self.crud_db.delete('datasource_description', **datasourcedescrinfo):
                    deletetatus = '{"success":"true", "message":"Eumetcast data source and description deleted!"}'
                else:
                    deletetatus = '{"success":"true", "message":"Eumetcast data source deleted!"}'
            else:
                deletetatus = '{"success":false, "message":"An error occured while deleting the Eumetcast data source!"}'

        else:
            deletetatus = '{"success":false, "message":"No Eumetcast data source passed!"}'

        return deletetatus


class GetInternetSources(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        internetsources_dict_all = []
        internetsources = querydb.get_internetsources()

        if hasattr(internetsources, "__len__") and internetsources.__len__() > 0:
            for row in internetsources:
                row_dict = functions.row2dict(row)

                # updatedate = row_dict['update_datetime'][0:16]     # datetime.strptime(row_dict['update_datetime'], "%Y-%m-%d  %H:%M")

                startdate = None
                if row_dict['start_date'] != '':
                    try:
                        startdate = int(row_dict['start_date'])
                    except ValueError:
                        startdate = None

                enddate = None
                if row_dict['end_date'] != '':
                    try:
                        enddate = int(row_dict['end_date'])
                    except ValueError:
                        enddate = None

                prod_id_position = None
                if row_dict['prod_id_position'] != '':
                    try:
                        prod_id_position = int(row_dict['prod_id_position'])
                    except ValueError:
                        prod_id_position = None

                prod_id_length = None
                if row_dict['prod_id_length'] != '':
                    try:
                        prod_id_length = int(row_dict['prod_id_length'])
                    except ValueError:
                        prod_id_length = None

                area_length = None
                if row_dict['area_length'] != '':
                    try:
                        area_length = int(row_dict['area_length'])
                    except ValueError:
                        area_length = None

                release_length = None
                if row_dict['release_length'] != '':
                    try:
                        release_length = int(row_dict['release_length'])
                    except ValueError:
                        release_length = None

                internetsource = {'internet_id': row_dict['internet_id'],
                                  'orig_internet_id': row_dict['internet_id'],
                                  'defined_by': row_dict['defined_by'],
                                  'descriptive_name': row_dict['descriptive_name'],
                                  'description': row_dict['description'],
                                  'modified_by': row_dict['modified_by'],
                                  'update_datetime': row_dict['update_datetime'][0:16],
                                  'url': row_dict['url'],
                                  'user_name': row_dict['user_name'],
                                  'password': row_dict['password'],
                                  'type': row_dict['type'],
                                  'include_files_expression': row_dict['include_files_expression'],
                                  'files_filter_expression': row_dict['files_filter_expression'],
                                  'status': row_dict['status'],
                                  'pull_frequency': row_dict['pull_frequency'],
                                  'frequency_id': row_dict['frequency_id'],
                                  'start_date': startdate,
                                  'end_date': enddate,
                                  'https_params': row_dict['https_params'],
                                  'datasource_descr_id': row_dict['datasource_descr_id'],
                                  'format_type': row_dict['format_type'],
                                  'file_extension': row_dict['file_extension'],
                                  'delimiter': row_dict['delimiter'],
                                  'date_format': row_dict['date_format'],
                                  'date_position': row_dict['date_position'],
                                  'product_identifier': row_dict['product_identifier'],
                                  'prod_id_position': prod_id_position,
                                  'prod_id_length': prod_id_length,
                                  'area_type': row_dict['area_type'],
                                  'area_position': row_dict['area_position'],
                                  'area_length': area_length,
                                  'preproc_type': row_dict['preproc_type'],
                                  'product_release': row_dict['product_release'],
                                  'release_position': row_dict['release_position'],
                                  'release_length': release_length,
                                  'native_mapset': row_dict['native_mapset']}

                internetsources_dict_all.append(internetsource)

            internetsources_json = json.dumps(internetsources_dict_all,
                                              ensure_ascii=False,
                                              # encoding='utf-8',
                                              sort_keys=True,
                                              indent=4,
                                              separators=(', ', ': '))

            internetsources_json = '{"success":"true", "total":' \
                                   + str(internetsources.__len__()) \
                                   + ',"internetsources":' + internetsources_json + '}'

        else:
            internetsources_json = '{"success":false, "error":"No Internet Sources defined!"}'

        return internetsources_json


class UpdateInternetSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'internetsources' in getparams:

            startdate = None
            if getparams['internetsources']['start_date'] != None:
                try:
                    startdate = int(getparams['internetsources']['start_date'])
                except ValueError:
                    startdate = None

            enddate = None
            if getparams['internetsources']['end_date'] != None:
                try:
                    enddate = int(getparams['internetsources']['end_date'])
                except ValueError:
                    enddate = None

            prod_id_position = None
            if getparams['internetsources']['prod_id_position'] != None:
                try:
                    prod_id_position = int(getparams['internetsources']['prod_id_position'])
                except ValueError:
                    prod_id_position = None

            prod_id_length = None
            if getparams['internetsources']['prod_id_length'] != None:
                try:
                    prod_id_length = int(getparams['internetsources']['prod_id_length'])
                except ValueError:
                    prod_id_length = None

            area_length = None
            if getparams['internetsources']['area_length'] != None:
                try:
                    area_length = int(getparams['internetsources']['area_length'])
                except ValueError:
                    area_length = None

            release_length = None
            if getparams['internetsources']['release_length'] != None:
                try:
                    release_length = int(getparams['internetsources']['release_length'])
                except ValueError:
                    release_length = None

            internetsourceinfo = {'internet_id': getparams['internetsources']['internet_id'],
                                  'defined_by': getparams['internetsources']['defined_by'],
                                  'descriptive_name': getparams['internetsources']['descriptive_name'],
                                  'description': getparams['internetsources']['description'],
                                  'modified_by': getparams['internetsources']['modified_by'],
                                  # 'update_datetime': datetime.date.today(),     # Created a trigger which updates this field
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
                                  'https_params': getparams['internetsources']['https_params'],
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

            if getparams['internetsources']['internet_id'] != getparams['internetsources']['orig_internet_id']:
                internetsourceinfo['orig_internet_id'] = getparams['internetsources']['orig_internet_id']

                # if self.crud_db.update('datasource_description', datasourcedescrinfo):
                if querydb.update_internet_source_info(internetsourceinfo, datasourcedescrinfo):
                    updatestatus = '{"success":"true", "message":"Internet data source and description updated!"}'
                else:
                    updatestatus = '{"success":false, "message":"An error occured while updating the internet data source!"}'
                # else:
                #     updatestatus = '{"success":false, "message":"An error occured while updating the internet data source description!"}'

            else:
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


class CreateInternetSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'internetsources' in getparams:

            startdate = None
            if getparams['internetsources']['start_date'] != None:
                try:
                    startdate = int(getparams['internetsources']['start_date'])
                except ValueError:
                    startdate = None

            enddate = None
            if getparams['internetsources']['end_date'] != None:
                try:
                    enddate = int(getparams['internetsources']['end_date'])
                except ValueError:
                    enddate = None

            prod_id_position = None
            if getparams['internetsources']['prod_id_position'] != None:
                try:
                    prod_id_position = int(getparams['internetsources']['prod_id_position'])
                except ValueError:
                    prod_id_position = None

            prod_id_length = None
            if getparams['internetsources']['prod_id_length'] != None:
                try:
                    prod_id_length = int(getparams['internetsources']['prod_id_length'])
                except ValueError:
                    prod_id_length = None

            area_length = None
            if getparams['internetsources']['area_length'] != None:
                try:
                    area_length = int(getparams['internetsources']['area_length'])
                except ValueError:
                    area_length = None

            release_length = None
            if getparams['internetsources']['release_length'] != None:
                try:
                    release_length = int(getparams['internetsources']['release_length'])
                except ValueError:
                    release_length = None

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
                                  'https_params': getparams['internetsources']['https_params'],
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

            if self.crud_db.create('internet_source', internetsourceinfo):
                if self.crud_db.create('datasource_description', datasourcedescrinfo):
                    createstatus = '{"success":"true", "message":"Internet data source and description created!"}'
                else:
                    createstatus = '{"success":"true", "message":"Internet data source created!"}'
            else:
                createstatus = '{"success":false, "message":"An error occured while creating the internet data source!"}'

        else:
            createstatus = '{"success":false, "message":"No internet data source passed!"}'

        return createstatus


class DeleteInternetSource(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'internetsources' in getparams:

            internetsourceinfo = {'internet_id': getparams['internetsources']['internet_id']}
            datasourcedescrinfo = {'datasource_descr_id': getparams['internetsources']['internet_id']}

            if self.crud_db.delete('internet_source', **internetsourceinfo):
                if self.crud_db.delete('datasource_description', **datasourcedescrinfo):
                    deletetatus = '{"success":"true", "message":"Internet data source and description deleted!"}'
                else:
                    deletetatus = '{"success":"true", "message":"Internet data source deleted!"}'
            else:
                deletetatus = '{"success":false, "message":"An error occured while deleting the internet data source!"}'

        else:
            deletetatus = '{"success":false, "message":"No internet data source passed!"}'

        return deletetatus


class GetSystemStatus(object):
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


class GetDashboard(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        PC1_connection = False
        PC23_connection = False

        PC2_mode = ''  # 'nominal' 'recovery'
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

        PC3_mode = ''  # 'nominal' 'recovery'
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
        #     "PC2_version": "2.2.0",
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
        #     "PC3_version": "2.2.0",
        #     "activePC": "pc2",
        #     "type_installation": "full"
        # }

        # print dashboard_dict
        dashboard_json = json.dumps(dashboard_dict,
                                    ensure_ascii=False,
                                    # encoding='utf-8',
                                    sort_keys=True,
                                    indent=4,
                                    separators=(', ', ': '))

        dashboard_json = '{"success":"true", "dashboard":' + dashboard_json + '}'

        return dashboard_json


class SetDataAutoSync(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        getparams = web.input()
        if hasattr(getparams, "dataautosync"):

            functions.setSystemSetting('data_sync', getparams['dataautosync'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"Data Auto Sync changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class SetDBAutoSync(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        getparams = web.input()
        if hasattr(getparams, "dbautosync"):

            functions.setSystemSetting('db_sync', getparams['dbautosync'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"DB Auto Sync changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class GetI18n(object):
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
                                           # encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            translations_json = '{"success":"true", "total":' \
                                + str(i18n.__len__()) \
                                + ',"translations":' + translations_json + '}'

        else:
            translations_json = '{"success":false, "error":"No translations defined!"}'

        return translations_json


class AddIngestMapset(object):
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


class DisableIngestMapset(object):
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


class GetMapsetsForIngest(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        mapsets_dict_all = []
        mapsets = querydb.get_mapsets_for_ingest(productcode=getparams['productcode'], version=getparams['version'],
                                                 subproductcode=getparams['subproductcode'])

        if hasattr(mapsets, "__len__") and mapsets.__len__() > 0:
            for mapset in mapsets:
                mapset_dict = functions.row2dict(mapset)
                mapsets_dict_all.append(mapset_dict)

            mapsets_json = json.dumps(mapsets_dict_all,
                                      ensure_ascii=False,
                                      # encoding='utf-8',
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

            mapsets_json = '{"success":"true", "total":' \
                           + str(mapsets.__len__()) \
                           + ',"mapsets":' + mapsets_json + '}'

        else:
            mapsets_json = '{"success":false, "error":"No Mapsets defined!"}'

        return mapsets_json


class GetMapsets(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        mapsets_dict_all = []
        mapsets = querydb.get_mapsets()

        if hasattr(mapsets, "__len__") and mapsets.__len__() > 0:
            for mapset in mapsets:
                # print (mapset)
                mapset_dict = functions.row2dict(mapset)
                mapsets_dict_all.append(mapset_dict)

            mapsets_json = json.dumps(mapsets_dict_all,
                                      ensure_ascii=False,
                                      # encoding='utf-8',
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

            mapsets_json = '{"success":"true", "total":' \
                           + str(mapsets.__len__()) \
                           + ',"mapsets":' + mapsets_json + '}'

        else:
            mapsets_json = '{"success":false, "error":"No Mapsets defined!"}'

        return mapsets_json


class CreateMapset(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'mapsets' in getparams:

            bboxcode = getparams['mapsets']['bboxcode']
            if bboxcode == None:
                bboxcode = getparams['mapsets']['mapsetcode']

            bboxinfo = { 'bboxcode': bboxcode,
                         'descriptive_name': bboxcode,
                         'defined_by': getparams['mapsets']['defined_by'],
                         'upper_left_long': getparams['mapsets']['upper_left_long'],
                         'upper_left_lat': getparams['mapsets']['upper_left_lat'],
                         'lower_right_long': getparams['mapsets']['lower_right_long'],
                         'lower_right_lat': getparams['mapsets']['lower_right_lat'],
                         'predefined': functions.str_to_bool(getparams['mapsets']['predefined'])
                       }

            bbox_pk = {
                'bboxcode': bboxcode
            }

            bboxexists = False
            if self.crud_db.read('bbox', **bbox_pk):
                bbox_pk = {
                    'bboxcode': bboxcode,
                    'predefined': False,
                }
                bboxexists = True
                bboxstatus = ''
                if self.crud_db.read('bbox', **bbox_pk):
                    if self.crud_db.update('bbox', bboxinfo):
                        bboxstatus = 'and BBOX updated!'
                    else:
                        createstatus = '{"success":false, "message":"An error occured while updating the custom BBOX!"}'
            else:
                if self.crud_db.create('bbox', bboxinfo):
                    bboxexists = True
                    bboxstatus = 'and BBOX created!'
                else:
                    createstatus = '{"success":false, "message":"An error occured while creating the custom BBOX!"}'

            mapsetinfo = { 'mapsetcode': getparams['mapsets']['mapsetcode'],
                           'descriptive_name': getparams['mapsets']['descriptive_name'],
                           'description': getparams['mapsets']['description'],
                           'defined_by': getparams['mapsets']['defined_by'],
                           'proj_code': getparams['mapsets']['proj_code'],
                           'resolutioncode': getparams['mapsets']['resolutioncode'],
                           'bboxcode': bboxcode,
                           'pixel_size_x': getparams['mapsets']['pixel_size_x'],
                           'pixel_size_y': getparams['mapsets']['pixel_size_y'],
                           'footprint_image': getparams['mapsets']['footprint_image'],
                           'center_of_pixel': functions.str_to_bool(getparams['mapsets']['center_of_pixel']),
                           }

            if bboxexists:
                if self.crud_db.create('mapset_new', mapsetinfo):
                    message = 'Mapset created ' + bboxstatus
                    createstatus = '{"success":true, "message":"' + message + '"}'
                else:
                    createstatus = '{"success":false, "message":"An error occured while creating the Mapset!"}'
        else:
            createstatus = '{"success":false, "message":"No mapset information passed!"}'

        return createstatus


class UpdateMapset(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'mapsets' in getparams:

            bboxcode = getparams['mapsets']['bboxcode']
            if bboxcode == None:
                bboxcode = getparams['mapsets']['mapsetcode']

            bboxinfo = { 'bboxcode': bboxcode,
                         'descriptive_name': bboxcode,
                         'defined_by': getparams['mapsets']['defined_by'],
                         'upper_left_long': getparams['mapsets']['upper_left_long'],
                         'upper_left_lat': getparams['mapsets']['upper_left_lat'],
                         'lower_right_long': getparams['mapsets']['lower_right_long'],
                         'lower_right_lat': getparams['mapsets']['lower_right_lat'],
                         'predefined': functions.str_to_bool(getparams['mapsets']['predefined'])
                       }

            bbox_pk = {
                'bboxcode': bboxcode
            }

            bboxexists = False
            bboxstatus = ''
            if self.crud_db.read('bbox', **bbox_pk):
                bbox_pk = {
                    'bboxcode': bboxcode,
                    'predefined': False,
                }
                bboxexists = True
                if self.crud_db.read('bbox', **bbox_pk):
                    if self.crud_db.update('bbox', bboxinfo):
                        bboxstatus = 'and BBOX updated!'
                    else:
                        createstatus = '{"success":false, "message":"An error occured while updating the custom BBOX!"}'
            else:
                if self.crud_db.create('bbox', bboxinfo):
                    bboxexists = True
                    bboxstatus = 'and BBOX created!'
                else:
                    createstatus = '{"success":false, "message":"An error occured while creating the custom BBOX!"}'

            mapsetinfo = { 'mapsetcode': getparams['mapsets']['mapsetcode'],
                           'descriptive_name': getparams['mapsets']['descriptive_name'],
                           'description': getparams['mapsets']['description'],
                           'defined_by': getparams['mapsets']['defined_by'],
                           'proj_code': getparams['mapsets']['proj_code'],
                           'resolutioncode': getparams['mapsets']['resolutioncode'],
                           'bboxcode': bboxcode,
                           'pixel_size_x': getparams['mapsets']['pixel_size_x'],
                           'pixel_size_y': getparams['mapsets']['pixel_size_y'],
                           'footprint_image': getparams['mapsets']['footprint_image'],
                           'center_of_pixel': functions.str_to_bool(getparams['mapsets']['center_of_pixel']),
                           }

            if bboxexists:
                if self.crud_db.update('mapset_new', mapsetinfo):
                    message = 'Mapset updated ' + bboxstatus
                    createstatus = '{"success":true, "message":"' + message + '"}'
                else:
                    createstatus = '{"success":false, "message":"An error occured while updating the Mapset!"}'

        else:
            createstatus = '{"success":false, "message":"No mapset information passed!"}'

        return createstatus


class DeleteMapset(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'mapsets' in getparams:

            mapsetinfo = {'mapsetcode': getparams['mapsets']['mapsetcode']}

            if self.crud_db.delete('mapset_new', **mapsetinfo):
                deletetatus = '{"success":true, "message":"Mapset deleted!"}'
            else:
                deletetatus = '{"success":false, "message":"An error occured while deleting the Mapset!"}'

        else:
            deletetatus = '{"success":false, "message":"No Mapset passed!"}'

        return deletetatus


class GetLanguages(object):
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
                                   # encoding='utf-8',
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

            languages_json = '{"success":"true", "total":' \
                             + str(languages.__len__()) \
                             + ',"languages":' + lang_json + '}'

        else:
            languages_json = '{"success":false, "error":"No languages defined!"}'

        return languages_json


class GetTimeLine(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        p = Product(product_code=getparams['productcode'], version=getparams['productversion'])
        dataset = p.get_dataset(mapset=getparams['mapsetcode'], sub_product_code=getparams['subproductcode'])
        dataset.get_filenames()
        all_present_product_dates = dataset.get_dates()
        # completeness = dataset.get_dataset_normalized_info()
        timeline = []
        if len(all_present_product_dates) > 0:
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

        timeline_json = '{"success":"true", "total":' + str(timeline.__len__()) + ',"timeline":' + timeline_json + '}'

        # print timeline_json
        return timeline_json


class GetAllColorSchemes(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        return webpy_esapp_helpers.getAllColorSchemes()


class GetProductColorSchemes(object):
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

                if default_legend or default_legend == 'true':
                    defaultlegend = True
                else:
                    defaultlegend = False

                # if there is only 1 legend defined, this is the default legend (even if not defined as default legend).
                if product_legends.__len__() == 1:
                    defaultlegend = True

                if defaultlegend:
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
                    color_html = 'rgb(' + r + ',' + g + ',' + b + ')'
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

            colorschemes = '{"success":"true", "total":' + str(
                product_legends.__len__()) + ',"legends":' + legends_json + '}'
        else:
            colorschemes = '{"success":"true", "message":"No legends defined for this product!"}'

        return colorschemes


class ProductNavigatorDataSets(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        force = False
        if 'force' in getparams:
            force = getparams.force
        return webpy_esapp_helpers.getProductNavigatorDataSets(force)


class GetLogFile(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        logfilename = ''
        if getparams['logtype'] == 'get':
            if sys.platform == 'win32':
                getparams['data_source_id'] = getparams['data_source_id'].replace(':', '_')

            if getparams['gettype'] == 'EUMETCAST':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.get_eumetcast.' + getparams[
                    'data_source_id'] + '.log'
            else:
                logfilename = es_constants.es2globals['log_dir'] + 'apps.get_internet.' + getparams[
                    'data_source_id'] + '.log'
        elif getparams['logtype'] == 'ingest':
            logfilename = es_constants.es2globals['log_dir'] + 'apps.ingestion.' + getparams['productcode'] + '.' + \
                          getparams['version'] + '.log'
        elif getparams['logtype'] == 'processing':
            # apps.processing.ID=6_PROD=tamsat-rfe_METHOD=std_precip_prods_only_ALGO=std_precip.log
            logfilename = es_constants.es2globals['log_dir'] + 'apps.processing.' \
                          + 'ID=' + getparams['process_id'] + '_' \
                          + 'PROD=' + getparams['productcode'] + '_' \
                          + 'METHOD=' + getparams['derivation_method'] + '_' \
                          + 'ALGO=' + getparams['algorithm'] + '.log'
        elif getparams['logtype'] == 'service':
            if getparams['service'] == 'eumetcast':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.acquisition.get_eumetcast.log'
            if getparams['service'] == 'internet':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.acquisition.get_internet.log'
            if getparams['service'] == 'ingest':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.acquisition.ingestion.log'
            if getparams['service'] == 'processing':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.processing.processing.log'
            if getparams['service'] == 'system':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.es2system.es2system.log'
            if getparams['service'] == 'dbsync':
                logfilename = '/var/log/bucardo/log.bucardo'
            if getparams['service'] == 'datasync':
                # logfilename = '/var/log/rsyncd.log'
                logfilename = es_constants.es2globals['log_dir'] + 'rsync.log'
            if getparams['service'] == 'ingestarchive':
                logfilename = es_constants.es2globals['log_dir'] + 'apps.es2system.ingest_archive.log'
                # logfilename = es_constants.es2globals['log_dir']+'apps.tools.ingest_historical_archives.log'

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

            logfilecontent = logfilecontent.replace('\'', '')
            logfilecontent = logfilecontent.replace('"', '')
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
        logfile_json = '{"success":"true","filename":"' + logfilename + '","logfilecontent":"' + logfilecontent + '"}'

        return logfile_json


class setIngestArchives(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "setingestarchives"):

            functions.setSystemSetting('ingest_archive_eum', getparams['setingestarchives'])

            # Todo: call system service to change the mode

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            result_json = '{"success":"true", "message":"Setting Ingest Archives from Eumetcast changed!"}'
        else:
            result_json = '{"success":false, "error":"No setting given!"}'

        return result_json


class ChangeRole(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "role"):

            functions.setSystemSetting('role', getparams['role'])

            # Todo: call system service to change the mode

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            reloadmodules.reloadallmodules()
            # Reloading the settings does not work well so set manually

            changerole_json = '{"success":"true", "message":"Role changed!"}'
        else:
            changerole_json = '{"success":false, "error":"No role given!"}'

        return changerole_json


class ChangeMode(object):
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
                    target = IP_other_PC + '::products' + es_constants.es2globals['processing_dir']

                    statusdatasync = es2system.system_data_sync(source, target)

                    statusdbsync = es2system.system_db_sync_full(systemsettings['role'].lower())

                    message = 'Data and Settings Synchronized to the other PC. You must now put the other PC in Nominal mode!'

                # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
                reloadmodules.reloadallmodules()
                # Reloading the settings does not work well so set manually

                changemode_json = '{"success":"true", "message":"' + message + '"}'
            else:
                changemode_json = '{"success":false, "message":"' + message + '"}'

        else:
            changemode_json = '{"success":false, "error":"No mode given!"}'

        return changemode_json


class GetAvailableVersions(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # getparams = web.input()

        versions_dict = functions.getListVersions()
        versions_json = json.dumps(versions_dict,
                                   ensure_ascii=False,
                                   # encoding='utf-8',
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        versions_json = '{"success":"true", "versions":' + versions_json + '}'

        # versions_json = '{"success":false, "error":"No versions available!"}'

        return versions_json


class ChangeVersion(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "version"):

            functions.setSystemSetting('active_version', getparams['version'])

            # Todo: call system service to change the version! PROBLEMS: answer back to browser?
            base = es_constants.es2globals['base_dir']  # +"-"

            if os.path.exists(base):
                if sys.platform != 'win32':
                    if os.path.islink(base):
                        os.unlink(base)
                        # print base+"-"+getparams['version']
                        os.symlink(base + "-" + getparams['version'], base)
                        changeversion_json = '{"success":"true", "message":"Version changed!"}'
                    elif os.path.isdir(base):
                        changeversion_json = '{"success":"false", "message":"The base is a directory and should be a symbolic link!"}'
                else:
                    base = base.replace('\\', '/')
                    os.unlink(base)  # Todo:  NO PERMISSIONS on windows version
                    os.symlink(base + "-" + getparams['version'], base)
                    changeversion_json = '{"success":true, "message":"Version changed!"}'
            else:
                changeversion_json = '{"success":false, "message":"Version path does not exist!"}'

        else:
            changeversion_json = '{"success":false, "error":"No version given!"}'

        return changeversion_json


class GetThemas(object):
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
                                     # encoding='utf-8',
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))

            themas_json = '{"success":"true", "total":' + str(themas.__len__()) + ',"themas":' + themas_json + '}'

        else:
            themas_json = '{"success":false, "error":"No themas defined!"}'

        return themas_json


class ChangeThema(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "thema"):
            changethema_json = webpy_esapp_helpers.ChangeThema(getparams['thema'])
        else:
            changethema_json = '{"success":false, "error":"No thema given!"}'

        return changethema_json


class ChangeThemaFromOtherPC(object):
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


class ChangeLogLevel(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if hasattr(getparams, "loglevel"):

            functions.setUserSetting('log_general_level', getparams['loglevel'])

            # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
            reloadmodules.reloadallmodules()

            # ToDo: Query thema products and activate them.

            changethema_json = '{"success":"true", "message":"Thema changed!"}'
        else:
            changethema_json = '{"success":false, "error":"No log level given!"}'

        return changethema_json


class GetLayers(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        layers_dict_all = []
        layers = querydb.get_layers()

        if hasattr(layers, "__len__") and layers.__len__() > 0:
            for row in layers:
                # row_dict = functions.row2dict(row)
                row_dict = row

                layer = {'layerid': row_dict['layerid'],
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
                                     # encoding='utf-8',
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))

            layers_json = '{"success":"true", "total":' \
                          + str(layers.__len__()) \
                          + ',"layers":' + layers_json + '}'

        else:
            layers_json = '{"success":false, "error":"No Layers defined!"}'

        return layers_json


class GetServerLayerFileList(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        layerfiledir = es_constants.es2globals['estation2_layers_dir']  # '/eStation2/layers/'
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
                    layerfile = {'layerfilename': os.path.join(root, filename).replace(layerfiledir, ""),
                                 'filesize': os.path.getsize(os.path.join(root, filename))}
                    layerfiles_dict.append(layerfile)

            layers_json = json.dumps(layerfiles_dict,
                                     ensure_ascii=False,
                                     # encoding='utf-8',
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))

            layerfiles_json = '{"success":"true",' \
                              + '"layerfiles":' + layers_json + '}'

        return layerfiles_json


class SaveDrawnVectorLayer(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def GET(self):
        getparams = web.input()

        # layerfiledir = '/eStation2/layers/' # change this to the directory you want to store the file in.
        layerfiledir = es_constants.es2globals['estation2_layers_dir']
        if 'layerfilename' in getparams:  # to check if the file-object is created
            try:
                filename = getparams.layerfilename.replace('\\',
                                                           '/')  # replaces the windows-style slashes with linux ones.
                filename = filename.split('/')[
                    -1]  # splits the filepath and chooses the last part (the filename with extension)
                filename = filename.replace(' ', '_')
                filename += '.geojson'

                # Separate base from extension
                base, extension = os.path.splitext(filename)

                # Initial new name
                new_name = os.path.join(layerfiledir, filename).encode('utf-8').decode()
                new_name_final = os.path.join(layerfiledir, filename)

                if not os.path.exists(new_name):  # file does not exist in <layerfiledir>
                    fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                    fout.write(
                        getparams.drawnlayerfeaturesGEOSON)  # .read()  writes the uploaded file to the newly created file.
                    fout.close()  # closes the file, upload complete.
                else:  # file exists in <layerfiledir>
                    ii = 1
                    while True:
                        new_name = os.path.join(layerfiledir, base + "_" + str(ii) + extension).encode('utf-8').decode()
                        new_name_final = os.path.join(layerfiledir, base + "_" + str(ii) + extension)
                        if not os.path.exists(new_name):
                            fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                            fout.write(
                                getparams.drawnlayerfeaturesGEOSON)  # .read()  writes the uploaded file to the newly created file.
                            fout.close()  # closes the file, upload complete.
                            break
                        ii += 1

                finalfilename = new_name_final.split('/')[
                    -1]  # splits the and chooses the last part (the filename with extension)
                success = True
            except:
                success = False
        else:
            success = False

        if success:
            layerdrawprobs = {
                # 'layerid': getparams['layer']['layerid'],
                # 'layerlevel': getparams['layer']['layerlevel'],
                'layername': getparams.layerfilename,
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
                'submenu': 'User defined',
                'menu': 'other',
                'defined_by': 'USER',
                # 'open_in_mapview': '',
                'provider': 'User'}

            if self.crud_db.create('layers', layerdrawprobs):
                newlayer = self.crud_db.read('layers', filename=finalfilename)
                for layer in newlayer:
                    layerid = layer['layerid']

                status = '{"success":true, "layerid":' + layerid + ', "layerfilename": "' + finalfilename + '", "message":"Layer created!"}'
            else:
                status = '{"success":false, "message":"An error occured while saving the settings in the database for the drawn layer!"}'

            # SEE class DownloadVectorLayer below
            #
            # web.header('Content-Type', 'text/html')   # 'application/x-compressed'  'application/force-download'
            # web.header('Content-transfer-encoding', 'binary')
            # web.header('Content-Disposition', 'attachment; filename=' + finalfilename)  # force browser to show "Save as" dialog.
            # f = open(layerfiledir+'/'+finalfilename, 'rb')
            # while 1:
            #     buf = f.read(1024 * 8)
            #     if not buf:
            #         break
            #     yield buf
            # f.close()
        else:
            status = '{"success":false, "message":"An error occured while saving the drawn layer!"}'

        return status


class DownloadVectorLayer(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        if not hasattr(getparams, "layerfilename"):
            status = '{"success":false, "message":"No layer filename given!"}'
            # return status
        else:
            layerfilename = getparams['layerfilename'].encode('utf-8').decode()
            layerfiledir = es_constants.es2globals['estation2_layers_dir']
            if os.path.exists(layerfiledir + '/' + layerfilename):
                web.header('Content-Type', 'text/html')  # 'application/x-compressed'  'application/force-download'
                web.header('Content-transfer-encoding', 'binary')
                web.header('Content-Disposition',
                           'attachment; filename=' + layerfilename)  # force browser to show "Save as" dialog.
                f = open(layerfiledir + '/' + layerfilename, 'rb')
                while 1:
                    buf = f.read(1024 * 8)
                    if not buf:
                        break
                    yield buf
                f.close()
            else:
                status = '{"success":false, "message":"Layer file not found!"}'


class ImportLayer(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # getparams = json.loads(web.data())  # get PUT data
        getparams = web.input()  # get POST data

        # layerfiledir = '/eStation2/layers/' # change this to the directory you want to store the file in.
        layerfiledir = es_constants.es2globals['estation2_layers_dir']
        if 'layerfilename' in getparams:  # to check if the file-object is created
            try:
                filepath = getparams.layerfilename.replace('\\',
                                                           '/')  # replaces the windows-style slashes with linux ones.
                filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)

                # Separate base from extension
                base, extension = os.path.splitext(filename)

                # Initial new name
                new_name = os.path.join(layerfiledir, filename).encode('utf-8').decode()
                new_name_final = layerfiledir + '/' + filename

                if not os.path.exists(new_name):  # file does not exist in <layerfiledir>
                    fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                    fout.write(getparams.layerfile)  # .read()  writes the uploaded file to the newly created file.
                    fout.close()  # closes the file, upload complete.
                else:  # file exists in <layerfiledir>
                    ii = 1
                    while True:
                        new_name = os.path.join(layerfiledir, base + "_" + str(ii) + extension).encode('utf-8').decode()
                        new_name_final = os.path.join(layerfiledir, base + "_" + str(ii) + extension)
                        if not os.path.exists(new_name):
                            fout = open(new_name, 'w')  # creates the file where the uploaded file should be stored
                            fout.write(
                                getparams.layerfile)  # .read()  writes the uploaded file to the newly created file.
                            fout.close()  # closes the file, upload complete.
                            break
                        ii += 1

                finalfilename = new_name_final.split('/')[
                    -1]  # splits the and chooses the last part (the filename with extension)
                success = True
            except:
                success = False
        else:
            success = False

        if success:
            status = '{"success":"true", "filename":"' + finalfilename + '","message":"Layer imported!"}'
        else:
            status = '{"success":false, "message":"An error occured while importing the layer!"}'

        return status


class DeleteLayer(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def DELETE(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'layer' in getparams:  # hasattr(getparams, "layer")
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


class CreateLayer(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        # getparams = web.input() # get POST data
        if 'layer' in getparams:  # hasattr(getparams, "layer")
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
                                'enabled': functions.str_to_bool(getparams['layer']['enabled']),
                                'deletable': True,
                                'background_legend_image_filename': '',
                                # 'projection': getparams['layer']['projection'],
                                'submenu': getparams['layer']['submenu'],
                                'menu': getparams['layer']['menu'],
                                'defined_by': 'USER',
                                # 'open_in_mapview': functions.str_to_bool(getparams['layer']['open_in_mapview']),
                                'provider': getparams['layer']['provider'] }

            if self.crud_db.create('layers', layerdrawprobs):
                status = '{"success":"true", "message":"Layer created!"}'
            else:
                status = '{"success":false, "message":"An error occured while creating the new layer!"}'

        else:
            status = '{"success":false, "message":"No layer info passed!"}'

        return status


class UpdateLayer(object):
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
                                'enabled': functions.str_to_bool(getparams['layer']['enabled']),
                                # 'deletable': functions.str_to_bool(getparams['layer']['deletable']),
                                # 'background_legend_image_filename': getparams['layer']['background_legend_image_filename'],
                                # 'projection': getparams['layer']['projection'],
                                'submenu': getparams['layer']['submenu'],
                                'menu': getparams['layer']['menu'],
                                'defined_by': getparams['layer']['defined_by'],
                                'open_in_mapview': functions.str_to_bool(getparams['layer']['open_in_mapview']),
                                'provider': getparams['layer']['provider'] }

            if self.crud_db.update('layers', layerdrawprobs):
                updatestatus = '{"success":"true", "message":"Layer updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the layer!"}'

        else:
            updatestatus = '{"success":false, "message":"No layer info passed!"}'

        return updatestatus


class GetVectorLayer(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        filename = getparams['file']
        layerfilepath = es_constants.estation2_layers_dir + os.path.sep + filename  #.encode('utf-8').decode()
        # if isFile(layerfilepath):
        layerfile = open(layerfilepath, 'rb')
        layerfilecontent = layerfile.read()
        # else:
        #   layerfilecontent = '{"success":false, "message":"Layerfile not found!"}'
        return layerfilecontent


class SystemReport(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):

        filename = es2system.system_create_report()
        web.header('Content-Type', 'application/force-download')  # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition',
                   'attachment; filename=' + os.path.basename(filename))  # force browser to show "Save as" dialog.
        f = open(filename, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()
        os.remove(filename)


class InstallReport(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):

        filename = es2system.system_install_report()
        web.header('Content-Type', 'application/force-download')  # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition',
                   'attachment; filename=' + os.path.basename(filename))  # force browser to show "Save as" dialog.
        f = open(filename, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()
        os.remove(filename)


class ResetUserSettings(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        updatestatus = webpy_esapp_helpers.ResetUserSettings()

        # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
        import imp
        imp.reload(webpy_esapp_helpers)

        return updatestatus


class UpdateUserSettings(object):
    def __init__(self):
        self.lang = "eng"

    def PUT(self):
        params = json.loads(web.data())
        updatestatus = webpy_esapp_helpers.UpdateUserSettings(params)

        # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
        import imp
        imp.reload(webpy_esapp_helpers)

        return updatestatus


class UserSettings(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        import configparser

        systemsettings = functions.getSystemSettings()

        if sys.platform != 'win32':
            if systemsettings['type_installation'].lower() == 'jrc_online':
                factory_settings_filename = 'factory_settings_jrc_online.ini'
            else:
                factory_settings_filename = 'factory_settings.ini'
        else:
            factory_settings_filename = 'factory_settings_windows.ini'

        config_usersettings = configparser.ConfigParser()
        config_usersettings.read(['user_settings.ini',
                                  es_constants.es2globals['settings_dir'] + '/user_settings.ini'])

        config_factorysettings = configparser.ConfigParser()
        config_factorysettings.read([factory_settings_filename,
                                     es_constants.es2globals['config_dir'] + '/' + factory_settings_filename])

        settings = {}
        usersettings = config_usersettings.items('USER_SETTINGS')
        for setting, value in usersettings:
            if value is not None and value != "":
                settings[setting] = value
            else:
                settings[setting] = config_factorysettings.get('FACTORY_SETTINGS', setting)

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

        settings_json = '{"success":"true", "systemsettings":' + settings_json + '}'

        # systemsettings_json = '{"success":false, "error":"No ingestions defined!"}'

        return settings_json


class IPSettings(object):
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

        settings_json = '{"success":"true", "ipsettings":' + settings_json + '}'

        # systemsettings_json = '{"success":false, "error":"No ingestions defined!"}'

        return settings_json


class UpdateIPSettings(object):
    def __init__(self):
        self.lang = "eng"

    def PUT(self):
        import configparser

        systemsettingsfilepath = es_constants.es2globals['settings_dir'] + '/system_settings.ini'
        # usersettingsfilepath = '/eStation2/settings/system_settings.ini'
        config_systemsettings = configparser.ConfigParser()
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
        command = es_constants.es2globals['base_dir'] + '/apps/es2system/network_config_1.0.sh ' + \
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


class IngestArchive(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        getparams = web.input()
        return webpy_esapp_helpers.IngestArchive(getparams)


class GetProductLayer(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        # filename_png = self.getProductLayer(getparams)
        filename_png = webpy_esapp_helpers.getProductLayer(getparams)

        web.header('Content-type', 'image/jpg')
        f = open(filename_png, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()
        os.remove(filename_png)

    def POST(self):
        getparams = web.input()
        filename_png = webpy_esapp_helpers.getProductLayer(getparams)

        web.header('Content-type', 'image/jpg')
        f = open(filename_png, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        f.close()
        os.remove(filename_png)


class GetBackgroundLayer(object):
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
        errorfile = es_constants.log_dir + "/mapserver_error.log"

        # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

        owsrequest = mapscript.OWSRequest()

        inputparams = web.input()
        for k, v in inputparams.items():
            # print k + ':' + v
            owsrequest.setParameter(k.upper(), v)

        owsrequest.setParameter("LAYERS", getparams['layername'])

        backgroundlayer = mapscript.mapObj(es_constants.template_mapfile)
        backgroundlayer.setConfigOption("PROJ_LIB", projlib)
        backgroundlayer.setConfigOption("MS_ERRORFILE", errorfile)
        backgroundlayer.maxsize = 4096

        outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
        outputformat_png.setOption("INTERLACE", "OFF")
        backgroundlayer.appendOutputFormat(outputformat_png)
        # outputformat_gd = mapscript.outputFormatObj('GD/GIF', 'gif')
        # backgroundlayer.appendOutputFormat(outputformat_gd)
        backgroundlayer.selectOutputFormat('png')
        backgroundlayer.debug = mapscript.MS_TRUE
        backgroundlayer.status = mapscript.MS_ON
        backgroundlayer.units = mapscript.MS_DD

        coords = list(map(float, inputparams.BBOX.split(',')))
        llx = coords[0]
        lly = coords[1]
        urx = coords[2]
        ury = coords[3]
        backgroundlayer.setExtent(llx, lly, urx, ury)  # -26, -35, 60, 38

        # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
        # epsg = "+init=epsg:3857"
        # epsg = "+init=" + inputparams.CRS.lower()   # CRS = "EPSG:4326"
        epsg = inputparams.CRS.lower()  # CRS = "EPSG:4326"
        backgroundlayer.setProjection(epsg)

        w = int(inputparams.WIDTH)
        h = int(inputparams.HEIGHT)
        backgroundlayer.setSize(w, h)

        # General web service information
        backgroundlayer.setMetaData("WMS_TITLE", "Background layer description")
        backgroundlayer.setMetaData("WMS_SRS", inputparams.CRS.lower())
        # backgroundlayer.setMetaData("WMS_SRS", "epsg:3857")
        backgroundlayer.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 background layers.")
        backgroundlayer.setMetaData("WMS_ENABLE_REQUEST", "*")  # necessary!!

        layer = mapscript.layerObj(backgroundlayer)
        layer.name = getparams['layername']
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON  # MS_DEFAULT
        layer.data = filename
        # layer.setProjection("+init=epsg:4326")
        layer.setProjection("epsg:4326")
        layer.dump = mapscript.MS_TRUE

        result_map_file = es_constants.apps_dir + '/analysis/Backgroundlayer_result.map'
        if os.path.isfile(result_map_file):
            os.remove(result_map_file)
        # backgroundlayer.save(result_map_file)
        image = backgroundlayer.draw()

        contents = backgroundlayer.OWSDispatch(owsrequest)
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        # web.header = "Content-Type","%s; charset=utf-8"%content_type
        web.header('Content-type', 'image/png')
        # web.header('Content-transfer-encoding', 'binary')
        return content


class Processing(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        force = False
        if 'force' in getparams:
            force = getparams.force
        return webpy_esapp_helpers.getProcessing(force)


class UpdateProcessing(object):
    def __init__(self):
        self.lang = "eng"
        self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'processes' in getparams:  # hasattr(getparams, "processes")
            processinfo = {'process_id': getparams['processes']['process_id'],
                           'activated': functions.str_to_bool(getparams['processes']['process_activated'])}

            if self.crud_db.update('processing', processinfo):
                updatestatus = '{"success":"true", "message":"Process updated!"}'
            else:
                updatestatus = '{"success":false, "message":"An error occured while updating the process!"}'

        else:
            updatestatus = '{"success":false, "message":"No process info passed!"}'

        return updatestatus

    def POST(self):
        getparams = json.loads(web.data())  # get PUT data
        if 'processoutputproduct' in getparams:  # hasattr(getparams, "processoutputproduct")
            for outputproduct in getparams['processoutputproduct']:
                if 'subactivated' in outputproduct:
                    processproductinfo = {'process_id': outputproduct['process_id'],
                                          'productcode': outputproduct['productcode'],
                                          'subproductcode': outputproduct['subproductcode'],
                                          'version': outputproduct['version'],
                                          'mapsetcode': outputproduct['mapsetcode'],
                                          'activated': functions.str_to_bool(outputproduct['subactivated'])}

                    if self.crud_db.update('process_product', processproductinfo):
                        updatestatus = '{"success":"true", "message":"Process output product updated!"}'
                    else:
                        updatestatus = '{"success":false, "message":"An error occured while updating the process output product!"}'

        else:
            updatestatus = '{"success":false, "message":"No process info passed!"}'

        return updatestatus


class DataSets(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        force = False
        if 'force' in getparams:
            force = getparams.force
        return webpy_esapp_helpers.getDataSets(force)


class CheckStatusAllServices(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        if sys.platform == 'win32':
            status_services = functions.getStatusAllServicesWin()
        else:
            status_services = functions.getStatusAllServices()

        systemsettings = functions.getSystemSettings()

        servicesstatus_json = '{"success": true, "eumetcast": ' + status_services['eumetcast'] + \
                              ', "internet": ' + status_services['internet'] + \
                              ', "ingest": ' + status_services['ingest'] + \
                              ', "processing": ' + status_services['process'] + \
                              ', "system": ' + status_services['system'] + \
                              ', "ingest_archive_eum": ' + systemsettings['ingest_archive_eum'] + '}'

        return servicesstatus_json


class ExecuteServiceTask(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        message = ''
        getparams = web.input()

        if sys.platform == 'win32':
            message = webpy_esapp_helpers.execServiceTaskWin(getparams)
        else:
            message = webpy_esapp_helpers.execServiceTask(getparams)

        logger.info(message)
        servicesstatus_json = '{"success": true, "message": "' + message + '"}'
        return servicesstatus_json


class UpdateProductInfo(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # getparams = json.loads(web.data())
        getparams = web.input()

        productinfo = {
            'orig_productcode': getparams['orig_productcode'],
            'orig_version': getparams['orig_version'],
            'productcode': getparams['productcode'],
            'subproductcode': getparams['productcode'] + '_native',
            'version': getparams['version'],
            'provider': getparams['provider'].replace("'", "''"),
            'descriptive_name': getparams['prod_descriptive_name'].replace("'", "''"),
            'description': getparams['description'].strip(u'\u200b').replace("'", "''"),
            'category_id': getparams['category_id'],
            'defined_by': getparams['defined_by'],
            'activated': getparams['activated']
        }

        productupdated = querydb.update_product_info(productinfo)

        if productupdated:
            updatestatus = '{"success":"true", "message":"Product updated!"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the product!"}'

        return updatestatus


class CreateProduct(object):
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
                       'subproductcode': getparams['productcode'] + '_native',
                       'version': version,
                       'product_type': 'Native',
                       'defined_by': getparams['defined_by'],
                       'activated': functions.str_to_bool(getparams['activated']),
                       'provider': getparams['provider'].replace("'", "''"),
                       'descriptive_name': getparams['prod_descriptive_name'].replace("'", "''"),
                       'description': getparams['description'].strip(u'\u200b').replace("'", "''"),
                       'category_id': getparams['category_id'],
                       'frequency_id': 'undefined',
                       'date_format': 'undefined',
                       'data_type_id': 'undefined',
                       'masked': False
                       }

        if self.crud_db.create('product', productinfo):
            createstatus = '{"success":"true", "message":"Product created!"}'
        else:
            createstatus = '{"success":"false", "message":"An error occured while creating the product!"}'

        return createstatus


class UpdateProduct(object):
    def __init__(self):
        self.lang = "eng"
        # self.crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    def PUT(self):
        getparams = json.loads(web.data())
        # productinfo = {'productcode': getparams['products']['productcode'],
        #                'subproductcode': getparams['products']['subproductcode'],
        #                'version': getparams['products']['version'],
        #                'product_type': getparams['products']['product_type'],
        #                'defined_by': getparams['products']['defined_by'],
        #                'activated': getparams['products']['activated']}
        # if self.crud_db.update('product', productinfo):

        updatestatus = webpy_esapp_helpers.UpdateProduct(productcode=getparams['products']['productcode'],
                                                         version=getparams['products']['version'],
                                                         activate=getparams['products']['activated'])

        return updatestatus


class DeleteProduct(object):
    def __init__(self):
        self.lang = "eng"

    def DELETE(self):
        getparams = json.loads(web.data())

        deletestatus = webpy_esapp_helpers.DeleteProduct(productcode=getparams['products']['productcode'],
                                                         version=getparams['products']['version'])

        return deletestatus


class UpdateDataAcquisition(object):
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
                               'activated': functions.str_to_bool(getparams['dataacquisitions']['activated']),
                               'store_original_data': functions.str_to_bool(getparams['dataacquisitions']['store_original_data'])}

        # ToDO: distinguish upodate of activated and store_original_data! Different queries?
        if self.crud_db.update('product_acquisition_data_source', dataacquisitioninfo):
            if getparams['dataacquisitions']['store_original_data']:
                message = '<b>Activated</b> Store Native for data source <b>' + getparams['dataacquisitions'][
                    'data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'
            elif not getparams['dataacquisitions']['store_original_data']:
                message = '<b>Deactivated</b> Store Native for data source <b>' + getparams['dataacquisitions'][
                    'data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'

            if getparams['dataacquisitions']['activated']:
                message = '<b>Activated</b> data source <b>' + getparams['dataacquisitions'][
                    'data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'
            elif not getparams['dataacquisitions']['activated']:
                message = '<b>Deactivated</b> data source <b>' + getparams['dataacquisitions'][
                    'data_source_id'] + '</b></br>' + \
                          ' for productcode: <b>' + getparams['dataacquisitions']['productcode'] + '</b>'

            updatestatus = '{"success":"true", "message":"' + message + '"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the Get!"}'

        return updatestatus


class UpdateIngestion(object):
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
                         'activated': functions.str_to_bool(getparams['ingestions']['activated'])}

        if self.crud_db.update('ingestion', ingestioninfo):
            message = 'Ingestion for: </br>' + \
                      'Productcode: <b>' + getparams['ingestions']['productcode'] + '</b></br>' \
                                                                                    'Mapsetcode: <b>' + \
                      getparams['ingestions']['mapsetcode'] + '</b></br>' \
                                                              'Subproductcode: <b>' + getparams['ingestions'][
                          'subproductcode'] + '</b>'
            if getparams['ingestions']['activated']:
                message = '<b>Activated</b> ' + message
            else:
                message = '<b>Deactivated</b> ' + message
            updatestatus = '{"success":"true", "message":"' + message + '"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the Ingestion!"}'

        return updatestatus


class Ingestion(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        force = False
        if 'force' in getparams:
            force = getparams.force
        return webpy_esapp_helpers.getIngestion(force)


class getIngestSubProducts(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()

        return webpy_esapp_helpers.getIngestSubProducts()


class CreateIngestSubProduct(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()
        createstatus = webpy_esapp_helpers.CreateIngestSubProduct(params)

        return createstatus


class UpdateIngestSubProduct(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        # params = json.loads(web.data())
        params = web.input()
        updatestatus = webpy_esapp_helpers.UpdateIngestSubProduct(params)

        return updatestatus


class DeleteIngestSubProduct(object):
    def __init__(self):
        self.lang = "eng"

    def DELETE(self):
        params = json.loads(web.data())

        deletestatus = webpy_esapp_helpers.DeleteIngestSubProduct(params)

        return deletestatus


class getSubDatasourceDescriptions(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # getparams = web.input()
        return webpy_esapp_helpers.getSubDatasourceDescriptions()


class CreateSubDatasourceDescription(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()

        return webpy_esapp_helpers.CreateSubDatasourceDescription(params)


class UpdateSubDatasourceDescription(object):
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        params = web.input()

        return webpy_esapp_helpers.UpdateSubDatasourceDescription(params)


class DeleteSubDatasourceDescription(object):
    def __init__(self):
        self.lang = "eng"

    def DELETE(self):
        params = json.loads(web.data())

        return webpy_esapp_helpers.DeleteSubDatasourceDescription(params)


class DataAcquisition(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        # return web.ctx

        dataacquisitions = querydb.get_dataacquisitions()

        if hasattr(dataacquisitions, "__len__") and dataacquisitions.__len__() > 0:
            # dataacquisitions_json = tojson(dataacquisitions)

            acq_dict_all = []
            for row in dataacquisitions:
                acq_dict = functions.row2dict(row)
                # Retrieve datetime of latest acquired file and lastest datetime
                # the acquisition was active of a specific eumetcast id
                acq_dates = get_eumetcast.get_eumetcast_info(row.data_source_id)
                if acq_dates:
                    for key in list(acq_dates.keys()):
                        # acq_info += '"%s": "%s", ' % (key, acq_dates[key])
                        if isinstance(acq_dates[key], datetime.date):
                            datetostring = acq_dates[key].strftime("%y-%m-%d %H:%M")
                            acq_dict[key] = datetostring
                        else:
                            acq_dict[key] = acq_dates[key]
                else:
                    acq_dict['time_latest_copy'] = ''  # datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['time_latest_exec'] = ''  # datetime.datetime.now().strftime("%y-%m-%d %H:%M")
                    acq_dict['length_proc_list'] = ''  # datetime.datetime.now().strftime("%y-%m-%d %H:%M")

                acq_dict_all.append(acq_dict)
                acq_json = json.dumps(acq_dict_all,
                                      ensure_ascii=False,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))
                dataacquisitions_json = '{"success":"true", "total":' \
                                        + str(dataacquisitions.__len__()) \
                                        + ',"dataacquisitions":' + acq_json + '}'
        else:
            dataacquisitions_json = '{"success":false, "error":"No data acquisitions defined!"}'

        return dataacquisitions_json


class ProductAcquisition(object):
    def __init__(self):
        self.lang = "eng"

    def GET(self, params):
        params = web.input()

        return webpy_esapp_helpers.getProductAcquisition(params.activated)


if __name__ == "__main__":
    app.run()
