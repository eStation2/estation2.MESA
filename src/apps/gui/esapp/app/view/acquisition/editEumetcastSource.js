
Ext.define("esapp.view.acquisition.editEumetcastSource",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-editeumetcastsource",
    "viewModel": {
        "type": "acquisition-editeumetcastsource"
    },
    xtype: 'editeumetcastsource',

    requires: [
        'esapp.view.acquisition.editEumetcastSourceController',
        'esapp.view.acquisition.editEumetcastSourceModel',

        'Ext.layout.container.Center'
    ],

    title: esapp.Utils.getTranslation('editeumetcastdatasource'),
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

    //width: 1100,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-35 : 715,  // 600,
    //maxHeight: 700,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'hbox',

    data_source_id: null,

    //listeners: {
    //    beforerender: "getEumetcastSource"
    //},

    session:true,
    //store: 'theEumetcastSource',

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('editeumetcastdatasource');

        me.buttons = [{
            text: esapp.Utils.getTranslation('save'),    // 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            handler: 'onSaveClick'
        }, {
            text: esapp.Utils.getTranslation('cancel'),    // 'Cancel',
            scale: 'medium',
            handler: 'onCancelClick'
        }];

        me.items = [{
            xtype: 'form',
            //bind: '{theEumetcastSource}',     // NO BIND otherwise does not work with formula on store.
            reference: 'eumetcastsourceform',
            border: false,
            // use the Model's validations for displaying form errors
            //modelValidation: true,
            fieldDefaults: {
                labelAlign: 'left',
                labelStyle: 'font-weight: bold;',
                msgTarget: 'right',
                preventMark: false
            },
            items : [{
                layout: {
                    type: 'hbox'
                    ,align: 'stretch'
                },
                items: [{
                    xtype: 'fieldset',
                    title: '<b>'+esapp.Utils.getTranslation('eumetcastdatasourceinfo')+'</b>',    // '<b>Eumetcast data source info</b>',
                    collapsible: false,
                    width: 525,
                    margin: '10 5 10 10',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 500,
                        labelWidth: 120,
                        labelAlign: 'top'
                    },
                    items: [{
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('id'),    // 'ID',
                        labelAlign: 'left',
                        labelWidth: 50,
                        reference: 'eumetcast_id',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.eumetcast_id}'
                        //dataIndex: 'eumetcast_id'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('filterexpression'),    // 'Filter expression',
                        reference: 'filter_expression_jrc',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.filter_expression_jrc}',
                        //dataIndex: 'filter_expression_jrc',
                        allowBlank: false,
                        grow: true
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('collectionname'),    // 'Collection name',
                        labelAlign: 'top',
                        reference: 'collection_name',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        bind: '{theEumetcastSource.collection_name}'
                        //dataIndex: 'collection_name'
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('theme'),    // 'Theme',
                        labelAlign: 'top',
                        reference: 'keywords_theme',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        bind: '{theEumetcastSource.keywords_theme}'
                        //dataIndex: 'keywords_theme'
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('socialbenefitarea'),    // 'Societal benefit area',
                        labelAlign: 'top',
                        reference: 'keywords_societal_benefit_area',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        bind: '{theEumetcastSource.keywords_societal_benefit_area}'
                        //dataIndex: 'keywords_societal_benefit_area'
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('tipicalfilename'),    // 'Typical file name',
                        reference: 'typical_file_name',
                        msgTarget: 'side',
                        minHeight: 80,
                        shrinkWrap: 2,
                        bind: '{theEumetcastSource.typical_file_name}'
                        //dataIndex: 'typical_file_name'
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                        reference: 'description',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        minHeight: 160,
                        grow: true,
                        bind: '{theEumetcastSource.description}'
                        //dataIndex: 'description'
                    }]
                },{
                    xtype: 'fieldset',
                    title: '<b>'+esapp.Utils.getTranslation('datasourcedescription')+'</b>',    // '<b>Data source description</b>',
                    collapsible: false,
                    width: 525,
                    margin: '10 10 10 5',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 500,
                        labelWidth: 200
                    },
                    items: [{
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('format_type'),    // 'Format type',
                        reference: 'format_type',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.format_type}',
                        //dataIndex: 'format_type',
                        allowBlank: false
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('file_extension'),    // 'File extension',
                        reference: 'file_extension',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.file_extension}'
                        //dataIndex: 'file_extension'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('delimiter'),    // 'Delimiter',
                        reference: 'delimiter',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.delimiter}'
                        //dataIndex: 'delimiter'
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('date_format'),    // 'Date format',
                        reference: 'date_format',
                        allowBlank: false,
                        store: {
                            type: 'dateformats'
                        },
                        bind: '{theEumetcastSource.date_format}',
                        valueField: 'date_format',
                        displayField: 'date_format',    // 'definition',
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectadateformat')    // 'Select a date format...'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('date_position'),    // 'Date position',
                        reference: 'date_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.date_position}'
                        //dataIndex: 'date_position'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('product_identifier'),    // 'Product identifier',
                        reference: 'product_identifier',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.product_identifier}'
                        //dataIndex: 'product_identifier'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('prod_id_position'),    // 'Product ID position',
                        reference: 'prod_id_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.prod_id_position}'
                        //dataIndex: 'prod_id_position'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('prod_id_length'),    // 'Product ID length',
                        reference: 'prod_id_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.prod_id_length}'
                        //dataIndex: 'prod_id_length'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('area_type'),    // 'Area type',
                        reference: 'area_type',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.area_type}'
                        //dataIndex: 'description'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('area_position'),    // 'Area position',
                        reference: 'area_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.area_position}'
                        //dataIndex: 'area_position'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('area_length'),    // 'Area length',
                        reference: 'area_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.area_length}'
                        //dataIndex: 'area_length'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                        reference: 'preproc_type',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.preproc_type}'
                        //dataIndex: 'preproc_type'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('product_release'),    // 'Product release',
                        reference: 'product_release',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.product_release}'
                        //dataIndex: 'product_release'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('release_position'),    // 'Release position',
                        reference: 'release_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.release_position}'
                        //dataIndex: 'release_position'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('release_length'),    // 'Release length',
                        reference: 'release_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theEumetcastSource.release_length}'
                        //dataIndex: 'release_length'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                        reference: 'native_mapset',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.native_mapset}'
                        //dataIndex: 'native_mapset'
                    }]
                }]
            }]
        }];

        me.callParent();

    }
});
