Ext.define('esapp.store.InternetSourceStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.internetsource',

    model: 'esapp.model.InternetSource',

    requires : [
        'esapp.model.InternetSource',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'InternetSourceStore'

    ,autoLoad: true
    ,autoSync: false
    //,session: true

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'internetsource',
            create: 'internetsource/create',
            update: 'internetsource/update',
            destroy: 'internetsource/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'internetsources'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'internetsources'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('INTERNET SOURCE STORE - REMOTE EXCEPTION - Reopen edit internet source window!');

                //Ext.Msg.show({
                //    title: 'INTERNET SOURCE STORE - REMOTE EXCEPTION',
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
               Ext.toast({ html: result.message, title: esapp.Utils.getTranslation('datasourceupdated'), width: 200, align: 't' });
            }
        }
    }

});