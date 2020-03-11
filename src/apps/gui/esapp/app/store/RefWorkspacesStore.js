Ext.define('esapp.store.RefWorkspacesStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.refworkspaces',

    model: 'esapp.model.UserWorkspace',

    requires : [
        'esapp.model.UserWorkspace',
        'Ext.data.proxy.Rest'
    ],

    storeId : 'RefWorkspacesStore',

    autoLoad: true,
    autoSync: false,
    // session: true,

    sorters: [{
        property: 'showindefault',
        direction: 'DESC'
    },{
        property: 'workspacename',
        direction: 'ASC'
    }],

    proxy: {
        type: 'rest',

        appendId: false,

        //extraParams: {
        //    userid: null    // esapp.getUser().userid  // 'jurvtk'
        //},

        api: {
            read: 'analysis/refworkspaces',
            create: 'analysis/refworkspaces/create',
            update: 'analysis/refworkspaces/update',
            destroy: 'analysis/refworkspaces/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'refworkspaces'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true
            // ,rootProperty: 'refworkspaces'
        },
        listeners: {
            exception: function(proxy, response, operation){
                console.info('REFERENCE WORKSPACE STORE - REMOTE EXCEPTION - Error querying the reference workspaces!');
            }
        }
    },
    listeners: {
        remove: function(store, record,  index , isMove , eOpts  ){

        },
        update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
            // console.info(store);
            // console.info(record);
            // console.info(operation);
            // console.info(modifiedFieldNames);
            // console.info(details);
            // This event is triggered on every change made in a record!
            // var result = Ext.JSON.decode(operation.getResponse().responseText);
            // if (operation.success) {
            //     Ext.toast({html: operation.getRecords()[0].get('workspacename') + ' ' + esapp.Utils.getTranslation('updated'), title: esapp.Utils.getTranslation('workspace_updated'), width: 300, align: 't'});   // "Workspace updated"
            // }
        },
        write: function(store, operation){

        }
    }

});