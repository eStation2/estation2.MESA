Ext.define('esapp.store.MapsetsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.mapsets',

    requires : [
        'esapp.model.MapSet'
    ],

    model: 'esapp.model.MapSet',

    storeId : 'mapsets'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'getmapsetsall',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'mapsets'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('MAPSETS STORE - REMOTE EXCEPTION');
            }
        }
    }
});
