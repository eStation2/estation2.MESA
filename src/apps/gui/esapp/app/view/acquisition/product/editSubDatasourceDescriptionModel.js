Ext.define('esapp.view.acquisition.product.editSubDatasourceDescriptionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-editsubdatasourcedescription',
    stores: {
        subdatasourcedescriptions: {
            source:'SubDatasourceDescriptionStore'
        }
    }

    ,formulas: {
        theSubDatasourceDescription: {
            get: function(get) {
                return this.getView().params.subdatasourcedescrrecord;
            }
        }
    }

});
