
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

        'Ext.layout.container.Center',
        'Ext.grid.plugin.CellEditing',
        //'Ext.grid.column.Check',
        'Ext.XTemplate',
        'Ext.grid.column.Action'
    ],

    title: 'Activate Product',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: false,
    width: 685,
    height: 800,
    layout: {
        type  : 'border',
        padding: 5
    },
    autoScroll: false,
    changesmade:false,

//    tbar: Ext.create('Ext.toolbar.Toolbar', {
//            items: [
//                {
//                    xtype: 'button',
//                    text: 'Select Product',
//                    name: 'selectroduct',
//                    iconCls: 'fa fa-plus-circle',
//                    style: { color: 'gray' },
//                    hidden: true,
//                    // glyph: 'xf055@FontAwesome',
//                    scale: 'small',
//                    handler: ''
//                }
//            ]
//        }),

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
                region: 'center',
                width: 650,
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
                    groupByText: 'Product category'
                }],

                listeners: {
                    rowclick: function(gridview, record){
                        //console.info(this);
                        //console.info(record);
                        //var productinfo = Ext.ComponentQuery.query('panel[id=productinfo]')[0];
                        //productinfo.expand(true);
                    }
                },

                columns : [{
                    text: '<div class="grid-header-style">Product categories</div>',
                    menuDisabled: true,
                    columns: [{
                        xtype: 'actioncolumn',
                        hidden:true,
                        width: 30,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        shrinkWrap: 0,
                        items: [{
                            icon: 'resources/img/icons/edit.png',
                            // iconCls: 'fa fa-edit fa-2x', // xf044
                            // cls: 'fa fa-edit fa-2x', // xf044
                            tooltip: 'Edit Product',
                            handler: 'editProduct'
                        }]
                    }, {
                        xtype:'templatecolumn',
                        header: 'Product',
                        tpl: new Ext.XTemplate(
                                //'<b>{prod_descriptive_name}</b> <br> ' +
                                //'<span class="smalltext">' +
                                //'<b style="color:darkgrey">{productcode}' +
                                //    '<tpl if="version != \'undefined\'">',
                                //        ' - {version}',
                                //    '</tpl>',
                                //'</b>' +
                                //'<p>{description}</p>' +
                                //'</span>' +
                                //
                                '<b>{prod_descriptive_name}</b>' +
                                '<tpl if="version != \'undefined\'">',
                                    '<b class="smalltext"> - {version}</b>',
                                '</tpl>',
                                '</br><span class="smalltext">' +
                                '<b style="color:darkgrey">{productcode}</b>' +
                                '<p>{description}</p>' +
                                '</span></br>'
                            ),
                        width: 500,
                        cellWrap:true,
                        sortable: false,
                        hideable: false,
                        variableRowHeight : true,
                        menuDisabled:true
                    }, {
                        xtype: 'actioncolumn',
                        header: 'Active',
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
                                    return 'Deactivate Product';
                                } else {
                                    return 'Activate Product';
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
                            }
                        }]
        //                xtype: 'checkcolumn',
        //                header: 'Active',
        //                width: 80,
        //                sortable: false,
        //                dataIndex: 'activated',
        //                stopSelection: false,
        //                disabled: false,
        //                menuDisabled:true,
        //                listeners: {
        //                  checkchange: function(chkBox, rowIndex, checked, eOpts){
        ////                      console.info(chkBox);
        ////                      console.info(rowIndex);
        ////                      console.info(checked);
        ////                      console.info(eOpts);
        //                  }
        //                }
                    }]
                }]
            }, {
                region: 'east',
                id: 'productinfo',
                title: 'Product info',
                autoWidth:true,
                split: true,
                collapsible: true,
                collapsed: true,
                floatable: false,
                html: "TEST",
                listeners: {
                    expand: function(){
                        this.setWidth(600);
                        this.up().setWidth(1285);
                    },
                    collapse: function(){
                        this.setWidth(5);
                        this.up().setWidth(685);
                    }
                },
                items: [
                    {
                        xtype:''
                    }
                ]
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
