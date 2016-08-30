
Ext.define("esapp.view.analysis.ProductNavigator",{
    "extend": "Ext.window.Window",
    "controller": "analysis-productnavigator",
    "viewModel": {
        "type": "analysis-productnavigator"
    },
    xtype: "productnavigator",

    requires: [
        'esapp.view.analysis.ProductNavigatorModel',
        'esapp.view.analysis.ProductNavigatorController',

        'esapp.model.ProductNavigator',
        //'esapp.model.ProductNavigatorMapSet',
        //'esapp.model.ProductNavigatorMapSetDataSet',

        'Ext.layout.container.Form',
        'Ext.layout.container.Center',
        'Ext.grid.plugin.RowExpander',
        'Ext.XTemplate',
        'Ext.form.RadioGroup'
    ],

    //bind: '{products}',
    //session: true,

    title: '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('productnavigator') + '</div>',    // '<div class="panel-title-style-16">Product Navigator</div>',
    header: {
        titlePosition: 0,
        titleAlign: 'center',
        iconCls: 'africa'
    },
    constrainHeader: Ext.getBody(),

    modal: true,
    closable: true,
    closeAction: 'hide', // 'destroy',
    maximizable: false,
    resizable: true,
    resizeHandles: 'n,s',
    autoScroll: false,
    width: 565,
    height: Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-10 : 830,  // 600,
    minHeight:750,

    border:false,
    frame: false,
    layout: {
        type  : 'border',
        padding: 5
    },

    tools: [
    {
        type: 'refresh',
        align: 'c-c',
        tooltip: esapp.Utils.getTranslation('refreshproductlist'),    // 'Refresh product list',
        callback: 'loadProductsGrid'
    }],

    productselected:false,
    mapviewid:null,
    selectedproduct:{
        productcode: null,
        productversion: null,
        mapsetcode: null,
        subproductcode: null,
        legendid: null
    },

    initComponent: function () {
        var me = this
            ,cfg = {productselected:false}
        ;

        Ext.apply(cfg, {
            id: me.mapviewid+'-productnavigator',

            border:false,
            frame: false,
            bodyBorder: false,

            listeners: {
                close: me.onClose
            },

            items : [{
                xtype : 'grid',
                reference: 'productsGrid',
                region: 'center',
                width: 465,
                //store: 'ProductNavigatorStore',
                bind: '{products}',
                session:true,

                viewConfig: {
                    stripeRows: false,
                    enableTextSelection: true,
                    draggable:false,
                    markDirty: false,
                    resizable:false,
                    disableSelection: false,
                    trackOver:true
                },

                selModel : {
                    allowDeselect : false,
                    mode:'SINGLE'
                },

                collapsible: false,
                enableColumnMove:false,
                enableColumnResize:false,
                multiColumnSort: false,
                columnLines: false,
                rowLines: true,
                frame: false,
                border: false,
                bodyBorder: false,

                features: [{
                    reference: 'selectproductcategories',
                    ftype: 'grouping',
                    groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                    hideGroupedHeader: true,
                    enableGroupingMenu: false,
                    startCollapsed : false,
                    groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
                }],

                plugins: [{
                    ptype: 'rowexpander',
                    cellWrap:true,
                    layout:'fit',
                    rowBodyTpl : new Ext.XTemplate(
                        '<span class="smalltext">' +
                        '<p>{description}</p>' +
                        '</span>'
                    )
                }],

                listeners: {
                    //scope: 'controller',
                    afterrender: 'loadProductsGrid', // 'loadProductsStore',
                    rowclick: 'productsGridRowClick'
                },

                columns : [{
                    text: '<div class="grid-header-style">'+esapp.Utils.getTranslation('productcategories')+'</div>',
                    menuDisabled: true,
                    defaults: {
                        sortable: false,
                        hideable: false,
                        variableRowHeight : true,
                        menuDisabled:true
                    },
                    columns: [
                        {
                            text: esapp.Utils.getTranslation('product'),   // "Product",
                            xtype: 'templatecolumn',
                            width: 455,
                            tpl:  new Ext.XTemplate(
                                '<b>{prod_descriptive_name}</b>' +
                                '<tpl if="version != \'undefined\'">',
                                    '<b class="smalltext"> - {version}</b>',
                                '</tpl>',
                                '</br>' +
                                '<b class="smalltext" style="color:darkgrey">{productcode}</b>'
                            )
                            //dataIndex: 'prod_descriptive_name',
                            //renderer : function(val) {
                            //    return '<b>' + val + '</b>';
                            //}
                        }
                    ]
                }]
            }, {
                region: 'east',
                reference: 'product-datasets-info',
                title: '<div class="panel-title-style-16">'+esapp.Utils.getTranslation('productinfo')+'</div>',
                header: {
                    titlePosition: 0,
                    titleAlign: 'left',
                    height: 33
                    //,style: {backgroundColor:'#ADD2ED'}
                },
                autoWidth:true,
                autoScroll:true,
                split: true,
                collapsible: true,
                collapsed: true,
                floatable: false,
                frame: false,
                border: false,
                bodyBorder: false,
                defaults: {
                    margin: {top: 10, right: 10, bottom: 20, left: 10},
                    layout: {
                        type: 'vbox'
                    }
                },
                listeners: {
                    expand: function(){
                        //this.up().down('grid').setWidth(460)
                        this.setWidth(550);
                        me.center();
                        this.up().setPosition(200,10);
                        this.up().setWidth(1100);
                    },
                    collapse: function(){
                        //this.up().down('grid').setWidth(485)
                        this.setWidth(5);
                        me.center();
                        //this.up().setPosition(670,140);
                        this.up().setWidth(565);
                    }
                },
                bbar: Ext.create('Ext.toolbar.Toolbar', {
                    items: ['->',{
                        text: esapp.Utils.getTranslation('addtomap'),    // 'Add to Map',
                        reference: 'addtomapbtn_'+me.mapviewid.replace(/-/g,'_'),
                        disabled: true,
                        handler: function(btn) {
                            //console.info(me.getViewModel().getStore('colorschemes'));
                            me.getViewModel().getStore('colorschemes').each(function(rec){
                                if (rec.get('default_legend')==true || rec.get('default_legend')=="true"){
                                    //console.info(rec);
                                    me.selectedproduct.legendid = rec.get('legend_id');
                                    me.selectedproduct.colorschemeHTML = rec.get('colorschemeHTML');
                                    me.selectedproduct.legendHTML = rec.get('legendHTML');
                                    me.selectedproduct.legendHTMLVertical = rec.get('legendHTMLVertical');
                                }
                            },this);

                            Ext.getCmp(me.mapviewid).getController().addProductLayer(me.selectedproduct.productcode,
                                                                                     me.selectedproduct.productversion,
                                                                                     me.selectedproduct.mapsetcode,
                                                                                     me.selectedproduct.subproductcode,
                                                                                     me.selectedproduct.legendid,
                                                                                     me.selectedproduct.colorschemeHTML,
                                                                                     me.selectedproduct.legendHTML,
                                                                                     me.selectedproduct.legendHTMLVertical,
                                                                                     me.selectedproduct.productname
                            );
                            me.close();
                        }
                    }]
                }),

                items: [{
                    xtype: 'fieldset',
                    title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('mapsetsavailable')+'</div>',
                    titleAlign: 'center',
                    reference: 'product-mapsets-dataview',
                    border: true,
                    autoWidth: true,
                    //flex: 1,
                    height: 220,
                    //width: 530,
                    collapsible: false,
                    layout: 'fit',
                    padding: {top: 5, right: 0, bottom: 0, left: 0},
                    items: Ext.create('Ext.view.View', {
                        bind: '{productmapsets}',
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
                        width: 140,
                        trackOver: true,
                        cls:'mapsets',
                        overItemCls: 'mapset-hover',
                        itemSelector: 'div.mapset',
                        emptyText: esapp.Utils.getTranslation('nomapsetstodisplay'),    // 'No mapsets to display. Please select a product to view its mapsets',
                        autoScroll: true,
                        listeners: {
                            itemclick: 'mapsetItemClick'
                        }
                    })
                }, {
                    xtype: 'grid',
                    reference: 'mapset-dataset-grid',
                    autoWidth: true,
                    //flex: 1,
                    //width: 530,
                    maxHeight: 250,
                    autoScroll: true,
                    hidden: true,
                    bind: '{mapsetdatasets}',
                    layout: 'fit',

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: false,
                        disableSelection: false,
                        trackOver: true
                    },

                    selModel: {
                        allowDeselect: true
                    },

                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: false,
                    multiColumnSort: false,
                    columnLines: true,
                    rowLines: true,
                    frame: false,
                    border: false,
                    bodyBorder: false,

                    plugins: [{
                        ptype: 'rowexpander',
                        cellWrap: true,
                        layout: 'fit',
                        rowBodyTpl: new Ext.XTemplate(
                            '<span class="smalltext">' +
                            '<p>{description}</p>' +
                            '</span>'
                        )
                    }],

                    listeners: {
                        rowclick: 'mapsetDataSetGridRowClick'
                        //,afterrender: function (grid) {
                        //    var viewEl = grid.getView().getEl();
                        //    if (viewEl.getStyle('overflowY') === 'hidden') {
                        //        viewEl.on('mousewheel', function (e) {
                        //            viewEl.setScrollTop(viewEl.getScrollTop() + e.browserEvent.deltaY);
                        //        });
                        //    }
                        //}
                    },
                    defaults: {
                        sortable: true,
                        hideable: false,
                        variableRowHeight: false
                    },
                    columns: [{
                        text: '<div class="grid-header-style">'+esapp.Utils.getTranslation('datasets')+'</div>',
                        xtype: 'templatecolumn',
                        tpl: new Ext.XTemplate(
                            '<b>{descriptive_name}</b>' +
                            '<tpl if="version != \'undefined\'">',
                            '<b class="smalltext"> - {version} </b>',
                            '</tpl>',
                            '</br>' +
                            '<span class="smalltext"><b style="color:darkgrey">{subproductcode}</b>' +
                            '</span>'
                        ),
                        width: 475,
                        sortable: true,
                        menuDisabled: true
                    }]
                },{
                    xtype: 'grid',
                    reference: 'colorschemesGrid',
                    autoWidth: true,
                    //flex: 1,
                    //width: 530,
                    //height: 150,
                    autoScroll: true,
                    hidden: true,
                    bind: '{colorschemes}',
                    layout: 'fit',

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: false,
                        disableSelection: true,
                        trackOver: true
                    },

                    selModel: {
                        allowDeselect: true
                    },

                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: false,
                    multiColumnSort: false,
                    columnLines: false,
                    rowLines: true,
                    frame: false,
                    border: false,
                    bodyBorder: false,

                    //listeners: {
                    //    rowclick: function (gridview, record) {
                    //        console.info(record);
                    //    }
                    //},
                    defaults: {
                        sortable: false,
                        hideable: false,
                        variableRowHeight: false
                    },
                    columns: [{
                        xtype: 'actioncolumn',
                        width: 30,
                        align: 'center',
                        shrinkWrap: 0,
                        items: [{
                            tooltip: esapp.Utils.getTranslation('selectacolorscheme'),    // 'Select color scheme',
                            getClass: function(v, meta, rec) {
                                return rec.get('defaulticon');
                            },
                            handler: 'onRadioColumnAction'
                        }]
                    },{
                        xtype:'templatecolumn',
                        text: '<div class="grid-header-style">'+esapp.Utils.getTranslation('colorschemes')+'</div>',
                        width: 475,
                        sortable: false,
                        menuDisabled: true,
                        shrinkWrap: 0,
                        tpl: new Ext.XTemplate(
                                '{colorschemeHTML}' +
                                '<b>{colorbar}</b>'
                        )
                    }]
                }]
            }]
        });

        Ext.apply(me, cfg);
        me.callParent(arguments);
    }
    ,onClose: function(win, ev) {
        //if (win.changesmade){
        //    Ext.data.StoreManager.lookup('ProductsActiveStore').load();
        //}
    }
});

