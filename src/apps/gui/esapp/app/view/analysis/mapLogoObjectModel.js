Ext.define('esapp.view.analysis.mapLogoObjectModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-maplogoobject',
    stores: {
        logos: {
            source:'LogosMapView'
        }
    },
    data: {
        logoData: [
            { src:'resources/img/logo/GMES.png', width:'20%', height:'50px' },
            { src:'resources/img/logo/AUC_h110.jpg', width:'20%', height:'50px' },
            { src:'resources/img/logo/ACP_h110.jpg', width:'20%', height:'50px' },
            { src:'resources/img/logo/logo_en.gif', width:'20%', height:'50px' }
        ]
    }

});
