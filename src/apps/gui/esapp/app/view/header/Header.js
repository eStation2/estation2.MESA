
Ext.define("esapp.view.header.Header",{
    extend: "Ext.view.View",
    xtype  : 'headerLogos',

    controller: "header",

    viewModel: {
        type: "header"
    },
    requires: [
        'esapp.view.header.HeaderController',
        'esapp.view.header.HeaderModel'
    ],

    store: "LogoImages", // Ext.data.StoreManager.lookup('imagesStore'),
    //tpl: imageTpl,
    itemSelector: 'img',
    emptyText: esapp.Utils.getTranslation('noimagesavailable'),  // 'No images available'

    initComponent: function () {
        var me = this;

        //me.emptyText = esapp.Utils.getTranslation('noimagesavailable');  // 'No images available'

        var imageTpl = new Ext.XTemplate(
            '<div id="logo">',
            '<tpl for=".">',
                  '<img alt="{caption}" src="{src}" width="60" height="50" />  ',
            '</tpl>',
            '</div>',
            '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">' + esapp.Utils.getTranslation('earthobservationprocessingservice') + '</span></div>'
        //    '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">EARTH OBSERVATION PROCESSING SERVICE</span></div>'
        );

        me.tpl = imageTpl;
        me.emptyText = esapp.Utils.getTranslation('noimagesavailable'); // 'No images available'

        me.callParent();
    }
});

