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
        {name: 'get_eumetcast_output_dir'},
        {name: 'get_internet_output_dir'},
        {name: 'ingest_dir'},
        {name: 'eumetcast_files_dir'},
        {name: 'ingest_server_in_dir'},
        {name: 'host'},
        {name: 'port'},
        {name: 'dbuser'},
        {name: 'dbpass'},
        {name: 'dbname'},
        //{name: 'ip_pc1'},
        //{name: 'ip_pc2'},
        //{name: 'ip_pc3'},
        //{name: 'dns_ip'},
        //{name: 'gateway_ip'},
        //{name: 'lan_access_ip'},
        {name: 'type_installation'},
        {name: 'role'},
        {name: 'current_mode'},
        {name: 'active_version'},
        {name: 'thema'},
        {name: 'loglevel'},
        {name: 'log_general_level'},
        {name: 'proxy_host'},
        {name: 'proxy_port'},
        {name: 'proxy_user'},
        {name: 'proxy_userpwd'}
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
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('SYSTEM SETTINGS MODEL - REMOTE EXCEPTION - Reload System settings!');
                //Ext.Msg.show({
                //    title: 'SYSTEM SETTINGS MODEL - REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
    ,listeners: {
        update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
            Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
        },
        write: function(store, operation){
            if (operation.action == 'update' && operation.success) {
               Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
            }
        }
    }
});