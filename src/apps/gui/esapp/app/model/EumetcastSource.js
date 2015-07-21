Ext.define('esapp.model.EumetcastSource', {
    extend: 'esapp.model.Base',
    
    requires : [
        'Ext.data.proxy.Rest'
    ],

    fields: [
        {name: 'eumetcast_id'},
        {name: 'collection_name'},
        {name: 'filter_expression_jrc'},
        {name: 'description'},
        {name: 'typical_file_name'},
        {name: 'keywords_theme'},
        {name: 'keywords_societal_benefit_area'},
        {name: 'datasource_descr_id'},
        {name: 'format_type'},
        {name: 'file_extension'},
        {name: 'delimiter'},
        {name: 'date_type'},
        {name: 'date_position'},
        {name: 'product_identifier'},
        {name: 'prod_id_position'},
        {name: 'prod_id_length'},
        {name: 'area_type'},
        {name: 'area_position'},
        {name: 'area_length'},
        {name: 'preproc_type'},
        {name: 'product_release'},
        {name: 'release_position'},
        {name: 'release_length'},
        {name: 'native_mapset'}
    ]

    ,autoLoad: true
    ,autoSync: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'eumetcastsource',
            create: 'eumetcastsource/create',
            update: 'eumetcastsource/update',
            destroy: 'eumetcastsource/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'eumetcastsources'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'eumetcastsources'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'EUMETCAST SOURCE MODEL - REMOTE EXCEPTION',
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
