Ext.define('esapp.store.ResolutionsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.resolutions',

    requires : [
        'esapp.model.Resolution'
    ],

    model: 'esapp.model.Resolution',

    storeId : 'ResolutionsStore'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'resolutions',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'resolutions'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('RESOLUTIONS STORE - REMOTE EXCEPTION!');
            }
        }
    }
});