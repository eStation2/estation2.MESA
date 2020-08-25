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
from datetime import datetime
from config import es_constants

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
    # url and job
    remote_url = base_url + '/resources/'+ resourcename_uuid
    # {'format': 'netcdf', 'variable': ['lake_mix_layer_temperature', 'skin_temperature',  ], 'year': [ '2018', '2019',],  'day': '01', 'time': '00:00'    }
    # template_object = {'format': str(format), 'variable': variable, 'year': year, 'month': month,'day': day, 'time': time}
    response = http_post_request_cds(remote_url, userpwd=usr_pwd, https_params=https_params, data=parameters)
    return response.get('request_id')

######################################################################################
#   Purpose: Get task status
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/03/04
#   Inputs: base_url: base url of the cds API
#           request_id: request id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: status
#   Output type: string
def get_task_status(base_url, request_id, usr_pwd=None, https_params=None):
    # url and job
    get_jobs_url = base_url + '/tasks/' + request_id
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    status = response.get('state')
    return str(status)


######################################################################################
#   Purpose: Get task information
#   Author: Vijay Charan, JRC, European Commission
#   Date: 2020/06/10
#   Inputs: base_url: base url of the cds API
#           request_id: request id
#           usr_pwd: User and password separated by ":" (eg user:password)
#           https_params: Additional Http parameters
#   Output: status and location to download the file
#   Output type: Boolean , string
def get_job_download_url(base_url, request_id, usr_pwd=None, https_params=None):
    # url and job
    download_url = False
    get_jobs_url = base_url + '/tasks/' + request_id
    response = http_request_cds(get_jobs_url, userpwd=usr_pwd, https_params=https_params)
    status = response.get('state')
    if str(status) == 'completed':
        download_url = str(response.get('location'))
    # elif str(status) == 'failed':
    #     download_url = str(status)
    # elif str(status) == 'queued':
    #     download_url = str(status)
    # else:
    #     download_url = str(status)
    return download_url

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
        logger.error('User and password is not defined to delete CDS task')
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
        logger.error('Error in HTTP POST Request of CDS: %s - error : %i' %(remote_url_file,r.status_code))
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
        logger.error('Error in HTTP Request of CDS API: %s - error : %i' %(remote_url_file,c.getinfo(pycurl.HTTP_CODE)))
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
        logger.error('Output NOT downloaded: %s - error : %i' % (remote_url_file, c.getinfo(pycurl.HTTP_CODE)))
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
            logger.error('Task deletion : %s - error : %i' % (remote_url_file, r.status_code))
    except:
        logger.error('Error in HTTP DELETE Request of CDS: %s - error : %i' %(remote_url_file,r.status_code))
        return 1
    finally:
        r = None

##############################
####### CDS WRAPPER ##########
##############################
# This method creates the basic resource name(id to differentiate products with different parameters)
def create_basic_resourcename_identifier(template, resourcename_identifier):
    if type(template) is dict:
        resources_parameters = template
    else:
        resources_parameters = json.loads(template)

    variable = resources_parameters.get('variable')
    if 'product_type' in resources_parameters:
        product_type = resources_parameters.get('product_type')
        resourcename_identifier = resourcename_identifier + '_' + product_type

    if 'pressure_level' in resources_parameters:
        pressure_level = resources_parameters.get('pressure_level')
        resourcename_identifier = resourcename_identifier + '_' + pressure_level

    if 'ensemble_member' in resources_parameters:
        ensemble_member = resources_parameters.get('ensemble_member')
        resourcename_identifier = resourcename_identifier + '_' + ensemble_member

    if 'experiment' in resources_parameters:
        experiment = resources_parameters.get('experiment')
        resourcename_identifier = resourcename_identifier + '_' + experiment

    if 'model' in resources_parameters:
        model = resources_parameters.get('model')
        resourcename_identifier = resourcename_identifier + '_' + model

    if 'area' in resources_parameters:
        area = resources_parameters.get('area')
        area_str = ''
        for ele in area:
            area_str += str(ele)
        resourcename_identifier = resourcename_identifier + '_' + str(area_str)

    return resourcename_identifier


def create_list_cds(dates, template, base_url, resourcename_uuid):

    #Check if template is dict or string them create resources_parameters
    if type(template) is dict:
        resources_parameters = template
    else:
        resources_parameters = json.loads(template)

    variable = resources_parameters.get('variable')

    resourcename_identifier = create_basic_resourcename_identifier(resources_parameters, resourcename_uuid)
    list_resource = []
    for date in dates:
        list_resource.append(date.strftime("%Y%m%d%H%M%S")+':'+resourcename_identifier+':'+variable)

    return list_resource

def create_list_cds_with_period(template, base_url, resourcename_uuid):

    list_resource = []
    period_list = []
    # Check if template is dict or string them create resources_parameters
    if type(template) is dict:
        resources_parameters = template
    else:
        resources_parameters = json.loads(template)

    variable = resources_parameters.get('variable')

    resourcename_identifier = create_basic_resourcename_identifier(resources_parameters, resourcename_uuid)

    if 'period' in resources_parameters:
        period = resources_parameters.get('period')
        if type(period) is list:
            period_list = period
        else:
            # convert string to list
            period_list.append(period)

    for date in period_list:
        list_resource.append(date+':'+resourcename_identifier+':'+variable)

    return list_resource

