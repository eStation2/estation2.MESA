#
#	purpose: To implement CDS API in climate station
#	author:  Vijay Charan
#	date:	 03.2020
#   descr:


import requests
import json
import os
import pycurl
import certifi
import base64
from lib.python import es_logging as log
from io import BytesIO
logger = log.my_logger(__name__)

######################################################################################
#   Purpose: Get list of resources available
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of resources
#   Output type: Python Dict
def get_resources_list(base_url, usr_pwd, https_params):

    get_jobs_url = base_url + '/resources'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get datasets list of CDS
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of resources - datasets alone
#   Output type: Python Dict
def get_resources_datasets(base_url, usr_pwd, https_params):

    get_jobs_url = base_url + '/resources/datasets'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get Application list of CDS
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of resources - application alone
#   Output type: Python Dict
def get_resources_applications(base_url, usr_pwd, https_params):

    get_jobs_url = base_url + '/resources/applications'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get resource information
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           resourcename_uuid: UUID or resource id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: Resource detail
#   Output type: Python Dict
def get_resource_details(base_url, resourcename_uuid, usr_pwd, https_params):

    get_jobs_url = base_url + '/resources/'+ resourcename_uuid
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get resource availablity information
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           resourcename_uuid: UUID or resource id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: Availability of the resource
#   Output type: Boolean
def get_resource_availablity(base_url, resourcename_uuid, usr_pwd, https_params):

    get_jobs_url = base_url + '/resources/'+ resourcename_uuid+ '/availability'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response.get('available')

######################################################################################
#   Purpose: Create request to download any dataset using the parameters (variable)
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           resourcename_uuid: UUID or resource id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#           parameters: list of variables to query the dataset for download
#   Output: Request id
#   Output type: string
def post_request_resource(base_url, resourcename_uuid, usr_pwd, https_params, parameters):

    # parameters = template #json.loads(template)
    # format = parameters.get('format')
    # variable = parameters.get('variable')
    # year = parameters.get('year')
    # day = parameters.get('day')
    # time = parameters.get('time')
    # month = parameters.get('month')
    # url and job
    remote_url = base_url + '/resources/'+ resourcename_uuid
    # {'format': 'netcdf', 'variable': ['lake_mix_layer_temperature', 'skin_temperature',  ], 'year': [ '2018', '2019',],  'day': '01', 'time': '00:00'    }
    # template_object = {'format': str(format), 'variable': variable, 'year': year, 'month': month,'day': day, 'time': time}
    # response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    response = http_post_request_cds(remote_url, userpwd=usr_pwd, https_params=https_params, data=parameters)
    return response.get('request_id')

######################################################################################
#   Purpose: Get task information
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           request_id: request id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: status and location to download the file
#   Output type: Boolean , string
def get_task_details(base_url, request_id, usr_pwd, https_params):
    # url and job
    get_jobs_url = base_url + '/tasks/' + request_id
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    status = response.get('state')
    if str(status) == 'completed':
        download_location = str(response.get('location'))
    return status

