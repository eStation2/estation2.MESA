Ext.define('esapp.view.acquisition.IngestionModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.ingestion'

    ,stores: {
        productingestions: {
             source:'IngestionsStore'
        }
    }
});
