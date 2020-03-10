from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define the get CODA EUM data routine
#	author:  Vijay Charan
#	date:	 06.2019
#   descr:	 Gets data from CODA EUM


from future import standard_library
standard_library.install_aliases()
import requests
# import pycurl

import json
import os
# import re
# from urlparse import urljoin
# import datetime
from lib.python import es_logging as log
from config import es_constants
logger = log.my_logger(__name__)

def generate_list_uuid(dates, template, base_url, username, password):

    coda_eum_dic = {
        'user': username,
        'pwd': password,
        'base_url': base_url,
        'out_path': es_constants.es2globals['base_tmp_dir']
    }

    list_download_links = []
    for single_date in dates:
        list_data_uuid = coda_getlists(single_date, coda_eum_dic, template)
        for uuid in list_data_uuid:
            list_download_links.append(uuid)
    return list_download_links


def coda_getlists(datetime_start=None, motu_client_dic='', template=''):
    #try:

    #if datetime_start is None:
    str_day = datetime_start.strftime("%Y-%m-%d")

    if motu_client_dic is not None:
        user = motu_client_dic.get('user')
        pwd = motu_client_dic.get('pwd')
        base_url = motu_client_dic.get('base_url')
        out_path = motu_client_dic.get('out_path')

    credential = (user, pwd)

    if template is not None:
        sentinelsat_obj = json.loads(template)
        platformname = sentinelsat_obj.get('platformname')
        producttype = sentinelsat_obj.get('producttype')
        timeliness = sentinelsat_obj.get('timeliness')
        instrumentshortname = sentinelsat_obj.get('instrumentshortname')
        productlevel = sentinelsat_obj.get('productlevel')

    try:
        resource = 'S3A* AND ( beginPosition:[{0}T03:00:00.000Z TO {0}T12:59:59.999Z] AND endPosition:[{0}T03:00:00.000Z TO {0}T12:59:59.999Z] ) AND   (platformname:{1} AND producttype:{2} AND timeliness:"{3}" AND instrumentshortname:{4} AND productlevel:{5})&offset=0&limit=25&sortedby=ingestiondate&order=asc'.format(str_day, platformname, producttype, timeliness,instrumentshortname, productlevel)
        requestURL = base_url+  resource.encode()
        headers = {'Content-type':'application/plain'}
        thisCoverage = requests.get(
            requestURL,
            headers=headers,
            auth=credential
            )
        thisCoverage.raise_for_status()
        list_of_dict = thisCoverage.json()

        list_links = []
        for each_dict in list_of_dict:
            link = each_dict.get("uuid")
            identifier = each_dict.get("identifier")
            list_links.append(link+os.path.sep +identifier)

        list_links

    except:
        print ('Error when creating uuid list')
        return True
    else:
        return list_links