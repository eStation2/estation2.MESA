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
                Ext.MessageBox.show({
                    title: 'CATEGORIES MODEL- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
});
