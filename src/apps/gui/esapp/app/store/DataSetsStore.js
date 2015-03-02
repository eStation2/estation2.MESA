Ext.define('esapp.store.DataSetsStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.dataset',

    model: 'esapp.model.DataSet',

    requires : [
        'esapp.model.DataSet',
        'Ext.data.proxy.Rest'
    ],

    storeId : 'DataSetsStore'

    ,autoLoad: true
    ,autoSync: true
    ,remoteSort: false
    ,remoteGroup: false

    ,sorters: {property: 'order_index', direction: 'DESC'}

    ,proxy: {
        type: 'rest',
        // url: '',
        appendId: false,
        api: {
            read: 'datasets',
            create: 'datasets/create',
            update: 'datasets/update',
            destroy: 'datasets/delete'
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
                    title: 'DATASETS STORE - REMOTE EXCEPTION',
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