Ext.define('esapp.store.EumetcastSourceStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.eumetcastsource',

    model: 'esapp.model.EumetcastSource',

    requires : [
        'esapp.model.EumetcastSource',

        'Ext.data.proxy.Rest'
    ],

    storeId : 'EumetcastSourceStore'

    ,autoLoad: true
    ,autoSync: false
    // ,session: false

    ,proxy: {
        type: 'rest',

        appendId: false,

        api: {
            read: 'eumetcastsource',
            create: 'eumetcastsource/create',
            update: 'eumetcastsource/update',
            destroy: 'eumetcastsource/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'eumetcastsources'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'eumetcastsources'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('EUMETCAST SOURCE STORE - REMOTE EXCEPTION - Reopen window edit eumetcast datasource!');

                //Ext.Msg.show({
                //    title: 'EUMETCAST SOURCE MODEL - REMOTE EXCEPTION',
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