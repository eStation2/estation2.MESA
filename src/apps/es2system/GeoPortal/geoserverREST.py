from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
__author__ = "Bruno Combal - MESA"
__license__ = "GNU General Public License version 3"
__date__ = "20 May 2016"
__version__ = "0.2"

import os, re, sys
import requests
import json
from urllib.parse import urljoin
# from html.parser import HTMLParser
# from lxml import etree
import logging

# Make functions silent
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# NOTE: this version is the "naive approach"
# next version should have a class to store the connection parameters (server, login, password)
# documentation: https://mesa-geoportals.slack.com/files/bruno.combal/F1A99U3PZ/Publishing_raster_in_geoserver

# session variables
with open('./geoportal.conf') as confFile:
    conf = json.load(confFile)

restLogin = str(conf["restLogin"])
restPassword = str(conf["restPassword"])
restHost = str(conf["restHost"])
restServer = 'http://{0}'.format(restHost)
restPort = str(conf["restPort"])
restBaseDir = str(conf["restBaseDir"])
#restURL='{0}:{1}/geoserver/rest/'.format(restServer, restPort)         # MUST end with '/' for urljoin to work
restURL='{0}/geoserver/rest/'.format(restServer)                        #edit by VO removed the ":" & restPort as running on terminal gives warning couldnot resolve 197.254.113.174:
restFormat={'text':'text', 'xml':'text/xml', 'json':'text/json'}

# MC 22.06.2016 -> add user of the geoserver machine
sshUser=str(conf["sshUser"])
sshKeyAgentParam=str(conf["sshKeyAgentParam"])
templ_sld='/var/www/eStation2/apps/es2system/GeoPortal/template_discrete_color.sld'
geoserverWorkspaceName = str(conf["geoserverWorkspaceName"])

# ----------------------------------------------------
#   WorkSpaces
# ----------------------------------------------------

# List workspaces
# M.C. The extra '/' does work with 'text' format only (not text/xlm nor text/json)
def listWorkspaces(format='text'):

    commandString = 'curl -s -u {0}:{1} -XGET -H "Accept: {3}" "{2}workspaces/"'.format(restLogin, restPassword, restURL, restFormat[format])
    response = os.popen(commandString).read()
    #
    # Parse the response and extract Workspace name
    these_regex = "<li><a[ ^>]*href=.*/workspaces.*>(.+?)</a>.*</li>"
    pattern = re.compile(these_regex)
    wsps = re.findall(pattern, response)
    return wsps

# Check if a workspace exists
# returns information on workspace "name" if it exists
# see https://gist.github.com/jgomo3/73f38cc5a91d85146ccf
def isWorkspace(name):

    credential=(restLogin, restPassword)
    resource = 'workspaces/{0}'.format(name)
    headers = {'Accept' : 'application/json'}
    request_url = urljoin(restURL, resource)
    try:
        r = requests.get(request_url,
                         headers=headers,
                         auth=credential)
    except:
        return False

    if r.status_code == requests.codes.ok:
        return True
    else:
        return False

# Creates a workspace
# to do: add a test of existence (do not create if already exist)
# curl -v -u admin:geoserver -XPOST -H "Content-type: text/xml" -d "<workspace><name>mylandsat</name></workspace>" http://localhost:8082/geoserver/rest/workspaces
def createWorkspace(name):
    resource = 'workspaces'
    requestUrl = urljoin(restURL, resource)
    commandString = 'curl -s -u {0}:{1} -XPOST -H "Content-type: text/xml" -d "<workspace><name>{3}</name></workspace>" "{2}" >/dev/null'.format(restLogin, restPassword, requestUrl, name)

    return os.popen(commandString).read()

# ----------------------------------------------------
#   Styles
# ----------------------------------------------------

# List Styles
# commandString = 'curl -v -u {0}:{1} -XGET -H "Accept: {3}" "{2}/workspaces/"'.format(restLogin, restPassword, restURL, restFormat[format])
def listStyles(format='text'):

    commandString = 'curl -s -u {0}:{1} -XGET -H "Accept: {3}" "{2}styles/"'.format(restLogin, restPassword, restURL, restFormat[format])
    response = os.popen(commandString).read()

    # Parse the response and extract Styles name
    these_regex = "<li><a[ ^>]*href=.*/styles.*>(.+?)</a>.*</li>"
    pattern = re.compile(these_regex)
    styles = re.findall(pattern, response)
    return styles

# Check if a Style exists
# returns information on workspace "name" if it exists
# see https://gist.github.com/jgomo3/73f38cc5a91d85146ccf
def isStyle(name):
    credential=(restLogin, restPassword)
    resource = 'styles/{0}'.format(name)
    headers = {'Accept' : 'application/json'}
    request_url = urljoin(restURL, resource)
    try:
        r = requests.get(request_url,headers=headers,auth=credential).raise_for_status()
    except:
        return False
    return True

# Creates a Style (called 'name') and upload the .sld 'file'
# Note: the .sld file is created with the eStationTools.createSLD() method
def createStyle(name, file):

    if not isStyle(name):
        credential = (restLogin, restPassword)

        # MC 22.06.2016 -> remove the subdir for ICPAC installation
        payload = '<style><name>{0}</name><filename>{1}</filename></style>'.format(name,os.path.basename(file))
        headers = {'content-type': 'text/xml'}
        resource = 'styles'
        request_url = urljoin(restURL, resource)
        sld = requests.post(
            request_url,
            data=payload,
            headers=headers,
            auth=credential
        )
        sld.raise_for_status()

        resource = 'styles/{0}'.format(name)
        headers = {'Content-type': 'application/vnd.ogc.sld+xml'}

        request_url = urljoin(restURL, resource)

        with open(file, 'rb') as f:

            r = requests.put(
                request_url,
                data=f,
                headers=headers,
                auth=credential
            )
        return r

