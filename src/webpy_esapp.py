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
# import re

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
# from apps.analysis import mapserver

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
    "/systemsettings/changeloglevel", "ChangeLogLevel",
    "/systemsettings/ipsettings", "IPSettings",
    "/systemsettings/ipsettings/update", "UpdateIPSettings",

    "/processing", "Processing",
    "/processing/update", "UpdateProcessing",

    "/datasets", "DataSets",

    "/analysis/getproductlayer", "GetProductLayer",
    "/analysis/getvectorlayer", "GetVectorLayer",
    "/analysis/getbackgroundlayer", "GetBackgroundLayer",
    "/analysis/productnavigator", "ProductNavigatorDataSets",
    "/analysis/getcolorschemes", "GetColorSchemes",
    "/analysis/gettimeline", "GetTimeLine",
    "/analysis/timeseriesproduct", "TimeseriesProducts",
    "/analysis/gettimeseries", "GetTimeseries",

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
            functions.setUserSetting('default_language', getparams['lang'])

        render = web.template.render(es_constants.es2globals['base_dir']+'/apps/gui/esapp')
        # print es_constants.es2globals['default_language']
        if es_constants.es2globals['default_language'] == 'eng':
            return render.index()
        elif es_constants.es2globals['default_language'] == 'fra':
            return render.index_fr()
        else:
            return render.index()


