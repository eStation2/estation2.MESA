
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

    store: "HeaderLogoImages",
    //tpl: imageTpl,
    itemSelector: 'img',
    emptyText: esapp.Utils.getTranslation('noimagesavailable'),  // 'No images available'

    initComponent: function () {
        var me = this;
        var imageTpl = '';
        //me.emptyText = esapp.Utils.getTranslation('noimagesavailable');  // 'No images available'
        var logoImagesStore = Ext.data.StoreManager.lookup('HeaderLogoImages');
        var data = [];

        if (esapp.globals['typeinstallation'].toLowerCase() == 'jrc_online'){
            data = [
                { src:'resources/img/logo/logo_en.gif', caption:'European Commission logo' }
            ];
        }
        else {
            data = [
                { src:'resources/img/logo/GMES.png', height: 70, caption:'GMES&Africa logo' },
                { src:'resources/img/logo/AUC_h110.jpg', height: 70, caption:'African Union logo' },
                { src:'resources/img/logo/ACP_h110.jpg', height: 70, caption:'ACP logo' },
                { src:'resources/img/logo/logo_en.gif', height: 70, caption:'European Commission logo' }
            ];
        }

        logoImagesStore.setData(data);

        if (esapp.globals['typeinstallation'].toLowerCase() == 'jrc_online') {
            imageTpl = new Ext.XTemplate(
                //'<div id="top">',
                '   <div class="lang-en" id="header-jrc">',
                '   <tpl for=".">',
                '       <img id="banner-flag" alt="{caption}" src="{src}" width="60" height="50" />  ',
                '   </tpl>',
                '        <div id="main-title" style="margin-top: 65px; !important">Joint Research Centre</div>',
                '        <div id="sub-title">eStation 2 - EARTH OBSERVATION PROCESSING SERVICE</div>',
                '        <p class="off-screen">Service tools</p>',
                '        <ul class="reset-list" id="services">',
                '           <li>',
                '                 <a class="first" accesskey="1" href="http://ec.europa.eu/geninfo/legal_notices_en.htm">Legal notice</a>',
                '            </li>',
                '            <li>',
                '                 <a accesskey="2" href="https://ec.europa.eu/info/cookies_en">Cookies</a>',
                '            </li>',
                '            <li>',
                '                <a accesskey="3" href="mailto:estation@jrc.ec.europa.eu" target="_top">Contact</a>',
                '            </li>',
                '            <li>',
                '                 <a accesskey="4" href="http://ec.europa.eu/geninfo/query/search_en.html">Search</a>',
                '            </li>',
                '        </ul>',
                '    </div>',
                '     <div id="path">',
                '             <p class="off-screen">Navigation path</p>',
                '             <ul class="reset-list">',
                '                 <li class="first"><a id="firstTab" href="http://ec.europa.eu/index_en.htm">European Commission</a></li>',
                '                 <li><a href="https://ec.europa.eu/jrc/">EU Science Hub</a></li>',
                '                 <li><a href="../">eStation</a></li>',
                '             </ul>',
                '         <div id="releaseBox" align="right">',
                '             <div id="releaseBoxText">Release 2.2.0</div>',
                '         </div>',
                '     </div>'
                //' </div>'
            );
        }
        else {
            imageTpl = new Ext.XTemplate(
                '<div id="logo">',
                '<tpl for=".">',
                      '<img alt="{caption}" src="{src}" width="{width}" height="60" />  ',
                '</tpl>',
                '</div>',
                '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">' + esapp.Utils.getTranslation('earthobservationprocessingservice') + '</span></div>'
            //    '<div id="header"> <p id="banner-title-text">eStation 2 - </p><span id="banner-title-text-small">EARTH OBSERVATION PROCESSING SERVICE</span></div>'
            );
        }

        me.tpl = imageTpl;
        me.emptyText = esapp.Utils.getTranslation('noimagesavailable'); // 'No images available'

        me.callParent();
    }
});

