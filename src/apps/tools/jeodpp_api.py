from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#
#	purpose: To incorporate all the JEODPP request and download methods here
#	author:  Vijay Charan
#	date:	 09.2019
#   descr:	 Gets data from JEODPP


from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
import requests
# import pycurl

import json
import os
import pycurl
import certifi
import datetime
import tempfile
import shutil
import zipfile
import base64
from lib.python import es_logging as log
from io import BytesIO
from config import es_constants
logger = log.my_logger(__name__)

def generate_list_products(dates, template, frequency, base_url, usr_pwd):

    list_product_id_band = []
    # To check if the user and password is not defined and throw error
    if usr_pwd is ':' or usr_pwd is None:
        logger.warning('User and password is not defined to query the JEODPP server')
        return list_product_id_band

    #Get the parameters from the template
    parameters = json.loads(template)
    bands = parameters.get('band')
    minlon = parameters.get('minlon')
    minlat = parameters.get('minlat')
    maxlon = parameters.get('maxlon')
    product_type = parameters.get('product_type')
    maxlat = parameters.get('maxlat')
    upper_left_coord = minlon+' '+maxlat
    upper_right_coord = maxlon+' '+maxlat
    lower_right_coord = maxlon+' '+minlat
    lower_left_coord = minlon+' '+minlat
    wkt = 'POLYGON(('+upper_left_coord+','+upper_right_coord+','+lower_right_coord+','+lower_left_coord+','+upper_left_coord+'))'   #POLYGON((36.11 -8.92,36.45 -8.92,36.45 -9.15,36.11 -9.15,36.11 -8.92))
    max_clouds = parameters.get('max_clouds')

    download_links = get_download_links(dates,wkt,max_clouds,frequency,product_type)
    for download_link in download_links:
        result = get_json_from_url(str(base_url + os.path.sep + download_link), userpwd=str(usr_pwd), https_params='')
        if result is not 1:
            for each_dict in result:
                # {"acquisitionStartTime": "2018-04-01T09:05:51.026Z",
                #     "cloudCoverPercentage": "17.290071",
                #     "crs": "EPSG:32634",
                #     "productType": "S2MSI2A",
                #     "uuid": "b0f00735-d493-4295-8140-38ea0ae270f4",
                #     "id": "S2A_MSIL2A_20180401T090551_N0207_R050_T34SFF_20180401T111317"
                # }
                product_id = each_dict.get("id")
                # id = each_dict.get("id")
                # productType = each_dict.get("productType")
                # cloudCoverPercentage = each_dict.get("cloudCoverPercentage")
                # if cloudCoverPercentage > X:
                #     list_product_id_band.append(product_id)
                for band in str(bands).split(','):
                    list_product_id_band.append(product_id+':'+band)

    return list_product_id_band


def get_download_links(dates, wkt,max_clouds, frequency, product_type):

    list_download_links = []
    # parameters = json.loads(template)
    # minlon = parameters.get('minlon')
    # minlat = parameters.get('minlat')
    # maxlon = parameters.get('maxlon')
    # maxlat = parameters.get('maxlat')
    # wkt = parameters.get('wkt')
    # max_clouds = parameters.get('max_clouds')

    for date in dates:
        import urllib.request, urllib.parse, urllib.error
        # &lat=43.5&lon=12.25&datemin=2019-08-01&datemax=2019-09-01
        #template_filled = 'products/query?wkt=' + str(wkt).encode() + '&max_clouds=' + str(max_clouds) + '&start=' + str(date.date()) + '&stop=' + str(frequency.next_date(date).date())  # + '&format=' + format + '&user=' + username + '&pwd=' + password
        template_object = {'wkt': str(wkt), 'max_clouds': str(max_clouds), 'start':str(date.date()), 'stop':str(frequency.next_date(date).date()), 'product_type':product_type }
        template_filled = 'products/query?'+ urllib.parse.urlencode(template_object)
        list_download_links.append(template_filled)

    return list_download_links


def get_jeodpp_jobs(base_url, usr_pwd, https_params=''):
    # url and job
    get_jobs_url = base_url + '/jobs'
    response = http_request_jeodpp(get_jobs_url, userpwd=usr_pwd,  https_params=https_params)

    return True

