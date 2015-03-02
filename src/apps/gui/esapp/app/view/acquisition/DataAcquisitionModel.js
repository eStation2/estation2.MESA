Ext.define('esapp.view.acquisition.DataAcquisitionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.dataacquisition'

    ,stores: {
        productdatasources: {
             source:'DataAcquisitionsStore'
        }
    }
});
