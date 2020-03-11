Ext.define('esapp.store.ProjectionsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.projections',

    requires : [
        'esapp.model.Projection'
    ],

    model: 'esapp.model.Projection',

    storeId : 'ProjectionsStore'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'projections',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'projections'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('PROJECTIONS STORE - REMOTE EXCEPTION!');
            }
        }
    }
});