def get_jeodpp_job_status(base_url, job_id, usr_pwd, https_params=''):

    status = False

    # To check if the user and password is not defined and throw error
    if usr_pwd is ':' or usr_pwd is None:
        logger.warning('User and password is not defined to query the JEODPP server')
        return status

    job_url = base_url + '/jobs/'+job_id
    response = http_request_jeodpp(job_url, userpwd=usr_pwd, https_params=https_params)
    # {
    #     "job_id": 4,
    #     "job_status": "created",
    #     "product_id": "S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004",
    #     "job_data": {
    #         "band": "B01"
    #     },
    #     "created_at": "2019-09-27T12:29:42.971725",
    #     "url": "/downloads/e05b9b021d9c103b/L2A_T34SFF_20150825T091006_B01_60m.jp2"
    # }
    if response.get('job_status') == 'created':
        status = True

    return status

# def create_jeodpp_job(base_url, product_id, usr_pwd):
#     # url and job
#     bands= ['B01','B02','B03']
#     created_job_list = []
#     for band in bands:
#         #"https://jeodpp.jrc.ec.europa.eu/services/gmes-dev/jobs/?product_id=S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004&band=B01"
#         job_url = base_url+'/jobs/?product_id='+product_id+'&band='+band
#         response = http_post_request_jeodpp(job_url, userpwd=usr_pwd)
# #         response = {"status": "created",
# #                       "job_id": 5,
# #                       "url": "/downloads/5a824f633be103ba/L2A_T34SFF_20150825T091006_B01_60m.jp2"   }
#         if response.get('status') == "created":
#             job_id = response.get('job_id')
#             download_url = response.get('url')
#             created_job_list.append(str(product_id)+':'+str(job_id)+':'+str(download_url))
#             # created_job_list.append(job_id + os.path.sep + download_url)
#
#     return created_job_list

def create_jeodpp_job(base_url, product_id, band, usr_pwd, https_params=''):
    created_job_link = None

    # To check if the user and password is not defined and throw error
    if usr_pwd is ':' or usr_pwd is None:
        logger.warning('User and password is not defined to query the JEODPP server')
        return created_job_link
    #"https://jeodpp.jrc.ec.europa.eu/services/gmes-dev/jobs/?product_id=S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004&band=B01"
    job_url = base_url+'/jobs/?product_id='+product_id+'&band='+band
    response = http_post_request_jeodpp(job_url, userpwd=usr_pwd, https_params=https_params)
    # response = {"status": "created",
    #               "job_id": 5,
    #               "url": "/downloads/5a824f633be103ba/L2A_T34SFF_20150825T091006_B01_60m.jp2"   }
    if response.get('status') == "created":
        job_id = response.get('job_id')
        download_url = response.get('url')
        created_job_link = str(product_id)+':'+str(band)+':'+str(job_id)+':'+str(download_url)

    return created_job_link


def delete_results_jeodpp_job(base_url, job_id, usr_pwd, https_params=''):
    # url and job
    success = False
    # To check if the user and password is not defined and throw error
    if usr_pwd is ':' or usr_pwd is None:
        logger.warning('User and password is not defined to query the JEODPP server')
        return success

    job_url = base_url + '/jobs/'+str(job_id)
    response = http_delete_request_jeodpp(job_url, userpwd=usr_pwd, https_params=https_params)
    if str(response) == 'data deleted':
        success = True
    return success

def cancel_jeodpp_job(base_url, job_id, usr_pwd):
    # url and job
    job_url = base_url + '/job/'+job_id+'/cancel'
    response = http_request_jeodpp(job_url, userpwd=usr_pwd, put=True)
    return True

