Ext.define('esapp.view.analysis.userWorkspaceAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-userworkspaceadmin',
    stores: {
        userworkspaces: {
            source:'UserWorkspacesStore'
            // model: 'esapp.model.UserWorkspace',
            // autoLoad: false,
            // autoSync: true,
            // session: true,
            // storeId: 'userworkspaces',
            //
            // sorters: [{
            //     property: 'workspacename',
            //     direction: 'ASC'
            // }],
            //
            // proxy: {
            //     type: 'rest',
            //
            //     appendId: false,
            //
            //     //extraParams: {
            //     //    userid: null    // esapp.getUser().userid  // 'jurvtk'
            //     //},
            //
            //     api: {
            //         read: 'analysis/userworkspaces',
            //         create: 'analysis/userworkspaces/create',
            //         update: 'analysis/userworkspaces/update',
            //         destroy: 'analysis/userworkspaces/delete'
            //     },
            //     reader: {
            //          type: 'json'
            //         ,successProperty: 'success'
            //         ,rootProperty: 'userworkspaces'
            //         ,messageProperty: 'message'
            //     },
            //     writer: {
            //         type: 'json',
            //         writeAllFields: true,
            //         rootProperty: 'userworkspace'
            //     },
            //     listeners: {
            //         exception: function(proxy, response, operation){
            //             console.info('USER WORKSPACE VIEW MODEL - REMOTE EXCEPTION - Error querying the users workspaces!');
            //         }
            //     }
            // }
            // ,listeners: {
            //     remove: function(store, record,  index , isMove , eOpts  ){
            //
            //     },
            //     update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
            //         // This event is triggered on every change made in a record!
            //     },
            //     write: function(store, operation){
            //         var result = Ext.JSON.decode(operation.getResponse().responseText);
            //         if (operation.success) {
            //             Ext.toast({html: operation.getRecords()[0].get('workspacename') + ' ' + esapp.Utils.getTranslation('deleted'), title: esapp.Utils.getTranslation('workspace_deleted'), width: 300, align: 't'});   // "Workspace deleted"
            //         }
            //     }
            // }
        }
    }

});
