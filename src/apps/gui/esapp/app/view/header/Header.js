
var imageTpl = new Ext.XTemplate(
    '<div id="logo">',
    '<tpl for=".">',
          '<img alt="{caption}" src="{src}" width="60" height="50" />  ',
    '</tpl>',
    '</div>',
    '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">Earth Observation Processing Service</span></div>'
//    '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">EARTH OBSERVATION PROCESSING SERVICE</span></div>'
);


Ext.define("esapp.view.header.Header",{
    extend: "Ext.view.View",
    xtype  : 'headerLogos',

    controller: "header",

    viewModel: {
        type: "header"
    },
    store: "LogoImages", // Ext.data.StoreManager.lookup('imagesStore'),
    tpl: imageTpl,
    itemSelector: 'img',
    emptyText: 'No images available'
});

