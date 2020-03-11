Ext.define('esapp.store.ProcessingStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.processing',

    model: 'esapp.model.Processing',

    requires : [
        'esapp.model.Processing',
        'Ext.data.proxy.Rest'
    ],

    storeId : 'ProcessingStore'

    ,autoLoad: false
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    //sorters: {property: 'productcode', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        appendId: false,
        api: {
            read: 'processing',
            create: 'processing/create',
            update: 'processing/update',
            destroy: 'processing/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'processes'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            allDataOptions: {
                associated: true
                ,changes: true
            },
            writeAllFields: false,
            appendId: true,
            rootProperty: 'processes'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('PROCESSING STORE - REMOTE EXCEPTION - Reload processing page!');

                //Ext.Msg.show({
                //    title: 'PROCESSING STORE - REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
    ,grouper:{
             groupFn : function (item) {
                 return esapp.Utils.getTranslation(item.get('category_id'));
                 //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
             },
             property: 'order_index',
             sortProperty: 'order_index'
    }
    ,listeners: {
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message,
                        title: esapp.Utils.getTranslation('processingchainupdated'),  // "Processing chain updated",  "Cha�ne de traitement mise � jour"
                        width: 300, align: 't' });
        }
    }

});