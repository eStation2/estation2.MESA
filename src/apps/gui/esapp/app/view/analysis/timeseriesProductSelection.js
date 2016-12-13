
Ext.define("esapp.view.analysis.timeseriesProductSelection",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.analysis.timeseriesProductSelectionController",
        "esapp.view.analysis.timeseriesProductSelectionModel",

        "Ext.tree.Panel"
        //,"Ext.data.TreeStore"
    ],
    
    controller: "analysis-timeseriesproductselection",
    viewModel: {
        type: "analysis-timeseriesproductselection"
    },
    xtype: 'timeseriesproductselection',

    //layout: 'fit',
    layout: {
        type: 'vbox'
        ,align: 'stretch'
    },
    defaults: {
        margin: '5 0 5 0'
    },


    initComponent: function () {
        var me = this;

        me.items = [{
            title: esapp.Utils.getTranslation('products'),  // 'Products',
            xtype: 'grid',
            reference: 'TimeSeriesProductsGrid',
            //region: 'center',
            //width: 395,
            height: 300,
            bind: '{products}',
            session: true,
            viewConfig: {
                stripeRows: false,
                enableTextSelection: true,
                draggable: false,
                markDirty: false,
                resizable: false,
                disableSelection: false,
                trackOver: true
            },
            layout: 'fit',
            hideHeaders: true,

            selModel: {
                allowDeselect: true,
                mode: 'SIMPLE'
            },

            collapsible: false,
            enableColumnMove: false,
            enableColumnResize: true,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: true,
            bodyBorder: false,
            forceFit: true,
            reserveScrollbar: true,

            tools: [{
                type: 'refresh',
                tooltip: esapp.Utils.getTranslation('refreshproductlist'),  // 'Refresh product list',
                callback: function (grid) {
                    var timeseriesProductsStore = grid.getStore('products');

                    if (timeseriesProductsStore.isStore) {
                        timeseriesProductsStore.load();
                    }
                }
            }],

            features: [{
                reference: 'timeseriesproductcategories',
                ftype: 'grouping',
                groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                hideGroupedHeader: true,
                enableGroupingMenu: false,
                startCollapsed: true,
                groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product category'
            }],

            //plugins: [{
            //    ptype: 'rowexpander',
            //    //cellWrap:true,
            //    //layout:'fit',
            //    useArrows: true,
            //    rowBodyTpl: [
            //        '<div class="subproducts"></div>'
            //    ]
            //    //rowBodyTpl: new Ext.XTemplate(
            //    //    '<span class="smalltext">' +
            //    //    '<p>{description}</p>' +
            //    //    '</span>'
            //    //)
            //}],

            listeners: {
                //afterrender: 'loadTimeseriesProductsGrid',
                rowclick: 'TimeseriesProductsGridRowClick'
            },

            //columns: [{
            //    text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',   // '<div class="grid-header-style">Product categories</div>',
            //    menuDisabled: true,
            //    defaults: {
            //        sortable: false,
            //        hideable: false,
            //        variableRowHeight: true,
            //        menuDisabled: true,
            //        autoSize: true
            //    },
                columns: [
                    {
                        xtype: 'templatecolumn',
                        width: 300,
                        minWidth: 300,
                        cellWrap: true,
                        tpl: new Ext.XTemplate(
                            '<b>{descriptive_name}</b>',
                            '<tpl if="version != \'undefined\'">',
                            '<b class="smalltext"> - {version}</b>',
                            '</tpl>',
                            '</br>',
                            '<b class="smalltext" style="color:darkgrey">{productcode} - {subproductcode}</b>',
                            '<tpl for="productmapsets">',
                            '<b class="smalltext"> - {descriptive_name}</b>',
                            '</tpl>'
                        )
                    },{
                        xtype: 'actioncolumn',
                        //header: esapp.Utils.getTranslation('active'),   // 'Active',
                        hidden: false,
                        hideable: false,
                        width: 25,
                        align: 'center',
                        shrinkWrap: 0,
                        variableRowHeight:true,
                        items: [{
                            getClass: function(v, meta, rec) {
                                //if (rec.get('activated')) {
                                return 'info';
                            },
                            getTip: function(v, meta, rec) {
                                return rec.get('description');
                            },
                            handler: function(grid, rowIndex, colIndex, icon, e, record) {

                            }
                        }]
                    }
                ]
            //}]
        },{
            xtype: 'grid',
            id: 'timeseries-mapset-dataset-grid',
            reference: 'timeseries-mapset-dataset-grid',
            //autoWidth: true,
            //width: 395,
            maxHeight: 305,
            //margin:'10 0 10 0',
            autoScroll: false,
            hidden: false,
            bind: '{timeseriesmapsetdatasets}',
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

            selType: 'checkboxmodel',
            selModel: {
                allowDeselect: true,
                checkOnly: false,
                mode: 'SIMPLE'
                //,listeners: {}
            },
            collapsible: false,
            enableColumnMove: false,
            enableColumnResize: true,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: true,
            bodyBorder: false,
            forceFit: false,
            reserveScrollbar: true,

            //listeners: {
            //    //rowclick: 'mapsetDataSetGridRowClick'
            //},
            defaults: {
                sortable: false,
                hideable: false,
                variableRowHeight: false
            },
            columns: [{
                text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('timeseries') + '</div>',   //'<div class="grid-header-style">Time series</div>',
                xtype: 'templatecolumn',
                tpl: new Ext.XTemplate(
                    //'<b>{prod_descriptive_name}</b>' +
                    '<b>{descriptive_name}</b>' +
                    '<tpl if="version != \'undefined\'">',
                    '<b class="smalltext"> - {version} </b>',
                    '</tpl>',
                    '</br>' +
                    '<span class="smalltext"><b style="color:darkgrey">{productcode} - {subproductcode}</b> - <b>{mapsetcode}</b>' +
                    '</span>'
                ),
                minWidth: 415,
                sortable: false,
                menuDisabled: true,
                cellWrap: true
            }, {
                xtype: 'actioncolumn',
                //header: esapp.Utils.getTranslation('actions'),   // 'Edit draw properties',
                menuDisabled: true,
                sortable: true,
                variableRowHeight: true,
                draggable: false,
                groupable: false,
                hideable: false,
                width: 35,
                align: 'center',
                stopSelection: false,

                items: [{
                    // scope: me,
                    width: '35',
                    disabled: false,
                    getClass: function (v, meta, rec) {
                        return 'chart-curve_edit';
                    },
                    getTip: function (v, meta, rec) {
                        return esapp.Utils.getTranslation('edittimeseriesdrawproperties') + ' ' + rec.get('productcode') + ' - ' + rec.get('subproductcode');
                    },
                    handler: 'editTSDrawProperties'
                }]
            }]
        }];


        me.callParent();
    }

    ,onRender: function() {
        var me = this;
        me.callParent(arguments);
        if(me.border){
            me.el.setStyle("border","1px solid #333");
        }
    }
});
