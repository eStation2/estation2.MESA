Ext.define('esapp.store.LogoImages', {
    extend  : 'Ext.data.Store',

    requires : [
        'esapp.model.LogoImage'
    ],

    storeId : 'LogoImages',
    model   : 'esapp.model.LogoImage',

    data: [
        { src:'resources/img/logo/AfricanUnion_logo.jpg', caption:'African Union logo' },
        { src:'resources/img/logo/ACP_logo.jpg', caption:'ACP logo' },
        { src:'resources/img/logo/logo_en.gif', caption:'European Commission logo' }
    ]
});