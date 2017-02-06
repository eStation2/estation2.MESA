
Ext.define("esapp.view.acquisition.selectMapsetForIngest",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-selectmapsetforingest",
    "viewModel": {
        "type": "acquisition-selectmapsetforingest"
    },
    xtype: "selectmapsetforingest",

    requires: [
        'esapp.view.acquisition.selectMapsetForIngestController',
        'esapp.view.acquisition.selectMapsetForIngestModel',

        'Ext.layout.container.Form',
        'Ext.layout.container.Center',
        'Ext.XTemplate'
    ],

    //bind: '{products}',
    //session: true,

    title: '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('selectmapset') + '</div>',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    constrainHeader: Ext.getBody(),

    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: false,
    resizable: true,
    resizeHandles: 'n,s',
    autoScroll: false,
    width: 650,
    height: Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-10 : 650,  // 600,
    minHeight:650,

    border:false,
    frame: false,
    bodyBorder: false,
    layout: {
        type  : 'fit',
        padding: 15
    },

    listeners:  {
        close: 'onClose',
        beforerender: 'loadMapsetStore'
    },
    mapsetselected:false,
    productcode: null,
    productversion: null,
    subproductcode: null,
    selectedmapset: null,

    initComponent: function () {
        var me = this;

        me.title = '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('selectmapset') + '</div>';

        //me.listeners =  {
        //    close: 'onClose',
        //    beforerender: 'loadMapsetStore'
        //};

        me.bbar =  Ext.create('Ext.toolbar.Toolbar', {
            items: ['->',{
                reference: 'savemapsetbtn',
                text: esapp.Utils.getTranslation('save'),
                disabled: true,
                handler: function(btn) {

                    Ext.Ajax.request({
                        method: 'GET',
                        url: 'addingestmapset',
                        params: {
                            productcode: me.productcode,
                            version: me.productversion,
                            subproductcode: me.subproductcode,
                            selectedmapset: me.selectedmapset
                        },
                        success: function(response, opts){
                            var result = Ext.JSON.decode(response.responseText);
                            if (result.success){
                                var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');

                                if (ingestiongridstore.isStore) {
                                    ingestiongridstore.load({
                                        callback: function(records, options, success){
                                            me.getController().onClose();
                                        }
                                    });
                                }
                            }
                        },
                        failure: function(response, opts) {
                            console.info(response.status);
                        }
                    });

                    //me.close();
                }
            }]
        });

        me.items = [{
            xtype: 'fieldset',
            title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('mapsetsavailable')+'</div>',
            titleAlign: 'center',
            reference: 'mapsets-ingest',
            border: true,
            //autoWidth: true,
            //flex: 1,
            height: 220,
            //width: 530,
            collapsible: false,
            layout: 'fit',
            margin: {top: 10, right: 10, bottom: 0, left: 10},
            //padding: {top: 10, right: 10, bottom: 0, left: 10},
            items: Ext.create('Ext.view.View', {
                bind: '{mapsets}',
                //id: 'mapsets',
                //boxLabel: '{descriptive_name}',
                tpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                        '<div class="mapset" id="{mapsetcode:stripTags}">',
                            '<img src="{footprint_image}" title="{descriptive_name:htmlEncode}">',
                            '<span><strong>{descriptive_name:htmlEncode}</strong></span>',
                        '</div>',
                    '</tpl>',
                    '<div class="x-clear"></div>'
                ),
                multiSelect: false,
                height: 250,
                //maxWidth: 140,
                trackOver: true,
                cls:'mapsets',
                overItemCls: 'mapset-hover',
                itemSelector: 'div.mapset',
                emptyText: esapp.Utils.getTranslation('nomapsets'),    // 'No mapsets to display. Please select a product to view its mapsets',
                autoScroll: true,
                listeners: {
                    itemclick: 'mapsetItemClick'
                }
            })
        }];

        me.callParent();
    }
});
