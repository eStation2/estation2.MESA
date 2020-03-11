
Ext.define("esapp.view.acquisition.product.editIngestSubProduct",{
    extend: "Ext.window.Window",
    "controller": "acquisition-product-editingestsubproduct",
    "viewModel": {
        "type": "acquisition-product-editingestsubproduct"
    },

    xtype: 'editingestsubproduct',

    requires: [
        'esapp.view.acquisition.product.editIngestSubProductController',
        'esapp.view.acquisition.product.editIngestSubProductModel',

        'Ext.layout.container.Center'
    ],

    bind: {
        title: '{title}'
    },
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

    // width: 870,
    height: Ext.getBody().getViewSize().height < 660 ? Ext.getBody().getViewSize().height-35 : 825,
    maxHeight: 825,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'vbox',

    params: {
        // productcode: null,
        // version: null,
        // category_id: null,
        // provider: null,
        // defined_by: null,
        // product_type: 'Ingest'
        create: false,
        view: true,
        edit: false,
        ingestsubproductrecord: null,
        orig_subproductcode: null
    },

    initComponent: function () {
        var me = this;
        var labelwidth = 120;
        var user = esapp.getUser();

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editingestsubproduct') + '</span>');
            me.params.orig_subproductcode = me.params.ingestsubproductrecord.get('subproductcode');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newingestsubproduct') + '</span>');
            me.height = 700;
        }


        me.listeners = {
            beforerender: function(){
                Ext.data.StoreManager.lookup('SubDatasourceDescriptionStore').load();
            },
            afterrender: function(){
                // console.info(me);
                // console.info(me.params.create);
                // if (me.params.create){
                //     me.lookupReference('productid').setValue('');
                // }
            },
            beforeclose: function(){
                if (Ext.data.StoreManager.lookup('IngestSubProductsStore').getUpdatedRecords() !== []){
                    Ext.data.StoreManager.lookup('IngestSubProductsStore').rejectChanges();
                }
                Ext.data.StoreManager.lookup('IngestSubProductsStore').load();
            }
        };


        var categoryrec = Ext.data.StoreManager.lookup('categoriesall').findRecord('category_id', me.params.ingestsubproductrecord.get('category_id'), 0, true, false, false);
        me.params.categoryname = categoryrec.get('descriptive_name');

        me.items = [{
            xtype: 'form',
            reference: 'ingestsubproductform',
            border: false,
            // use the Model's validations for displaying form errors
            // modelValidation: true,
            fieldDefaults: {
                labelAlign: 'left',
                labelStyle: 'font-weight: bold;',
                msgTarget: 'right',
                preventMark: false
            },

            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">' + esapp.Utils.getTranslation('ingestsubproductdefinition') + '</div>',  // '<b>Ingested Sub Product definition</b>',
                id: 'ingestsubproductinfofieldset',
                hidden: false,
                collapsible: false,
                padding: '10 10 10 20',
                margin: '10 10 10 10',
                width: 660,
                defaults: {
                    width: 630,
                    labelWidth: labelwidth,
                    msgTarget: 'side'
                },
                items: [{
                    xtype: 'container',
                    defaults: {
                        disabled: me.params.view ? true : false,
                        labelWidth: labelwidth,
                        padding: '0 10 5 10'
                    },
                    layout: {
                        type: 'hbox'
                        // , align: 'stretch'
                    },
                    items: [{
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('category'),
                        labelAlign: 'top',
                        reference: 'category',
                        value: me.params.categoryname,
                        // bind: '{theIngestSubProduct.category_id}',
                        allowBlank: false,
                        padding: '0 10 10 0',
                        cls:'greenbold',
                        width: 120
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('productcode'),
                        labelAlign: 'top',
                        reference: 'productcode',
                        bind: '{theIngestSubProduct.productcode}',
                        allowBlank: false,
                        cls:'greenbold',
                        width: 120
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('version'),
                        labelAlign: 'top',
                        reference: 'version',
                        bind: '{theIngestSubProduct.version}',
                        allowBlank: false,
                        cls:'greenbold',
                        width: 100
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('provider'),
                        labelAlign: 'top',
                        reference: 'provider',
                        bind: '{theIngestSubProduct.provider}',
                        cls:'greenbold',
                        width: 250
                    }]
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('subproductcode'),    // 'Sub product code',
                    reference: 'subproductcode',
                    bind: '{theIngestSubProduct.subproductcode}',
                    allowBlank: false,
                    width: 150 + labelwidth
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('product_name'),    // 'Product name',
                    reference: 'descriptive_name',
                    width: 610,
                    allowBlank: false,
                    bind: '{theIngestSubProduct.descriptive_name}'
                }, {
                    // xtype: 'textareafield',
                    xtype: 'htmleditor',
                    fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                    reference: 'description',
                    // bind: '{theIngestSubProduct.description}',
                    labelAlign: 'top',
                    width: 610,
                    allowBlank: true,
                    grow: true,
                    growMax: 130,
                    height: 130,
                    minHeight: 130,
                    scrollable: true,

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
                }, {
                    xtype: 'container',
                    defaults: {
                        disabled: me.params.view ? true : false,
                        labelWidth: labelwidth,
                        padding: '20 10 10 0'
                    },
                    layout: {
                        type: 'hbox'
                        , align: 'stretch'
                    },
                    items: [{
                        xtype: 'container',
                        defaults: {
                            disabled: me.params.view ? true : false,
                            labelWidth: 100,
                            padding: '0 10 5 10'
                        },
                        flex: 1,
                        layout: {
                            type: 'vbox'
                        },
                        items: [{
                            id: 'ingest_subproduct_frequency',
                            name: 'ingest_subproduct_frequency',
                            reference: 'ingest_subproduct_frequency',
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('frequency'),    // 'Frequency',
                            width: 145 + 100,
                            allowBlank: false,
                            bind: '{theIngestSubProduct.frequency_id}',
                            store: {
                                type: 'frequencies'
                            },
                            valueField: 'frequency_id',
                            displayField: 'frequency_id',
                            typeAhead: false,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('selectafrequency')    // 'Select a frequency...'
                        }, {
                            id: 'ingest_subproduct_date_format',
                            name: 'ingest_subproduct_date_format',
                            reference: 'ingest_subproduct_date_format',
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('date_format'),    // 'Date format',
                            width: 175 + labelwidth,
                            allowBlank: false,
                            bind: '{theIngestSubProduct.date_format}',
                            store: {
                                type: 'dateformats'
                            },
                            valueField: 'date_format',
                            displayField: 'date_format',
                            typeAhead: false,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('selectadateformat')    // 'Select a date format...'
                        }, {
                            id: 'ingest_subproduct_data_type',
                            name: 'ingest_subproduct_data_type',
                            reference: 'ingest_subproduct_data_type',
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('data_type'),    // 'Data type',
                            width: 145 + 100,
                            allowBlank: false,
                            bind: '{theIngestSubProduct.data_type_id}',
                            store: {
                                type: 'datatypes'
                            },
                            valueField: 'data_type_id',
                            displayField: 'data_type_id',
                            typeAhead: false,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('selectadatatype')    // 'Select a data type...'
                        }, {
                            xtype: 'numberfield',
                            fieldLabel: esapp.Utils.getTranslation('scale_offset'),    // 'Scale offset',
                            reference: 'ingest_subproduct_scale_offset',
                            width: 100 + 100,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theIngestSubProduct.scale_offset}'
                        }, {
                            xtype: 'numberfield',
                            fieldLabel: esapp.Utils.getTranslation('scale_factor'),    // 'Scale factor',
                            reference: 'ingest_subproduct_scale_factor',
                            width: 100 + 100,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theIngestSubProduct.scale_factor}'
                        }, {
                            xtype: 'numberfield',
                            fieldLabel: esapp.Utils.getTranslation('nodata'),    // 'No data value',
                            reference: 'ingest_subproduct_nodata',
                            width: 100 + 100,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theIngestSubProduct.nodata}'
                        }]
                    }, {
                        xtype: 'container',
                        defaults: {
                            disabled: me.params.view ? true : false,
                            labelWidth: 130,
                            padding: '0 10 5 10'
                        },
                        flex: 1,
                        layout: {
                            type: 'vbox'
                        },
                        items: [{
                            xtype: 'numberfield',
                            fieldLabel: esapp.Utils.getTranslation('mask_min'),    // 'Mask min',
                            reference: 'ingest_subproduct_mask_min',
                            width: 100 + 130,
                            allowBlank: true,
                            maxValue: 99999999,
                            minValue: -99999999,
                            allowDecimals: true,
                            hideTrigger: false,
                            bind: '{theIngestSubProduct.mask_min}'
                        }, {
                            xtype: 'numberfield',
                            fieldLabel: esapp.Utils.getTranslation('mask_max'),    // 'Mask max',
                            reference: 'ingest_subproduct_mask_max',
                            width: 100 + 130,
                            allowBlank: true,
                            maxValue: 99999999,
                            minValue: -99999999,
                            allowDecimals: true,
                            hideTrigger: false,
                            bind: '{theIngestSubProduct.mask_max}'
                        }, {
                            xtype: 'textfield',
                            fieldLabel: esapp.Utils.getTranslation('unit'),    // 'Unit',
                            reference: 'ingest_subproduct_unit',
                            width: 100 + 130,
                            allowBlank: true,
                            bind: '{theIngestSubProduct.unit}'
                        }, {
                            xtype: 'checkboxfield',
                            fieldLabel: esapp.Utils.getTranslation('show_in_analysistool'),    // 'Show in Analysis tool',
                            reference: 'masked',
                            width: 100 + 130,
                            allowBlank: true
                            // ,bind: '{theIngestSubProduct.masked}'
                        }, {
                            xtype: 'checkboxfield',
                            fieldLabel: esapp.Utils.getTranslation('enable_timeseries'),    // 'Enable time series',
                            reference: 'enable_in_timeseries',
                            width: 100 + 130,
                            allowBlank: true,
                            bind: '{theIngestSubProduct.enable_in_timeseries}'
                        },{
                            reference: 'defined_by_field',
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('definedby'),
                            labelWidth: 100,
                            width: 150 + 100,
                            // margin: '0 0 5 80',
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
                    }]
                },{
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('save'),    // 'Save',
                    iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                    style: {color: 'lightblue'},
                    scale: 'medium',
                    width: 135,
                    disabled: false,
                    handler: 'saveIngestSubProductInfo'
                }]
            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('datasourceingestparameters')+'</div>',   // '<b>Datasource Ingest parameters</b>',
                id: 'ingestsubproductdatasourcesfieldset',
                hidden: true,
                collapsible: false,
                padding: '10 10 10 10',
                margin: '10 10 10 10',
                width: 660,

                items:[{
                    xtype: 'grid',
                    reference: 'ingestsubproductDataSourcesGrid',
                    //store: 'subdatasourcedescriptions',
                    bind:{
                        store:'{subdatasourcedescriptions}'
                    },
                    // session: true,
                    // stateful: false,

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
                        ,listeners: {
                            selectionchange: function (sm, selections) {
                                // if (selections.length) {
                                //     me.lookupReference('unassignDataSource-btn').enable();
                                //     // unassignDataSourceAction.enable();
                                // } else {
                                //     me.lookupReference('unassignDataSource-btn').disable();
                                //     // unassignDataSourceAction.disable();
                                // }
                            }
                        }
                    },

                    layout: 'fit',
                    autoHeight: true,
                    minHeight: 105,
                    collapsible: false,
                    enableColumnMove: false,
                    enableColumnResize: false,
                    multiColumnSort: false,
                    columnLines: false,
                    rowLines: true,
                    frame: false,
                    border: true,

                    // defaults: {
                    //     disabled: me.params.view ? true : false
                    // },

                    columns: [{
                        header: esapp.Utils.getTranslation('type'),    // 'Type',
                        dataIndex: 'pads_type',
                        // bind: '{subdatasourcedescriptions.pads_type}',
                        width: 120,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    },{
                        header: esapp.Utils.getTranslation('id'),    // 'ID',
                        dataIndex: 'pads_data_source_id',
                        // bind: '{subdatasourcedescriptions.pads_data_source_id}',
                        width: 250,
                        sortable: false,
                        hideable: false,
                        variableRowHeight: true,
                        menuDisabled: true
                    // },{
                    //     header: esapp.Utils.getTranslation('description'),    // 'ID',
                    //     dataIndex: 'datasource_descriptivename',
                    //     // bind: '{subdatasourcedescriptions.datasource_descriptivename}',
                    //     width: 55,
                    //     sortable: false,
                    //     hideable: false,
                    //     variableRowHeight: true,
                    //     menuDisabled: true
                    },{
                        xtype: 'actioncolumn',
                        header: esapp.Utils.getTranslation('ingestparameters'),    // 'ID',
                        hidden: false,
                        width: 140,
                        align: 'center',
                        sortable: false,
                        menuDisabled: true,
                        items: [{
                            getClass: function (v, meta, rec) {
                                // console.info(rec.get('ingestparameters'));
                               if (rec.get('productcode') != '' ) {
                                   return 'edit';
                               }
                               else {
                                   // return 'x-hide-display';
                                   return 'add24';
                               }
                            },
                            getTip: function (v, meta, rec) {
                               if (rec.get('productcode') != '' ) {
                                   return esapp.Utils.getTranslation('editingestparameters')    // 'Edit Ingest parameters',
                               }
                               else {
                                   return esapp.Utils.getTranslation('addingestparameters')    // 'Add Ingest parameters',
                               }
                            },
                            handler: 'addEditIngestParameters'
                        }]
                    // },{
                    //    xtype: 'actioncolumn',
                    //    // header: 'Delete',
                    //    hidden: false,
                    //    width: 70,
                    //    align: 'center',
                    //    sortable: false,
                    //    menuDisabled: true,
                    //    items: [{
                    //        getClass: function(v, meta, rec) {
                    //            // return 'delete';
                    //            if (rec.get('productcode') != '' && (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                    //                return 'delete';
                    //            }
                    //            else {
                    //                return 'x-hide-display';
                    //            }
                    //        },
                    //        getTip: function(v, meta, rec) {
                    //            if (rec.get('productcode') != '' && (esapp.Utils.objectExists(user) && user.userlevel == 1)){
                    //                var tipText = esapp.Utils.getTranslation('deleteingestparameters') + ': <BR>' +
                    //                    '<b>' + rec.get('pads_data_source_id') + '</b>';
                    //                return tipText;
                    //            }
                    //        },
                    //        handler: 'deleteIngestParameters'
                    //    }]
                    }]
                }]
            }]
        }];

                // },{
                //     // xtype: 'container',
                //     // items: [{
                //     xtype: 'fieldset',
                //     title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('assignedmapset')+'</div>',   // '<b>Assigned mapset</b>',
                //     reference: 'ingestion-mapset-dataview',
                //     collapsible:false,
                //     border: true,
                //     padding:'10 10 10 10',
                //     margin: '10 10 10 5',
                //     defaults: {
                //         labelWidth: labelwidth
                //     },
                //     autoWidth: true,
                //     //height: 250,
                //     layout: 'fit',
                //
                //     items:[ Ext.create('Ext.view.View', {
                //         bind: '{ingestionmapset}',
                //         //id: 'mapsets',
                //         //boxLabel: '{descriptive_name}',
                //         tpl: Ext.create('Ext.XTemplate',
                //             '<tpl for=".">',
                //             '<div class="mapset" id="{mapsetcode:stripTags}">',
                //             '<img src="{footprint_image}" title="{descriptive_name:htmlEncode}">',
                //             '<span><strong>{descriptive_name:htmlEncode}</strong></span>',
                //             '</div>',
                //             '</tpl>',
                //             '<div class="x-clear"></div>'
                //         ),
                //         multiSelect: false,
                //         height: 160,
                //         width: 140,
                //         trackOver: true,
                //         cls: 'mapsets',
                //         overItemCls: 'mapset-hover',
                //         itemSelector: 'div.mapset',
                //         emptyText: esapp.Utils.getTranslation('nomapsetassignedtoingestion'),    // 'No Mapset assigned to Ingestion. Please assign a Mapset.',
                //         autoScroll: true,
                //         listeners: {
                //             itemclick: 'mapsetItemClick'
                //         }
                //     }),{
                //         xtype: 'button',
                //         text: esapp.Utils.getTranslation('assignmapset'),    // 'Assign a mapset',
                //         //scope:me,
                //         iconCls: 'fa fa-plus-circle fa-2x',
                //         style: { color: 'lightblue' },
                //         scale: 'medium',
                //         disabled: false,
                //         handler: 'AssignMapset'
                //     }]

        me.callParent();

        me.controller.setup();

    }

});
