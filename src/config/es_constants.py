#
#	purpose: Define all variables for es2 (previously iniEnv + iniEnv_db)
#	author:  M.Clerici
#	date:	 13.03.2014
#   descr:	 Define all variables for es2 (previously iniEnv + iniEnv_db)
#	history: 1.0
#

import os
import locals
from osgeo import gdalconst

# Get base dir
try:
    base_dir = locals.es2globals['base_dir']
except EnvironmentError:
    print 'Error - base_dir not defined in locals.  Exit'
    exit(1)

try:
    data_dir = locals.es2globals['data_dir']
except EnvironmentError:
    print 'Error - data_dir not defined in locals.  Exit'
    exit(1)

# Software version
ES2_SW_VERSION = '2.0.0'

# Application paths
install_path = base_dir
apps_dir = install_path+'/apps/'
config_dir = install_path+'/config/'
processing_dir = apps_dir+'/processing'

log_dir = install_path+'/log/'
wrk_dir = install_path+'/wrk_dir/'
base_tmp_dir = os.path.sep+'tmp'+os.path.sep+'eStation2'+os.path.sep

# Data paths (temp)
eumetcast_files_dir = data_dir+'my_eumetcast_dir/'
ingest_server_in_dir = data_dir+'my_data_ingest_dir/'

processed_list_base_dir = base_tmp_dir + 'get_lists' +os.path.sep
processed_list_eum_dir = processed_list_base_dir+'get_eumetcast'+os.path.sep
processed_list_int_dir = processed_list_base_dir+'get_internet'+os.path.sep

get_eumetcast_processed_list_prefix = processed_list_eum_dir+'get_eum_processed_list_'
get_internet_processed_list_prefix = processed_list_int_dir + 'get_internet_processed_list_'

poll_frequency = 5

#umask 0002
# Python libs paths
#export PYTHONPATH = /opt/extern/gdal/lib/python2.6/site-packages/:/opt/extern/gdal/lib/python2.6/site-packages/osgeo
#export LD_LIBRARY_PATH = /opt/extern/gdal/lib:/usr/share/szip-2.1/lib/usr/local/lib

# GDAL netcdf _directory
#GDALnc_dir = /opt/extern/gdal_netcdf/bin/
# Additional processing generic product _directories
#processing__dir = "archive tif xml derived"

# Define eStation specific variables: database schemas/tables
DB_SCHEMA_PRODUCTS = 'products'
DB_SCHEMA_ANALYSIS = 'analysis'
DB_SCHEMA_DATA = 'data'

dbglobals = {
    'host': locals.es2globals['host'],
    'port': locals.es2globals['port'],
    'dbUser': locals.es2globals['dbUser'],
    'dbPass': locals.es2globals['dbPass'],
    'dbName': locals.es2globals['dbName'],
    'schema_products': DB_SCHEMA_PRODUCTS,
    'schema_analysis': DB_SCHEMA_ANALYSIS,
    'schema_data': DB_SCHEMA_DATA
}

prefix = DB_SCHEMA_PRODUCTS+'.'

DB_TABLE_PRODUCTS = prefix+'products_data'
DB_TABLE_PGROUP = prefix+'product_groups'
DB_TABLE_DESCRIPTION = prefix+'products_description'
DB_TABLE_LEGEND = prefix+'legend'
DB_TABLE_LEGENDSTEP = prefix+'legend_step'
DB_TABLE_I18N = prefix+'i18n'
DB_TABLE_PRODUCTLEGEND = prefix+'product_legend'
DB_TABLE_USERS = prefix+'users'
DB_TABLE_MAPLEGEND = prefix+'maplegend'
DB_TABLE_MAPLEGENDSTEP = prefix+'maplegendstep'
DB_TABLE_PORTFOLIO = prefix+'portfolio'
DB_TABLE_TSDATA = prefix+'timeseries_data'
DB_TABLE_TSDRAWPROP = prefix+'timeseries_user_drawproperties'
DB_TABLE_TSPROP = prefix+'timeseriesgroup_user_graphproperties'
DB_TABLE_TSGROUP = prefix+'timeseries_groups'
DB_TABLE_TS = prefix+'timeseries'
DB_TABLE_TSUNIQDATE = prefix+'timeseries_dates'
DB_TABLE_TSDECAD = prefix+'timeseries_decad'

# Various definitions
ES2_OUTFILE_FORMAT = 'GTiff'
ES2_OUTFILE_OPTIONS = 'COMPRESS=LZW'
ES2_OUTFILE_INTERP_METHOD = gdalconst.GRA_NearestNeighbour
