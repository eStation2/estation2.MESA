Ext.define('esapp.view.acquisition.editEumetcastSourceModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-editeumetcastsource',
    stores: {
        // Define a store of EumetcastSource records that links to the Session.
        eumetcastsources: {
            source: 'EumetcastSourceStore'
            ,session: true
            //model: 'EumetcastSource'
            //autoLoad: false,
            //autoSync: false
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
                //console.info(this.getView());
                //console.info(get('eumetcastsources'));
                //console.info(get('eumetcastsources').findRecord('eumetcast_id', this.getView().data_source_id, 0, true, false, false));
                return get('eumetcastsources').findRecord('eumetcast_id', this.getView().data_source_id, 0, true, false, false)
                //return get('eumetcastsources').first();
            }
        }
    }

    //,links: {
    //    theEumetcastSource: {
    //        reference: 'esapp.model.EumetcastSource',
    //        id: 0
    //    }
    //}
});
