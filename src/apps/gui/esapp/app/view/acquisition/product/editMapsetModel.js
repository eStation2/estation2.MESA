Ext.define('esapp.view.acquisition.product.editMapsetModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-editmapset',
    stores: {
        mapsets: {
            source: 'MapsetsStore'
        }
        //theMapset: {
        //    source: '{mapsets}',
        //    filters: [{
        //        property: 'mapsetcode',
        //        value: '',
        //        anyMatch: false
        //    }],
        //}
    }

    ,formulas: {
        theMapset: {
            get: function(get) {
                if (this.getView().params.create){
                    return this.getView().params.mapsetrecord;
                }
                else {
                    return get('mapsets').findRecord('mapsetcode', this.getView().params.mapsetcode, 0, true, false, false);
                }
            }
        }
    }
});