######################################################################################
#   Purpose: Get task list of specific user
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of task
#   Output type: Python Dict
def get_tasks_list(base_url,  usr_pwd, https_params):

    get_jobs_url = base_url + '/tasks'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Delete specific task
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           task_id: Task it
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output:
#   Output type: Boolean
def delete_cds_task(base_url, task_id, usr_pwd, https_params=''):
    # url and job
    success = False
    # To check if the user and password is not defined and throw error
    if usr_pwd is ':' or usr_pwd is None:
        logger.warning('User and password is not defined to query the JEODPP server')
        return success

    job_url = base_url + '/tasks/'+str(task_id)
    response = http_delete_request_cds(job_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Download file and send the response
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: download_url: download url
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#           target_path: Target path to download
#   Output: Success result
#   Output type: Boolean
def get_file(download_url, usr_pwd, https_params, target_path):

    response = get_cds_file_from_url(download_url, target_fullpath=target_path, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get Terms and condition license list of CDS
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of Terms and condition
#   Output type: Python Dict
def get_termsConditions_list(base_url, usr_pwd, https_params):

    get_jobs_url = base_url + '/terms/list'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Get user specific Terms and condition license list
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: List of user specific Terms and condition
#   Output type: Python Dict
def get_user_termsConditions_list(base_url, usr_pwd, https_params):

    get_jobs_url = base_url + '/users/me/terms-and-conditions'
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    return response

######################################################################################
#   Purpose: Accept Terms and condition license list
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           terms_list: List of Terms and condition to be accepted
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output:
#   Output type: Boolean
def accept_termsConditions_list(base_url, terms_list, usr_pwd, https_params):

    remote_url = base_url + '/users/me/terms-and-conditions'
    response = http_post_request_cds(remote_url, userpwd=usr_pwd, https_params=https_params, data=terms_list)
    return response


######################################################################################
#   Purpose: http post request specific to CDS
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: remote_url_file: remote url
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#           data: Data to pass
#   Output: Success if http code is 202
#   Output type: dict or boolean
def http_post_request_cds(remote_url_file, userpwd='', https_params='', data=None):
    try:

        remote_url_file = remote_url_file.replace('\\','') #Pierluigi

        if userpwd is not None:
            https_params = "Basic "+base64.b64encode(userpwd)

        # Adding empty header as parameters are being sent in payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": str(https_params) #"Basic dmVua2F2aTpORVZaOW4zWERIU1hrRHpv"
        }
        # data={'format': 'netcdf', 'variable': ['lake_mix_layer_temperature', 'skin_temperature',  ], 'year': [ '2018', '2019',],  'day': '01', 'time': '00:00'}
        r = requests.post(url=remote_url_file, headers=headers, data=json.dumps(data) )
        # print(r.content)

        # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
        if r.status_code >= 400:
            raise Exception('HTTP Error in downloading the file: %i' %r.status_code)
        # See ES2-67
        elif r.status_code == 301:
            raise Exception('File moved permanently: %i' % r.status_code)
        elif r.status_code == 202:
            return True
        else:
            list_dict = json.loads(r.content)
            return list_dict
    except:
        logger.warning('Error in HTTP POST Request of CDS: %s - error : %i' %(remote_url_file,r.status_code))
        return 1
    finally:
        r = None

######################################################################################
#   Purpose: http request specific to CDS Pycurl
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: remote_url_file: remote url
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: depending on the request
#   Output type: dict
def http_request_cds(remote_url_file, userpwd='', https_params='', post=False, delete=False, put=False):
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

        if userpwd is not None:
            c.setopt(c.USERPWD,userpwd)
            https_params = "Authorization: Basic "+base64.b64encode(userpwd)
        if remote_url_file.startswith('https'):
            c.setopt(c.CAINFO, certifi.where()) #Pierluigi
            if https_params is not None:
            #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
                c.setopt(pycurl.HTTPHEADER, [https_params])
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
        logger.warning('Error in HTTP Request of CDS API: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
        return 1
    finally:
        c = None

######################################################################################
#   Purpose: Get cds file from the url passed
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: remote_url_file: remote url
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#           target_fullpath: Target full path
#   Output:
#   Output type: Boolean
def get_cds_file_from_url(remote_url_file, target_fullpath, userpwd='', https_params=''):
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
#   Purpose: http Delete request specific to CDS
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: remote_url_file: remote url
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#           data: Data to pass
#   Output: Success if http code is 204
#   Output type:  boolean
def http_delete_request_cds(remote_url_file, userpwd='', https_params=''):

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
        elif r.status_code == 204:
            return True
        else:
            # list_dict = json.loads(r.content)
            logger.warning('Task deletion : %s - error : %i' % (remote_url_file, r.status_code))
    except:
        logger.warning('Error in HTTP DELETE Request of JEODPP: %s - error : %i' %(remote_url_file,r.status_code))
        return 1
    finally:
        r = None

##################
#####OLD##########
##################
# def cancel_jeodpp_job(base_url, job_id, usr_pwd):
#     # url and job
#     job_url = base_url + '/job/'+job_id+'/cancel'
#     response = http_request_cds(job_url, userpwd=usr_pwd, put=True)
#     return True
#
# def get_download_links(dates, wkt,max_clouds, frequency, product_type):
#
#     list_download_links = []
#     # parameters = json.loads(template)
#     # minlon = parameters.get('minlon')
#     # minlat = parameters.get('minlat')
#     # maxlon = parameters.get('maxlon')
#     # maxlat = parameters.get('maxlat')
#     # wkt = parameters.get('wkt')
#     # max_clouds = parameters.get('max_clouds')
#
#     for date in dates:
#         import urllib
#         # &lat=43.5&lon=12.25&datemin=2019-08-01&datemax=2019-09-01
#         #template_filled = 'products/query?wkt=' + str(wkt).encode() + '&max_clouds=' + str(max_clouds) + '&start=' + str(date.date()) + '&stop=' + str(frequency.next_date(date).date())  # + '&format=' + format + '&user=' + username + '&pwd=' + password
#         template_object = {'wkt': str(wkt), 'max_clouds': str(max_clouds), 'start':str(date.date()), 'stop':str(frequency.next_date(date).date()), 'product_type':product_type }
#         template_filled = 'products/query?'+ urllib.urlencode(template_object)
#         list_download_links.append(template_filled)
#
#     return list_download_links
#
#
# def generate_list_products(dates, template, frequency, base_url, usr_pwd):
#
#     list_product_id_band = []
#     # To check if the user and password is not defined and throw error
#     if usr_pwd is ':' or usr_pwd is None:
#         logger.warning('User and password is not defined to query the JEODPP server')
#         return list_product_id_band
#
#     #Get the parameters from the template
#     parameters = json.loads(template)
#     bands = parameters.get('band')
#     minlon = parameters.get('minlon')
#     minlat = parameters.get('minlat')
#     maxlon = parameters.get('maxlon')
#     product_type = parameters.get('product_type')
#     maxlat = parameters.get('maxlat')
#     upper_left_coord = minlon+' '+maxlat
#     upper_right_coord = maxlon+' '+maxlat
#     lower_right_coord = maxlon+' '+minlat
#     lower_left_coord = minlon+' '+minlat
#     wkt = 'POLYGON(('+upper_left_coord+','+upper_right_coord+','+lower_right_coord+','+lower_left_coord+','+upper_left_coord+'))'   #POLYGON((36.11 -8.92,36.45 -8.92,36.45 -9.15,36.11 -9.15,36.11 -8.92))
#     max_clouds = parameters.get('max_clouds')
#
#     download_links = get_download_links(dates,wkt,max_clouds,frequency,product_type)
#     for download_link in download_links:
#         result = get_json_from_url(str(base_url + os.path.sep + download_link), userpwd=str(usr_pwd), https_params='')
#         if result is not 1:
#             for each_dict in result:
#                 # {"acquisitionStartTime": "2018-04-01T09:05:51.026Z",
#                 #     "cloudCoverPercentage": "17.290071",
#                 #     "crs": "EPSG:32634",
#                 #     "productType": "S2MSI2A",
#                 #     "uuid": "b0f00735-d493-4295-8140-38ea0ae270f4",
#                 #     "id": "S2A_MSIL2A_20180401T090551_N0207_R050_T34SFF_20180401T111317"
#                 # }
#                 product_id = each_dict.get("id")
#                 # id = each_dict.get("id")
#                 # productType = each_dict.get("productType")
#                 # cloudCoverPercentage = each_dict.get("cloudCoverPercentage")
#                 # if cloudCoverPercentage > X:
#                 #     list_product_id_band.append(product_id)
#                 for band in str(bands).split(','):
#                     list_product_id_band.append(product_id+':'+band)
#
#     return list_product_id_band
#
#
# def get_download_links(dates, wkt,max_clouds, frequency, product_type):
#
#     list_download_links = []
#     # parameters = json.loads(template)
#     # minlon = parameters.get('minlon')
#     # minlat = parameters.get('minlat')
#     # maxlon = parameters.get('maxlon')
#     # maxlat = parameters.get('maxlat')
#     # wkt = parameters.get('wkt')
#     # max_clouds = parameters.get('max_clouds')
#
#     for date in dates:
#         import urllib
#         # &lat=43.5&lon=12.25&datemin=2019-08-01&datemax=2019-09-01
#         #template_filled = 'products/query?wkt=' + str(wkt).encode() + '&max_clouds=' + str(max_clouds) + '&start=' + str(date.date()) + '&stop=' + str(frequency.next_date(date).date())  # + '&format=' + format + '&user=' + username + '&pwd=' + password
#         template_object = {'wkt': str(wkt), 'max_clouds': str(max_clouds), 'start':str(date.date()), 'stop':str(frequency.next_date(date).date()), 'product_type':product_type }
#         template_filled = 'products/query?'+ urllib.urlencode(template_object)
#         list_download_links.append(template_filled)
#
#     return list_download_links
#
#
# def get_jeodpp_jobs(base_url, usr_pwd, https_params=''):
#     # url and job
#     get_jobs_url = base_url + '/jobs'
#     response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
#
#     return True
#
# def get_jeodpp_job_status(base_url, job_id, usr_pwd, https_params=''):
#
#     status = False
#
#     # To check if the user and password is not defined and throw error
#     if usr_pwd is ':' or usr_pwd is None:
#         logger.warning('User and password is not defined to query the JEODPP server')
#         return status
#
#     job_url = base_url + '/jobs/'+job_id
#     response = http_request_cds(job_url, userpwd=usr_pwd, https_params=https_params)
#     # {
#     #     "job_id": 4,
#     #     "job_status": "created",
#     #     "product_id": "S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004",
#     #     "job_data": {
#     #         "band": "B01"
#     #     },
#     #     "created_at": "2019-09-27T12:29:42.971725",
#     #     "url": "/downloads/e05b9b021d9c103b/L2A_T34SFF_20150825T091006_B01_60m.jp2"
#     # }
#     if response.get('job_status') == 'created':
#         status = True
#
#     return status
#
# # def create_jeodpp_job(base_url, product_id, usr_pwd):
# #     # url and job
# #     bands= ['B01','B02','B03']
# #     created_job_list = []
# #     for band in bands:
# #         #"https://jeodpp.jrc.ec.europa.eu/services/gmes-dev/jobs/?product_id=S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004&band=B01"
# #         job_url = base_url+'/jobs/?product_id='+product_id+'&band='+band
# #         response = http_post_request_jeodpp(job_url, userpwd=usr_pwd)
# # #         response = {"status": "created",
# # #                       "job_id": 5,
# # #                       "url": "/downloads/5a824f633be103ba/L2A_T34SFF_20150825T091006_B01_60m.jp2"   }
# #         if response.get('status') == "created":
# #             job_id = response.get('job_id')
# #             download_url = response.get('url')
# #             created_job_list.append(str(product_id)+':'+str(job_id)+':'+str(download_url))
# #             # created_job_list.append(job_id + os.path.sep + download_url)
# #
# #     return created_job_list
#
# def create_jeodpp_job(base_url, product_id, band, usr_pwd, https_params=''):
#     created_job_link = None
#
#     # To check if the user and password is not defined and throw error
#     if usr_pwd is ':' or usr_pwd is None:
#         logger.warning('User and password is not defined to query the JEODPP server')
#         return created_job_link
#     #"https://jeodpp.jrc.ec.europa.eu/services/gmes-dev/jobs/?product_id=S2A_MSIL2A_20150825T091006_N0204_R050_T34SFF_20150825T091004&band=B01"
#     job_url = base_url+'/jobs/?product_id='+product_id+'&band='+band
#     response = http_post_request_cds(job_url, userpwd=usr_pwd, https_params=https_params)
#     # response = {"status": "created",
#     #               "job_id": 5,
#     #               "url": "/downloads/5a824f633be103ba/L2A_T34SFF_20150825T091006_B01_60m.jp2"   }
#     if response.get('status') == "created":
#         job_id = response.get('job_id')
#         download_url = response.get('url')
#         created_job_link = str(product_id)+':'+str(band)+':'+str(job_id)+':'+str(download_url)
#
#     return created_job_link
#
#
#
#
# #Returns the product Id from the ongoing and processed list
# def get_product_id_from_list(list):
#     product_id_list = []
#     for item in list:
#         product_id = item.split(':')[0]
#         product_id_list.append(product_id)
#     return  product_id_list
#
# #Returns the product Id and Band from the ongoing and processed list
# def get_product_id_band_from_list(list):
#     product_id_band_list = []
#     for item in list:
#         product_id = item.split(':')[0]
#         product_band = item.split(':')[1]
#         product_id_band_list.append(product_id+':'+product_band)
#     return  product_id_band_list
#
# #Not used
# def get_job_id_from_list(list):
#     job_id_list = []
#     for item in list:
#         job_id = item.split(':')[1]
#         job_id_list.append(job_id)
#     return job_id_list
#
# #Not used
# def get_download_url_from_list(ongoing_job_id, list):
#     download_url = None
#     for item in list:
#         job_id = item.split(':')[1]
#         if job_id == ongoing_job_id:
#             download_url = item.split(':')[2]
#         # download_url_list.append(download_url)
#     return download_url
#
# #Download file loops over the download url to download the data and zip it along with the metadata file
# def download_file(remote_url, target_dir, product_id=None, userpwd='', https_params='', download_urls=[]):
#     try:
#         download_result = False
#         tmpdir_root = tempfile.mkdtemp(prefix=__name__, dir=es_constants.es2globals['base_tmp_dir'])
#         tmpdir = tmpdir_root+ os.sep+product_id
#         # os.mkdir(tmpdir)
#
#         if not os.path.exists(tmpdir):
#             # ES2-284 fix
#             # path = os.path.join(tmpdir, untar_file)
#             if os.path.isdir(tmpdir_root):
#                 os.makedirs(tmpdir)
#             else:
#                 return False
#
#         target_fullpath_zip = tmpdir_root + os.sep + product_id+'.zip'
#         target_final = target_dir + os.sep + product_id+'.zip'
#
#         listtozip = []
#         for download_url in download_urls:
#             remote_url_file = remote_url+ os.sep + download_url
#             target_fullpath = tmpdir + os.sep + download_url.split('/')[-1]
#
#             downloaded = get_cds_file_from_url(remote_url_file, target_fullpath, userpwd=userpwd, https_params=https_params)
#             if downloaded:
#                 listtozip.append(target_fullpath)
#
#         # Download metadata file
#         metadata_url = remote_url+os.sep+'products'+os.sep+product_id+os.sep+'mtd'
#         metadata_file = tmpdir+os.sep+'MTD_MSIL1C.xml'
#         download_urls.append(metadata_url)
#
#         metadata_download = get_cds_file_from_url(metadata_url, metadata_file, userpwd=userpwd, https_params=https_params)
#         if metadata_download:
#             listtozip.append(metadata_file)
#
#         if len(listtozip) == len(download_urls):
#             # Make Zip
#             shutil.make_archive(tmpdir_root + os.sep + product_id, 'zip', tmpdir)
#
#             if not os.path.exists(target_fullpath_zip):
#                 return False
#             shutil.move(target_fullpath_zip, target_final)
#             download_result = True
#
#         return download_result
#
#     except:
#         logger.warning('Download files failed')
#         return False
#     finally:
#         # c = None
#         shutil.rmtree(tmpdir_root)
#
#
# ######################################################################################
# #   get_json_from_url
# #   Purpose: download and save locally a file
# #   Author: Vijay Charan, JRC, European Commission
# #   Date: 2019/09/13
# #   Inputs: remote_url_file: full file path
# #           target_file: target file name (by default 'test_output_file')
# #           target_dir: target directory (by default a tmp dir is created)
# #   Output: full pathname is returned (or positive number for error)
# #
# def get_json_from_url(remote_url_file, userpwd='', https_params=''):
#
#     c = pycurl.Curl()
#
#     try:
#         data = BytesIO()
#
#         # import cStringIO
#         # data = cStringIO.StringIO()
#
#         remote_url_file = remote_url_file.replace('\\','') #Pierluigi
#
#         c.setopt(c.URL,remote_url_file)
#         c.setopt(c.WRITEFUNCTION,data.write)
#
#         if userpwd is not ':':
#             c.setopt(c.USERPWD,userpwd)
#             https_params = "Authorization: Basic "+base64.b64encode(userpwd)
#
#         if remote_url_file.startswith('https'):
#             c.setopt(c.CAINFO, certifi.where()) #Pierluigi
#             if https_params is not '':
#             #headers = 'Authorization: Bearer ACB5F378-5483-11E9-849E-54E83FFDBADB'
#                 c.setopt(pycurl.HTTPHEADER, [https_params])
#         # if userpwd is not ':':
#         #     c.setopt(c.USERPWD,userpwd)
#         c.perform()
#
#         # Check the result (filter server/client errors http://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
#         if c.getinfo(pycurl.HTTP_CODE) >= 400:
#
#             raise Exception('HTTP Error in downloading the file: %i' % c.getinfo(pycurl.HTTP_CODE))
#         # See ES2-67
#         elif c.getinfo(pycurl.HTTP_CODE) == 301:
#
#             raise Exception('File moved permanently: %i' % c.getinfo(pycurl.HTTP_CODE))
#         else:
#             list_dict = json.loads(data.getvalue())
#
#             return list_dict
#     except:
#         logger.warning('Error in creating list from JEODPP server: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
#         return 1
#     finally:
#         c = None
        # shutil.rmtree(tmpdir)