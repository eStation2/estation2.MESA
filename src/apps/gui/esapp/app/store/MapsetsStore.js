Ext.define('esapp.store.MapsetsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.mapsets',

    requires : [
        'esapp.model.MapSet'
    ],

    model: 'esapp.model.MapSet',

    storeId : 'mapsets'

    ,autoLoad: true
    ,autoSync: false
    ,remoteSort: false
    ,remoteGroup: false
    ,loadMask: true
    ,session: false

    ,sorters: {property: 'mapsetcode', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        appendId: false,
        api: {
            read: 'mapsets/getmapsetsall',
            create: 'mapsets/create',
            update: 'mapsets/update',
            destroy: 'mapsets/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'mapsets'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'mapsets'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('MAPSETS STORE - REMOTE EXCEPTION');
            }
        }
    }

    // ,proxy: {
    //     type : 'ajax',
    //     url : 'getmapsetsall',
    //     reader: {
    //          type: 'json'
    //         ,successProperty: 'success'
    //         ,rootProperty: 'mapsets'
    //         ,messageProperty: 'message'
    //     },
    //     listeners: {
    //         exception: function(proxy, response, operation){
    //             // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
    //             console.info('MAPSETS STORE - REMOTE EXCEPTION');
    //         }
    //     }
    // }
});
