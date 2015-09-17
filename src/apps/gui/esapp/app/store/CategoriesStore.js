Ext.define('esapp.store.CategoriesStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.categories',

    requires : [
        'esapp.model.Category'
    ],

    model: 'esapp.model.Category',

    storeId : 'categories'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'categories',
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'categories'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                Ext.Msg.show({
                    title: 'CATEGORIES STORE- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
});
