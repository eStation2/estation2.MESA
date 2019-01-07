Ext.define('esapp.model.Product', {
    extend : 'esapp.model.Base',

    idProperty : 'productid',

    fields: [
        {name: 'productid'},
        {name: 'productcode'},
        {name: 'subproductcode'},
        {name: 'version'},
        {name: 'defined_by'},
        {name: 'product_type'},
        {name: 'activated', type: 'boolean'},
        {name: 'prod_descriptive_name'},
        {name: 'description'},
        {name: 'provider'},
        {name: 'category_id'},
        {name: 'cat_descr_name'},
        {name: 'order_index'}
    ]

    // ,autoLoad: true
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

});