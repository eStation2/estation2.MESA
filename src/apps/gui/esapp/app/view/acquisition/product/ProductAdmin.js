
Ext.define("esapp.view.acquisition.product.ProductAdmin",{
    "extend": "Ext.window.Window",

    "controller": "acquisition-product-productadmin",
    "viewModel": {
        "type": "acquisition-product-productadmin"
    },
    xtype: "productadmin",

    requires: [
        'esapp.view.acquisition.product.ProductAdminModel',
        'esapp.view.acquisition.product.ProductAdminController',
        'esapp.view.acquisition.product.editProduct',
        'esapp.view.acquisition.selectMapsetForIngest',

        // 'Ext.layout.container.Center',
        // 'Ext.grid.plugin.CellEditing',
        //'Ext.grid.column.Check',
        'Ext.XTemplate',
        'Ext.grid.column.Action'
    ],

    title: esapp.Utils.getTranslation('productadministration'),  // 'Product Administration',
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
    scrollable: 'y',    // vertical scrolling only
    maximizable: false,

    // minWidth: 700,
    width: 790,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    // layout: {
    //     type  : 'fit'
    // },

    config: {
        changesmade:false
    },

    initComponent: function () {
        var me = this;
        var user = esapp.getUser();

        me.setTitle('<div class="panel-title-style-16">' + esapp.Utils.getTranslation('productadministration') + '</div>');

        if ((esapp.Utils.objectExists(user) && user.userlevel == 1)) {
           me.width = 790;
        }
        else {
           me.width = 700;
        }

        me.listeners = {
            close: me.onClose,
            beforerender: function(){
                Ext.data.StoreManager.lookup('IngestSubProductsStore').load();
                // console.info(Ext.data.StoreManager.lookup('IngestSubProductsStore'));
            }
        };

        me.tbar = {
            items: [
            {
               text: esapp.Utils.getTranslation('newproduct'),  // 'New product',
               name: 'newproduct',
               iconCls: 'fa fa-plus-circle fa-2x',
               style: {color: 'green'},
               hidden: false,
               scale: 'medium',
               handler: function () {

                   var newProductWin = new esapp.view.acquisition.product.editProduct({
                       params: {
                           new: true,
                           edit: false,
                           view: false
                       }
                   });
                   newProductWin.show();
               }
            },
            '->',{
               text: esapp.Utils.getTranslation('eumetcastsources'),  // 'EUMETCAST Sources',
               name: 'eumetcastsources',
               iconCls: 'eumetsat-icon',        // 'fa fa-plus-circle fa-2x',
               // style: {color: 'green'},
               hidden: false,
               scale: 'medium',
               handler: function () {
                    // open EUMETCAST datasource administration window
                    var EumetcastSourceAdminWin = new esapp.view.acquisition.product.EumetcastSourceAdmin({
                        params: {
                            assigntoproduct: false,
                            product: null
                        }
                    });

                    EumetcastSourceAdminWin.show();
               }
            },
            {
               text: esapp.Utils.getTranslation('internetsources'),  // 'INTERNET Sources',
               name: 'internetsources',
               iconCls: 'internet-icon',    // 'fa fa-plus-circle fa-2x',
               // style: {color: 'green'},
               hidden: false,
               scale: 'medium',
               handler: function () {
                    // open INTERNET datasource administration window
                    var InternetSourceAdminWin = new esapp.view.acquisition.product.InternetSourceAdmin({
                        params: {
                            assigntoproduct: false,
                            product: null
                        }
                    });

                    InternetSourceAdminWin.show();
               }
            },
            {
               text: esapp.Utils.getTranslation('mapsets'),  // 'Mapsets',
               name: 'mapsetsadmin',
               iconCls: 'mapset-icon',    // 'fa fa-plus-circle fa-2x',
               style: {color: 'green'},
               hidden: false,
               scale: 'medium',
               handler: function () {
                   // open MAPSET administration window
                    var selectMapsetForIngestWin = new esapp.view.acquisition.product.MapsetAdmin({
                        productcode: null,
                        productversion: null,
                        subproductcode: null
                    });
                    selectMapsetForIngestWin.show();
               }
            },
                '->', {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'reloadProductsStore'
            }]
        };

        // me.bbar = {
        //     items: ['->', {
        //         text: esapp.Utils.getTranslation('close'),  // 'Close',
        //         iconCls: 'fa fa-times fa-2x',
        //         style: { color: 'green' },
        //         hidden: false,
        //         scale: 'medium',
        //         handler: function () {
        //             me.close();
        //         }
        //     }]
        // };

        me.items = [{
            xtype : 'grid',
            // layout: 'fit',
            store: 'ProductsStore',
            // session: true,
            // bind: '{products}',

            viewConfig: {
                stripeRows: false,
                enableTextSelection: true,
                draggable:false,
                markDirty: false,
                resizable:false,
                disableSelection: true,
                trackOver:true
            },

            bufferedRenderer: false,    // if true then the scrolling gives hickups so false
            scrollable: 'y',    // vertical scrolling only
            collapsible: false,
            enableColumnMove:false,
            enableColumnResize:false,
            multiColumnSort: false,
            columnLines: false,
            rowLines: true,
            frame: false,
            border: false,

            features: [{
                id: 'categoriesallproducts',
                ftype: 'grouping',
                groupHeaderTpl: Ext.create('Ext.XTemplate', '<div class="group-header-style">{name} ({children.length})</div>'),
                hideGroupedHeader: true,
                enableGroupingMenu: false,
                startCollapsed : false,
                groupByText: esapp.Utils.getTranslation('productcategories')  // 'Product categories'
            }],

            // listeners: {
            //     // itemdblclick: 'editProduct'
            //     'rowclick': function(grid, record, element, rowIndex, e, eOpts ) {
            //         console.info(record);
            //         console.info(element);
            //         console.info(rowIndex);
            //     }
            // },

            // plugins: [{
            //     ptype: 'rowexpander',
            //     rowBodyTpl : new Ext.XTemplate(
            //         '<div class="grid-color-azur">',
            //         // '<tpl for=".">',
            //         '<table class="x-grid-item" cellpadding="0" cellspacing="0" style="width:650px;">',
            //         '<tbody><tr class="wordwrap  x-grid-row">',
            //         '<td class="x-grid-cell x-grid-td x-grid-cell-first" style="width:220px;" tabindex="-1">',
            //         '	<div class="x-grid-cell-inner" style="text-align:left;"><b>{prod_descriptive_name}</b> <span class="smalltext"><b style="color:darkgrey"> - {productcode}</b></span></div>',
            //         '</td>',
            //         // '<td class="x-grid-cell x-grid-td" style="width: 80px;" tabindex="-1">',
            //         // '	<div class="x-grid-cell-inner " style="text-align:center;"><b style="color:darkgrey"> {productcode}</b></div>',
            //         // '</td>',
            //         '<td class="x-grid-cell x-grid-td x-wrap-cell" style="width: 40px;" tabindex="-1">',
            //         '	<div class="x-grid-cell-inner " style="text-align:left;"><b style="color:black">{product_type}</b></div>',
            //         '</td>',
            //         '<td class="x-grid-cell x-grid-td" style="width: 50px;" tabindex="-1">',
            //         '	<div class="x-grid-cell-inner " style="text-align:left;"><b style="color:black">{totgets} Mapsets</b></div>',
            //         '</td>',
            //         // '<td class="x-grid-cell x-grid-td x-grid-cell-last" style="width: 50px;" tabindex="-1">',
            //         // '	<div class="x-grid-cell-inner">Edit - Delete</div>',
            //         // '</td>',
            //         '</tr></tbody></table>',
            //         // '</tpl>',
            //         '</div>'
            //     )
            // }],

            // columns : [{
                // text: '<div class="grid-header-style">' + esapp.Utils.getTranslation('productcategories') + '</div>',
                // menuDisabled: true,
                columns: [{
                   xtype: 'actioncolumn',
                   reference: 'editproduct',
                   hidden: false,
                   width: 40,
                   align: 'center',
                   sortable: false,
                   menuDisabled: true,
                   shrinkWrap: 0,
                   items: [{
                       width:'35',
                       disabled: false,
                       //icon: 'resources/img/icons/edit.png',
                       getClass: function (v, meta, rec) {
                           // return 'editproduct';
                           if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                               return 'editproduct';
                           }
                           else {
                               // return 'x-hide-display';
                               return 'vieweye';
                           }
                       },
                       getTip: function (v, meta, rec) {
                           // return esapp.Utils.getTranslation('editproduct');    // 'Edit Product',
                           if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                               return esapp.Utils.getTranslation('editproduct');    // 'Edit Product',
                           }
                       },
                       //tooltip: esapp.Utils.getTranslation('editproduct'),  // 'Edit Product',
                       handler: 'editProduct'
                   }]
                }, {
                    xtype:'templatecolumn',
                    header: esapp.Utils.getTranslation('product'),  // 'Product',
                    reference: 'productinfocolumn',
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
                            // '<p>{description}</p>' +
                            '</span>'
                        ),
                    minWidth: 410,
                    cellWrap:true,
                    sortable: false,
                    hideable: false,
                    variableRowHeight : true,
                    menuDisabled:true
                }, {
                    xtype: 'actioncolumn',
                    header: esapp.Utils.getTranslation('activate'),  // 'Active',
                    reference: 'activateproduct',
                    hideable: false,
                    hidden: false,
                    width: 75,
                    align: 'center',
                    shrinkWrap: 0,
                    menuDisabled: true,
                    sortable: false,
                    stopSelection: false,
                    items: [{
                        height: 85,
                        getClass: function (v, meta, rec) {
                            if (rec.get('activated')) {
                                return 'activated';
                            } else {
                                return 'deactivated';
                            }
                        },
                        getTip: function (v, meta, rec) {
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
                        handler: function (grid, rowIndex, colIndex, icon, e, record) {
                            var rec = record;
                            // var action = (rec.get('activated') ? 'deactivated' : 'activated');
                            rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                            // rec.save();
                            // rec.drop();
                            me.changesmade = true;
                            // grid.up().up().changesmade = true;

                            if (rec.get('activated')){
                                Ext.toast({
                                    html: esapp.Utils.getTranslation('product') + ' <b>' + rec.get('prod_descriptive_name') + '</b> (' + rec.get('productcode') + ') ' + esapp.Utils.getTranslation('activated') + '!',
                                    title: esapp.Utils.getTranslation('productactivated'), width: 300, align: 't'
                                });
                            }
                            else {
                                Ext.toast({
                                    html: esapp.Utils.getTranslation('product') + ' <b>' + rec.get('prod_descriptive_name') + '</b> (' + rec.get('productcode') + ') ' + esapp.Utils.getTranslation('deactivated') + '!',
                                    title: esapp.Utils.getTranslation('productdeactivated'), width: 300, align: 't'
                                });
                            }
                        }
                    }]
                },{
                    header: esapp.Utils.getTranslation('nrsubproducts'),  // 'Subproducts',
                    reference: 'totsubprods',
                    dataIndex: 'totsubprods',
                    width: 110,
                    minWidth: 80,
                    align: 'center',
                    menuDisabled: true,
                    sortable: false,
                    cellWrap:true
                // },{
                //     header: esapp.Utils.getTranslation('nrdatasources'),  // 'Datasources',
                //     dataIndex: 'totdatasources',
                //     width: 110,
                //     minWidth: 80,
                //     align: 'center',
                //     menuDisabled: true,
                //     sortable: false,
                //     cellWrap:true
                },{
                    header: esapp.Utils.getTranslation('definedby'),  // 'Defined by',
                    reference: 'defined_by_column',
                    dataIndex: 'defined_by',
                    width: 90,
                    minWidth: 80,
                    align: 'center',
                    menuDisabled: true,
                    sortable: false,
                    cellWrap:true,
                    hidden: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? false : true
                },{
                   xtype: 'actioncolumn',
                   reference: 'deleteproduct',
                   hidden: false,
                   width: 35,
                   align: 'center',
                   sortable: false,
                   menuDisabled: true,
                   shrinkWrap: 0,
                   items: [{
                       width:'35',
                       disabled: false,
                       isDisabled: function(view, rowIndex, colIndex, item, record){
                            if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                return false;
                            }
                            else {
                                return true;
                            }
                       },
                       getClass: function(cell, meta, rec) {
                           if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                               return 'delete';
                           }
                           else {
                               // cell.setDisabled(true);   // This will not make syncing record content possible!
                               return 'x-hide-display';
                           }
                       },
                       getTip: function(v, meta, rec) {
                           // console.info(rec);
                           if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                               var tipText = esapp.Utils.getTranslation('delete_product-and-its-subproducts') + ': <BR>' +
                                         '<b>'+ rec.get('prod_descriptive_name')+'</b>';

                               if (rec.get('version') != ''){
                                   tipText += '<b> - ' + rec.get('version') + '</b>';
                                   // tipText += '<span class="smalltext"><b> - ' + rec.get('version') + '</b></span>';
                               }
                               tipText += '<b> - ' + rec.get('productcode') + '</b>';
                               // tipText += '<span class="smalltext"><b style="color:darkgrey"> - ' + rec.get('productcode') + '</b></span>';
                               return tipText;
                           }
                       },
                       handler: 'deleteProduct'
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
