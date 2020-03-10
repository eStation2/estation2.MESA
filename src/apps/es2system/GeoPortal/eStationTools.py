#!/usr/bin/env python
# -*- coding: utf8 -*-

# Methods for naming geoserver objects

# Translation table to assign a different LayerName (e.g. for SADC).
# Entry is 'product'_'subproduct'
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.utils import old_div
import os
import xml.etree.cElementTree as ET
from database import querydb
from lib.python import functions
from apps.es2system.GeoPortal import geoserverREST
import subprocess
import pipes
from lib.python import es_logging as log

TranslateLayerNames = False
tempDir='/tmp/eStation2/tempStationTools/'

translator = {
    'vgt-ndvi_vci' : {'category':'AMESD_SADC', 'region':'SAfri', 'version':'v2', 'product':'VCI_______', 'stringType':0},
    'fewsnet-rfe_10davg':{'category':'AMESD_SADC', 'region':'SAfri', 'version':'2.0', 'product':'LtavgRFE__', 'stringType':0},
    'tamsat-rfe_10d':{'category':'AMESD_SADC', 'region':'SAfri', 'version':'2.0', 'product':'LtavgRFE__', 'stringType':0}}

logger = log.my_logger(__name__)


def fnameTranslator(product, subproduct, date):
    key = '{0}_{1}'.format(product, subproduct)
    tr = translator[ key ]
    if tr['stringType'] == 0:
        outname = '{0}_{1}_{2}_{3}_{4}.tif'.format( tr['category'], tr['product'], date, tr['region'], tr['version'])
    else:
        outname = None
    return outname

# 	Name of the workspace
def setWorkspaceName(service, product, subproduct, version, mapset, nameType='full'):

    nameType = nameType.lower().replace('_','')

    wrkList = {"full":'{0}_{1}_{2}_{3}_{4}'.format(service, product, subproduct, mapset, version.replace('.', '_')),
               "serviceproductsubproduct":'{0}_{1}_{2}'.format(service, product, subproduct),
               "service":service,
               "product":product,
               "serviceproduct":"{0}_{1}".format(service, product),
               "productsubproduct":'{0}_{1}'.format(product, subproduct),
               "productsubproductmapset":'{0}_{1}_{2}'.format(product, subproduct, mapset),
               "productsubproductmapsetversion":'{0}_{1}_{2}_{3}'.format(product, subproduct, mapset, version.replace('.','_'))
               }

    if nameType in list(wrkList.keys()):
        return wrkList[nameType]
    else:
        return wrkList["full"]

# 	Name of the coverage
def setCoverageName(date, product, subproduct, version, mapset):

    coverageName = '{0}_{1}_{2}_{3}_{4}'.format(date, product, subproduct, mapset, version.replace('.', '_'))
    return coverageName

# 	Name of the layer
def setLayerName(date, product, subproduct, translate=False):

    if translate:
        layerName = fnameTranslator(product, subproduct, date)
    else:
        layerName = '{0}_{1}_{2}'.format(date, product, subproduct)

    return layerName

# 	Name of the style associated to prod-version-subproduct
def setStyleName(product, version, subproduct):

    style_name = '{0}_{1}_{2}'.format(product, version, subproduct).replace('.','_')
    return style_name

# 	Name of the .sld file associated to prod-version-subproduct on the local machine
def setStyleFilename(product, version, subproduct):

    style_name = setStyleName(product,version,subproduct)
    return '{0}/{1}.sld'.format(tempDir, style_name)

#	Directory containing raster files on geoserver machine
def setFileDir(dataRoot, product, subproduct, version, mapset, productType):

    subdir = functions.set_path_sub_directory(product,subproduct,productType,version,mapset)
    fileDir = '{0}/{1}'.format(dataRoot, subdir)
    return fileDir

#	Name of the raster file on geoserver machine
def setFileName(date, product, subproduct, mapset, version):

    fileName = '{0}_{1}_{2}_{3}_{4}.tif'.format(date, product, subproduct, mapset, version)
    return fileName

