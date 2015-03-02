Ext.define('esapp.store.ProductsActiveStore', {
     extend  : 'Ext.data.Store'
    ,alias: 'store.productsactive'

    ,requires : [
        'esapp.model.Product',
        'Ext.data.proxy.Rest'
    ]
    ,model: 'esapp.model.Product'

    ,storeId : 'ProductsActiveStore'

    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    ,proxy: {
        type: 'rest',
        // url: 'pa',
        appendId: false,
        extraParams:{
            activated:'True'
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
                    title: 'PRODUCTS ACTIVE STORE - REMOTE EXCEPTION',
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
//            Ext.toast({ html: 'Store update! Checkbox clicked!', title: 'Activate Product', width: 200, align: 't' });
//            if (operation == 'commit') {
//                store.remove(record);
//            }
//            console.info('store');
//            console.info(store);
//            console.info('record');
//            console.info(record);
//            console.info('operation');
//            console.info(operation);
//            console.info('modifiedFieldNames');
//            console.info(modifiedFieldNames);
//            console.info('details');
//            console.info(details);
//            console.info('eOpts');
//            console.info(eOpts);
        },
        write: function(store, operation){
            if (operation.action == 'update' && operation.success) {
                var records = operation.getRecords();
                store.suspendAutoSync();
                store.remove(records[0], true);
                store.resumeAutoSync();
            }
//            if (operation.action == 'destroy') {
//                // main.child('#form').setActiveRecord(null);
//            }
//            Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
        }
    }

});
