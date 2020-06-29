#
#	purpose: Define all variables for es2
#	author:  M.Clerici & Jurriaan van 't Klooster
#	date:	 13.03.2014
#   descr:	 Define all variables for es2
#	history: 1.0
#
#   NOTE: all the definitions are going to be in es_constants.ini, that will contain two sections
#         Factory Settings : some of them are going to be written at the .deb package generation from iniEnv
#         User Settings: User can overwrite a sub-set of the Factory settings (not the 'internal' ones)
#         This module will:     1. Read both Factory/User Settings from .ini
#                               2. Manage priorities (User -> Factory)
#                               3. Make available the settings, part in es2globals, part
#
#   This module will be be imported by any other (instead of locals.py -> to be discontinued)
#
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library

import os
import sys
import configparser
from osgeo import gdalconst

#from lib.python import functions
# logger = log.my_logger(__name__)

standard_library.install_aliases()

# Set the mask for log files
os.umask(0000)

if sys.platform != 'win32':
    # system_settings = functions.getSystemSettings()
    # install_type = system_settings['type_installation'].lower()
    # if install_type == 'jeobatch':
    #     factory_settings_filename = 'factory_settings_jeobatch.ini'
    # elif install_type == 'jeodesk':
    #     factory_settings_filename = 'factory_settings_jeodesk.ini'
    # else:
    #     factory_settings_filename = 'factory_settings.ini'
    factory_settings_filename = 'factory_settings.ini'
else:
    factory_settings_filename = 'factory_settings_windows.ini'

thisfiledir = os.path.dirname(os.path.abspath(__file__))
config_factorysettings = configparser.ConfigParser()
config_factorysettings.read([os.path.join(thisfiledir, factory_settings_filename)])

base_local_dir = config_factorysettings.get('FACTORY_SETTINGS', 'base_local_dir')
# print 'base_local_dir: ' + base_local_dir

usersettingsfile = base_local_dir + '/settings/user_settings.ini'


# if sys.platform != 'win32':
#     usersettingsfile = '/eStation2/settings/user_settings.ini'
# else:
#     usersettingsfile = 'C:/eStation2/eStation2/settings/user_settings.ini'

if not os.path.isfile(usersettingsfile):
    usersettingsfile = os.path.join(thisfiledir, 'install/user_settings.ini')
    # ToDo: copy user_settings.ini from config dir to /eStation2/settings/ ???

config_usersettings = configparser.ConfigParser()
config_usersettings.read([usersettingsfile])

usersettings = config_usersettings.items('USER_SETTINGS')
for setting, value in usersettings:
    if value is not None and value != "":
        config_factorysettings.set('FACTORY_SETTINGS', setting, value)
    else:
        config_factorysettings.set('FACTORY_SETTINGS',
                                   setting,
                                   config_factorysettings.get('FACTORY_SETTINGS', setting))

es2globals = {}
factorysettings = config_factorysettings.items('FACTORY_SETTINGS')
for setting, value in factorysettings:
    es2globals[setting] = value
    locals()[setting] = value

# for setting in es2globals:
#    logger.info(setting + ': ' + str(es2globals[setting]))

# ---------------------------------------------------------------
# Various definitions
# ---------------------------------------------------------------
ES2_OUTFILE_FORMAT = 'GTiff'
ES2_OUTFILE_EXTENSION = '.tif'
ES2_OUTFILE_OPTIONS = 'COMPRESS=LZW'
ES2_OUTFILE_INTERP_METHOD = gdalconst.GRA_NearestNeighbour
