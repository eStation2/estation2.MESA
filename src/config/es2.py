#
#	purpose: Define variables common to the project (dirs, DB access, ..)
#	author:  M. Clerici
#	date:	 19.02.2014
#   descr:	 It is now a plain module in python (to be converted into other format ?)
#
#   TODO-M.C.: a script for creating the environment (e.g. dedicated dirs like /tmp/eStation/)
#
import os, sys

# Customize the path to eStation2 dirs
sys.path.append('/srv/www/eStation2/')
import locals

# Import eStation lib modules
from lib.python import es_logging as log
from lib.python.mapset import *

# Define eStation specific variables: directories
baseDir=os.environ['ESTATION2PATH']

# Application paths
installPath=baseDir
addonPath='/opt/facilities/Addon_PS'
binDir=installPath+'/bin/'
configDir=installPath+'/config/'
addonConfigDir=addonPath+'/config/'
addonBinDir=addonPath+'/bin/'
addonProcessingDir=addonPath+'/processing/'
scriptsDir=installPath+'/scripts/'
dataRoot=installPath+'/data/'
staticDataDir=installPath+'/data/static_data'
processingDir=installPath+'/processing'
logDir=installPath+'/log/'
wrkDir=installPath+'/wrkdir/'
testDataDirIn=baseDir+'/TestFiles/Inputs/'
testDataDirOut=baseDir+'/TestFiles/Outputs/'
testDataDirRef=baseDir+'/TestFiles/RefsOutput/'

#mpeEnviHeader=${staticDataDir}/processing/MPE_ENVI_Header.hdr
#MRT_HOME=/opt/extern/mrt
#PATH=$PATH:/opt/extern/mrt/bin
#MRTDATADIR=/opt/extern/mrt/data
#export MRT_HOME PATH MRTDATADIR
#ingestInDir=$(xml sel -t -v "//ingest_server_in" ${configDir}/ingest_repositories.xml)
#ingestOutDir=$(xml sel -t -v "//ingest_server_out" ${configDir}/ingest_repositories.xml)
#dataDir=ingestOutDir

#umask 0002
# Python libs paths
#export PYTHONPATH=/opt/extern/gdal/lib/python2.6/site-packages/:/opt/extern/gdal/lib/python2.6/site-packages/osgeo
#export LD_LIBRARY_PATH=/opt/extern/gdal/lib:/usr/share/szip-2.1/lib/usr/local/lib

# GDAL netcdf directory
#GDALncDir=/opt/extern/gdal_netcdf/bin/
# Additionnal processing generic product directories
#processing_dir="archive tif xml derived"

# Define eStation specific variables: database definition
#DB_HOST='localhost'
#DB_PASS='mesadmin'

DB_HOST='balthazar.jrc.it'
DB_PORT='5432'
DB_USER='estation'
DB_OWNER=DB_USER
DB_PASS='estation01'
#DB_PASS_MD5=$(echo ${db_pass} | tr -d [:punct:] | tr -d [:space:])
DB_DATABASE='estationdb'

# Define eStation specific variables: database schemas/tables
DB_SCHEMA_PRODUCTS='products'
DB_SCHEMA_ANALYSIS='analysis'
DB_SCHEMA_DATA='data'

prefix=DB_SCHEMA_PRODUCTS+'.'

DB_TABLE_PRODUCTS=prefix+'products_data'
DB_TABLE_PGROUP=prefix+'product_groups'
DB_TABLE_DESCRIPTION=prefix+'products_description'
DB_TABLE_LEGEND=prefix+'legend'
DB_TABLE_LEGENDSTEP=prefix+'legend_step'
DB_TABLE_I18N=prefix+'i18n'
DB_TABLE_PRODUCTLEGEND=prefix+'product_legend'
DB_TABLE_USERS=prefix+'users'
DB_TABLE_MAPLEGEND=prefix+'maplegend'
DB_TABLE_MAPLEGENDSTEP=prefix+'maplegendstep'
DB_TABLE_PORTFOLIO=prefix+'portfolio'
DB_TABLE_TSDATA=prefix+'timeseries_data'
DB_TABLE_TSDRAWPROP=prefix+'timeseries_user_drawproperties'
DB_TABLE_TSPROP=prefix+'timeseriesgroup_user_graphproperties'
DB_TABLE_TSGROUP=prefix+'timeseries_groups'
DB_TABLE_TS=prefix+'timeseries'
DB_TABLE_TSUNIQDATE=prefix+'timeseries_dates'
DB_TABLE_TSDECAD=prefix+'timeseries_decad'