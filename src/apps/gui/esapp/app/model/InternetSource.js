Ext.define('esapp.model.InternetSource', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'internet_id'},
        {name: 'orig_internet_id'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'modified_by'},
        {name: 'update_datetime'},
        {name: 'url'},
        {name: 'user_name'},
        {name: 'password'},
        {name: 'type'},
        {name: 'include_files_expression'},
        {name: 'files_filter_expression'},
        {name: 'status', type: 'boolean'},
        {name: 'pull_frequency', type: 'number'},
        {name: 'frequency_id'},
        {name: 'start_date', type: 'number'},   // , type: 'number', useNull : true, defaultValue: null
        {name: 'end_date', type: 'number'},
        {name: 'https_params'},
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
    //        read: 'internetsource',
    //        create: 'internetsource/create',
    //        update: 'internetsource/update',
    //        destroy: 'internetsource/delete'
    //    },
    //    reader: {
    //         type: 'json'
    //        ,successProperty: 'success'
    //        ,rootProperty: 'internetsources'
    //        ,messageProperty: 'message'
    //    },
    //    writer: {
    //        type: 'json',
    //        writeAllFields: true,
    //        rootProperty: 'internetsources'
    //    },
    //    listeners: {
    //        exception: function(proxy, response, operation){
    //            // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
    //            Ext.Msg.show({
    //                title: 'INTERNET SOURCE MODEL - REMOTE EXCEPTION',
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
