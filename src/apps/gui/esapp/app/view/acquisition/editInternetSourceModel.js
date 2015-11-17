Ext.define('esapp.view.acquisition.editInternetSourceModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-editinternetsource',
    stores: {
        // Define a store of EumetcastSource records that links to the Session.
        internetsources: {
            source: 'InternetSourceStore'
            //,session: true
            //model: 'InternetSource',
            //autoLoad: true,
            //autoSync: false
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
