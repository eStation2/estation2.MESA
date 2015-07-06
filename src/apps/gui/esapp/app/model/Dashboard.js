Ext.define('esapp.model.Dashboard', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'type_installation', type: 'string', mapping: 'type_installation'},
        {name: 'activePC', type: 'string', mapping: 'activePC'},
        {name: 'pc1_connection', type: 'boolean', mapping: 'pc1_connection'},
        {name: 'pc3_connection', type: 'boolean', mapping: 'pc3_connection'},
        {name: 'PC2_version', type: 'string', mapping: 'PC2_version'},
        {name: 'PC2_mode', type: 'string', mapping: 'PC2_mode'},
        {name: 'PC2_postgresql_status', type: 'boolean', mapping: 'PC2_postgresql_status'},
        {name: 'PC2_internet_status',type: 'boolean',  mapping: 'PC2_internet_status'},
        {name: 'PC3_version', type: 'string', mapping: 'PC3_version'},
        {name: 'PC3_mode', type: 'string', mapping: 'PC3_mode'},
        {name: 'PC3_postgresql_status', type: 'boolean', mapping: 'PC3_postgresql_status'},
        {name: 'PC3_internet_status', type: 'boolean', mapping: 'PC3_internet_status'}
    ]

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'dashboard/getdashboard',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'dashboard'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'DASHBOARD MODEL- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

});

