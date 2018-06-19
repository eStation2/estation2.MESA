#!/usr/bin/python

#if __name__ == '__main__' and __package__ is None:
#    from os import sys, path
#    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import sys
import os

os.umask(0000)

cur_dir = os.path.dirname(__file__)
if cur_dir not in sys.path:
    sys.path.append(cur_dir)

# import web
import datetime
import json
import glob
# import time
import calendar
import numpy as NP

from config import es_constants
from database import querydb
from database import crud

# from apps.acquisition import get_eumetcast
# from apps.acquisition import acquisition
# from apps.processing import processing      # Comment in WINDOWS version!
from apps.productmanagement.datasets import Dataset
# from apps.es2system import es2system
# from apps.productmanagement.datasets import Frequency
from apps.productmanagement.products import Product
from apps.analysis import generateLegendHTML
from apps.analysis.getTimeseries import (getTimeseries, getFilesList)
# from multiprocessing import (Process, Queue)

from lib.python import functions
from lib.python import es_logging as log

logger = log.my_logger(__name__)


WEBPY_COOKIE_NAME = "webpy_session_id"


def getWorkspaceMaps(workspaceid):
    wsmaps = querydb.get_workspace_maps(workspaceid)
    maps = []
    if hasattr(wsmaps, "__len__") and wsmaps.__len__() > 0:
        for row_dict in wsmaps:
            wsmap = {
                'workspaceid': row_dict['workspaceid'],
                'userid': row_dict['userid'],
                'map_tpl_id': row_dict['map_tpl_id'],
                'parent_tpl_id': row_dict['parent_tpl_id'],
                'map_tpl_name': row_dict['map_tpl_name'],
                'istemplate': row_dict['istemplate'],
                'mapviewposition': row_dict['mapviewposition'],
                'mapviewsize': row_dict['mapviewsize'],
                'productcode': row_dict['productcode'],
                'subproductcode': row_dict['subproductcode'],
                'productversion': row_dict['productversion'],
                'mapsetcode': row_dict['mapsetcode'],
                'legendid': row_dict['legendid'],
                'legendlayout': row_dict['legendlayout'],
                'legendobjposition': row_dict['legendobjposition'],
                'showlegend': row_dict['showlegend'],
                'titleobjposition': row_dict['titleobjposition'],
                'titleobjcontent': row_dict['titleobjcontent'],
                'disclaimerobjposition': row_dict['disclaimerobjposition'],
                'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                'logosobjposition': row_dict['logosobjposition'],
                'logosobjcontent': row_dict['logosobjcontent'],
                'showobjects': row_dict['showobjects'],
                'showtoolbar': row_dict['showtoolbar'],
                'showgraticule': row_dict['showgraticule'],
                'showtimeline': row_dict['showtimeline'],
                'scalelineobjposition': row_dict['scalelineobjposition'],
                'vectorlayers': row_dict['vectorlayers'],
                'outmask': row_dict['outmask'],
                'outmaskfeature': row_dict['outmaskfeature'],
                'auto_open': row_dict['auto_open'],
                'zoomextent': row_dict['zoomextent'],
                'mapsize': row_dict['mapsize'],
                'mapcenter': row_dict['mapcenter']
            }
            maps.append(wsmap)
    return maps


def getWorkspaceGraphs(workspaceid):
    wsgraphs = querydb.get_workspace_graphs(workspaceid)
    graphs = []
    if hasattr(wsgraphs, "__len__") and wsgraphs.__len__() > 0:
        for row_dict in wsgraphs:
            graph = {
                'userid': row_dict['userid'],
                'workspaceid': row_dict['workspaceid'],
                'graph_tpl_id': row_dict['graph_tpl_id'],
                'parent_tpl_id': row_dict['parent_tpl_id'],
                'graph_tpl_name': row_dict['graph_tpl_name'],
                'istemplate': row_dict['istemplate'],
                'graphviewposition': row_dict['graphviewposition'],
                'graphviewsize': row_dict['graphviewsize'],
                'graph_type': row_dict['graph_type'],
                'selectedtimeseries': row_dict['selectedtimeseries'],
                'yearts': row_dict['yearts'],
                'tsfromperiod': row_dict['tsfromperiod'],
                'tstoperiod': row_dict['tstoperiod'],
                'yearstocompare': row_dict['yearstocompare'],
                'tsfromseason': row_dict['tsfromseason'],
                'tstoseason': row_dict['tstoseason'],
                'wkt_geom': row_dict['wkt_geom'],
                'selectedregionname': row_dict['selectedregionname'],
                'disclaimerobjposition': row_dict['disclaimerobjposition'],
                'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                'logosobjposition': row_dict['logosobjposition'],
                'logosobjcontent': row_dict['logosobjcontent'],
                'showobjects': row_dict['showobjects'],
                'showtoolbar': row_dict['showtoolbar'],
                'auto_open': row_dict['auto_open']
            }
            graphs.append(graph)
    return graphs


def getUserWorkspaces(params):
    workspaces_dict_all = []

    if 'userid' in params:
        userworkspaces = querydb.get_user_workspaces(params['userid'])
        if hasattr(userworkspaces, "__len__") and userworkspaces.__len__() > 0:
            for row_dict in userworkspaces:
                maps = getWorkspaceMaps(row_dict['workspaceid'])
                graphs = getWorkspaceGraphs(row_dict['workspaceid'])

                workspace = {
                    'userid': row_dict['userid'],
                    'workspaceid': row_dict['workspaceid'],
                    'workspacename': row_dict['workspacename'],
                    'pinned': row_dict['pinned'],
                    'shownewgraph': row_dict['shownewgraph'],
                    'showbackgroundlayer': row_dict['showbackgroundlayer'],
                    'maps': maps,
                    'graphs': graphs
                }

                workspaces_dict_all.append(workspace)

            workspaces_json = json.dumps(workspaces_dict_all, ensure_ascii=False, encoding='utf-8',
                                         sort_keys=True, indent=4, separators=(', ', ': '))

            workspaces_json = '{"success":"true", "total":' \
                              + str(userworkspaces.__len__()) \
                              + ',"userworkspaces":' + workspaces_json + '}'

        else:
            workspaces_json = '{"success":"true", "total":' \
                              + str(userworkspaces.__len__()) \
                              + ',"userworkspaces":[]}'
    else:
        workspaces_json = '{"success":false, "error":"Userid not given!"}'

    return workspaces_json


