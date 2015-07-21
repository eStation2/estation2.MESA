
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

        'Ext.form.FieldSet',
        'Ext.form.field.Number',
        'Ext.Action'
    ],

    session:true,

    title: '',
    titleAlign: 'center',
    modal: true,
    resizable: false,
    closable: true,
    closeAction: 'destroy', // 'hide',
    border:true,
    frame:true,
    autoScroll:false,
    fieldDefaults: {
        labelWidth: 120,
        labelAlign: 'left'
    },
    bodyPadding:'10 15 5 15',
    viewConfig:{forceFit:true},
    layout:'vbox',

    params: {},


    initComponent: function () {
        var me = this;

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editproduct') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newproduct') + '</span>');
        }

        var deleteDataSourceAction = Ext.create('Ext.Action', {
            text: 'Unassign',
            iconCls: 'fa fa-chain-broken fa-2x',
            style: { color: 'red' },
            scale: 'medium',
            disabled: true,
            handler: 'deleteDataSource'
        });

        var addDataSourceAction = Ext.create('Ext.Action', {
            text: 'Add',
            iconCls: 'fa fa-plus-circle fa-2x',
            style: { color: 'green' },
            scale: 'medium',
            disabled: false,
            handler: 'addDataSource'
        });

        me.items = [{
            //margin:'0 15 5 0',
            items: [{
                xtype: 'fieldset',
                title: '<b>Product info</b>',
                collapseable:false,
                width:565,
                //height:500,
                padding:'10 10 10 10',
                //layout: 'fit',
                defaults: {
                    //autoWidth: true,
                    labelWidth: 120
                },
                items:[{
                    id: 'category',
                    name: 'category',
                    //bind: '{product.category_id}',
                    xtype: 'combobox',
                    fieldLabel: 'Category',
                    width:150+120,
                    allowBlank: false,
                    //store: 'categories',
                    store: {
                        type: 'categories'
                    },
                    valueField: 'category_id',
                    displayField: 'descriptive_name',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: 'Select a category...'

                },{
                    id: 'productcode',
                    name: 'productcode',
                    //bind: '{product.productcode}',
                    xtype: 'textfield',
                    fieldLabel: 'Product code',
                    width:150+120,
                    allowBlank: false
                },{
                    id: 'version',
                    name: 'version',
                    //bind: '{product.version}',
                    xtype: 'textfield',
                    fieldLabel: 'Version',
                    width:150+120,
                    allowBlank: false
                },{
                    id: 'provider',
                    name: 'provider',
                    //bind: '{product.provider}',
                    xtype: 'textfield',
                    fieldLabel: 'Provider',
                    width:530,
                    allowBlank: true
                },{
                    id: 'product_name',
                    name: 'product_name',
                    //bind: '{product.prod_descriptive_name}',
                    xtype: 'textfield',
                    fieldLabel: 'Product name',
                    width:530,
                    allowBlank: true
                }, {
                    id: 'productdescription',
                    name: 'productdescription',
                    //bind: '{product.description}',
                    xtype: 'textareafield',
                    fieldLabel: 'Product description',
                    labelAlign: 'top',
                    width: 530,
                    allowBlank: true,
                    grow: true
                },{
                    xtype: 'button',
                    text: 'Save',
                    //scope:me,
                    iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                    style: { color: 'lightblue' },
                    scale: 'medium',
                    disabled: false,
                    handler: 'saveProductInfo'
                }]
            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: '<b>Data sources</b>',
                id: 'datasourcesfieldset',
                hidden: true,
                collapseable:false,
                padding:'10 10 10 10',
                width: 565,

                items:[{
                    xtype: 'grid',
                    reference: 'productDataSourcesGrid',
                    //store: 'productdatasources',
                    bind:{
                        store:'{productdatasources}'
                    },
                    //session: true,
                    stateful: false,

                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        items: [
                            '->', addDataSourceAction, deleteDataSourceAction
                        ]
                    }],

                    viewConfig: {
                        stripeRows: false,
                        enableTextSelection: true,
                        draggable: false,
                        markDirty: false,
                        resizable: true,
                        disableSelection: false,
                        trackOver: true
                    },

                    selModel: {
                        allowDeselect: true
                        ,listeners: {
                            selectionchange: function (sm, selections) {
                                if (selections.length) {
                                    deleteDataSourceAction.enable();
                                } else {
                                    deleteDataSourceAction.disable();
                                }
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

                    columns: [{
                        xtype: 'actioncolumn',
                        hidden: false,
                        width: 35,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        items: [{
                            icon: 'resources/img/icons/edit.png',
                            tooltip: 'Edit Data Source',
                            handler: 'editDataSource'
                        }]
                    }, {
                        header: 'Type',
                        dataIndex: 'type',
                        //bind: '{productdatasources.type}',
                        width: 120,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        header: 'ID',
                        dataIndex: 'data_source_id',
                        //bind: '{productdatasources.data_source_id}',
                        width: 300,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    }, {
                        xtype: 'actioncolumn',
                        header: 'Active',
                        hideable: false,
                        hidden: false,
                        menuDisabled: true,
                        width: 65,
                        align: 'center',
                        shrinkWrap: 0,
                        items: [{
                            getClass: function (v, meta, rec) {
                                if (rec.get('activated')) {
                                    return 'activated';
                                } else {
                                    return 'deactivated';
                                }
                            },
                            getTip: function (v, meta, rec) {
                                if (rec.get('activated')) {
                                    return 'Deactivate Data Source';
                                } else {
                                    return 'Activate Data Source';
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
                    }]
                }]

            }]
        }];

        me.callParent();

        me.controller.setup();

    }
});
