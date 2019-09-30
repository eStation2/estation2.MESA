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
                if (this.getView().params.create){
                    return this.getView().params.internetsourcerecord;
                }
                else {
                    return get('internetsources').findRecord('internet_id', this.getView().params.data_source_id, 0, true, false, false);
                }
            }
        }
    }

});
