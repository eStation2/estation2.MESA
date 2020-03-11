Ext.define('esapp.model.IPSetting', {
    extend : 'esapp.model.Base',

    requires : [
        'Ext.data.proxy.Rest'
    ],

    fields: [
        {name: 'ip_pc1'},
        {name: 'ip_pc2'},
        {name: 'ip_pc3'},
        {name: 'dns_ip'},
        {name: 'gateway_ip'},
        {name: 'lan_access_ip'},
        {name: 'type_installation'},
        {name: 'role'}
    ]

    ,autoLoad: false
    ,autoSync: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'systemsettings/ipsettings',
            create: 'systemsettings/ipsettings/create',
            update: 'systemsettings/ipsettings/update',
            destroy: 'systemsettings/ipsettings/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'ipsettings'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'ipsettings'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('IP SETTINGS MODEL- REMOTE EXCEPTION - Reload System page!');
                //Ext.Msg.show({
                //    title: 'IP SETTINGS MODEL - REMOTE EXCEPTION',
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