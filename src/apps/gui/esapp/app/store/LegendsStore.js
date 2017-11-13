Ext.define('esapp.store.LegendsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.legends',

    model: 'esapp.model.Legend',

    requires : [
        'esapp.model.Legend',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'LegendsStore'

    ,autoLoad: true
    ,autoSync: true
    // ,session: true

    ,sorters: {property: 'legend_descriptive_name', direction: 'ASC'}

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'legends',
            create: 'legends/create',
            update: 'legends/update',
            destroy: 'legends/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'legends'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'legend'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('LEGENDS STORE - REMOTE EXCEPTION');
            }
        }
    }
    ,listeners: {
        write: function(store, operation){
            // var result = Ext.JSON.decode(operation.getResponse().responseText);
            // if (operation.success) {
            //    //Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('legendupdated'), width: 200, align: 't' });
            // }
        }
    }

});