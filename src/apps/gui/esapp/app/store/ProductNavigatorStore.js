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

    ,sorters: {property: 'order_index', direction: 'DESC'}

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
                Ext.MessageBox.show({
                    title: 'PRODUCT NAVIGATOR STORE - REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
    ,grouper:{
             // property: 'cat_descr_name',
             groupFn : function (item) {
                 return "<span style='display: none;'>" + item.get('order_index') + "</span>" + item.get('cat_descr_name')
                 //return item.get('cat_descr_name')
             },
             sortProperty: 'order_index'
    }
    ,listeners: {
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 300, align: 't' });
        }
    }

});