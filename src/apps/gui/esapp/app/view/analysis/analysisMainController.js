Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,showUserWorkspaceAdmin: function(btn){
        // console.info(btn);
        btn.userWorkspaceAdminPanel.show();
    }

    ,showRefWorkspaceAdmin: function(btn){
        // console.info(btn);
        btn.refWorkspaceAdminPanel.show();
    }

    ,openWorkspace: function(workspace, activateTab){
        var me = this.getView();
        var analysisWorkspaces = Ext.ComponentQuery.query('analysisworkspace');
        var wsdata = workspace.getData();
        // console.info(wsdata);

        var params = {
            'userid': wsdata['userid'],
            'workspaceid': wsdata['workspaceid'],
            'workspacename': wsdata['workspacename'],
            'pinned': wsdata['pinned'],
            'showindefault': wsdata['showindefault'],
            'shownewgraph': wsdata['shownewgraph'],
            'showbackgroundlayer': wsdata['showbackgroundlayer'],
            'isrefworkspace': wsdata['isrefworkspace']
        }

        // console.info(params);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/workspacemapsgraphs',
            params: params,
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                if (result.success){
                    workspace.set('maps',result.workspace.maps);
                    workspace.set('graphs', result.workspace.graphs);
                    workspace.dirty = false;
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });

        // console.info(workspace);
        var task = new Ext.util.DelayedTask(function() {
            if (workspace.get('showindefault')){
                var defaultworkspace = null;
                Ext.Object.each(analysisWorkspaces, function(id, ws, thisObj) {
                    if (ws.workspaceid == 'defaultworkspace'){
                        // ws.setTitle(workspace.get('workspacename'));
                        ws.setMaps(workspace.get('maps'));
                        ws.setGraphs(workspace.get('graphs'));

                        ws.getController().closeAllMapsGraphs();
                        if (ws.maps.length > 0) {
                            ws.getController().openWorkspaceMaps(ws.maps);
                        }
                        if (ws.graphs.length > 0) {
                            ws.getController().openWorkspaceGraphs(ws.graphs);
                        }
                    }
                });
            }
            else {
                me.tabBar.items.length
                var tab = me.insert(me.tabBar.items.length, {
                    xtype: 'analysisworkspace',
                    workspaceid: workspace.get('workspaceid'),
                    workspacename: workspace.get('workspacename'),
                    isNewWorkspace: false,
                    title: workspace.get('workspacename'),
                    closable: false,
                    titleEditable: true,
                    pinable: true,
                    pinned: workspace.get('pinned'),
                    maps: workspace.get('maps'),
                    graphs: workspace.get('graphs'),
                    isrefworkspace: workspace.get('isrefworkspace')
                });

                if (activateTab){
                    me.setActiveTab(tab);
                }
            }
        });
        task.delay(2000);

    }

    ,addNewWorkspace: function() {
        var me = this.getView();
        var tab = me.add({
            xtype: 'analysisworkspace',
            workspacename: 'New workspace',
            title: 'New workspace',
            closable: true,
            titleEditable: true,
            pinable: true,
            pinned: false,
            isrefworkspace: false
            // tabConfig: {
            //     itemId: 'TabNewWorkspace',
            //     cls:'newworkspacetab'
            // }
            // listeners : {
            //     close: function() {
            //         console.info(me.items);
            //         if (me.items.length == 2) {
            //             me.getTabBar().hide();
            //         }
            //     }
            // }
        });

        me.setActiveTab(tab);

        if (me.items.length == 1){
            me.getTabBar().hide();
        }
        else {
            me.getTabBar().show();
        }
    }

});
