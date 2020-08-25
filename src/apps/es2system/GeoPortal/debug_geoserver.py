from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
standard_library.install_aliases()
__author__ = 'adminuser'

from unittest import TestCase

import os
from apps.es2system.GeoPortal import geoserverREST
from apps.es2system.GeoPortal import eStationTools as esTool
from apps.es2system.GeoPortal import system_geoserver as sysGeo
from database import querydb

from lib.python import es_logging as log

TranslateLayerNames = False
# MC: 19/07/2016
dataRoot = '/data/processing/'

case='fewsnet'
case='tamsat'
case='vgt-ndvi'
case='vgt-dmp'
case='modis-firms'
case='modis-chla'

if case == 'fewsnet':
    #service = 'precipitation'  # 'drought' #'agriculture'
    service = 'rainfall'
    product = 'fewsnet-rfe'
    subproduct = '1moncum'
    productType = 'Derived'
    mapset = 'FEWSNET-Africa-8km'
    version = '2.0'
    date = '20150311'

elif case == 'tamsat':

    service = 'rainfall'  # 'drought' #'agriculture'
    product='tamsat-rfe'
    subproduct='10d'
    productType = 'Ingest'
    mapset='TAMSAT-Africa-4km'
    version = '2.0'
    date = '20150101'

elif case == 'vgt-ndvi':

    service = 'vegetation'  # 'drought' #'agriculture'
    product='vgt-ndvi'
    subproduct='ndv'
    productType = 'Ingest'
    mapset='SPOTV-IGAD-1km'
    version = 'sv2-pv2.1'
    date = '20150111'

elif case == 'vgt-dmp':

    service = 'vegetation'  # 'drought' #'agriculture'
    product='vgt-dmp'
    subproduct='dmp'
    productType = 'Ingest'
    mapset='SPOTV-Africa-1km'
    version = 'V1.0'
    date = '20140801'

elif case == 'modis-firms':

    service = 'fire'  # 'drought' #'agriculture'
    product='modis-firms'
    subproduct='10dcount'
    productType = 'Derived'
    mapset='SPOTV-Africa-1km'
    version = 'v5.0'
    date = '20160701'

elif case == 'modis-chla':

    service = 'oceanography'  # 'drought' #'agriculture'
    product='modis-chla'
    subproduct='monavg'
    productType = 'Derived'
    mapset='MODIS-Africa-4km'
    version = 'v2013.1'
    date = '20160701'


logger = log.my_logger(__name__)

sld_name = esTool.setStyleName(product,version,subproduct)
sld_file_name = esTool.setStyleFilename(product,version,subproduct)
workSpace = esTool.setWorkspaceName(service,product,subproduct,version,mapset,nameType=geoserverREST.geoserverWorkspaceName)

# ----------------------------------------------------
#   geoserverREST.py
# ----------------------------------------------------
class TestgeoserverREST(TestCase):

    # ----------------------------------------------------
    #   WorkSpaces
    # ----------------------------------------------------

    def test_ListWorkspaces(self):

        WorkSpaces=geoserverREST.listWorkspaces()
        print ('List of workspaces')
        print (WorkSpaces)

    def TestIsWorkspace(self):

        result=geoserverREST.isWorkspace(workSpace)
        if result:
            print ('WorkSpace {0} exists.'.format(workSpace))
        else:
            print ('WorkSpace {0} does NOT exist.'.format(workSpace))

    def TestCreateWorkspaces(self):

        workspace = esTool.setWorkspaceName(service, product, subproduct, version, mapset,nameType=geoserverREST.geoserverWorkspaceName)

        print ('Creating workspace: {0}'.format(workSpace))

        if not geoserverREST.isWorkspace(workspace):
            print (geoserverREST.createWorkspace(workspace))
        else:
            print ('WS already exists')

    # ----------------------------------------------------
    #   Styles
    # ----------------------------------------------------

    def TestListStyles(self):
        Styles = geoserverREST.listStyles()
        print (Styles)

    def TestIsStyle(self):

        result = geoserverREST.isStyle(sld_name)

        if result:
            print ('Style {0} exists.'.format(sld_name))
        else:
            print ('Style {0} does NOT exist.'.format(sld_name))

    def TestCreateStyle(self):

        name = esTool.createSLD(product,version,subproduct,output_file=sld_file_name)
        print ('SLD name {}'.format(name))
        print ('sld_name {}'.format(sld_name))
        print ('sld_file_name {}'.format(sld_file_name))
        status = geoserverREST.createStyle(sld_name, sld_file_name)

    # ----------------------------------------------------
    #   Rasters
    # ----------------------------------------------------

    def TestIsRaster(self):
        layerName = esTool.setLayerName(date,product,subproduct,translate=False)
        thisResult = geoserverREST.isRaster(workSpace, layerName)
        print ('TestISRaster {} {}'.format(workSpace, layerName))
        print (thisResult)

    def TestRegisterRaster(self):
        esTool.registerRaster(service, product, subproduct, version, mapset, date, productType, geoserverREST.restBaseDir)

# ----------------------------------------------------
#   eStationTools.py
# ----------------------------------------------------

class TestEsTools(TestCase):

    def TestCreateSLD(self):

        sld_file = esTool.createSLD(product,version,subproduct)
        print ('Created .sld file is {0}'.format(sld_file))

    def TestExistRemote(self):

        fileDir = esTool.setFileDir(geoserverREST.restBaseDir, product,subproduct,version,mapset,productType)
        fileName = esTool.setFileName(date, product,subproduct,mapset,version)
        host = geoserverREST.restHost
        path = fileDir+fileName

        status = esTool.existsRemote(host, path, user=geoserverREST.sshUser)
        self.assertEqual(status,True)

    def TestUploadRemote(self):

        local_fileDir = esTool.setFileDir(dataRoot, product,subproduct,version,mapset,productType)
        remote_fileDir = esTool.setFileDir(geoserverREST.restBaseDir, product,subproduct,version,mapset,productType)
        fileName = esTool.setFileName(date, product,subproduct,mapset,version)
        host = geoserverREST.restHost
        path = local_fileDir+os.path.sep+fileName

        status = esTool.uploadRemote(host, path, remote_fileDir, user=geoserverREST.sshUser)
        self.assertEqual(status,False)

    def TestUploadAndRegister(self):

        local_fileDir = esTool.setFileDir(dataRoot, product,subproduct,version,mapset,productType)
        remote_fileDir = esTool.setFileDir(geoserverREST.restBaseDir, product,subproduct,version,mapset,productType)
        fileName = esTool.setFileName(date, product,subproduct,mapset,version)
        host = geoserverREST.restHost
        path = local_fileDir+os.path.sep+fileName

        status=esTool.uploadAndRegisterRaster(service, product, subproduct, version, mapset, date, productType, dataRoot)

        self.assertEqual(status, False)


# ----------------------------------------------------
#   system_geoserver.py
# ----------------------------------------------------

class TestSystem(TestCase):

    # This function is obsolete (replaced by syncGeoserver)
    # def TestLftpMirror(self):
    #
    #     fileDir  = esTool.setFileDir('', product, subproduct, version, mapset, productType)
    #     lftp_mirror.lftp_mirror(fileDir, logger)


    def TestSyncGeoserver(self):

        sysGeo.syncGeoserver()