class GetCategories:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        categories_dict_all = []
        categories = querydb.get_categories()

        if categories.__len__() > 0:
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

        if frequencies.__len__() > 0:
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

        if dateformats.__len__() > 0:
            for row in dateformats:
                row_dict = functions.row2dict(row)
                # internetsource = {'category_id': row_dict['category_id'],
                #                   'descriptive_name': row_dict['descriptive_name']}
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

        if datatypes.__len__() > 0:
            for row in datatypes:
                row_dict = functions.row2dict(row)
                # internetsource = {'category_id': row_dict['category_id'],
                #                   'descriptive_name': row_dict['descriptive_name']}
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

        productinfo = {
            'productcode': getparams['productcode'],
            'subproductcode': getparams['subproductcode'],
            'version': getparams['version'],
            'data_source_id': getparams['data_source_id'],
            'defined_by': 'JRC',
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

        productinfo = {
            'productcode': getparams['productcode'],
            'subproductcode': getparams['subproductcode'],
            'version': getparams['version'],
            'data_source_id': getparams['data_source_id'],
            'defined_by': 'JRC',
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

        if eumetcastsources.__len__() > 0:
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
                                   'date_type': row_dict['date_type'],
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


class GetInternetSources:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        internetsources_dict_all = []
        internetsources = querydb.get_internetsources()

        if internetsources.__len__() > 0:
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
                                  'date_type': row_dict['date_type'],
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
                                  'start_date': int(getparams['internetsources']['start_date']),
                                  'end_date': int(getparams['internetsources']['end_date']),
                                  'datasource_descr_id': getparams['internetsources']['internet_id']}

            datasourcedescrinfo = {'datasource_descr_id': getparams['internetsources']['internet_id'],
                                  'format_type': getparams['internetsources']['format_type'],
                                  'file_extension': getparams['internetsources']['file_extension'],
                                  'delimiter': getparams['internetsources']['delimiter'],
                                  'date_format': getparams['internetsources']['date_format'],
                                  'date_position': getparams['internetsources']['date_position'],
                                  'product_identifier': getparams['internetsources']['product_identifier'],
                                  'prod_id_position': int(getparams['internetsources']['prod_id_position']),
                                  'prod_id_length': int(getparams['internetsources']['prod_id_length']),
                                  'area_type': getparams['internetsources']['area_type'],
                                  'area_position': getparams['internetsources']['area_position'],
                                  'area_length': int(getparams['internetsources']['area_length']),
                                  'preproc_type': getparams['internetsources']['preproc_type'],
                                  'product_release': getparams['internetsources']['product_release'],
                                  'release_position': getparams['internetsources']['release_position'],
                                  'release_length': int(getparams['internetsources']['release_length']),
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

        # TODO: Use port 80?
        IP_port = ':22'

        # IP_PC1 = '139.191.147.79:22'
        PC1_connection = functions.check_connection(systemsettings['ip_pc1'] + IP_port)

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
                PC23_connection = functions.check_connection(systemsettings['ip_pc3'] + IP_port)
                # print "PC23_connection: " + str(PC23_connection)

                if PC23_connection:
                    status_PC3 = functions.get_remote_system_status(systemsettings['ip_pc3'])
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
                PC23_connection = functions.check_connection(systemsettings['ip_pc2'] + IP_port)
                if PC23_connection:
                    status_PC2 = functions.get_remote_system_status(systemsettings['ip_pc2'])
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

        if i18n.__len__() > 0:
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


class GetLanguages:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        languages_dict_all = []
        languages = querydb.get_languages()

        if languages.__len__() > 0:
            for lang in languages:
                if es_constants.es2globals['default_language'] == lang.langcode:
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
        from apps.analysis.getTimeseries import getTimeseries
        getparams = web.input()
        yearts = getparams.yearTS
        wkt = getparams.WKT
        requestedtimeseries = json.loads(getparams.selectedTimeseries)
        tsFromPeriod = getparams.tsFromPeriod
        tsToPeriod = getparams.tsToPeriod
        # print tsFromPeriod

        if getparams.yearTS != '':
            from_date = datetime.date(int(yearts), 01, 01)
            to_date = datetime.date(int(yearts), 12, 31)
        elif tsFromPeriod != '' and tsToPeriod != '':
            from_date = datetime.datetime.strptime(tsFromPeriod, '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(tsToPeriod, '%Y-%m-%d').date()

        yaxes = []
        count = 0
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries)
        axes = len(timeseries_yaxes)
        for yaxe in timeseries_yaxes:
            count += 1
            opposite = "false"
            if axes >= 2 and count % 2 == 0:   # and yaxe.oposite == "f"
                opposite = "false"
            if axes >= 2 and count % 2 != 0:   # and yaxe.oposite == "t"
                opposite = "true"
            if axes == 1:
                opposite = "false"
            yaxe = {'id': yaxe.yaxes_id, 'title': yaxe.title, 'unit': yaxe.unit, 'opposite': opposite, 'min': yaxe.min, 'max': yaxe.max}
            yaxes.append(yaxe)

        timeseries = []
        for timeserie in requestedtimeseries:
            productcode = timeserie['productcode']
            subproductcode = timeserie['subproductcode']
            version = timeserie['version']
            mapsetcode = timeserie['mapsetcode']

            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date)
            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)

            product = {"productcode": productcode,
                       "subproductcode": subproductcode,
                       "version": version}

            timeseries_drawproperties = querydb.get_timeseries_drawproperties(product)
            for ts_drawprops in timeseries_drawproperties:
                ts = {'name': ts_drawprops.tsname_in_legend,
                      'type': ts_drawprops.charttype,
                      'dashStyle': ts_drawprops.linestyle,
                      'lineWidth': ts_drawprops.linewidth,
                      'color': ts_drawprops.color,
                      'yAxis': ts_drawprops.yaxes_id,
                      'data': data}
                timeseries.append(ts)

        ts_json = {"data_available": "true",
                   "showYearInTicks": "false",
                   "showYearInToolTip": "false",
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


        # categories = ["20140101","20140111","20140121","20140201","20140211","20140221","20140301","20140311","20140321","20140401","20140411","20140421","20140501","20140511","20140521","20140601","20140611","20140621","20140701","20140711","20140721","20140801","20140811","20140821","20140901","20140911","20140921","20141001","20141011","20141021","20141101","20141111","20141121","20141201","20141211","20141221"]
        # categories_dict = []
        # for category in categories:
        #     catdate = datetime.datetime.strptime(category, "%Y%m%d").date()
        #     dateinmilisecond = functions.unix_time_millis(catdate)
        #     categories_dict.append(dateinmilisecond)
        #
        # categories_json = json.dumps(categories_dict, ensure_ascii=False, sort_keys=True, separators=(', '))
        #
        # ts_json = '{ "data_available": true, ' \
        #                 '"doubleYAxis": true, ' \
        #                 '"showYearInTicks": false, ' \
        #                 '"showYearInToolTip": false, ' \
        #                 '"countryName": "Democratic Republic of the Congo",  ' \
        #                 '"areaName": "Province Orientale", ' \
        #                 '"yaxes": [{  ' \
        #                               '"title": "NDVI",' \
        #                               '"unit": "", ' \
        #                               '"opposite": "false", ' \
        #                               '"min": -0.3, ' \
        #                               '"max": 0.9' \
        #                            '},{' \
        #                               '"title": "Rainfall",' \
        #                               '"unit": "mm", ' \
        #                               '"opposite": "true", ' \
        #                               '"min": 0, ' \
        #                               '"max": 300' \
        #                            '}] , ' \
        #                 '"timeseries": [{  ' \
        #                                   '"name": "NDVI LT Avg",' \
        #                                   '"type": "line", ' \
        #                                   '"color": "#0000FF", ' \
        #                                   '"dashStyle": "Dot", ' \
        #                                   '"lineWidth": 2,  ' \
        #                                   '"data": [ 0.682429414148,0.665795900748,0.676792722328,0.679051417212,0.67749200162,0.675859547696,0.690964958864,0.713044955724,0.730121381764,0.762949236784,0.771540240408,0.786731403608,0.810586347168,0.811921311132,0.81605310452,0.810409428016,0.805994611068,0.794733260956,0.786224346984,0.779756948712,0.761564045884,0.754823617124,0.766585143812,0.785626437156,0.783121682604,0.788527801396,0.783964658024,0.780348056976,0.786888467424,0.78249986266,0.773902528352,0.769902292912,0.767212274208,0.749625495404,0.725021359528,0.701504558356 ] ' \
        #                                 '},{' \
        #                                   '"name": "2014 NDVI FLT",' \
        #                                   '"type": "line", ' \
        #                                   '"color": "0 158 0", ' \
        #                                   '"dashStyle": "Solid", ' \
        #                                   '"lineWidth": 2,  ' \
        #                                   '"data": [ 0.712062652872,0.70030905262,0.702135272652,0.724906517728,0.734870678716,0.697523288816,0.740597622068,0.76381709024,0.779385112424,0.806405660996,0.828472708724,0.817024394072,0.828586687244,0.853539141696,0.816409218736,0.806515582148,0.818801761188,0.815976032044,0.821417105848,0.780959175648,0.721066951896,0.74492574836,0.8137755414,0.783673285768,0.800044382656,0.829115502856,0.846606379212,0.840695975932,0.837681983244,0.84627264206,0.855277682732,0.832560596228,0.83627795148,0.784619065412,0.735257231628,0.742863495436 ] ' \
        #                                 '},{  ' \
        #                                   '"name": "NDVI LT Max",' \
        #                                   '"type": "line", ' \
        #                                   '"color": "0 117 0", ' \
        #                                   '"dashStyle": "Dot", ' \
        #                                   '"lineWidth": 2,  ' \
        #                                   '"data": [ 0.754279989012,0.740387087492,0.73948480766,0.748570860528,0.768685911604,0.76194239598,0.774810013996,0.79494651616,0.812892312924,0.834063333028,0.840643558788,0.852169437432,0.871287274536,0.874501746172,0.882002197428,0.873734922108,0.873594469804,0.864482701792,0.856139248952,0.863340143616,0.847142375052,0.838947196316,0.839489254836,0.855931932036,0.845945561324,0.852995592064,0.857437039748,0.854838371288,0.856289171124,0.847283429036,0.837323322824,0.83644673198,0.835083018324,0.823158594168,0.797529070148,0.769986082952 ] ' \
        #                                 '},{  ' \
        #                                   '"name": "NDVI LT Min","type": "line", "color": "0 117 0", "dashStyle": "Dot", "lineWidth": 2,  ' \
        #                                   '"data": [ 0.593016729232,0.58264918316,0.604970530916,0.60829359214,0.586810406392,0.587016467632,0.59653795142,0.617739290808,0.635957464064,0.671430368984,0.685795848428,0.700389781956,0.72296171504,0.728800020928,0.727054294796,0.7004881692,0.699403633604,0.679096019776,0.66385470812,0.637215491872,0.604477626776,0.60098086406,0.632033301504,0.670075314244,0.67648466378,0.690335003204,0.66805333996,0.66012219272,0.684134723296,0.682981858136,0.680139458228,0.682533844324,0.683593240292,0.654764600472,0.636241115456,0.628774044184 ] ' \
        #                                 '},{  ' \
        #                                   '"name": "Rain LT Avg","yAxis": 1, "type": "column", "color": "255 0 0", ' \
        #                                   '"tooltip": { "valueSuffix": " mm"}, ' \
        #                                   '"data": [ 9.82575569304,10.8701424405,17.2014440244,21.4522647901,21.9089571371,27.4563261089,38.9160137601,44.3764992871,49.2297555361,65.2618863877,65.4977371719,61.6682863982,52.8434593803,64.8513792788,57.7788706787,55.7619844872,47.1656050122,54.0385988777,47.852471453,43.8664277399,51.4886923993,51.8721109701,57.3762900082,54.1176670634,48.5540201169,64.0870011641,59.3985258917,58.4831268884,69.2455626333,75.4914391849,62.5487881444,49.042549017,25.2966790054,23.236262802,12.8735497626,9.02715393771 ] ' \
        #                                 '},{  ' \
        #                                   '"name": "2014 Rain","yAxis": 1, "type": "column", "color": "0 0 255", ' \
        #                                   '"tooltip": { "valueSuffix": " mm"}, ' \
        #                                   '"data": [ 1.79759589889,4.43279992405,58.1308123945,21.8904228742,3.04111616966,47.7462231698,61.9103501498,41.1399094869,35.412017841,74.2559480988,97.8953605483,74.2271787896,67.8109949904,103.582567067,67.2348697893,64.567754045,61.1725569958,47.2133271422,23.9413495873,38.714883654,58.6170065269,41.7090696245,80.0464141368,42.2478712412,35.4303624449,56.6631198253,77.596176736,56.7892757642,98.0659947942,77.7210246818,86.7891318849,75.7514486024,33.0697945143,35.039122075,18.2669907359,7.49441711302 ] ' \
        #                                 '}] , ' \
        #                 '"xaxis": { "ticks":3, ' \
        #                            '"categories": ["20140101","20140111","20140121","20140201","20140211","20140221","20140301","20140311","20140321","20140401","20140411","20140421","20140501","20140511","20140521","20140601","20140611","20140621","20140701","20140711","20140721","20140801","20140811","20140821","20140901","20140911","20140921","20141001","20141011","20141021","20141101","20141111","20141121","20141201","20141211","20141221"]' \
        #                          '} ' \
        #             '}'
        #            # '"dates":["20140101","20140111","20140121","20140201","20140211","20140221","20140301","20140311","20140321","20140401","20140411","20140421","20140501","20140511","20140521","20140601","20140611","20140621","20140701","20140711","20140721","20140801","20140811","20140821","20140901","20140911","20140921","20141001","20141011","20141021","20141101","20141111","20141121","20141201","20141211","20141221"]' \


class TimeseriesProducts:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        db_products = querydb.get_timeseries_products()

        if db_products.__len__() > 0:
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
                if all_prod_mapsets.__len__() > 0:
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
                                dataset_dict = functions.row2dict(subproduct)
                                dataset_dict['mapsetcode'] = mapset
                                mapset_dict['timeseriesmapsetdatasets'].append(dataset_dict)

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


class GetColorSchemes:
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
                legend_dict = functions.row2dict(legend)
                # legend_dict = legend.__dict__
                legend_id = legend_dict['legend_id']
                legend_name = legend_dict['legend_name']
                default_legend = legend_dict['default_legend']

                if default_legend == 'True':
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
                                      "<td height=10 style='padding:0; margin:0; background-color: " + \
                                      color_html + ";'>&nbsp</td>"
                colorschemeHTML = colorschemeHTML + '</tr></table>'

                legend_dict['default_legend'] = defaultlegend
                legend_dict['defaulticon'] = defaulticon
                legend_dict['colorschemeHTML'] = colorschemeHTML
                # legend_dict['legendHTML'] = legendHTML

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

        if db_products.__len__() > 0:
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
                                                                  echo=False)

                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                dataset_dict['mapsetcode'] = mapset

                                # dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                # completeness = dataset.get_dataset_normalized_info()
                                # dataset_dict['datasetcompleteness'] = completeness

                                mapset_dict['mapsetdatasets'].append(dataset_dict)
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
        elif getparams['logtype'] == 'service':
            if getparams['service'] == 'eumetcast':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.get_eumetcast.log'
            if getparams['service'] == 'internet':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.get_internet.log'
            if getparams['service'] == 'ingest':
                logfilename = es_constants.es2globals['log_dir']+'apps.acquisition.ingestion.log'
            if getparams['service'] == 'processing':
                logfilename = es_constants.es2globals['log_dir']+'apps.processing.processing.log'
            if getparams['service'] == 'dbsync':
                logfilename = '/var/log/bucardo/log.bucardo'
            if getparams['service'] == 'datasync':
                logfilename = '/var/log/rsyncd.log'

        # logfilepath = es_constants.es2globals['log_dir']+logfilename
        # Display only latest (most recent file) - see #69-1
        #logfilenames = sorted(glob.glob(logfilepath + "*"), key=str, reverse=False)
        logfilenames = sorted(glob.glob(logfilename), key=str, reverse=False)

        # print sorted(logfilenames, key=str, reverse=False)
        if len(logfilenames) > 0:
            logfilecontent_all = ''
            logfilecontent = ''
            for logfilepath in logfilenames:
                if os.path.isfile(logfilepath):
                    logfile = open(logfilepath, 'r')
                    logfilecontent = logfile.read()
                    logfilecontent = logfilecontent.replace('\'', '"')
                    logfilecontent = logfilecontent.replace(chr(10), '<br />')
                    logfilecontent = logfilecontent.replace(' TRACE ', '<b style="color:gray"> TRACE </b>')
                    logfilecontent = logfilecontent.replace(' DEBUG ', '<b style="color:gray"> DEBUG </b>')
                    logfilecontent = logfilecontent.replace(' INFO ', '<b style="color:green"> INFO </b>')
                    logfilecontent = logfilecontent.replace(' WARNING ', '<b style="color:orange"> WARN </b>')
                    logfilecontent = logfilecontent.replace(' WARN ', '<b style="color:orange"> WARN </b>')
                    logfilecontent = logfilecontent.replace(' ERROR ', '<b style="color:red"> ERROR </b>')
                    logfilecontent = logfilecontent.replace(' CRITICAL ', '<b style="color:red"> FATAL </b>')
                    logfilecontent = logfilecontent.replace(' FATAL ', '<b style="color:red"> FATAL </b>')
                    logfilecontent = logfilecontent.replace(' CLOSED ', '<b style="color:brown"> CLOSED </b>')

                    logfilecontent_all += logfilecontent
        else:
            logfilecontent = 'NO LOG FILE PRESENT'

        logfilecontent_json = json.dumps(logfilecontent,
                                         ensure_ascii=False,
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

        logfile_json = '{"success":"true", "filename":\'' + logfilename + '\',"logfilecontent":\''+logfilecontent+'\'}'

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
            permitChangeMode = False

            # TODO: Use port 80?
            IP_port = ':22'

            if systemsettings['type_installation'].lower() == 'full':
                # Check if other PC is reachable and in which mode it is!
                if systemsettings['role'].lower() == 'pc2':
                    # Check connection to PC3
                    PC23_connection = functions.check_connection(systemsettings['ip_pc3'] + IP_port)

                    if PC23_connection:
                        status_PC3 = functions.get_remote_system_status(systemsettings['ip_pc3'])
                        if 'mode' in status_PC3:
                            Other_PC_mode = status_PC3['mode']
                        else:
                            PC3_Webserver_Status = False

                elif systemsettings['role'].lower() == 'pc3':
                    This_PC_mode = systemsettings['mode'].lower()

                    # Check connection to PC2
                    PC23_connection = functions.check_connection(systemsettings['ip_pc2'] + IP_port)
                    if PC23_connection:
                        status_PC2 = functions.get_remote_system_status(systemsettings['ip_pc2'])
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
                        permitChangeMode = False
                    if Other_PC_mode == 'recovery':
                        permitChangeMode = True
                    if Other_PC_mode == 'maintenance':
                        permitChangeMode = False
                else:
                    permitChangeMode = False

            elif This_PC_mode == 'maintenance' and newmode == 'recovery':
                permitChangeMode = True

            else:
                permitChangeMode = False

            if permitChangeMode:
                functions.setSystemSetting('mode', getparams['mode'])
                if newmode == 'recovery':
                    functions.setSystemSetting('data_sync', 'false')
                    functions.setSystemSetting('db_sync', 'false')
                elif newmode == 'nominal':
                    functions.setSystemSetting('data_sync', 'true')
                    functions.setSystemSetting('db_sync', 'true')

                # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
                from lib.python import reloadmodules
                reloadmodules.reloadallmodules()
                # Reloading the settings does not work well so set manually

                changemode_json = '{"success":"true", "message":"Mode changed!"}'
            else:
                changemode_json = '{"success":false, "message":"Changing to Mode NOT possible!"}'

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

            # Todo: call system service to change the version! PROBLEMS: answer back to browser!

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

        if themas.__len__() > 0:
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
            # print themaset
            if themaset:
                # print "thema changed"
                changethema_json = '{"success":"true", "message":"Thema changed!"}'
            else:
                changethema_json = '{"success":false, "error":"Changing thema in database error!"}'
        else:
            changethema_json = '{"success":false, "error":"No thema given!"}'

        return changethema_json


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


class GetVectorLayer:
    def __init__(self):
        self.lang = "eng"

    def GET(self):
        getparams = web.input()
        filename = getparams['file']
        # layerfilepath = '/srv/www/eStation2_Layers/'+filename
        layerfilepath = es_constants.estation2_layers_dir + os.path.sep + filename

        layerfile = open(layerfilepath, 'r')
        layerfilecontent = layerfile.read()
        return layerfilecontent


class SystemReport:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        filename = 'eStation-PS-Report_2015-05-13.tgz'
        reportfile = es_constants.es2globals['base_tmp_dir']+'/'+filename

        web.header('Content-Type', 'application/force-download')   # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition', 'attachment; filename=' + filename)  # force browser to show "Save as" dialog.
        f = open(reportfile, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        #return contents


class InstallReport:
    def __init__(self):
        self.lang = "eng"

    def POST(self):
        filename = 'eStation-PS-Report_2015-05-13.tgz'
        reportfile = es_constants.es2globals['base_tmp_dir']+'/'+filename

        web.header('Content-Type', 'application/force-download')   # 'application/x-compressed')
        web.header('Content-transfer-encoding', 'binary')
        web.header('Content-Disposition', 'attachment; filename=' + filename)  # force browser to show "Save as" dialog.
        f = open(reportfile, 'rb')
        while 1:
            buf = f.read(1024 * 8)
            if not buf:
                break
            yield buf
        #return contents


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
        settings['ip_pc1'] = systemsettings['ip_pc1']
        settings['ip_pc2'] = systemsettings['ip_pc2']
        settings['ip_pc3'] = systemsettings['ip_pc3']
        settings['dns_ip'] = systemsettings['dns_ip']
        settings['gateway_ip'] = systemsettings['gateway_ip']
        settings['lan_access_ip'] = systemsettings['lan_access_ip']
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
        #import StringIO
        import mapscript
        getparams = web.input()

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

        inputparams = web.input()
        for k, v in inputparams.iteritems():
            #print k + ':' + v
            owsrequest.setParameter(k.upper(), v)

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

        coords = map(float, inputparams.BBOX.split(","))
        llx = coords[0]
        lly = coords[1]
        urx = coords[2]
        ury = coords[3]
        productmap.setExtent(llx, lly, urx, ury)   # -26, -35, 60, 38

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
        if product_info.__len__() > 0:
            for row in product_info:
                scale_factor = row.scale_factor
                scale_offset = row.scale_offset
                nodata = row.nodata

        legend_info = querydb.get_legend_info(legendid=inputparams.legendid)
        if legend_info.__len__() > 0:
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
            if legend_steps.__len__() > 0:
                stepcount = 0
                for step in legend_steps:
                    stepcount += 1
                    min_step = int((step.from_step - scale_offset)/scale_factor)
                    max_step = int((step.to_step - scale_offset)/scale_factor)
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

        result_map_file = es_constants.apps_dir+'/analysis/MAP_result.map'
        if os.path.isfile(result_map_file):
            os.remove(result_map_file)
        # productmap.save(result_map_file)
        image = productmap.draw()
        # image.save(es_constants.apps_dir+'/analysis/'+filenamenoextention+'.png')

        contents = productmap.OWSDispatch(owsrequest)
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        #web.header = "Content-Type","%s; charset=utf-8"%content_type
        web.header('Content-type', 'image/png')
        #web.header('Content-transfer-encoding', 'binary')
        return content



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

        processing_chains_json = '{"success":false, "error":"No processing chains defined!"}'

        processing_chains = querydb.get_processing_chains()

        if processing_chains.__len__() > 0:
            processing_chains_dict_all = []

            for process in processing_chains:
                process_id = process.process_id
                process_dict = functions.row2dict(process)

                db_process_input_products = querydb.get_processingchains_input_products(process_id)
                process_dict['inputproducts'] = []
                if db_process_input_products.__len__() > 0:

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
                if db_process_output_products.__len__() > 0:
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
        db_products = querydb.get_products(echo=False)

        if db_products.__len__() > 0:
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
            system_service_script = es_constants.es2globals['status_system_dir']+os.sep+'service_system.py'
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
                       'defined_by': 'JRC',
                       'activated': 'false',
                       'provider': getparams['provider'],
                       'descriptive_name': getparams['prod_descriptive_name'],
                       'description': getparams['description'],
                       'category_id': getparams['category_id'],
                       'frequency_id': 'undefined',
                       'date_format': 'undefined',
                       'data_type_id': 'undefined',
                       'masked':'true'
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

        if ingestions.__len__() > 0:
            ingest_dict_all = []
            for row in ingestions:
                ingest_dict = functions.row2dict(row)

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
                    dataset = Dataset(**kwargs)
                    completeness = dataset.get_dataset_normalized_info()
                    ingest_dict['completeness'] = completeness
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

        if dataacquisitions.__len__() > 0:
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
