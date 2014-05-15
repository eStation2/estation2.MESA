#
#	purpose: Define all variables for es2 (previously iniEnv + iniEnv_db)
#	author:  M.Clerici
#	date:	 13.03.2014
#   descr:	 Define all variables for es2 (previously iniEnv + iniEnv_db)
#	history: 1.0
#
import os
from osgeo.gdalconst import *

# Define eStation specific variables: directories
base_dir = os.environ['ESTATION2PATH']

# Application paths
install_path = base_dir
addon_path = '/opt/facilities/Addon_PS'
bin_dir = install_path+'/bin/'
config_dir = install_path+'/config/'
addon_config_dir = addon_path+'/config/'
addon_bin_dir = addon_path+'/bin/'
addon_processing_dir = addon_path+'/processing/'
scripts_dir = install_path+'/scripts/'
data_root = install_path+'/data/'
static_data_dir = install_path+'/data/static_data'
processing_dir = install_path+'/processing'
log_dir = install_path+'/log/'
wrk_dir = install_path+'/wrk_dir/'
test_data_dir_in = base_dir+'/TestFiles/Inputs/'
test_data_dir_out = base_dir+'/TestFiles/Outputs/'
test_data_dir_ref = base_dir+'/TestFiles/RefsOutput/'
base_tmp_dir = os.path.sep+'tmp'+os.path.sep+'eStation2'+os.path.sep

eumetcast_files_dir = '/home/esuser/my_eumetcast_dir/'
ingest_server_in_dir = '/home/esuser/my_data_ingest_dir/'
processed_list_dir = base_tmp_dir + 'processed' +os.path.sep
get_eumetcast_processed_list = processed_list_dir + 'get_eum_processed_list'
poll_frequency = 2


#mpeEnviHeader = ${staticData_dir}/processing/MPE_ENVI_Header.hdr
#MRT_HOME = /opt/extern/mrt
#PATH = $PATH:/opt/extern/mrt/bin
#MRTDATA_dir = /opt/extern/mrt/data
#export MRT_HOME PATH MRTDATA_dir
#ingestIn_dir = $(xml sel -t -v "//ingest_server_in" ${config_dir}/ingest_repositories.xml)
#ingestOut_dir = $(xml sel -t -v "//ingest_server_out" ${config_dir}/ingest_repositories.xml)
#data_dir = ingestOut_dir

#umask 0002
# Python libs paths
#export PYTHONPATH = /opt/extern/gdal/lib/python2.6/site-packages/:/opt/extern/gdal/lib/python2.6/site-packages/osgeo
#export LD_LIBRARY_PATH = /opt/extern/gdal/lib:/usr/share/szip-2.1/lib/usr/local/lib

# GDAL netcdf _directory
#GDALnc_dir = /opt/extern/gdal_netcdf/bin/
# Additional processing generic product _directories
#processing__dir = "archive tif xml derived"

# Define eStation specific variables: database definition
#DB_HOST = 'localhost'
#DB_PASS = 'mesadmin'


DB_HOST = 'h05-dev-vm19'
DB_PORT = '5432'
DB_USER = 'estation'
DB_OWNER = DB_USER
DB_PASS = 'mesadmin'    # 'estation01'
#DB_PASS_MD5 = $(echo ${db_pass} | tr -d [:punct:] | tr -d [:space:])
DB_DATABASE = 'estationdb'

# Define eStation specific variables: database schemas/tables
DB_SCHEMA_PRODUCTS = 'products'
DB_SCHEMA_ANALYSIS = 'analysis'
DB_SCHEMA_DATA = 'data'

dbglobals = {
    'host': DB_HOST,
    'port': DB_PORT,
    'dbUser': DB_USER,
    'dbPass': DB_PASS,
    'dbName': DB_DATABASE,
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
ES2_OUTFILE_INTERP_METHOD = GRA_NearestNeighbour