# Get the default (or only) legend for a product/subproduct, and write to an .sld file (for geoserver)
def createSLD(product, version, subproduct, output_file=None):

    if output_file is None:
        output_file = '{0}/{1}_{2}_{3}.sld'.format(tempDir, product,version,subproduct)

    # make sure /data/temp exists
    # Note 1: see http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
    # Note 2: /data/temp should be a variable
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    product_legends = querydb.get_product_legends(productcode=product,
                                                  subproductcode=subproduct,
                                                  version=version)

    # Get scale factor
    product_info = querydb.get_product_out_info(productcode=product,subproductcode=subproduct,version=version)
    scale_factor = product_info[0].scale_factor

    if hasattr(product_legends, "__len__") and product_legends.__len__() > 0:

        for legend in product_legends:

            # Changes for ES2-85
            legend_dict = legend
            defaultlegend = legend_dict['default_legend']

            # Changes for ES2-85
            # if default_legend == 'True':
            #     defaultlegend = True
            # else:
            #     defaultlegend = False

            # if there is only 1 legend defined, this is the default legend (even if not defined as default legend).
            if product_legends.__len__() == 1:
                defaultlegend = True

            if defaultlegend:
                legend_id = legend_dict['legend_id']
                legend_steps = querydb.get_legend_steps(legendid=legend_id)
                legend_name = legend_dict['legend_name']

    else:
        logger.warning('Error: no legend exists for this product. Exit')
        return 1

    num_steps = len(legend_steps)

    # Read the schema from the template
    tree = ET.ElementTree(file=geoserverREST.templ_sld)

    # Modify the schema for that Legend
    # Modify Layer Name
    for child in tree.getiterator():
        if child.tag == 'NamedLayer':
            child.set("Name", product)

    # Modify User Style Title
    for child in tree.getiterator():
        if child.tag == 'UserStyle':
            child.set("Title",legend_name)

    # Modify the Steps (and remove remaining ones)
    for child in tree.getiterator():
        if child.tag == 'ColorMap':
            ColorMap = child
            num_CME = len(ColorMap)

            # Check there are enough CME for this legend
            if num_steps > num_CME:
                logger.error('Too many legend steps [>255]. Exit')
                return 1

            for istep in range(0, num_steps):

                step = legend_steps[istep]
                # Build the RGB color
                color_rgb = step.color_rgb.split(' ')
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = rgb2html(color_rgb)

                to_value = old_div(step.to_step, scale_factor)

                # Modify steps
                ColorMap[istep].set('quantity',str(to_value))
                ColorMap[istep].set('color',color_html)

            for istep in range(num_steps, num_CME):
                del ColorMap[num_steps]

    tree.write(output_file)

    return output_file

# Register a raster in geoserver, and manage the style as well
def registerRaster(service, product, subproduct, version, mapset, date, productType, dataRoot):

    workspace = setWorkspaceName(service, product, subproduct, version, mapset, nameType=geoserverREST.geoserverWorkspaceName)
    coverage = setCoverageName(date, product, subproduct, version, mapset)
    fileDir = setFileDir(dataRoot, product, subproduct, version, mapset, productType)
    fileName = setFileName(date, product, subproduct, mapset, version)
    layerName = setLayerName(date, product, subproduct, translate=TranslateLayerNames)
    sld_name = setStyleName(product, version, subproduct)
    sld_file_name = setStyleFilename(product, version, subproduct)

    filepath = '{0}/{1}'.format(fileDir, fileName)
    rasterExists = geoserverREST.isRaster(workspace, coverage)

    if not rasterExists:

        # Check if the style is defined on geoserver
        style_defined = geoserverREST.isStyle(sld_name)

        if not style_defined:
            # Create locally the SLD file
            sld=0
            sld = createSLD(product, version, subproduct, output_file=sld_file_name)

            # Upload to geoserver the style
            if sld==0:
                resultSLD = geoserverREST.createStyle(sld_name, sld_file_name)
            else:
                logger.warning('CreateSLD failed for prod/subprod/version {0}/{1}/{2}. Exit'.format(product,subproduct,version))

        # Register the Raster and assign the default style
        geoserverREST.registerRaster(workspace, coverage, filepath, layerName, sld_name)

# Returns True if the file exists
def existsRemote(host, path, user=None):

    """Test if a file exists at path on a host accessible with SSH."""
    if user is not None:
        my_host = '{0}@{1}'.format(user,host)
    else:
        my_host = host

    try:
        if geoserverREST.sshKeyAgentParam == '':
            status = subprocess.call(
                ['ssh', my_host, 'test -f {}'.format(pipes.quote(path))])
        else:
            status = subprocess.call(
                 [geoserverREST.sshKeyAgentParam,'ssh', my_host, 'test', '-f', pipes.quote(path)], shell=True)

    except:
        logger.debug('SSH command failed')
        return False
    else:
        # MC outtext=['file not found','file exists']
        outtext=['file exists','file not found']
        print ('status={}, {}'.format(status, outtext[status]))

    return not(status)

# Returns True in case of error
def uploadRemote(host, local_path, target_path, user=None):

    if user is not None:
        #my_host = '{0}@{1}'.format(user, host)
        my_host = '{0}@{1}'.format(user,host)#VO edit to restLogin
    else:
        my_host = host

    # Create remote subdir
    subdir = os.path.dirname(target_path)
    try:
        if geoserverREST.sshKeyAgentParam == '':
            thisCommand='{0} ssh {1} mkdir -p {2}'.format(geoserverREST.sshKeyAgentParam, my_host, subdir)#VO
            status = subprocess.call(thisCommand, shell=True)
        else:
            status = subprocess.call(
                [geoserverREST.sshKeyAgentParam,'ssh', my_host, 'mkdir -p {0}'.format(subdir)], shell=True)
    except:
        logger.error('UploadRemote SSH command failed to create remote dir. Exit')
        return False

    # Upload file to remote server
    try:
        if geoserverREST.sshKeyAgentParam == '':
            thisCommand='{0} scp {1} {2}:{3}'.format(geoserverREST.sshKeyAgentParam, local_path, my_host,target_path)#VO
            status = subprocess.call(thisCommand, shell=True)
        else:
            status = subprocess.call(
                        [geoserverREST.sshKeyAgentParam,'scp', local_path, '{0}:{1}'.format(my_host,target_path)])
    except:
        logger.error('UploadRemote SSH command failed to copy data. Exit')
        return True
    return False

