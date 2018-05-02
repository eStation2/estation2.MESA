Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,showUserWorkspaceAdmin: function(btn){
        btn.userWorkspaceAdminPanel.show();
    }

    ,openWorkspace: function(workspace, activateTab){
        var me = this.getView();
        // console.info(workspace);
        var tab = me.add({
            xtype: 'analysisworkspace',
            workspaceid: workspace.get('workspaceid'),
            workspacename: workspace.get('workspacename'),
            isNewWorkspace: false,
            title: workspace.get('workspacename'),
            closable: true,
            titleEditable: true,
            pinable: true,
            pinned: workspace.get('pinned'),
            maps: workspace.get('maps'),
            graphs: workspace.get('graphs')
        });
        if (activateTab){
            me.setActiveTab(tab);
        }
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
            pinned: false
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
