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
def get_resources_list(base_url, usr_pwd=None, https_params=None):

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
def get_resource_details(base_url, resourcename_uuid, usr_pwd=None, https_params=None):

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
def get_resource_availablity(base_url, resourcename_uuid, usr_pwd=None, https_params=None):

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
def get_task_details(base_url, request_id, usr_pwd=None, https_params=None):
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
def get_tasks_list(base_url, usr_pwd=None, https_params=None):

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
def delete_cds_task(base_url, task_id, usr_pwd, https_params=None):
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
def get_termsConditions_list(base_url, usr_pwd=None, https_params=None):

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
            https_params = "Basic "+base64.b64encode(userpwd.encode()).decode()

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
        # elif r.status_code == 202:
        #     return True
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
            https_params = "Authorization: Basic "+base64.b64encode(userpwd.encode()).decode()
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
            https_params = "Authorization: Basic "+base64.b64encode(userpwd.encode()).decode()
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
            https_params = "Basic "+base64.b64encode(userpwd.encode()).decode()

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

def create_list_cds(dates, template, base_url):
    resources_parameters = json.loads(template)
    variable = resources_parameters.get('variable')
    resourcename_uuid = resources_parameters.get('resourcename_uuid')
    list_resource = []
    for date in dates:
        list_resource.append(date.strftime("%Y%m%d%H%M%S")+'_'+resourcename_uuid+'_'+variable)

    return list_resource