def http_request_jeodpp(remote_url_file, userpwd='', https_params='', post=False, delete=False, put=False):
    c = pycurl.Curl()

    try:
        data = BytesIO()
        remote_url_file = remote_url_file.replace('\\','') #Pierluigi

        c.setopt(c.URL,remote_url_file)
        c.setopt(c.WRITEFUNCTION,data.write)

        if post:
            c.setopt(pycurl.POST, 1)
        if delete:
            c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        if put:
            c.setopt(pycurl.CUSTOMREQUEST, "PUT")

        if userpwd is not ':':
            c.setopt(c.USERPWD,userpwd)
            https_params = "Authorization: Basic "+base64.b64encode(userpwd)
        if remote_url_file.startswith('https'):
            c.setopt(c.CAINFO, certifi.where()) #Pierluigi
            if https_params is not '':
            #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
                c.setopt(pycurl.HTTPHEADER, [https_params])
        # if userpwd is not ':':
        #     c.setopt(c.USERPWD,userpwd)
        c.perform()

        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if c.getinfo(pycurl.HTTP_CODE) >= 400:

            raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
        # See ES2-67
        elif c.getinfo(pycurl.HTTP_CODE) == 301:

            raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
        else:
            list_dict = json.loads(data.getvalue())
            return list_dict
    except:
        logger.warning('Error in HTTP Request of JEODPP: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
        return 1
    finally:
        c = None


def http_post_request_jeodpp(remote_url_file, userpwd='', https_params=''):
    try:

        remote_url_file = remote_url_file.replace('\\','') #Pierluigi

        if userpwd is not ':':
            https_params = "Basic "+base64.b64encode(userpwd)

        # Adding empty header as parameters are being sent in payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": str(https_params) #"Basic dmVua2F2aTpORVZaOW4zWERIU1hrRHpv"
        }

        r = requests.post(url=remote_url_file, headers=headers )
        # print (r.content)

        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if r.status_code >= 400:
            raise Exception('HTTP Error in downloading the file: %i' %r.status_code)
        # See ES2-67
        elif r.status_code == 301:
            raise Exception('File moved permanently: %i' % r.status_code)
        else:
            list_dict = json.loads(r.content)
            return list_dict
    except:
        logger.warning('Error in HTTP POST Request of JEODPP: %s - error : %i' %(remote_url_file,r.status_code))
        return 1
    finally:
        r = None

def http_delete_request_jeodpp(remote_url_file, userpwd='', https_params=''):

    try:

        remote_url_file = remote_url_file.replace('\\','') #Pierluigi

        if userpwd is not ':':
            https_params = "Basic "+base64.b64encode(userpwd)

        # Adding empty header as parameters are being sent in payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": str(https_params) #"Basic dmVua2F2aTpORVZaOW4zWERIU1hrRHpv"
        }

        r = requests.delete(url=remote_url_file, headers=headers )
        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if r.status_code >= 400:
            raise Exception('HTTP Error in downloading the file: %i' %r.status_code)
        # See ES2-67
        elif r.status_code == 301:
            raise Exception('File moved permanently: %i' % r.status_code)
        else:
            list_dict = json.loads(r.content)
            return list_dict
    except:
        logger.warning('Error in HTTP DELETE Request of JEODPP: %s - error : %i' %(remote_url_file,r.status_code))
        return 1
    finally:
        r = None

#Returns the product Id from the ongoing and processed list
def get_product_id_from_list(list):
    product_id_list = []
    for item in list:
        product_id = item.split(':')[0]
        product_id_list.append(product_id)
    return  product_id_list

#Returns the product Id and Band from the ongoing and processed list
def get_product_id_band_from_list(list):
    product_id_band_list = []
    for item in list:
        product_id = item.split(':')[0]
        product_band = item.split(':')[1]
        product_id_band_list.append(product_id+':'+product_band)
    return  product_id_band_list

#Not used
def get_job_id_from_list(list):
    job_id_list = []
    for item in list:
        job_id = item.split(':')[1]
        job_id_list.append(job_id)
    return job_id_list

#Not used
def get_download_url_from_list(ongoing_job_id, list):
    download_url = None
    for item in list:
        job_id = item.split(':')[1]
        if job_id == ongoing_job_id:
            download_url = item.split(':')[2]
        # download_url_list.append(download_url)
    return download_url

