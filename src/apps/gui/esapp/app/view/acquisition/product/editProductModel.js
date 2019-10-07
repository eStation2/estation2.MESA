Ext.define('esapp.view.acquisition.product.editProductModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-editproduct',

    stores: {
        productdatasources: {
            source:'DataAcquisitionsStore'
        },
        // productingestions: {
        //     source:'IngestionsStore'
        // },
        ingestsubproducts: {
            source:'IngestSubProductsStore'
        }
    }
});
