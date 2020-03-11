Ext.define('esapp.view.acquisition.editEumetcastSourceModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-editeumetcastsource',
    stores: {
        // Define a store of EumetcastSource records that links to the Session.
        eumetcastsources: {
            source: 'EumetcastSourceStore'
            // ,session: true
        },
        mapsets: {
            source: 'MapsetsStore'
        }
        //theEumetcastSource: {
        //    source: '{eumetcastsources}',
        //    filters: [{
        //        property: 'eumetcast_id',
        //        value: '', // this.data_source_id,
        //        anyMatch: false
        //    }],
        //}
    }

    ,formulas: {
        theEumetcastSource: {
            get: function(get) {
                if (this.getView().params.create){
                    return this.getView().params.eumetcastsourcerecord;
                }
                else {
                    return get('eumetcastsources').findRecord('eumetcast_id', this.getView().params.data_source_id, 0, true, false, false);
                }
            }
        }
    }
});
