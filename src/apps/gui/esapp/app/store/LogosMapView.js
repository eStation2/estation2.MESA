Ext.define('esapp.store.LogosMapView', {
    extend  : 'Ext.data.Store',

    requires : [
        'esapp.model.LogosMapView'
    ],

    storeId : 'LogosMapView',
    model   : 'esapp.model.LogosMapView',

    data: [
        { src:'resources/img/logo/MESA_logo.png', width:'65', height:'50' },
        { src:'resources/img/logo/AfricanUnion_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/ACP_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/logo_en.gif', width:'65', height:'50' },
        { src:'resources/img/logo/ACMAD_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/CEMAC_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/CICOS_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/CILSS_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/ECOWAS_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/ICPAC_logo.jpg', width:'65', height:'50' },
        //{ src:'resources/img/logo/ICPAC_logo2.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/IGAD_ICPAC_logo.png', width:'65', height:'50' },
        //{ src:'resources/img/logo/IGAD_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/INDIAN_OCEAN_COMMISSION_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/MOI_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/RCMRD_logo.jpg', width:'65', height:'50' },
        { src:'resources/img/logo/SADC_logo.jpg', width:'65', height:'50' }
    ]
});