def create_cds_job(internet_source, usr_pwd, template, resourcename_uuid):
    # template =json.loads(template)
    request_id = post_request_resource(internet_source.url, resourcename_uuid, usr_pwd, internet_source.https_params, template)
    return request_id

#Currently current list is checked with ongoing and processed list
# TODO Check the list also in the file system
def check_processed_list(current_list, processed_list, ongoing_list, template_paramater):
    listtoprocessrequest = []

    for current_file in current_list:
        # Check if current list (file is already there in filesystem)
        file_location = get_cds_target_path(es_constants.ingest_dir, current_file, template_paramater)
        if os.path.exists(file_location):
            continue

        # Check if current list is not in processed list
        if len(processed_list) == 0 and len(ongoing_list) == 0:
            listtoprocessrequest.append(current_file)
        else:
            if current_file not in processed_list and current_file not in ongoing_list:
                # if current_file not in processed_list and current_file not in ongoing_product_band_list:
                listtoprocessrequest.append(current_file)

    return listtoprocessrequest

def build_cds_date_template(date_str, template):
    # resources_parameters = {"format": "netcdf", "product_type": "reanalysis",
    #     "variable": "sea_surface_temperature",
    #     "year": "2019","month": "01","day":"01","time": "12:00"}
    if type(template) is dict:
        resources_parameters = template
    else:
        resources_parameters = json.loads(template)

    if 'period' in template:
        final_template_object = template
    else:
        datetimeObj = datetime.strptime(date_str, "%Y%m%d%H%M%S")
        template["year"] = str(datetimeObj.year)
        template["month"] = str(datetimeObj.month)

        if 'day' in template:
            template["day"] = str(datetimeObj.day)
        if 'time' in template:
            template["time"] = datetimeObj.strftime("%H:%M")
        final_template_object = remove_resoucename(template)
    # if datetimeObj.second != "00":
    #     template["seconds"] = datetimeObj.seconds
    return final_template_object

#Returns the date, resourceid and variable from the ongoing and processed list
def get_cds_current_list_pattern(list):
    list_reduced = []
    for item in list:
        reduced = get_cds_current_Item_pattern(item)
        list_reduced.append(reduced)
    return  list_reduced

def get_cds_current_Item_pattern(item):
    datetime = item.split(':')[0]
    resource_id = item.split(':')[1]
    variable = item.split(':')[2]
    reduced_item = datetime+':'+resource_id+':'+variable
    return reduced_item

def get_cds_target_path(dir, cs_parameters, resources_parameters):
    # resources_parameters = {"format": "netcdf", "product_type": "reanalysis",
    #     "variable": "sea_surface_temperature"}
    datetime = cs_parameters.split(':')[0]
    resourcename_uuid = cs_parameters.split(':')[1]
    variable = cs_parameters.split(':')[2]
    filename = datetime + '_' + resourcename_uuid + '_' + variable

    if 'format' in resources_parameters:
        format = resources_parameters["format"]

    if format == "GRIB":
        filename += ".GRIB"
    elif format == "zip":
        filename += ".zip"
    elif format == "tgz":
        filename += ".tar.gz"
    else:
        filename += ".nc"
    target_path = os.path.join(dir, filename)
    return target_path

def remove_resoucename(dict):
    if 'resourcename_uuid' in dict:
        del dict['resourcename_uuid']

    return dict

def read_cds_parameter_file(internet_id):
    #Read the CDS parameters from the file.
    try:
        parameter_file = '/eStation2/get_lists/get_cds/' +internet_id.replace(":", "_")+'.txt'
        with open(parameter_file) as json_file:
            data = json.load(json_file)
    except:
        logger.error('Error in loading the CDS parameters from the file: %s ' %(parameter_file))
        return None
    return data


#####################################################################################
#   build_list_matching_files_cds
#   Purpose: return the list of file names matching a 'template' with 'date' placeholders
#            It is the entry point for the 'http_cds' source type
#   Author: VIJAY CHARAN VENKATACHALAM, JRC, European Commission
#   Date: 2020/06
#   Inputs: template: object with the needed parameters to fill the template get
#           from_date: start date for the dataset (datetime.datetime object)
#           to_date: end date for the dataset (datetime.datetime object)
#           frequency: dataset 'frequency' (see DB 'frequency' table)
#
def build_list_matching_files_cds_period(base_url, template, resourcename_uuid):
    list_input_files = []
    try:
        # if sys.platform == 'win32':
        #     template.replace("-", "#")

        # return lst
        list_input_files =  create_list_cds_with_period(template, base_url, resourcename_uuid)

    except Exception as inst:
        logger.debug("Error in frequency.get_internet_dates: %s" % inst.args[0])
        raise

    return list_input_files