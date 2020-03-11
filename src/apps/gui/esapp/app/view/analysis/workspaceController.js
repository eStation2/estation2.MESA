Ext.define('esapp.view.analysis.workspaceController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-workspace'

    ,closeAllMapsGraphs: function(){
        var me = this.getView();
        var mapViewWindows = me.query('mapview-window');
        var tsGraphWindows = me.query('timeserieschart-window');

        Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
            mapview_window.close();
        });

        Ext.Object.each(tsGraphWindows, function(id, tsgraph_window, thisObj) {
            tsgraph_window.close();
        });
    }

    ,openWorkspaceGraphs: function(graphs){
        var me = this.getView();
        me.allGraphsLoaded = false;

        for (var i = 0; i < graphs.length; i++) {
           // console.info(graphs[i]);
            var wsgraph = {
                workspace: me,
                isTemplate: graphs[i].istemplate,
                isNewTemplate: !graphs[i].istemplate,
                workspaceid: graphs[i].workspaceid,
                userid: graphs[i].userid,
                graph_tpl_id: graphs[i].graph_tpl_id,
                parent_tpl_id: graphs[i].parent_tpl_id,
                graph_tpl_name: graphs[i].graph_tpl_name,
                istemplate: graphs[i].istemplate,
                graphviewposition: esapp.Utils.objectExists(graphs[i].graphviewposition) ? graphs[i].graphviewposition.split(",").map(function(x){return parseInt(x)}) : [50,5],      // .filter(Boolean)
                graphviewsize: esapp.Utils.objectExists(graphs[i].graphviewsize) ? graphs[i].graphviewsize.split(",").map(function(x){return parseInt(x)}) : [700,600],
                graphtype: graphs[i].graph_type,
                selectedTimeseries: graphs[i].selectedtimeseries,
                yearTS: graphs[i].yearts,
                tsFromPeriod: graphs[i].tsfromperiod,
                tsToPeriod: graphs[i].tstoperiod,
                yearsToCompare: graphs[i].yearstocompare != '' ? Ext.decode(graphs[i].yearstocompare) : '',
                tsFromSeason: graphs[i].tsfromseason,
                tsToSeason: graphs[i].tstoseason,
                wkt_geom: graphs[i].wkt_geom,
                selectedregionname: graphs[i].selectedregionname,
                disclaimerObjPosition: graphs[i].disclaimerobjposition != null ? graphs[i].disclaimerobjposition.split(",").map(function(x){return parseInt(x)}) : [0,611],
                disclaimerObjContent: graphs[i].disclaimerobjcontent,
                logosObjPosition: graphs[i].logosobjposition != null ? graphs[i].logosobjposition.split(",").map(function(x){return parseInt(x)}) : [434, 583],
                logosObjContent: graphs[i].logosobjcontent != '' ? Ext.decode(graphs[i].logosobjcontent) : null,
                showObjects: graphs[i].showobjects,
                showtoolbar: graphs[i].showtoolbar,
                auto_open: graphs[i].auto_open
            };
            var newGraphViewWin = new esapp.view.analysis.timeseriesChartView(wsgraph);

            me.add(newGraphViewWin);
            newGraphViewWin.show();

            if (i==graphs.length-1){
                me.allGraphsLoaded = true;
            }
        }
    }

    ,openWorkspaceMaps: function(maps){
        var me = this.getView();
        me.allMapsLoaded = false;

        for (var i = 0; i < maps.length; i++) {
            var wsmap = {
                workspace : me,
                isTemplate: maps[i].istemplate,
                isNewTemplate: !maps[i].istemplate,
                userid: maps[i].userid,
                map_tpl_id: maps[i].map_tpl_id,
                parent_tpl_id: maps[i].parent_tpl_id,
                templatename: maps[i].map_tpl_name,
                mapviewPosition: maps[i].mapviewposition.split(",").map(function(x){return parseInt(x)}),      // .filter(Boolean)
                mapviewSize: maps[i].mapviewsize.split(",").map(function(x){return parseInt(x)}),
                productcode: maps[i].productcode,
                subproductcode: maps[i].subproductcode,
                productversion: maps[i].productversion,
                mapsetcode: maps[i].mapsetcode,
                productdate: maps[i].productdate,
                legendid: maps[i].legendid,
                legendlayout: maps[i].legendlayout,
                legendObjPosition: maps[i].legendobjposition.split(",").map(function(x){return parseInt(x)}),
                showlegend: maps[i].showlegend,
                titleObjPosition: maps[i].titleobjposition.split(",").map(function(x){return parseInt(x)}),
                titleObjContent: maps[i].titleobjcontent,
                disclaimerObjPosition: maps[i].disclaimerobjposition.split(",").map(function(x){return parseInt(x)}),
                disclaimerObjContent: maps[i].disclaimerobjcontent,
                logosObjPosition: maps[i].logosobjposition.split(",").map(function(x){return parseInt(x)}),
                logosObjContent: Ext.decode(maps[i].logosobjcontent),
                showObjects: maps[i].showobjects,
                showtoolbar: maps[i].showtoolbar,
                showgraticule: maps[i].showgraticule,
                showtimeline: maps[i].showtimeline,
                scalelineObjPosition: maps[i].scalelineobjposition.split(",").map(function(x){return parseInt(x)}),
                vectorLayers: maps[i].vectorlayers,
                outmask: maps[i].outmask,
                outmaskFeature: maps[i].outmaskfeature,
                zoomextent: maps[i].zoomextent,
                mapsize: maps[i].mapsize,
                mapcenter: maps[i].mapcenter
            };
            // console.info(wsmap);
            var newMapViewWin = new esapp.view.analysis.mapView(wsmap);

            me.add(newMapViewWin);
            newMapViewWin.show();
            if (i==maps.length-1){
                me.allMapsLoaded = true;
            }
        }
    }

    ,setWorkspaceName: function(){
        var me = this.getView();
        var newWorkspaceName = '';

        // Open dialog asking to give a workspace name, proposing the name of workspace to copy with in the end " - copy"
        if (esapp.Utils.objectExists(me.workspacename) && me.workspacename != ''){
            newWorkspaceName = me.workspacename + ' - copy';
        }
        else {
            newWorkspaceName = esapp.Utils.getTranslation('name_new_workspace_copy');   // 'New workspace - copy';     // Will never be given because the workspace to copy always has a name.
        }

        Ext.MessageBox.prompt(esapp.Utils.getTranslation('workspace_name'), esapp.Utils.getTranslation('workspace_name_save_message') + ':', function(btn, text){   // Workspace name'   'Please give a name for the workspace to copy'
            if (btn == 'ok'){
                me.saveasWorkspacename = text;
                me.saveAs = true;
                this.saveWorkspace();
            }
        }, this, false, newWorkspaceName);
    }

    ,saveWorkspaceName: function(){
        var me = this.getView();
        var params = {};

        params.userid = esapp.getUser().userid;
        params.workspaceid = me.saveAs ? -1 : me.workspaceid;
        params.isNewWorkspace = me.isNewWorkspace;
        params.workspacename = me.workspacename;

        // console.info(params);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/saveworkspacename',
            params: params,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);

                if (responseJSON.success){
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, width: 300, align: 't'});

                    if (me.isNewWorkspace){
                        me.isNewWorkspace = false;
                        me.lookupReference('saveWorkspaceBtn').setArrowVisible(true);
                        me.tab.removeCls('newworkspacetab');
                        me.tab.updateLayout();
                        if (!me.saveAs){
                            me.workspaceid = responseJSON.workspaceid;
                        }
                    }

                    me.up().lookupReference('analysismain_addworkspacebtn').userWorkspaceAdminPanel.setDirtyStore(true);
                }
                else {
                    Ext.toast({hideDuration: 2000, html: responseJSON, title: esapp.Utils.getTranslation('error_save_workspace_name_change'), width: 300, align: 't'});
                    // me.templatename = '';
                }
                me.saveAs = false;
            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                Ext.toast({hideDuration: 2000, html: responseJSON, title: esapp.Utils.getTranslation('error_save_workspace_name_change'), width: 300, align: 't'});
                me.saveAs = false;
            }
        });
    }

    ,savePin: function(){
        var me = this.getView();
        var params = {};

        params.userid = esapp.getUser().userid;
        params.workspaceid = me.saveAs ? -1 : me.workspaceid;
        params.isNewWorkspace = me.saveAs ? true : me.isNewWorkspace;
        params.workspacename = me.workspacename;
        params.pinned = me.pinned;

        // console.info(params);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/saveworkspacepin',
            params: params,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);

                if (responseJSON.success){
                    // Ext.toast({hideDuration: 2000, html: responseJSON.message, width: 300, align: 't'});     // "Save Map template"

                    if (me.isNewWorkspace){
                        me.isNewWorkspace = false;
                        me.lookupReference('saveWorkspaceBtn').setArrowVisible(true);
                        me.tab.removeCls('newworkspacetab');
                        me.tab.updateLayout();
                        if (!me.saveAs){
                            me.workspaceid = responseJSON.workspaceid;
                        }
                    }

                    me.up().lookupReference('analysismain_addworkspacebtn').userWorkspaceAdminPanel.setDirtyStore(true);
                }
                else {
                    Ext.toast({hideDuration: 2000, html: responseJSON, title: esapp.Utils.getTranslation('error_save_workspace_pin_change'), width: 300, align: 't'});
                    // me.templatename = '';
                }
                me.saveAs = false;
            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                Ext.toast({hideDuration: 2000, html: responseJSON, title: esapp.Utils.getTranslation('error_save_workspace_pin_change'), width: 300, align: 't'});
                me.saveAs = false;
            }
        });
    }

    ,saveWorkspace: function(){
        var me = this.getView();
        var mapViewWindows = me.query('mapview-window');
        var tsGraphWindows = me.query('timeserieschart-window');
        var params = {};
        var openmaps = [];
        var opengraphs = [];

        // me.workspacename = me.title;
        // console.info(me);
        // console.info(me.workspaceid);
        Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
            openmaps.push(mapview_window.getController().getMapSettings());
        });

        Ext.Object.each(tsGraphWindows, function(id, tsgraph_window, thisObj) {
            opengraphs.push(tsgraph_window.getController().getGraphSettings());
        });
        me.workspacename = me.title;
        params.userid = esapp.getUser().userid;
        params.workspaceid = me.saveAs ? -1 : me.workspaceid;
        params.workspacename = me.saveAs ? me.saveasWorkspacename : me.workspacename;
        params.isNewWorkspace = me.saveAs ? true : me.isNewWorkspace;
        // params.title = me.title;
        params.pinned = me.saveAs ? false : me.pinned;
        params.maps = Ext.util.JSON.encode(openmaps);
        params.graphs = Ext.util.JSON.encode(opengraphs);
        // console.info(params);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/saveworkspace',
            params: params,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);

                if (responseJSON.success){
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, width: 300, align: 't'});     // "Save Map template"

                    if (me.isNewWorkspace){
                        me.isNewWorkspace = false;
                        me.lookupReference('saveWorkspaceBtn').setArrowVisible(true);
                        me.tab.removeCls('newworkspacetab');
                        me.tab.updateLayout();
                        if (!me.saveAs){
                            me.workspaceid = responseJSON.workspaceid;
                        }
                    }

                    // console.info(me.up());
                    me.up().lookupReference('analysismain_addworkspacebtn').userWorkspaceAdminPanel.setDirtyStore(true);
                }
                else {
                    // Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_map_tpl'), width: 300, align: 't'});     // "ERROR saving the Map template"
                    // me.templatename = '';
                }
                me.saveAs = false;
            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                // Ext.toast({hideDuration: 2000, html: result.message, title: esapp.Utils.getTranslation('error_save_map_tpl'), width: 300, align: 't'});     // "ERROR saving the Map template"
                me.saveAs = false;
            }
        });
    }

    ,newMapView: function() {
        var newMapViewWin = new esapp.view.analysis.mapView({
            workspace : this.getView()
        });
        this.getView().add(newMapViewWin);
        newMapViewWin.show();
    }

    ,layerAdmin: function(){
        var newLayerAdminWin = new esapp.view.analysis.layerAdmin();
        this.getView().add(newLayerAdminWin);
        newLayerAdminWin.show();
        // this.getView().lookupReference('analysismain_layersbtn').disable();
    }
    ,logosAdmin: function(){
        var newLogosAdminWin = new esapp.view.analysis.logoAdmin();
        this.getView().add(newLogosAdminWin);
        newLogosAdminWin.show();
        // this.getView().lookupReference('analysismain_logosbtn').disable();
    }
    ,legendAdmin: function(){
        var newLegendAdminWin = new esapp.view.analysis.legendAdmin();
        this.getView().add(newLegendAdminWin);
        newLegendAdminWin.show();
        // this.getView().lookupReference('analysismain_legendsbtn').disable();
    }

    ,showUserMaptemplates: function(btn){
        btn.mapTemplateAdminPanel.show();
    }

    ,showUserGraphTemplates: function(btn){
        btn.graphTemplateAdminPanel.show();
    }

    ,showTimeseriesChartSelection: function(){
        var timeseriesChartSelectionWindow = this.getView().lookupReference('timeserieschartselection'+this.getView().id);
        timeseriesChartSelectionWindow.show();

        // if (!esapp.Utils.objectExists(timeseriesChartSelectionWindow)) {
        //     this.getView().add({
        //         xtype: 'timeserieschartselection',
        //         reference: 'timeserieschartselection' + this.getView().id,
        //         workspace: this.getView()
        //     });
        //     timeseriesChartSelectionWindow = this.getView().lookupReference('timeserieschartselection'+this.getView().id);
        //     timeseriesChartSelectionWindow.show();
        //     // this.getView().add(new esapp.view.analysis.timeseriesChartSelection({
        //     //     reference: 'timeserieschartselection' + this.getView().id,
        //     //     workspace: this.getView()
        //     // }).show());
        // }
        // else{
        //     timeseriesChartSelectionWindow.show();
        // }
    }

    ,toggleBackgroundlayer: function(btn, event) {
        var analysismain = btn.up().up();
        var i, ii;
        var me = this.getView();

        if (!esapp.Utils.objectExists(analysismain.map)){
            me.map = new ol.Map({
                layers: me.backgroundLayers,
                // renderer: _getRendererFromQueryString(),
                projection:"EPSG:4326",
                displayProjection:"EPSG:4326",
                target: 'backgroundmap_'+ me.id,
                //overlays: [overlay],
                view: me.commonMapView,
                controls: ol.control.defaults({
                    zoom: false,
                    attribution:false,
                    attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                      collapsible: true // false to show always without the icon.
                    })
                }).extend([me.scaleline])   // me.mousePositionControl,
            });
            me.map.addInteraction(new ol.interaction.MouseWheelZoom({
              duration: 50
            }));
        }

        if (btn.pressed){
            btn.setText(esapp.Utils.getTranslation('hidebackgroundlayer'));
            analysismain.map.addControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                //analysismain.backgroundLayers[i].setVisible(analysismain.bingStyles[i] == 'Road');
                analysismain.backgroundLayers[i].setVisible(true);
            }
        }
        else {
            btn.setText(esapp.Utils.getTranslation('showbackgroundlayer'));
            analysismain.map.removeControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(false);
            }
        }
    }
});
