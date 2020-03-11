Ext.define('esapp.store.ProductsInactiveStore', {
     extend  : 'Ext.data.Store'
    ,alias: 'store.productsinactive'

    ,requires : [
        'esapp.model.Product'
    ]
    ,model: 'esapp.model.Product'

    ,storeId : 'ProductsInactiveStore'

    ,autoLoad: true
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
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('PRODUCTS ACTIVE STORE - REMOTE EXCEPTION - Reload or reopen Activate product window!');

                //Ext.Msg.show({
                //    title: 'PRODUCTS INACTIVE STORE - REMOTE EXCEPTION',
                //    msg: operation.getError(),
                //    icon: Ext.Msg.ERROR,
                //    buttons: Ext.Msg.OK
                //});
            }
        }
    }
    ,grouper:{
        groupFn : function (item) {
            return esapp.Utils.getTranslation(item.get('category_id'));
            //return "<span style='display: none;'>" + item.get('order_index') + "</span>" + esapp.Utils.getTranslation(item.get('category_id'));
            //            "</span><span class='group-header-style'>" + item.get('cat_descr_name') + "</span>"
        },
        property: 'order_index',
        sortProperty: 'order_index'
    }

    ,listeners: {
        // update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
        //
        // },
        write: function(store, operation){
            if (operation.action == 'update' && operation.success) {
                var records = operation.getRecords();
                store.suspendAutoSync();
                store.remove(records[0], true);
                store.resumeAutoSync();
            }
           // Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
        }
    }

});
