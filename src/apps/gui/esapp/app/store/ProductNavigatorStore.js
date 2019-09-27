// STORE NOT USED ANYMORE! REMOVE THIS FILE?
// The Product Navigator is using a binding to the ProductNavigator Model!
Ext.define('esapp.store.ProductNavigatorStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.productnavigator',

    model: 'esapp.model.ProductNavigator',

    requires : [
        'esapp.model.ProductNavigator',
        'Ext.data.proxy.Rest'
    ],

    storeId : 'ProductNavigatorStore'

    ,autoLoad: true
    ,autoSync: false
    ,remoteSort: false
    ,remoteGroup: false
    ,loadMask: true

    ,sorters: [{property: 'order_index', direction: 'DESC'},{property: 'prod_descriptive_name', direction: 'ASC'},{property: 'version', direction: 'ASC'}]

    ,proxy: {
        type: 'rest',
        // url: '',
        appendId: false,
        actionMethods: {
            create: 'POST',
            read: 'GET',
            update: 'POST',
            destroy: 'POST'
        },
        api: {
            read: 'analysis/productnavigator',
            create: 'analysis/productnavigator/create',
            update: 'analysis/productnavigator/update',
            destroy: 'analysis/productnavigator/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'products'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            writeAllFields: true,
            rootProperty: 'products'
        },
        listeners: {
            exception: function(proxy, response, operation){
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('PRODUCT NAVIGATOR STORE - REMOTE EXCEPTION - Reopen or reload Product navigator!');

                //Ext.Msg.show({
                //    title: 'PRODUCT NAVIGATOR STORE - REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
    // ,grouper:{
    //          // property: 'cat_descr_name',
    //          groupFn : function (item) {
    //              return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'))
    //              //return item.get('cat_descr_name')
    //          },
    //          sortProperty: 'order_index'
    // }
    ,listeners: {
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 300, align: 't' });
        }
    }

});