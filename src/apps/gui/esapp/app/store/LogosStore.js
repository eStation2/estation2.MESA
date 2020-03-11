Ext.define('esapp.store.LogosStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.logos',

    model: 'esapp.model.Logo',

    requires : [
        'esapp.model.Logo',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'LogosStore'

    ,autoLoad: true
    ,autoSync: true
    // ,session: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'logos',
            create: 'logos/create',
            update: 'logos/update',
            destroy: 'logos/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'logos'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'logo'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('LOGOS STORE - REMOTE EXCEPTION');
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
               //Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('logoupdated'), width: 200, align: 't' });
            }
        }
    }

});