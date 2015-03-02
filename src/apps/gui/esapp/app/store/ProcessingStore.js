Ext.define('esapp.store.ProcessingStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.processing',

    model: 'esapp.model.Processing',

    requires : [
        'esapp.model.Processing',
        'Ext.data.proxy.Rest'
    ],

    storeId : 'ProcessingStore'

    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    //sorters: {property: 'productcode', direction: 'ASC'}

    ,proxy: {
        type: 'rest',
        appendId: false,
        api: {
            read: 'processing',
            create: 'processing/create',
            update: 'processing/update',
            destroy: 'processing/delete'
        },
        reader: {
             type: 'json'
            ,successProperty: 'success'
            ,rootProperty: 'products'
            ,messageProperty: 'message'
        },
        writer: {
            type: 'json',
            allDataOptions: {
                associated: true
                //,changes: true
            },
            writeAllFields: true,
            //appendId: false,
            rootProperty: 'products'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'PROCESSING STORE - REMOTE EXCEPTION',
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
        write: function(store, operation){
            Ext.toast({ html: operation.getResultSet().message, title: "Processing chain update", width: 300, align: 't' });
        }
    }

});