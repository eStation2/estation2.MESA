Ext.define('esapp.view.analysis.layerAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-layeradmin',
    stores: {
        layers: {
            source:'LayersStore'
        }
    }
});