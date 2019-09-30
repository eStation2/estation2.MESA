Ext.define('esapp.view.acquisition.product.EumetcastSourceAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-eumetcastsourceadmin',
    stores: {
        // Define a store of EumetcastSource records that links to the Session.
        eumetcastsources: {
            source: 'EumetcastSourceStore'
            ,session: true
        }
    }

});
