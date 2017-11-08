Ext.define('esapp.store.LayersStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.layers',

    model: 'esapp.model.Layer',

    requires : [
        'esapp.model.Layer',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'LayersStore'

    ,autoLoad: true
    ,autoSync: true
    // ,session: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'layers',
            create: 'layers/create',
            update: 'layers/update',
            destroy: 'layers/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'layers'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'layer'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('LAYERS STORE - REMOTE EXCEPTION');
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
               //Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('layerupdated'), width: 200, align: 't' });
            }
        }
    }

});