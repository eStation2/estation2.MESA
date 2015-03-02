Ext.define('esapp.store.ProductsInactiveStore', {
     extend  : 'Ext.data.Store'
    ,alias: 'store.productsinactive'

    ,requires : [
        'esapp.model.Product'
    ]
    ,model: 'esapp.model.Product'

    ,storeId : 'ProductsInactiveStore'

    ,autoLoad: false
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    ,proxy: {
        type: 'rest',
        // url: 'pa',
        appendId: false,
        extraParams:{
            activated:'False'
        },
        api: {
            read: 'pa',
            create: 'product/create',
            update: 'product/update',
            destroy: 'product/delete'
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
                    title: 'PRODUCTS INACTIVE STORE - REMOTE EXCEPTION',
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
//                                "</span><span class='group-header-style'>" + item.get('cat_descr_name') + "</span>"
             },
             sortProperty: 'order_index'
    }

    ,listeners: {
        update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){

        },
        write: function(store, operation){
            if (operation.action == 'update' && operation.success) {
                var records = operation.getRecords();
                store.suspendAutoSync();
                store.remove(records[0], true);
                store.resumeAutoSync();
            }
//            Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
        }
    }

});