# ----------------------------------------------------
#   Rasters
# ----------------------------------------------------

# check if a raster exists
def isRaster(workspace, coverage):
    credential = (restLogin, restPassword)
    resource = 'workspaces/{0}/coveragestores/{1}.json'.format(workspace, coverage)
    headers = {'Content-type' : 'application/json'}
    request_url = urljoin(restURL, resource)
    thisRaster = None
    print (request_url)
    try:
        thisRaster = requests.get(
            request_url,
            headers = headers,
            auth = credential
            )
    except:
        print ('geoserverREST:isRaster failed.')
        return False

    if thisRaster.status_code == requests.codes.ok:
        return True
    else:
        return False

    return True

# Register a raster
def registerRaster(workspace, coverageName, filepath, layerName, SLD=None):
    # assumes the raster file is already in the file system (filepath)
    # create a coverage named "coverageName"
    # link the real file "filepath" to the coverage
    # optionally change the SLD from default to the value set in input
    credential = (restLogin, restPassword)

    # CreateCoverageStore
    # curl -v -u admin:geoserver -XPOST -H "Content-type: application/xml" -d "<coverageStore><name>clip10</name><workspace>mylandsat</workspace><enabled>true</enabled></coverageStore>" http://localhost:8082/geoserver/rest/workspaces/mylandsat/coveragestores
    # resultCS = os.popen('curl -v -u {0}:{1} -XPOST -H "Content-type: application/xml" -d "{2}" {3}'.format(login, password, payload, requestURL) ).read()
    thisCoverage = None
    try:
        payload = '<coverageStore><name>{0}</name><workspace>{1}</workspace><enabled>true</enabled></coverageStore>'.format(coverageName, workspace)
        resource = 'workspaces/{0}/coveragestores'.format(workspace)
        requestURL = urljoin(restURL, resource)
        headers = {'Content-type':'application/xml'}
        thisCoverage = requests.post(
            requestURL,
            data=payload,
            headers=headers,
            auth=credential
            )
        thisCoverage.raise_for_status()

    except:
        print ('Error when creating coverage')
        return True
    else:
        pass

    # Link file to the coverage
    # curl -v -u admin:geoserver -XPUT -H "Content-type: text/plain" -d "file:/usr/local/lib/geoserver-2.8.2/data_dir/data/mylandsat/clip10.tif" http://localhost:8082/geoserver/rest/workspaces/mylandsat/coveragestores/clip10/external.geotiff?configure=first\&coverageName=clipten
    # resultLink = os.popen('curl -v -u {0}:{1} -XPUT -H "Content-type: text/plain" -d "file:{2}" "{3}/workspaces/{4}/coveragestore/{5}/external.geotiff?configure=first\&coverageName={5}" '.format(restLogin, restPassword, filepath, restURL, workspace, layerName))
    thisLink = None

    try:
        payload = 'file:{0}'.format(filepath)
        resource = 'workspaces/{0}/coveragestores/{1}/external.geotiff?configure=first&coverageName={2}'.format(workspace, coverageName, layerName)
        requestURL = urljoin(restURL, resource)
        headers = {'Content-type':'text/plain'}
        thisLink = requests.put(
            requestURL,
            data = payload,
            headers = headers,
            auth=credential
            )
        thisLink.raise_for_status()

    except:
        print ('Error when linking file to coverage. Remove Coverage store')
        # Remove the Coverage store
        commandString = 'curl -s -u {0}:{1} -X DELETE {2}workspaces/{3}/coveragestores/{4}.html'.format(restLogin, restPassword, restURL, workspace, coverageName)
        response = os.popen(commandString).read()
        return True
    else:
        pass

    # Change the default SLD (if passed as argument)
    # curl -v -u admin:geoserver -XPUT -H "Content-type: text/xml" -d "<layer><defaultStyle><name>rain</name></defaultStyle></layer>" http://localhost:8082/geoserver/rest/layers/clipten
    # resultSLD = os.popen( 'curl -v -u {0}:{1} -XPUT -H "Content-type: text/xml" -d '.format(login, password, ) )
    thisSLD = None
    if SLD is not None:
        payload = '<layer><defaultStyle><name>{0}</name></defaultStyle></layer>'.format(SLD)
        resource = 'layers/{0}'.format(layerName)
        requestURL = urljoin(restURL, resource)
        headers = {'Content-type':'text/xml'}
        thisSLD = requests.put(
            requestURL,
            data = payload,
            headers = headers,
            auth = credential
            )
        thisSLD.raise_for_status()

    return False    #(thisCoverage, thisLink, thisSLD)


# change the default SLD for a layer
def setDefaultStyle(layerName, SLD):
    credential = (restLogin, restPassword)
    thisSLD = None
    payload = '<layer><defaultStyle><name>{0}</name></defaultStyle></layer>'.format(SLD)
    resource = 'layers/{0}'.format(layerName)
    requestURL = urljoin(restURL, resource)
    headers = {'Content-type':'text/xml'}
    thisSLD = requests.put(
        requestURL,
        data = payload,
        headers = headers,
        auth = credential
        )
    thisSLD.raise_for_status()
    return thisSLD


if __name__ == "__main__":
    print ("This file is a library")
    print ("install it in your python library path, then use")
    print ("import geoserverREST")
    print ("in your python code")

    sys.exit(0)
