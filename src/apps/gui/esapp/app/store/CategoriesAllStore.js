Ext.define('esapp.store.CategoriesAllStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.categoriesall',

    requires : [
        'esapp.model.Category'
    ],

    model: 'esapp.model.Category',

    storeId : 'categoriesall'

    ,autoLoad: true

    ,proxy: {
        type : 'ajax',
        url : 'categories',
        extraParams: {all: true},
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'categories'
            //,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('CATEGORIES STORE - REMOTE EXCEPTION - Reopen window (edit datasource or edit product!');

                //Ext.Msg.show({
                //    title: 'CATEGORIES STORE- REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
});
