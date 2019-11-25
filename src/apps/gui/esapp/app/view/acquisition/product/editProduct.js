
Ext.define("esapp.view.acquisition.product.editProduct",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-editproduct",
    "viewModel": {
        "type": "acquisition-product-editproduct"
    },
    xtype: "editproduct",

    requires: [
        'esapp.view.acquisition.product.editProductModel',
        'esapp.view.acquisition.product.editProductController',
        'esapp.view.acquisition.product.InternetSourceAdmin',
        'esapp.view.acquisition.product.EumetcastSourceAdmin',
        'esapp.view.acquisition.product.editIngestSubProduct',

        'Ext.form.FieldSet',
        'Ext.form.field.Number',
        'Ext.Action'
    ],

    // session:true,

    title: '',
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
    autoScroll: true,
    maximizable: false,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 830,  // 600,
    maxHeight: 830,

    border: true,
    frame: true,
    fieldDefaults: {
        labelWidth: 120,
        labelAlign: 'left'
    },
    bodyPadding: '10 15 5 15',
    viewConfig: {forceFit:true},
    layout: 'vbox',

    params: {
        new: false,
        view: true,
        edit: false,
        product: null,
        orig_productcode: '',
        orig_version: ''
    },


    initComponent: function () {
        var me = this;
        var user = esapp.getUser();
        var width_fieldsets = 685;

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editproduct') + '</span>');
        }
        else if (me.params.view){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('viewproduct') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newproduct') + '</span>');
            me.height = 400;
        }

        me.listeners = {
            close: me.onClose
        };


        me.items = [{
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('productinfo')+'</div>',   // '<b>Product info</b>',
                collapsible: false,
                width: width_fieldsets,
                padding: '10 5 10 10',
                defaults: {
                    disabled: me.params.view ? true : false,
                    labelWidth: 120
                },
                items:[{
                    xtype: 'container',
                    disabled: false,
                    width: width_fieldsets,
                    layout: 'hbox',
                    defaults: {
                        disabled: me.params.view ? true : false,
                        labelWidth: 120
                    },
                    items: [{
                        id: 'category',
                        name: 'category',
                        //bind: '{product.category_id}',
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('category'),    // 'Category',
                        width: 150 + 100,
                        allowBlank: false,
                        // store: 'categories',
                        store: {
                            type: 'categoriesall'
                        },
                        valueField: 'category_id',
                        displayField: 'descriptive_name',
                        typeAhead: false,
                        queryMode: 'local',
                        emptyText: esapp.Utils.getTranslation('selectacategory')    // 'Select a category...'
                    },{
                        id: 'activate_product_field',
                        name: 'activate_product_field',
                        xtype: 'checkboxfield',
                        boxLabel : esapp.Utils.getTranslation('activate'),
                        labelWidth: 100,
                        inputValue: '0',
                        margin: '0 0 5 80',
                        hidden: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? false : true
                    }]
                },{
                    xtype: 'container',
                    disabled: false,
                    width: 600,
                    layout: 'hbox',
                    defaults: {
                        disabled: me.params.view ? true : false,
                        labelWidth: 120
                    },
                    items: [{
                        id: 'productcode',
                        name: 'productcode',
                        //bind: '{product.productcode}',
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('productcode'),    // 'Product code',
                        width: 150 + 100,
                        allowBlank: false
                    },{
                        id: 'defined_by_field',
                        name: 'defined_by_field',
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('definedby'),
                        labelWidth: 100,
                        width: 150 + 100,
                        margin: '0 0 5 80',
                        allowBlank: false,
                        editable: false,
                        store: {
                            type: 'definedby'
                        },
                        valueField: 'defined_by',
                        displayField: 'defined_by_descr',
                        typeAhead: false,
                        queryMode: 'local',
                        emptyText: esapp.Utils.getTranslation('select'),    // 'Select...'
                        hidden: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? false : true
                    }]
                },{
                    id: 'version',
                    name: 'version',
                    //bind: '{product.version}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('version'),    // 'Version',
                    width:150+120,
                    allowBlank: false
                },{
                    id: 'provider',
                    name: 'provider',
                    //bind: '{product.provider}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('provider'),    // 'Provider',
                    width:530,
                    allowBlank: true
                },{
                    id: 'product_name',
                    name: 'product_name',
                    //bind: '{product.prod_descriptive_name}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('product_name'),    // 'Product name',
                    width:530,
                    allowBlank: true
                }, {
                    id: 'productdescription',
                    name: 'productdescription',
                    //bind: '{product.description}',
                    // xtype: 'textareafield',
                    xtype: 'htmleditor',
                    fieldLabel: esapp.Utils.getTranslation('productdescription'),    // 'Product description',
                    labelAlign: 'top',
                    width: 650,
                    height: 130,
                    minHeight: 130,
                    scrollable: true,
                    allowBlank: true,
                    grow: true,
                    growMax: 130,

                    layout: 'fit',
                    resizable: true,
                    resizeHandles: 's',
                    style: 'background: white;',
                    hidden: false,
                    enableAlignments: false,
                    enableColors: true,
                    enableFont: true,
                    enableFontSize: true,
                    enableFormat: true,
                    enableLinks: false,
                    enableLists: false,
                    enableSourceEdit: true
                },{
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('save'),    // 'Save',
                    //scope:me,
                    iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                    style: { color: 'lightblue' },
                    scale: 'medium',
                    hidden: me.params.view ? true : false,
                    handler: 'saveProductInfo'
                }]
            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('datasources')+'</div>',   // '<b>Data sources</b>',
                id: 'datasourcesfieldset',
                hidden: true,
                collapsible: false,
                padding: '10 10 10 10',
                width: width_fieldsets,

                items:[{
                    xtype: 'grid',
                    reference: 'productDataSourcesGrid',
                    //store: 'productdatasources',
                    bind:{
                        store:'{productdatasources}'
                    },
                    // session: true,
                    // stateful: false,

                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        // disabled: me.params.view ? true : false,
                        items: [
                            '->',
                            {
                                reference: 'addDataSource-btn',
                                text: esapp.Utils.getTranslation('add'),    // 'Add',
                                iconCls: 'fa fa-plus-circle fa-2x',
                                style: { color: 'green' },
                                scale: 'medium',
                                disabled: false,
                                handler: 'addDataSource'
                            // },{
                            //     reference: 'unassignDataSource-btn',
                            //     text: esapp.Utils.getTranslation('unassign'),    // 'Unassign',
                            //     iconCls: 'fa fa-chain-broken fa-2x',
                            //     style: { color: 'red' },
                            //     scale: 'medium',
                            //     disabled: true,
                            //     handler: 'unassignDataSource'
                            }
                            // addDataSourceAction, unassignDataSourceAction
                        ]
                    }],

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: false,
                        disableSelection: false,
                        trackOver: true
                    },

                    // selModel: {
                    //     allowDeselect: true
                    //     ,listeners: {
                    //         selectionchange: function (sm, selections) {
                    //             // if (selections.length) {
                    //             //     me.lookupReference('unassignDataSource-btn').enable();
                    //             //     // unassignDataSourceAction.enable();
                    //             // } else {
                    //             //     me.lookupReference('unassignDataSource-btn').disable();
                    //             //     // unassignDataSourceAction.disable();
                    //             // }
                    //         }
                    //     }
                    // },

                    layout: 'fit',
                    autoHeight: true,
                    minHeight: 105,
                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: true,
                    multiColumnSort: false,
                    columnLines: false,
                    rowLines: true,
                    frame: false,
                    border: true,

                    cls: 'grid-column-header-multiline',

                    // defaults: {
                    //     disabled: me.params.view ? true : false
                    // },

                    columns: [{
                        xtype: 'actioncolumn',
                        hidden: false,
                        width: 40,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        items: [{
                            getClass: function (cell, meta, rec) {
                                // console.info(rec.get('defined_by'));
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                                   return 'edit';
                               }
                               else {
                                   // return 'x-hide-display';
                                   return 'vieweye';
                               }
                            },
                            getTip: function (cell, meta, rec) {
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                                   return esapp.Utils.getTranslation('editdatasource')    // 'Edit Data Source',
                               }
                            },
                            handler: 'editDataSource'
                        }]
                    }, {
                        header: esapp.Utils.getTranslation('type'),    // 'Type',
                        dataIndex: 'type',
                        //bind: '{productdatasources.type}',
                        width: 110,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        header: esapp.Utils.getTranslation('id'),    // 'ID',
                        dataIndex: 'data_source_id',
                        //bind: '{productdatasources.data_source_id}',
                        width: 270,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        xtype: 'actioncolumn',
                        header: esapp.Utils.getTranslation('storenative'),    // 'Active',
                        hideable: false,
                        hidden: false,
                        menuDisabled: true,
                        width: 130,
                        align: 'center',
                        shrinkWrap: 0,
                        items: [{
                            // scope: me,
                            disabled: false,
                            getClass: function(cell, meta, rec) {
                                if (rec.get('store_original_data')) {
                                    return 'activated';
                                } else {
                                    return 'deactivated';
                                }
                            },
                            getTip: function(cell, meta, rec) {
                                if (rec.get('store_original_data')) {
                                    return esapp.Utils.getTranslation('tipdeactivatestoreoriginalget');     // 'Deactivate store original data for this Get';
                                } else {
                                    return esapp.Utils.getTranslation('tipactivatestoreoriginalget');     // 'Activate store original data for this Get';
                                }
                            },
                            handler: function(grid, rowIndex, colIndex) {
                                var rec = grid.getStore().getAt(rowIndex),
                                    action = (rec.get('store_original_data') ? 'deactivated' : 'activated');
                                // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                                rec.get('store_original_data') ? rec.set('store_original_data', false) : rec.set('store_original_data', true);
                                grid.up().up().changesmade = true;
                            }
                        }]
                    }, {
                        xtype: 'actioncolumn',
                        header: esapp.Utils.getTranslation('active'),    // 'Active',
                        hideable: false,
                        hidden: false,
                        menuDisabled: true,
                        width: 70,
                        align: 'center',
                        shrinkWrap: 0,
                        items: [{
                            getClass: function (cell, meta, rec) {
                                if (rec.get('activated')) {
                                    return 'activated';
                                } else {
                                    return 'deactivated';
                                }
                            },
                            getTip: function (cell, meta, rec) {
                                if (rec.get('activated')) {
                                    return esapp.Utils.getTranslation('deactivatedatasource');    // 'Deactivate Data Source';
                                } else {
                                    return esapp.Utils.getTranslation('activatedatasource');    // 'Activate Data Source';
                                }
                            },
                            isDisabled: function (view, rowIndex, colIndex, item, record) {
                                // Returns true if 'editable' is false (, null, or undefined)
                                return false;    // !record.get('editable');
                            },
                            handler: function (grid, rowIndex, colIndex) {
                                var rec = grid.getStore().getAt(rowIndex),
                                    action = (rec.get('activated') ? 'deactivated' : 'activated');
                                // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                                rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                                grid.up().up().changesmade = true;
                            }
                        }]
                    },{
                       xtype: 'actioncolumn',
                       hidden: false,
                       width: 35,
                       align: 'center',
                       sortable: false,
                       menuDisabled: true,
                       shrinkWrap: 0,
                       items: [{
                           width:'35',
                           // disabled: false,
                           isDisabled: function(view, rowIndex, colIndex, item, record){
                                if (!record.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                    return false;
                                }
                                else {
                                    return true;
                                }
                           },
                           getClass: function(cell, meta, rec) {
                               // return 'delete';
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                   return 'delete';
                               }
                               else {
                                   // cell.setDisabled(true);
                                   return 'x-hide-display';
                               }
                           },
                           getTip: function(cell, meta, rec) {
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                   var tipText = esapp.Utils.getTranslation('unassignproductdatasource') + ': <BR>' +
                                       '<b>' + Ext.getCmp('product_name').getValue() + '</b>';

                                   if (Ext.getCmp('version').getValue() != ''){
                                       tipText += '<b> - ' + Ext.getCmp('version').getValue() + '</b>' ;
                                       // tipText += '<span class="smalltext">' + '<b> - ' + Ext.getCmp('version').getValue() + '</b></span>' ;
                                   }

                                   tipText += '<b style="color:darkgrey;"> - ' + Ext.getCmp('productcode').getValue() + '</b>';
                                   // tipText += '<span class="smalltext">' + '<b style="color:darkgrey"> - ' + Ext.getCmp('productcode').getValue() + '</b></span>';
                                   return tipText;
                               }
                           },
                           handler: 'unassignDataSource'
                       }]
                    }]
                }]

            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('ingestedproducts')+'</div>',   // 'Ingested SubProducts',
                id: 'ingestionsfieldset',
                hidden: true,
                collapsible:false,
                padding:'10 10 10 10',
                width: width_fieldsets,

                items:[{
                    xtype: 'grid',
                    reference: 'productIngestionsGrid',
                    //store: 'ingestsubproducts',
                    bind:{
                        store:'{ingestsubproducts}'
                    },
                    // session: true,
                    // stateful: false,

                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        disabled: me.params.view ? true : false,
                        items: [
                            '->',
                            {
                                reference: 'addIngestion-btn',
                                text: esapp.Utils.getTranslation('add'),    // 'Add',
                                iconCls: 'fa fa-plus-circle fa-2x',
                                style: { color: 'green' },
                                scale: 'medium',
                                disabled: false,
                                handler: 'addIngestSubProduct'
                            // },{
                            //     reference: 'deleteIngestion-btn',
                            //     text: esapp.Utils.getTranslation('delete'),    // 'Delete',
                            //     iconCls: 'fa fa-trash-o fa-2x',
                            //     style: { color: 'red' },
                            //     scale: 'medium',
                            //     disabled: true,
                            //     handler: 'deleteIngestion'
                            }
                        ]
                    }],

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: false,
                        disableSelection: false,
                        trackOver: true
                    },

                    // selModel: {
                    //     allowDeselect: true
                    //     ,listeners: {
                    //         selectionchange: function (sm, selections) {
                    //             // if (selections.length) {
                    //             //     me.lookupReference('deleteIngestion-btn').enable();
                    //             //     // deleteIngestionAction.enable();
                    //             // } else {
                    //             //     me.lookupReference('deleteIngestion-btn').disable();
                    //             //     // deleteIngestionAction.disable();
                    //             // }
                    //         }
                    //     }
                    // },

                    layout: 'fit',
                    autoHeight: true,
                    minHeight: 105,
                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: true,
                    multiColumnSort: false,
                    columnLines: false,
                    rowLines: true,
                    frame: false,
                    border: true,

                    cls: 'grid-column-header-multiline',

                    // defaults: {
                    //     disabled: me.params.view ? true : false
                    // },

                    columns: [{
                        xtype: 'actioncolumn',
                        hidden: false,
                        width: 40,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        items: [{
                            // icon: 'resources/img/icons/edit.png',
                            // tooltip: esapp.Utils.getTranslation('editingestion'),    // 'Edit Ingestion',
                            getClass: function (cell, meta, rec) {
                                // console.info(rec.get('defined_by'));
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                                   return 'edit';
                               }
                               else {
                                   // return 'x-hide-display';
                                   return 'vieweye';
                               }
                            },
                            getTip: function (cell, meta, rec) {
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel <= 1)) {
                                   return esapp.Utils.getTranslation('editingestsubproduct')    // 'Edit Ingest Sub Product',
                               }
                            },
                            handler: 'editIngestSubProduct'
                        }]
                    }, {
                        xtype:'templatecolumn',
                        text: esapp.Utils.getTranslation('subproduct'),
                        tpl: new Ext.XTemplate(
                                '<b>{descriptive_name}</b>' +
                                // '<tpl if="version != \'undefined\'">',
                                //     '<b class="smalltext"> - {version}</b>',
                                // '</tpl>',
                                '<BR><span class="smalltext"><b style="color:darkgrey;">' +
                                '{productcode}' +
                                '<tpl if="version != \'undefined\'">',
                                    ' - {version}',
                                '</tpl>',
                                ' - {subproductcode}' +
                                '</span></b>'
                            ),
                        width: 220,
                        cellWrap:true,
                        sortable: false,
                        hideable: false,
                        variableRowHeight : true,
                        menuDisabled:true
                    }, {
                        text: esapp.Utils.getTranslation('scale_factor'),
                        headerWrap: true,
                        dataIndex: 'scale_factor',
                        width: 80,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        text: esapp.Utils.getTranslation('scale_offset'),
                        headerWrap: true,
                        dataIndex: 'scale_offset',
                        width: 140,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        text: esapp.Utils.getTranslation('nodata'),
                        headerWrap: true,
                        dataIndex: 'nodata',
                        width: 80,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    },{
                        text: esapp.Utils.getTranslation('definedby'),  // 'Defined by',
                        dataIndex: 'defined_by',
                        width: 60,
                        align: 'center',
                        menuDisabled: true,
                        sortable: false,
                        cellWrap:true,
                        hidden: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? false : true
                    },{
                       xtype: 'actioncolumn',
                       hidden: false,
                       width: 35,
                       align: 'center',
                       sortable: false,
                       menuDisabled: true,
                       shrinkWrap: 0,
                       items: [{
                           width:'35',
                           disabled: false,
                           getClass: function(cell, meta, rec) {
                               // return 'delete';
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                   return 'delete';
                               }
                               else {
                                   // cell.setDisabled(true);
                                   return 'x-hide-display';
                               }
                           },
                           getTip: function(cell, meta, rec) {
                               if (!rec.get('defined_by').includes('JRC') || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                                   var tipText = esapp.Utils.getTranslation('delete_ingest_product') + ': <BR>' +
                                       '<b>' + rec.get('descriptive_name') + '</b>';

                                   if (rec.get('version') != ''){
                                       tipText += '<b> - ' + rec.get('version') + '</b>' ;
                                       // tipText += '<span class="smalltext">' + '<b> - ' + Ext.getCmp('version').getValue() + '</b></span>' ;
                                   }

                                   tipText += '<b> - ' + rec.get('productcode') + '</b>';
                                   tipText += '<b> - ' + rec.get('subproductcode') + '</b>';
                                   // tipText += '<span class="smalltext">' + '<b style="color:darkgrey"> - ' + Ext.getCmp('productcode').getValue() + '</b></span>';
                                   return tipText;
                               }
                           },
                           handler: 'deleteIngestSubProduct'
                       }]
                    }]
                }]

            }]
        }];

        me.callParent();

        me.controller.setup();

    }
    ,onClose: function(win, ev) {
        Ext.data.StoreManager.lookup('ProductsStore').load();
    }
});
