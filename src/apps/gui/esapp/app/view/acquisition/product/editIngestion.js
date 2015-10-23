
Ext.define("esapp.view.acquisition.product.editIngestion",{
    extend: "Ext.window.Window",
    "controller": "acquisition-product-editingestion",
    "viewModel": {
        "type": "acquisition-product-editingestion"
    },

    xtype: 'editingestion',

    requires: [
        'esapp.view.acquisition.product.editIngestionController',
        'esapp.view.acquisition.product.editIngestionModel',

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

    width: 870,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-35 : 625,
    maxHeight: 625,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'hbox',

    params: {},

    initComponent: function () {
        var me = this;
        var labelwidth = 140;

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editingestion') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newingestion') + '</span>');
        }


        me.items = [{
            xtype: 'container',
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">'+esapp.Utils.getTranslation('assignedmapset')+'</div>',   // '<b>Assigned mapset</b>',
                reference: 'ingestion-mapset-dataview',
                collapsible:false,
                border: true,
                padding:'10 10 10 10',
                margin: '10 10 10 5',
                defaults: {
                    labelWidth: labelwidth
                },
                autoWidth: true,
                //height: 250,
                layout: 'fit',

                items:[ Ext.create('Ext.view.View', {
                    bind: '{ingestionmapset}',
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
                    height: 160,
                    width: 140,
                    trackOver: true,
                    cls: 'mapsets',
                    overItemCls: 'mapset-hover',
                    itemSelector: 'div.mapset',
                    emptyText: esapp.Utils.getTranslation('nomapsetassignedtoingestion'),    // 'No Mapset assigned to Ingestion. Please assign a Mapset.',
                    autoScroll: true,
                    listeners: {
                        itemclick: 'mapsetItemClick'
                    }
                }),{
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('assignmapset'),    // 'Assign a mapset',
                    //scope:me,
                    iconCls: 'fa fa-plus-circle fa-2x',
                    style: { color: 'lightblue' },
                    scale: 'medium',
                    disabled: false,
                    handler: 'AssignMapset'
                }]
            }]
        }, {
            items: [{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">' + esapp.Utils.getTranslation('ingestiondefinition') + '</div>',  // '<b>Ingestion definition</b>',
                id: 'ingestioninfofieldset',
                hidden: false,
                collapsible: false,
                padding: '10 10 10 10',
                margin: '10 10 10 5',
                width: 630,
                defaults: {
                    width: 400,
                    labelWidth: labelwidth,
                    msgTarget: 'side'
                },
                items: [{
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('subproductcode'),    // 'Sub product code',
                    reference: 'format_type',
                    //bind: '{theInternetSource.format_type}',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('product_name'),    // 'Product name',
                    reference: 'file_extension',
                    width: 450 + labelwidth
                    //bind: '{theInternetSource.file_extension}'
                }, {
                    xtype: 'textareafield',
                    fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                    reference: 'delimiter',
                    //bind: '{theInternetSource.delimiter}'
                    labelAlign: 'top',
                    width: 600,
                    allowBlank: true,
                    grow: true
                }, {
                    id: 'ingestion_frequency',
                    name: 'ingestion_frequency',
                    reference: 'ingestion_frequency',
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('frequency'),    // 'Frequency',
                    width: 175 + labelwidth,
                    allowBlank: false,
                    //bind: '{theInternetSource.date_type}'
                    store: {
                        type: 'frequencies'
                    },
                    valueField: 'frequency_id',
                    displayField: 'frequency_id',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: esapp.Utils.getTranslation('selectafrequency')    // 'Select a frequency...'
                }, {
                    id: 'ingestion_date_format',
                    name: 'ingestion_date_format',
                    reference: 'ingestion_date_format',
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('date_format'),    // 'Date format',
                    width: 175 + labelwidth,
                    allowBlank: false,
                    //bind: '{theInternetSource.date_type}'
                    store: {
                        type: 'dateformats'
                    },
                    valueField: 'date_format',
                    displayField: 'date_format',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: esapp.Utils.getTranslation('selectadateformat')    // 'Select a date format...'
                }, {
                    id: 'ingestion_data_type',
                    name: 'ingestion_data_type',
                    reference: 'ingestion_data_type',
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('data_type'),    // 'Data type',
                    width: 175 + labelwidth,
                    allowBlank: false,
                    //bind: '{theInternetSource.data_type}'
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
                    reference: 'ingestion_scale_offset',
                    width: 175 + labelwidth,
                    maxValue: 99999999,
                    minValue: -99999999,
                    allowDecimals: true,
                    hideTrigger: false
                    //bind: '{theInternetSource.prod_id_position}'
                }, {
                    xtype: 'numberfield',
                    fieldLabel: esapp.Utils.getTranslation('scale_factor'),    // 'Scale factor',
                    reference: 'ingestion_scale_factor',
                    width: 175 + labelwidth,
                    maxValue: 99999999,
                    minValue: -99999999,
                    allowDecimals: true,
                    hideTrigger: false
                    //bind: '{theInternetSource.prod_id_length}'
                }, {
                    xtype: 'numberfield',
                    fieldLabel: esapp.Utils.getTranslation('nodata'),    // 'No data value',
                    reference: 'ingestion_nodata',
                    width: 175 + labelwidth,
                    maxValue: 99999999,
                    minValue: -99999999,
                    allowDecimals: true,
                    hideTrigger: false
                    //bind: '{theInternetSource.area_type}'
                }, {
                    xtype: 'numberfield',
                    fieldLabel: esapp.Utils.getTranslation('mask_min'),    // 'Mask min',
                    reference: 'ingestion_mask_min',
                    width: 175 + labelwidth,
                    maxValue: 99999999,
                    minValue: -99999999,
                    allowDecimals: true,
                    hideTrigger: false
                    //bind: '{theInternetSource.area_position}'
                }, {
                    xtype: 'numberfield',
                    fieldLabel: esapp.Utils.getTranslation('mask_max'),    // 'Mask max',
                    reference: 'ingestion_mask_max',
                    width: 175 + labelwidth,
                    maxValue: 99999999,
                    minValue: -99999999,
                    allowDecimals: true,
                    hideTrigger: false
                    //bind: '{theInternetSource.area_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('unit'),    // 'Unit',
                    reference: 'ingestion_unit',
                    width: 175 + labelwidth
                    //bind: '{theInternetSource.preproc_type}'
                }, {
                    xtype: 'checkboxfield',
                    fieldLabel: esapp.Utils.getTranslation('show_in_analysistool'),    // 'Show in Analysis tool',
                    reference: 'ingestion_masked'
                    //bind: '{theInternetSource.product_release}'
                }, {
                    xtype: 'checkboxfield',
                    fieldLabel: esapp.Utils.getTranslation('enable_timeseries'),    // 'Enable time series',
                    reference: 'ingestion_enable_timeseries'
                    //bind: '{theInternetSource.release_position}'
                }]
            },{
                xtype: 'button',
                text: esapp.Utils.getTranslation('save'),    // 'Save',
                //scope:me,
                iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: false,
                handler: 'saveIngestion'
            }]
        }];

        me.callParent();

        //me.controller.setup();

    }
});
