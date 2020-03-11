Ext.define('esapp.view.acquisition.product.editProductModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-editproduct',

    stores: {
        // categories: {
        //     source:'CategoriesAllStore',
        //     session: true
        //     // proxy:{
        //     //   extraParams: {all: true}
        //     // }
        // },
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