def saveWorkspaceGraphs(wsgraphs, workspaceid):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    for wsgraph in wsgraphs:
        wsgraphSettings = {
            'userid': wsgraph['userid'],
            'workspaceid': int(workspaceid),
            # 'graph_tpl_id': wsgraph['graph_tpl_id'],
            'parent_tpl_id': wsgraph['parent_tpl_id'],
            'graph_tpl_name': wsgraph['graph_tpl_name'],
            'istemplate': wsgraph['istemplate'],
            'graphviewposition': wsgraph['graphviewposition'],
            'graphviewsize': wsgraph['graphviewsize'],
            'graph_type': wsgraph['graph_type'],
            'selectedtimeseries': wsgraph['selectedtimeseries'],
            'yearts': wsgraph['yearts'],
            'tsfromperiod': wsgraph['tsfromperiod'],
            'tstoperiod': wsgraph['tstoperiod'],
            'yearstocompare': wsgraph['yearstocompare'],
            'tsfromseason': wsgraph['tsfromseason'],
            'tstoseason': wsgraph['tstoseason'],
            'wkt_geom': wsgraph['wkt_geom'],
            'selectedregionname': wsgraph['selectedregionname'],
            'disclaimerobjposition': wsgraph['disclaimerObjPosition'],
            'disclaimerobjcontent': wsgraph['disclaimerObjContent'],
            'logosobjposition': wsgraph['logosObjPosition'],
            'logosobjcontent': wsgraph['logosObjContent'],
            'showobjects': wsgraph['showObjects'],
            'showtoolbar': wsgraph['showtoolbar']
        }

        graphproperties = json.loads(wsgraph['graphproperties'])
        yaxes = json.loads(wsgraph['yAxes'])
        tsdrawprops = json.loads(wsgraph['tsdrawprops'])

        createstatus = '{"success":false, "message":"Error saving the workspace Graph!"}'
        if crud_db.create('user_graph_templates', wsgraphSettings):

            createdGraphTpl = querydb.get_last_graph_tpl_id(wsgraph['userid'], int(workspaceid))
            graphproperties['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
            crud_db.create('user_graph_tpl_drawproperties', graphproperties)

            for yaxe in yaxes:
                # print yaxe
                yaxe['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                yaxe['yaxe_id'] = yaxe['id']
                if yaxe['min'] == '':
                    yaxe['min'] = None
                if yaxe['max'] == '':
                    yaxe['max'] = None
                crud_db.create('user_graph_tpl_yaxes', yaxe)

            for tsdrawprop in tsdrawprops:
                tsdrawprop['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

            # Todo: use logger!
            createstatus = '{"success":true, "message":"Workspace Graph saved."}'


def saveWorkspaceMaps(wsmaps, workspaceid):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    for wsmap in wsmaps:
        legendid = wsmap['legendid']
        if wsmap['legendid'] == '':
            legendid = None

        wsmapSettings = {
            'userid': wsmap['userid'],
            'workspaceid': int(workspaceid),
            # 'map_tpl_id': None,
            'parent_tpl_id': wsmap['parent_tpl_id'],
            'map_tpl_name': wsmap['map_tpl_name'],
            'istemplate': wsmap['istemplate'],
            'mapviewposition': wsmap['mapviewPosition'],
            'mapviewsize': wsmap['mapviewSize'],
            'productcode': wsmap['productcode'],
            'subproductcode': wsmap['subproductcode'],
            'productversion': wsmap['productversion'],
            'mapsetcode': wsmap['mapsetcode'],
            'legendid': legendid,
            'legendlayout': wsmap['legendlayout'],
            'legendobjposition': wsmap['legendObjPosition'],
            'showlegend': wsmap['showlegend'],
            'titleobjposition': wsmap['titleObjPosition'],
            'titleobjcontent': wsmap['titleObjContent'],
            'disclaimerobjposition': wsmap['disclaimerObjPosition'],
            'disclaimerobjcontent': wsmap['disclaimerObjContent'],
            'logosobjposition': wsmap['logosObjPosition'],
            'logosobjcontent': wsmap['logosObjContent'],
            'showobjects': wsmap['showObjects'],
            'showtoolbar': wsmap['showtoolbar'],
            'showgraticule': wsmap['showgraticule'],
            'showtimeline': wsmap['showtimeline'],
            'scalelineobjposition': wsmap['scalelineObjPosition'],
            'vectorlayers': wsmap['vectorLayers'],
            'outmask': wsmap['outmask'],
            'outmaskfeature': wsmap['outmaskFeature'],
            'auto_open': wsmap['auto_open'],
            'zoomextent': wsmap['zoomextent'],
            'mapsize': wsmap['mapsize'],
            'mapcenter': wsmap['mapcenter']
        }

        if not crud_db.create('user_map_templates', wsmapSettings):
            # Todo: use logger!
            createstatus = '{"success":false, "message":"Error saving the workspace Map!"}'


def saveWorkspace(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace!"}'

    if 'userid' in params and 'workspacename' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename'],
            'pinned': params['pinned'],
            'shownewgraph': 'true',
            'showbackgroundlayer': 'false'
        }
        wsmaps = json.loads(params['maps'])
        wsgraphs = json.loads(params['graphs'])

        # If new user workspace, create new user workspace and get its workspaceid
        #   Insert all open/passed maps and graphs in the new workspace
        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                createdWorkspace = querydb.getCreatedUserWorkspace(params['userid'])
                for row in createdWorkspace:
                    newworkspaceid = row['lastworkspaceid']

                saveWorkspaceMaps(wsmaps, newworkspaceid)
                saveWorkspaceGraphs(wsgraphs, newworkspaceid)

                createstatus = '{"success":true, "message":"Workspace created!", "workspaceid": ' + str(newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace!"}'
        # Else, it is an existing user workspace, update workspace settings
        #   Delete all the workspace maps and graphs
        #   Insert all open/passed maps and graphs in the workspace
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                workspaceinfo = {
                    'userid': params['userid'],
                    'workspaceid': int(params['workspaceid'])
                }
                if crud_db.delete('user_map_templates', **workspaceinfo):
                    saveWorkspaceMaps(wsmaps, params['workspaceid'])
                if crud_db.delete('user_graph_templates', **workspaceinfo):
                    saveWorkspaceGraphs(wsgraphs, params['workspaceid'])

                createstatus = '{"success":true, "message":"Workspace updated!", "workspaceid": ' + str(params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No Workspace data given!"}'

    return createstatus


def saveWorkspacePin(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace pin change!"}'

    if 'userid' in params and 'workspaceid' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename'],
            'pinned': params['pinned']
        }

        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                createdWorkspace = querydb.getCreatedUserWorkspace(params['userid'])
                for row in createdWorkspace:
                    newworkspaceid = row['lastworkspaceid']

                createstatus = '{"success":true, "message":"Workspace created on pin setting change!", "workspaceid": ' + str(newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace on pin setting change!"}'
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                createstatus = '{"success":true, "message":"Workspace pin setting changed!", "workspaceid": ' + str(params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No user data given when changing the workspace pin setting!"}'

    return createstatus


def saveWorkspaceName(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    # ToDo: Better error handling.
    createstatus = '{"success":false, "message":"An error occured while saving the Workspace when changing the workspace name!"}'

    if 'userid' in params and 'workspaceid' in params:
        workspace = {
            'userid': params['userid'],
            'workspacename': params['workspacename']
        }

        if params['isNewWorkspace'] == 'true':
            if crud_db.create('user_workspaces', workspace):
                createdWorkspace = querydb.getCreatedUserWorkspace(params['userid'])
                for row in createdWorkspace:
                    newworkspaceid = row['lastworkspaceid']

                createstatus = '{"success":true, "message":"Workspace created when changing the workspace name!", "workspaceid": ' + str(newworkspaceid) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the new Workspace when changing the workspace name!"}'
        else:
            workspace['workspaceid'] = int(params['workspaceid'])
            if crud_db.update('user_workspaces', workspace):
                createstatus = '{"success":true, "message":"Workspace name updated!", "workspaceid": ' + str(params['workspaceid']) + '}'

    else:
        createstatus = '{"success":false, "message":"No user data given when changing the workspace name!"}'

    return createstatus


def getMapTemplates(params):
    maptemplate_dict_all = []
    if 'userid' in params:
        usermaptemplates = querydb.get_user_map_templates(params['userid'])
        if hasattr(usermaptemplates, "__len__") and usermaptemplates.__len__() > 0:
            for row_dict in usermaptemplates:
                # row_dict = functions.row2dict(row)

                mapTemplate = {
                    'workspaceid': row_dict['workspaceid'],
                    'userid': row_dict['userid'],
                    'map_tpl_id': row_dict['map_tpl_id'],
                    'parent_tpl_id': row_dict['parent_tpl_id'],
                    'map_tpl_name': row_dict['map_tpl_name'],
                    'istemplate': row_dict['istemplate'],
                    'mapviewposition': row_dict['mapviewposition'],
                    'mapviewsize': row_dict['mapviewsize'],
                    'productcode': row_dict['productcode'],
                    'subproductcode': row_dict['subproductcode'],
                    'productversion': row_dict['productversion'],
                    'mapsetcode': row_dict['mapsetcode'],
                    'legendid': row_dict['legendid'],
                    'legendlayout': row_dict['legendlayout'],
                    'legendobjposition': row_dict['legendobjposition'],
                    'showlegend': row_dict['showlegend'],
                    'titleobjposition': row_dict['titleobjposition'],
                    'titleobjcontent': row_dict['titleobjcontent'],
                    'disclaimerobjposition': row_dict['disclaimerobjposition'],
                    'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                    'logosobjposition': row_dict['logosobjposition'],
                    'logosobjcontent': row_dict['logosobjcontent'],
                    'showobjects': row_dict['showobjects'],
                    'showtoolbar': row_dict['showtoolbar'],
                    'showgraticule': row_dict['showgraticule'],
                    'showtimeline': row_dict['showtimeline'],
                    'scalelineobjposition': row_dict['scalelineobjposition'],
                    'vectorlayers': row_dict['vectorlayers'],
                    'outmask': row_dict['outmask'],
                    'outmaskfeature': row_dict['outmaskfeature'],
                    'auto_open': row_dict['auto_open'],
                    'zoomextent': row_dict['zoomextent'],
                    'mapsize': row_dict['mapsize'],
                    'mapcenter': row_dict['mapcenter']
                }

                maptemplate_dict_all.append(mapTemplate)

            maptemplates_json = json.dumps(maptemplate_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            maptemplates_json = '{"success":"true", "total":' \
                                + str(usermaptemplates.__len__()) \
                                + ',"usermaptemplates":' + maptemplates_json + '}'

        else:
            maptemplates_json = '{"success":true, "total":' \
                                + str(usermaptemplates.__len__()) \
                                + ',"usermaptemplates":[]}'
            # maptemplates_json = '{"success":true, "error":"No Map Templates defined for user!"}'   # OR RETURN A DEFAULT MAP TEMPLATE?????

    else:
        maptemplates_json = '{"success":false, "error":"Userid not given!"}'

    return maptemplates_json


def saveMapTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Map Template!"}'

    if 'userid' in params and 'map_tpl_name' in params:
        legendid = params['legendid']
        if params['legendid'] == '':
            legendid = None

        defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['userid'])
        if not defaultworkspaceid:
            return createstatus

        mapTemplate = {
            'userid': params['userid'],
            'workspaceid': defaultworkspaceid,
            # 'map_tpl_id': None,
            'map_tpl_name': params['map_tpl_name'],
            'istemplate': params['istemplate'],
            'mapviewposition': params['mapviewPosition'],
            'mapviewsize': params['mapviewSize'],
            'productcode': params['productcode'],
            'subproductcode': params['subproductcode'],
            'productversion': params['productversion'],
            'mapsetcode': params['mapsetcode'],
            'legendid': legendid,
            'legendlayout': params['legendlayout'],
            'legendobjposition': params['legendObjPosition'],
            'showlegend': params['showlegend'],
            'titleobjposition': params['titleObjPosition'],
            'titleobjcontent': params['titleObjContent'],
            'disclaimerobjposition': params['disclaimerObjPosition'],
            'disclaimerobjcontent': params['disclaimerObjContent'],
            'logosobjposition': params['logosObjPosition'],
            'logosobjcontent': params['logosObjContent'],
            'scalelineobjposition': params['scalelineObjPosition'],
            'showobjects': params['showObjects'],
            'showtoolbar': params['showtoolbar'],
            'showgraticule': params['showgraticule'],
            'showtimeline': params['showtimeline'],
            'vectorlayers': params['vectorLayers'],
            'outmask': params['outmask'],
            'outmaskfeature': params['outmaskFeature'],
            'auto_open': params['auto_open'],
            'zoomextent': params['zoomextent'],
            'mapsize': params['mapsize'],
            'mapcenter': params['mapcenter']
        }

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_map_templates', mapTemplate):
                # createdMapTpl = crud_db.read('user_map_templates', **mapTemplate)
                createdMapTpl = querydb.get_last_map_tpl_id(params['userid'], defaultworkspaceid)
                updateMapTemplate = {
                    'userid': params['userid'],
                    'workspaceid': defaultworkspaceid,
                    'map_tpl_id': createdMapTpl[0]['map_tpl_id'],
                    'parent_tpl_id': createdMapTpl[0]['map_tpl_id']
                }
                # mapTemplate['map_tpl_id'] = createdMapTpl[0]['map_tpl_id']
                # mapTemplate['parent_tpl_id'] = createdMapTpl[0]['map_tpl_id']
                crud_db.update('user_map_templates', updateMapTemplate)
                createstatus = '{"success":true, "message":"Map Template created!", "map_tpl_id": ' + str(createdMapTpl[0]['map_tpl_id']) + '}'
            else:
                createstatus = '{"success":false, "message":"Error saving the Map Template!"}'
        else:
            mapTemplate['map_tpl_id'] = params['parent_tpl_id']
            if crud_db.update('user_map_templates', mapTemplate):
                createstatus = '{"success":true, "message":"Map Template updated!"}'

    else:
        createstatus = '{"success":false, "message":"No Map Template data given!"}'

    return createstatus


def getGraphTemplates(params):
    graphtemplate_dict_all = []

    if 'userid' in params:
        usergraphtemplates = querydb.get_user_graph_templates(params['userid'])
        if hasattr(usergraphtemplates, "__len__") and usergraphtemplates.__len__() > 0:
            for row_dict in usergraphtemplates:
                # row_dict = functions.row2dict(row)

                graphTemplate = {
                    'userid': row_dict['userid'],
                    'workspaceid': row_dict['workspaceid'],
                    'graph_tpl_id': row_dict['graph_tpl_id'],
                    'parent_tpl_id': row_dict['parent_tpl_id'],
                    'graph_tpl_name': row_dict['graph_tpl_name'],
                    'istemplate': row_dict['istemplate'],
                    'graphviewposition': row_dict['graphviewposition'],
                    'graphviewsize': row_dict['graphviewsize'],
                    'graph_type': row_dict['graph_type'],
                    'selectedtimeseries': row_dict['selectedtimeseries'],
                    'yearts': row_dict['yearts'],
                    'tsfromperiod': row_dict['tsfromperiod'],
                    'tstoperiod': row_dict['tstoperiod'],
                    'yearstocompare': row_dict['yearstocompare'],
                    'tsfromseason': row_dict['tsfromseason'],
                    'tstoseason': row_dict['tstoseason'],
                    'wkt_geom': row_dict['wkt_geom'],
                    'selectedregionname': row_dict['selectedregionname'],
                    'disclaimerobjposition': row_dict['disclaimerobjposition'],
                    'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                    'logosobjposition': row_dict['logosobjposition'],
                    'logosobjcontent': row_dict['logosobjcontent'],
                    'showobjects': row_dict['showobjects'],
                    'showtoolbar': row_dict['showtoolbar'],
                    'auto_open': row_dict['auto_open']
                }

                graphtemplate_dict_all.append(graphTemplate)

            graphtemplates_json = json.dumps(graphtemplate_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":' + graphtemplates_json + '}'

        else:
            graphtemplates_json = '{"success":"true", "total":0' \
                                  + ',"usergraphtemplates":[]}'
            # graphtemplates_json = '{"success":true, "error":"No Graph Templates defined for user!"}'  # OR RETURN A DEFAULT GRAPH TEMPLATE?????

    else:
        graphtemplates_json = '{"success":false, "error":"Userid not given!"}'

    return graphtemplates_json


def __getGraphTemplates(params):
    graphtemplate_dict_all = []

    if 'userid' in params:
        usergraphtemplates = querydb.get_user_graph_templates(params['userid'])
        if hasattr(usergraphtemplates, "__len__") and usergraphtemplates.__len__() > 0:
            for row_dict in usergraphtemplates:
                # row_dict = functions.row2dict(row)

                graphTemplate = {
                    'userid': row_dict['userid'],
                    'graph_tpl_name': row_dict['graph_tpl_name'],
                    'graphviewposition': row_dict['graphviewposition'],
                    'graphviewsize': row_dict['graphviewsize'],
                    'graph_type': row_dict['graph_type'],
                    'selectedtimeseries': row_dict['selectedtimeseries'],
                    'yearts': row_dict['yearts'],
                    'tsfromperiod': row_dict['tsfromperiod'],
                    'tstoperiod': row_dict['tstoperiod'],
                    'yearstocompare': row_dict['yearstocompare'],
                    'tsfromseason': row_dict['tsfromseason'],
                    'tstoseason': row_dict['tstoseason'],
                    'wkt_geom': row_dict['wkt_geom'],
                    'selectedregionname': row_dict['selectedregionname'],
                    'disclaimerobjposition': row_dict['disclaimerobjposition'],
                    'disclaimerobjcontent': row_dict['disclaimerobjcontent'],
                    'logosobjposition': row_dict['logosobjposition'],
                    'logosobjcontent': row_dict['logosobjcontent'],
                    'showobjects': row_dict['showobjects'],
                    'auto_open': row_dict['auto_open']
                }

                graphtemplate_dict_all.append(graphTemplate)

            graphtemplates_json = json.dumps(graphtemplate_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":' + graphtemplates_json + '}'

        else:
            graphtemplates_json = '{"success":"true", "total":' \
                                  + str(usergraphtemplates.__len__()) \
                                  + ',"usergraphtemplates":[]}'
            # graphtemplates_json = '{"success":true, "error":"No Graph Templates defined for user!"}'  # OR RETURN A DEFAULT GRAPH TEMPLATE?????

    else:
        graphtemplates_json = '{"success":false, "error":"Userid not given!"}'

    return graphtemplates_json


def saveGraphTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Graph Template!"}'

    if 'userid' in params and 'graph_tpl_name' in params:

        defaultworkspaceid = querydb.getDefaultUserWorkspaceID(params['userid'])
        if not defaultworkspaceid:
            return createstatus

        graphTemplate = {
            'userid': params['userid'],
            'workspaceid': defaultworkspaceid,
            # 'graph_tpl_id': params['graph_tpl_id'],
            'graph_tpl_name': params['graph_tpl_name'],
            'istemplate': params['istemplate'],
            'graphviewposition': params['graphviewposition'],
            'graphviewsize': params['graphviewsize'],
            'graph_type': params['graph_type'],
            'selectedtimeseries': params['selectedtimeseries'],
            'yearts': params['yearts'],
            'tsfromperiod': params['tsfromperiod'],
            'tstoperiod': params['tstoperiod'],
            'yearstocompare': params['yearstocompare'],
            'tsfromseason': params['tsfromseason'],
            'tstoseason': params['tstoseason'],
            'wkt_geom': params['wkt_geom'],
            'selectedregionname': params['selectedregionname'],
            'disclaimerobjposition': params['disclaimerObjPosition'],
            'disclaimerobjcontent': params['disclaimerObjContent'],
            'logosobjposition': params['logosObjPosition'],
            'logosobjcontent': params['logosObjContent'],
            'showobjects': params['showObjects'],
            'showtoolbar': params['showtoolbar']
        }

        graphproperties = json.loads(params['graphproperties'])
        yaxes = json.loads(params['yAxes'])
        tsdrawprops = json.loads(params['tsdrawprops'])

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_graph_templates', graphTemplate):
                # createdGraphTpl = crud_db.read('user_graph_templates', **graphTemplate)
                createdGraphTpl = querydb.get_last_graph_tpl_id(params['userid'], defaultworkspaceid)
                updateGraphTemplate = {
                    'userid': params['userid'],
                    'workspaceid': defaultworkspaceid,
                    'graph_tpl_id': createdGraphTpl[0]['graph_tpl_id'],
                    'parent_tpl_id': createdGraphTpl[0]['graph_tpl_id']
                }

                crud_db.update('user_graph_templates', updateGraphTemplate)

                graphproperties['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                crud_db.create('user_graph_tpl_drawproperties', graphproperties)

                for yaxe in yaxes:
                    yaxe['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                    yaxe['yaxe_id'] = yaxe['id']
                    if yaxe['min'] == '':
                        yaxe['min'] = None
                    if yaxe['max'] == '':
                        yaxe['max'] = None
                    crud_db.create('user_graph_tpl_yaxes', yaxe)

                for tsdrawprop in tsdrawprops:
                    tsdrawprop['graph_tpl_id'] = createdGraphTpl[0]['graph_tpl_id']
                    crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

                createstatus = '{"success":true, "message":"Graph Template created!", "graph_tpl_id": ' + str(createdGraphTpl[0]['graph_tpl_id']) + '}'
            else:
                createstatus = '{"success":false, "message":"Error creating the Graph Template!"}'
        else:
            graphTemplate['graph_tpl_id'] = params['parent_tpl_id']
            if crud_db.update('user_graph_templates', graphTemplate):
                graphproperties['graph_tpl_id'] = params['parent_tpl_id']
                crud_db.update('user_graph_tpl_drawproperties', graphproperties)

                crud_db.delete('user_graph_tpl_yaxes', **{'graph_tpl_id': params['parent_tpl_id']})
                for yaxe in yaxes:
                    yaxe['graph_tpl_id'] = params['parent_tpl_id']
                    yaxe['yaxe_id'] = yaxe['id']
                    if yaxe['min'] == '':
                        yaxe['min'] = None
                    if yaxe['max'] == '':
                        yaxe['max'] = None
                    crud_db.create('user_graph_tpl_yaxes', yaxe)

                crud_db.delete('user_graph_tpl_timeseries_drawproperties', **{'graph_tpl_id': params['parent_tpl_id']})
                for tsdrawprop in tsdrawprops:
                    tsdrawprop['graph_tpl_id'] = params['parent_tpl_id']
                    crud_db.create('user_graph_tpl_timeseries_drawproperties', tsdrawprop)

                createstatus = '{"success":true, "message":"Graph Template updated!"}'
            else:
                createstatus = '{"success":false, "message":"Error updating the Graph Template!"}'
    else:
        createstatus = '{"success":false, "message":"No Graph Template data given!"}'

    return createstatus


def __saveGraphTemplate(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":false, "message":"An error occured while saving the Graph Template!"}'

    if 'userid' in params and 'graph_tpl_name' in params:

        # graphProperties:{"localRefresh": false, "title": "Polygon", "subtitle": 2017, "filename": "Polygon_2017",
        #                  "graph_title_font_size": "26", "graph_title_font_color": "#000000",
        #                  "graph_subtitle_font_size": "22", "graph_subtitle_font_color": "#808080",
        #                  "xaxe_font_size": "22", "xaxe_font_color": "#000000", "legend_title_font_size": "22",
        #                  "legend_title_font_color": "#000000", "width": "1100", "height": "800"}

        # selectedTimeseries:[{"productcode": "vgt-ndvi", "version": "sv2-pv2.1", "subproductcode": "ndvi-linearx2",
        #                      "mapsetcode": "SPOTV-Africa-1km", "date_format": "YYYYMMDD", "frequency_id": "e1dekad",
        #                      "cumulative": false, "difference": false, "reference": false, "colorramp": false,
        #                      "legend_id": null, "zscore": false}]

        graphTemplate = {
            'userid': params['userid'],
            'graph_tpl_name': params['graph_tpl_name'],
            'graphviewposition': params['graphviewposition'],
            'graphviewsize': params['graphviewsize'],
            'graph_type': params['graph_type'],
            'selectedtimeseries': params['selectedtimeseries'],
            'yearts': params['yearts'],
            'tsfromperiod': params['tsfromperiod'],
            'tstoperiod': params['tstoperiod'],
            'yearstocompare': params['yearstocompare'],
            'tsfromseason': params['tsfromseason'],
            'tstoseason': params['tstoseason'],
            'wkt_geom': params['wkt_geom'],
            'selectedregionname': params['selectedregionname'],

            'disclaimerobjposition': params['disclaimerObjPosition'],
            'disclaimerobjcontent': params['disclaimerObjContent'],
            'logosobjposition': params['logosObjPosition'],
            'logosobjcontent': params['logosObjContent'],
            'showobjects': params['showObjects']
        }

        # print params
        if params['newtemplate'] == 'true':
            if crud_db.create('user_graph_templates', graphTemplate):
                createstatus = '{"success":true, "message":"Graph Template created!"}'
            else:
                createstatus = '{"success":false, "message":"Error saving the Graph Template! Name already exists!"}'
        else:
            if crud_db.update('user_graph_templates', graphTemplate):
                createstatus = '{"success":true, "message":"Graph Template updated!"}'
    else:
        createstatus = '{"success":false, "message":"No Graph Template data given!"}'

    return createstatus


def getGraphTimeseries(params):
    if params['graphtype'] == 'ranking':
        return rankTimeseries(params)
    if params['graphtype'] == 'matrix':
        return matrixTimeseries(params)
    else:
        return classicTimeseries(params)


def matrixTimeseries(params):
    # params = web.input()
    # yearts = params.yearTS
    # tsFromPeriod = params.tsFromPeriod
    # tsToPeriod = params.tsToPeriod
    # showYearInTicks = True

    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    yearsToCompare = sorted(json.loads(params.yearsToCompare))
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    data_available = False
    colorramp = False
    legend_id = None
    overTwoYears = False

    userid = params.userid
    istemplate = params.istemplate
    graphtype = params.graphtype
    graph_tpl_id = params.graph_tpl_id
    graph_tpl_name = params.graph_tpl_name

    # if hasattr(params, "userid") and params.userid != '':
    #     user = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        date_format = timeserie['date_format']
        frequency_id = timeserie['frequency_id']
        colorramp = timeserie['colorramp']
        legend_id = timeserie['legend_id']

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                   passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                   passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop

        nodata = None
        subproductinfo = querydb.get_subproduct(productcode, version, subproductcode)
        if subproductinfo != []:
            subproductinfo_rec = functions.row2dict(subproductinfo)
            nodata = subproductinfo_rec['nodata']

        if len(yearsToCompare) > 0:
            data = []
            y = 0

            xAxesYear = yearsToCompare[-1]
            for year in yearsToCompare:    # Handle Leap year date 29 February. If exists in data then change the year of all data to the leap year.
                if calendar.isleap(year):
                    xAxesYear = year

            for year in yearsToCompare:
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))
                        overTwoYears = True

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

                if len(list_values) > 0 and not data_available:
                    data_available = True

                x = 0
                for val in list_values:
                    value = []
                    # # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    # valdate = functions.unix_time_millis(val['date'])
                    # # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    # date = str(yearsToCompare[-1]) + '-' + str(val['date'].strftime('%m')) + '-' + str(val['date'].strftime('%d'))
                    # print val['date']

                    # if overTwoYears:
                    #     date = datetime.date(val['date'].year, val['date'].month, val['date'].day)
                    # else:
                    #     date = datetime.date(yearsToCompare[-1], val['date'].month, val['date'].day)
                    date = datetime.date(xAxesYear, val['date'].month, val['date'].day)

                    valdate = functions.unix_time_millis(date)
                    value.append(valdate)    # Date for xAxe
                    # if overTwoYears:
                    #     value.append(str(year) + '-' + str(year+1))  # Year for yAxe
                    # else:
                    value.append(val['date'].year)  # Year for yAxe

                    if val['meanvalue'] == float(nodata):
                        value.append(None)
                    else:
                        value.append(val['meanvalue'])
                    data.append(value)
                    x += 1
                y += 1

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {
                    'name': productcode + '-' + version + '-' + subproductcode,
                    'frequency_id': frequency_id,
                    # 'type': 'heatmap',
                    'yAxis': productcode + ' - ' + version,
                    'data': data
                    # 'visible': True,
                    # 'borderWidth': 1,
                    # 'dataLabels': {
                    #     'enabled': True,
                    #     'color': '#000000'
                    # }
                }
            else:
                # for ts_drawprops in product_ts_drawproperties:
                # print ts_drawprops
                ts = {
                    'name': ts_drawprops['tsname_in_legend'],
                    'frequency_id': frequency_id,
                    # 'type': 'heatmap',
                    'yAxis': ts_drawprops['yaxe_id'],
                    'data': data
                }
            timeseries.append(ts)

    legend_info = querydb.get_legend_info(legendid=legend_id)
    step_type = 'linear'
    if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
        for row in legend_info:
            step_type = row.step_type

        if step_type != 'logarithmic':
            step_type = 'linear'

    legend_steps = querydb.get_legend_steps(legendid=legend_id)
    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        minimizeSteps = False
        if legend_steps.__len__() > 35:
            colorramp = True
            minimizeSteps = True

        firstStep = 0.01
        roundTo = 2
        if legend_steps.__len__() >= 100:
            firstStep = 0.001
            roundTo = 3

        # min = float((legend_steps[0].from_step - legend_steps[0].scale_offset)/legend_steps[0].scale_factor)
        # max = float((legend_steps[legend_steps.__len__()-1].to_step - legend_steps[legend_steps.__len__()-1].scale_offset)/legend_steps[legend_steps.__len__()-1].scale_factor)

        if step_type == 'logarithmic':
            if legend_steps[0].from_step <= 0:
                min = legend_steps[0].to_step
                minColorSecondRow = True
            else:
                min = legend_steps[0].from_step
                minColorSecondRow = False
        else:
            min = legend_steps[0].from_step

        max = legend_steps[legend_steps.__len__()-1].to_step

        stops = []
        colors = []
        dataClasses = []
        rownr = 0
        for step in legend_steps:
            stop = []
            rownr += 1
            # from_step = float((step.from_step - step.scale_offset)/step.scale_factor)
            # to_step = float((step.to_step - step.scale_offset)/step.scale_factor)
            from_step = step.from_step
            to_step = step.to_step

            colorRGB = map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip()))
            colorHex = functions.rgb2html(colorRGB)

            if step_type == 'logarithmic':
                if rownr == 1 and not minColorSecondRow:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)

                if rownr == 2 and minColorSecondRow:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)
            else:
                if rownr == 1:
                    mincolor = colorHex
                    if step.color_label is None or (step.color_label is not None and step.color_label.strip() == ''):
                        # stop.append(firstStep)
                        stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                        stop.append(colorHex)
                        stops.append(stop)

            if rownr == legend_steps.__len__():
                maxcolor = colorHex

            if minimizeSteps:
                if step.color_label is not None and step.color_label.strip() != '':
                    # stop.append(round(to_step / max, roundTo))
                    # stop.append(round((from_step-min)/(max-min), roundTo))
                    stop.append(round(rownr/float(legend_steps.__len__()), roundTo))
                    # stop.append(round(rownr * firstStep, 3))
                    # stop.append(round(rownr/max, 2))
                    stop.append(colorHex)
                    stops.append(stop)
            else:
                colors.append(colorHex)
                # stop.append((from_step-min)/(max-min))
                stop.append(round(rownr / float(legend_steps.__len__()), roundTo))
                # stop.append(round(rownr * firstStep, 3))
                stop.append(colorHex)
                stops.append(stop)

            dataClass = {
                'from': from_step,
                'to': to_step,
                'color': colorHex,
                'name': step.color_label
            }
            dataClasses.append(dataClass)

    if colorramp:
        if minimizeSteps:
            tickPixelInterval = int(legend_steps.__len__()/len(stops))
            # tickInterval = legend_steps.__len__()
        else:
            tickPixelInterval = 72
            # tickPixelInterval = int(legend_steps.__len__()/len(stops))
            # tickPixelInterval = legend_steps.__len__()
            # tickInterval = tickPixelInterval

        colorAxis = {
            'min': min,
            'max': max,
            # 'floor': min,
            'ceiling': max,
            'stops': stops,
            # 'colors': colors,
            'maxColor': maxcolor,
            'minColor': mincolor,
            # 'minPadding': 0.05,
            # 'maxPadding': 0.5,
            'startOnTick': True,
            'endOnTick': True,
            'tickWidth': 2,
            'tickmarkPlacement': 'on',
            # 'tickInterval': None,
            # 'tickPixelInterval': tickPixelInterval,
            # 'tickLength': tickInterval,
            'gridLineWidth': 0,
            # 'gridLineColor': 'white',
            # 'minorTickInterval': 0.1,
            # 'minorGridLineColor': 'white',
            'type': step_type   # 'logarithmic'  'linear'  #
        }
    else:
        colorAxis = {
            'dataClasses': dataClasses,
            # 'dataClassColor': 'category',
            'startOnTick': False,
            'endOnTick': False
        }

    if overTwoYears:
        yearsToCompare.append(yearsToCompare[-1] + 1)  # Add extra year
        # for year in yearsToCompare:
        #     categories.append(str(year) + '-' + str(year+1))
    categories = yearsToCompare
    min = yearsToCompare[0]  # yaxe.min
    max = yearsToCompare[-1]  # yaxe.max

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            yaxe = {'id': passedyaxe['id'],
                    'categories': categories,
                    'title': passedyaxe['title'],
                    'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'],
                    'unit': passedyaxe['unit'],
                    'opposite': passedyaxe['opposite'],
                    'min': min,
                    'max': max,
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe in timeseries_yaxes:
            # min = yearsToCompare[0]    # yaxe.min
            # max = yearsToCompare[-1]    # yaxe.max

            yaxe = {'id': yaxe.yaxe_id,
                    'categories': categories,
                    'title': yaxe.title,
                    'title_color': yaxe.title_color.replace("  ", " "),
                    'title_font_size': yaxe.title_font_size,
                    'unit': yaxe.unit,
                    'opposite': yaxe.opposite,
                    'min': min,
                    'max': max,
                    'aggregation_type': yaxe.aggregation_type,
                    'aggregation_min': yaxe.aggregation_min,
                    'aggregation_max': yaxe.aggregation_max
                    }
            yaxes.append(yaxe)

    ts_json = {"data_available": data_available,
               "showYearInTicks": False,
               "showYearInToolTip": "true",
               "colorAxis": colorAxis,
               'colors': colors,
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json,
                         ensure_ascii=False,
                         sort_keys=True,
                         separators=(', ', ': '))
    return ts_json


def rankTimeseries(params):
    # params = web.input()
    # yearts = params.yearTS
    # tsFromPeriod = params.tsFromPeriod
    # tsToPeriod = params.tsToPeriod
    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    yearsToCompare = sorted(json.loads(params.yearsToCompare))
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    showYearInTicks = True
    data_available = False

    userid = params.userid
    istemplate = params.istemplate
    graphtype = params.graphtype
    graph_tpl_id = params.graph_tpl_id
    graph_tpl_name = params.graph_tpl_name

    # if hasattr(params, "userid") and params.userid != '':
    #     user = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        # date_format = timeserie['date_format']
        zscore = timeserie['zscore']
        tscolor = "#000000"

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                   passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                   passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop

        tscolor = ts_drawprops['color'].replace("  ", " ")

        if len(yearsToCompare) > 1:
            dataRanking = []
            dataZScore = []
            yearDataZScoreForAVGSTD = []

            for year in yearsToCompare:
                showYearInTicks = False

                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

                if len(list_values) > 0:
                    data_available = True

                cumulatedValue = 0
                for val in list_values:
                    if val['meanvalue'] != None:
                        cumulatedValue += val['meanvalue']

                yearDataRanking = {
                    'name': str(year),
                    'color': tscolor,   # '#0065a2',
                    'y': cumulatedValue
                }
                dataRanking.append(yearDataRanking)

                yearDataZScore = {
                    'name': str(year),
                    'color': tscolor,   # '#0065a2',
                    'y': cumulatedValue
                }
                dataZScore.append(yearDataZScore)
                yearDataZScoreForAVGSTD.append(cumulatedValue)

            dataRanking = sorted(dataRanking, key=lambda k:k['name'], reverse=True)
            dataRanking[0]['color'] = '#ff0000'
            dataRanking = sorted(dataRanking, key=lambda k:k['y'], reverse=False)

            # from operator import itemgetter, attrgetter
            # data = sorted(data, key=attrgetter('y'), reverse=False)
            # data = sorted(data, key=itemgetter(2), reverse=False)

            zScoreAVG = NP.mean(yearDataZScoreForAVGSTD)
            zScoreSTD = NP.std(yearDataZScoreForAVGSTD)
            for yearData in dataZScore:
                zScoreValue = (yearData['y']-zScoreAVG)/zScoreSTD
                yearData['y'] = zScoreValue
                if zScoreValue < 0:
                    yearData['color'] = '#ff0000'

            if zscore:
                data = dataZScore
            else:
                data = dataRanking

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'column',
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True
                      }
            else:
                # for ts_drawprops in product_ts_drawproperties:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': 'column',  # ts_drawprops.graphtype,
                      'color': ts_drawprops['color'].replace("  ", " "),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'visible': True
                      }
            timeseries.append(ts)

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            min = None
            max = None
            yaxe = {'id': passedyaxe['id'], 'title': passedyaxe['title'], 'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'], 'unit': passedyaxe['unit'], 'opposite': passedyaxe['opposite'],
                    'min': min, 'max': max,
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe in timeseries_yaxes:
            min = None    # yaxe.min
            max = None    # yaxe.max

            yaxe = {'id': yaxe.yaxe_id,
                    'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "), 'title_font_size': yaxe.title_font_size,
                    'unit': yaxe.unit, 'opposite': yaxe.opposite, 'min': min, 'max': max,
                    'aggregation_type': yaxe.aggregation_type, 'aggregation_min': yaxe.aggregation_min, 'aggregation_max': yaxe.aggregation_max}
            yaxes.append(yaxe)

    ts_json = {"data_available": data_available,
               "showYearInTicks": showYearInTicks,
               "showYearInToolTip": "true",
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json,
                         ensure_ascii=False,
                         sort_keys=True,
                         separators=(', ', ': '))
    return ts_json


def classicTimeseries(params):
    yearts = params['yearTS']
    wkt = params['WKT']
    requestedtimeseries = json.loads(params['selectedTimeseries'])
    passedyaxes = None
    if params['yAxes']:
        passedyaxes = json.loads(params['yAxes'])
    passedtsdrawprops = None
    if params['tsdrawprops']:
        passedtsdrawprops = json.loads(params['tsdrawprops'])
    tsFromPeriod = params['tsFromPeriod']
    tsToPeriod = params['tsToPeriod']
    yearsToCompare = params['yearsToCompare']
    tsFromSeason = params['tsFromSeason']
    tsToSeason = params['tsToSeason']
    showYearInTicks = True
    data_available = False
    cumulative = False
    if params['graphtype'] == 'cumulative':
        cumulative = True
    userid = params.userid
    istemplate = params.istemplate
    graphtype = params.graphtype
    graph_tpl_id = params.graph_tpl_id
    graph_tpl_name = params.graph_tpl_name

    # if hasattr(params, "userid") and params.userid != '':
    #     userid = params.userid
    #     graph_tpl_name = params.graph_tpl_name

    if tsFromSeason != '' and tsToSeason != '' and yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) >= 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

    elif yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) >= 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

    elif params['yearTS'] != '':
        if tsFromSeason != '' and tsToSeason != '':
            if tsToSeason != '':
                from_date = datetime.date(int(params['yearTS']), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params['yearTS']), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(params['yearTS'])+1, int(tsToSeason[:2]), int(tsToSeason[3:]))
            else:
                from_date = datetime.date(int(params['yearTS']), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params['yearTS']), 12, 31)
        else:
            from_date = datetime.date(int(params['yearTS']), 1, 1)
            to_date = datetime.date(int(params['yearTS']), 12, 31)
        showYearInTicks = False

    elif tsFromPeriod != '' and tsToPeriod != '':
        from_date = datetime.datetime.strptime(tsFromPeriod, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(tsToPeriod, '%Y-%m-%d').date()

    cum_yaxe = []
    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        date_format = timeserie['date_format']

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = {'aggregation_type': 'mean',
                     'aggregation_min': None,
                     'aggregation_max': None}

        product_yaxe = querydb.get_product_yaxe(product, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        for yaxe_info in product_yaxe:
            if passedyaxes is not None:
                for passedyaxe in passedyaxes:
                    if passedyaxe['id'] == yaxe_info.yaxe_id:
                        aggregate = {'aggregation_type': passedyaxe['aggregation_type'],
                                     'aggregation_min': passedyaxe['aggregation_min'],
                                     'aggregation_max': passedyaxe['aggregation_max']}
            else:
                aggregate = {'aggregation_type': yaxe_info.aggregation_type,
                             'aggregation_min': yaxe_info.aggregation_min,
                             'aggregation_max': yaxe_info.aggregation_max}
            if cumulative:
                cum_yaxe.append(yaxe_info.yaxe_id)

        ts_drawprops = None
        if passedtsdrawprops is not None:
            for passedtsdrawprop in passedtsdrawprops:
                if passedtsdrawprop['productcode'] == product['productcode'] and \
                   passedtsdrawprop['subproductcode'] == product['subproductcode'] and \
                   passedtsdrawprop['version'] == product['version']:
                    ts_drawprops = passedtsdrawprop
        else:
            product_ts_drawproperties = querydb.get_product_timeseries_drawproperties(product, userid, istemplate,
                                                                                      graphtype, graph_tpl_id,
                                                                                      graph_tpl_name)
            for ts_drawprop in product_ts_drawproperties:
                ts_drawprops = ts_drawprop


        if date_format == 'MMDD' and len(yearsToCompare) > 1:
            year = yearsToCompare[0]
            showYearInTicks = False
            from_date = datetime.date(year, 1, 1)
            to_date = datetime.date(year, 12, 31)

            if tsFromSeason != '' and tsToSeason != '':
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)
            # print list_values
            # list_values = sorted(list_values, key=lambda k:k['date'], reverse=True)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)
            if len(data) > 0:
                data_available = True

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      # 'xAxis': str(year),
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            else:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': ts_drawprops['charttype'],
                      'dashStyle': ts_drawprops['linestyle'],
                      'lineWidth': ts_drawprops['linewidth'],
                      'color': ts_drawprops['color'].replace("  ", " "),
                      # 'xAxis': str(year),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

        elif len(yearsToCompare) > 1:     # yearsToCompare != '' or
            # yearsToCompare = json.loads(yearsToCompare)
            colorAdd = 0
            colorSubstract = 0
            for year in yearsToCompare:
                showYearInTicks = False
                from_date = datetime.date(int(year), 1, 1)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                if ts_drawprops['color'][0] == '#':        # Transform HTML HEX color code to RGB
                    h = ts_drawprops['color'].lstrip('#')
                    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                    rgb = list(rgb)
                else:
                    if functions.isValidRGB(ts_drawprops['color'].replace("  ", " ")):
                        rgb = ts_drawprops['color'].replace("  ", " ").split(' ')
                    else:
                        # RGB value stored in the database is not correct so define as default value BLACK.
                        rgb = "0 0 0".split(' ')

                rgb = map(int, rgb)
                rgb[-1] = rgb[-1]+colorAdd
                rgb[-2] = rgb[-2]+colorAdd
                rgb[-3] = rgb[-3]-colorSubstract
                tsColor = ' '.join([str(i) for i in rgb])
                colorAdd += 65
                colorSubstract += 50

                # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
                # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
                # p = Process(target=getTimeseries, args=args)
                # p.start()
                # p.join()
                # list_values = self.out_queue.get()
                # self.out_queue.empty()
                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(data) > 0:
                    data_available = True

                if ts_drawprops is None:
                    # Set defaults in case no entry exists in the DB
                    ts = {'name': str(year) + ' ' + productcode + '-' + version + '-' + subproductcode,
                          'type': 'line',
                          'dashStyle': 'Solid',
                          'lineWidth': 2,
                          'color': '#000000',
                          'xAxis': str(year),
                          'yAxis': productcode + ' - ' + version,
                          'data': data,
                          'visible': True,
                          'cumulative': cumulative,     # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                else:
                    ts = {'name': str(year) + ' ' + ts_drawprops['tsname_in_legend'],
                          'type': ts_drawprops['charttype'],
                          'dashStyle': ts_drawprops['linestyle'],
                          'lineWidth': ts_drawprops['linewidth'],
                          'color': tsColor,
                          'xAxis': str(year),
                          'yAxis': ts_drawprops['yaxe_id'],
                          'data': data,
                          'visible': True,
                          'cumulative': cumulative,     # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)

        else:
            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()

            if cumulative:
                if to_date > datetime.date.today():
                    to_date = datetime.date.today()

            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)

            if len(data) > 0:
                data_available = True

            if ts_drawprops is None:
                # Set defaults in case no entry exists in the DB
                ts = {'name': productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            else:
                ts = {'name': ts_drawprops['tsname_in_legend'],
                      'type': ts_drawprops['charttype'],
                      'dashStyle': ts_drawprops['linestyle'],
                      'lineWidth': ts_drawprops['linewidth'],
                      'color': ts_drawprops['color'].replace("  ", " "),
                      'yAxis': ts_drawprops['yaxe_id'],
                      'data': data,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

    yaxes = []
    if passedyaxes is not None:
        for passedyaxe in passedyaxes:
            if passedyaxe['id'] in cum_yaxe:
                min = None
                max = None
            else:
                min = passedyaxe['min']
                max = passedyaxe['max']
            yaxe = {'id': passedyaxe['id'], 'title': passedyaxe['title'], 'title_color': passedyaxe['title_color'].replace("  ", " "),
                    'title_font_size': passedyaxe['title_font_size'], 'unit': passedyaxe['unit'], 'opposite': passedyaxe['opposite'],
                    'min': min, 'max': max,
                    'aggregation_type': passedyaxe['aggregation_type'],
                    'aggregation_min': passedyaxe['aggregation_min'],
                    'aggregation_max': passedyaxe['aggregation_max']}
            yaxes.append(yaxe)
    else:
        timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries, userid, istemplate, graphtype, graph_tpl_id, graph_tpl_name)
        # axes = len(timeseries_yaxes)
        # count = 0
        for yaxe in timeseries_yaxes:
            # count += 1
            # opposite = "false"
            # # if axes >= 2 and count % 2 == 0:   # and yaxe.opposite == "f"
            # #     opposite = "false"
            # # if axes >= 2 and count % 2 != 0:   # and yaxe.opposite == "t"
            # #     opposite = "true"
            # if axes >= 2:
            #     if yaxe.opposite:
            #         opposite = "true"
            # if axes == 1:
            #     opposite = "false"

            if yaxe.yaxe_id in cum_yaxe:
                min = None
                max = None
            else:
                min = yaxe.min
                max = yaxe.max
            yaxe = {'id': yaxe.yaxe_id, 'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "),
                    'title_font_size': yaxe.title_font_size, 'unit': yaxe.unit, 'opposite': yaxe.opposite,
                    'min': min, 'max': max,
                    'aggregation_type': yaxe.aggregation_type,
                    'aggregation_min': yaxe.aggregation_min,
                    'aggregation_max': yaxe.aggregation_max}
            yaxes.append(yaxe)

    ts_json = {"data_available": data_available,
               "showYearInTicks": showYearInTicks,
               "showYearInToolTip": "true",
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json, ensure_ascii=False, sort_keys=True, separators=(', ', ': '))

    return ts_json


def __classicTimeseries(params):
    # params = web.input()
    yearts = params.yearTS
    wkt = params.WKT
    requestedtimeseries = json.loads(params.selectedTimeseries)
    tsFromPeriod = params.tsFromPeriod
    tsToPeriod = params.tsToPeriod
    yearsToCompare = params.yearsToCompare
    tsFromSeason = params.tsFromSeason
    tsToSeason = params.tsToSeason
    showYearInTicks = True
    data_available = False
    cumulative = False
    if params.graphtype == 'cumulative':
         cumulative = True

    # if isinstance(yearsToCompare, basestring):  # One year passed but is not a list so make it a list.
    #     # yearsToCompare = list(yearsToCompare)
    #     yearsToCompare = []
    #     yearsToCompare.append(getparams.yearsToCompare)

    if tsFromSeason != '' and tsToSeason != '' and yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) == 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

    elif yearsToCompare != '':
        yearsToCompare = json.loads(yearsToCompare)
        showYearInTicks = False
        if len(yearsToCompare) == 1:
            for year in yearsToCompare:
                from_date = datetime.date(int(year), 01, 01)
                to_date = datetime.date(int(year), 12, 31)

    elif params.yearTS != '':
        if tsFromSeason != '' and tsToSeason != '':
            if tsToSeason != '':
                from_date = datetime.date(int(params.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params.yearTS), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(params.yearTS)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))
            else:
                from_date = datetime.date(int(params.yearTS), int(tsFromSeason[:2]), int(tsFromSeason[3:]))
                to_date = datetime.date(int(params.yearTS), 12, 31)
        else:
            from_date = datetime.date(int(params.yearTS), 01, 01)
            to_date = datetime.date(int(params.yearTS), 12, 31)
        showYearInTicks = False

    elif tsFromPeriod != '' and tsToPeriod != '':
        from_date = datetime.datetime.strptime(tsFromPeriod, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(tsToPeriod, '%Y-%m-%d').date()


    cum_yaxe = []
    timeseries = []
    for timeserie in requestedtimeseries:
        productcode = timeserie['productcode']
        subproductcode = timeserie['subproductcode']
        version = timeserie['version']
        mapsetcode = timeserie['mapsetcode']
        date_format = timeserie['date_format']

        product = {"productcode": productcode,
                   "subproductcode": subproductcode,
                   "version": version}

        # Set defaults in case no entry exists in the DB
        aggregate = { 'aggregation_type': 'mean',
                      'aggregation_min': None,
                      'aggregation_max': None }
        timeseries_drawproperties = querydb.get_product_timeseries_drawproperties(product)
        for ts_drawprops in timeseries_drawproperties:
            aggregate = { 'aggregation_type': ts_drawprops.aggregation_type,
                          'aggregation_min': ts_drawprops.aggregation_min,
                          'aggregation_max': ts_drawprops.aggregation_max}

            # if timeserie['cumulative']:
            if cumulative:
                cum_yaxe.append(ts_drawprops.yaxes_id)

        mapset_info = querydb.get_mapset(mapsetcode=mapsetcode)
        product_info = querydb.get_product_out_info(productcode=productcode,
                                                    subproductcode=subproductcode,
                                                    version=version)

        if date_format == 'MMDD' and len(yearsToCompare) > 1:
            year = yearsToCompare[0]
            showYearInTicks = False
            from_date = datetime.date(year, 01, 01)
            to_date = datetime.date(year, 12, 31)

            if tsFromSeason != '' and tsToSeason != '':
                from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                    to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)
            if len(data) > 0:
                data_available = True

            # Set defaults in case no entry exists in the DB
            ts = {'name': productcode + '-' + version + '-' + subproductcode,
                  'type': 'line',
                  'dashStyle': 'Solid',
                  'lineWidth': 2,
                  'color': '#000000',
                  # 'xAxis': str(year),
                  'yAxis': productcode + ' - ' + version,
                  'data': data,
                  'visible': True,
                  'cumulative': cumulative,     # timeserie['cumulative'],
                  'difference': timeserie['difference'],
                  'reference': timeserie['reference']
                  }
            for ts_drawprops in timeseries_drawproperties:
                # print ts_drawprops.color
                ts = {'name': ts_drawprops.tsname_in_legend,
                      'type': ts_drawprops.charttype,
                      'dashStyle': ts_drawprops.linestyle,
                      'lineWidth': ts_drawprops.linewidth,
                      'color': ts_drawprops.color.replace("  ", " "),
                      # 'xAxis': str(year),
                      'yAxis': ts_drawprops.yaxes_id,
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)

        elif len(yearsToCompare) > 1:     # yearsToCompare != '' or
            # yearsToCompare = json.loads(yearsToCompare)
            colorAdd = 0
            colorSubstract = 0
            for year in yearsToCompare:
                showYearInTicks = False
                from_date = datetime.date(int(year), 01, 01)
                to_date = datetime.date(int(year), 12, 31)

                if tsFromSeason != '' and tsToSeason != '':
                    from_date = datetime.date(int(year), int(tsFromSeason[:2]), int(tsFromSeason[3:]))  # year month day
                    to_date = datetime.date(int(year), int(tsToSeason[:2]), int(tsToSeason[3:]))
                    if int(tsToSeason[:2]) < int(tsFromSeason[:2]):  # season over 2 years
                        to_date = datetime.date(int(year)+1, int(tsToSeason[:2]), int(tsToSeason[3:]))

                if ts_drawprops.color[0] == '#':        # Transform HTML HEX color code to RGB
                    h = ts_drawprops.color.lstrip('#')
                    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
                    rgb = list(rgb)
                else:
                    # print ts_drawprops.color
                    # rgb = ts_drawprops.color.replace("  ", " ").split(' ')
                    if (functions.isValidRGB(ts_drawprops.color.replace("  ", " "))):
                        rgb = ts_drawprops.color.replace("  ", " ").split(' ')
                    else:
                        # RGB value stored in the database is not correct so define as default value BLACK.
                        rgb = "0 0 0".split(' ')
                # print rgb
                rgb = map(int,rgb)
                rgb[-1] = rgb[-1]+colorAdd
                rgb[-2] = rgb[-2]+colorAdd
                rgb[-3] = rgb[-3]-colorSubstract
                tsColor = ' '.join([str(i) for i in rgb])
                colorAdd += 65
                colorSubstract += 50

                # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
                # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
                # p = Process(target=getTimeseries, args=args)
                # p.start()
                # p.join()
                # list_values = self.out_queue.get()
                # self.out_queue.empty()
                list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

                data = []
                for val in list_values:
                    value = []
                    # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                    valdate = functions.unix_time_millis(val['date'])
                    # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                    value.append(valdate)
                    value.append(val['meanvalue'])
                    data.append(value)
                if len(data) > 0:
                    data_available = True

                # Set defaults in case no entry exists in the DB
                ts = {'name': str(year) + ' ' + productcode + '-' + version + '-' + subproductcode,
                      'type': 'line',
                      'dashStyle': 'Solid',
                      'lineWidth': 2,
                      'color': '#000000',
                      'xAxis': str(year),
                      'yAxis': productcode + ' - ' + version,
                      'data': data,
                      'visible': True,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
                for ts_drawprops in timeseries_drawproperties:
                    ts = {'name': str(year) + ' ' + ts_drawprops.tsname_in_legend,
                          'type': ts_drawprops.charttype,
                          'dashStyle': ts_drawprops.linestyle,
                          'lineWidth': ts_drawprops.linewidth,
                          'color': tsColor,
                          'xAxis': str(year),
                          'yAxis': ts_drawprops.yaxes_id,
                          'data': data,
                          'visible': True,
                          'cumulative': cumulative,     # timeserie['cumulative'],
                          'difference': timeserie['difference'],
                          'reference': timeserie['reference']
                          }
                timeseries.append(ts)

        else:
            # [list_files, dates_list] = getFilesList(productcode, subproductcode, version, mapsetcode, date_format, from_date, to_date)
            # args = [self.out_queue, productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate, mapset_info, product_info, list_files, dates_list]
            # p = Process(target=getTimeseries, args=args)
            # p.start()
            # p.join()
            # list_values = self.out_queue.get()
            list_values = getTimeseries(productcode, subproductcode, version, mapsetcode, wkt, from_date, to_date, aggregate)

            data = []
            for val in list_values:
                value = []
                # valdate = 'Date.UTC(' + str(val['date'].year) + ',' + str(val['date'].month) + ',' + str(val['date'].day) + ')'
                valdate = functions.unix_time_millis(val['date'])
                # valdate = str(val['date'].year) + str(val['date'].month) + str(val['date'].day)
                value.append(valdate)
                value.append(val['meanvalue'])
                data.append(value)

            if len(data) > 0:
                data_available = True

            # Set defaults in case no entry exists in the DB
            ts = {'name': productcode + '-' + version + '-' + subproductcode,
                  'type': 'line',
                  'dashStyle': 'Solid',
                  'lineWidth': 2,
                  'color': '#000000',
                  'yAxis': productcode + ' - ' + version,
                  'data': data,
                  'cumulative': cumulative,     # timeserie['cumulative'],
                  'difference': timeserie['difference'],
                  'reference': timeserie['reference']
                  }
            for ts_drawprops in timeseries_drawproperties:
                # print ts_drawprops.color
                ts = {'name': ts_drawprops.tsname_in_legend,
                      'type': ts_drawprops.charttype,
                      'dashStyle': ts_drawprops.linestyle,
                      'lineWidth': ts_drawprops.linewidth,
                      'color': ts_drawprops.color.replace("  ", " "),
                      'yAxis': ts_drawprops.yaxes_id,
                      'data': data,
                      'cumulative': cumulative,     # timeserie['cumulative'],
                      'difference': timeserie['difference'],
                      'reference': timeserie['reference']
                      }
            timeseries.append(ts)


    yaxes = []
    count = 0
    timeseries_yaxes = querydb.get_timeseries_yaxes(requestedtimeseries)
    axes = len(timeseries_yaxes)
    for yaxe in timeseries_yaxes:
        # count += 1
        # opposite = "false"
        # # if axes >= 2 and count % 2 == 0:   # and yaxe.opposite == "f"
        # #     opposite = "false"
        # # if axes >= 2 and count % 2 != 0:   # and yaxe.opposite == "t"
        # #     opposite = "true"
        # if axes >= 2:
        #     if yaxe.opposite:
        #         opposite = "true"
        # if axes == 1:
        #     opposite = "false"

        if yaxe.yaxes_id in cum_yaxe:
            min = ''
            max = ''
        else:
            min = yaxe.min
            max = yaxe.max
        yaxe = {'id': yaxe.yaxes_id, 'title': yaxe.title, 'title_color': yaxe.title_color.replace("  ", " "), 'unit': yaxe.unit, 'opposite': yaxe.opposite,
                'min': min, 'max': max, 'aggregation_type': yaxe.aggregation_type, 'aggregation_min': yaxe.aggregation_min, 'aggregation_max': yaxe.aggregation_max}
        yaxes.append(yaxe)



    ts_json = {"data_available": data_available,
               "showYearInTicks": showYearInTicks,
               "showYearInToolTip": "true",
               "yaxes": yaxes,
               "timeseries": timeseries}

    ts_json = json.dumps(ts_json,
                         ensure_ascii=False,
                         sort_keys=True,
                         # indent=4,
                         separators=(', ', ': '))

    # print ts_json
    # timeseries_json = '{"success":"true", "total":' + str(timeline.__len__()) + ',"timeline":'+timeline_json+'}'
    # timeline_json = '{"success":"true"}'
    return ts_json


def updateGraphProperties(params, graphtpl_info):
    updatestatus = '{"success":false, "message":"An error occured while updating the graph draw properties!"}'

    if 'graphproperty' in params:  # hasattr(getparams, "graphproperty")
        graphdrawprobs = params['graphproperty']

        try:
            querydb.update_user_graph_tpl_drawproperties(graphdrawprobs, graphtpl_info)
            updatestatus = '{"success":true, "message":"Graph draw properties updated!"}'
        except:
            updatestatus = '{"success":false, "error":"Error saving the Graph Draw Properties in the database!"}'

    else:
        updatestatus = '{"success":false, "message":"No graph properties given!"}'

    return updatestatus


def __updateChartProperties(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'chartproperty' in params:  # hasattr(getparams, "chartproperty")
        chartdrawprobs = {'chart_type': params['chartproperty']['chart_type'],
                          'chart_width': params['chartproperty']['chart_width'],
                          'chart_height': params['chartproperty']['chart_height'],
                          'chart_title_font_size': params['chartproperty']['chart_title_font_size'],
                          'chart_title_font_color': params['chartproperty']['chart_title_font_color'],
                          'chart_subtitle_font_size': params['chartproperty']['chart_subtitle_font_size'],
                          'chart_subtitle_font_color': params['chartproperty']['chart_subtitle_font_color'],
                          'yaxe1_font_size': params['chartproperty']['yaxe1_font_size'],
                          'yaxe2_font_size': params['chartproperty']['yaxe2_font_size'],
                          'legend_font_size': params['chartproperty']['legend_font_size'],
                          'legend_font_color': params['chartproperty']['legend_font_color'],
                          'xaxe_font_size': params['chartproperty']['xaxe_font_size'],
                          'xaxe_font_color': params['chartproperty']['xaxe_font_color'],
                          'yaxe3_font_size': params['chartproperty']['yaxe3_font_size']
                          }

        if crud_db.update('chart_drawproperties', chartdrawprobs):
            updatestatus = '{"success":"true", "message":"Chart draw properties updated!"}'
        else:
            updatestatus = '{"success":false, "message":"An error occured while updating the chart draw properties!"}'

    else:
        updatestatus = '{"success":false, "message":"No chart properties passed!"}'

    return updatestatus


def getGraphProperties(params):
    if hasattr(params, "graphtype") and params['graphtype'] == '':
        params['graphtype'] = 'default'

    graphproperties_dict_all = []
    graphproperties = querydb.get_graph_drawproperties(params)

    if hasattr(graphproperties, "__len__") and graphproperties.__len__() > 0:
        for row in graphproperties:
            # row_dict = functions.row2dict(row)
            row_dict = row

            graphproperty = {'graph_tpl_id': row_dict['graph_tpl_id'],
                             'graph_type': row_dict['graph_type'],
                             'graph_width': row_dict['graph_width'],
                             'graph_height': row_dict['graph_height'],
                             'graph_title': row_dict['graph_title'],
                             'graph_title_font_size': row_dict['graph_title_font_size'],
                             'graph_title_font_color': row_dict['graph_title_font_color'],
                             'graph_subtitle': row_dict['graph_subtitle'],
                             'graph_subtitle_font_size': row_dict['graph_subtitle_font_size'],
                             'graph_subtitle_font_color': row_dict['graph_subtitle_font_color'],
                             'legend_position': row_dict['legend_position'],
                             'legend_font_size': row_dict['legend_font_size'],
                             'legend_font_color': row_dict['legend_font_color'],
                             'xaxe_font_size': row_dict['xaxe_font_size'],
                             'xaxe_font_color': row_dict['xaxe_font_color']
                             }

            graphproperties_dict_all.append(graphproperty)

        graphproperties_json = json.dumps(graphproperties_dict_all,
                                          ensure_ascii=False,
                                          encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

        graphproperties_json = '{"success":"true", "total":' \
                               + str(graphproperties.__len__()) \
                               + ',"graphproperties":' + graphproperties_json + '}'

    else:
        graphproperties_json = '{"success":false, "error":"No graph properties defined!"}'

    return graphproperties_json


def __getChartProperties(params):
    charttype = 'default'
    if hasattr(params, "charttype") and params['charttype'] != '':
        charttype = params['charttype']

    chartproperties_dict_all = []
    chartproperties = querydb.get_chart_drawproperties(charttype)

    if hasattr(chartproperties, "__len__") and chartproperties.__len__() > 0:
        for row in chartproperties:
            row_dict = functions.row2dict(row)

            chartproperty = {'chart_type': row_dict['chart_type'],
                             'chart_width': row_dict['chart_width'],
                             'chart_height': row_dict['chart_height'],
                             'chart_title_font_size': row_dict['chart_title_font_size'],
                             'chart_title_font_color': row_dict['chart_title_font_color'],
                             'chart_subtitle_font_size': row_dict['chart_subtitle_font_size'],
                             'chart_subtitle_font_color': row_dict['chart_subtitle_font_color'],
                             'yaxe1_font_size': row_dict['yaxe1_font_size'],
                             'yaxe2_font_size': row_dict['yaxe2_font_size'],
                             'yaxe3_font_size': row_dict['yaxe3_font_size'],
                             'yaxe4_font_size': row_dict['yaxe4_font_size'],
                             'legend_font_size': row_dict['legend_font_size'],
                             'legend_font_color': row_dict['legend_font_color'],
                             'xaxe_font_size': row_dict['xaxe_font_size'],
                             'xaxe_font_color': row_dict['xaxe_font_color']
                             }

            chartproperties_dict_all.append(chartproperty)

        chartproperties_json = json.dumps(chartproperties_dict_all,
                                          ensure_ascii=False,
                                          encoding='utf-8',
                                          sort_keys=True,
                                          indent=4,
                                          separators=(', ', ': '))

        chartproperties_json = '{"success":"true", "total":' \
                               + str(chartproperties.__len__()) \
                               + ',"chartproperties":' + chartproperties_json + '}'

    else:
        chartproperties_json = '{"success":false, "error":"No chart properties defined!"}'

    return chartproperties_json


def updateTimeseriesDrawProperties(params):
    # crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
    updatestatus = '{"success":"false", "message":"An error occured while updating the Timeseries Draw Properties!"}'

    if params.productcode != '':
        tsdrawproperties = params  # getparams['tsdrawproperties']

        try:
            querydb.update_user_tpl_timeseries_drawproperties(tsdrawproperties)
            updatestatus = '{"success":true, "message":"Timeseries Draw Properties updated!"}'
        except:
            updatestatus = '{"success":false, "error":"Error saving the Timeseries Draw Properties in the database!"}'

        # if crud_db.update('timeseries_drawproperties', tsdrawproperties):
        #     updatestatus = '{"success":"true", "message":"Timeseries Draw Properties updated!"}'
    else:
        updatestatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

    return updatestatus


def createTimeseriesDrawProperties(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    createstatus = '{"success":"false", "message":"An error occured while creating the Timeseries Draw Properties!"}'

    # if hasattr(getparams['tsdrawproperties'], "yaxes_id"):
    if 'tsdrawproperties' in params:
        tsdrawproperties = params['tsdrawproperties']

        if crud_db.create('timeseries_drawproperties_new', tsdrawproperties):
            createstatus = '{"success":"true", "message":"Timeseries Draw Properties created!"}'
    else:
        createstatus = '{"success":"false", "message":"No Timeseries Draw Properties given!"}'

    return createstatus


def getTimeseriesDrawProperties(params):
    tsdrawproperties_dict_all = []
    tsdrawproperties = querydb.get_timeseries_drawproperties(params)

    if hasattr(tsdrawproperties, "__len__") and tsdrawproperties.__len__() > 0:
        for row in tsdrawproperties:
            # row_dict = functions.row2dict(row)
            row_dict = row

            tsdrawproperty = {
                'productcode': row_dict['productcode'],
                'subproductcode': row_dict['subproductcode'],
                'version': row_dict['version'],
                'tsname_in_legend': row_dict['tsname_in_legend'],
                'charttype': row_dict['charttype'],
                'linestyle': row_dict['linestyle'],
                'linewidth': row_dict['linewidth'],
                'color': row_dict['color'],
                'yaxe_id': row_dict['yaxe_id']
            }

            tsdrawproperties_dict_all.append(tsdrawproperty)

        tsdrawproperties_json = json.dumps(tsdrawproperties_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

        tsdrawproperties_json = '{"success":"true", "total":' \
                                + str(tsdrawproperties.__len__()) \
                                + ',"tsdrawproperties":' + tsdrawproperties_json + '}'

    else:
        tsdrawproperties_json = '{"success":false, "error":"No timeseries draw properties defined!"}'

    return tsdrawproperties_json


def __getTimeseriesDrawProperties():
    tsdrawproperties_dict_all = []
    tsdrawproperties = querydb.get_timeseries_drawproperties()

    if hasattr(tsdrawproperties, "__len__") and tsdrawproperties.__len__() > 0:
        for row in tsdrawproperties:
            # row_dict = functions.row2dict(row)
            row_dict = row

            tsdrawproperty = {
                'productcode': row_dict['productcode'],
                'subproductcode': row_dict['subproductcode'],
                'version': row_dict['version'],
                'title': row_dict['title'],
                'unit': row_dict['unit'],
                'min': row_dict['min'],
                'max': row_dict['max'],
                'oposite': row_dict['oposite'],
                'tsname_in_legend': row_dict['tsname_in_legend'],
                'charttype': row_dict['charttype'],
                'linestyle': row_dict['linestyle'],
                'linewidth': row_dict['linewidth'],
                'color': row_dict['color'],
                'yaxes_id': row_dict['yaxes_id'],
                'title_color': row_dict['title_color'],
                'aggregation_type': row_dict['aggregation_type'],
                'aggregation_min': row_dict['aggregation_min'],
                'aggregation_max': row_dict['aggregation_max']
            }

            tsdrawproperties_dict_all.append(tsdrawproperty)

        tsdrawproperties_json = json.dumps(tsdrawproperties_dict_all,
                                           ensure_ascii=False,
                                           encoding='utf-8',
                                           sort_keys=True,
                                           indent=4,
                                           separators=(', ', ': '))

        tsdrawproperties_json = '{"success":"true", "total":' \
                                + str(tsdrawproperties.__len__()) \
                                + ',"tsdrawproperties":' + tsdrawproperties_json + '}'

    else:
        tsdrawproperties_json = '{"success":false, "error":"No timeseries draw properties defined!"}'

    return tsdrawproperties_json


def getProductLayer(getparams):
    import mapscript
    # To solve issue with Chla Legends (Tuleap ticket #10905 - see http://trac.osgeo.org/mapserver/ticket/1762)
    import locale
    locale.setlocale(locale.LC_NUMERIC, 'C')

    p = Product(product_code=getparams['productcode'], version=getparams['productversion'])
    dataset = p.get_dataset(mapset=getparams['mapsetcode'], sub_product_code=getparams['subproductcode'])
    # print dataset.fullpath

    if hasattr(getparams, "date"):
        filedate = getparams['date']
    else:
        dataset.get_filenames()
        lastdate = dataset.get_dates()[-1].strftime("%Y%m%d")
        filedate = lastdate

    if dataset.no_year():
        filedate=dataset.strip_year(filedate)

    # Check the case of daily product, with time/minutes
    frequency_id = dataset._db_product.frequency_id
    date_format = dataset._db_product.date_format


    if frequency_id=='e1day' and date_format=='YYYYMMDD':
        regex = dataset.fullpath + filedate+'*'+'.tif'
        filename = glob.glob(regex)
        productfile = filename[0]
    # lastdate = lastdate.replace("-", "")
    # mydate=lastdate.strftime("%Y%m%d")
    else:
        filename = functions.set_path_filename(filedate,
                                               getparams['productcode'],
                                               getparams['subproductcode'],
                                               getparams['mapsetcode'],
                                               getparams['productversion'],
                                               '.tif')
        productfile = dataset.fullpath + filename

    # if (hasattr(getparams, "outmask") and getparams['outmask'] == 'true'):
    #     # print productfile
    #     # print es_constants.base_tmp_dir
    #     from greenwich import Raster, Geometry
    #
    #     # try:
    #     #     from osgeo import gdal
    #     #     from osgeo import gdal_array
    #     #     from osgeo import ogr, osr
    #     #     from osgeo import gdalconst
    #     # except ImportError:
    #     #     import gdal
    #     #     import gdal_array
    #     #     import ogr
    #     #     import osr
    #     #     import gdalconst
    #
    #     # try:
    #
    #     # ogr.UseExceptions()
    #     wkt = getparams['selectedfeature']
    #     theGeomWkt = ' '.join(wkt.strip().split())
    #     # print wkt
    #     geom = Geometry(wkt=str(theGeomWkt), srs=4326)
    #     # print "wearehere"
    #     with Raster(productfile) as img:
    #         # Assign nodata from prod_info
    #         # img._nodata = nodata
    #         # print "nowwearehere"
    #         with img.clip(geom) as clipped:
    #             # Save clipped image (for debug only)
    #             productfile = es_constants.base_tmp_dir + '/clipped_'+filename
    #             # print productfile
    #             clipped.save(productfile)
    #
    #     # except:
    #     #     print 'errorrrrrrrrr!!!!!!'
    #
    #web.header('Content-type', 'image/png')
    #web.header('Content-transfer-encoding', 'binary')
    #buf = StringIO.StringIO()
    #mapscript.msIO_installStdoutToBuffer()
    #map = mapserver.getmap()
    ##map.save to a file fname.png
    ##web.header('Content-Disposition', 'attachment; filename="fname.png"')
    #contents = buf.getvalue()
    #return contents

    # #logger.debug("MapServer: Installing stdout to buffer.")
    # mapscript.msIO_installStdoutToBuffer()
    #
    # owsrequest = mapscript.OWSRequest()
    #
    # inputparams = web.input()
    # for k, v in inputparams.iteritems():
    #     print k + ':' + v
    #     if k not in ('productcode', 'subproductcode', 'mapsetcode', 'productversion', 'legendid', 'date' 'TRANSPARENT'):
    #         # if k == 'CRS':
    #         #     owsrequest.setParameter('SRS', v)
    #         owsrequest.setParameter(k.upper(), v)
    #
    # #owsrequest.setParameter(k.upper(), v)


    # projlib = "/usr/share/proj/"

    projlib = es_constants.proj4_lib_dir
    # errorfile = es_constants.apps_dir+"/analysis/ms_tmp/ms_errors.log"
    errorfile = es_constants.log_dir+"/mapserver_error.log"
    # imagepath = es_constants.apps_dir+"/analysis/ms_tmp/"

    inputparams = getparams

    filenamenoextention = functions.set_path_filename(filedate,
                                           getparams['productcode'],
                                           getparams['subproductcode'],
                                           getparams['mapsetcode'],
                                           getparams['productversion'],
                                           '')
    # owsrequest.setParameter("LAYERS", filenamenoextention)
    # owsrequest.setParameter("UNIT", mapscript.MS_METERS)

    productmap = mapscript.mapObj(es_constants.template_mapfile)
    productmap.setConfigOption("PROJ_LIB", projlib)
    productmap.setConfigOption("MS_ERRORFILE", errorfile)
    productmap.maxsize = 4096

    outputformat_png = mapscript.outputFormatObj('GD/PNG', 'png')
    outputformat_png.setOption("INTERLACE", "OFF")
    productmap.appendOutputFormat(outputformat_png)
    # outputformat_gd = mapscript.outputFormatObj('GD/GIF', 'gif')
    # productmap.appendOutputFormat(outputformat_gd)
    productmap.selectOutputFormat('png')
    # productmap.debug = mapscript.MS_TRUE
    productmap.debug = 5
    productmap.status = mapscript.MS_ON
    productmap.units = mapscript.MS_DD

    coords = map(float, inputparams['BBOX'].split(","))
    lly = coords[0]
    llx = coords[1]
    ury = coords[2]
    urx = coords[3]
    productmap.setExtent(llx, lly, urx, ury)   # -26, -35, 60, 38
    # productmap.setExtent(lly, llx, ury, urx)   # -26, -35, 60, 38
    # print llx, lly, urx, ury

    # epsg must be in lowercase because in unix/linux systems the proj filenames are lowercase!
    # epsg = "+init=epsg:3857"
    # epsg = "+init=" + inputparams.CRS.lower()   # CRS = "EPSG:4326"
    epsg = inputparams['CRS'].lower()   # CRS = "EPSG:4326"
    productmap.setProjection(epsg)

    w = int(inputparams['WIDTH'])
    h = int(inputparams['HEIGHT'])
    productmap.setSize(w, h)

    # General web service information
    productmap.setMetaData("WMS_TITLE", "Product description")
    productmap.setMetaData("WMS_SRS", inputparams['CRS'].lower())
    # productmap.setMetaData("WMS_SRS", "epsg:3857")
    productmap.setMetaData("WMS_ABSTRACT", "A Web Map Service returning eStation2 raster layers.")
    productmap.setMetaData("WMS_ENABLE_REQUEST", "*")   # necessary!!

    product_info = querydb.get_product_out_info(productcode=inputparams['productcode'],
                                                subproductcode=inputparams['subproductcode'],
                                                version=inputparams['productversion'])
    if hasattr(product_info, "__len__") and product_info.__len__() > 0:
        for row in product_info:
            scale_factor = row.scale_factor
            scale_offset = row.scale_offset
            nodata = row.nodata

    legend_info = querydb.get_legend_info(legendid=inputparams['legendid'])
    if hasattr(legend_info, "__len__") and legend_info.__len__() > 0:
        for row in legend_info:
            minstep = float((row.min_value - scale_offset)/scale_factor)    #int(row.min_value*scale_factor+scale_offset)
            maxstep = float((row.max_value - scale_offset)/scale_factor)    # int(row.max_value*scale_factor+scale_offset)
            realminstep = float((row.realminstep - scale_offset)/scale_factor)
            realmaxstep = float((row.realmaxstep - scale_offset)/scale_factor)
            minstepwidth = float((row.minstepwidth - scale_offset)/scale_factor)
            maxstepwidth = float((row.maxstepwidth - scale_offset)/scale_factor)
            totwidth = float((row.totwidth - scale_offset)/scale_factor)
            totsteps = row.totsteps

        # maxstep = 255
        processing_scale = 'SCALE='+str(minstep)+','+str(maxstep)  # min(legend_step.from_step) max(legend_step.to_step) example: 'SCALE=-7000,10000'

        minbuckets = 256
        maxbuckets = 5000
        num_buckets = maxbuckets
        if minstepwidth > 0:
            num_buckets = round(totwidth / minstepwidth, 0)

        if num_buckets < minbuckets:
            num_buckets = minbuckets
        elif num_buckets > maxbuckets:
            num_buckets = maxbuckets

        # num_buckets = 10000
        if num_buckets > 0:
            processing_buckets = 'SCALE_BUCKETS='+str(num_buckets)

        # nodata = -32768     # get this value from the table products.product
        processing_novalue = ''
        if nodata is not None and minstep <= nodata < maxstep:
            processing_novalue = 'NODATA='+str(nodata)

        layer = mapscript.layerObj(productmap)
        layer.name = filenamenoextention
        layer.type = mapscript.MS_LAYER_RASTER
        layer.status = mapscript.MS_ON     # MS_DEFAULT
        layer.data = productfile
        layer.units = mapscript.MS_METERS
        # layer.setProjection("+init=epsg:4326")
        layer.setProjection("epsg:4326")
        layer.dump = mapscript.MS_TRUE

        # scale & buckets
        if num_buckets > 0:
            layer.setProcessing(processing_scale)
            layer.setProcessing(processing_buckets)

        if processing_novalue != '':
            layer.setProcessing(processing_novalue)

        resample_processing = "RESAMPLE=AVERAGE"
        layer.setProcessing(resample_processing)

        legend_steps = querydb.get_legend_steps(legendid=inputparams['legendid'])
        if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
            stepcount = 0
            for step in legend_steps:
                stepcount += 1
                min_step = float((step.from_step - scale_offset)/scale_factor)
                max_step = float((step.to_step - scale_offset)/scale_factor)
                # min_step = float(step.from_step)
                # max_step = float(step.to_step)
                colors = map(int, (color.strip() for color in step.color_rgb.split(" ") if color.strip()))

                if stepcount == legend_steps.__len__():    # For the last step use <= max_step
                    expression_string = '([pixel] >= '+str(min_step)+' and [pixel] <= '+str(max_step)+')'
                else:
                    expression_string = '([pixel] >= '+str(min_step)+' and [pixel] < '+str(max_step)+')'
                # define class object and style
                layerclass = mapscript.classObj(layer)
                layerclass.name = layer.name+'_'+str(stepcount)
                layerclass.setExpression(expression_string)
                style = mapscript.styleObj(layerclass)
                style.color.setRGB(colors[0], colors[1], colors[2])

    # result_map_file = '/tmp/eStation2/MAP_result.map'
    # if os.path.isfile(result_map_file):
    #     os.remove(result_map_file)
    # productmap.save(result_map_file)

    image = productmap.draw()
    filename_png = es_constants.base_tmp_dir+filenamenoextention+str(llx)+'_'+str(lly)+'_'+str(urx)+'_'+str(ury)+'.png'
    image.save(filename_png)

    return filename_png

    # web.header('Content-type', 'image/png')
    # f = open(filename_png, 'rb')
    # while 1:
    #     buf = f.read(1024 * 8)
    #     if not buf:
    #         break
    #     yield buf
    # f.close()
    # os.remove(filename_png)

    # #print owsrequest.getValueByName('BBOX')
    # mapscript.msIO_installStdoutToBuffer()
    # contents = productmap.OWSDispatch(owsrequest)
    # content_type = mapscript.msIO_stripStdoutBufferContentType()
    # content = mapscript.msIO_getStdoutBufferBytes()
    # #web.header = "Content-Type","%s; charset=utf-8"%content_type
    # web.header('Content-type', 'image/png')
    # #web.header('Content-transfer-encoding', 'binary')
    # return content


def GetAssignedDatasets(legendid):
    assigned_datasets_dict_all = []
    legend_assigned_datasets = querydb.get_legend_assigned_datasets(legendid=legendid)

    if hasattr(legend_assigned_datasets, "__len__") and legend_assigned_datasets.__len__() > 0:
        for assigned_dataset in legend_assigned_datasets:
            # row_dict = functions.row2dict(assigned_dataset)
            row_dict = assigned_dataset

            assigned_dataset_dict = {'legend_id': row_dict['legend_id'],
                                     'productcode': row_dict['productcode'],
                                     'subproductcode': row_dict['subproductcode'],
                                     'version': row_dict['version'],
                                     'default_legend': row_dict['default_legend'],
                                     'descriptive_name': row_dict['descriptive_name'],
                                     'description': row_dict['description']
                                    }

            assigned_datasets_dict_all.append(assigned_dataset_dict)

        assigned_datasets_json = json.dumps(assigned_datasets_dict_all,
                                            ensure_ascii=False,
                                            encoding='utf-8',
                                            sort_keys=True,
                                            indent=4,
                                            separators=(', ', ': '))

        assigned_datasets_json = '{"success":true, "total":' + str(legend_assigned_datasets.__len__()) + ',"assigneddatasets":' + assigned_datasets_json + '}'

    else:
        assigned_datasets_json = '{"success":true, "message":"No products assigned!"}'

    return assigned_datasets_json


def UnassignLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legendid' in params:

        productlegend = {
            'productcode': params['productcode'],
            'subproductcode': params['subproductcode'],
            'version': params['productversion'],
            'legend_id': params['legendid']
        }

        if crud_db.delete('product_legend', **productlegend):
            message = '{"success":true, "message":"Legend unassigned from product!"}'
        else:
            message = '{"success":false, "message":"Error unassigning legend!"}'

    else:
        message = '{"success":false, "message":"No legendid given!"}'

    return message


def AssignLegends(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legendids' in params:
        legendIDS = json.loads(params['legendids'])
        # legendIDS = params['legendids']

        message = '{"success":false, "message":"Error assigning legends!"}'
        if len(legendIDS) > 0:
            for legendid in legendIDS:
                productlegend = {
                    'productcode': params['productcode'],
                    'subproductcode': params['subproductcode'],
                    'version': params['productversion'],
                    'legend_id': legendid,
                    'default_legend': False
                }

                if crud_db.create('product_legend', productlegend):
                    message = '{"success":true, "message":"Legends assigned!"}'
                else:
                    message = '{"success":false, "message":"Error assigning legends!"}'
                    break
        else:
            message = '{"success":false, "message":"No legend ids given!"}'
    else:
        message = '{"success":false, "message":"No legend ids given!"}'

    return message


def copyLegend(params):

    if 'legendid' in params:
        newlegendname = params['legend_descriptive_name'] + ' - copy'
        newlegendid = querydb.copylegend(legendid=params['legendid'], legend_descriptive_name=newlegendname)

        if newlegendid != -1:
            message = '{"success":true, "legendid": ' + str(newlegendid) + ', "legend_descriptive_name": "' + newlegendname + '","message":"Legend copied!"}'
        else:
            message = '{"success":false, "message":"Error copying the legend!"}'
    else:
        message = '{"success":false, "message":"No legend id given!"}'

    return message


def DeleteLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    if 'legend' in params:
        legend = {
            'legend_id': params['legend']['legendid']
        }

        if crud_db.delete('legend', **legend):
            message = '{"success":true, "legendid": ' + str(params['legend']['legendid']) + ',"message":"Legend deleted!"}'
        else:
            message = '{"success":false, "message":"Error deleting the legend!"}'
    else:
        message = '{"success":false, "message":"No legend id given!"}'

    return message


def SaveLegend(params):
    crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])

    # if hasattr(params, 'legendid'):
    if 'legendid' in params:
        legend = {
            'legend_id': params['legendid'],
            'colorbar': params['legend_descriptive_name'],
            'legend_name': params['title_in_legend'],
            'min_value': params['minvalue'],
            'max_value': params['maxvalue']
        }
        legendClasses = json.loads(params['legendClasses'])

        if int(params['legendid']) == -1:
            newlegendid = querydb.createlegend(legend)
            # if crud_db.create('legend', legend):
            if newlegendid != -1:
                message = '{"success":true, "legendid": ' + str(newlegendid) + ',"message":"Legend created!"}'
                for legendstep in legendClasses:
                    legendstep_dict = {'legend_id': newlegendid,
                                       'from_step': float(legendstep['from_step']),
                                       'to_step': float(legendstep['to_step']),
                                       'color_rgb': legendstep['color_rgb'],
                                       'color_label': legendstep['color_label'],
                                       'group_label': legendstep['group_label']
                                       }
                    if not crud_db.create('legend_step', legendstep_dict):
                        message = '{"success":false, "message":"Error saving a legend class of the new legend!"}'
                        break
            else:
                message = '{"success":false, "message":"Error saving the new legend!"}'
        else:
            if crud_db.update('legend', legend):
                if querydb.deletelegendsteps(params['legendid']):

                    message = '{"success":true, "legendid": ' + params['legendid'] + ',"message":"Legend updated!"}'
                    for legendstep in legendClasses:
                        legendstep_dict = {'legend_id': int(params['legendid']),
                                           'from_step': float(legendstep['from_step']),
                                           'to_step': float(legendstep['to_step']),
                                           'color_rgb': legendstep['color_rgb'],
                                           'color_label': legendstep['color_label'],
                                           'group_label': legendstep['group_label']
                                           }
                        if not crud_db.create('legend_step', legendstep_dict):
                            message = '{"success":false, "message":"Error creating for updating a legend class of the legend!"}'
                            break
                else:
                    message = '{"success":false, "message":"Error deleting the legend steps!"}'
            else:
                message = '{"success":false, "message":"Error updating the legend!"}'
    else:
        message = '{"success":false, "message":"No legend data given!"}'

    return message


def GetLegendClasses(legendid):
    legendsteps_dict_all = []
    legend_steps = querydb.get_legend_steps(legendid=legendid)

    if hasattr(legend_steps, "__len__") and legend_steps.__len__() > 0:
        for legendstep in legend_steps:
            row_dict = functions.row2dict(legendstep)
            # row_dict = legendstep

            legendstep_dict = {'legend_id': row_dict['legend_id'],
                               'from_step': row_dict['from_step'],
                               'to_step': row_dict['to_step'],
                               'color_rgb': row_dict['color_rgb'],
                               'color_label': row_dict['color_label'],
                               'group_label': row_dict['group_label']
                              }

            legendsteps_dict_all.append(legendstep_dict)

        legendsteps_json = json.dumps(legendsteps_dict_all,
                                 ensure_ascii=False,
                                 encoding='utf-8',
                                 sort_keys=True,
                                 indent=4,
                                 separators=(', ', ': '))

        legendsteps_json = '{"success":"true", "total":' + str(legend_steps.__len__()) + ',"legendclasses":' + legendsteps_json + '}'

    else:
        legendsteps_json = '{"success":false, "error":"No Legends defined!"}'

    return legendsteps_json


def GetLegends():
    legends_dict_all = []
    legends = querydb.get_all_legends()

    if hasattr(legends, "__len__") and legends.__len__() > 0:
        for legend in legends:
            # row_dict = functions.row2dict(legend)
            row_dict = legend

            legend_steps = querydb.get_legend_steps(legendid=row_dict['legend_id'])

            legendname = row_dict['legend_name']
            # print legendname.encode('utf-8')
            legendname = legendname.replace('<BR>', ' ')
            legendname = legendname.replace('</BR>', ' ')
            legendname = legendname.replace('<br>', ' ')
            legendname = legendname.replace('</br>', ' ')
            legendname = legendname.replace('<div>', ' ')
            legendname = legendname.replace('</div>', ' ')
            legendname = legendname.replace('<DIV>', ' ')
            legendname = legendname.replace('</DIV>', ' ')

            # colorschemeHTML = '<table cellspacing=0 cellpadding=0 width=100%><tr><th colspan='+str(len(legend_steps))+'>'+legendname+'</th></tr><tr>'
            colorschemeHTML = legendname+'<table cellspacing=0 cellpadding=0 width=100%><tr>'

            for step in legend_steps:
                # convert step['color_rgb'] from RGB to html color
                color_rgb = step.color_rgb.split(' ')
                color_html = functions.rgb2html(color_rgb)
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = 'rgb('+r+','+g+','+b+')'
                colorschemeHTML += "<td height=15 style='padding:0; margin:0; background-color: " + color_html + ";'></td>"
            colorschemeHTML += '</tr></table>'

            legend_dict = {'legendid': row_dict['legend_id'],
                           'colourscheme': colorschemeHTML,
                           'legendname': row_dict['legend_name'],
                           'minvalue': row_dict['min_value'],
                           'maxvalue': row_dict['max_value'],
                           'legend_descriptive_name': row_dict['colorbar'],
                           'defined_by': row_dict['defined_by']
                           }

            legends_dict_all.append(legend_dict)

        legends_json = json.dumps(legends_dict_all,
                                 ensure_ascii=False,
                                 encoding='utf-8',
                                 sort_keys=True,
                                 indent=4,
                                 separators=(', ', ': '))

        legends_json = '{"success":"true", "total":' + str(legends.__len__()) + ',"legends":' + legends_json + '}'

    else:
        legends_json = '{"success":false, "error":"No Legends defined!"}'

    return legends_json


def getAllColorSchemes():
    # import time
    colorschemes_file = es_constants.base_tmp_dir + os.path.sep + 'colorschemes.json'
    if os.path.isfile(colorschemes_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(colorschemes_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            colorschemes_json = ColorSchemes().encode('utf-8')
            try:
                with open(colorschemes_file, "w") as text_file:
                    text_file.write(colorschemes_json)
            except IOError:
                try:
                    os.remove(colorschemes_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(colorschemes_file) as text_file:
                    colorschemes_json = text_file.read()
            except IOError:
                colorschemes_json = ColorSchemes().encode('utf-8')
                try:
                    os.remove(colorschemes_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        colorschemes_json = ColorSchemes().encode('utf-8')
        try:
            with open(colorschemes_file, "w") as text_file:
                text_file.write(colorschemes_json)
        except IOError:
            try:
                os.remove(colorschemes_file)  # remove file and recreate next call
            except OSError:
                pass
    return colorschemes_json


def ColorSchemes():
    all_legends = querydb.get_all_legends()

    if hasattr(all_legends, "__len__") and all_legends.__len__() > 0:
        legends_dict_all = []
        for legend in all_legends:
            # legend_dict = functions.row2dict(legend)
            # legend_dict = legend.__dict__
            legend_dict = {}
            legend_id = legend['legend_id']
            legend_name = legend['legend_name']
            # legend_name = legend['colorbar']

            legend_steps = querydb.get_legend_steps(legendid=legend_id)

            colorschemeHTML = '<table cellspacing=0 cellpadding=0 width=100%><tr>'
            for step in legend_steps:
                # convert step['color_rgb'] from RGB to html color
                color_rgb = step.color_rgb.split(' ')
                color_html = functions.rgb2html(color_rgb)
                r = color_rgb[0]
                g = color_rgb[1]
                b = color_rgb[2]
                color_html = 'rgb('+r+','+g+','+b+')'
                colorschemeHTML = colorschemeHTML + \
                                  "<td height=15 style='padding:0; margin:0; background-color: " + \
                                  color_html + ";'></td>"
            colorschemeHTML = colorschemeHTML + '</tr></table>'

            legend_dict['legend_id'] = legend_id
            legend_dict['legend_name'] = legend_name
            legend_dict['colorbar'] = legend['colorbar']
            legend_dict['colorschemeHTML'] = colorschemeHTML
            legendsHTML = generateLegendHTML.generateLegendHTML(legend_id)
            # print legendsHTML['legendHTML']
            legend_dict['legendHTML'] = legendsHTML['legendHTML']
            legend_dict['legendHTMLVertical'] = legendsHTML['legendHTMLVertical']

            legends_dict_all.append(legend_dict)

        legends_json = json.dumps(legends_dict_all,
                                  ensure_ascii=False,
                                  sort_keys=True,
                                  indent=4,
                                  separators=(', ', ': '))

        colorschemes = '{"success":"true", "total":' + str(all_legends.__len__()) + ',"legends":'+legends_json+'}'
    else:
        colorschemes = '{"success":"true", "message":"No legends defined!"}'

    return colorschemes


def getProductNavigatorDataSets(forse):
    # import time
    datasetsinfo_file = es_constants.base_tmp_dir + os.path.sep + 'product_navigator_datasets_info.json'
    if forse:
        dataset_json = ProductNavigatorDataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(dataset_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(datasetsinfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(datasetsinfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            dataset_json = ProductNavigatorDataSets().encode('utf-8')
            try:
                with open(datasetsinfo_file, "w") as text_file:
                    text_file.write(dataset_json)
            except IOError:
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(datasetsinfo_file) as text_file:
                    dataset_json = text_file.read()
            except IOError:
                dataset_json = ProductNavigatorDataSets().encode('utf-8')
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        dataset_json = ProductNavigatorDataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(dataset_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return dataset_json


def ProductNavigatorDataSets():
    db_products = querydb.get_products(activated=None, masked=False)

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = functions.row2dict(row)
            productcode = prod_dict['productcode']
            version = prod_dict['version']

            p = Product(product_code=productcode, version=version)

            # does the product have mapsets AND subproducts?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != []:
                        mapset_dict = functions.row2dict(mapset_info)
                        mapset_dict['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print productcode + ' - ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode,
                                                                  masked=True)

                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                dataset_dict['mapsetcode'] = mapset

                                # dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                # completeness = dataset.get_dataset_normalized_info()
                                # dataset_dict['datasetcompleteness'] = completeness

                                mapset_dict['mapsetdatasets'].append(dataset_dict)
                        if mapset_dict['mapsetdatasets'].__len__() > 0:
                            prod_dict['productmapsets'].append(mapset_dict)
                products_dict_all.append(prod_dict)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        dataset_json = '{"success":"true", "total":'\
                              + str(db_products.__len__())\
                              + ',"products":'+prod_json+'}'

    else:
        dataset_json = '{"success":false, "error":"No data sets defined!"}'

    return dataset_json


def getDataSets(forse):
    # import time
    datasetsinfo_file = es_constants.base_tmp_dir + os.path.sep + 'datasets_info.json'
    if forse:
        datamanagement_json = DataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(datamanagement_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(datasetsinfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(datasetsinfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            datamanagement_json = DataSets().encode('utf-8')
            try:
                with open(datasetsinfo_file, "w") as text_file:
                    text_file.write(datamanagement_json)
            except IOError:
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(datasetsinfo_file) as text_file:
                    datamanagement_json = text_file.read()
            except IOError:
                datamanagement_json = DataSets().encode('utf-8')
                try:
                    os.remove(datasetsinfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        datamanagement_json = DataSets().encode('utf-8')
        try:
            with open(datasetsinfo_file, "w") as text_file:
                text_file.write(datamanagement_json)
        except IOError:
            try:
                os.remove(datasetsinfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return datamanagement_json


def DataSets():
    from dateutil.relativedelta import relativedelta

    db_products = querydb.get_products(activated=True)

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = functions.row2dict(row)
            productcode = prod_dict['productcode']
            version = prod_dict['version']

            p = Product(product_code=productcode, version=version)
            # print productcode
            # does the product have mapsets AND subproducts?
            all_prod_mapsets = p.mapsets
            all_prod_subproducts = p.subproducts
            if all_prod_mapsets.__len__() > 0 and all_prod_subproducts.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_dict = []
                    # print mapset
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != []:
                        mapset_dict = functions.row2dict(mapset_info)
                        # print mapset_dict
                        mapset_dict['productcode'] = productcode
                        mapset_dict['version'] = version
                        # else:
                        #   mapset_dict['mapsetcode'] = mapset
                        mapset_dict['mapsetdatasets'] = []
                        all_mapset_datasets = p.get_subproducts(mapset=mapset)
                        for subproductcode in all_mapset_datasets:
                            # print 'productcode: ' + productcode
                            # print 'version: ' + version
                            # print 'subproductcode: ' + subproductcode
                            dataset_info = querydb.get_subproduct(productcode=productcode,
                                                                  version=version,
                                                                  subproductcode=subproductcode)
                            # print dataset_info
                            # dataset_info = querydb.db.product.get(productcode, version, subproductcode)
                            # dataset_dict = {}
                            if dataset_info is not None:
                                dataset_dict = functions.row2dict(dataset_info)
                                # dataset_dict = dataset_info.__dict__
                                # del dataset_dict['_labels']
                                if hasattr(dataset_info, 'frequency_id'):
                                    if dataset_info.frequency_id == 'e15minute':
                                        # dataset_dict['nodisplay'] = 'no_minutes_display'
                                        today = datetime.date.today()
                                        from_date = today - datetime.timedelta(days=3)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    elif dataset_info.frequency_id == 'e30minute':
                                        # dataset_dict['nodisplay'] = 'no_minutes_display'
                                        today = datetime.date.today()
                                        from_date = today - datetime.timedelta(days=6)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    # elif dataset_info.frequency_id == 'e1year':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'

                                    elif dataset_info.frequency_id == 'e1day':
                                        today = datetime.date.today()
                                        from_date = today - relativedelta(years=1)
                                        # if sys.platform != 'win32':
                                        #     from_date = today - relativedelta(years=1)
                                        # else:
                                        #     from_date = today - datetime.timedelta(days=365)
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode,
                                                  'from_date': from_date}
                                    else:
                                        kwargs = {'mapset': mapset,
                                                  'sub_product_code': subproductcode}

                                    # if dataset_info.frequency_id == 'e15minute' or dataset_info.frequency_id == 'e30minute':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # # To be implemented in dataset.py
                                    # elif dataset_info.frequency_id == 'e1year':
                                    #     dataset_dict['nodisplay'] = 'no_minutes_display'
                                    # else:
                                    #     dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                    dataset = p.get_dataset(**kwargs)
                                    completeness = dataset.get_dataset_normalized_info()
                                    dataset_dict['datasetcompleteness'] = completeness
                                    dataset_dict['nodisplay'] = 'false'

                                    dataset_dict['mapsetcode'] = mapset_dict['mapsetcode']
                                    dataset_dict['mapset_descriptive_name'] = mapset_dict['descriptive_name']

                                    mapset_dict['mapsetdatasets'].append(dataset_dict)
                                else:
                                    pass
                    prod_dict['productmapsets'].append(mapset_dict)
            products_dict_all.append(prod_dict)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        datamanagement_json = '{"success":"true", "total":' \
                              + str(db_products.__len__()) \
                              + ',"products":' + prod_json + '}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    datamanagement_json = datamanagement_json.replace('\\r\\n', ' ')
    datamanagement_json = datamanagement_json.replace("'", "\'")
    datamanagement_json = datamanagement_json.replace(', ', ',')
    return datamanagement_json


def getTimeseriesProducts(forse):
    # import time
    timeseriesproducts_file = es_constants.base_tmp_dir + os.path.sep + 'timeseries_products.json'

    if forse:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
        try:
            with open(timeseriesproducts_file, "w") as text_file:
                text_file.write(timeseriesproducts_json)
        except IOError:
            try:
                os.remove(timeseriesproducts_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(timeseriesproducts_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(timeseriesproducts_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5  hours
            timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
            try:
                with open(timeseriesproducts_file, "w") as text_file:
                    text_file.write(timeseriesproducts_json)
            except IOError:
                try:
                    os.remove(timeseriesproducts_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(timeseriesproducts_file) as text_file:
                    timeseriesproducts_json = text_file.read()
            except IOError:
                timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
                try:
                    os.remove(timeseriesproducts_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        timeseriesproducts_json = TimeseriesProducts().encode('utf-8')
        try:
            with open(timeseriesproducts_file, "w") as text_file:
                text_file.write(timeseriesproducts_json)
        except IOError:
            try:
                os.remove(timeseriesproducts_file)  # remove file and recreate next call
            except OSError:
                pass

    return timeseriesproducts_json


def TimeseriesProducts():
    import copy
    # import time
    # t0 = time.time()
    # print 'START: ' + str(t0)

    db_products = querydb.get_timeseries_products()
    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        for row in db_products:
            prod_dict = {}
            prod_record = functions.row2dict(row)
            productcode = prod_record['productcode']
            subproductcode = prod_record['subproductcode']
            version = prod_record['version']

            prod_dict['category_id'] = prod_record['category_id']
            prod_dict['cat_descr_name'] = prod_record['cat_descr_name']
            prod_dict['order_index'] = prod_record['order_index']
            prod_dict['display_index'] = prod_record['display_index']
            prod_dict['productid'] = prod_record['productid']
            prod_dict['productcode'] = prod_record['productcode']
            prod_dict['version'] = prod_record['version']
            prod_dict['subproductcode'] = prod_record['subproductcode']
            # prod_dict['mapsetcode'] = ""
            # prod_dict['mapset_name'] = ""
            prod_dict['group_product_descriptive_name'] = prod_record['group_product_descriptive_name']
            prod_dict['product_descriptive_name'] = prod_record['descriptive_name']
            prod_dict['product_description'] = prod_record['description']
            prod_dict['frequency_id'] = prod_record['frequency_id']
            prod_dict['date_format'] = prod_record['date_format']
            prod_dict['timeseries_role'] = prod_record['timeseries_role']
            prod_dict['selected'] = False
            prod_dict['cumulative'] = False
            prod_dict['difference'] = False
            prod_dict['reference'] = False
            # prod_dict['years'] = []

            # does the product have mapsets?
            # t1 = time.time()
            # print 'before calling Product(): ' + str(t1)
            p = Product(product_code=productcode, version=version)
            # t2 = time.time()
            # print 'after calling Product(): ' + str(t2-t1)

            all_prod_mapsets = p.mapsets
            if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != []:
                        mapset_record = functions.row2dict(mapset_info)

                        tmp_prod_dict = copy.deepcopy(prod_dict)
                        tmp_prod_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_record['mapsetcode']
                        tmp_prod_dict['mapsetcode'] = mapset_record['mapsetcode']
                        tmp_prod_dict['mapset_name'] = mapset_record['descriptive_name']

                        # t3 = time.time()
                        # print 'before getting dataset info: ' + str(t3)

                        dataset = p.get_dataset(mapset=mapset, sub_product_code=tmp_prod_dict['subproductcode'])
                        # dataset.get_filenames()
                        all_present_product_dates = dataset.get_dates()

                        # t4 = time.time()
                        # tot_get_dataset = t4-t3
                        # print 'after getting dataset info: ' + str(tot_get_dataset)


                        # t5 = time.time()
                        # print 'before getting years: ' + str(t5)

                        distinctyears = []
                        for product_date in all_present_product_dates:
                            if product_date.year not in distinctyears:
                                distinctyears.append(product_date.year)
                        tmp_prod_dict['years'] = distinctyears

                        if tmp_prod_dict['years'].__len__() > 0:
                            products_dict_all.append(tmp_prod_dict)
                            # tmp_prod_dict = copy.deepcopy(prod_dict)
                            #
                            # products_dict_all.append(tmp_prod_dict)
                            # tmp_prod_dict = []

                        # t6 = time.time()
                        # total = t6-t5
                        # print 'after getting years: ' + str(total)

                        timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                        version=version,
                                                                                        subproductcode=subproductcode)
                        # t7 = time.time()
                        # print 'before getting subproduct info: ' + str(t7)

                        for subproduct in timeseries_mapset_datasets:
                            if subproduct is not None:
                                # t7 = time.time()
                                dataset_record = functions.row2dict(subproduct)
                                dataset = p.get_dataset(mapset=mapset,
                                                        sub_product_code=dataset_record['subproductcode'])
                                # t8 = time.time()
                                # totals_subproduct = t8 - t7
                                # print 'after getting subproduct dataset: ' + str(totals_subproduct)

                                # dataset.get_filenames()
                                all_present_product_dates = dataset.get_dates()

                                distinctyears = []
                                for product_date in all_present_product_dates:
                                    if product_date.year not in distinctyears:
                                        distinctyears.append(product_date.year)

                                dataset_dict = {}
                                dataset_dict['category_id'] = prod_record['category_id']
                                dataset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                                dataset_dict['order_index'] = prod_record['order_index']
                                dataset_dict['productid'] = dataset_record['productid']
                                dataset_dict['productcode'] = dataset_record['productcode']
                                dataset_dict['version'] = dataset_record['version']
                                dataset_dict['subproductcode'] = dataset_record['subproductcode']
                                dataset_dict['productmapsetid'] = tmp_prod_dict['productmapsetid']
                                dataset_dict['display_index'] = dataset_record['display_index']
                                dataset_dict['mapsetcode'] = mapset_record['mapsetcode']
                                dataset_dict['mapset_name'] = mapset_record['descriptive_name']
                                dataset_dict['group_product_descriptive_name'] = prod_record['group_product_descriptive_name']
                                dataset_dict['product_descriptive_name'] = dataset_record['descriptive_name']
                                dataset_dict['product_description'] = dataset_record['description']
                                dataset_dict['frequency_id'] = dataset_record['frequency_id']
                                dataset_dict['date_format'] = dataset_record['date_format']
                                dataset_dict['timeseries_role'] = dataset_record['timeseries_role']
                                dataset_dict['years'] = distinctyears
                                dataset_dict['selected'] = False
                                dataset_dict['cumulative'] = False
                                dataset_dict['difference'] = False
                                dataset_dict['reference'] = False

                                if dataset_dict['years'].__len__() > 0:
                                    products_dict_all.append(dataset_dict)
                                    # # tmp_prod_dict = prod_dict.copy()
                                    # tmp_prod_dict = copy.deepcopy(dataset_dict)
                                    #
                                    # products_dict_all.append(tmp_prod_dict)
                                    # tmp_prod_dict = []

                        # t8 = time.time()
                        # totals_subproduct = t8-t7
                        # print 'after getting subproduct info: ' + str(totals_subproduct)

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        timeseriesproducts_json = '{"success":"true", "total":' \
                                  + str(db_products.__len__()) \
                                  + ',"products":' + prod_json + '}'

    else:
        timeseriesproducts_json = '{"success":false, "error":"No data sets defined!"}'

    # t9 = time.time()
    # total = t9-t0
    # print 'Total time: ' + str(total)

    timeseriesproducts_json = timeseriesproducts_json.replace('\\r\\n', ' ')
    timeseriesproducts_json = timeseriesproducts_json.replace("'", "\'")
    timeseriesproducts_json = timeseriesproducts_json.replace(', ', ',')
    return timeseriesproducts_json


def __TimeseriesProducts():
    import copy

    db_products = querydb.get_timeseries_products()

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = functions.row2dict(row)
            productcode = prod_dict['productcode']
            subproductcode = prod_dict['subproductcode']
            version = prod_dict['version']

            p = Product(product_code=productcode, version=version)

            # does the product have mapsets?
            all_prod_mapsets = p.mapsets
            # print productcode
            # print all_prod_mapsets
            if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                prod_dict['productmapsets'] = []
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    mapset_dict = functions.row2dict(mapset_info)
                    mapset_dict['timeseriesmapsetdatasets'] = []
                    timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                    version=version,
                                                                                    subproductcode=subproductcode)
                    for subproduct in timeseries_mapset_datasets:
                        if subproduct is not None:
                            dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                            dataset.get_filenames()
                            all_present_product_dates = dataset.get_dates()

                            distinctyears = []
                            for product_date in all_present_product_dates:
                                if product_date.year not in distinctyears:
                                    distinctyears.append(product_date.year)

                            dataset_dict = functions.row2dict(subproduct)

                            # if productcode == 'vgt-ndvi':
                            #     print dataset.get_filenames()
                            #     print all_present_product_dates
                            #     print distinctyears

                            dataset_dict['years'] = distinctyears
                            dataset_dict['mapsetcode'] = mapset
                            mapset_dict['timeseriesmapsetdatasets'].append(dataset_dict)

                    if dataset_dict['years'].__len__() > 0:
                        # tmp_prod_dict = prod_dict.copy()
                        tmp_prod_dict = copy.deepcopy(prod_dict)

                        tmp_prod_dict['productmapsets'].append(mapset_dict)
                        products_dict_all.append(tmp_prod_dict)
                        tmp_prod_dict = []

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        datamanagement_json = '{"success":"true", "total":' \
                              + str(db_products.__len__()) \
                              + ',"products":' + prod_json + '}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    return datamanagement_json


def __TimeseriesProductsTree():
    import copy

    db_products = querydb.get_timeseries_products()

    if hasattr(db_products, "__len__") and db_products.__len__() > 0:
        products_dict_all = []
        # loop the products list
        for row in db_products:
            prod_dict = {}
            prod_record = functions.row2dict(row)
            productcode = prod_record['productcode']
            subproductcode = prod_record['subproductcode']
            version = prod_record['version']

            # prod_dict['itemtype'] = "TimeseriesProduct"
            prod_dict['cat_descr_name'] = prod_record['cat_descr_name']
            prod_dict['category_id'] = prod_record['category_id']
            prod_dict['order_index'] = prod_record['order_index']
            prod_dict['productid'] = prod_record['productid']
            prod_dict['productcode'] = prod_record['productcode']
            prod_dict['version'] = prod_record['version']
            prod_dict['subproductcode'] = prod_record['subproductcode']
            # prod_dict['mapsetcode'] = ""
            prod_dict['descriptive_name'] = prod_record['descriptive_name']
            prod_dict['description'] = prod_record['description']
            # prod_dict['years'] = []
            # prod_dict['parentId'] = 'root'
            # prod_dict['leaf'] = False

            # does the product have mapsets?
            p = Product(product_code=productcode, version=version)
            all_prod_mapsets = p.mapsets
            # print all_prod_mapsets

            if hasattr(all_prod_mapsets, "__len__") and all_prod_mapsets.__len__() > 0:
                prod_dict['productmapsets'] = []
                # prod_dict['children'] = []
                for mapset in all_prod_mapsets:
                    mapset_info = querydb.get_mapset(mapsetcode=mapset, allrecs=False)
                    if mapset_info != []:
                        mapset_record = functions.row2dict(mapset_info)
                        # print mapset_record
                        mapset_dict = {}
                        # mapset_dict['itemtype'] = "TimeseriesMapset"
                        # mapset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                        # mapset_dict['category_id'] = prod_record['category_id']
                        # mapset_dict['order_index'] = prod_record['order_index']
                        # mapset_dict['productid'] = prod_record['productid']
                        # mapset_dict['productcode'] = prod_record['productcode']
                        # mapset_dict['version'] = prod_record['version']
                        # mapset_dict['subproductcode'] = prod_record['subproductcode']
                        mapset_dict['productmapsetid'] = prod_record['productid'] + '_' + mapset_record['mapsetcode']
                        mapset_dict['mapsetcode'] = mapset_record['mapsetcode']
                        mapset_dict['descriptive_name'] = mapset_record['descriptive_name']
                        mapset_dict['description'] = mapset_record['description']
                        mapset_dict['timeseriesmapsetdatasets'] = []
                        # mapset_dict['years'] = []
                        # mapset_dict['parentId'] = prod_record['productid']
                        # mapset_dict['leaf'] = False
                        # mapset_dict['children'] = []
                        timeseries_mapset_datasets = querydb.get_timeseries_subproducts(productcode=productcode,
                                                                                        version=version,
                                                                                        subproductcode=subproductcode)
                        for subproduct in timeseries_mapset_datasets:
                            if subproduct is not None:
                                dataset = p.get_dataset(mapset=mapset, sub_product_code=subproductcode)
                                dataset.get_filenames()
                                all_present_product_dates = dataset.get_dates()

                                distinctyears = []
                                for product_date in all_present_product_dates:
                                    if product_date.year not in distinctyears:
                                        distinctyears.append(product_date.year)

                                dataset_record = functions.row2dict(subproduct)
                                dataset_dict = {}
                                # dataset_dict['itemtype'] = "TimeseriesSubproduct"
                                # dataset_dict['cat_descr_name'] = prod_record['cat_descr_name']
                                # dataset_dict['category_id'] = prod_record['category_id']
                                # dataset_dict['order_index'] = prod_record['order_index']
                                dataset_dict['subproductid'] = dataset_record['productid']
                                dataset_dict['productcode'] = dataset_record['productcode']
                                dataset_dict['version'] = dataset_record['version']
                                dataset_dict['subproductcode'] = dataset_record['subproductcode']
                                dataset_dict['mapsetcode'] = mapset_record['mapsetcode']
                                dataset_dict['descriptive_name'] = dataset_record['descriptive_name']
                                dataset_dict['description'] = dataset_record['description']
                                dataset_dict['years'] = distinctyears
                                # dataset_dict['leaf'] = True
                                # dataset_dict['checked'] = False
                                # dataset_dict['parentId'] = mapset_dict['productmapsetid']

                                # dataset_dict['mapsetcode'] = mapset
                                mapset_dict['timeseriesmapsetdatasets'].append(dataset_dict)
                                # mapset_dict['children'].append(dataset_dict)

                        if dataset_dict['years'].__len__() > 0:
                            # tmp_prod_dict = prod_dict.copy()
                            tmp_prod_dict = copy.deepcopy(prod_dict)

                            tmp_prod_dict['productmapsets'].append(mapset_dict)
                            # tmp_prod_dict['children'].append(mapset_dict)
                            products_dict_all.append(tmp_prod_dict)
                            tmp_prod_dict = []

        prod_json = json.dumps(products_dict_all,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        # datamanagement_json = '{"products":'+prod_json+'}'
        # datamanagement_json = '{"descriptive_name": "", "productid": "root", "parentId": null, "leaf": false, "children": '+prod_json+'}'

        datamanagement_json = '{"success":"true", "total":' \
                              + str(db_products.__len__()) \
                              + ',"products":' + prod_json + '}'

    else:
        datamanagement_json = '{"success":false, "error":"No data sets defined!"}'

    return datamanagement_json


def getIngestion(forse):
    # import time
    ingestioninfo_file = es_constants.base_tmp_dir + os.path.sep + 'ingestion_info.json'
    if forse:
        ingestions_json = Ingestion().encode('utf-8')
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
        except IOError:
            try:
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                pass

    elif os.path.isfile(ingestioninfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(ingestioninfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            ingestions_json = Ingestion().encode('utf-8')
            try:
                with open(ingestioninfo_file, "w") as text_file:
                    text_file.write(ingestions_json)
            except IOError:
                try:
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    pass
        else:
            try:
                with open(ingestioninfo_file) as text_file:
                    ingestions_json = text_file.read()
            except IOError:
                ingestions_json = Ingestion().encode('utf-8')
                try:
                    os.remove(ingestioninfo_file)  # remove file and recreate next call
                except OSError:
                    pass

    else:
        ingestions_json = Ingestion().encode('utf-8')
        try:
            with open(ingestioninfo_file, "w") as text_file:
                text_file.write(ingestions_json)
        except IOError:
            try:
                os.remove(ingestioninfo_file)  # remove file and recreate next call
            except OSError:
                pass
    return ingestions_json


def Ingestion():
    from dateutil.relativedelta import relativedelta

    # return web.ctx
    ingestions = querydb.get_ingestions()
    # print ingestions

    if hasattr(ingestions, "__len__") and ingestions.__len__() > 0:
        ingest_dict_all = []
        for row in ingestions:
            ingest_dict = functions.row2dict(row)

            if row.mapsetcode != None and row.mapsetcode != '':
                if row.frequency_id == 'e15minute':
                    # ingest_dict['nodisplay'] = 'no_minutes_display'
                    today = datetime.date.today()
                    from_date = today - datetime.timedelta(days=3)
                    # week_ago = datetime.datetime(2015, 8, 27, 00, 00)   # .strftime('%Y%m%d%H%S')
                    # kwargs.update({'from_date': week_ago})  # datetime.date(2015, 08, 27)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                    # dataset = Dataset(**kwargs)
                    # completeness = dataset.get_dataset_normalized_info()
                elif row.frequency_id == 'e30minute':
                    today = datetime.date.today()
                    from_date = today - datetime.timedelta(days=6)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                elif row.frequency_id == 'e1day':
                    today = datetime.date.today()
                    from_date = today - relativedelta(years=1)

                    # if sys.platform != 'win32':
                    #     from_date = today - relativedelta(years=1)
                    # else:
                    #     from_date = today - datetime.timedelta(days=365)
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode,
                              'from_date': from_date}
                else:
                    kwargs = {'product_code': row.productcode,
                              'sub_product_code': row.subproductcode,
                              'version': row.version,
                              'mapset': row.mapsetcode}
                # print kwargs
                dataset = Dataset(**kwargs)
                completeness = dataset.get_dataset_normalized_info()
                ingest_dict['completeness'] = completeness
                ingest_dict['nodisplay'] = 'false'
            else:
                ingest_dict['completeness'] = {}
                ingest_dict['nodisplay'] = 'false'

            ingest_dict_all.append(ingest_dict)

        # ingestions_json = tojson(ingestions)
        ingestions_json = json.dumps(ingest_dict_all,
                                     ensure_ascii=False,
                                     sort_keys=True,
                                     indent=4,
                                     separators=(', ', ': '))
        ingestions_json = '{"success":"true", "total":' + str(
            ingestions.__len__()) + ',"ingestions":' + ingestions_json + '}'
    else:
        ingestions_json = '{"success":false, "error":"No ingestions defined!"}'

    ingestions_json = ingestions_json.replace('\\r\\n', ' ')
    ingestions_json = ingestions_json.replace("'", "\'")
    ingestions_json = ingestions_json.replace(', ', ',')
    return ingestions_json


def getProcessing(forse):
    # import time
    # forse = True
    processinginfo_file = es_constants.base_tmp_dir + os.path.sep + 'processing_info.json'
    if forse:
        processing_chains_json = Processing().encode('utf-8')
        try:
            with open(processinginfo_file, "w") as text_file:
                text_file.write(processing_chains_json)
        except IOError:
            try:
                os.remove(processinginfo_file)  # remove file and recreate next call
            except OSError:
                pass
        finally:
            text_file.close()

    elif os.path.isfile(processinginfo_file):
        # now = time.time()
        # nowdatetime = datetime.datetime.fromtimestamp(now)   # .strftime('%Y-%m-%d %H:%M:%S')
        lastmodfified = os.path.getmtime(processinginfo_file)
        lastmodfifieddatetime = datetime.datetime.fromtimestamp(lastmodfified)  # .strftime('%Y-%m-%d %H:%M:%S')
        if lastmodfifieddatetime < datetime.datetime.now() - datetime.timedelta(hours=3):  # seconds=5
            processing_chains_json = Processing().encode('utf-8')
            try:
                with open(processinginfo_file, "w") as text_file:
                    text_file.write(processing_chains_json)
            except IOError:
                try:
                    os.remove(processinginfo_file)  # remove file and recreate next call
                except OSError:
                    pass
            finally:
                text_file.close()
        else:
            try:
                with open(processinginfo_file) as text_file:
                    processing_chains_json = text_file.read()
                    # processing_chains_json = json.loads(processing_chains_json)
            except IOError:
                processing_chains_json = Processing().encode('utf-8')
                try:
                    os.remove(processinginfo_file)  # remove file and recreate next call
                except OSError:
                    pass
            finally:
                text_file.close()

    else:
        processing_chains_json = Processing().encode('utf-8')
        try:
            with open(processinginfo_file, "w") as text_file:
                text_file.write(processing_chains_json)
        except IOError:
            try:
                os.remove(processinginfo_file)  # remove file and recreate next call
            except OSError:
                pass
        finally:
            text_file.close()

    return processing_chains_json


def Processing():
    #   Todo JURVTK: on each call of a processing chain for a product, get the list of output (sub)products from the
    #   Todo JURVTK: processing chain algorithm using processing_std_precip . get_subprods_std_precip () and loop
    #   Todo JURVTK: this list to check the existance of the output product in the table product.process_product
    #   Todo JURVTK: Insert the output product in the table product.process_product if no record exists.
    #   Todo JURVTK:  Use: from apps . processing import processing_std_precip
    #   Todo JURVTK:       brachet l1, l2 brachet = processing_std_precip . get_subprods_std_precip ()

    processing_chains_json = '{"success":true, "message":"No processing chains defined!"}'

    processing_chains = querydb.get_processing_chains()

    if hasattr(processing_chains, "__len__") and processing_chains.__len__() > 0:
        processing_chains_dict_all = []

        for process in processing_chains:
            process_id = process.process_id
            process_dict = functions.row2dict(process)

            db_process_input_products = querydb.get_processingchains_input_products(process_id)
            process_dict['inputproducts'] = []
            if hasattr(db_process_input_products, "__len__") and db_process_input_products.__len__() > 0:

                for input_product in db_process_input_products:
                    # process_id = input_product.process_id
                    input_mapsetcode = input_product.mapsetcode
                    process_dict['category_id'] = input_product.category_id
                    process_dict['cat_descr_name'] = input_product.cat_descr_name
                    process_dict['order_index'] = input_product.order_index

                    input_prod_dict = functions.row2dict(input_product)
                    # prod_dict = input_product.__dict__
                    # del prod_dict['_labels']
                    # input_prod_dict['inputproductmapset'] = []
                    # mapset_info = querydb.get_mapset(mapsetcode=input_mapsetcode)
                    # mapset_dict = functions.row2dict(mapset_info)
                    # input_prod_dict['inputproductmapset'].append(mapset_dict)
                    process_dict['inputproducts'].append(input_prod_dict)

            db_process_output_products = querydb.get_processingchain_output_products(process_id)
            process_dict['outputproducts'] = []
            if hasattr(db_process_output_products, "__len__") and db_process_output_products.__len__() > 0:
                for outputproduct in db_process_output_products:
                    output_mapsetcode = outputproduct.mapsetcode
                    output_product_dict = functions.row2dict(outputproduct)
                    # output_product_dict = outputproduct.__dict__
                    # del outputproduct_dict['_labels']

                    # output_product_dict['outputproductmapset'] = []
                    # mapset_info = querydb.get_mapset(mapsetcode=output_mapsetcode)
                    # mapset_dict = functions.row2dict(mapset_info)
                    # output_product_dict['outputproductmapset'].append(mapset_dict)
                    process_dict['outputproducts'].append(output_product_dict)

            processing_chains_dict_all.append(process_dict)

            processes_json = json.dumps(processing_chains_dict_all,
                                        ensure_ascii=False,
                                        sort_keys=True,
                                        indent=4,
                                        separators=(', ', ': '))

            processing_chains_json = '{"success":"true", "total":' \
                                     + str(processing_chains.__len__()) \
                                     + ',"processes":' + processes_json + '}'

    processing_chains_json = processing_chains_json.replace('\\r\\n', ' ')
    processing_chains_json = processing_chains_json.replace('\\n', ' ')
    processing_chains_json = processing_chains_json.replace("'", "\'")
    processing_chains_json = processing_chains_json.replace(', ', ',')
    return processing_chains_json