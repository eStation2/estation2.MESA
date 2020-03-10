#!/usr/bin/python

# if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from builtins import open
from builtins import round
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import str
from past.utils import old_div
import sys
import os

# TODO: This turns of caching, remove!!!
# import sys
# sys.dont_write_bytecode = True

os.umask(0000)

cur_dir = os.path.dirname(__file__)
if cur_dir not in sys.path:
    sys.path.append(cur_dir)

import shutil
import datetime
import json
import glob
import time
import calendar
import numpy as NP
import base64
import configparser
import subprocess
from subprocess import *
from multiprocessing import *

import matplotlib as mpl

mpl.use('Agg')
mpl.rcParams['savefig.pad_inches'] = 0

from matplotlib import pyplot as plt

from lib.python import reloadmodules
from config import es_constants
from database import querydb
from database import crud

from apps.acquisition import get_eumetcast
from apps.acquisition import acquisition
from apps.processing import processing  # Comment in WINDOWS version!
from apps.productmanagement.datasets import Dataset
from apps.es2system import es2system
from apps.productmanagement.datasets import Frequency
from apps.productmanagement.products import Product
from apps.productmanagement import requests
from apps.analysis import generateLegendHTML
from apps.analysis.getTimeseries import (getTimeseries, getFilesList)
# from multiprocessing import (Process, Queue)
from apps.tools import ingest_historical_archives as iha

from lib.python import functions
from lib.python import es_logging as log

logger = log.my_logger(__name__)

WEBPY_COOKIE_NAME = "webpy_session_id"


def GetLogos():
    logos_dict_all = []
    logos = querydb.get_logos()
    if hasattr(logos, "__len__") and logos.__len__() > 0:
        for logo in logos:
            logofilepath = es_constants.estation2_logos_dir + os.path.sep + logo['logo_filename'].encode('utf-8').decode()
            if os.path.exists(logofilepath):
                logofile = open(logofilepath, 'rb')
                logofilecontent = logofile.read()
                encoded = base64.b64encode(logofilecontent)
                # encoded = base64.b64encode(open(logofilepath, "rb").read())
                filename, file_extension = os.path.splitext(logofilepath)
                if file_extension == '.png':
                    mime = 'png'
                elif file_extension == '.jpg':
                    mime = 'jpeg'
                elif file_extension == '.gif':
                    mime = 'gif'
                src = "data:image/" + mime + ";base64," + encoded.decode()
            else:
                src = ''

            logo = {
                'logo_id': logo['logo_id'],
                'logo_filename': logo['logo_filename'],
                'logo_description': logo['logo_description'],
                'active': logo['active'],
                'deletable': logo['deletable'],
                'defined_by': logo['defined_by'],
                'isdefault': logo['isdefault'],
                'orderindex_defaults': logo['orderindex_defaults'],
                'src': src,
                'width': '20%',
                'height': '60px'
            }

            logos_dict_all.append(logo)

        logos_json = json.dumps(logos_dict_all,
                                ensure_ascii=False,
                                # encoding='utf-8',
                                sort_keys=True,
                                indent=4,
                                separators=(', ', ': '))

        logos_json = '{"success":"true", "total":' + str(logos.__len__()) + ',"logos":' + logos_json + '}'
    else:
        logos_json = '{"success":"true", "total":' + str(logos.__len__()) + ',"logos":[]}'

    return logos_json


def IngestArchive(params):
    # from apps.es2system import service_ingest_archive as sia
    # service = params['service']
    task = params['task']
    # # if task == 'run':
    # #     task = 'start'
    # print task

    pid_file = es_constants.es2globals['ingest_archive_pid_filename']
    ingestarchive_daemon = es2system.IngestArchiveDaemon(pid_file, dry_run=False)
    status = ingestarchive_daemon.status()
    if status:
        message = 'Ingest Archive service is running'
    else:
        message = 'Ingest Archive service is not running'

    ingestarchive_service_script = es_constants.es2globals['system_service_dir'] + os.sep + 'service_ingest_archive.py'
    if task == 'stop':
        if status:
            os.system("python " + ingestarchive_service_script + " stop")
            message = 'Ingest Archive service stopped'
        else:
            message = 'Ingest Archive service is already down'

    elif task == 'run':
        if not status:
            os.system("python " + ingestarchive_service_script + " start")
            message = 'Ingest Archive service started'
        else:
            message = 'Ingest Archive service was already up'

    elif task == 'restart':
        # os.system("python " + ingestarchive_service_script + " restart")
        os.system("python " + ingestarchive_service_script + " stop")
        os.system("python " + ingestarchive_service_script + " start")
        message = 'Ingest Archive service restarted'

    status = ingestarchive_daemon.status()

    running = 'false'
    if status:
        running = 'true'
    response = '{"success":"true", "running":"' + running + '", "message":"' + message + '"}'
    # running = sia.service_ingest_archive(command=task)
    #
    # if not running:
    #     if task == 'status':
    #         response = '{"success":"false", "running":"false", "message":"Ingest archive is not running!"}'
    #     else:
    #         response = '{"success":"false", "message":"Ingest archive stopped!"}'
    # else:
    #     response = '{"success":"true", "running":"true", "message":"Ingest archive is running!"}'

    # task = params['task']
    # running = 'false'
    # if task == 'run':
    #     iha.ingest_historical_archives(input_dir=None, dry_run=False)
    #     running = 'true'
    # message = 'Ingest Archive service is running'
    # response = '{"success":"true", "running":"' + running + '", "message":"' + message + '"}'
    return response


def ChangeThema(thema):
    functions.setSystemSetting('thema', thema)

    # Set thema in database by activating the thema products, ingestion and processes.
    themaset = querydb.set_thema(thema)

    if themaset:
        themaproducts = querydb.get_thema_products(thema=thema)
        if hasattr(themaproducts, "__len__") and themaproducts.__len__() > 0:
            for themaproduct in themaproducts:
                productcode = themaproduct['productcode']
                version = themaproduct['version']
                checkCreateSubproductDir(productcode, version)

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
            setThemaOtherPC = functions.setThemaOtherPC(otherPC, thema)
            if not setThemaOtherPC:
                message = '<B>Thema NOT set on other pc</B>, ' + otherPC + ' because of an error on the other pc. Please set the Thema manually on the other pc!'
        else:
            message = '<B>Thema NOT set on other pc</B>, ' + otherPC + ' because there is no connection. Please set the Thema manually on the other pc!'

    if themaset:
        changethema_json = '{"success":"true", "message":"Thema changed on this PC!</BR>' + message + '"}'
    else:
        changethema_json = '{"success":false, "error":"Changing thema in database error!"}'

    return changethema_json


def checkCreateSubproductDir(productcode, version):
    subproducts = querydb.get_product_subproducts(productcode=productcode, version=version)
    if hasattr(subproducts, "__len__") and subproducts.__len__() > 0:
        for subproduct in subproducts:
            subproductcode = subproduct['subproductcode']
            product_type = subproduct['product_type']
            if product_type == 'Ingest':
                mapsets = querydb.get_product_active_ingest_mapsets(productcode=productcode,
                                                                    subproductcode=subproductcode,
                                                                    version=version)
                for mapset in mapsets:
                    mapsetcode = mapset['mapsetcode']
                    subproductdir = functions.set_path_sub_directory(productcode,
                                                                     subproductcode,
                                                                     product_type,
                                                                     version,
                                                                     mapsetcode)
                    subproductdir = es_constants.es2globals['processing_dir'] + os.path.sep + subproductdir
                    functions.check_output_dir(subproductdir)
            else:
                mapsets = querydb.get_product_active_derived_mapsets(productcode=productcode,
                                                                     subproductcode=subproductcode,
                                                                     version=version)
                for mapset in mapsets:
                    mapsetcode = mapset['mapsetcode']
                    subproductdir = functions.set_path_sub_directory(productcode,
                                                                     subproductcode,
                                                                     product_type,
                                                                     version,
                                                                     mapsetcode)
                    subproductdir = es_constants.es2globals['processing_dir'] + os.path.sep + subproductdir
                    functions.check_output_dir(subproductdir)


def __checkCreateSubproductDir(productcode, version):
    subproducts = querydb.get_product_subproducts(productcode=productcode, version=version)
    mapsets = querydb.get_product_active_mapsets(productcode=productcode, version=version)
    if hasattr(subproducts, "__len__") and subproducts.__len__() > 0:
        if hasattr(mapsets, "__len__") and mapsets.__len__() > 0:
            for subproduct in subproducts:
                # subproduct = functions.row2dict(subproduct)
                subproductcode = subproduct['subproductcode']
                product_type = subproduct['product_type']
                for mapset in mapsets:
                    mapsetcode = mapset['mapsetcode']
                    subproductdir = functions.set_path_sub_directory(productcode,
                                                                     subproductcode,
                                                                     product_type,
                                                                     version,
                                                                     mapsetcode)
                    subproductdir = es_constants.es2globals['processing_dir'] + os.path.sep + subproductdir
                    functions.check_output_dir(subproductdir)


def UpdateProduct(productcode, version, activate):
    result = querydb.activate_deactivate_product(productcode=productcode,
                                                 version=version,
                                                 activate=activate, force=True)

    if result:
        if activate:
            checkCreateSubproductDir(productcode, version)

        updatestatus = '{"success":"true", "message":"Product updated!"}'
    else:
        updatestatus = '{"success":false, "message":"An error occured while updating the product!"}'

    return updatestatus


def DeleteProduct(productcode, version):
    # result = querydb.delete_product(productcode=productcode, version=version)
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    if productcode != '':
        product = {
            'productcode': productcode,
            'version': version
        }

        if crud_db.delete('product', **product):
            deletestatus = '{"success":true, "productcode": "' + productcode + '", "version": "' + version + '"' + \
                           ', "message":"Product and all its subproducts and definitions deleted!"}'
        else:
            deletestatus = '{"success":false, "message":"An error occured while deleting the product!"}'
    else:
        deletestatus = '{"success":false, "message":"No productcode given!"}'

    return deletestatus


