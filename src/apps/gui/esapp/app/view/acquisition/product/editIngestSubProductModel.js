Ext.define('esapp.view.acquisition.product.editIngestSubProductModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-editingestsubproduct',
    stores: {
        subdatasourcedescriptions: {
            source:'SubDatasourceDescriptionStore'
        }
        // ingestsubproducts: {
        //     source:'IngestSubProductsStore'
        // }
    }

    ,formulas: {
        theIngestSubProduct: {
            get: function(get) {
                return this.getView().params.ingestsubproductrecord;
                // if (this.getView().params.create){
                //     return this.getView().params.ingestsubproductrecord;
                // }
                // else {
                //     return get('ingestsubproducts').findRecord('productcode', this.getView().params.productcode, 0, true, false, false);
                // }
            }
        }
    }

});
