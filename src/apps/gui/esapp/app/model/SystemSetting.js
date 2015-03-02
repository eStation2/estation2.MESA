Ext.define('esapp.model.SystemSetting', {
    extend : 'esapp.model.Base',

    requires : [
        'Ext.data.proxy.Rest'
    ],

    fields: [
       {name: 'base_dir'},
       {name: 'base_tmp_dir'},
       {name: 'data_dir'},
       {name: 'static_data_dir'},
       {name: 'archive_dir'},
       {name: 'ingest_dir'},
       {name: 'eumetcast_files_dir'},
       {name: 'ingest_server_in_dir'},
       {name: 'host'},
       {name: 'port'},
       {name: 'dbuser'},
       {name: 'dbpass'},
       {name: 'dbname'}
    ]

    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'systemsettings',
            create: 'systemsettings/create',
            update: 'systemsettings/update',
            destroy: 'systemsettings/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'systemsettings'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'systemsettings'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'SYSTEM SETTINGS MODEL - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
    ,listeners: {
        update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
            Ext.toast({ html: "Update: "+operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
        },
        write: function(store, operation){
            if (operation.action == 'update' && operation.success) {
               Ext.toast({ html: "Write: "+operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
            }
        }
    }
});