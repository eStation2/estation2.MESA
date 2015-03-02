Ext.define('esapp.store.IngestionsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.ingestions',

    model: 'esapp.model.Ingestion',

    requires : [
        'esapp.model.Ingestion'
    ],

    storeId : 'IngestionsStore'

    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false

    ,sorters: {property: 'mapsetname', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        // url: 'ingestion',
        appendId: false,
        api: {
            read: 'ingestion',
            create: 'ingestion/create',
            update: 'ingestion/update',
            destroy: 'ingestion/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'ingestions'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'ingestions'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'INGESTION STORE - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }

    ,listeners: {
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message, title: "Ingestion update", width: 300, align: 't' });
        }
    }

});