def ResetUserSettings():
    usersettingsinifile = es_constants.es2globals['settings_dir'] + '/user_settings.ini'
    # usersettingsinifile = '/eStation2/settings/user_settings.ini'

    config_usersettings = configparser.ConfigParser()
    config_usersettings.read(['user_settings.ini', usersettingsinifile])

    for option in config_usersettings.options('USER_SETTINGS'):
        config_usersettings.set('USER_SETTINGS', option, '')

    # Writing our configuration file to 'example.cfg' - COMMENTS ARE NOT PRESERVED!
    with open(usersettingsinifile, 'wb') as configfile:
        config_usersettings.write(configfile)
        configfile.close()

    # The data_dir has been changed, delete all completeness_bars
    completeness_bars_dir = es_constants.base_local_dir + os.path.sep + 'completeness_bars/'
    for the_file in os.listdir(completeness_bars_dir):
        file_path = os.path.join(completeness_bars_dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error('UpdateUserSettings - could not delete completeness_bars file: ' + e)

    # ToDo: After changing the settings restart apache or reload all dependend modules to apply the new settings
    reloadmodules.reloadallmodules()

    # from config import es_constants as constantsreloaded
    updatestatus = '{"success":"true", "message":"System settings reset to factory settings!"}'

    return updatestatus


def UpdateUserSettings(params):
    systemsettings = functions.getSystemSettings()

    if sys.platform != 'win32':
        if systemsettings['type_installation'].lower() == 'jrc_online':
            factory_settings_filename = 'factory_settings_jrc_online.ini'
        else:
            factory_settings_filename = 'factory_settings.ini'
    else:
        factory_settings_filename = 'factory_settings_windows.ini'

    config_factorysettings = configparser.ConfigParser()
    config_factorysettings.read([factory_settings_filename,
                                 es_constants.es2globals['config_dir'] + '/' + factory_settings_filename])

    usersettingsfilepath = es_constants.es2globals['settings_dir'] + '/user_settings.ini'
    # usersettingsfilepath = '/eStation2/settings/user_settings.ini'
    config_usersettings = configparser.ConfigParser()
    config_usersettings.read(['user_settings.ini', usersettingsfilepath])

    for setting in params['systemsettings']:
        if setting in ('data_dir', 'ingest_dir', 'static_data_dir', 'archive_dir', 'eumetcast_files_dir',
                       'get_eumetcast_output_dir', 'get_internet_output_dir', 'proxy_host', 'proxy_port', 'proxy_user',
                       'proxy_userpwd'):
            if setting == 'data_dir' and (
                    ((config_usersettings.get('USER_SETTINGS', setting, 0) == '' and params['systemsettings'][
                        setting] != config_factorysettings.get('FACTORY_SETTINGS', setting, 0))
                     or (config_usersettings.get('USER_SETTINGS', setting, 0) != '' and params['systemsettings'][
                                setting] != config_usersettings.get('USER_SETTINGS', setting, 0)
                     ))):
                # The data_dir has been changed, delete all completeness_bars
                completeness_bars_dir = es_constants.base_local_dir + os.path.sep + 'completeness_bars/'
                for the_file in os.listdir(completeness_bars_dir):
                    file_path = os.path.join(completeness_bars_dir, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        logger.error('UpdateUserSettings - could not delete completeness_bars file: ' + e)

            if config_factorysettings.has_option('FACTORY_SETTINGS', setting) \
                    and config_factorysettings.get('FACTORY_SETTINGS', setting, 0) == params['systemsettings'][setting]:
                config_usersettings.set('USER_SETTINGS', setting, '')
            elif config_usersettings.has_option('USER_SETTINGS', setting):
                config_usersettings.set('USER_SETTINGS', setting, params['systemsettings'][setting])

    # Writing our configuration file to 'example.cfg' - COMMENTS ARE NOT PRESERVED!
    with open(usersettingsfilepath, 'wb') as configfile:
        config_usersettings.write(configfile)
        configfile.close()

    reloadmodules.reloadallmodules()

    updatestatus = '{"success":"true", "message":"System settings updated!"}'

    return updatestatus


def getRunningRequestJobs():
    success = True
    message = ''
    list_of_jobs = []
    dirnames = os.listdir(es_constants.es2globals['request_jobs_dir'])
    # dirnames = glob.glob(os.path.join(es_constants.es2globals['request_jobs_dir'], "*"))
    for dirname in dirnames:
        dirpath = os.path.join(es_constants.es2globals['request_jobs_dir'], dirname)
        if os.path.isdir(dirpath):
            requestid = dirname
            jobstatus = statusRequestJob(requestid)
            if jobstatus['status'].lower() in ['stopped']:  # 'finished', 'stopped', 'error', 'running'
                deleteJobDir(requestid)
            # elif jobstatus['status'].lower() in ['error']:
            #     # No internet connection or proxy settings missing!
            #     # Putting the job on Paused is not possible, so delete the job and send a message to the user!
            #     # resp = json.loads(pauseRequestJob(requestid))
            #     # if resp['success']:
            #     #     jobstatus = statusRequestJob(requestid)
            #     #     list_of_jobs.append(jobstatus)
            #     # else:
            #     #     list_of_jobs.append(jobstatus)
            #     # deleteJobDir(requestid)
            #     success = False
            #     message = 'Error connecting to the server, please check if your network is connected to the internet or uses a proxy. Set your proxy settings under the system tab!'
            else:
                list_of_jobs.append(jobstatus)

    response = {'success': success,
                'requests': list_of_jobs,
                'message': message
                }

    response_json = json.dumps(response,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
    return response_json


def archiveRequestJob(requestid):
    functions.check_output_dir(es_constants.es2globals['request_job_archive_dir'])
    # TODO: set permissions to 777 on request_job_archive_dir

    # Move request job directory to archive directory
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M')
    shutil.move(es_constants.es2globals['request_jobs_dir'] + os.path.sep + requestid,
                es_constants.es2globals['request_job_archive_dir'] + os.path.sep + requestid + '_' + st)
    # Move request file to archive directory
    shutil.move(es_constants.es2globals['requests_dir'] + os.path.sep + requestid + '.req',
                es_constants.es2globals['request_job_archive_dir'] + os.path.sep + requestid + '_' + st + '.req')


def deleteJobDir(requestid):
    shutil.rmtree(es_constants.es2globals['request_jobs_dir'] + os.path.sep + requestid, ignore_errors=True)
    os.remove(es_constants.es2globals['requests_dir'] + os.path.sep + requestid + '.req')


def statusRequestJob(requestid):
    message = 'Missing requestid.'
    jobstatus = 'error'
    totfiles = 0
    totok = 0
    totko = 0
    mapsetcode = ''
    subproductcode = ''

    requestinfo = requestid.split('_')
    level = requestinfo[len(requestinfo) - 1]
    productcode = requestinfo[0]
    version = requestinfo[1]
    if level == 'mapset':
        mapsetcode = requestinfo[2]
    elif level == 'dataset':
        mapsetcode = requestinfo[2]
        subproductcode = requestinfo[3]

    if requestid != '':
        p1_jobid = requestid
        p2_action = 'status'
        p3_datapath = es_constants.es2globals['processing_dir']  # '/eStation2/mydata/processing/'     #
        p4_jobspath = es_constants.es2globals['request_jobs_dir']
        p5_requestfile = ''  # mandatory but empty for status action

        db_product_info = querydb.get_product_native(productcode=productcode, version=version)
        descriptive_name = ''
        if hasattr(db_product_info, "__len__") and db_product_info.__len__() > 0:
            for row in db_product_info:
                prod_dict = functions.row2dict(row)
                descriptive_name = prod_dict['descriptive_name']

        try:
            # command = 'java -jar ' + es_constants.es2globals['estation_sync_file'] \
            #           + ' ' + '"' + p1_jobid + '"' \
            #           + ' ' + '"' + p2_action + '"' \
            #           + ' ' + '"' + p3_datapath + '"' \
            #           + ' ' + '"' + p4_jobspath + '"' \
            #           + ' ' + '"' + p5_requestfile + '"'
            # print command
            # status = os.popen(command).readlines()  # returns a ';' delimited string with format "<jobstatus> <totfiles> <ok> <ko>"
            # status = os.system(command)

            args = [es_constants.es2globals['estation_sync_file'],
                    p1_jobid,
                    p2_action,
                    p3_datapath,
                    p4_jobspath,
                    p5_requestfile
                    ]

            if sys.platform.startswith('win'):
                job = Popen(['java', '-jar'] + args, shell=True, stdin=None, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            else:
                job = Popen(['java', '-jar'] + args, stdout=PIPE, stderr=STDOUT)  # .pid

            statusresult = job.communicate()

            status = statusresult[0].split(';')
            if status[0] == 'Error':
                jobstatus = 'error'  # status[2]
                datestatus = status[1]
                totfiles = None
                totok = None
                totko = None
            elif len(status) >= 3:
                jobstatus = status[0].split(':')[0]
                datestatus = status[1]
                totfiles = status[2].split(':')[1]
                totok = status[3].split(':')[1]
                totko = status[4].split(':')[1]
            else:
                jobstatus = status[0].split(':')[0]
                datestatus = status[1]
                totfiles = None
                totok = None
                totko = None

            message = 'Status info request: ' + requestid

            # statusresult = job.stdout.readline().rstrip("\n\r")   # Not good, creates defunct process with no kill
            # job.poll()
            # job.terminate()
            # job.kill()

        except subprocess.CalledProcessError:
            message = 'Error getting the status of the request: ' + requestid
        # finally:
        #     job.terminate()
        # job.kill()

    response = {'requestid': requestid,
                'prod_descriptive_name': descriptive_name,
                'productcode': productcode,
                'version': version,
                'mapsetcode': mapsetcode,
                'subproductcode': subproductcode,
                'level': level,
                'status': jobstatus,  # 'Running' 'Paused' 'Finished' 'Stopped'
                'totfiles': totfiles,
                'totok': totok,
                'totko': totko,
                'message': message
                }

    return response


def pauseRequestJob(requestid):
    # requestid = params['requestid']
    message = 'Missing requestid.'
    success = False
    status = 'running'

    if requestid != '':
        requestfilename = requestid + '.req'
        p1_jobid = requestid
        p2_action = 'pause'
        p3_datapath = es_constants.es2globals['processing_dir']  # '/eStation2/mydata/processing'    #
        p4_jobspath = es_constants.es2globals['request_jobs_dir']
        p5_requestfile = es_constants.es2globals['requests_dir'] + os.path.sep + requestfilename
        try:
            # command = 'java -jar ' + es_constants.es2globals['estation_sync_file'] \
            #           + ' ' + '"' + p1_jobid + '"' \
            #           + ' ' + '"' + p2_action + '"' \
            #           + ' ' + '"' + p3_datapath + '"' \
            #           + ' ' + '"' + p4_jobspath + '"' \
            #           + ' ' + '"' + p5_requestfile + '"'
            # # print command
            # os.system(command)

            args = [es_constants.es2globals['estation_sync_file'],
                    p1_jobid,
                    p2_action,
                    p3_datapath,
                    p4_jobspath,
                    p5_requestfile
                    ]

            job = Popen(['nohup', 'java', '-jar'] + args)

            # time.sleep(6)
            pausingjob = True
            counter = 0
            while pausingjob and counter <= 3:
                counter += 1
                time.sleep(4)
                jobstatus = statusRequestJob(requestid)
                status = jobstatus['status'].lower()
                if jobstatus['status'].lower() in ['paused', 'defunct']:  # 'finished', 'stopped', 'error', 'running'
                    success = True
                    pausingjob = False
                    message = 'Paused request: ' + requestid
                # elif jobstatus['status'].lower() in ['error']:
                #     pausingjob = False
                #     message = 'Error pausing request: ' + requestid + ' job status: ' + jobstatus['status'].lower()
                else:
                    message = 'Error pausing request: ' + requestid + ' job status: ' + jobstatus['status'].lower()
        except:
            message = 'Exception error pausing request: ' + requestid + ' job status: ' + jobstatus['status'].lower()

    response = {'success': success,
                'status': status,
                'message': message,
                'requestid': requestid}

    response_json = json.dumps(response,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
    return response_json


def restartRequestJob(requestid):
    # requestid = params['requestid']
    message = 'Missing requestid.'
    success = False
    status = 'paused'
    proxy_host = es_constants.es2globals['proxy_host']
    proxy_port = es_constants.es2globals['proxy_port']
    proxy_user = es_constants.es2globals['proxy_user']
    proxy_userpwd = es_constants.es2globals['proxy_userpwd']
    requestfilename = requestid + '.req'

    if requestid != '':
        p1_jobid = requestid
        p2_action = 'restart'
        p3_datapath = es_constants.es2globals['processing_dir']  # '/eStation2/mydata/processing'  #
        p4_jobspath = es_constants.es2globals['request_jobs_dir']
        p5_requestfile = es_constants.es2globals['requests_dir'] + os.path.sep + requestfilename
        try:
            # command = 'java -jar ' + es_constants.es2globals['estation_sync_file'] \
            #           + ' ' + '"' + p1_jobid + '"' \
            #           + ' ' + '"' + p2_action + '"' \
            #           + ' ' + '"' + p3_datapath + '"' \
            #           + ' ' + '"' + p4_jobspath + '"' \
            #           + ' ' + '"' + p5_requestfile + '"'
            # # print command
            # os.system(command)

            if proxy_host.strip() != '' and proxy_port.strip() != '':
                args = [es_constants.es2globals['estation_sync_file'],
                        p1_jobid,
                        p2_action,
                        p3_datapath,
                        p4_jobspath,
                        p5_requestfile,
                        proxy_host,
                        proxy_port,
                        proxy_user,
                        proxy_userpwd
                        ]
            else:
                args = [es_constants.es2globals['estation_sync_file'],
                        p1_jobid,
                        p2_action,
                        p3_datapath,
                        p4_jobspath,
                        p5_requestfile
                        ]

            job = Popen(['nohup', 'java', '-jar'] + args)

            # time.sleep(6)
            restartingjob = True
            counter = 0
            while restartingjob and counter <= 3:
                counter += 1
                time.sleep(12)
                jobstatus = statusRequestJob(requestid)
                status = jobstatus['status'].lower()
                if jobstatus['status'].lower() in ['running']:  # 'finished', 'stopped', 'error', 'running'
                    success = True
                    restartingjob = False
                    message = 'Restarted request: ' + requestid
                elif jobstatus['status'].lower() in ['error']:
                    restartingjob = False
                    message = 'Error connecting to the server, please check if your network is connected to the internet or uses a proxy. Set your proxy settings under the system tab!'
                else:
                    message = 'Error restarting request: ' + requestid + ' job status: ' + jobstatus['status'].lower()
        except:
            message = 'Exception error restarting request: ' + requestid + ' job status: ' + jobstatus['status'].lower()

    response = {'success': success,
                'status': status,
                'message': message,
                'requestid': requestid}

    response_json = json.dumps(response,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
    return response_json


def deleteRequestJob(requestid):
    # requestid = params['requestid']
    message = 'Missing requestid.'
    success = False

    if requestid != '':
        p1_jobid = requestid
        p2_action = 'stop'
        p3_datapath = es_constants.es2globals['processing_dir']  # '/eStation2/mydata/processing' #
        p4_jobspath = es_constants.es2globals['request_jobs_dir']
        p5_requestfile = ''
        try:
            jobstatus = statusRequestJob(requestid)
            if jobstatus['status'].lower() in ['finished', 'stopped',
                                               'error']:  # 'finished', 'stopped', 'error', 'running'
                success = True
                message = 'Request deleted: ' + requestid
                deleteJobDir(requestid)
            else:
                # command = 'java -jar ' + es_constants.es2globals['estation_sync_file'] \
                #           + ' ' + '"' + p1_jobid + '"' \
                #           + ' ' + '"' + p2_action + '"' \
                #           + ' ' + '"' + p3_datapath + '"' \
                #           + ' ' + '"' + p4_jobspath + '"' \
                #           + ' ' + '"' + p5_requestfile + '"'
                # print command
                # os.system(command)

                args = [es_constants.es2globals['estation_sync_file'],
                        p1_jobid,
                        p2_action,
                        p3_datapath,
                        p4_jobspath,
                        p5_requestfile
                        ]

                job = Popen(['nohup', 'java', '-jar'] + args)

                stoppingjob = True
                counter = 0
                while stoppingjob and counter <= 3:
                    counter += 1
                    time.sleep(8)
                    jobstatus = statusRequestJob(requestid)
                    if jobstatus['status'].lower() in ['stopped']:  # 'finished', 'stopped', 'error', 'running'
                        success = True
                        stoppingjob = False
                        message = 'Request stopped and deleted: ' + requestid
                        deleteJobDir(requestid)
                    elif jobstatus['status'].lower() in ['error']:
                        success = False
                        stoppingjob = False
                        message = 'Error stopping request: ' + requestid + ' job status: ' + jobstatus['status'].lower()
                    else:
                        message = 'Stopping request: ' + requestid + ' job status: ' + jobstatus['status'].lower()
        except:
            message = 'Error stopping and deleting request: ' + requestid

    response = {'success': success,
                'message': message,
                'requestid': requestid}

    response_json = json.dumps(response,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
    return response_json


def createRequestJob(params):
    productcode = None
    version = None
    mapsetcode = None
    subproductcode = None
    requestid = None
    requestfilename = None
    createnewrequest = False
    proxy_host = es_constants.es2globals['proxy_host']
    proxy_port = es_constants.es2globals['proxy_port']
    proxy_user = es_constants.es2globals['proxy_user']
    proxy_userpwd = es_constants.es2globals['proxy_userpwd']

    message = 'Missing request parameters.'

    functions.check_output_dir(es_constants.es2globals['request_jobs_dir'])
    # TODO: set permissions to 777 on request_jobs_dir

    if "level" in params:  # hasattr(params, "level"):
        if params['level'] == 'product':
            productcode = params['productcode']
            version = params['version']
            requestid = params['productcode'] + '_' + params['version'] + '_' + params['level']
        elif params['level'] == 'mapset':
            productcode = params['productcode']
            version = params['version']
            mapsetcode = params['mapsetcode']
            requestid = params['productcode'] + '_' + params['version'] + '_' + params[
                'mapsetcode'] + '_' + params['level']
        elif params['level'] == 'dataset':
            productcode = params['productcode']
            version = params['version']
            mapsetcode = params['mapsetcode']
            subproductcode = params['subproductcode']
            requestid = params['productcode'] + '_' + params['version'] + '_' + params['mapsetcode'] + '_' + \
                        params['subproductcode'] + '_' + params['level']

        # Check if same request exists and has not finished
        # In the es_constants.es2globals['request_jobs_dir'] check first if a directory exists
        # with the same name as requestid and check the job status in 'finished' or 'stopped'
        # if true then move the existing and finished job to the jobarchive directory and create a new request
        # else don't create a new request and send a message to the user that the request is already existing
        # and is still running.
        if os.path.isdir(es_constants.es2globals['request_jobs_dir'] + os.path.sep + requestid):
            jobstatus = statusRequestJob(requestid)
            if jobstatus['status'].lower() in ['finished', 'stopped']:  # 'finished', 'stopped', 'error', 'running'
                message = 'Request already exists and has finished. Existing request is deleted. New request created.'
                createnewrequest = True
                deleteJobDir(requestid)
            else:
                message = 'Request already exists and has not finished yet. No new request created.'
        else:
            message = 'Request does not exists. New request created.'
            createnewrequest = True

        if createnewrequest:
            request = requests.create_request(productcode,
                                              version,
                                              mapsetcode=mapsetcode,
                                              subproductcode=subproductcode,
                                              dekad_frequency=int(params['dekad_frequency']),
                                              daily_frequency=int(params['daily_frequency']),
                                              high_frequency=int(params['high_frequency']))

            request_json = json.dumps(request,
                                      ensure_ascii=False,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

            # ts = time.time()
            # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H%M')
            # requestfilename = requestid + '_' + st + '.req'
            requestfilename = requestid + '.req'
            with open(es_constants.es2globals['requests_dir'] + os.path.sep + requestfilename, 'w+') as f:
                f.write(request_json)
            f.close()

            p1_jobid = requestid
            p2_action = 'start'
            p3_datapath = es_constants.es2globals['processing_dir']  # '/eStation2/mydata/processing'    #
            p4_jobspath = es_constants.es2globals['request_jobs_dir']
            p5_requestfile = es_constants.es2globals['requests_dir'] + os.path.sep + requestfilename

            if proxy_host.strip() != '' and proxy_port.strip() != '':
                args = [es_constants.es2globals['estation_sync_file'],
                        p1_jobid,
                        p2_action,
                        p3_datapath,
                        p4_jobspath,
                        p5_requestfile,
                        proxy_host,
                        proxy_port,
                        proxy_user,
                        proxy_userpwd
                        ]
            else:
                args = [es_constants.es2globals['estation_sync_file'],
                        p1_jobid,
                        p2_action,
                        p3_datapath,
                        p4_jobspath,
                        p5_requestfile
                        ]

            if sys.platform.startswith('win'):
                job = Popen(['java', '-jar'] + args, shell=True, stdin=None, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            else:
                job = Popen(['nohup', 'java', '-jar'] + args,
                            # close_fds=True,
                            # shell=True,    # pass args as string
                            stdout=PIPE,
                            stderr=STDOUT)  # .pid

            # time.sleep(6)
            creatingjob = True
            counter = 0
            while creatingjob and counter <= 3:
                counter += 1
                time.sleep(12)
                jobstatus = statusRequestJob(requestid)
                if jobstatus['status'].lower() in ['running']:  # 'finished', 'stopped', 'error', 'running'
                    creatingjob = False
                    message = 'Created request: ' + requestid
                elif jobstatus['status'].lower() in ['error']:
                    # No internet connection or proxy settings missing!
                    # Putting the job on Paused is not possible, so delete the job and send a message to the user!
                    # resp = json.loads(pauseRequestJob(requestid))
                    # if resp['success']:
                    #     jobstatus = statusRequestJob(requestid)
                    #     list_of_jobs.append(jobstatus)
                    # else:
                    #     list_of_jobs.append(jobstatus)
                    # deleteJobDir(requestid)
                    createnewrequest = False
                    creatingjob = False
                    message = 'Error connecting to the server, please check if your network is connected to the internet or uses a proxy. Set your proxy settings under the system tab!'
                else:
                    createnewrequest = False
                    # todo: Delete job dir?
                    message = 'Error creating request!'

            # jobstatus = job.poll()
            # answer = job.stdout.readline()

            # command = 'python -u ./apps/tools/createSyncJob.py '
            # job = os.system(command)
            #
            # *****************************************
            # DIRECT JAVA CALL
            # *****************************************
            #
            # # Command as string - creates job but waits until finished! NOT WORKING PROPERLY!
            # command = 'java -jar ' + es_constants.es2globals['estation_sync_file'] \
            #           + ' ' + '"' + p1_jobid + '"' \
            #           + ' ' + '"' + p2_action + '"' \
            #           + ' ' + '"' + p3_datapath + '"' \
            #           + ' ' + '"' + p4_jobspath + '"' \
            #           + ' ' + '"' + p5_requestfile + '"' \
            #           + ' ' + '"' + proxy_host + '"' \
            #           + ' ' + '"' + proxy_port + '"' \
            #           + ' ' + '"' + proxy_user + '"' \
            #           + ' ' + '"' + proxy_userpwd + '"'
            #
            # # job = os.system(command)    # os.system waits until the job finishes and does not read response of job!
            # job = os.popen(command).readlines()  # Should return 'Job created' but waits until the job finishes.
            #
            # Command as list
            # Creates job and reads response but when finishing this function call createRequestJob,
            # all PIDs of subprocess are killed! NOT WORKING PROPERLY!
            #
            # command = ['java', '-jar', es_constants.es2globals['estation_sync_file'],
            #            '"' + p1_jobid + '"',
            #            '"' + p2_action + '"',
            #            '"' + p3_datapath + '"',
            #            '"' + p4_jobspath + '"',
            #            '"' + p5_requestfile + '"',
            #            '"' + proxy_host + '"',
            #            '"' + proxy_port + '"',
            #            '"' + proxy_user + '"',
            #            '"' + proxy_userpwd + '"'
            #            ]
            #
            #
            # args = [es_constants.es2globals['estation_sync_file'],
            #         p1_jobid,
            #         p2_action,
            #         p3_datapath,
            #         p4_jobspath,
            #         p5_requestfile,
            #         proxy_host,
            #         proxy_port,
            #         proxy_user,
            #         proxy_userpwd
            #         ]
            #
            # job = subprocess.Popen(['java', '-jar'] + list(args),
            #                        # close_fds=True,
            #                        # shell=True,    # pass args as string
            #                        stdout=subprocess.PIPE,
            #                        stderr=subprocess.STDOUT)    # .pid
            # job.poll()
            # line = job.stdout.readline()  # Returns 'Job created'
            #
            #
            # *************************************************************************************************
            # CALL python script createSyncJob.py which creates another process that creates the request job
            # *************************************************************************************************
            #
            # command = 'python ./apps/tools/createSyncJob.py ' + es_constants.es2globals['estation_sync_file'] \
            #           + ' ' + '"' + p1_jobid + '"' \
            #           + ' ' + '"' + p2_action + '"' \
            #           + ' ' + '"' + p3_datapath + '"' \
            #           + ' ' + '"' + p4_jobspath + '"' \
            #           + ' ' + '"' + p5_requestfile + '"' \
            #           + ' ' + '"' + proxy_host + '"' \
            #           + ' ' + '"' + proxy_port + '"' \
            #           + ' ' + '"' + proxy_user + '"' \
            #           + ' ' + '"' + proxy_userpwd + '"'
            #
            #
            # args = ['-p0 ' + es_constants.es2globals['estation_sync_file'],
            #         '-p1 ' + p1_jobid,
            #         '-p2 ' + p2_action,
            #         '-p3 ' + p3_datapath,
            #         '-p4 ' + '"' + p4_jobspath + '"',
            #         '-p5 ' + '"' + p5_requestfile + '"',
            #         '-p6 ' + '"' + proxy_host + '"',
            #         '-p7 ' + '"' + proxy_port + '"',
            #         '-p8 ' + '"' + proxy_user + '"',
            #         '-p9 ' + '"' + proxy_userpwd + '"'
            #         ]
            #
            # argslist = ['/srv/www/eStation2/apps/tools/eStationSync.jar',
            #             "vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset",
            #             "start",
            #             "/home/webtklooju/mydata/processing/",
            #             "/eStation2/requests/requestjobs",
            #             "/eStation2/requests/vgt-ndvi_sv2-pv2.2_SPOTV-IGAD-1km_1monmin_dataset.req",
            #             "10.168.209.72",
            #             "8012"]
            #
            # job_pid = subprocess.Popen([sys.executable, './apps/tools/createSyncJob.py']).pid
            #
            # job = subprocess.check_call([sys.executable, './apps/tools/createSyncJob.py'] + list(args))
            # job = subprocess.call([sys.executable, '-u ', './apps/tools/createSyncJob.py'] + args)
            # job = subprocess.Popen([sys.executable, '-u ', './apps/tools/createSyncJob.py'] + args,
            #                        stdout=subprocess.PIPE,
            #                        stderr=subprocess.STDOUT)
            # # job.wait()
            # job.poll()
            # line = job.stdout.readline()  # Returns 'Job created'
            #
            #
            # DIRECT JAVA CALL - NOT WORKING
            #
            # command = ['java -jar', es_constants.es2globals['estation_sync_file']]
            #
            # stdin = ' ' + '"' + p1_jobid + '"' \
            #         + ' ' + '"' + p2_action + '"' \
            #         + ' ' + '"' + p3_datapath + '"' \
            #         + ' ' + '"' + p4_jobspath + '"' \
            #         + ' ' + '"' + p5_requestfile + '"' \
            #         + ' ' + '"' + proxy_host + '"' \
            #         + ' ' + '"' + proxy_port + '"' \
            #         + ' ' + '"' + proxy_user + '"' \
            #         + ' ' + '"' + proxy_userpwd + '"'
            #
            # print command
            # os.system(command)
            # os.spawnl(os.P_NOWAIT, command)  # run in the background
            #
            # subprocess.call(command)
            # from subprocess import STDOUT, PIPE
            # proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # stdout, stderr = proc.communicate(stdin)
            # print ('Job start: "' + stdout + '"')
            # print ('Job start error: "' + stderr + '"')

    response = {'success': createnewrequest,
                'message': message,
                'requestid': requestid,
                'requestfile': requestfilename}

    response_json = json.dumps(response,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
    return response_json


def execServiceTaskWin(getparams):
    message = ''

    if getparams.service == 'eumetcast':
        command = 'NET START | find "estation2 - eumetcast"'
        status = os.system(command)  # is 0 if success
        if not status:
            status = True
        else:
            status = False

        # logger.info(getparams.service)
        # logger.info('status: ' + str(status))

        if getparams.task == 'stop':
            if status:
                os.system('NET STOP "estation2 - eumetcast"')
                message = 'Get_eumetcast service stopped'
            else:
                message = 'Get_eumetcast service is already down'

        elif getparams.task == 'run':
            if not status:
                os.system('NET START "estation2 - eumetcast"')
                message = 'Get_eumetcast service started'
            else:
                message = 'Get_eumetcast service was already up'

        elif getparams.task == 'restart':
            os.system('NET STOP "estation2 - eumetcast"')
            os.system('NET START "estation2 - eumetcast"')
            message = 'Get_eumetcast service restarted'

    if getparams.service == 'internet':
        command = 'NET START | find "estation2 - get internet"'
        status = os.system(command)  # is 0 if success
        if not status:
            status = True
        else:
            status = False

        if getparams.task == 'stop':
            if status:
                os.system('NET STOP "estation2 - get internet"')
                message = 'Get_internet service stopped'
            else:
                message = 'Get_internet service is already down'
        elif getparams.task == 'run':
            if not status:
                os.system('NET START "estation2 - get internet"')
                message = 'Get_internet service started'
            else:
                message = 'Get_internet service was already up'

        elif getparams.task == 'restart':
            os.system('NET STOP "estation2 - get internet"')
            os.system('NET START "estation2 - get internet"')
            message = 'Get_internet service restarted'

    if getparams.service == 'ingest':
        command = 'NET START | find "estation2 - ingestion"'
        status = os.system(command)  # is 0 if success
        if not status:
            status = True
        else:
            status = False

        if getparams.task == 'stop':
            if status:
                os.system('NET STOP "estation2 - ingestion"')
                message = 'Ingestion service stopped'
            else:
                message = 'Ingestion service is already down'

        elif getparams.task == 'run':
            if not status:
                os.system('NET START "estation2 - ingestion"')
                message = 'Ingestion service started'
            else:
                message = 'Ingestion service was already up'

        elif getparams.task == 'restart':
            os.system('NET STOP "estation2 - ingestion"')
            os.system('NET START "estation2 - ingestion"')
            message = 'ingest service restarted'

    if getparams.service == 'processing':
        command = 'NET START | find "estation2 - processing"'
        status = os.system(command)  # is 0 if success
        if not status:
            status = True
        else:
            status = False

        if getparams.task == 'stop':
            if status:
                os.system('NET STOP "estation2 - processing"')
                message = 'Processing service stopped'
            else:
                message = 'Processing service is already down'

        elif getparams.task == 'run':
            if not status:
                os.system('NET START "estation2 - processing"')
                message = 'Processing service started'
            else:
                message = 'Processing service was already up'

        elif getparams.task == 'restart':
            os.system('NET STOP "estation2 - processing"')
            os.system('NET START "estation2 - processing"')
            message = 'Processing service restarted'

    if getparams.service == 'system':
        command = 'NET START | find "estation2 - es2system"'
        status = os.system(command)  # is 0 if success
        if not status:
            status = True
        else:
            status = False

        if getparams.task == 'stop':
            if status:
                os.system('NET STOP "estation2 - es2system"')
                message = 'System service stopped'
            else:
                message = 'System service is already down'
        #
        elif getparams.task == 'run':
            if not status:
                os.system('NET START "estation2 - es2system"')
                message = 'System service started'
            else:
                message = 'System service was already up'

        elif getparams.task == 'restart':
            os.system('NET STOP "estation2 - es2system"')
            os.system('NET START "estation2 - es2system"')
            message = 'System service restarted'

    return message


def execServiceTask(getparams):
    message = ''
    dryrun = False
    if getparams.service == 'eumetcast':
        # Define pid file and create daemon
        pid_file = es_constants.get_eumetcast_pid_filename
        eumetcast_daemon = acquisition.GetEumetcastDaemon(pid_file, dry_run=dryrun)
        eumetcast_service_script = es_constants.es2globals['acq_service_dir'] + os.sep + 'service_get_eumetcast.py'
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
        internet_service_script = es_constants.es2globals['acq_service_dir'] + os.sep + 'service_get_internet.py'
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
        ingest_service_script = es_constants.es2globals['acq_service_dir'] + os.sep + 'service_ingestion.py'
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
        processing_service_script = es_constants.es2globals['proc_service_dir'] + os.sep + 'service_processing.py'
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
        system_service_script = es_constants.es2globals['system_service_dir'] + os.sep + 'service_system.py'
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

    return message


def getWorkspaceMaps(workspaceid, userid, withoutmaskfeature=False):
    wsmaps = querydb.get_workspace_maps(workspaceid, userid)
    maps = []
    outmaskfeature = None
    if hasattr(wsmaps, "__len__") and wsmaps.__len__() > 0:
        for row_dict in wsmaps:
            if withoutmaskfeature:
                outmaskfeature = row_dict['outmaskfeature']

            wsmap = {
                'workspaceid': row_dict['workspaceid'],
                'userid': row_dict['userid'],
                'map_tpl_id': row_dict['map_tpl_id'],
                'parent_tpl_id': row_dict['parent_tpl_id'],
                'map_tpl_name': row_dict['map_tpl_name'],
                'istemplate': row_dict['istemplate'],
                'mapviewposition': row_dict['mapviewposition'],
                'mapviewsize': row_dict['mapviewsize'],
                'productcode': row_dict['productcode'],
                'subproductcode': row_dict['subproductcode'],
                'productversion': row_dict['productversion'],
                'mapsetcode': row_dict['mapsetcode'],
                'productdate': row_dict['productdate'],
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
                'showtoolbar': row_dict['showtoolbar'],
                'showgraticule': row_dict['showgraticule'],
                'showtimeline': row_dict['showtimeline'],
                'scalelineobjposition': row_dict['scalelineobjposition'],
                'vectorlayers': row_dict['vectorlayers'],
                'outmask': row_dict['outmask'],
                'outmaskfeature': outmaskfeature,
                'auto_open': row_dict['auto_open'],
                'zoomextent': row_dict['zoomextent'],
                'mapsize': row_dict['mapsize'],
                'mapcenter': row_dict['mapcenter']
            }
            maps.append(wsmap)
    return maps


def getWorkspaceGraphs(workspaceid, userid, withwkt=False):
    wsgraphs = querydb.get_workspace_graphs(workspaceid, userid)
    graphs = []
    wkt_geom = None
    if hasattr(wsgraphs, "__len__") and wsgraphs.__len__() > 0:
        for row_dict in wsgraphs:
            if withwkt:
                wkt_geom = row_dict['wkt_geom']

            graph_tpl_id = row_dict['graph_tpl_id']

            yaxesGraph = querydb.get_graph_yaxes(graph_tpl_id)
            yAxes = []
            if hasattr(yaxesGraph, "__len__") and yaxesGraph.__len__() > 0:
                for row in yaxesGraph:
                    yAxe = {'graph_tpl_id': graph_tpl_id,
                            'id': row['yaxe_id'],
                            'title': row['title'],
                            'title_color': row['title_color'],
                            'title_font_size': row['title_font_size'],
                            'min': row['min'],
                            'max': row['max'],
                            'unit': row['unit'],
                            'opposite': row['opposite'],
                            'aggregation_type': row['aggregation_type'],
                            'aggregation_min': row['aggregation_min'],
                            'aggregation_max': row['aggregation_max']
                            }

                    yAxes.append(yAxe)
            # print (yAxes)
            params = {
                'userid': row_dict['userid'],
                'graph_tpl_id': graph_tpl_id,
                'graphtype': row_dict['graph_type']
            }
            graphDrawProps = querydb.get_graph_drawproperties(params)
            graphproperties = []
            if hasattr(graphDrawProps, "__len__") and graphDrawProps.__len__() > 0:
                for row in graphDrawProps:
                    graphproperty = {'graph_tpl_id': graph_tpl_id,
                                     'graph_type': row['graph_type'],
                                     'graph_width': row['graph_width'],
                                     'graph_height': row['graph_height'],
                                     'graph_title': row['graph_title'],
                                     'graph_title_font_size': row['graph_title_font_size'],
                                     'graph_title_font_color': row['graph_title_font_color'],
                                     'graph_subtitle': row['graph_subtitle'],
                                     'graph_subtitle_font_size': row['graph_subtitle_font_size'],
                                     'graph_subtitle_font_color': row['graph_subtitle_font_color'],
                                     'legend_position': row['legend_position'],
                                     'legend_font_size': row['legend_font_size'],
                                     'legend_font_color': row['legend_font_color'],
                                     'xaxe_font_size': row['xaxe_font_size'],
                                     'xaxe_font_color': row['xaxe_font_color']
                                     }

                    graphproperties.append(graphproperty)
            # print (graphproperties)

            graphTSDrawProps = querydb.get_graph_tsdrawprops(row_dict['graph_tpl_id'])
            tsdrawprops = []
            if hasattr(graphTSDrawProps, "__len__") and graphTSDrawProps.__len__() > 0:
                for row in graphTSDrawProps:
                    props = {'graph_tpl_id': graph_tpl_id,
                             'productcode': row['productcode'],
                             'subproductcode': row['subproductcode'],
                             'version': row['version'],
                             'tsname_in_legend': row['tsname_in_legend'],
                             'charttype': row['charttype'],
                             'color': row['color'],
                             'linestyle': row['linestyle'],
                             'linewidth': row['linewidth'],
                             'yaxe_id': row['yaxe_id']
                             }

                    tsdrawprops.append(props)
            # print (tsdrawprops)

            graph = {
                'userid': row_dict['userid'],
                'workspaceid': row_dict['workspaceid'],
                'graph_tpl_id': row_dict['graph_tpl_id'],
                'parent_tpl_id': row_dict['parent_tpl_id'],
                'graph_tpl_name': row_dict['graph_tpl_name'],
                'istemplate': row_dict['istemplate'],
                'graphviewposition': row_dict['graphviewposition'],
                'graphviewsize': row_dict['graphviewsize'],
                'graph_type': row_dict['graph_type'],
                'selectedtimeseries': row_dict['selectedtimeseries'],
                'yearts': row_dict['yearts'],
                'tsfromperiod': row_dict['tsfromperiod'],
                'tstoperiod': row_dict['tstoperiod'],
                'yearstocompare': row_dict['yearstocompare'],
                'tsfromseason': row_dict['tsfromseason'],
                'tstoseason': row_dict['tstoseason'],
                'wkt_geom': wkt_geom,
                'selectedregionname': row_dict['selectedregionname'],
                'disclaimerobjposition': row_dict['disclaimerobjposition'],
                'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                'logosobjposition': row_dict['logosobjposition'],
                'logosobjcontent': row_dict['logosobjcontent'],
                'showobjects': row_dict['showobjects'],
                'showtoolbar': row_dict['showtoolbar'],
                'auto_open': row_dict['auto_open'],
                'yAxes': yAxes,
                'graphproperties': graphproperties,
                'tsdrawprops': tsdrawprops
            }
            graphs.append(graph)
    return graphs


def getWorkspaceMapsAndGraphs(params):
    if 'workspaceid' in params:
        maps = getWorkspaceMaps(params['workspaceid'], params['userid'], True)
        graphs = getWorkspaceGraphs(params['workspaceid'], params['userid'], True)

        workspace = {
            'userid': params['userid'],
            'workspaceid': params['workspaceid'],
            'workspacename': params['workspacename'],
            'pinned': params['pinned'],
            'showindefault': params['showindefault'],
            'shownewgraph': params['shownewgraph'],
            'showbackgroundlayer': params['showbackgroundlayer'],
            'isrefworkspace': params['isrefworkspace'],
            'maps': maps,
            'graphs': graphs
        }

        workspace_json = json.dumps(workspace,
                                    ensure_ascii=False,
                                    # encoding='utf-8',
                                    sort_keys=True,
                                    indent=4,
                                    separators=(', ', ': '))

        workspace_json = '{"success":"true","workspace":' + workspace_json + '}'

    else:
        workspace_json = '{"success":false, "error":"Workspaceid not given!"}'

    return workspace_json


def getUserWorkspaces(params):
    workspaces_dict_all = []

    if 'userid' in params:
        userworkspaces = querydb.get_user_workspaces(params['userid'])
        if hasattr(userworkspaces, "__len__") and userworkspaces.__len__() > 0:
            for row_dict in userworkspaces:
                # maps = getWorkspaceMaps(row_dict['workspaceid'], row_dict['userid'])
                # graphs = getWorkspaceGraphs(row_dict['workspaceid'], row_dict['userid'])

                workspace = {
                    'userid': row_dict['userid'],
                    'workspaceid': row_dict['workspaceid'],
                    'workspacename': row_dict['workspacename'],
                    'pinned': row_dict['pinned'],
                    'showindefault': row_dict['showindefault'],
                    'shownewgraph': row_dict['shownewgraph'],
                    'showbackgroundlayer': row_dict['showbackgroundlayer'],
                    'isrefworkspace': False,
                    'maps': [],
                    'graphs': []
                }

                workspaces_dict_all.append(workspace)

            workspaces_json = json.dumps(workspaces_dict_all,
                                         ensure_ascii=False,
                                         # encoding='utf-8',
                                         sort_keys=True,
                                         indent=4,
                                         separators=(', ', ': '))

            workspaces_json = '{"success":"true", "total":' \
                              + str(userworkspaces.__len__()) \
                              + ',"userworkspaces":' + workspaces_json + '}'

        else:
            workspaces_json = '{"success":"true", "total":' \
                              + str(userworkspaces.__len__()) \
                              + ',"userworkspaces":[]}'
    else:
        workspaces_json = '{"success":false, "error":"Userid not given!"}'

    return workspaces_json


def getRefWorkspaces(params):
    workspaces_dict_all = []
    refuser = es_constants.es2globals['jrc_ref_user']  # 'jrc_ref'

    userworkspaces = querydb.get_user_workspaces(refuser)
    if hasattr(userworkspaces, "__len__") and userworkspaces.__len__() > 0:
        for row_dict in userworkspaces:
            # maps = getWorkspaceMaps(row_dict['workspaceid'], row_dict['userid'])
            # graphs = getWorkspaceGraphs(row_dict['workspaceid'], row_dict['userid'])

            workspace = {
                'userid': row_dict['userid'],
                'workspaceid': row_dict['workspaceid'],
                'workspacename': row_dict['workspacename'],
                'pinned': row_dict['pinned'],
                'showindefault': row_dict['showindefault'],
                'shownewgraph': row_dict['shownewgraph'],
                'showbackgroundlayer': row_dict['showbackgroundlayer'],
                'isrefworkspace': True,
                'maps': [],
                'graphs': []
            }

            workspaces_dict_all.append(workspace)

        workspaces_json = json.dumps(workspaces_dict_all,
                                     ensure_ascii=False,
                                     # encoding='utf-8',
                                     separators=(',', ': '))  # sort_keys=True, indent=4,

        workspaces_json = '{"success":"true", "total":' \
                          + str(userworkspaces.__len__()) \
                          + ',"refworkspaces":' + workspaces_json + '}'

    else:
        workspaces_json = '{"success":"true", "total":' \
                          + str(userworkspaces.__len__()) \
                          + ',"refworkspaces":[]}'

    return workspaces_json


def saveWorkspaceGraphs(wsgraphs, workspaceid):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if type(workspaceid) is not int:
        workspaceid = int(workspaceid)

    for wsgraph in wsgraphs:
        wsgraphSettings = {
            'userid': wsgraph['userid'],
            'workspaceid': workspaceid,
            # 'graph_tpl_id': wsgraph['graph_tpl_id'],
            'parent_tpl_id': wsgraph['parent_tpl_id'],
            'graph_tpl_name': wsgraph['graph_tpl_name'],
            'istemplate': functions.str_to_bool(wsgraph['istemplate']),
            'graphviewposition': wsgraph['graphviewposition'],
            'graphviewsize': wsgraph['graphviewsize'],
            'graph_type': wsgraph['graph_type'],
            'selectedtimeseries': wsgraph['selectedtimeseries'],
            'yearts': wsgraph['yearts'],
            'tsfromperiod': wsgraph['tsfromperiod'],
            'tstoperiod': wsgraph['tstoperiod'],
            'yearstocompare': wsgraph['yearstocompare'],
            'tsfromseason': wsgraph['tsfromseason'],
            'tstoseason': wsgraph['tstoseason'],
            'wkt_geom': wsgraph['wkt_geom'],
            'selectedregionname': wsgraph['selectedregionname'],
            'disclaimerobjposition': wsgraph['disclaimerobjposition'],
            'disclaimerobjcontent': wsgraph['disclaimerobjcontent'],
            'logosobjposition': wsgraph['logosobjposition'],
            'logosobjcontent': wsgraph['logosobjcontent'],
            'showobjects': functions.str_to_bool(wsgraph['showobjects']),
            'showtoolbar': functions.str_to_bool(wsgraph['showtoolbar'])
        }

        if type(wsgraph['graphproperties']) is list:
            graphproperties = wsgraph['graphproperties'][0]
        else:
            graphproperties = json.loads(wsgraph['graphproperties'])

        if type(wsgraph['yAxes']) is list:
            yaxes = wsgraph['yAxes']
        else:
            yaxes = json.loads(wsgraph['yAxes'])

        if type(wsgraph['tsdrawprops']) is list:
            tsdrawprops = wsgraph['tsdrawprops']
        else:
            tsdrawprops = json.loads(wsgraph['tsdrawprops'])

        createstatus = '{"success":false, "message":"Error saving the workspace Graph!"}'
        if crud_db.create('user_graph_templates', wsgraphSettings):
            createdGraphTpl = querydb.get_last_graph_tpl_id(wsgraph['userid'], workspaceid)
            graphproperties['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
            crud_db.create('user_graph_tpl_drawproperties', graphproperties)

            for yaxe in yaxes:
                yaxe['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                yaxe['yaxe_id'] = yaxe['id']
                if yaxe['min'] == '':
                    yaxe['min'] = None
                if yaxe['max'] == '':
                    yaxe['max'] = None
                yaxe['opposite'] = functions.str_to_bool(yaxe['opposite'])
                crud_db.create('user_graph_tpl_yaxes', yaxe)

            for tsdrawprop in tsdrawprops:
                tsdrawprop['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

            # Todo: use logger!
            createstatus = '{"success":true, "message":"Workspace Graph saved."}'


def saveWorkspaceMaps(wsmaps, workspaceid):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if type(workspaceid) is not int:
        workspaceid = int(workspaceid)

    for wsmap in wsmaps:
        productcode = ''
        if 'productcode' in wsmap:
            productcode = wsmap['productcode']

        subproductcode = ''
        if 'subproductcode' in wsmap:
            subproductcode = wsmap['subproductcode']

        productversion = ''
        if 'productversion' in wsmap:
            productversion = wsmap['productversion']

        mapsetcode = ''
        if 'mapsetcode' in wsmap:
            mapsetcode = wsmap['mapsetcode']

        legendid = None
        if 'legendid' in wsmap and wsmap['legendid'] != '':
            legendid = wsmap['legendid']

        wsmapSettings = {
            'userid': wsmap['userid'],
            'workspaceid': workspaceid,
            # 'map_tpl_id': None,
            'parent_tpl_id': wsmap['parent_tpl_id'],
            'map_tpl_name': wsmap['map_tpl_name'],
            'istemplate': functions.str_to_bool(wsmap['istemplate']),
            'mapviewposition': str(wsmap['mapviewposition']),
            'mapviewsize': wsmap['mapviewsize'],
            'productcode': productcode,
            'subproductcode': subproductcode,
            'productversion': productversion,
            'mapsetcode': mapsetcode,
            'productdate': wsmap['productdate'],
            'legendid': legendid,
            'legendlayout': wsmap['legendlayout'],
            'legendobjposition': wsmap['legendobjposition'],
            'showlegend': functions.str_to_bool(wsmap['showlegend']),
            'titleobjposition': wsmap['titleobjposition'],
            'titleobjcontent': wsmap['titleobjcontent'],
            'disclaimerobjposition': wsmap['disclaimerobjposition'],
            'disclaimerobjcontent': wsmap['disclaimerobjcontent'],
            'logosobjposition': wsmap['logosobjposition'],
            'logosobjcontent': wsmap['logosobjcontent'],
            'showobjects': functions.str_to_bool(wsmap['showobjects']),
            'showtoolbar': functions.str_to_bool(wsmap['showtoolbar']),
            'showgraticule': functions.str_to_bool(wsmap['showgraticule']),
            'showtimeline': functions.str_to_bool(wsmap['showtimeline']),
            'scalelineobjposition': wsmap['scalelineobjposition'],
            'vectorlayers': wsmap['vectorlayers'],
            'outmask': functions.str_to_bool(wsmap['outmask']),
            'outmaskfeature': wsmap['outmaskfeature'],
            'auto_open': functions.str_to_bool(wsmap['auto_open']),
            'zoomextent': wsmap['zoomextent'],
            'mapsize': wsmap['mapsize'],
            'mapcenter': wsmap['mapcenter']
        }

        if not crud_db.create('user_map_templates', wsmapSettings):
            # Todo: use logger!
            createstatus = '{"success":false, "message":"Error saving the workspace Map!"}'


def saveWorkspace(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace!"}'

    if 'userid' in params and 'workspacename' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename'],
            'pinned': functions.str_to_bool(params['pinned']),
            'shownewgraph': True,
            'showbackgroundlayer': False
        }

        if type(params['maps']) is list:
            wsmaps = params['maps']
        else:
            wsmaps = json.loads(params['maps'])

        if type(params['graphs']) is list:
            wsgraphs = params['graphs']
        else:
            wsgraphs = json.loads(params['graphs'])

        # print (wsgraphs)

        # If new user workspace, create new user workspace and get its workspaceid
        #   Insert all open/passed maps and graphs in the new workspace
        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                newworkspaceid = querydb.getCreatedUserWorkspace(params['userid'], params['workspacename'])
                # for row in createdWorkspace:
                #     newworkspaceid = row['lastworkspaceid']

                saveWorkspaceMaps(wsmaps, newworkspaceid)
                saveWorkspaceGraphs(wsgraphs, newworkspaceid)

                createstatus = '{"success":true, "message":"Workspace created!", "workspaceid": ' + str(
                    newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace!"}'
        # Else, it is an existing user workspace, update workspace settings
        #   Delete all the workspace maps and graphs
        #   Insert all open/passed maps and graphs in the workspace
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                workspaceinfo = {
                    'userid': params['userid'],
                    'workspaceid': int(params['workspaceid'])
                }
                if crud_db.delete('user_map_templates', **workspaceinfo):
                    saveWorkspaceMaps(wsmaps, params['workspaceid'])
                if crud_db.delete('user_graph_templates', **workspaceinfo):
                    saveWorkspaceGraphs(wsgraphs, params['workspaceid'])

                createstatus = '{"success":true, "message":"Workspace updated!", "workspaceid": ' + str(
                    params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No Workspace data given!"}'

    return createstatus


def importWorkspaces(params):
    if 'importfilename' in params:
        try:
            # print (params.userid)

            filename = params.importfilename + '.json'
            with open(es_constants.es2globals['base_tmp_dir'] + filename, 'w+') as f:
                f.write(params.workspacesfile)
            f.close()

            with open(es_constants.es2globals['base_tmp_dir'] + filename, 'r') as f:
                workspaces_dict = json.load(f)

            for workspace in workspaces_dict['workspaces']:
                workspace['isNewWorkspace'] = 'true'
                workspace['isrefworkspace'] = 'false'
                workspace['pinned'] = 'false'
                workspace['showindefault'] = 'false'
                workspace['userid'] = params.userid
                workspace['workspaceid'] = None
                for wsmap in workspace['maps']:
                    wsmap['userid'] = params.userid
                for wsgraph in workspace['graphs']:
                    wsgraph['userid'] = params.userid

                # print (workspace)
                saveWorkspace(workspace)

            success = True
        except:
            success = False
    else:
        success = False

    if success:
        status = '{"success":true,"message":"Workspaces imported!"}'
    else:
        status = '{"success":false, "message":"An error occured while importing the workspaces!"}'

    return status


def importJRCRefWorkspaces():
    try:
        filename = 'jrc_ref_workspaces.json'

        with open(es_constants.es2globals['base_dir'] + '/database/referenceWorkspaces/' + filename, 'r') as f:
            workspaces_dict = json.load(f)

        for workspace in workspaces_dict['workspaces']:
            workspace['isNewWorkspace'] = 'true'
            workspace['isrefworkspace'] = 'true'
            workspace['pinned'] = 'false'
            # workspace['showindefault'] = 'false'
            workspace['userid'] = es_constants.es2globals['jrc_ref_user']
            workspace['workspaceid'] = None
            for wsmap in workspace['maps']:
                wsmap['userid'] = es_constants.es2globals['jrc_ref_user']
            for wsgraph in workspace['graphs']:
                wsgraph['userid'] = es_constants.es2globals['jrc_ref_user']

            saveWorkspace(workspace)

        success = True
    except:
        success = False

    if success:
        status = '{"success":true,"message":"JRC reference workspaces imported!"}'
    else:
        status = '{"success":false, "message":"An error occured while importing the JRC reference workspaces!"}'

    return status


def saveWorkspacePin(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace pin change!"}'

    if 'userid' in params and 'workspaceid' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename'],
            'pinned': functions.str_to_bool(params['pinned'])
        }

        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                createdWorkspace = querydb.getCreatedUserWorkspace(params['userid'])
                for row in createdWorkspace:
                    newworkspaceid = row['lastworkspaceid']

                createstatus = '{"success":true, "message":"Workspace created on pin setting change!", "workspaceid": ' + str(
                    newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace on pin setting change!"}'
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                createstatus = '{"success":true, "message":"Workspace pin setting changed!", "workspaceid": ' + str(
                    params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No user data given when changing the workspace pin setting!"}'

    return createstatus


def saveWorkspaceName(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace when changing the workspace name!"}'

    if 'userid' in params and 'workspaceid' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename']
        }

        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                createdWorkspace = querydb.getCreatedUserWorkspace(params['userid'])
                for row in createdWorkspace:
                    newworkspaceid = row['lastworkspaceid']

                createstatus = '{"success":true, "message":"Workspace created when changing the workspace name!", "workspaceid": ' + str(
                    newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace when changing the workspace name!"}'
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                createstatus = '{"success":true, "message":"Workspace name updated!", "workspaceid": ' + str(
                    params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No user data given when changing the workspace name!"}'

    return createstatus


def saveWorkspaceInDefaultWS(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace In Default WS change!"}'

    if 'userid' in params and 'workspaceid' in params:
        workspace = {
            'userid': params['userid'],
            'workspaceid': int(params['workspaceid']),
            'workspacename': params['workspacename'],
            'showindefault': functions.str_to_bool(params['showindefault'])
        }

        if crud_db.update('user_workspaces', workspace):
            createstatus = '{"success":true, "message":"Workspace In Default WS setting changed!", "workspaceid": ' + str(
                params['workspaceid']) + '}'
        else:
            createstatus = '{"success":false, "message":"Error updating the Workspace on In Default WS setting!"}'

    else:
        createstatus = '{"success":false, "message":"No user data given when changing the workspace In Default WS setting!"}'

    return createstatus


def getMapTemplates(params):
    maptemplate_dict_all = []
    if 'userid' in params:
        usermaptemplates = querydb.get_user_map_templates(params['userid'])
        if hasattr(usermaptemplates, "__len__") and usermaptemplates.__len__() > 0:
            for row_dict in usermaptemplates:
                # row_dict = functions.row2dict(row)

                mapTemplate = {
                    'workspaceid': row_dict['workspaceid'],
                    'userid': row_dict['userid'],
                    'map_tpl_id': row_dict['map_tpl_id'],
                    'parent_tpl_id': row_dict['parent_tpl_id'],
                    'map_tpl_name': row_dict['map_tpl_name'],
                    'istemplate': row_dict['istemplate'],
                    'mapviewposition': row_dict['mapviewposition'],
                    'mapviewsize': row_dict['mapviewsize'],
                    'productcode': row_dict['productcode'],
                    'subproductcode': row_dict['subproductcode'],
                    'productversion': row_dict['productversion'],
                    'mapsetcode': row_dict['mapsetcode'],
                    'productdate': row_dict['productdate'],
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
                    'showtoolbar': row_dict['showtoolbar'],
                    'showgraticule': row_dict['showgraticule'],
                    'showtimeline': row_dict['showtimeline'],
                    'scalelineobjposition': row_dict['scalelineobjposition'],
                    'vectorlayers': row_dict['vectorlayers'],
                    'outmask': row_dict['outmask'],
                    'outmaskfeature': row_dict['outmaskfeature'],
                    'auto_open': row_dict['auto_open'],
                    'zoomextent': row_dict['zoomextent'],
                    'mapsize': row_dict['mapsize'],
                    'mapcenter': row_dict['mapcenter']
                }

                maptemplate_dict_all.append(mapTemplate)

            maptemplates_json = json.dumps(maptemplate_dict_all,
                                           ensure_ascii=False,
                                           # encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            maptemplates_json = '{"success":"true", "total":' \
                                + str(usermaptemplates.__len__()) \
                                + ',"usermaptemplates":' + maptemplates_json + '}'

        else:
            maptemplates_json = '{"success":true, "total":' \
                                + str(usermaptemplates.__len__()) \
                                + ',"usermaptemplates":[]}'
            # maptemplates_json = '{"success":true, "error":"No Map Templates defined for user!"}'   # OR RETURN A DEFAULT MAP TEMPLATE?????

    else:
        maptemplates_json = '{"success":false, "error":"Userid not given!"}'

    return maptemplates_json


def saveMapTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Map Template!"}'

    if 'userid' in params and 'map_tpl_name' in params:
        legendid = params['legendid']
        if params['legendid'] == '':
            legendid = None

        defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['userid'])
        if not defaultworkspaceid:
            return createstatus

        mapTemplate = {
            'userid': params['userid'],
            'workspaceid': defaultworkspaceid,
            # 'map_tpl_id': None,
            'map_tpl_name': params['map_tpl_name'],
            'istemplate': functions.str_to_bool(params['istemplate']),
            'mapviewposition': params['mapviewposition'],
            'mapviewsize': params['mapviewsize'],
            'productcode': params['productcode'],
            'subproductcode': params['subproductcode'],
            'productversion': params['productversion'],
            'mapsetcode': params['mapsetcode'],
            'productdate': params['productdate'],
            'legendid': legendid,
            'legendlayout': params['legendlayout'],
            'legendobjposition': params['legendobjposition'],
            'showlegend': functions.str_to_bool(params['showlegend']),
            'titleobjposition': params['titleobjposition'],
            'titleobjcontent': params['titleobjcontent'],
            'disclaimerobjposition': params['disclaimerobjposition'],
            'disclaimerobjcontent': params['disclaimerobjcontent'],
            'logosobjposition': params['logosobjposition'],
            'logosobjcontent': params['logosobjcontent'],
            'scalelineobjposition': params['scalelineobjposition'],
            'showobjects': functions.str_to_bool(params['showobjects']),
            'showtoolbar': functions.str_to_bool(params['showtoolbar']),
            'showgraticule': functions.str_to_bool(params['showgraticule']),
            'showtimeline': functions.str_to_bool(params['showtimeline']),
            'vectorlayers': params['vectorlayers'],
            'outmask': functions.str_to_bool(params['outmask']),
            'outmaskfeature': params['outmaskfeature'],
            'auto_open': functions.str_to_bool(params['auto_open']),
            'zoomextent': params['zoomextent'],
            'mapsize': params['mapsize'],
            'mapcenter': params['mapcenter']
        }

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_map_templates', mapTemplate):
                # createdMapTpl = crud_db.read('user_map_templates', **mapTemplate)
                createdMapTpl = querydb.get_last_map_tpl_id(params['userid'], defaultworkspaceid)
                updateMapTemplate = {
                    'userid': params['userid'],
                    'workspaceid': defaultworkspaceid,
                    'map_tpl_id': createdMapTpl[0]['map_tpl_id'],
                    'parent_tpl_id': createdMapTpl[0]['map_tpl_id']
                }
                # mapTemplate['map_tpl_id'] = createdMapTpl[0]['map_tpl_id']
                # mapTemplate['parent_tpl_id'] = createdMapTpl[0]['map_tpl_id']
                crud_db.update('user_map_templates', updateMapTemplate)
                createstatus = '{"success":true, "message":"Map Template created!", "map_tpl_id": ' + str(
                    createdMapTpl[0]['map_tpl_id']) + '}'
            else:
                createstatus = '{"success":false, "message":"Error saving the Map Template!"}'
        else:
            mapTemplate['map_tpl_id'] = params['parent_tpl_id']
            if crud_db.update('user_map_templates', mapTemplate):
                createstatus = '{"success":true, "message":"Map Template updated!"}'

    else:
        createstatus = '{"success":false, "message":"No Map Template data given!"}'

    return createstatus


def getGraphTemplates(params):
    graphtemplate_dict_all = []

    if 'userid' in params:
        usergraphtemplates = querydb.get_user_graph_templates(params['userid'])
        if hasattr(usergraphtemplates, "__len__") and usergraphtemplates.__len__() > 0:
            for row_dict in usergraphtemplates:
                # row_dict = functions.row2dict(row)

                graphTemplate = {
                    'userid': row_dict['userid'],
                    'workspaceid': row_dict['workspaceid'],
                    'graph_tpl_id': row_dict['graph_tpl_id'],
                    'parent_tpl_id': row_dict['parent_tpl_id'],
                    'graph_tpl_name': row_dict['graph_tpl_name'],
                    'istemplate': row_dict['istemplate'],
                    'graphviewposition': row_dict['graphviewposition'],
                    'graphviewsize': row_dict['graphviewsize'],
                    'graph_type': row_dict['graph_type'],
                    'selectedtimeseries': row_dict['selectedtimeseries'],
                    'yearts': row_dict['yearts'],
                    'tsfromperiod': row_dict['tsfromperiod'],
                    'tstoperiod': row_dict['tstoperiod'],
                    'yearstocompare': row_dict['yearstocompare'],
                    'tsfromseason': row_dict['tsfromseason'],
                    'tstoseason': row_dict['tstoseason'],
                    'wkt_geom': row_dict['wkt_geom'],
                    'selectedregionname': row_dict['selectedregionname'],
                    'disclaimerobjposition': row_dict['disclaimerobjposition'],
                    'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                    'logosobjposition': row_dict['logosobjposition'],
                    'logosobjcontent': row_dict['logosobjcontent'],
                    'showobjects': row_dict['showobjects'],
                    'showtoolbar': row_dict['showtoolbar'],
                    'auto_open': row_dict['auto_open']
                }

                graphtemplate_dict_all.append(graphTemplate)

            graphtemplates_json = json.dumps(graphtemplate_dict_all,
                                             ensure_ascii=False,
                                             # encoding='utf-8',
                                             sort_keys=True,
                                             indent=4,
                                             separators=(', ', ': '))

            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":' + graphtemplates_json + '}'

        else:
            graphtemplates_json = '{"success":"true", "total":0' \
                                  + ',"usergraphtemplates":[]}'
            # graphtemplates_json = '{"success":true, "error":"No Graph Templates defined for user!"}'  # OR RETURN A DEFAULT GRAPH TEMPLATE?????

    else:
        graphtemplates_json = '{"success":false, "error":"Userid not given!"}'

    return graphtemplates_json


def __getGraphTemplates(params):
    graphtemplate_dict_all = []

    if 'userid' in params:
        usergraphtemplates = querydb.get_user_graph_templates(params['userid'])
        if hasattr(usergraphtemplates, "__len__") and usergraphtemplates.__len__() > 0:
            for row_dict in usergraphtemplates:
                # row_dict = functions.row2dict(row)

                graphTemplate = {
                    'userid': row_dict['userid'],
                    'graph_tpl_name': row_dict['graph_tpl_name'],
                    'graphviewposition': row_dict['graphviewposition'],
                    'graphviewsize': row_dict['graphviewsize'],
                    'graph_type': row_dict['graph_type'],
                    'selectedtimeseries': row_dict['selectedtimeseries'],
                    'yearts': row_dict['yearts'],
                    'tsfromperiod': row_dict['tsfromperiod'],
                    'tstoperiod': row_dict['tstoperiod'],
                    'yearstocompare': row_dict['yearstocompare'],
                    'tsfromseason': row_dict['tsfromseason'],
                    'tstoseason': row_dict['tstoseason'],
                    'wkt_geom': row_dict['wkt_geom'],
                    'selectedregionname': row_dict['selectedregionname'],
                    'disclaimerobjposition': row_dict['disclaimerobjposition'],
                    'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                    'logosobjposition': row_dict['logosobjposition'],
                    'logosobjcontent': row_dict['logosobjcontent'],
                    'showobjects': row_dict['showobjects'],
                    'auto_open': row_dict['auto_open']
                }

                graphtemplate_dict_all.append(graphTemplate)

            graphtemplates_json = json.dumps(graphtemplate_dict_all,
                                             ensure_ascii=False,
                                             # encoding='utf-8',
                                             sort_keys=True,
                                             indent=4,
                                             separators=(', ', ': '))

            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":' + graphtemplates_json + '}'

        else:
            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":[]}'
            # graphtemplates_json = '{"success":true, "error":"No Graph Templates defined for user!"}'  # OR RETURN A DEFAULT GRAPH TEMPLATE?????

    else:
        graphtemplates_json = '{"success":false, "error":"Userid not given!"}'

    return graphtemplates_json


def saveGraphTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Graph Template!"}'

    if 'userid' in params and 'graph_tpl_name' in params:

        defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['userid'])
        if not defaultworkspaceid:
            return createstatus

        graphTemplate = {
            'userid': params['userid'],
            'workspaceid': defaultworkspaceid,
            # 'graph_tpl_id': params['graph_tpl_id'],
            'graph_tpl_name': params['graph_tpl_name'],
            'istemplate': functions.str_to_bool(params['istemplate']),
            'graphviewposition': params['graphviewposition'],
            'graphviewsize': params['graphviewsize'],
            'graph_type': params['graph_type'],
            'selectedtimeseries': params['selectedtimeseries'],
            'yearts': params['yearts'],
            'tsfromperiod': params['tsfromperiod'],
            'tstoperiod': params['tstoperiod'],
            'yearstocompare': params['yearstocompare'],
            'tsfromseason': params['tsfromseason'],
            'tstoseason': params['tstoseason'],
            'wkt_geom': params['wkt_geom'],
            'selectedregionname': params['selectedregionname'],
            'disclaimerobjposition': params['disclaimerobjposition'],
            'disclaimerobjcontent': params['disclaimerobjcontent'],
            'logosobjposition': params['logosobjposition'],
            'logosobjcontent': params['logosobjcontent'],
            'showobjects': functions.str_to_bool(params['showobjects']),
            'showtoolbar': functions.str_to_bool(params['showtoolbar'])
        }

        graphproperties = json.loads(params['graphproperties'])
        yaxes = json.loads(params['yAxes'])
        tsdrawprops = json.loads(params['tsdrawprops'])

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_graph_templates', graphTemplate):
                # createdGraphTpl = crud_db.read('user_graph_templates', **graphTemplate)
                createdGraphTpl = querydb.get_last_graph_tpl_id(params['userid'], defaultworkspaceid)
                updateGraphTemplate = {
                    'userid': params['userid'],
                    'workspaceid': defaultworkspaceid,
                    'graph_tpl_id': createdGraphTpl[0]['graph_tpl_id'],
                    'parent_tpl_id': createdGraphTpl[0]['graph_tpl_id']
                }

                crud_db.update('user_graph_templates', updateGraphTemplate)

                graphproperties['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                crud_db.create('user_graph_tpl_drawproperties', graphproperties)

                for yaxe in yaxes:
                    yaxe['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                    yaxe['yaxe_id'] = yaxe['id']
                    if yaxe['min'] == '':
                        yaxe['min'] = None
                    if yaxe['max'] == '':
                        yaxe['max'] = None
                    yaxe['opposite'] = functions.str_to_bool(yaxe['opposite'])
                    crud_db.create('user_graph_tpl_yaxes', yaxe)

                for tsdrawprop in tsdrawprops:
                    tsdrawprop['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                    crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

                createstatus = '{"success":true, "message":"Graph Template created!", "graph_tpl_id": ' + str(
                    createdGraphTpl[0]['graph_tpl_id']) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the Graph Template!"}'
        else:
            if params['parent_tpl_id'] != '':
                graphTemplate['graph_tpl_id'] = params['parent_tpl_id']
            else:
                graphTemplate['graph_tpl_id'] = params['graph_tpl_id']

            if crud_db.update('user_graph_templates', graphTemplate):
                graphproperties['graph_tpl_id'] = params['parent_tpl_id']
                crud_db.update('user_graph_tpl_drawproperties', graphproperties)

                crud_db.delete('user_graph_tpl_yaxes', **{'graph_tpl_id': params['parent_tpl_id']})
                for yaxe in yaxes:
                    yaxe['graph_tpl_id'] = params['parent_tpl_id']
                    yaxe['yaxe_id'] = yaxe['id']
                    if yaxe['min'] == '':
                        yaxe['min'] = None
                    if yaxe['max'] == '':
                        yaxe['max'] = None
                    yaxe['opposite'] = functions.str_to_bool(yaxe['opposite'])
                    crud_db.create('user_graph_tpl_yaxes', yaxe)

                crud_db.delete('user_graph_tpl_timeseries_drawproperties', **{'graph_tpl_id': params['parent_tpl_id']})
                for tsdrawprop in tsdrawprops:
                    tsdrawprop['graph_tpl_id'] = params['parent_tpl_id']
                    crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

                createstatus = '{"success":true, "message":"Graph Template updated!"}'
            else:
                createstatus = '{"success":false, "message":"Error updating the Graph Template!"}'
    else:
        createstatus = '{"success":false, "message":"No Graph Template data given!"}'

    return createstatus


def __saveGraphTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Graph Template!"}'

    if 'userid' in params and 'graph_tpl_name' in params:

        # graphProperties:{"localRefresh": false, "title": "Polygon", "subtitle": 2017, "filename": "Polygon_2017",
        #                  "graph_title_font_size": "26", "graph_title_font_color": "#000000",
        #                  "graph_subtitle_font_size": "22", "graph_subtitle_font_color": "#808080",
        #                  "xaxe_font_size": "22", "xaxe_font_color": "#000000", "legend_title_font_size": "22",
        #                  "legend_title_font_color": "#000000", "width": "1100", "height": "800"}

        # selectedTimeseries:[{"productcode": "vgt-ndvi", "version": "sv2-pv2.1", "subproductcode": "ndvi-linearx2",
        #                      "mapsetcode": "SPOTV-Africa-1km", "date_format": "YYYYMMDD", "frequency_id": "e1dekad",
        #                      "cumulative": false, "difference": false, "reference": false, "colorramp": false,
        #                      "legend_id": null, "zscore": false}]

        graphTemplate = {
            'userid': params['userid'],
            'graph_tpl_name': params['graph_tpl_name'],
            'graphviewposition': params['graphviewposition'],
            'graphviewsize': params['graphviewsize'],
            'graph_type': params['graph_type'],
            'selectedtimeseries': params['selectedtimeseries'],
            'yearts': params['yearts'],
            'tsfromperiod': params['tsfromperiod'],
            'tstoperiod': params['tstoperiod'],
            'yearstocompare': params['yearstocompare'],
            'tsfromseason': params['tsfromseason'],
            'tstoseason': params['tstoseason'],
            'wkt_geom': params['wkt_geom'],
            'selectedregionname': params['selectedregionname'],

            'disclaimerobjposition': params['disclaimerObjPosition'],
            'disclaimerobjcontent': params['disclaimerObjContent'],
            'logosobjposition': params['logosObjPosition'],
            'logosobjcontent': params['logosObjContent'],
            'showobjects': params['showObjects']
        }

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_graph_templates', graphTemplate):
                createstatus = '{"success":true, "message":"Graph Template created!"}'
            else:
                createstatus = '{"success":false, "message":"Error saving the Graph Template! Name already exists!"}'
        else:
            if crud_db.update('user_graph_templates', graphTemplate):
                createstatus = '{"success":true, "message":"Graph Template updated!"}'
    else:
        createstatus = '{"success":false, "message":"No Graph Template data given!"}'

    return createstatus


def getGraphTimeseries(params):
    if params['graphtype'] == 'ranking':
        return rankTimeseries(params)
    if params['graphtype'] == 'matrix':
        return matrixTimeseries(params)
    # if params['graphtype'] == 'scatter':
    #     return scatterTimeseries(params)
    else:
        return classicTimeseries(params)


# def plot_1o1(data_1, data_2, x_label=None, y_label=None, figure_title=None):
#     from scipy import stats  # , interpolate
#
#     """
#     :param data_1:              -> np.array dataset 1
#     :param data_2:              -> np.array dataset 2
#     :param x_label:             -> STRING; label for x-axis (typically: Name of dataset-1)
#     :param y_label:             -> STRING; label for y-axis (typically: Name of dataset-2)
#     :param figure_title:        -> STRING; title to be printed on the canvas
#     """
#     '''
#     ************************************************************
#     # Replace no data to nan
#     ************************************************************
#     '''
#
#     if NP.shape(data_1) != NP.shape(data_2):
#         raise Exception('Dataset must have te same dimensions')
#
#     '''
#     ************************************************************
#     # Check the labels (if assigned)
#     ************************************************************
#     '''
#     if x_label is None:
#         x_label = 'dataset(1)'
#
#     if y_label is None:
#         y_label = 'dataset(2)'
#
#     if figure_title is None:
#         figure_title = 'Density Scatter Plot'
#
#     '''
#     ***************  SPATIAL CONSISTENCY! **********************
#     '''
#     sz = data_1.shape
#     if len(sz) == 2:
#         n_plots = 1
#         data_1 = [data_1]
#         data_2 = [data_2]
#         figure_title = [figure_title]
#     else:
#         n_plots = sz[0]
#
#     for sp in range(n_plots):
#         d1 = data_1[sp]
#         d2 = data_2[sp]
#         # max_v = 900
#         max_v = NP.ceil(min(NP.nanmax(d1), NP.nanmax(d2)))
#         min_v = NP.round(min(NP.nanmin(d1), NP.nanmin(d2)))
#         # min_v = -100
#
#         mask = d1 + d2
#         x_line = d1[~NP.isnan(mask)]
#         y_line = d2[~NP.isnan(mask)]
#         xx = NP.linspace(min_v, max_v, 10)
#         slope, intercept, r_value, p_value, std_err = stats.linregress(x_line, y_line)
#
#         slp = NP.full_like(xx, fill_value=slope)
#         itc = NP.full_like(xx, fill_value=intercept)
#
#         line = slp * xx + itc
#
#         rmsd = NP.sqrt(NP.nansum(NP.square(NP.array(data_1).flatten() - NP.array(data_2).flatten())) /
#                        NP.count_nonzero(~NP.isnan((NP.array(data_1) - NP.array(data_2)))))
#
#         h, x_edges, y_edges = NP.histogram2d(x_line, y_line, bins=150)
#         h = NP.rot90(h)
#         h = NP.flipud(h)
#
#         h_mask = NP.ma.masked_where(h < 1, h)  # Mask pixels with a value of zero
#         # Log
#         h_mask = NP.log10(h_mask)
#
#         txt_1 = 'Slope=' + str("{:.3f}".format(slope)) + '\n'
#         txt_2 = 'Intercept=' + str("{:.3f}".format(intercept)) + '\n'
#         txt_3 = 'R$^{2 }$=' + str("{:.3f}".format(r_value ** 2)) + '\n'
#         txt_4 = 'RMSD=' + str("{:.3f}".format(rmsd))
#         lbl = txt_1 + txt_2 + txt_3 + txt_4
#
#         # color_map = cm.get_cmap('jet')
#         plt.figure(figsize=(7, 6), facecolor='w', edgecolor='k')
#         plt.grid()
#
#         color_map = plt.cm.get_cmap('jet')
#
#         plt.pcolormesh(x_edges, y_edges, h_mask, cmap=color_map)
#
#         cb = plt.colorbar(aspect=30)  # , ticks=cb_ticks)
#         cb.ax.set_ylabel('log$_{10}$(N)', fontsize=12)
#         plt.plot(xx, xx, color=[0, 0, 0], ls='-', lw=2, label=None)
#         plt.plot(xx, line, color=[1, 0, 1], ls='-', lw=3, label=lbl)
#         plt.xlim([min_v, max_v])
#         plt.ylim([min_v, max_v])
#         cb.ax.tick_params(labelsize=12)
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.minorticks_on()
#         plt.xlabel(x_label, fontsize=12)
#         plt.ylabel(y_label, fontsize=12)
#         plt.title(figure_title[sp] + '\n', fontsize=14, fontweight='bold')
#         plt.legend(loc=2, fontsize=10, numpoints=1, shadow=True)
#         plt.grid()
#         plt.tight_layout()
#
#         plt.savefig("/data/processing/scatter_test/test.png")
#
#         plt.show()
#
#
# def clipOverWKT(productcode, subproductcode, version, mapsetcode, wkt, file):
#     from greenwich import Raster, Geometry
#     try:
#         from osgeo import gdal
#         from osgeo import gdal_array
#         from osgeo import ogr, osr
#         from osgeo import gdalconst
#     except ImportError:
#         import gdal
#         import gdal_array
#         import ogr
#         import osr
#         import gdalconst
#
#     #    Extract timeseries from a list of files and return as JSON object
#     #    It applies to a single dataset (prod/sprod/version/mapset) and between 2 dates
#     #    Several types of aggregation foreseen:
#     #
#     #       mean :      Sum(Xi)/N(Xi)        -> min/max not considered          e.g. Rain
#     #       cumulate:   Sum(Xi)              -> min/max not considered          e.g. Fire
#     #
#     #       count:      N(Xi where min < Xi < max)                              e.g. Vegetation anomalies
#     #       surface:    count * PixelArea                                       e.g. Water Bodies
#     #       percent:    count/Ntot                                              e.g. Vegetation anomalies
#     #
#     #   History: 1.0 :  Initial release - since 2.0.1 -> now renamed '_green' from greenwich package
#     #            1.1 :  Since Feb. 2017, it is based on a different approach (gdal.RasterizeLayer instead of greenwich)
#     #                   in order to solve the issue with MULTIPOLYGON
#     #
#
#     # Convert the wkt into a geometry
#     ogr.UseExceptions()
#     theGeomWkt = ' '.join(wkt.strip().split())
#     geom = Geometry(wkt=str(theGeomWkt), srs=4326)
#
#     # Get Mapset Info
#     mapset_info = querydb.get_mapset(mapsetcode=mapsetcode)
#
#     # Prepare for computing conversion to area: the pixel size at Lat=0 is computed
#     # The correction to the actual latitude (on AVERAGE value - will be computed below)
#     const_d2km = 12364.35
#     area_km_equator =  abs(mapset_info.pixel_shift_lat) * abs(mapset_info.pixel_shift_long) *const_d2km
#
#     # Get Product Info
#     product_info = querydb.get_product_out_info(productcode=productcode,
#                                                 subproductcode=subproductcode,
#                                                 version=version)
#     if product_info.__len__() > 0:
#         # Get info from product_info
#         scale_factor = 0
#         scale_offset = 0
#         nodata = 0
#         date_format = ''
#         for row in product_info:
#             scale_factor = row.scale_factor
#             scale_offset = row.scale_offset
#             nodata = row.nodata
#             date_format = row.date_format
#             date_type = row.data_type_id
#
#         # Create an output/temp shapefile, for managing the output layer (really mandatory ?? Can be simplified ???)
#         try:
#             tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_getTimeseries',
#                                       dir=es_constants.base_tmp_dir)
#         except:
#             logger.error('Cannot create temporary dir ' + es_constants.base_tmp_dir + '. Exit')
#             raise NameError('Error in creating tmpdir')
#
#         out_shape = tmpdir+os.path.sep+"output_shape.shp"
#         outDriver = ogr.GetDriverByName('ESRI Shapefile')
#
#         # Create the output shapefile
#         outDataSource = outDriver.CreateDataSource(out_shape)
#         dest_srs = ogr.osr.SpatialReference()
#         dest_srs.ImportFromEPSG(4326)
#
#         outLayer = outDataSource.CreateLayer("Layer", dest_srs)
#         # outLayer = outDataSource.CreateLayer("Layer")
#         idField = ogr.FieldDefn("id", ogr.OFTInteger)
#         outLayer.CreateField(idField)
#
#         featureDefn = outLayer.GetLayerDefn()
#         feature = ogr.Feature(featureDefn)
#         feature.SetGeometry(geom)
#         feature.SetField("id", 1)
#         outLayer.CreateFeature(feature)
#         feature = None
#
#         [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, start_date, end_date)
#
#         # Built a dictionary with filenames/dates
#         dates_to_files_dict = dict(zip(dates_list, list_files))
#
#         # Generate unique list of files
#         unique_list = set(list_files)
#         uniqueFilesValues = []
#
#         geo_mask_created = False
#         for infile in unique_list:
#             single_result = {'filename': '', 'meanvalue_noscaling': nodata, 'meanvalue': None}
#
#             if infile.strip() != '' and os.path.isfile(infile):
#                 # try:
#
#                     # Open input file
#                     orig_ds = gdal.Open(infile, gdal.GA_ReadOnly)
#                     orig_cs = osr.SpatialReference()
#                     orig_cs.ImportFromWkt(orig_ds.GetProjectionRef())
#                     orig_geoT = orig_ds.GetGeoTransform()
#                     x_origin = orig_geoT[0]
#                     y_origin = orig_geoT[3]
#                     pixel_size_x = orig_geoT[1]
#                     pixel_size_y = -orig_geoT[5]
#
#                     in_data_type_gdal = conv_data_type_to_gdal(date_type)
#
#                     # Create a mask from the geometry, with the same georef as the input file[s]
#                     if not geo_mask_created:
#
#                         # Read polygon extent and round to raster resolution
#                         x_min, x_max, y_min, y_max = outLayer.GetExtent()
#                         x_min_round = int((x_min-x_origin)/pixel_size_x)*pixel_size_x+x_origin
#                         x_max_round = (int((x_max-x_origin)/(pixel_size_x))+1)*pixel_size_x+x_origin
#                         y_min_round = (int((y_min-y_origin)/(pixel_size_y))-1)*pixel_size_y+y_origin
#                         y_max_round = int((y_max-y_origin)/(pixel_size_y))*pixel_size_y+y_origin
#                     #
#                     #     # Create the destination data source
#                         x_res = int(round((x_max_round - x_min_round) / pixel_size_x))
#                         y_res = int(round((y_max_round - y_min_round) / pixel_size_y))
#                     #
#                     #     # Create mask in memory
#                         mem_driver = gdal.GetDriverByName('MEM')
#                         mem_ds = mem_driver.Create('', x_res, y_res, 1, in_data_type_gdal)
#                         mask_geoT = [x_min_round, pixel_size_x, 0, y_max_round, 0, -pixel_size_y]
#                         mem_ds.SetGeoTransform(mask_geoT)
#                         mem_ds.SetProjection(orig_cs.ExportToWkt())
#                     #
#                     #     # Create a Layer with '1' for the pixels to be selected
#                         gdal.RasterizeLayer(mem_ds, [1], outLayer, burn_values=[1])
#                         # gdal.RasterizeLayer(mem_ds, [1], outLayer, None, None, [1])
#
#                         # Read the polygon-mask
#                         band = mem_ds.GetRasterBand(1)
#                         geo_values = mem_ds.ReadAsArray()
#
#                         # Create a mask from geo_values (mask-out the '0's)
#                         geo_mask = ma.make_mask(geo_values == 0)
#                         geo_mask_created = True
#                     #
#                     #     # Clean/Close objects
#                         mem_ds = None
#                         mem_driver = None
#                         outDriver = None
#                         outLayer = None
#
#                     # Read data from input file
#                     x_offset = int((x_min-x_origin)/pixel_size_x)
#                     y_offset = int((y_origin-y_max)/pixel_size_y)
#
#                     band_in = orig_ds.GetRasterBand(1)
#                     data = band_in.ReadAsArray(x_offset, y_offset, x_res, y_res)
#                     #   Catch the Error ES2-105 (polygon not included in Mapset)
#                     if data is None:
#                         logger.error('ERROR: polygon extends out of file mapset for file: %s' % infile)
#                         return []
#
#                     # Create a masked array from the data (considering Nodata)
#                     masked_data = ma.masked_equal(data, nodata)
#
#                     # Apply on top of it the geo mask
#                     mxnodata = ma.masked_where(geo_mask, masked_data)
#                     # mxnodata = masked_data  # TEMP !!!!
#
#                     # Test ONLY
#                     # write_ds_to_geotiff(mem_ds, '/data/processing/exchange/Tests/mem_ds.tif')
#
#                     if aggregate['aggregation_type'] == 'count' or aggregate['aggregation_type'] == 'percent' or aggregate['aggregation_type'] == 'surface':
#
#                         if mxnodata.count() == 0:
#                             meanResult = None
#                         else:
#                             mxrange = mxnodata
#                             min_val = aggregate['aggregation_min']
#                             max_val = aggregate['aggregation_max']
#
#                             if min_val is not None:
#                                 min_val_scaled = (min_val - scale_offset) / scale_factor
#                                 mxrange = ma.masked_less(mxnodata, min_val_scaled)
#
#                                 # See ES2-271
#                                 if max_val is not None:
#                                     # Scale threshold from physical to digital value
#                                     max_val_scaled = (max_val - scale_offset) / scale_factor
#                                     mxrange = ma.masked_greater(mxrange, max_val_scaled)
#
#                             elif max_val is not None:
#                                 # Scale threshold from physical to digital value
#                                 max_val_scaled = (max_val - scale_offset) / scale_factor
#                                 mxrange = ma.masked_greater(mxnodata, max_val_scaled)
#
#                             if aggregate['aggregation_type'] == 'percent':
#                                 # 'percent'
#                                 meanResult = float(mxrange.count())/float(mxnodata.count()) * 100
#
#                             elif aggregate['aggregation_type'] == 'surface':
#                                 # 'surface'
#                                 # Estimate 'average' Latitude
#                                 y_avg = (y_min + y_max)/2.0
#                                 pixelAvgArea = area_km_equator * math.cos(y_avg / 180 * math.pi)
#                                 meanResult = float(mxrange.count()) * pixelAvgArea
#                             else:
#                                 # 'count'
#                                 meanResult = float(mxrange.count())
#
#                         # Both results are equal
#                         finalvalue = meanResult
#
#                     else:   # if aggregate['type'] == 'mean' or if aggregate['type'] == 'cumulate':
#                         if mxnodata.count() == 0:
#                             finalvalue = None
#                             meanResult = None
#                         else:
#                             if aggregate['aggregation_type'] == 'mean':
#                                 # 'mean'
#                                 meanResult = mxnodata.mean()
#                             else:
#                                 # 'cumulate'
#                                 meanResult = mxnodata.sum()
#
#                             finalvalue = (meanResult*scale_factor+scale_offset)
#
#                     # Assign results
#                     single_result['filename'] = infile
#                     single_result['meanvalue_noscaling'] = meanResult
#                     single_result['meanvalue'] = finalvalue
#
#             else:
#                 logger.debug('ERROR: raster file does not exist - %s' % infile)
#
#             uniqueFilesValues.append(single_result)
#
#         # Define a dictionary to associate filenames/values
#         files_to_values_dict = dict((x['filename'], x['meanvalue']) for x in uniqueFilesValues)
#
#         # Prepare array for result
#         resultDatesValues = []
#
#         # Returns a list of 'filenames', 'dates', 'values'
#         for mydate in dates_list:
#
#             my_result = {'date': datetime.date.today(), 'meanvalue':nodata}
#
#             # Assign the date
#             my_result['date'] = mydate
#             # Assign the filename
#             my_filename = dates_to_files_dict[mydate]
#
#             # Map from array of Values
#             my_result['meanvalue'] = files_to_values_dict[my_filename]
#
#             # Map from array of dates
#             resultDatesValues.append(my_result)
#
#         try:
#             shutil.rmtree(tmpdir)
#         except:
#             logger.debug('ERROR: Error in deleting tmpdir. Exit')
#
#         # Return result
#         return resultDatesValues
#     else:
#         logger.debug('ERROR: product not registered in the products table! - %s %s %s' % (productcode, subproductcode, version))
#         return []
#
#
# def scatterTimeseries(params):
#     from osgeo import gdal
#
#     date1 = params['tsFromPeriod']
#     date2 = params['tsToPeriod']
#
#     wkt = params['WKT']
#     requestedtimeseries = json.loads(params['selectedTimeseries'])
#
#     userid = params['userid']
#     istemplate = params['istemplate']
#     graphtype = params['graphtype']
#     graph_tpl_id = params['graph_tpl_id']
#     graph_tpl_name = params['graph_tpl_name']
#
#     timeseries = []
#     for timeserie in requestedtimeseries:
#         productcode = timeserie['productcode']
#         subproductcode = timeserie['subproductcode']
#         version = timeserie['version']
#         mapsetcode = timeserie['mapsetcode']
#         date_format = timeserie['date_format']
#         frequency_id = timeserie['frequency_id']
#
#         product = {"productcode": productcode,
#                    "subproductcode": subproductcode,
#                    "version": version}
#
#         nodata = None
#         subproductinfo = querydb.get_subproduct(productcode, version, subproductcode)
#         if subproductinfo != []:
#             subproductinfo_rec = functions.row2dict(subproductinfo)
#             nodata = subproductinfo_rec['nodata']
#
#         p = Product(product_code=productcode, version=version)
#         dataset = p.get_dataset(mapset=mapsetcode, sub_product_code=subproductcode)
#         # print dataset.fullpath
#
#         # Check the case of daily product, with time/minutes
#         frequency_id = dataset._db_product.frequency_id
#         date_format = dataset._db_product.date_format
#
#         filedate = date1
#         if dataset.no_year():
#             filedate = dataset.strip_year(filedate)
#
#         if frequency_id == 'e1day' and date_format == 'YYYYMMDD':
#             regex = dataset.fullpath + filedate+'*'+'.tif'
#             filename = glob.glob(regex)
#             productfile_date1 = filename[0]
#         else:
#             filename = functions.set_path_filename(filedate,
#                                                    productcode,
#                                                    subproductcode,
#                                                    mapsetcode,
#                                                    version,
#                                                    '.tif')
#             productfile_date1 = dataset.fullpath + filename
#
#         filedate = date2
#         if dataset.no_year():
#             filedate = dataset.strip_year(filedate)
#
#         if frequency_id == 'e1day' and date_format == 'YYYYMMDD':
#             regex = dataset.fullpath + filedate+'*'+'.tif'
#             filename = glob.glob(regex)
#             productfile_date2 = filename[0]
#         else:
#             filename = functions.set_path_filename(filedate,
#                                                    productcode,
#                                                    subproductcode,
#                                                    mapsetcode,
#                                                    version,
#                                                    '.tif')
#             productfile_date2 = dataset.fullpath + filename
#
#
#         ds_1 = gdal.Open(productfile_date1)
#         data_1 = NP.array(ds_1.GetRasterBand(1).ReadAsArray())
#
#         ds_2 = gdal.Open(productfile_date2)
#         data_2 = NP.array(ds_2.GetRasterBand(1).ReadAsArray())
#
#         data_1 = data_1.astype('float')
#         data_2 = data_2.astype('float')
#         #
#         data_1[data_1 == nodata] = NP.nan
#         data_2[data_2 == nodata] = NP.nan
#
#         plot_1o1(data_1, data_2, date1, date2, filename)
#
#     return timeseries


def matrixTimeseries(params):
    # params = web.input()
    # yearts = params.yearTS
    # tsFromPeriod = params.tsFromPeriod
    # tsToPeriod = params.tsToPeriod
    # showYearInTicks = True

    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    yearsToCompare = sorted(json.loads(params.yearsToCompare))
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    data_available = False
    colorramp = False
    legend_id = None
    overTwoYears = False

    userid = params.userid
    istemplate = params.istemplate
    graphtype = params.graphtype
    graph_tpl_id = params.graph_tpl_id
    graph_tpl_name = params.graph_tpl_name

    # if hasattr(params, "userid") and params.userid != '':
    #     user = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        date_format = timeserie['date_format']
        frequency_id = timeserie['frequency_id']
        colorramp = timeserie['colorramp']
        legend_id = timeserie['legend_id']

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                        passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                        passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate,
                                                                                      graphtype, graph_tpl_id,
                                                                                      graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop

        nodata = None
        subproductinfo = querydb.get_subproduct(productcode, version, subproductcode)
        if subproductinfo != []:
            subproductinfo_rec = functions.row2dict(subproductinfo)
            nodata = subproductinfo_rec['nodata']

        if len(yearsToCompare) > 0:
            data = []
            y = 0

            xAxesYear = yearsToCompare[-1]
            for year in yearsToCompare:  # Handle Leap year date 29 February. If exists in data then change the year of all data to the leap year.
                if calendar.isleap(year):
                    xAxesYear = year

            for year in yearsToCompare:
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))
                        overTwoYears = True

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                            aggregate)

                if len(list_values) > 0 and not data_available:
                    data_available = True

                x = 0
                for val in list_values:
                    value = []
                    # # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    # valdate = functions.unix_time_millis(val['date'])
                    # # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    # date = str(yearsToCompare[-1]) + '-' + str(val['date'].strftime('%m')) + '-' + str(val['date'].strftime('%d'))
                    # print val['date']

                    # if overTwoYears:
                    #     date = datetime.date(val['date'].year, val['date'].month, val['date'].day)
                    # else:
                    #     date = datetime.date(yearsToCompare[-1], val['date'].month, val['date'].day)
                    date = datetime.date(xAxesYear, val['date'].month, val['date'].day)

                    valdate = functions.unix_time_millis(date)
                    value.append(valdate)  # Date for xAxe
                    # if overTwoYears:
                    #     value.append(str(year) + '-' + str(year+1))  # Year for yAxe
                    # else:
                    value.append(val['date'].year)  # Year for yAxe

                    if val['meanvalue'] == float(nodata):
                        value.append(None)
                    else:
                        value.append(val['meanvalue'])
                    data.append(value)
                    x += 1
                y += 1

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {
                    'name': productcode + '-' + version + '-' + subproductcode,
                    'frequency_id': frequency_id,
                    # 'type': 'heatmap',
                    'yAxis': productcode + ' - ' + version,
                    'data': data
                    # 'visible': True,
                    # 'borderWidth': 1,
                    # 'dataLabels': {
                    #     'enabled': True,
                    #     'color': '#000000'
                    # }
                }
            else:
                # for ts_drawprops in product_ts_drawproperties:
                # print ts_drawprops
                ts = {
                    'name': ts_drawprops['tsname_in_legend'],
                    'frequency_id': frequency_id,
                    # 'type': 'heatmap',
                    'yAxis': ts_drawprops['yaxe_id'],
                    'data': data
                }
            timeseries.append(ts)

    legend_info = querydb.get_legend_info(legendid=legend_id)
    step_type = 'linear'
    if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
        for row in legend_info:
            step_type = row.step_type

        if step_type != 'logarithmic':
            step_type = 'linear'

    legend_steps = querydb.get_legend_steps(legendid=legend_id)
    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        minimizeSteps = False
        if legend_steps.__len__() > 35:
            colorramp = True
            minimizeSteps = True

        firstStep = 0.01
        roundTo = 2
        if legend_steps.__len__() >= 100:
            firstStep = 0.001
            roundTo = 3

        # min = float((legend_steps[0].from_step - legend_steps[0].scale_offset)/legend_steps[0].scale_factor)
        # max = float((legend_steps[legend_steps.__len__()-1].to_step - legend_steps[legend_steps.__len__()-1].scale_offset)/legend_steps[legend_steps.__len__()-1].scale_factor)

        if step_type == 'logarithmic':
            if legend_steps[0].from_step <= 0:
                min = legend_steps[0].to_step
                minColorSecondRow = True
            else:
                min = legend_steps[0].from_step
                minColorSecondRow = False
        else:
            min = legend_steps[0].from_step

        max = legend_steps[legend_steps.__len__() - 1].to_step

        stops = []
        colors = []
        dataClasses = []
        rownr = 0
        for step in legend_steps:
            stop = []
            rownr += 1
            # from_step = float((step.from_step - step.scale_offset)/step.scale_factor)
            # to_step = float((step.to_step - step.scale_offset)/step.scale_factor)
            from_step = step.from_step
            to_step = step.to_step

            colorRGB = list(map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip())))
            colorHex = functions.rgb2html(colorRGB)

            if step_type == 'logarithmic':
                if rownr == 1 and not minColorSecondRow:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)

                if rownr == 2 and minColorSecondRow:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)
            else:
                if rownr == 1:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)

            if rownr == legend_steps.__len__():
                maxcolor = colorHex

            if minimizeSteps:
                if step.color_label is not None and step.color_label.strip() != '':
                    # stop.append(round(to_step / max, roundTo))
                    # stop.append(round((from_step-min)/(max-min), roundTo))
                    stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                    # stop.append(round(rownr * firstStep, 3))
                    # stop.append(round(rownr/max, 2))
                    stop.append(colorHex)
                    stops.append(stop)
            else:
                colors.append(colorHex)
                # stop.append((from_step-min)/(max-min))
                stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                # stop.append(round(rownr * firstStep, 3))
                stop.append(colorHex)
                stops.append(stop)

            dataClass = {
                'from': from_step,
                'to': to_step,
                'color': colorHex,
                'name': step.color_label
            }
            dataClasses.append(dataClass)

    if colorramp:
        if minimizeSteps:
            tickPixelInterval = int(old_div(legend_steps.__len__(), len(stops)))
            # tickInterval = legend_steps.__len__()
        else:
            tickPixelInterval = 72
            # tickPixelInterval = int(legend_steps.__len__()/len(stops))
            # tickPixelInterval = legend_steps.__len__()
            # tickInterval = tickPixelInterval

        colorAxis = {
            'min': min,
            'max': max,
            # 'floor': min,
            'ceiling': max,
            'stops': stops,
            # 'colors': colors,
            'maxColor': maxcolor,
            'minColor': mincolor,
            # 'minPadding': 0.05,
            # 'maxPadding': 0.5,
            'startOnTick': True,
            'endOnTick': True,
            'tickWidth': 2,
            'tickmarkPlacement': 'on',
            # 'tickInterval': None,
            # 'tickPixelInterval': tickPixelInterval,
            # 'tickLength': tickInterval,
            'gridLineWidth': 0,
            # 'gridLineColor': 'white',
            # 'minorTickInterval': 0.1,
            # 'minorGridLineColor': 'white',
            'type': step_type  # 'logarithmic'  'linear'  #
        }
    else:
        colorAxis = {
            'dataClasses': dataClasses,
            # 'dataClassColor': 'category',
            'startOnTick': False,
            'endOnTick': False
        }

    if overTwoYears:
        yearsToCompare.append(yearsToCompare[-1] + 1)  # Add extra year
        # for year in yearsToCompare:
        #     categories.append(str(year) + '-' + str(year+1))
    categories = yearsToCompare
    min = yearsToCompare[0]  # yaxe.min
    max = yearsToCompare[-1]  # yaxe.max

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            yaxe = {'id': passedyaxe['id'],
                    'categories': categories,
                    'title': passedyaxe['title'],
                    'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'],
                    'unit': passedyaxe['unit'], 'unit_orig': passedyaxe['unit_orig'],
                    'opposite': passedyaxe['opposite'],
                    'min': min,
                    'max': max,
                    # 'productcategory': passedyaxe['productcategory'],
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype,
                                                        graph_tpl_id, graph_tpl_name)
        for yaxe in timeseries_yaxes:
            # min = yearsToCompare[0]    # yaxe.min
            # max = yearsToCompare[-1]    # yaxe.max

            yaxe = {'id': yaxe.yaxe_id,
                    'categories': categories,
                    'title': yaxe.title,
                    'title_color': yaxe.title_color.replace("  ", " "),
                    'title_font_size': yaxe.title_font_size,
                    'unit': yaxe.unit, 'unit_orig': yaxe.unit,
                    'opposite': yaxe.opposite,
                    'min': min,
                    'max': max,
                    # 'productcategory': yaxe.productcategory,
                    'aggregation_type': yaxe.aggregation_type,
                    'aggregation_min': yaxe.aggregation_min,
                    'aggregation_max': yaxe.aggregation_max
                    }
            yaxes.append(yaxe)

    ts_json = {"data_available": data_available,
               "showYearInTicks": False,
               "showYearInToolTip": "true",
               "colorAxis": colorAxis,
               'colors': colors,
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json,
                         ensure_ascii=False,
                         sort_keys=True,
                         separators=(', ', ': '))
    return ts_json


def rankTimeseries(params):
    # params = web.input()
    # yearts = params.yearTS
    # tsFromPeriod = params.tsFromPeriod
    # tsToPeriod = params.tsToPeriod
    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    yearsToCompare = sorted(json.loads(params.yearsToCompare))
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    showYearInTicks = True
    data_available = False

    userid = params.userid
    istemplate = params.istemplate
    graphtype = params.graphtype
    graph_tpl_id = params.graph_tpl_id
    graph_tpl_name = params.graph_tpl_name

    # if hasattr(params, "userid") and params.userid != '':
    #     user = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        # date_format = timeserie['date_format']
        zscore = timeserie['zscore']
        tscolor = "#000000"

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                        passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                        passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate,
                                                                                      graphtype, graph_tpl_id,
                                                                                      graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop

        tscolor = ts_drawprops['color'].replace("  ", " ")

        if len(yearsToCompare) > 1:
            dataRanking = []
            dataZScore = []
            yearDataZScoreForAVGSTD = []

            for year in yearsToCompare:
                showYearInTicks = False

                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                            aggregate)

                if len(list_values) > 0:
                    data_available = True

                cumulatedValue = 0
                for val in list_values:
                    if val['meanvalue'] != None:
                        cumulatedValue += val['meanvalue']

                yearDataRanking = {
                    'name': str(year),
                    'color': tscolor,  # '#0065a2',
                    'y': cumulatedValue
                }
                dataRanking.append(yearDataRanking)

                yearDataZScore = {
                    'name': str(year),
                    'color': tscolor,  # '#0065a2',
                    'y': cumulatedValue
                }
                dataZScore.append(yearDataZScore)
                yearDataZScoreForAVGSTD.append(cumulatedValue)

            dataRanking = sorted(dataRanking, key=lambda k: k['name'], reverse=True)
            dataRanking[0]['color'] = '#ff0000'
            dataRanking = sorted(dataRanking, key=lambda k: k['y'], reverse=False)

            emptyDataRanking = {
                'name': '',
                'color': '',
                'y': ''
            }
            dataRanking.append(emptyDataRanking)

            # from operator import itemgetter, attrgetter
            # data = sorted(data, key=attrgetter('y'), reverse=False)
            # data = sorted(data, key=itemgetter(2), reverse=False)

            zScoreAVG = NP.mean(yearDataZScoreForAVGSTD)
            zScoreSTD = NP.std(yearDataZScoreForAVGSTD)
            for yearData in dataZScore:
                zScoreValue = old_div((yearData['y'] - zScoreAVG), zScoreSTD)
                yearData['y'] = zScoreValue
                if zScoreValue < 0:
                    yearData['color'] = '#ff0000'

            emptyDataZScore = {
                'name': '',
                'color': '',
                'y': ''
            }
            dataZScore.append(emptyDataZScore)

            if zscore:
                data = dataZScore
            else:
                data = dataRanking

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'column',
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True
                      }
            else:
                # for ts_drawprops in product_ts_drawproperties:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': 'column',  # ts_drawprops.graphtype,
                      'color': ts_drawprops['color'].replace("  ", " "),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'visible': True
                      }
            timeseries.append(ts)

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            min = None
            max = None
            yaxe = {'id': passedyaxe['id'], 'title': passedyaxe['title'],
                    'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'],
                    'unit': passedyaxe['unit'], 'unit_orig': passedyaxe['unit_orig'],
                    'opposite': passedyaxe['opposite'],
                    'min': min, 'max': max,
                    # 'productcategory': passedyaxe['productcategory'],
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype,
                                                        graph_tpl_id, graph_tpl_name)
        for yaxe in timeseries_yaxes:
            min = None  # yaxe.min
            max = None  # yaxe.max

            yaxe = {'id': yaxe.yaxe_id,
                    'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "),
                    'title_font_size': yaxe.title_font_size,
                    'unit': yaxe.unit, 'unit_orig': yaxe.unit,
                    'opposite': yaxe.opposite,
                    'min': min, 'max': max,
                    # 'productcategory': yaxe.productcategory,
                    'aggregation_type': yaxe.aggregation_type,
                    'aggregation_min': yaxe.aggregation_min,
                    'aggregation_max': yaxe.aggregation_max}
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


def classicTimeseries(params):
    yearts = params['yearTS']
    wkt = params['WKT']
    requestedtimeseries = json.loads(params['selectedTimeseries'])
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    tsFromPeriod = params['tsFromPeriod']
    tsToPeriod = params['tsToPeriod']
    yearsToCompare = params['yearsToCompare']
    tsFromSeason = params['tsFromSeason']
    tsToSeason = params['tsToSeason']
    showYearInTicks = True
    moreThenTwoYears = False
    data_available = False
    cumulative = False
    if params['graphtype'] == 'cumulative':
        cumulative = True
    userid = params['userid']
    istemplate = params['istemplate']
    graphtype = params['graphtype']
    graph_tpl_id = params['graph_tpl_id']
    graph_tpl_name = params['graph_tpl_name']

    # if hasattr(params, "userid") and params.userid != '':
    #     userid = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    if tsFromSeason != '' and tsToSeason != '' and yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) >= 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

    elif yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) >= 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

    elif params['yearTS'] != '':
        if tsFromSeason != '' and tsToSeason != '':
            if tsToSeason != '':
                from_date = datetime.date(int(params['yearTS']), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params['yearTS']), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(params['yearTS']) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))
            else:
                from_date = datetime.date(int(params['yearTS']), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params['yearTS']), 12, 31)
        else:
            from_date = datetime.date(int(params['yearTS']), 1, 1)
            to_date = datetime.date(int(params['yearTS']), 12, 31)
        showYearInTicks = False

    elif tsFromPeriod != '' and tsToPeriod != '':
        from_date = datetime.datetime.strptime(tsFromPeriod, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(tsToPeriod, '%Y-%m-%d').date()
        tsFromYear = tsFromPeriod[:4]
        tsToYear = tsToPeriod[:4]
        if (int(tsToYear) - int(tsFromYear)) > 2:
            moreThenTwoYears = True
            showYearInTicks = False

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
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        # product_native = querydb.get_product_native(productcode, version)
        # productcategory = product_native[0]['category_id']

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}
            if cumulative:
                cum_yaxe.append(yaxe_info.yaxe_id)

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                        passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                        passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate,
                                                                                      graphtype, graph_tpl_id,
                                                                                      graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop

        if date_format == 'MMDD' and len(yearsToCompare) > 1:
            year = yearsToCompare[0]
            showYearInTicks = False
            from_date = datetime.date(year, 1, 1)
            to_date = datetime.date(year, 12, 31)

            if tsFromSeason != '' and tsToSeason != '':
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                        aggregate)
            # print list_values
            # list_values = sorted(list_values, key=lambda k:k['date'], reverse=True)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)
            if len(data) > 0:
                data_available = True

            if ts_drawprops is None:
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
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            else:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': ts_drawprops['charttype'],
                      'dashStyle': ts_drawprops['linestyle'],
                      'lineWidth': ts_drawprops['linewidth'],
                      'color': ts_drawprops['color'].replace("  ", " "),
                      # 'xAxis': str(year),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

        elif len(yearsToCompare) > 1:  # yearsToCompare != '' or
            # yearsToCompare = json.loads(yearsToCompare)
            colorAdd = 0
            colorSubstract = 0
            for year in yearsToCompare:
                showYearInTicks = False
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                if ts_drawprops['color'][0] == '#':  # Transform HTML HEX color code to RGB
                    h = ts_drawprops['color'].lstrip('#')
                    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
                    rgb = list(rgb)
                else:
                    if functions.isValidRGB(ts_drawprops['color'].replace("  ", " ")):
                        rgb = ts_drawprops['color'].replace("  ", " ").split(' ')
                    else:
                        # RGB value stored in the database is not correct so define as default value BLACK.
                        rgb = "0 0 0".split(' ')

                rgb = list(map(int, rgb))
                rgb[-1] = rgb[-1] + colorAdd
                rgb[-2] = rgb[-2] + colorAdd
                rgb[-3] = rgb[-3] - colorSubstract
                tsColor = ' '.join([str(i) for i in rgb])
                colorAdd += 65
                colorSubstract += 50

                # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
                # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
                # p = Process(target=getTimeseries, args=args)
                # p.start()
                # p.join()
                # list_values = self.out_queue.get()
                # self.out_queue.empty()
                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                            aggregate)

                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(data) > 0:
                    data_available = True

                if ts_drawprops is None:
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
                          'cumulative': cumulative,  # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                else:
                    ts = {'name': str(year) + ' ' + ts_drawprops['tsname_in_legend'],
                          'type': ts_drawprops['charttype'],
                          'dashStyle': ts_drawprops['linestyle'],
                          'lineWidth': ts_drawprops['linewidth'],
                          'color': tsColor,
                          'xAxis': str(year),
                          'yAxis': ts_drawprops['yaxe_id'],
                          'data': data,
                          'visible': True,
                          'cumulative': cumulative,  # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)

        else:
            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()

            if cumulative:
                if to_date > datetime.date.today():
                    to_date = datetime.date.today()

            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                        aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)

            if len(data) > 0:
                data_available = True

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            else:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': ts_drawprops['charttype'],
                      'dashStyle': ts_drawprops['linestyle'],
                      'lineWidth': ts_drawprops['linewidth'],
                      'color': ts_drawprops['color'].replace("  ", " "),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            if passedyaxe['id'] in cum_yaxe:
                min = None
                max = None
            else:
                min = passedyaxe['min']
                max = passedyaxe['max']
            yaxe = {'id': passedyaxe['id'], 'title': passedyaxe['title'],
                    'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'],
                    'unit': passedyaxe['unit'], 'unit_orig': passedyaxe['unit_orig'],
                    'opposite': passedyaxe['opposite'],
                    'min': min, 'max': max,
                    # 'productcategory': passedyaxe['productcategory'],
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype,
                                                        graph_tpl_id, graph_tpl_name)
        # axes = len(timeseries_yaxes)
        # count = 0
        for yaxe in timeseries_yaxes:
            # count += 1
            # opposite = "false"
            # # if axes >= 2 and count % 2 == 0:   # and yaxe.opposite == "f"
            # #     opposite = "false"
            # # if axes >= 2 and count % 2 != 0:   # and yaxe.opposite == "t"
            # #     opposite = "true"
            # if axes >= 2:
            #     if yaxe.opposite:
            #         opposite = "true"
            # if axes == 1:
            #     opposite = "false"

            if yaxe.yaxe_id in cum_yaxe:
                min = None
                max = None
            else:
                min = yaxe.min
                max = yaxe.max
            yaxe = {'id': yaxe.yaxe_id, 'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "),
                    'title_font_size': yaxe.title_font_size, 'unit': yaxe.unit, 'unit_orig': yaxe.unit,
                    'opposite': yaxe.opposite,
                    'min': min, 'max': max,
                    # 'productcategory': yaxe.productcategory,
                    'aggregation_type': yaxe.aggregation_type,
                    'aggregation_min': yaxe.aggregation_min,
                    'aggregation_max': yaxe.aggregation_max}
            yaxes.append(yaxe)

    ts_json = {"data_available": data_available,
               "showYearInTicks": showYearInTicks,
               "moreThenTwoYears": moreThenTwoYears,
               "showYearInToolTip": True,
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json, ensure_ascii=False, sort_keys=True, separators=(', ', ': '))

    return ts_json


def __classicTimeseries(params):
    # params = web.input()
    yearts = params.yearTS
    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    tsFromPeriod = params.tsFromPeriod
    tsToPeriod = params.tsToPeriod
    yearsToCompare = params.yearsToCompare
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    showYearInTicks = True
    data_available = False
    cumulative = False
    if params.graphtype == 'cumulative':
        cumulative = True

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
                    to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

    elif yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) == 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

    elif params.yearTS != '':
        if tsFromSeason != '' and tsToSeason != '':
            if tsToSeason != '':
                from_date = datetime.date(int(params.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params.yearTS), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(params.yearTS) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))
            else:
                from_date = datetime.date(int(params.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params.yearTS), 12, 31)
        else:
            from_date = datetime.date(int(params.yearTS), 1, 1)
            to_date = datetime.date(int(params.yearTS), 12, 31)
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
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}
        timeseries_drawproperties = querydb.get_product_timeseries_drawproperties(product)
        for ts_drawprops in timeseries_drawproperties:
            aggregate = {'aggregation_type': ts_drawprops.aggregation_type,
                         'aggregation_min': ts_drawprops.aggregation_min,
                         'aggregation_max': ts_drawprops.aggregation_max}

            # if timeserie['cumulative']:
            if cumulative:
                cum_yaxe.append(ts_drawprops.yaxes_id)

        mapset_info = querydb.get_mapset(mapsetcode=mapsetcode)
        product_info = querydb.get_product_out_info(productcode=productcode,
                                                    subproductcode=subproductcode,
                                                    version=version)

        if date_format == 'MMDD' and len(yearsToCompare) > 1:
            year = yearsToCompare[0]
            showYearInTicks = False
            from_date = datetime.date(year, 1, 1)
            to_date = datetime.date(year, 12, 31)

            if tsFromSeason != '' and tsToSeason != '':
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                        aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)
            if len(data) > 0:
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
                  'cumulative': cumulative,  # timeserie['cumulative'],
                  'difference': timeserie['difference'],
                  'reference': timeserie['reference']
                  }
            for ts_drawprops in timeseries_drawproperties:
                # print ts_drawprops.color
                ts = {'name': ts_drawprops.tsname_in_legend,
                      'type': ts_drawprops.charttype,
                      'dashStyle': ts_drawprops.linestyle,
                      'lineWidth': ts_drawprops.linewidth,
                      'color': ts_drawprops.color.replace("  ", " "),
                      # 'xAxis': str(year),
                      'yAxis': ts_drawprops.yaxes_id,
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

        elif len(yearsToCompare) > 1:  # yearsToCompare != '' or
            # yearsToCompare = json.loads(yearsToCompare)
            colorAdd = 0
            colorSubstract = 0
            for year in yearsToCompare:
                showYearInTicks = False
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year) + 1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                if ts_drawprops.color[0] == '#':  # Transform HTML HEX color code to RGB
                    h = ts_drawprops.color.lstrip('#')
                    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
                    rgb = list(rgb)
                else:
                    # print ts_drawprops.color
                    # rgb = ts_drawprops.color.replace("  ", " ").split(' ')
                    if (functions.isValidRGB(ts_drawprops.color.replace("  ", " "))):
                        rgb = ts_drawprops.color.replace("  ", " ").split(' ')
                    else:
                        # RGB value stored in the database is not correct so define as default value BLACK.
                        rgb = "0 0 0".split(' ')
                # print rgb
                rgb = list(map(int, rgb))
                rgb[-1] = rgb[-1] + colorAdd
                rgb[-2] = rgb[-2] + colorAdd
                rgb[-3] = rgb[-3] - colorSubstract
                tsColor = ' '.join([str(i) for i in rgb])
                colorAdd += 65
                colorSubstract += 50

                # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
                # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
                # p = Process(target=getTimeseries, args=args)
                # p.start()
                # p.join()
                # list_values = self.out_queue.get()
                # self.out_queue.empty()
                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                            aggregate)

                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(data) > 0:
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
                      'cumulative': cumulative,  # timeserie['cumulative'],
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
                          'cumulative': cumulative,  # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)

        else:
            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date,
                                        aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)

            if len(data) > 0:
                data_available = True

            # Set defaults in case no entry exists in the DB
            ts = {'name': productcode + '-' + version + '-' + subproductcode,
                  'type': 'line',
                  'dashStyle': 'Solid',
                  'lineWidth': 2,
                  'color': '#000000',
                  'yAxis': productcode + ' - ' + version,
                  'data': data,
                  'cumulative': cumulative,  # timeserie['cumulative'],
                  'difference': timeserie['difference'],
                  'reference': timeserie['reference']
                  }
            for ts_drawprops in timeseries_drawproperties:
                # print ts_drawprops.color
                ts = {'name': ts_drawprops.tsname_in_legend,
                      'type': ts_drawprops.charttype,
                      'dashStyle': ts_drawprops.linestyle,
                      'lineWidth': ts_drawprops.linewidth,
                      'color': ts_drawprops.color.replace("  ", " "),
                      'yAxis': ts_drawprops.yaxes_id,
                      'data': data,
                      'cumulative': cumulative,  # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

    yaxes = []
    count = 0
    timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries)
    axes = len(timeseries_yaxes)
    for yaxe in timeseries_yaxes:
        # count += 1
        # opposite = "false"
        # # if axes >= 2 and count % 2 == 0:   # and yaxe.opposite == "f"
        # #     opposite = "false"
        # # if axes >= 2 and count % 2 != 0:   # and yaxe.opposite == "t"
        # #     opposite = "true"
        # if axes >= 2:
        #     if yaxe.opposite:
        #         opposite = "true"
        # if axes == 1:
        #     opposite = "false"

        if yaxe.yaxes_id in cum_yaxe:
            min = ''
            max = ''
        else:
            min = yaxe.min
            max = yaxe.max
        yaxe = {'id': yaxe.yaxes_id, 'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "),
                'unit': yaxe.unit, 'opposite': yaxe.opposite,
                'min': min, 'max': max, 'aggregation_type': yaxe.aggregation_type,
                'aggregation_min': yaxe.aggregation_min, 'aggregation_max': yaxe.aggregation_max}
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


