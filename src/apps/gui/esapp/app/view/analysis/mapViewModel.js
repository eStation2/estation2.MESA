Ext.define('esapp.view.analysis.mapViewModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-mapview',

    data: {
        titleData: {
            selected_area: '',
            product_name: '',
            product_date: ''
        }
    },

    stores: {
        layers: {
            source:'LayersStore'
        }
    }

});
