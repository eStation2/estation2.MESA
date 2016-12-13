Ext.define('esapp.view.analysis.mapLogoObjectModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-maplogoobject',
    stores: {
        logos: {
            source:'LogosMapView'
        }
    }

});
