from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
#
#	purpose: Define the get CMEMS data routine
#	author:  M.Clerici
#	date:	 08.10.2018
#   descr:	 Gets data from CMEMS
#	history: 2.0

# Import standard modules
# import pycurl
# import signal
# import StringIO
# import cStringIO
# import tempfile
from future import standard_library
standard_library.install_aliases()
import sys
import os
# import re
import datetime
#
# # Import eStation2 modules
from lib.python import es_logging as log
from config import es_constants
logger = log.my_logger(__name__)

# from database import querydb
from lib.python import functions
# from apps.productmanagement import datasets
# motu_path='more /var'


def motu_4_dates(dates, template, base_url, username, password, files_filter_expression):
    product_ID_star = files_filter_expression.replace("*", "")
    product_ID = product_ID_star.replace(".", "")
    motu_client_dic = {
        'motu_path': es_constants.es2globals['motu_path'],
        'user': username,
        'pwd': password,
        'mercator_motu_web': base_url,
        'lon_lat': '-x -35 -X 15 -y -10 -Y 30',
        'depth': '-z 0.494 -Z 0.4942',
        'out_path': es_constants.es2globals['base_tmp_dir'],
        'product_ID' : product_ID
    }

    list_motu_command = []
    for single_date in dates:
        motu_command = motu_getlists(single_date, motu_client_dic, template)
        list_motu_command.append(motu_command)

    return list_motu_command


def motu_getlists(datetime_start=None, motu_client_dic='', template=''):
    #try:

    if motu_client_dic is not None:
        motu_path = motu_client_dic.get('motu_path')
        user = motu_client_dic.get('user')
        pwd = motu_client_dic.get('pwd')
        mercator_motu_web = motu_client_dic.get('mercator_motu_web')
        out_path = motu_client_dic.get('out_path')
        product_ID = motu_client_dic.get('product_ID')

    #if template is not None:
        # service_ID = motu_product_dic.get('service_ID')
        # product_ID = motu_product_dic.get('product_ID')
        # lon_lat = motu_product_dic.get('lon_lat')
        # depth = motu_product_dic.get('depth')
        # variables = motu_product_dic.get('variables')
    #product_ID = 'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS'

    if datetime_start is None:
        # Forecasted date
        str_day = datetime.datetime.now() + datetime.timedelta(days=6)
        filename_date = str_day.strftime("%Y%m%d")
        str_day = str_day.strftime("%Y-%m-%d 12:00:00")
        out_filename = filename_date + '_' + product_ID + '.nc'
    else:
        str_day = datetime_start.strftime("%Y-%m-%d 12:00:00")
        filename_date = datetime_start.strftime("%Y%m%d")
        if product_ID == 'GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS' :
            str_day = datetime_start.strftime("%Y-%m-%d %H:%M:%S")
            filename_date = datetime_start.strftime("%Y%m%d%H%M%S")

        out_filename = filename_date + '_' + product_ID + '.nc'

    # python /home/webvenkavi/.local/lib/python2.7/site-packages/motu-client.py -u eeStation2 -p eStation2019! -m http://nrt.cmems-du.eu/motu-web/Motu -s GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS -d global-analysis-forecast-phy-001-024 -x -35 -X 15 -y -10 -Y 30 -t 2018-11-05 12:00:00 -T 2018-11-05 12:00:00 -z 0.494 -Z 0.4942 -v vo -v uo -v so -v zos -v thetao -o /data/processing/motu/ -f 20181105_global-analysis-forecast-phy-001-024.nc
    #command = 'python ' + motu_path + ' -u ' + user + ' -p ' + pwd + ' -m ' + mercator_motu_web + 's ' + service_ID + ' -d ' + product_ID + ' ' + lon_lat + ' -t ' + str_day + ' -T ' + str_day + ' ' + depth + ' ' + variables + ' -o ' + out_path + ' -f ' + out_filename

    # command = 'python ' + motu_path + ' --user ' + user + ' --pwd ' + pwd + ' --motu ' + mercator_motu_web + ' ' \
    #            + template + \
    #           ' --date-min "' + str_day + '" --date-max "' + str_day + \
    #           '" --out-dir ' + out_path + ' --out-name ' + out_filename
    command = motu_path + ' --user ' + user + ' --pwd ' + pwd + ' --motu ' + mercator_motu_web + ' ' \
               + template + \
              ' --date-min "' + str_day + '" --date-max "' + str_day + \
              '" --out-dir ' + out_path + ' --out-name ' + out_filename


    print (command)
    logger.info('Command is: ' + command)
    return command
    #os.system(command)

#except:
    #logger.error("Error in Motu-client")

    #return None


#motu_getlists(None, motu_client_dic, motu_product_dic)