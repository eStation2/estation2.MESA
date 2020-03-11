Ext.define('esapp.model.EumetcastSource', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'eumetcast_id'},
        {name: 'orig_eumetcast_id'},
        {name: 'collection_name'},
        {name: 'filter_expression_jrc'},
        {name: 'frequency'},
        {name: 'description'},
        {name: 'typical_file_name'},
        {name: 'keywords_theme'},
        {name: 'keywords_societal_benefit_area'},
        {name: 'defined_by'},
        {name: 'datasource_descr_id'},
        {name: 'format_type'},
        {name: 'file_extension'},
        {name: 'delimiter'},
        {name: 'date_format'},
        {name: 'date_position'},
        {name: 'product_identifier'},
        {name: 'prod_id_position', type: 'number'},
        {name: 'prod_id_length', type: 'number'},
        {name: 'area_type'},
        {name: 'area_position'},
        {name: 'area_length', type: 'number'},
        {name: 'preproc_type'},
        {name: 'product_release'},
        {name: 'release_position'},
        {name: 'release_length', type: 'number'},
        {name: 'native_mapset'}
    ]

    //,requires : [
    //    'Ext.data.proxy.Rest'
    //]
    //
    //,autoLoad: true
    //,autoSync: false
    //
    //,proxy: {
    //    type: 'rest',
    //
    //    appendId: false,
    //
    //    api: {
    //        read: 'eumetcastsource',
    //        create: 'eumetcastsource/create',
    //        update: 'eumetcastsource/update',
    //        destroy: 'eumetcastsource/delete'
    //    },
    //    reader: {
    //         type: 'json'
    //        ,successProperty: 'success'
    //        ,rootProperty: 'eumetcastsources'
    //        ,messageProperty: 'message'
    //    },
    //    writer: {
    //        type: 'json',
    //        writeAllFields: true,
    //        rootProperty: 'eumetcastsources'
    //    },
    //    listeners: {
    //        exception: function(proxy, response, operation){
    //            // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
    //            Ext.Msg.show({
    //                title: 'EUMETCAST SOURCE MODEL - REMOTE EXCEPTION',
    //                msg: operation.getError(),
    //                icon: Ext.Msg.ERROR,
    //                buttons: Ext.Msg.OK
    //            });
    //        }
    //    }
    //}
    //,listeners: {
    //    update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
    //        Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
    //    },
    //    write: function(store, operation){
    //        if (operation.action == 'update' && operation.success) {
    //           Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
    //        }
    //    }
    //}
});
