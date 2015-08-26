
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

        'Ext.layout.container.Center',
        'Ext.grid.plugin.CellEditing',
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
    resizable: true,
    autoScroll:true,
    maximizable: false,

    minWidth: 650,
    width: 650,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    layout: {
        type  : 'fit'
        //,padding: 5
    },

    bbar : {
        items : ['->',{
            text: esapp.Utils.getTranslation('newproduct'),  // 'New product',
            name: 'newproduct',
            iconCls: 'fa fa-plus-circle fa-2x',
            style: { color: 'green' },
            hidden: false,
            scale: 'medium',
            handler: function () {
                var newProductWin = new esapp.view.acquisition.product.editProduct({
                    params: {
                        edit: false
                    }
                });
                newProductWin.show();
            }
        }]
    },

    changesmade:false,


    initComponent: function () {
        var me = this
            ,cfg = {changesmade:false}
        ;
        Ext.apply(cfg, {

            listeners: {
                close:me.onClose
            },

            items : [{
                xtype : 'grid',
                //region: 'center',
                //width: 630,
                layout: 'fit',
                store: 'ProductsInactiveStore',
                session:true,

                plugins:[{
                    ptype:'cellediting'
                }],

                viewConfig: {
                    stripeRows: false,
                    enableTextSelection: true,
                    draggable:false,
                    markDirty: false,
                    resizable:false,
                    disableSelection: true,
                    trackOver:true
                },

                selModel : {
                    allowDeselect : true
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
                    id: 'selectproductcategories',
                    ftype: 'grouping',
                    groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                    hideGroupedHeader: true,
                    enableGroupingMenu: false,
                    startCollapsed : false,
                    groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
                }],

                //listeners: {
                //    rowclick: function(gridview, record){
                //        console.info(this);
                //        console.info(record);
                //        Ext.getCmp('productinfo').expand();
                //    }
                //},

                columns : [{
                    text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',
                    menuDisabled: true,
                    columns: [{
                        xtype: 'actioncolumn',
                        hidden:false,
                        width: 35,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        shrinkWrap: 0,
                        items: [{
                            icon: 'resources/img/icons/edit.png',
                            tooltip: esapp.Utils.getTranslation('editproduct'),  // 'Edit Product',
                            handler: 'editProduct'
                        }]
                    }, {
                        xtype:'templatecolumn',
                        header: esapp.Utils.getTranslation('product'),  // 'Product',
                        tpl: new Ext.XTemplate(
                                '<b>{prod_descriptive_name}</b>' +
                                '<tpl if="version != \'undefined\'">',
                                    '<b class="smalltext"> - {version}</b>',
                                '</tpl>',
                                '<span class="smalltext">' +
                                '<b style="color:darkgrey"> - {productcode}</b>' +
                                '<tpl if="provider != \'undefined\'">',
                                    '</br><b style="color:darkgrey">{provider}</b>',
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
                        header: esapp.Utils.getTranslation('active'),  // 'Active',
                        hideable: false,
                        hidden:false,
                        width: 65,
                        align: 'center',
                        shrinkWrap: 0,
                        items: [{
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
                            isDisabled: function(view, rowIndex, colIndex, item, record) {
                                // Returns true if 'editable' is false (, null, or undefined)
                                return false;    // !record.get('editable');
                            },
                            handler: function(grid, rowIndex, colIndex) {
                                var rec = grid.getStore().getAt(rowIndex),
                                    action = (rec.get('activated') ? 'deactivated' : 'activated');
                                // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                                rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                                grid.up().up().changesmade = true;
                                //Ext.getCmp('productinfo').collapse();
                            }
                        }]
                    }]
                }]
            //}, {
            //    region: 'east',
            //    id: 'productinfo',
            //    title: 'Product info',
            //    autoWidth:true,
            //    split: true,
            //    collapsible: true,
            //    collapsed: true,
            //    floatable: false,
            //    html: "TEST",
            //    listeners: {
            //        expand: function(){
            //            this.setWidth(600);
            //            this.up().setWidth(1240);
            //            me.center();
            //        },
            //        collapse: function(){
            //            this.setWidth(0);
            //            this.up().setWidth(668);
            //            me.center();
            //        }
            //    },
            //    items: [
            //        {
            //            xtype:''
            //        }
            //    ]
            }]
        });

        Ext.apply(me, cfg);
        me.callParent(arguments);
    }
    ,onClose: function(win, ev) {
        if (win.changesmade){
            Ext.data.StoreManager.lookup('ProductsActiveStore').load();
        }
    }
});
