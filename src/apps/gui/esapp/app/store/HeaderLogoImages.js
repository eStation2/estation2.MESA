Ext.define('esapp.store.HeaderLogoImages', {
    extend  : 'Ext.data.Store',

    requires : [
        'esapp.model.HeaderLogoImage'
    ],

    storeId : 'HeaderLogoImages',
    model   : 'esapp.model.HeaderLogoImage'

    // ,data: [
    //     { src:'resources/img/logo/MESA_h110.jpg', height: 70, caption:'MESA logo' },
    //     { src:'resources/img/logo/AUC_h110.jpg', height: 70, caption:'African Union logo' },
    //     { src:'resources/img/logo/ACP_h110.jpg', height: 70, caption:'ACP logo' },
    //     { src:'resources/img/logo/logo_en.gif', height: 70, caption:'European Commission logo' }
    // ]
});