#Download file loops over the download url to download the data and zip it along with the metadata file
def download_file(remote_url, target_dir, product_id=None, userpwd='', https_params='', download_urls=[]):
    try:
        download_result = False
        tmpdir_root = tempfile.mkdtemp(prefix=__name__, dir=es_constants.es2globals['base_tmp_dir'])
        tmpdir = tmpdir_root+ os.sep+product_id
        # os.mkdir(tmpdir)

        if not os.path.exists(tmpdir):
            # ES2-284 fix
            # path = os.path.join(tmpdir, untar_file)
            if os.path.isdir(tmpdir_root):
                os.makedirs(tmpdir)
            else:
                return False

        target_fullpath_zip = tmpdir_root + os.sep + product_id+'.zip'
        target_final = target_dir + os.sep + product_id+'.zip'

        listtozip = []
        for download_url in download_urls:
            remote_url_file = remote_url+ os.sep + download_url
            target_fullpath = tmpdir + os.sep + download_url.split('/')[-1]

            downloaded = get_jeodpp_file_from_url(remote_url_file, target_fullpath, userpwd=userpwd, https_params=https_params)
            if downloaded:
                listtozip.append(target_fullpath)

        # Download metadata file
        metadata_url = remote_url+os.sep+'products'+os.sep+product_id+os.sep+'mtd'
        metadata_file = tmpdir+os.sep+'MTD_MSIL1C.xml'
        download_urls.append(metadata_url)

        metadata_download = get_jeodpp_file_from_url(metadata_url, metadata_file, userpwd=userpwd, https_params=https_params)
        if metadata_download:
            listtozip.append(metadata_file)

        if len(listtozip) == len(download_urls):
            # Make Zip
            shutil.make_archive(tmpdir_root + os.sep + product_id, 'zip', tmpdir)

            if not os.path.exists(target_fullpath_zip):
                return False
            shutil.move(target_fullpath_zip, target_final)
            download_result = True

        return download_result

    except:
        logger.warning('Download files failed')
        return False
    finally:
        # c = None
        shutil.rmtree(tmpdir_root)


def get_jeodpp_file_from_url(remote_url_file, target_fullpath,  userpwd='', https_params=''):
    c = pycurl.Curl()
    try:
        outputfile = open(target_fullpath, 'wb')
        logger.debug('Output File: ' + target_fullpath)
        remote_url_file = remote_url_file.replace('\\', '')  # Pierluigi
        c.setopt(c.URL, remote_url_file)
        c.setopt(c.WRITEFUNCTION, outputfile.write)
        if userpwd is not ':':
            c.setopt(c.USERPWD,userpwd)
            https_params = "Authorization: Basic "+base64.b64encode(userpwd)
        if remote_url_file.startswith('https'):
            c.setopt(c.CAINFO, certifi.where())  # Pierluigi
            if https_params is not '':
                # headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
                c.setopt(pycurl.HTTPHEADER, [https_params])
        # if userpwd is not ':':
        #     c.setopt(c.USERPWD, userpwd)
        c.perform()
        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if c.getinfo(pycurl.HTTP_CODE) >= 400:
            outputfile.close()
            os.remove(target_fullpath)
            raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
        # See ES2-67
        elif c.getinfo(pycurl.HTTP_CODE) == 301:
            outputfile.close()
            os.remove(target_fullpath)
            raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
        else:
            outputfile.close()
            # listtozip.append(target_fullpath)
            # shutil.move(target_fullpath, target_final)
            return True
    except:
        logger.warning('Output NOT downloaded: %s - error : %i' % (remote_url_file, c.getinfo(pycurl.HTTP_CODE)))
        return False
    finally:
        c = None


######################################################################################
#   get_json_from_url
#   Purpose: download and save locally a file
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2019/09/13
#   Inputs: remote_url_file: full file path
#           target_file: target file name (by default 'test_output_file')
#           target_dir: target directory (by default a tmp dir is created)
#   Output: full pathname is returned (or positive number for error)
#
def get_json_from_url(remote_url_file, userpwd='', https_params=''):

    c = pycurl.Curl()

    try:
        data = BytesIO()

        # import cStringIO
        # data = cStringIO.StringIO()

        remote_url_file = remote_url_file.replace('\\','') #Pierluigi

        c.setopt(c.URL,remote_url_file)
        c.setopt(c.WRITEFUNCTION,data.write)

        if userpwd is not ':':
            c.setopt(c.USERPWD,userpwd)
            https_params = "Authorization: Basic "+base64.b64encode(userpwd)

        if remote_url_file.startswith('https'):
            c.setopt(c.CAINFO, certifi.where()) #Pierluigi
            if https_params is not '':
            #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
                c.setopt(pycurl.HTTPHEADER, [https_params])
        # if userpwd is not ':':
        #     c.setopt(c.USERPWD,userpwd)
        c.perform()

        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if c.getinfo(pycurl.HTTP_CODE) >= 400:

            raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
        # See ES2-67
        elif c.getinfo(pycurl.HTTP_CODE) == 301:

            raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
        else:
            list_dict = json.loads(data.getvalue())

            return list_dict
    except:
        logger.warning('Error in creating list from JEODPP server: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
        return 1
    finally:
        c = None
        # shutil.rmtree(tmpdir)