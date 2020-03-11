Ext.define('esapp.store.IngestSubProductsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.ingestsubproducts',

    model: 'esapp.model.IngestSubProduct',

    requires : [
        'esapp.model.IngestSubProduct'
    ],

    storeId : 'IngestSubProductsStore'

    ,autoLoad: false
    ,autoSync: false
    ,remoteSort: false

    // ,sorters: {property: 'productid', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        appendId: false,
        api: {
            read: 'ingestsubproduct',
            create: 'ingestsubproduct/create',
            update: 'ingestsubproduct/update',
            destroy: 'ingestsubproduct/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'ingestsubproducts'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'ingestproduct'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('INGEST SUB PRODUCT STORE - REMOTE EXCEPTION - Error deleting Ingest Sub Product');

                // Ext.Msg.show({
                //    title: 'INGEST SUB PRODUCT STORE - REMOTE EXCEPTION - Error deleting Ingest Sub Product',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                // });
                // gridStore.add(gridStore.getRemovedRecords());
            }
        }
    }

    ,listeners: {
        write: function(store, operation){
            // Ext.toast({ html: operation.getResultSet().message,
            //             title: esapp.Utils.getTranslation('ingestproductupdated'),  // "Ingest product updated",
            //             width: 300, align: 't' });
        }
    }

});