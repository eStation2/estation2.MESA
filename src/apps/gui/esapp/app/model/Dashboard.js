Ext.define('esapp.model.Dashboard', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'type_installation', type: 'string', mapping: 'type_installation'},
        {name: 'activePC', type: 'string', mapping: 'activePC'},
        {name: 'PC1_connection', type: 'boolean', mapping: 'PC1_connection'},
        {name: 'PC23_connection', type: 'boolean', mapping: 'PC23_connection'},

        {name: 'PC1_dvb_status', mapping: 'PC1_dvb_status'},
        {name: 'PC1_tellicast_status', mapping: 'PC1_tellicast_status'},
        {name: 'PC1_fts_status', mapping: 'PC1_fts_status'},

        {name: 'PC2_service_eumetcast', mapping: 'PC2_service_eumetcast'},
        {name: 'PC2_service_internet', mapping: 'PC2_service_internet'},
        {name: 'PC2_service_ingest', mapping: 'PC2_service_ingest'},
        {name: 'PC2_service_processing', mapping: 'PC2_service_processing'},
        {name: 'PC2_service_system', mapping: 'PC2_service_system'},
        {name: 'PC2_version', type: 'string', mapping: 'PC2_version'},
        {name: 'PC2_mode', type: 'string', mapping: 'PC2_mode'},
        {name: 'PC2_postgresql_status', mapping: 'PC2_postgresql_status'},
        {name: 'PC2_internet_status', mapping: 'PC2_internet_status'},
        {name: 'PC2_disk_status', mapping: 'PC2_disk_status'},
        {name: 'PC2_DBAutoSync', mapping: 'PC2_DBAutoSync'},
        {name: 'PC2_DataAutoSync', mapping: 'PC2_DataAutoSync'},

        {name: 'PC3_service_eumetcast', mapping: 'PC3_service_eumetcast'},
        {name: 'PC3_service_internet', mapping: 'PC3_service_internet'},
        {name: 'PC3_service_ingest', mapping: 'PC3_service_ingest'},
        {name: 'PC3_service_processing', mapping: 'PC3_service_processing'},
        {name: 'PC3_service_system', mapping: 'PC3_service_system'},
        {name: 'PC3_version', type: 'string', mapping: 'PC3_version'},
        {name: 'PC3_mode', type: 'string', mapping: 'PC3_mode'},
        {name: 'PC3_postgresql_status', mapping: 'PC3_postgresql_status'},
        {name: 'PC3_internet_status', mapping: 'PC3_internet_status'},
        {name: 'PC3_disk_status', mapping: 'PC3_disk_status'},
        {name: 'PC3_DBAutoSync', mapping: 'PC3_DBAutoSync'},
        {name: 'PC3_DataAutoSync', mapping: 'PC3_DataAutoSync'}
    ]

    //fields: [
    //    {name: 'type_installation', type: 'string', mapping: 'type_installation'},
    //    {name: 'activePC', type: 'string', mapping: 'activePC'},
    //    {name: 'PC1_connection', type: 'boolean', mapping: 'PC1_connection'},
    //    {name: 'PC23_connection', type: 'boolean', mapping: 'PC23_connection'},
    //
    //    {name: 'PC2_service_eumetcast', type: 'boolean', mapping: 'PC2_service_eumetcast'},
    //    {name: 'PC2_service_internet', type: 'boolean', mapping: 'PC2_service_internet'},
    //    {name: 'PC2_service_ingest', type: 'boolean', mapping: 'PC2_service_ingest'},
    //    {name: 'PC2_service_processing', type: 'boolean', mapping: 'PC2_service_processing'},
    //    {name: 'PC2_service_system', type: 'boolean', mapping: 'PC2_service_system'},
    //    {name: 'PC2_version', type: 'string', mapping: 'PC2_version'},
    //    {name: 'PC2_mode', type: 'string', mapping: 'PC2_mode'},
    //    {name: 'PC2_postgresql_status', type: 'boolean', mapping: 'PC2_postgresql_status'},
    //    {name: 'PC2_internet_status',type: 'boolean',  mapping: 'PC2_internet_status'},
    //    {name: 'PC2_disk_status',type: 'boolean',  mapping: 'PC2_disk_status'},
    //
    //    {name: 'PC3_service_eumetcast', type: 'boolean', mapping: 'PC3_service_eumetcast'},
    //    {name: 'PC3_service_internet', type: 'boolean', mapping: 'PC3_service_internet'},
    //    {name: 'PC3_service_ingest', type: 'boolean', mapping: 'PC3_service_ingest'},
    //    {name: 'PC3_service_processing', type: 'boolean', mapping: 'PC3_service_processing'},
    //    {name: 'PC3_service_system', type: 'boolean', mapping: 'PC3_service_system'},
    //    {name: 'PC3_version', type: 'string', mapping: 'PC3_version'},
    //    {name: 'PC3_mode', type: 'string', mapping: 'PC3_mode'},
    //    {name: 'PC3_postgresql_status', type: 'boolean', mapping: 'PC3_postgresql_status'},
    //    {name: 'PC3_internet_status', type: 'boolean', mapping: 'PC3_internet_status'},
    //    {name: 'PC3_disk_status',type: 'boolean',  mapping: 'PC3_disk_status'}
    //]
    //
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
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('DASHBOARD MODEL- REMOTE EXCEPTION - Reload dashboard!');
                //Ext.Msg.show({
                //    title: 'DASHBOARD MODEL- REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }

});

