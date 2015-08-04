Ext.define('esapp.store.LanguagesStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.languages',

    requires : [
        'esapp.model.Language'
    ],

    model: 'esapp.model.Language',

    storeId : 'LanguagesStore'

    //session: true,
    ,autoLoad: false
    //,remoteSort: false

    //sorters: {property: 'langcode', direction: 'ASC'}

    ,proxy: {
        type : 'ajax',
        url : 'getlanguages',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'languages'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.Msg.show({
                    title: 'LANGUAGES STORE- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
});