def updateGraphProperties(params, graphtpl_info):
    updatestatus = '{"success":false, "message":"An error occured while updating the graph draw properties!"}'

    if 'graphproperty' in params:  # hasattr(getparams, "graphproperty")
        graphdrawprobs = params['graphproperty']

        try:
            querydb.update_user_graph_tpl_drawproperties(graphdrawprobs, graphtpl_info)
            updatestatus = '{"success":true, "message":"Graph draw properties updated!"}'
        except:
            updatestatus = '{"success":false, "error":"Error saving the Graph Draw Properties in the database!"}'

    else:
        updatestatus = '{"success":false, "message":"No graph properties given!"}'

    return updatestatus


def __updateChartProperties(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'chartproperty' in params:  # hasattr(getparams, "chartproperty")
        chartdrawprobs = {'chart_type': params['chartproperty']['chart_type'],
                          'chart_width': params['chartproperty']['chart_width'],
                          'chart_height': params['chartproperty']['chart_height'],
                          'chart_title_font_size': params['chartproperty']['chart_title_font_size'],
                          'chart_title_font_color': params['chartproperty']['chart_title_font_color'],
                          'chart_subtitle_font_size': params['chartproperty']['chart_subtitle_font_size'],
                          'chart_subtitle_font_color': params['chartproperty']['chart_subtitle_font_color'],
                          'yaxe1_font_size': params['chartproperty']['yaxe1_font_size'],
                          'yaxe2_font_size': params['chartproperty']['yaxe2_font_size'],
                          'legend_font_size': params['chartproperty']['legend_font_size'],
                          'legend_font_color': params['chartproperty']['legend_font_color'],
                          'xaxe_font_size': params['chartproperty']['xaxe_font_size'],
                          'xaxe_font_color': params['chartproperty']['xaxe_font_color'],
                          'yaxe3_font_size': params['chartproperty']['yaxe3_font_size']
                          }

        if crud_db.update('chart_drawproperties', chartdrawprobs):
            updatestatus = '{"success":"true", "message":"Chart draw properties updated!"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the chart draw properties!"}'

    else:
        updatestatus = '{"success":false, "message":"No chart properties passed!"}'

    return updatestatus


def getGraphProperties(params):
    if hasattr(params, "graphtype") and params['graphtype'] == '':
        params['graphtype'] = 'default'

    graphproperties_dict_all = []
    graphproperties = querydb.get_graph_drawproperties(params)

    if hasattr(graphproperties, "__len__") and graphproperties.__len__() > 0:
        for row in graphproperties:
            # row_dict = functions.row2dict(row)
            row_dict = row

            graphproperty = {'graph_tpl_id': row_dict['graph_tpl_id'],
                             'graph_type': row_dict['graph_type'],
                             'graph_width': row_dict['graph_width'],
                             'graph_height': row_dict['graph_height'],
                             'graph_title': row_dict['graph_title'],
                             'graph_title_font_size': row_dict['graph_title_font_size'],
                             'graph_title_font_color': row_dict['graph_title_font_color'],
                             'graph_subtitle': row_dict['graph_subtitle'],
                             'graph_subtitle_font_size': row_dict['graph_subtitle_font_size'],
                             'graph_subtitle_font_color': row_dict['graph_subtitle_font_color'],
                             'legend_position': row_dict['legend_position'],
                             'legend_font_size': row_dict['legend_font_size'],
                             'legend_font_color': row_dict['legend_font_color'],
                             'xaxe_font_size': row_dict['xaxe_font_size'],
                             'xaxe_font_color': row_dict['xaxe_font_color']
                             }

            graphproperties_dict_all.append(graphproperty)

        graphproperties_json = json.dumps(graphproperties_dict_all,
                                          ensure_ascii=False,
                                          # encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

        graphproperties_json = '{"success":"true", "total":' \
                               + str(graphproperties.__len__()) \
                               + ',"graphproperties":' + graphproperties_json + '}'

    else:
        graphproperties_json = '{"success":false, "error":"No graph properties defined!"}'

    return graphproperties_json


def __getChartProperties(params):
    charttype = 'default'
    if hasattr(params, "charttype") and params['charttype'] != '':
        charttype = params['charttype']

    chartproperties_dict_all = []
    chartproperties = querydb.get_chart_drawproperties(charttype)

    if hasattr(chartproperties, "__len__") and chartproperties.__len__() > 0:
        for row in chartproperties:
            row_dict = functions.row2dict(row)

            chartproperty = {'chart_type': row_dict['chart_type'],
                             'chart_width': row_dict['chart_width'],
                             'chart_height': row_dict['chart_height'],
                             'chart_title_font_size': row_dict['chart_title_font_size'],
                             'chart_title_font_color': row_dict['chart_title_font_color'],
                             'chart_subtitle_font_size': row_dict['chart_subtitle_font_size'],
                             'chart_subtitle_font_color': row_dict['chart_subtitle_font_color'],
                             'yaxe1_font_size': row_dict['yaxe1_font_size'],
                             'yaxe2_font_size': row_dict['yaxe2_font_size'],
                             'yaxe3_font_size': row_dict['yaxe3_font_size'],
                             'yaxe4_font_size': row_dict['yaxe4_font_size'],
                             'legend_font_size': row_dict['legend_font_size'],
                             'legend_font_color': row_dict['legend_font_color'],
                             'xaxe_font_size': row_dict['xaxe_font_size'],
                             'xaxe_font_color': row_dict['xaxe_font_color']
                             }

            chartproperties_dict_all.append(chartproperty)

        chartproperties_json = json.dumps(chartproperties_dict_all,
                                          ensure_ascii=False,
                                          # encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

        chartproperties_json = '{"success":"true", "total":' \
                               + str(chartproperties.__len__()) \
                               + ',"chartproperties":' + chartproperties_json + '}'

    else:
        chartproperties_json = '{"success":false, "error":"No chart properties defined!"}'

    return chartproperties_json


def updateTimeseriesDrawProperties(params):
    # crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    updatestatus = '{"success":"false", "message":"An error occured while updating the Timeseries Draw Properties!"}'

    if params.productcode != '':
        tsdrawproperties = params  # getparams['tsdrawproperties']

        try:
            querydb.update_user_tpl_timeseries_drawproperties(tsdrawproperties)
            updatestatus = '{"success":true, "message":"Timeseries Draw Properties updated!"}'
        except:
            updatestatus = '{"success":false, "error":"Error saving the Timeseries Draw Properties in the database!"}'

        # if crud_db.update('timeseries_drawproperties', tsdrawproperties):
        #     updatestatus = '{"success":"true", "message":"Timeseries Draw Properties updated!"}'
    else:
        updatestatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

    return updatestatus


def createTimeseriesDrawProperties(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":"false", "message":"An error occured while creating the Timeseries Draw Properties!"}'

    if "yaxe_id" in params['tsdrawproperties']:
        yaxe_id = {'yaxe_id': params['tsdrawproperties']['yaxe_id']}
        yaxe = crud_db.read('graph_yaxes', **yaxe_id)
        if hasattr(yaxe, "__len__") and yaxe.__len__() == 0:
            new_yaxe = {
                'yaxe_id': params['tsdrawproperties']['yaxe_id'],
                'title': 'TITLE',
                'title_color': '#000000',
                'title_font_size': 26,
                'min': None,
                'max': None,
                'unit': '',
                'opposite': False,
                'aggregation_type': 'mean',
                'aggregation_min': None,
                'aggregation_max': None
            }
            crud_db.create('graph_yaxes', new_yaxe)

    if 'tsdrawproperties' in params:
        tsdrawproperties = params['tsdrawproperties']

        if crud_db.create('timeseries_drawproperties_new', tsdrawproperties):
            createstatus = '{"success":"true", "message":"Timeseries Draw Properties created!"}'
    else:
        createstatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

    return createstatus


def getTimeseriesDrawProperties(params):
    tsdrawproperties_dict_all = []
    tsdrawproperties = querydb.get_timeseries_drawproperties(params)

    if hasattr(tsdrawproperties, "__len__") and tsdrawproperties.__len__() > 0:
        for row in tsdrawproperties:
            # row_dict = functions.row2dict(row)
            row_dict = row

            tsdrawproperty = {
                'productcode': row_dict['productcode'],
                'subproductcode': row_dict['subproductcode'],
                'version': row_dict['version'],
                'tsname_in_legend': row_dict['tsname_in_legend'],
                'charttype': row_dict['charttype'],
                'linestyle': row_dict['linestyle'],
                'linewidth': row_dict['linewidth'],
                'color': row_dict['color'],
                'yaxe_id': row_dict['yaxe_id']
            }

            tsdrawproperties_dict_all.append(tsdrawproperty)

        tsdrawproperties_json = json.dumps(tsdrawproperties_dict_all,
                                           ensure_ascii=False,
                                           # encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

        tsdrawproperties_json = '{"success":"true", "total":' \
                                + str(tsdrawproperties.__len__()) \
                                + ',"tsdrawproperties":' + tsdrawproperties_json + '}'

    else:
        tsdrawproperties_json = '{"success":false, "error":"No timeseries draw properties defined!"}'

    return tsdrawproperties_json


def __getTimeseriesDrawProperties():
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
                                           # encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

        tsdrawproperties_json = '{"success":"true", "total":' \
                                + str(tsdrawproperties.__len__()) \
                                + ',"tsdrawproperties":' + tsdrawproperties_json + '}'

    else:
        tsdrawproperties_json = '{"success":false, "error":"No timeseries draw properties defined!"}'

    return tsdrawproperties_json


def getProductLayer(getparams):
    import mapscript
    # To solve issue with Chla Legends (Tuleap ticket #10905 - see http://trac.osgeo.org/mapserver/ticket/1762)
    import locale
    locale.setlocale(locale.LC_NUMERIC, 'C')

    p = Product(product_code=getparams['productcode'], version=getparams['productversion'])
    dataset = p.get_dataset(mapset=getparams['mapsetcode'], sub_product_code=getparams['subproductcode'])
    # print dataset.fullpath

    # from datetime import datetime as dt
    dataset.get_filenames()
    if 'date' in getparams:
        filedate = getparams['date']
        dates_available = dataset.get_dates()
        # date_present = [True for date in dates_available if date.strftime("%Y%m%d") == filedate]
        # if not date_present[0]:
        # print filedate
        # print datetime.datetime.strptime(filedate, "%Y%m%d")
        file_exists = False
        for date in dates_available:
            if date.strftime("%Y%m%d") == filedate:
                file_exists = True
                # print date.strftime("%Y%m%d")

        # if not datetime.datetime.strptime(filedate, "%Y%m%d") in dates_available:
        if not file_exists:
            # print "NOT FOUND!"
            lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
            filedate = lastdate
    else:
        lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
        filedate = lastdate

    if dataset.no_year():
        filedate = dataset.strip_year(filedate)

    # Check the case of daily product, with time/minutes
    frequency_id = dataset._db_product.frequency_id
    date_format = dataset._db_product.date_format

    if frequency_id == 'e1day' and date_format == 'YYYYMMDD':
        regex = dataset.fullpath + filedate + '*' + '.tif'
        filename = glob.glob(regex)
        if len(filename) > 0:
            productfile = filename[0]
        else:
            filename = functions.set_path_filename(filedate,
                                                   getparams['productcode'],
                                                   getparams['subproductcode'],
                                                   getparams['mapsetcode'],
                                                   getparams['productversion'],
                                                   '.tif')
            productfile = dataset.fullpath + filename
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

    # if (hasattr(getparams, "outmask") and getparams['outmask'] == 'true'):
    #     # print productfile
    #     # print es_constants.base_tmp_dir
    #     from greenwich import Raster, Geometry
    #
    #     # try:
    #     #     from osgeo import gdal
    #     #     from osgeo import gdal_array
    #     #     from osgeo import ogr, osr
    #     #     from osgeo import gdalconst
    #     # except ImportError:
    #     #     import gdal
    #     #     import gdal_array
    #     #     import ogr
    #     #     import osr
    #     #     import gdalconst
    #
    #     # try:
    #
    #     # ogr.UseExceptions()
    #     wkt = getparams['selectedfeature']
    #     theGeomWkt = ' '.join(wkt.strip().split())
    #     # print wkt
    #     geom = Geometry(wkt=str(theGeomWkt), srs=4326)
    #     # print "wearehere"
    #     with Raster(productfile) as img:
    #         # Assign nodata from prod_info
    #         # img._nodata = nodata
    #         # print "nowwearehere"
    #         with img.clip(geom) as clipped:
    #             # Save clipped image (for debug only)
    #             productfile = es_constants.base_tmp_dir + '/clipped_'+filename
    #             # print productfile
    #             clipped.save(productfile)
    #
    #     # except:
    #     #     print 'errorrrrrrrrr!!!!!!'
    #
    # web.header('Content-type', 'image/png')
    # web.header('Content-transfer-encoding', 'binary')
    # buf = StringIO.StringIO()
    # mapscript.msIO_installStdoutToBuffer()
    # map = mapserver.getmap()
    ##map.save to a file fname.png
    ##web.header('Content-Disposition', 'attachment; filename="fname.png"')
    # contents = buf.getvalue()
    # return contents

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
    errorfile = es_constants.log_dir + "/mapserver_error.log"
    # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

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

    outputformat_jpg = mapscript.outputFormatObj('AGG/JPEG', 'jpg')
    outputformat_jpg.setOption("INTERLACE", "OFF")
    productmap.appendOutputFormat(outputformat_jpg)

    outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
    outputformat_png.setOption("INTERLACE", "OFF")
    productmap.appendOutputFormat(outputformat_png)

    # outputformat_gd = mapscript.outputFormatObj('GD/GIF', 'gif')
    # productmap.appendOutputFormat(outputformat_gd)

    productmap.selectOutputFormat('jpg')
    # productmap.debug = mapscript.MS_TRUE
    productmap.debug = mapscript.MS_OFF
    productmap.status = mapscript.MS_ON
    productmap.units = mapscript.MS_DD

    coords = list(map(float, inputparams['BBOX'].split(",")))
    lly = coords[0]
    llx = coords[1]
    ury = coords[2]
    urx = coords[3]
    productmap.setExtent(llx, lly, urx, ury)  # -26, -35, 60, 38
    # productmap.setExtent(lly, llx, ury, urx)   # -26, -35, 60, 38
    # print llx, lly, urx, ury

    # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
    # epsg = "+init=epsg:3857"
    # epsg = "+init=" + inputparams.CRS.lower()   # CRS = "EPSG:4326"
    epsg = inputparams['CRS'].lower()  # CRS = "EPSG:4326"
    productmap.setProjection(epsg)

    w = int(inputparams['WIDTH'])
    h = int(inputparams['HEIGHT'])
    productmap.setSize(w, h)

    # General web service information
    productmap.setMetaData("WMS_TITLE", "Product description")
    productmap.setMetaData("WMS_SRS", inputparams['CRS'].lower())
    # productmap.setMetaData("WMS_SRS", "epsg:3857")
    productmap.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 raster layers.")
    productmap.setMetaData("WMS_ENABLE_REQUEST", "*")  # necessary!!

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
            totwidth = float(old_div((row.totwidth - scale_offset), scale_factor))
            minstep = float(
                old_div((row.min_value - scale_offset), scale_factor))  # int(row.min_value*scale_factor+scale_offset)
            maxstep = float(
                old_div((row.max_value - scale_offset), scale_factor))  # int(row.max_value*scale_factor+scale_offset)
            minstepwidth = float(old_div((row.minstepwidth - scale_offset), scale_factor))
            maxstepwidth = float(old_div((row.maxstepwidth - scale_offset), scale_factor))
            realminstep = float(old_div((row.realminstep - scale_offset), scale_factor))
            realmaxstep = float(old_div((row.realmaxstep - scale_offset), scale_factor))
            totsteps = row.totsteps
            step_type = row.step_type

        processing_scale = 'SCALE=' + str(minstep) + ',' + str(
            maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

        if step_type == 'logarithmic':
            minbuckets = 32  # 256
            maxbuckets = 256  # 5000
        else:
            minbuckets = 32  # 256
            maxbuckets = 1024  # 5000

        num_buckets = maxbuckets
        if minstepwidth > 0:
            num_buckets = round(old_div(totwidth, minstepwidth), 0)

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
        layer.name = filenamenoextention
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON  # MS_DEFAULT
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

        closeconnection = "CLOSE_CONNECTION=DEFER"
        layer.setProcessing(closeconnection)

        legend_steps = querydb.get_legend_steps(legendid=inputparams['legendid'])
        if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
            stepcount = 0
            for step in legend_steps:
                stepcount += 1
                min_step = float(old_div((step.from_step - scale_offset), scale_factor))
                max_step = float(old_div((step.to_step - scale_offset), scale_factor))
                # min_step = float(step.from_step)
                # max_step = float(step.to_step)
                colors = list(map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip())))

                if stepcount == legend_steps.__len__():  # For the last step use <= max_step
                    expression_string = '([pixel] >= ' + str(min_step) + ' and [pixel] <= ' + str(max_step) + ')'
                else:
                    expression_string = '([pixel] >= ' + str(min_step) + ' and [pixel] < ' + str(max_step) + ')'
                # define class object and style
                layerclass = mapscript.classObj(layer)
                layerclass.name = layer.name + '_' + str(stepcount)
                layerclass.setExpression(expression_string)
                style = mapscript.styleObj(layerclass)
                style.color.setRGB(colors[0], colors[1], colors[2])

    # result_map_file = '/tmp/eStation2/MAP_result.map'
    # if os.path.isfile(result_map_file):
    #     os.remove(result_map_file)
    # productmap.save(result_map_file)

    image = productmap.draw()
    filename_png = es_constants.base_tmp_dir + '/' + filenamenoextention + str(llx) + '_' + str(lly) + '_' + str(
        urx) + '_' + str(ury) + '.jpg'
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
                                            # encoding='utf-8',
                                            sort_keys=True,
                                            indent=4,
                                            separators=(', ', ': '))

        assigned_datasets_json = '{"success":true, "total":' + str(
            legend_assigned_datasets.__len__()) + ',"assigneddatasets":' + assigned_datasets_json + '}'

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
            message = '{"success":true, "legendid": ' + str(
                newlegendid) + ', "legend_descriptive_name": "' + newlegendname + '","message":"Legend copied!"}'
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
            message = '{"success":true, "legendid": ' + str(
                params['legend']['legendid']) + ',"message":"Legend deleted!"}'
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
            'max_value': params['maxvalue'],
            'step_type': params['legend_type'],
            'defined_by': params['defined_by']
        }
        legendClasses = json.loads(params['legendClasses'])

        if int(params['legendid']) == -1:
            newlegendid = querydb.createlegend(legend)
            # if crud_db.create('legend', legend):
            if newlegendid != -1:
                message = '{"success":true, "legendid": ' + str(newlegendid) + ',"message":"Legend created!"}'
                for legendstep in legendClasses:
                    legendstep_dict = {'legend_id': newlegendid,
                                       'from_step': legendstep['from_step'],
                                       'to_step': legendstep['to_step'],
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
                                           'from_step': legendstep['from_step'],
                                           'to_step': legendstep['to_step'],
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


def ExportLegend(params):
    legendid = params['legendid']
    legendname = params['legendname']
    legendname = legendname.replace(':', '_')
    legendname = legendname.replace(',', '_')
    legendname = legendname.replace('  ', '_')
    legendname = legendname.replace(' ', '_')
    output_filename = es_constants.base_tmp_dir + os.path.sep + legendname + '.txt'

    legend_steps = querydb.export_legend_steps(legendid=legendid)

    file_id = open(output_filename, 'w')
    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        for legendstep in legend_steps:
            if legendstep['legendstep'] is not None:
                lstep = legendstep['legendstep']
                file_id.write(lstep)
                file_id.write('\n')
    file_id.close()

    return output_filename


def GetLegendClasses(legendid):
    legendsteps_dict_all = []
    legend_steps = querydb.get_legend_steps(legendid=legendid)

    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        for legendstep in legend_steps:
            # row_dict = functions.row2dict(legendstep)
            row_dict = legendstep

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
                                      # encoding='utf-8',
                                      sort_keys=True,
                                      indent=4,
                                      separators=(', ', ': '))

        legendsteps_json = '{"success":"true", "total":' + str(
            legend_steps.__len__()) + ',"legendclasses":' + legendsteps_json + '}'

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
            colorschemeHTML = legendname + '<table cellspacing=0 cellpadding=0 width=100%><tr>'

            for step in legend_steps:
                # convert step['color_rgb'] from RGB to html color
                color_rgb = step.color_rgb.split(' ')
                color_html = functions.rgb2html(color_rgb)
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = 'rgb(' + r + ',' + g + ',' + b + ')'
                colorschemeHTML += "<td height=15 style='padding:0; margin:0; background-color: " + color_html + ";'></td>"
            colorschemeHTML += '</tr></table>'

            legend_dict = {'legendid': row_dict['legend_id'],
                           'colourscheme': colorschemeHTML,
                           'legendname': row_dict['legend_name'],
                           'minvalue': row_dict['min_value'],
                           'maxvalue': row_dict['max_value'],
                           'legend_descriptive_name': row_dict['colorbar'],
                           'defined_by': row_dict['defined_by'],
                           'legend_type': row_dict['step_type']
                           }

            legends_dict_all.append(legend_dict)

        legends_json = json.dumps(legends_dict_all,
                                  ensure_ascii=False,
                                  # encoding='utf-8',
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
                with open(colorschemes_file, "rb") as text_file:
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
            with open(colorschemes_file, "wb") as text_file:
                text_file.write(colorschemes_json)
        except IOError:
            try:
                os.remove(colorschemes_file)  # remove file and recreate next call
            except OSError:
                pass

    # colorschemes_json = ColorSchemes().encode('utf-8').decode()
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
                color_html = 'rgb(' + r + ',' + g + ',' + b + ')'
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

        colorschemes = '{"success":"true", "total":' + str(all_legends.__len__()) + ',"legends":' + legends_json + '}'
    else:
        colorschemes = '{"success":"true", "message":"No legends defined!"}'

    return colorschemes


def getProductNavigatorDataSets(force):
    # import time
    datasetsinfo_file = es_constants.base_tmp_dir + os.path.sep + 'product_navigator_datasets_info.json'
    if force:
        dataset_json = ProductNavigatorDataSets().encode('utf-8').decode()
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(dataset_json)
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
            dataset_json = ProductNavigatorDataSets().encode('utf-8').decode()
            try:
                with open(datasetsinfo_file, "w") as text_file:
                    text_file.write(dataset_json)
            except IOError:
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(datasetsinfo_file) as text_file:
                    dataset_json = text_file.read()
            except IOError:
                dataset_json = ProductNavigatorDataSets().encode('utf-8').decode()
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        dataset_json = ProductNavigatorDataSets().encode('utf-8').decode()
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(dataset_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return dataset_json


def ProductNavigatorDataSets():
    db_products = querydb.get_products(activated=True, masked=None)

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
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)

                    if mapset_info != [] and hasattr(mapset_info, "__len__") and mapset_info.__len__() > 0:
                        # for mapsetinfo in mapset_info:
                        #     mapset_dict = functions.row2dict(mapsetinfo)

                        mapset_info['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print productcode + ' - ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode,
                                                                  masked=True)  # -> TRUE means only NOT masked sprods

                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                dataset_dict['mapsetcode'] = mapset

                                # dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                # completeness = dataset.get_dataset_normalized_info()
                                # dataset_dict['datasetcompleteness'] = completeness

                                mapset_info['mapsetdatasets'].append(dataset_dict)
                        if mapset_info['mapsetdatasets'].__len__() > 0:
                            prod_dict['productmapsets'].append(mapset_info)

                if prod_dict['productmapsets'].__len__() > 0:
                    products_dict_all.append(prod_dict)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        dataset_json = '{"success":"true", "total":' \
                       + str(db_products.__len__()) \
                       + ',"products":' + prod_json + '}'

    else:
        dataset_json = '{"success":false, "error":"No data sets defined!"}'

    return dataset_json


def getDataSets(force):
    # import time
    datasetsinfo_file = es_constants.base_tmp_dir + os.path.sep + 'datasets_info.json'
    if force:
        datamanagement_json = DataSets().encode('utf-8').decode()
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
            datamanagement_json = DataSets().encode('utf-8').decode()
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
                datamanagement_json = DataSets().encode('utf-8').decode()
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        datamanagement_json = DataSets().encode('utf-8').decode()
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
    systemsettings = functions.getSystemSettings()

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
            # does the product have mapsets AND subproducts in the file system?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() == 0:
                checkCreateSubproductDir(productcode, version)
                p = Product(product_code=productcode, version=version)
                all_prod_mapsets = p.mapsets
                all_prod_subproducts = p.subproducts

            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_dict = []
                    # print mapset
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)

                    if mapset_info != [] and hasattr(mapset_info, "__len__") and mapset_info.__len__() > 0:
                        # for mapsetinfo in mapset_info:
                        #     mapset_dict = functions.row2dict(mapsetinfo)
                        # print mapset_dict
                        mapset_info['productcode'] = productcode
                        mapset_info['version'] = version
                        # else:
                        #   mapset_dict['mapsetcode'] = mapset
                        mapset_info['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print 'productcode: ' + productcode
                            # print 'version: ' + version
                            # print 'subproductcode: ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode)
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
                                        to_date = today + datetime.timedelta(days=1)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date,
                                                  'to_date': to_date}
                                    elif dataset_info.frequency_id == 'e30minute':
                                        # dataset_dict['nodisplay'] = 'no_minutes_display'
                                        today = datetime.date.today()
                                        from_date = today - datetime.timedelta(days=6)
                                        to_date = today + datetime.timedelta(days=1)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date,
                                                  'to_date': to_date}
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

                                    # elif dataset_info.frequency_id == 'e1dekad' and dataset_info.date_format == 'YYYYMMDD':
                                    #     today = datetime.date.today()
                                    #     from_date = today - relativedelta(years=5)
                                    #
                                    #     kwargs = {'mapset': mapset,
                                    #               'sub_product_code': subproductcode,
                                    #               'from_date': from_date}
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

                                    if systemsettings['type_installation'].lower() == 'jrc_online':
                                        # completeness = dataset.get_dataset_normalized_info()
                                        dataset_dict['datasetcompleteness'] = ''  # completeness['datasetcompleteness']
                                        dataset_dict['datasetcompletenessimage'] = ''
                                    else:
                                        completeness = getDatasetCompleteness(dataset, True)
                                        dataset_dict['datasetcompleteness'] = completeness['datasetcompleteness']
                                        dataset_dict['datasetcompletenessimage'] = completeness[
                                            'datasetcompletenessimage']

                                    # dataset_dict['datasetcompletenessimage'] = createDatasetCompletenessImage(completeness, dataset_info.frequency_id)
                                    dataset_dict['nodisplay'] = 'false'

                                    dataset_dict['mapsetcode'] = mapset_info['mapsetcode']
                                    dataset_dict['mapset_descriptive_name'] = mapset_info['descriptive_name']

                                    mapset_info['mapsetdatasets'].append(dataset_dict)
                                else:
                                    pass
                    prod_dict['productmapsets'].append(mapset_info)
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


def getDatasetCompleteness(dataset, fordatamanagement):
    completeness_dict = {}
    output_dir = es_constants.base_local_dir + os.path.sep + 'completeness_bars/'
    functions.check_output_dir(output_dir)  # if not exists output_dir -> create output_dir

    prod_ident = functions.set_path_filename_no_date(dataset._db_product.productcode,
                                                     dataset._db_product.subproductcode,
                                                     dataset.mapset,
                                                     dataset._db_product.version, '')

    if fordatamanagement:
        filePrefix = 'Dataset_'
    else:
        filePrefix = 'Ingestion_'

    completeness_file_json = output_dir + os.path.sep + filePrefix + prod_ident + '.json'
    completeness_file_png = output_dir + os.path.sep + filePrefix + prod_ident + '.png'

    # Check if completeness_file_json exists in path dataset
    if os.path.isfile(completeness_file_json) and os.path.isdir(dataset.fullpath):
        # command = 'find ' + dataset.fullpath + ' -newer ' + output_dir + completeness_file_json
        # list = os.popen(command).read()
        # if list != '':

        # Is NOT .json up-to-date with dir contents -> re-create .json
        if os.lstat(dataset.fullpath).st_mtime > os.lstat(completeness_file_json).st_mtime:
            completeness = dataset.get_dataset_normalized_info()
            completeness_dict['datasetcompleteness'] = completeness
            completeness_dict['datasetcompletenessimage'] = createDatasetCompletenessImage(completeness,
                                                                                           dataset.frequency_id,
                                                                                           completeness_file_png,
                                                                                           fordatamanagement)
            with open(completeness_file_json, 'w') as f:
                json.dump(completeness_dict, f)
        # ... else read it
        else:
            with open(completeness_file_json) as f:
                completeness_dict = json.load(f)
    # Create .json
    else:
        completeness = dataset.get_dataset_normalized_info()
        completeness_dict['datasetcompleteness'] = completeness
        completeness_dict['datasetcompletenessimage'] = createDatasetCompletenessImage(completeness,
                                                                                       dataset.frequency_id,
                                                                                       completeness_file_png,
                                                                                       fordatamanagement)
        with open(completeness_file_json, 'w') as f:
            json.dump(completeness_dict, f)

    return completeness_dict


def createDatasetCompletenessImage(datasetcompleteness, frequency_id, completeness_file_png, fordatamanagement):
    # TODO: IMPORTANT to set FONTCONFIG_FILE and FONTCONFIG_PATH for matplotlib
    # ToDo:   export FONTCONFIG_PATH=/etc/fonts
    # ToDO:   export FONTCONFIG_FILE=/etc/fonts/fonts.conf
    # import io
    # import StringIO

    # import matplotlib as mpl
    # mpl.use('agg')
    # mpl.rcParams['savefig.pad_inches'] = 0
    # from matplotlib import pyplot as plt
    # plt.autoscale(tight=True)

    totfiles = None
    missingfiles = None
    firstdate = ''
    lastdate = ''
    intervals = []
    fignum = 1
    if fordatamanagement:
        fignum = 500

    # create a figure with size height = yinch and width = xinch (in inches)
    # set the backgound color to white and resolution to dpi=128
    xinch = 3.4
    yinch = 0.38
    fig, ax = plt.subplots(num=fignum, figsize=(xinch, yinch), frameon=False, facecolor='w', dpi=128, tight_layout=True)
    # fignumber = fig.number
    # print fignumber
    fig.subplots_adjust(left=0.07,
                        right=0.95,
                        bottom=0.15,
                        top=0.9,
                        wspace=0,
                        hspace=0)  # Set padding around graph to create space for lables
    ax.set_ylim(0, 4)  # set the min and max of the yaxe to regulate the height of the horizonal bar
    ax.set_xlim(0, 100)  # set the min and max of the xaxe to regulate the width of the horizonal bar

    for attr, value in datasetcompleteness.items():
        if attr == 'missingfiles':
            missingfiles = value
        if attr == 'totfiles':
            totfiles = value
        if attr == 'firstdate':
            if len(value) > 10:
                firstdate = value[:10]
            else:
                firstdate = value
        if attr == 'lastdate':
            if len(value) > 10:
                lastdate = value[:10]
            else:
                lastdate = value
        if attr == 'intervals':
            intervals = value

    if frequency_id == 'singlefile' and totfiles == 1 and missingfiles == 0:
        d = 100
        color = '#81AF34'
        ax.barh(0, d, color=color, height=5, linewidth=0, align='center')
        totfiles = 'Files: ' + str(totfiles)
        missingfiles = 'Missing: ' + str(missingfiles)
        firstdate = ''
        lastdate = ''

    elif totfiles < 2 and missingfiles < 2:
        d = 100
        color = '#808080'
        ax.barh(0, d, color=color, height=5, linewidth=0, align='center')
        totfiles = 'Not any data'
        missingfiles = ''
        firstdate = ''
        lastdate = ''

    else:
        left = NP.zeros(1)  # left alignment of data starts at zero
        for interval in intervals:
            d = interval['intervalpercentage']
            if interval['missing']:
                color = '#FF0000'
            else:
                color = '#81AF34'

            if interval['intervaltype'] == 'permanent-missing':
                color = '#808080'

            ax.barh(0, d, color=color, height=5, linewidth=0, align='center', left=left)
            # accumulate the left-hand offsets
            left += d
        totfiles = 'Files: ' + str(totfiles)
        missingfiles = 'Missing: ' + str(missingfiles)

    font1 = {  # 'family': 'sans-serif',
        'color': 'black',
        'weight': 'bold',
        'size': 6}

    font2 = {  # 'family': 'sans-serif',
        'color': 'black',
        'weight': 'bold',
        'size': 6.5}

    font3 = {  # 'family': 'sans-serif',
        'color': '#FF0000',
        'weight': 'bold',
        'size': 6.5}

    # Add and position labels to graph (startdate, files, missing and enddate labels)
    fig.text(0.02, 0.7, firstdate, fontdict=font1)
    fig.text(0.3, 0.72, totfiles, fontdict=font2)
    fig.text(0.55, 0.72, missingfiles, fontdict=font3)
    if len(lastdate) < 6:
        fig.text(0.9, 0.7, lastdate, fontdict=font1)
    else:
        fig.text(0.83, 0.7, lastdate, fontdict=font1)

    ax.axis('off')  # do not show the axes
    # plt.margins(0)  # remove the margins -> creates conflict, replaced with: see above ax.set_xlim(0, 100)
    # plt.draw()    # not needed because fig.savefig() draws also
    fig.savefig(completeness_file_png, bbox_inches=0, pad_inches=0)
    plt.close(fig)
    # plt.close('all')

    encoded = base64.b64encode(open(completeness_file_png, "rb").read())
    datasetcompletenessimage = "data:image/png;base64," + encoded.decode()

    # buf = StringIO.StringIO()
    # plt.savefig(buf, format='png', bbox_inches=0, pad_inches=0)
    # encoded = base64.b64encode(str(buf))
    # buf.close()

    return datasetcompletenessimage


def getTimeseriesProducts(force):
    # import time
    timeseriesproducts_file = es_constants.base_tmp_dir + os.path.sep + 'timeseries_products.json'

    if force:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8').decode()
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
            timeseriesproducts_json = TimeseriesProducts().encode('utf-8').decode()
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
                timeseriesproducts_json = TimeseriesProducts().encode('utf-8').decode()
                try:
                    os.remove(timeseriesproducts_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8').decode()
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
    import copy
    # import time
    # t0 = time.time()
    # print 'START: ' + str(t0)

    # Get all subproducts with timeseries_role = 'Initial'
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
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != [] and hasattr(mapset_info, "__len__") and mapset_info.__len__() > 0:
                        # for mapsetinfo in mapset_info:
                        #     mapset_record = functions.row2dict(mapsetinfo)

                        tmp_prod_dict = copy.deepcopy(prod_dict)
                        tmp_prod_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_info['mapsetcode']
                        tmp_prod_dict['mapsetcode'] = mapset_info['mapsetcode']
                        tmp_prod_dict['mapset_name'] = mapset_info['descriptive_name']

                        # t3 = time.time()
                        # print 'before getting dataset info: ' + str(t3)

                        dataset = p.get_dataset(mapset=mapset, sub_product_code=tmp_prod_dict['subproductcode'])
                        # dataset.get_filenames()
                        all_present_product_dates = dataset.get_dates()

                        # t4 = time.time()
                        # tot_get_dataset = t4-t3
                        # print 'after getting dataset info: ' + str(tot_get_dataset)

                        # t5 = time.time()
                        # print 'before getting years: ' + str(t5)

                        distinctyears = []
                        for product_date in all_present_product_dates:
                            if product_date is not None and product_date.year not in distinctyears:
                                distinctyears.append(product_date.year)
                        tmp_prod_dict['years'] = distinctyears

                        # If there is data available on disk, include the subproduct with timeseries_role='Initial' in the list!
                        if tmp_prod_dict['years'].__len__() > 0:
                            products_dict_all.append(tmp_prod_dict)
                            # tmp_prod_dict = copy.deepcopy(prod_dict)
                            #
                            # products_dict_all.append(tmp_prod_dict)
                            # tmp_prod_dict = []

                        # t6 = time.time()
                        # total = t6-t5
                        # print 'after getting years: ' + str(total)

                        # Get all subproducts which have as timeseries_role = subproductcode ('Initial')
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
                                    if product_date is not None and product_date.year not in distinctyears:
                                        distinctyears.append(product_date.year)

                                dataset_dict = {}
                                dataset_dict['category_id'] = prod_record['category_id']
                                dataset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                                dataset_dict['order_index'] = prod_record['order_index']
                                dataset_dict['productid'] = dataset_record['productid']
                                dataset_dict['productcode'] = dataset_record['productcode']
                                dataset_dict['version'] = dataset_record['version']
                                dataset_dict['subproductcode'] = dataset_record['subproductcode']
                                dataset_dict['productmapsetid'] = tmp_prod_dict['productmapsetid']
                                dataset_dict['display_index'] = dataset_record['display_index']
                                dataset_dict['mapsetcode'] = mapset_info['mapsetcode']
                                dataset_dict['mapset_name'] = mapset_info['descriptive_name']
                                dataset_dict['group_product_descriptive_name'] = prod_record[
                                    'group_product_descriptive_name']
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

                                # If there is data available on disk, include the subproduct in the list!
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


def __TimeseriesProducts():
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
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    # mapset_dict = functions.row2dict(mapset_info)
                    mapset_info['timeseriesmapsetdatasets'] = []
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
                            mapset_info['timeseriesmapsetdatasets'].append(dataset_dict)

                    if dataset_dict['years'].__len__() > 0:
                        # tmp_prod_dict = prod_dict.copy()
                        tmp_prod_dict = copy.deepcopy(prod_dict)

                        tmp_prod_dict['productmapsets'].append(mapset_info)
                        products_dict_all.append(tmp_prod_dict)
                        tmp_prod_dict = []

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

    return datamanagement_json


def __TimeseriesProductsTree():
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
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != []:
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

        datamanagement_json = '{"success":"true", "total":' \
                              + str(db_products.__len__()) \
                              + ',"products":' + prod_json + '}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    return datamanagement_json


def getIngestion(force):
    # import time
    ingestioninfo_file = es_constants.base_tmp_dir + os.path.sep + 'ingestion_info.json'
    if force:
        ingestions_json = Ingestion().encode('utf-8').decode()
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
            # logger.info("getIngestion: FORCE writing ingestion_info.json!")
            # logger.info(ingestioninfo_file)
        except IOError:
            try:
                logger.error("getIngestion: Error writing ingestion_info.json!\n -> {}".format(IOError))
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                logger.error("getIngestion: Error removing ingestion_info.json!\n -> {}".format(IOError))
                pass

    elif os.path.isfile(ingestioninfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(ingestioninfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            ingestions_json = Ingestion().encode('utf-8').decode()
            try:
                with open(ingestioninfo_file, "w") as text_file:
                    text_file.write(ingestions_json)
                # logger.info("getIngestion: writing ingestion_info.json!")
            except IOError:
                try:
                    logger.error("getIngestion: Error writing ingestion_info.json!\n -> {}".format(IOError))
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    logger.error("getIngestion: Error removing ingestion_info.json!\n -> {}".format(IOError))
                    pass
        else:
            try:
                with open(ingestioninfo_file) as text_file:
                    ingestions_json = text_file.read()
                # logger.info("getIngestion: writing ingestion_info.json!")
            except IOError:
                ingestions_json = Ingestion().encode('utf-8').decode()
                try:
                    logger.error("getIngestion: Error writing ingestion_info.json!\n -> {}".format(IOError))
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    logger.error("getIngestion: Error removing ingestion_info.json!\n -> {}".format(IOError))
                    pass

    else:
        ingestions_json = Ingestion().encode('utf-8').decode()
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
            # logger.info("getIngestion: writing ingestion_info.json!")
        except IOError:
            try:
                logger.error("getIngestion: Error writing ingestion_info.json!\n -> {}".format(IOError))
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                logger.error("getIngestion: Error removing ingestion_info.json!\n -> {}".format(IOError))
                pass
    return ingestions_json


def Ingestion():
    from dateutil.relativedelta import relativedelta

    # return web.ctx
    ingestions = querydb.get_ingestions()
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
                    to_date = today + datetime.timedelta(days=1)
                    # week_ago = datetime.datetime(2015, 8, 27, 00, 00)   # .strftime('%Y%m%d%H%S')
                    # kwargs.update({'from_date': week_ago})  # datetime.date(2015, 08, 27)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date,
                              'to_date': to_date}
                    # dataset = Dataset(**kwargs)
                    # completeness = dataset.get_dataset_normalized_info()
                elif row.frequency_id == 'e30minute':
                    today = datetime.date.today()
                    from_date = today - datetime.timedelta(days=6)
                    to_date = today + datetime.timedelta(days=1)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date,
                              'to_date': to_date}
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

                # elif row.frequency_id == 'e1dekad':
                #     today = datetime.date.today()
                #     from_date = today - relativedelta(years=5)
                #
                #     kwargs = {'product_code': row.productcode,
                #               'sub_product_code': row.subproductcode,
                #               'version': row.version,
                #               'mapset': row.mapsetcode,
                #               'from_date': from_date}
                else:
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode}
                # print kwargs
                dataset = Dataset(**kwargs)

                completeness = getDatasetCompleteness(dataset, False)
                ingest_dict['completeness'] = completeness['datasetcompleteness']
                ingest_dict['datasetcompletenessimage'] = completeness['datasetcompletenessimage']
                # completeness = dataset.get_dataset_normalized_info()
                # ingest_dict['completeness'] = completeness
                ingest_dict['nodisplay'] = 'false'
            else:
                ingest_dict['datasetcompletenessimage'] = ''
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


def getIngestSubProducts():
    ingestsubproducts = querydb.get_ingestsubproducts()

    ingestsubproducts_json = functions.tojson(ingestsubproducts)
    ingestsubproducts_json = '{"success":"true", "total":' + str(
        ingestsubproducts.__len__()) + ',"ingestsubproducts":[' + ingestsubproducts_json + ']}'
    return ingestsubproducts_json


def CreateIngestSubProduct(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    if params['version'] == '':
        version = 'undefined'
    else:
        version = params['version']

    productinfo = {'productcode': params['productcode'],
                   'version': version,
                   'subproductcode': params['subproductcode'],
                   'category_id': params['category_id'],
                   'product_type': 'Ingest',
                   'activated': False,
                   'provider': params['provider'].replace("'", "''"),
                   'descriptive_name': params['descriptive_name'].replace("'", "''"),
                   'description': params['description'].strip(u'\u200b').replace("'", "''"),
                   'defined_by': params['defined_by'],
                   'frequency_id': params['frequency_id'],
                   'date_format': params['date_format'],
                   'data_type_id': params['data_type_id'],
                   'scale_factor': params['scale_factor'] if functions.is_float(params['scale_factor']) else None,
                   'scale_offset': params['scale_offset'] if functions.is_float(params['scale_offset']) else None,
                   'nodata': params['nodata'] if functions.is_int(params['nodata']) else None,
                   'mask_min': params['mask_min'] if functions.is_float(params['mask_min']) else None,
                   'mask_max': params['mask_max'] if functions.is_float(params['mask_max']) else None,
                   'unit': params['unit'],
                   'masked': params['masked'],
                   'timeseries_role': params['timeseries_role'],
                   'display_index': int(params['display_index']) if params['display_index'].isdigit() else None
                   }

    if crud_db.create('product', productinfo):
        createstatus = '{"success":true, "message":"Ingest Sub Product created!"}'
    else:
        createstatus = '{"success":false, "message":"An error occured while creating the Ingest Sub Product!"}'

    return createstatus


def UpdateIngestSubProduct(params):
    if params['version'] == '':
        version = 'undefined'
    else:
        version = params['version']

    productinfo = {'productcode': params['productcode'],
                   'version': version,
                   'orig_subproductcode': params['orig_subproductcode'],
                   'subproductcode': params['subproductcode'],
                   'category_id': params['category_id'],
                   'product_type': 'Ingest',
                   'activated': 'f',
                   'provider': params['provider'].replace("'", "''"),
                   'descriptive_name': params['descriptive_name'].replace("'", "''"),
                   'description': params['description'].strip(u'\u200b').replace("'", "''"),
                   'defined_by': params['defined_by'],
                   'frequency_id': params['frequency_id'],
                   'date_format': params['date_format'],
                   'data_type_id': params['data_type_id'],
                   'scale_factor': params['scale_factor'] if functions.is_float(params['scale_factor']) else 'NULL',
                   'scale_offset': params['scale_offset'] if functions.is_float(params['scale_offset']) else 'NULL',
                   'nodata': params['nodata'] if functions.is_int(params['nodata']) else 'NULL',
                   'mask_min': params['mask_min'] if functions.is_float(params['mask_min']) else 'NULL',
                   'mask_max': params['mask_max'] if functions.is_float(params['mask_max']) else 'NULL',
                   'unit': params['unit'],
                   'masked': params['masked'],
                   'timeseries_role': params['timeseries_role'],
                   'display_index': params['display_index'] if params['display_index'].isdigit() else 'NULL'
                   }
    # print (productinfo)
    productupdated = querydb.update_ingest_subproduct_info(productinfo)

    if productupdated:
        updatestatus = '{"success":"true", "message":"Ingest Sub Product updated!"}'
    else:
        updatestatus = '{"success":false, "message":"An error occured while updating the Ingest Sub Product!"}'

    return updatestatus


def DeleteIngestSubProduct(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])
    params = params['ingestproduct']

    if params['productcode'] != '' and params['version'] != '' and params['subproductcode'] != '':
        ingest_sub_product = {
            'productcode': params['productcode'],
            'version': params['version'],
            'subproductcode': params['subproductcode']
        }

        if crud_db.delete('product', **ingest_sub_product):
            deletestatus = '{"success":true, "productcode": "' + params['productcode'] + '", "version": "' + params[
                'version'] + '",' + \
                           ' "subproductcode": "' + params['subproductcode'] + '", ' + \
                           ' "message":"Ingest Sub Product deleted!"}'
        else:
            deletestatus = '{"success":false, "message":"An error occured while deleting the Ingest Sub Product!"}'
    else:
        deletestatus = '{"success":false, "message":"No primary key values given for Ingest Sub Product!"}'

    return deletestatus


def getSubDatasourceDescriptions():
    subdatasource_descriptions = querydb.get_active_subdatasource_descriptions()

    subdatasource_descriptions_json = functions.tojson(subdatasource_descriptions)
    subdatasource_descriptions_json = '{"success":"true", "total":' + str(
        subdatasource_descriptions.__len__()) + ',"subdatasourcedescription":[' + subdatasource_descriptions_json + ']}'
    return subdatasource_descriptions_json


def CreateSubDatasourceDescription(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    if params['version'] == '':
        version = 'undefined'
    else:
        version = params['version']

    datasource_description = {
        'datasource_descr_id': params['pads_data_source_id'],
        'preproc_type': params['preproc_type'],
        'native_mapset': params['native_mapset']
    }
    sub_datasource_description = {
        'productcode': params['productcode'],
        'subproductcode': params['subproductcode'],
        'version': version,
        'datasource_descr_id': params['datasource_descr_id'],
        'scale_factor': params['scale_factor'] if functions.is_float(params['scale_factor']) else None,
        'scale_offset': params['scale_offset'] if functions.is_float(params['scale_offset']) else None,
        'no_data': params['no_data'] if functions.is_int(params['no_data']) else None,
        'data_type_id': params['data_type_id'],
        'mask_min': params['mask_min'] if functions.is_float(params['mask_min']) else None,
        'mask_max': params['mask_max'] if functions.is_float(params['mask_max']) else None,
        're_process': params['re_process'],
        're_extract': params['re_extract'],
        'scale_type': params['scale_type'],
    }

    createstatus = '{"success":false, "message":"An error occured while creating the Sub Datasource Description!"}'
    if crud_db.create('sub_datasource_description', sub_datasource_description):
        if crud_db.update('datasource_description', datasource_description):
            createstatus = '{"success":true, "message":"Sub Datasource Description created!"}'

    return createstatus


def UpdateSubDatasourceDescription(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    if params['version'] == '':
        version = 'undefined'
    else:
        version = params['version']

    datasource_description = {
        'datasource_descr_id': params['pads_data_source_id'],
        'preproc_type': params['preproc_type'],
        'native_mapset': params['native_mapset']
    }
    sub_datasource_description = {
        'productcode': params['productcode'],
        'subproductcode': params['subproductcode'],
        'version': version,
        'datasource_descr_id': params['datasource_descr_id'],
        'scale_factor': params['scale_factor'] if functions.is_float(params['scale_factor']) else None,
        'scale_offset': params['scale_offset'] if functions.is_float(params['scale_offset']) else None,
        'no_data': params['no_data'] if functions.is_int(params['no_data']) else None,
        'data_type_id': params['data_type_id'],
        'mask_min': params['mask_min'] if functions.is_float(params['mask_min']) else None,
        'mask_max': params['mask_max'] if functions.is_float(params['mask_max']) else None,
        're_process': params['re_process'],
        're_extract': params['re_extract'],
        'scale_type': params['scale_type'],
    }

    status = '{"success":false, "message":"An error occured while updating the Sub Datasource Description!"}'
    if crud_db.update('sub_datasource_description', sub_datasource_description):
        if crud_db.update('datasource_description', datasource_description):
            status = '{"success":true, "message":"Sub Datasource Description updated!"}'

    return status


def DeleteSubDatasourceDescription(productcode, version, subproductcode, datasource_id):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

    if productcode != '' and version != '' and subproductcode != '' and datasource_id != '':
        sub_datasource_description = {
            'productcode': productcode,
            'version': version,
            'subproductcode': subproductcode,
            'datasource_id': datasource_id
        }

        if crud_db.delete('sub_datasource_description', **sub_datasource_description):
            deletestatus = '{"success":true, "productcode": "' + productcode + '", "version": "' + version + '",' + \
                           ' "subproductcode": "' + subproductcode + '", "datasource_id": "' + datasource_id + '",' + \
                           ' "message":"Sub Datasource Description deleted!"}'
        else:
            deletestatus = '{"success":false, "message":"An error occured while deleting the Sub Datasource Description!"}'
    else:
        deletestatus = '{"success":false, "message":"No primary key values given for Sub Datasource Description!"}'

    return deletestatus


def getProcessing(force):
    # import time
    # force = True
    processinginfo_file = es_constants.base_tmp_dir + os.path.sep + 'processing_info.json'
    if force:
        processing_chains_json = Processing().encode('utf-8').decode()
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
            processing_chains_json = Processing().encode('utf-8').decode()
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
                processing_chains_json = Processing().encode('utf-8').decode()
                try:
                    os.remove(processinginfo_file)  # remove file and recreate next call
                except OSError:
                    pass
            finally:
                text_file.close()

    else:
        processing_chains_json = Processing().encode('utf-8').decode()
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
