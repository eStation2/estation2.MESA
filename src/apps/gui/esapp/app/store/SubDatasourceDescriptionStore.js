Ext.define('esapp.store.SubDatasourceDescriptionStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.subdatasourcedescription',

    model: 'esapp.model.SubDatasourceDescription',

    requires : [
        'esapp.model.SubDatasourceDescription',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'SubDatasourceDescriptionStore'

    ,autoLoad: true
    ,autoSync: false
    //,session: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'subdatasourcedescription',
            create: 'subdatasourcedescription/create',
            update: 'subdatasourcedescription/update',
            destroy: 'subdatasourcedescription/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'subdatasourcedescription'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'subdatasourcedescription'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('SUB DATASOURCE DESCRIPTION STORE - REMOTE EXCEPTION!');

                //Ext.Msg.show({
                //    title: 'SUB DATASOURCE DESCRIPTION STORE - REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
    ,listeners: {
        //update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
        //    // This event is triggered on every change made in a record!
        //},
        write: function(store, operation){
            var result = Ext.JSON.decode(operation.getResponse().responseText);
            if (operation.success) {
               Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('subdatasourcedescriptionupdated'), width: 200, align: 't' });
            }
        }
    }

});