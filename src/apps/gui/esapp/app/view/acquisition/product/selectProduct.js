
Ext.define("esapp.view.acquisition.product.selectProduct",{
    "extend": "Ext.window.Window",

    "controller": "acquisition-product-selectproduct",
    "viewModel": {
        "type": "acquisition-product-selectproduct"
    },
    xtype: "selectproduct",

    requires: [
        'esapp.view.acquisition.product.selectProductModel',
        'esapp.view.acquisition.product.selectProductController',
        'esapp.view.acquisition.product.editProduct',

        // 'Ext.layout.container.Center',
        // 'Ext.grid.plugin.CellEditing',
        //'Ext.grid.column.Check',
        'Ext.XTemplate',
        'Ext.grid.column.Action'
    ],

    title: esapp.Utils.getTranslation('activateproduct'),  // 'Activate Product',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    constrainHeader: true,
    //constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: false,
    autoScroll: true,
    maximizable: false,

    // minWidth: 700,
    width: 640,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    layout: {
        type  : 'fit'
    },

    config: {
        changesmade:false
    },

    initComponent: function () {
        var me = this;

        me.setTitle('<div class="panel-title-style-16">' + esapp.Utils.getTranslation('activateproduct') + '</div>');

        me.listeners = {
            close: me.onClose
        };

        me.tbar = {
            items: [
            // {
            //    text: esapp.Utils.getTranslation('newproduct'),  // 'New product',
            //    name: 'newproduct',
            //    iconCls: 'fa fa-plus-circle fa-2x',
            //    style: {color: 'green'},
            //    hidden: false,
            //    scale: 'medium',
            //    handler: function () {
            //        var newProductWin = new esapp.view.acquisition.product.editProduct({
            //            params: {
            //                edit: false
            //            }
            //        });
            //        newProductWin.show();
            //    }
            // },
                '->', {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'loadInactiveProductsGrid'
            }]
        };

        me.bbar = {
            items: ['->', {
                text: esapp.Utils.getTranslation('close'),  // 'Close',
                iconCls: 'fa fa-times fa-2x',
                style: { color: 'green' },
                hidden: false,
                scale: 'medium',
                handler: function () {
                    me.close();
                }
            }]
        };

        me.items = [{
                xtype : 'grid',
                layout: 'fit',
                // store: 'ProductsInactiveStore',
                bind: '{products}',

                viewConfig: {
                    stripeRows: false,
                    enableTextSelection: true,
                    draggable:false,
                    markDirty: false,
                    resizable:false,
                    disableSelection: true,
                    trackOver:true
                },

                collapsible: false,
                enableColumnMove:false,
                enableColumnResize:false,
                multiColumnSort: false,
                columnLines: false,
                rowLines: true,
                frame: false,
                border: false,

                features: [{
                    id: 'categoriesactivateproducts',
                    ftype: 'grouping',
                    groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                    hideGroupedHeader: true,
                    enableGroupingMenu: false,
                    startCollapsed : true,
                    groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
                }],

                // columns : [{
                    // text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',
                    // menuDisabled: true,
                    columns: [{
                    //    xtype: 'actioncolumn',
                    //    hidden:false,
                    //    width: 35,
                    //    align: 'center',
                    //    sortable: false,
                    //    menuDisabled: true,
                    //    shrinkWrap: 0,
                    //    items: [{
                    //        //icon: 'resources/img/icons/edit.png',
                    //        getClass: function(v, meta, rec) {
                    //            return 'editproduct';
                    //            // if (rec.get('defined_by') != 'JRC') {
                    //            //     return 'editproduct';
                    //            // }
                    //            // else {
                    //            //     return 'x-hide-display';
                    //            // }
                    //        },
                    //        getTip: function(v, meta, rec) {
                    //            return esapp.Utils.getTranslation('editproduct');    // 'Edit Product',
                    //            // if (rec.get('defined_by') != 'JRC') {
                    //            //     return esapp.Utils.getTranslation('editproduct');    // 'Edit Product',
                    //            // }
                    //        },
                    //        //tooltip: esapp.Utils.getTranslation('editproduct'),  // 'Edit Product',
                    //        handler: 'editProduct'
                    //    }]
                    // }, {
                        xtype:'templatecolumn',
                        header: esapp.Utils.getTranslation('product'),  // 'Product',
                        tpl: new Ext.XTemplate(
                                '<b>{prod_descriptive_name}</b>' +
                                '<tpl if="version != \'undefined\'">',
                                    '<b class="smalltext"> - {version}</b>',
                                '</tpl>',
                                '<span class="smalltext">' +
                                '<b style="color:darkgrey;"> - {productcode}</b>' +
                                '<tpl if="provider != \'undefined\'">',
                                    '</br><b style="color:darkgrey;">{provider}</b>',
                                '</tpl>',
                                '<p>{description}</p>' +
                                '</span>'
                            ),
                        minWidth: 515,
                        cellWrap:true,
                        sortable: false,
                        hideable: false,
                        variableRowHeight : true,
                        menuDisabled:true
                    }, {
                        xtype: 'actioncolumn',
                        header: esapp.Utils.getTranslation('activate'),  // 'Active',
                        hideable: false,
                        hidden: false,
                        width: 90,
                        align: 'center',
                        shrinkWrap: 0,
                        menuDisabled: true,
                        stopSelection: false,
                        items: [{
                            height: 85,
                            getClass: function(v, meta, rec) {
                                if (rec.get('activated')) {
                                    return 'activated';
                                } else {
                                    return 'deactivated';
                                }
                            },
                            getTip: function(v, meta, rec) {
                                if (rec.get('activated')) {
                                    return esapp.Utils.getTranslation('deactivateproduct');  // 'Deactivate Product';
                                } else {
                                    return esapp.Utils.getTranslation('activateproduct');  // 'Activate Product';
                                }
                            },
                            // isDisabled: function(view, rowIndex, colIndex, item, record) {
                            //     // Returns true if 'editable' is false (, null, or undefined)
                            //     return false;    // !record.get('editable');
                            // },
                            handler: function(grid, rowIndex, colIndex, icon, e, record) {
                                var rec = record;
                                // var action = (rec.get('activated') ? 'deactivated' : 'activated');
                                rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                                rec.save();
                                rec.drop();
                                grid.up().up().changesmade = true;
                                Ext.toast({ html: esapp.Utils.getTranslation('product') + ' <b>' + rec.get('prod_descriptive_name') + '</b> (' + rec.get('productcode') + ') ' + esapp.Utils.getTranslation('activated') + '!',
                                            title: 'Product activated', width: 300, align: 't' });
                            }
                        }]
                    }]
                // }]
            }];

        me.callParent();
    }
    ,onClose: function(win, ev) {
        if (win.changesmade){
            var acquisitionmain = Ext.getCmp('acquisitionmain');
            acquisitionmain.setDirtyStore(true);
            acquisitionmain.fireEvent('loadstore');
        }
    }
});
