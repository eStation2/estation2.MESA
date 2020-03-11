
Ext.define("esapp.view.analysis.ProductNavigator",{
    "extend": "Ext.panel.Panel",
    "controller": "analysis-productnavigator",
    "viewModel": {
        "type": "analysis-productnavigator"
    },
    xtype: "productnavigator",

    requires: [
        'esapp.view.analysis.ProductNavigatorModel',
        'esapp.view.analysis.ProductNavigatorController',

        'esapp.model.ProductNavigator',

        'Ext.layout.container.Center',
        'Ext.grid.plugin.RowExpander',
        'Ext.XTemplate'

    ],

    title: '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('productnavigator') + '</div>',


    floating: true,
    defaultAlign: 'tl-tl',
    modal: false,
    closable: true,
    closeAction: 'hide', // 'destroy',
    maximizable: false,
    resizable: false,
    focusable: true,
    draggable: true,
    constrain: true,
    alwaysOnTop: true,
    // resizeHandles: 'n,s',
    scrollable: false,
    autoWidth:  true,
    minWidth: 340,
    width: 340,
    height: 590,    // 610,
    // height: Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-10 : 750,  // 600,
    // autoHeight:  true,
    minHeight: 300,
    // maxHeight: 750,

    bodyBorder: false,
    border:false,
    frame: false,
    frameHeader : false,
    shadow: false,
    componentCls: 'rounded-box',
    header: {
        titlePosition: 0,
        titleAlign: 'left',
        // iconCls: 'africa',
        cls: 'rounded-box-header',
        style: {
            'background-color': '#A9DEEC !important;',
            'font-weight':'bold',
            'color':'#000',
            'font-size': '13px;'
        }
    },
    // header: {
    //     titlePosition: 0,
    //     titleAlign: 'left',
    //     iconCls: 'africa'
    // },
    // constrainHeader: Ext.getBody(),

    layout: {
        type  : 'border',
        padding: 0
    },

    config: {
        productselected:false,
        mapviewid:null,
        selectedproduct:{
            productcode: null,
            productversion: null,
            mapsetcode: null,
            subproductcode: null,
            productdate: null,
            legendid: null,
            legendHTML: null,
            legendHTMLVertical: null,
            productname: null,
            date_format: null,
            frequency_id: null,
            productsensor: null
        }
    },

    initComponent: function () {
        var me = this;

        me.id = me.mapviewid+'-productnavigator';
        me.title = '<div class="panel-title-style-16">' + esapp.Utils.getTranslation('productnavigator') + '</div>';
        // me.constrainHeader = me.owner;
        // me.height = Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-10 : 750;  // 600,

        me.tools = [{
            type: 'refresh',
            align: 'c-c',
            tooltip: esapp.Utils.getTranslation('refreshproductlist'),    // 'Refresh product list',
            callback: 'loadProductsGrid'
        }];

        // Ext.util.Observable.capture(this, function(e){console.log('productnav event: ' + e);});
        me.listeners = {
            // close: me.onClose,
            afterrender: function(){
                me.alignTarget = me.owner.el;
            }
            ,show: function(){
                // me.fireEvent('align');
                // console.info(me.alignTarget);
                me.alignTo(me.alignTarget);
            }
            // align: function() {
            //     // me.alignTo(Ext.getCmp('analysismain').lookupReference('analysismain_maptemplatebtn'), 'tl-bc');
            //     me.alignTo(me.owner, 'tl-bc');
            //     me.updateLayout();
            // }
            // ,deactivate: function(){
            //     me.hide();
            // }
        };

        me.items = [{
            xtype : 'grid',
            reference: 'productsGrid',
            region: 'center',
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
                // reserveScrollbar: true
            },
            layout: 'fit',

            selModel : {
                allowDeselect : false,
                mode:'SINGLE'
            },
            hideHeaders: true,
            scrollable: 'vertical',
            reserveScrollbar: true,
            collapsible: false,
            focusable: false,
            enableColumnMove:false,
            enableColumnResize:false,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: false,
            bodyBorder: true,

            features: [{
                reference: 'selectproductcategories',
                ftype: 'grouping',
                groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                hideGroupedHeader: true,
                enableGroupingMenu: false,
                startCollapsed : true,
                groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
            }],

            listeners: {
                // afterrender: 'loadProductsGrid',
                rowclick: 'productsGridRowClick'
            },

            columns : [{
                // text: '<div class="grid-header-style">'+esapp.Utils.getTranslation('productcategories')+'</div>',
                // text: esapp.Utils.getTranslation('product'),   // "Product",
                sortable: false,
                hideable: false,
                variableRowHeight : true,
                menuDisabled:true,
                text: '',
                xtype: 'templatecolumn',
                minWidth: 265,
                tpl:  new Ext.XTemplate(
                    '<b>{prod_descriptive_name}</b>' +
                    '<tpl if="version != \'undefined\'">',
                        '<b class="smalltext"> - {version}</b>',
                    '</tpl>',
                    '</br>' +
                    '<b class="smalltext" style="color:darkgrey;">{productcode}</b>'
                )
            },{
                xtype: 'actioncolumn',
                hidden: false,
                hideable: false,
                width: 25,
                align: 'center',
                shrinkWrap: 0,
                variableRowHeight:true,
                menuDisabled:true,
                items: [{
                    getClass: function(v, meta, rec) {
                        return 'info';
                    },
                    getTip: function(v, meta, rec) {
                        return rec.get('description');
                    },
                    handler: function(grid, rowIndex, colIndex, icon, e, record) {

                    }
                }]
            }]
        }, {
            region: 'east',
            reference: 'product-datasets-info',
            title: '<div class="panel-title-style-16">'+esapp.Utils.getTranslation('productinfo')+'</div>',
            header: {
                titlePosition: 0,
                titleAlign: 'left',
                height: 25
                //,style: {backgroundColor:'#ADD2ED'}
            },
            autoWidth:true,
            scrollable:false,
            focusable: false,
            split: false,
            collapsible: true,
            collapsed: true,
            floatable: false,
            frame: false,
            border: false,
            bodyBorder: false,
            defaults: {
                margin: {top: 5, right: 5, bottom: 5, left: 5},
                layout: {
                    type: 'vbox'
                }
            },
            listeners: {
                expand: function(){
                    this.setWidth(335); // 400
                    this.up().setWidth(335+312);
                },
                collapse: function(){
                    this.setWidth(0);
                    this.up().setWidth(340);
                }
            },
            bbar: Ext.create('Ext.toolbar.Toolbar', {
                items: ['->',{
                    text: esapp.Utils.getTranslation('addtomap'),    // 'Add to Map',
                    reference: 'addtomapbtn_'+me.mapviewid.replace(/-/g,'_'),
                    disabled: true,
                    handler: function(btn) {
                        var productdate = null;

                        me.getViewModel().getStore('colorschemes').each(function(rec){
                            if (rec.get('default_legend')==true || rec.get('default_legend')=="true"){
                                //console.info(rec);
                                me.selectedproduct.legendid = rec.get('legend_id');
                                me.selectedproduct.colorschemeHTML = rec.get('colorschemeHTML');
                                me.selectedproduct.legendHTML = rec.get('legendHTML');
                                me.selectedproduct.legendHTMLVertical = rec.get('legendHTMLVertical');
                            }
                        },this);

                        Ext.getCmp(me.mapviewid).getController().addProductLayer(
                            me.selectedproduct.productcode,
                            me.selectedproduct.productversion,
                            me.selectedproduct.mapsetcode,
                            me.selectedproduct.subproductcode,
                            productdate,
                            me.selectedproduct.legendid,
                            //me.selectedproduct.colorschemeHTML,
                            me.selectedproduct.legendHTML,
                            me.selectedproduct.legendHTMLVertical,
                            me.selectedproduct.productname,
                            me.selectedproduct.date_format,
                            me.selectedproduct.frequency_id,
                            me.selectedproduct.productsensor
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
                maxHeight: 150,
                collapsible: false,
                focusable: false,
                layout: 'fit',
                padding: {top: 0, right: 0, bottom: 0, left: 0},
                items: Ext.create('Ext.view.View', {
                    bind: '{productmapsets}',
                    //id: 'mapsets',
                    //boxLabel: '{descriptive_name}',
                    tpl: Ext.create('Ext.XTemplate',
                        '<tpl for=".">',
                            '<div class="mapset" id="{mapsetcode:stripTags}">',
                                '<img width="100px" height="80px" src="{footprint_image}" title="{descriptive_name:htmlEncode}">',
                                '<span><strong>{descriptive_name:htmlEncode}</strong></span>',
                            '</div>',
                        '</tpl>',
                        '<div class="x-clear"></div>'
                    ),
                    multiSelect: false,
                    // height: 170,
                    // width: 140,
                    trackOver: true,
                    cls:'mapsets',
                    overItemCls: 'mapset-hover',
                    itemSelector: 'div.mapset',
                    emptyText: esapp.Utils.getTranslation('nomapsetstodisplay'),    // 'No mapsets to display. Please select a product to view its mapsets',
                    scrollable: true,
                    listeners: {
                        itemclick: 'mapsetItemClick'
                    }
                })
            }, {
                xtype: 'grid',
                reference: 'mapset-dataset-grid',
                autoWidth: true,
                maxHeight: 170,
                scrollable: 'vertical',
                reserveScrollbar: true,
                focusable: false,
                hidden: true,
                bind: '{mapsetdatasets}',
                layout: 'fit',
                cls: 'newpanelstyle',

                viewConfig: {
                    stripeRows: false,
                    enableTextSelection: true,
                    draggable: false,
                    markDirty: false,
                    resizable: false,
                    disableSelection: false,
                    trackOver: false,
                    preserveScrollOnRefresh: true,
                    preserveScrollOnReload: true
                },
                bufferedRenderer: false,
                scrollToTop: null,

                collapsible: false,
                enableColumnMove: false,
                enableColumnResize: false,
                multiColumnSort: false,
                columnLines: false,
                rowLines: true,
                frame: false,
                border: false,
                bodyBorder: false,
                forceFit: true,
                focusOnToFront: false,

                listeners: {
                    rowclick: 'mapsetDataSetGridRowClick'
                    ,scrolltoselection: function (events) {
                        var record = this.getSelection();
                        if (record.length > 0)
                            this.ensureVisible(record[0], {focus: true});
                    }
                },
                defaults: {
                    sortable: true,
                    hideable: false,
                    variableRowHeight: false,
                    menuDisabled: true
                },
                columns: [{
                    text: '<div class="grid-header-style">'+esapp.Utils.getTranslation('datasets')+'</div>',
                    xtype: 'templatecolumn',
                    tpl: new Ext.XTemplate(
                        '<b>{descriptive_name}</b>' +
                        // '<tpl if="version != \'undefined\'">',
                        // '<b class="smalltext"> - {version} </b>',
                        // '</tpl>',
                        // '</br>' +
                        '<span class="smalltext"><b style="color:darkgrey;"> - {subproductcode}</b>' +
                        // '</span>' +
                        // '<span>&nbsp;&nbsp;(display_index: <b style="color:black">{display_index}</b>)' +
                        '</span>'
                    ),
                    width: 250,
                    sortable: true,
                    menuDisabled: true
                },{
                    xtype: 'actioncolumn',
                    hidden: false,
                    hideable: false,
                    width: 25,
                    align: 'center',
                    shrinkWrap: 0,
                    variableRowHeight:true,
                    menuDisabled:true,
                    items: [{
                        getClass: function(v, meta, rec) {
                            return 'info x-action-col-cell-18';
                        },
                        getTip: function(v, meta, rec) {
                            return rec.get('description');
                        },
                        handler: function(grid, rowIndex, colIndex, icon, e, record) {

                        }
                    }]
                }]
            },{
                xtype: 'grid',
                reference: 'colorschemesGrid',
                autoWidth: true,
                // autoHeight: true,
                // maxHeight: 190,
                height: 165,
                layout: 'fit',
                scrollable: 'vertical',
                reserveScrollbar: true,

                hidden: true,
                bind: '{colorschemes}',
                // layout: 'fit',
                cls: 'newpanelstyle',

                viewConfig: {
                    stripeRows: false,
                    enableTextSelection: true,
                    draggable: false,
                    markDirty: false,
                    resizable: false,
                    disableSelection: true,
                    trackOver: false,
                    preserveScrollOnRefresh: true,
                    preserveScrollOnReload: true
                },
                bufferedRenderer: false,

                listeners: {
                    rowclick: function(view, record, el, rowIndex) {
                        switch(record.get('defaulticon')) {
                            case 'x-grid3-radio-col':
                                    view.getStore('colorschemes').each(function(rec){
                                        if (view.getStore().indexOf(rec) != rowIndex) {
                                            rec.set('default_legend', false);
                                            rec.set('defaulticon', 'x-grid3-radio-col');
                                        }
                                    },this);
                                    record.set('default_legend', true);
                                    record.set('defaulticon', 'x-grid3-radio-col-on');
                                break;
                            default:
                        }
                    }
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
                focusOnToFront: false,
                focusable: false,
                forceFit: true,

                tbar: {
                    padding: 4,
                    defaults: {
                        scale: 'small',
                        hidden: false
                    },
                    items: [{
                        xtype: 'container',
                        html: '<div class="grid-header-style">' + esapp.Utils.getTranslation('colorschemes') + '</div>'
                    },
                    '->',{
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('assign_legend'),    // 'Assign legend to product',
                        name: 'assign_legend',
                        iconCls: 'fa fa-plus-circle fa-1x',
                        style: {color: 'green'},
                        hidden: esapp.globals['typeinstallation'].toLowerCase() == 'jrc_online',
                        handler: 'assignLegend'
                    }]
                },

                defaults: {
                    sortable: false,
                    hideable: false,
                    variableRowHeight: true,
                    menuDisabled: true,
                    draggable:false,
                    groupable:false,
                    stopSelection: false
                },
                columns: [{
                    xtype: 'actioncolumn',
                    width: 30,
                    // minWidth: 30,
                    align: 'center',
                    menuDisabled:true,
                    // shrinkWrap: 0,
                    items: [{
                        tooltip: esapp.Utils.getTranslation('selectacolorscheme'),    // 'Select color scheme',
                        getClass: function(v, meta, rec) {
                            return rec.get('defaulticon');
                        },
                        handler: 'onRadioColumnAction'
                    }]
                },{
                    xtype: 'templatecolumn',
                    // text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('colorschemes') + '</div>',
                    text: '<div>' + esapp.Utils.getTranslation('colorschemes') + '</div>',
                    cls: 'column-header-small-style',
                    width: 240,
                    shrinkWrap: 0,
                    menuDisabled:true,
                    tpl: new Ext.XTemplate(
                        '{colorschemeHTML}' +
                        '<b>{colorbar}</b>'
                    )
                },{
                    xtype: 'actioncolumn',
                    // header: esapp.Utils.getTranslation('actions'),   // 'Actions',
                    width: 35,
                    // minWidth: 35,
                    align: 'center',
                    menuDisabled:true,
                    hidden: esapp.globals['typeinstallation'].toLowerCase() == 'jrc_online',
                    items: [{
                        // scope: me,
                        width:'35',
                        disabled: false,
                        iconCls: 'delete16',
                        // getClass: function (v, meta, rec) {
                        //     return 'delete16';
                        // },
                        getTip: function (v, meta, rec) {
                            return esapp.Utils.getTranslation('unassignlegendfromdataset') + ': <BR>' +
                                   me.selectedproduct['productname'] + ' ' +
                                   me.selectedproduct['productversion'] + ' - ' +
                                   me.selectedproduct['subproductcode'];
                        },
                        handler: 'unassignLegend'
                    }]
                // },{
                //     xtype: 'actioncolumn',
                //     // header: esapp.Utils.getTranslation('actions'),   // 'Actions',
                //     menuDisabled: true,
                //     sortable: true,
                //     variableRowHeight : true,
                //     draggable:false,
                //     groupable:false,
                //     hideable: false,
                //     width: 35,
                //     align: 'center',
                //     stopSelection: false,
                //
                //     items: [{
                //         // scope: me,
                //         width:'35',
                //         disabled: false,
                //         getClass: function (v, meta, rec) {
                //             return 'edit';
                //         },
                //         getTip: function (v, meta, rec) {
                //             return esapp.Utils.getTranslation('editlegendproperties') + ' ' + rec.get('legend_descriptive_name');
                //         },
                //         handler: 'editLegend'
                //     }]
                }]
            }]
        }];

        me.callParent();
    }
    ,onClose: function(win, ev) {
        //if (win.changesmade){
        //    Ext.data.StoreManager.lookup('ProductsActiveStore').load();
        //}
    }
});

