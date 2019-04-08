Ext.define('esapp.view.acquisition.editInternetSourceModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-editinternetsource',
    stores: {
        internetsources: {
            source: 'InternetSourceStore'
        },
        mapsets: {
            source: 'MapsetsStore'
        }
    }

    ,formulas: {
        theInternetSource: {
            get: function(get) {
                return get('internetsources').findRecord('internet_id', this.getView().data_source_id, 0, true, false, false)
            }
        }
    }

});