# For a raster, ensure it is uploaded and registered
def uploadAndRegisterRaster(service, product, subproduct, version, mapset, date, productType, dataRoot):

    status = False
    workspace = setWorkspaceName(service, product, subproduct, version, mapset, nameType=geoserverREST.geoserverWorkspaceName)
    coverage = setCoverageName(date, product, subproduct, version, mapset)
    localFileDir = setFileDir(dataRoot, product, subproduct, version, mapset, productType)
    remoteFileDir = setFileDir(geoserverREST.restBaseDir, product, subproduct, version, mapset, productType)
    fileName = setFileName(date, product, subproduct, mapset, version)
    layerName = setLayerName(date, product, subproduct, translate=TranslateLayerNames)
    sld_name = setStyleName(product, version, subproduct)
    sld_file_name = setStyleFilename(product, version, subproduct)

    localFilepath = '{0}/{1}'.format(localFileDir, fileName)
    remoteFilepath = '{0}/{1}'.format(remoteFileDir, fileName)

    # Check if the style exists, otherwise create it
    if not geoserverREST.isStyle(sld_name):
        name = createSLD(product,version,subproduct,output_file=sld_file_name)
        try:
            thisReturned = geoserverREST.createStyle(sld_name,sld_file_name)
        except:
            logger.error('UploadAndRegisterRaster failed to call geoserverREST.createStyle. Exit')
            return False

    # Check if file is registered
    #if not geoserverREST.isRaster(workspace,layerName):
    if not geoserverREST.isRaster(workspace, coverage):
        # Ensure file is uploaded
        if not existsRemote(geoserverREST.restHost,remoteFilepath, user=geoserverREST.sshUser):                         # Here, and below - we should act as sshUser - see ES2-72
            if uploadRemote(geoserverREST.restHost, localFilepath, remoteFilepath, user=geoserverREST.sshUser):         # the previously done changes by VO are rolled-back

        # if not existsRemote(geoserverREST.restHost,remoteFilepath, user=geoserverREST.restLogin):                     #VO changed sshUser to restLogin -> wrong (see above)
            # if uploadRemote(geoserverREST.restHost, localFilepath, remoteFilepath, user=geoserverREST.restLogin):     #VO changed sshUser to restLogin so that it is mesa@197.254.113.174 and not adminuser@197.254.113.117
                logger.error('Cannot upload file {0}.'.format(localFilepath))
                status = True
            else:
                logger.debug('File {0} copied to remote server'.format(localFilepath))

        # Ensure file is registered registerRaster(workspace, coverageName, filepath, layerName, SLD=None)
        if geoserverREST.registerRaster(workspace, coverage, remoteFilepath, layerName, SLD=sld_name):
            logger.error('Cannot register file {0}.'.format(localFilepath))
            status = True
        else:
            logger.info('File {0} uploaded to remote server'.format(localFilepath))

    return status

def rgb2html(rgb):
    r = int(rgb[0])
    g = int(rgb[1])
    b = int(rgb[2])

    r = 0 if r < 0 else 255 if r > 255 else r
    r = "%x" % r

    g = 0 if g < 0 else 255 if g > 255 else g
    g = "%x" % g

    b = 0 if b < 0 else 255 if b > 255 else b
    b = "%x" % b

    color = '00' if len(r) < 2 else '' + r
    color += '00' if len(g) < 2 else '' + g
    color += '00' if len(b) < 2 else '' + b

    return '#'+color


import sys, traceback
from sqlalchemy.orm import aliased
from database import connectdb

db = connectdb.ConnectDB().db

def get_activated_geoserver():
    global db
    try:
        session = db.session
        geoserver = aliased(db.geoserver)

        # The columns on the subquery "processinput" are accessible through an attribute called "c"
        # e.g. es.c.productcode
        active_geoserver = session.query(geoserver.geoserver_id,
                                                 geoserver.productcode,
                                                 geoserver.subproductcode,
                                                 geoserver.version,
                                                 geoserver.defined_by,
                                                 geoserver.activated,
                                                 geoserver.startdate,
                                                 geoserver.enddate).\
            filter(geoserver.activated == True).all()

        return active_geoserver

    except:
        exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
        # Exit the script and print an error telling what happened.
        logger.error("get_activated_geoserver: Database query error!\n -> {}".format(exceptionvalue))
    finally:
        if db.session:
            db.session.close()
