Ext.define('esapp.view.acquisition.product.selectProductModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-selectproduct'

    ,stores: {
        products: {
            source:'ProductsInactiveStore'
            // model: 'esapp.model.Product'
            // ,session: false
            // ,autoLoad: true
            // ,loadMask: false
            //
            // ,sorters: [{property: 'order_index', direction: 'DESC'},{property: 'prod_descriptive_name', direction: 'ASC'},{property: 'version', direction: 'ASC'}]
            //
            // ,grouper:{
            //     groupFn : function (item) {
            //         return esapp.Utils.getTranslation(item.get('category_id'));
            //     },
            //     property: 'order_index',
            //     sortProperty: 'order_index'
            // }

            // ,listeners: {
            //     write: function(store, operation){
            //         if (operation.action == 'update' && operation.success) {
            //             var records = operation.getRecords();
            //             store.suspendAutoSync();
            //             store.remove(records[0], true);
            //             store.resumeAutoSync();
            //         }
            //        // Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 200, align: 't' });
            //     }
            // }
        }
    }

});
