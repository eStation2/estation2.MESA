#
#	purpose: Define the get my ocean routine
#	author:  M.Clerici
#	date:	 19.02.2014
#   descr:	 Gets data from myocean
#	history: 1.0

# Import standard modules
# import pycurl
# import signal
# import StringIO
# import cStringIO
# import tempfile
import sys
import os
# import re
import datetime
#
# # Import eStation2 modules
from lib.python import es_logging as log
from config import es_constants
# from database import querydb
from lib.python import functions
# from apps.productmanagement import datasets
motu_path='/usr/local/lib/python2.7/dist-packages/motu-client-python/motu-client.py'
logger = log.my_logger(__name__)

# Date definition
sixthday=datetime.datetime.now() + datetime.timedelta(days=6)
str_day=sixthday.strftime("%Y-%m-%d 12:00:00")
filename_date=sixthday.strftime("%Y%m%d")

logger.info('I am executing now the script')
# Variable definition for Motu-client
user = 'bfoli'
pwd = 'He0feYqn'
mercator_motu_web = 'http://atoll.mercator-ocean.fr/mfcglo-mercator-gateway-servlet/Motu'
service_ID = 'http://purl.org/myocean/ontology/service/database#GLOBAL_ANALYSIS_FORECAST_PHYS_001_002-TDS'
product_ID = 'global-analysis-forecast-phys-001-002'
lon_lat = '-x -30 -X 15 -y -5 -Y 20'
depth = '-z 0.494 -Z 109.7294'
variables = '-v v -v u -v salinity -v ssh -v temperature'
out_path = '/data/myocean/forecast'
out_filename = filename_date+'_global-analysis-forecast-physics-001-002.nc'

command='python '+motu_path+' -u '+user+' -p '+pwd+' -m '+mercator_motu_web+ \
        ' -s '+service_ID+' -d '+product_ID+' '+lon_lat+ \
        ' -t '+str_day+' -T '+str_day+' '+depth+' '+variables+ \
        ' -o '+out_path+' -f '+out_filename

print(command)
logger.info('Command is: '+command)

#os.system(command)
