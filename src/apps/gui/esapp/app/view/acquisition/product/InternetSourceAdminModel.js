Ext.define('esapp.view.acquisition.product.InternetSourceAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-internetsourceadmin',
    stores: {
        // Define a store of InternetSource records that links to the Session.
        internetsources: {
            source: 'InternetSourceStore'
            ,session: true
        }
    }
});
