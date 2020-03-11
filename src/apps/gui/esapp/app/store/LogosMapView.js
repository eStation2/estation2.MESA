Ext.define('esapp.store.LogosMapView', {
    extend  : 'Ext.data.Store',

    requires : [
        'esapp.model.LogosMapView'
    ],

    storeId : 'LogosMapView',
    model   : 'esapp.model.LogosMapView',

    data: [

        { src:'resources/img/logo/MESA_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/AUC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/ACP_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/ACMAD_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/CILSS_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/CEMAC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/CICOS_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/ECOWAS_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/ICPAC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/IGAD_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/IOC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/MOI_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/SADC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/UoG_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/RCMRD_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/EC_h110.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/logo_en.gif', width:'20%', height:'50px' },
        { src:'resources/img/logo/logo_fr.gif', width:'20%', height:'50px' },
        { src:'resources/img/logo/GMES.png', width:'20%', height:'50px' },
        { src:'resources/img/logo/ECOAGRIS.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/TAFIRI_logo.png', width:'20%', height:'50px' },
        { src:'resources/img/logo/CSIR.jpg', width:'20%', height:'50px' },
        { src:'resources/img/logo/NARSS.png', width:'20%', height:'50px' },
        { src:'resources/img/logo/Logo-OSS_Fr&EN_Vect.png', width:'20%', height:'50px' },
        { src:'resources/img/logo/Logo-OSS_Vect_En.png', width:'20%', height:'50px' },
        { src:'resources/img/logo/Logo-OSS_Vect_Fr.png', width:'20%', height:'50px' }

        // { src:'resources/img/logo/IOTC-logo_110.PNG', width:'20%', height:'50px' },
        // { src:'resources/img/logo/DSFA-logo_90.png', width:'20%', height:'33px' },
        // { src:'resources/img/logo/MNRT_110.PNG', width:'20%', height:'50px' }
    ]
});