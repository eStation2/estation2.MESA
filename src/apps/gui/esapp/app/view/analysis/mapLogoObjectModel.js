Ext.define('esapp.view.analysis.mapLogoObjectModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-maplogoobject',
    stores: {
        logos: {
            source:'LogosStore' // 'LogosMapView',
            ,filters: [
                function(item) {
                    // console.info(item);
                    // console.info(item.data.active);
                    if (item.data.active){
                        return item;
                    }
                }
            ]
        },
        defaultlogos: {
            source:'LogosStore'
            ,filters: [
                function(item) {
                    if (item.data.isdefault){
                        return item;
                    }
                }
            ]
        }
    },
    data: {
        logoData: [],
        logoDefaultData: [
            { src:'resources/img/logo/GMES.png', width:'20%', height:'60px' },
            { src:'resources/img/logo/AUC_h110.jpg', width:'20%', height:'60px' },
            { src:'resources/img/logo/ACP_h110.jpg', width:'20%', height:'60px' },
            { src:'resources/img/logo/logo_en.gif', width:'20%', height:'60px' }
        ]
    }

});
