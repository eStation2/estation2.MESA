Ext.define('esapp.view.analysis.userWorkspaceAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-userworkspaceadmin',
    stores: {
        userworkspaces: {
            source:'UserWorkspacesStore',
            session: true
        },
        refworkspaces: {
            source:'RefWorkspacesStore',
            session: true
        }
    }

});
