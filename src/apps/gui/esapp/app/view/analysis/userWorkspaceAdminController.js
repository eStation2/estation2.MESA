Ext.define('esapp.view.analysis.userWorkspaceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-userworkspaceadmin'

    ,openWorkspaces: function(){
        var me = this.getView();
        var selectedWorkspaces = me.getSelectionModel().getSelection();
        var analysismainWorkspaceTabPanel = me.owner.up().up().up();
        var analysisWorkspaces = Ext.ComponentQuery.query('analysisworkspace');
        var alreadyOpen = false;
        var workspaceTabToActivate = null;

        for (var i = 0; i < selectedWorkspaces.length; i++) {
           // console.info(selectedWorkspaces[i]);
            Ext.Object.each(analysisWorkspaces, function(id, workspace, thisObj) {
                if (workspace.workspaceid == selectedWorkspaces[i].data.workspaceid){
                    alreadyOpen = true;
                    workspaceTabToActivate = workspace;
                }
            });
            if (!alreadyOpen){
                analysismainWorkspaceTabPanel.getController().openWorkspace(selectedWorkspaces[i], true);
            }
            else {
                // activate workspace tab
                analysismainWorkspaceTabPanel.setActiveTab(workspaceTabToActivate);
            }
        }
        me.hide();
    }

    ,newWorkspace: function(){
        var me = this.getView();
        var analysismainWorkspaceTabPanel = me.owner.up().up().up();
        analysismainWorkspaceTabPanel.getController().addNewWorkspace();
        me.hide();
    }

    ,deleteWorkspace: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        grid.getStore().remove(record);
    }
});
