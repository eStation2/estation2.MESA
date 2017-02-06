
Ext.define("esapp.view.acquisition.editInternetSource",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-editinternetsource",
    "viewModel": {
        "type": "acquisition-editinternetsource"
    },

    requires: [
        'esapp.view.acquisition.editInternetSourceController',
        'esapp.view.acquisition.editInternetSourceModel',

        'Ext.layout.container.Center'
    ],

    //bind: {
    //    title: '{title}'
    //},

    title: esapp.Utils.getTranslation('editinternetdatasource'),
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

    //width: 975,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-35 : 790,  // 725,
    maxHeight: 800,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'hbox',

    session:true,

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('editinternetdatasource');

        me.buttons = [{
            text: 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            handler: 'onSaveClick'
        }, {
            text: 'Cancel',
            scale: 'medium',
            handler: 'onCancelClick'
        }];

        me.items = [{
            xtype: 'form',
            reference: 'internetsourceform',
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
                    title: '<b>'+esapp.Utils.getTranslation('internetdatasourceinfo')+'</b>',    // '<b>Internet data source info</b>',
                    collapsible: false,
                    width: 425,
                    margin: '10 5 10 10',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 400,
                        labelWidth: 120,
                        labelAlign: 'left'
                    },
                    items: [{
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('id'),    // 'ID',
                        reference: 'internet_id',
                        msgTarget: 'side',
                        bind: '{theInternetSource.internet_id}',
                        allowBlank: false
                    //}, {
                    //    xtype: 'textfield',
                    //    fieldLabel: esapp.Utils.getTranslation('defined_by'),    // 'Defined by',
                    //    reference: 'defined_by',
                    //    msgTarget: 'side',
                    //    bind: '{theInternetSource.defined_by}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('name'),    // 'Name',
                        reference: 'descriptive_name',
                        msgTarget: 'side',
                        bind: '{theInternetSource.descriptive_name}'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                        labelAlign: 'top',
                        reference: 'description',
                        msgTarget: 'side',
                        bind: '{theInternetSource.description}',
                        grow: true
                    //}, {
                    //    xtype: 'textfield',
                    //    fieldLabel: esapp.Utils.getTranslation('modified_by'),    // 'Modified by',
                    //    reference: 'modified_by',
                    //    msgTarget: 'side',
                    //    bind: '{theInternetSource.modified_by}'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('url'),    // 'URL',
                        reference: 'url',
                        labelAlign: 'top',
                        msgTarget: 'side',
                        bind: '{theInternetSource.url}',
                        grow: true
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('user_name'),    // 'User name',
                        reference: 'user_name',
                        msgTarget: 'side',
                        bind: '{theInternetSource.user_name}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('password'),    // 'Password',
                        reference: 'password',
                        msgTarget: 'side',
                        bind: '{theInternetSource.password}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('type'),    // 'Type',
                        reference: 'type',
                        msgTarget: 'side',
                        bind: '{theInternetSource.type}'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('include_files_expression'),    // 'Include files expression',
                        labelAlign: 'top',
                        reference: 'include_files_expression',
                        msgTarget: 'side',
                        bind: '{theInternetSource.include_files_expression}',
                        grow: true
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('files_filter_expression'),    // 'Files filter expression',
                        labelAlign: 'top',
                        reference: 'files_filter_expression',
                        msgTarget: 'side',
                        bind: '{theInternetSource.files_filter_expression}',
                        grow: true
                    //}, {
                    //    xtype: 'textfield',
                    //    fieldLabel: esapp.Utils.getTranslation('status'),    // 'Status',
                    //    reference: 'status',
                    //    msgTarget: 'side',
                    //    bind: '{theInternetSource.status}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('pull_frequency'),    // 'Pull frequency',
                        reference: 'pull_frequency',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.pull_frequency}'
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('frequency'),    // 'Frequency',
                        reference: 'frequency_id',
                        allowBlank: false,
                        store: {
                            type: 'frequencies'
                        },
                        bind: '{theInternetSource.frequency_id}',
                        valueField: 'frequency_id',
                        displayField: 'frequency_id',
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectafrequency')    // 'Select a frequency...'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('start_date'),    // 'Start date',
                        reference: 'start_date',
                        msgTarget: 'side',
                        emptyText: '',
                        maxValue: 99999999,
                        minValue: -99999999,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.start_date}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('end_date'),    // 'End date',
                        reference: 'end_date',
                        msgTarget: 'side',
                        emptyText: '',
                        maxValue: 99999999,
                        minValue: -99999999,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.end_date}'
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
                        bind: '{theInternetSource.format_type}',
                        allowBlank: false
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('file_extension'),    // 'File extension',
                        reference: 'file_extension',
                        msgTarget: 'side',
                        bind: '{theInternetSource.file_extension}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('delimiter'),    // 'Delimiter',
                        reference: 'delimiter',
                        msgTarget: 'side',
                        bind: '{theInternetSource.delimiter}'
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('date_format'),    // 'Date format',
                        reference: 'date_format',
                        allowBlank: false,
                        store: {
                            type: 'dateformats'
                        },
                        bind: '{theInternetSource.date_format}',
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
                        bind: '{theInternetSource.date_position}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('product_identifier'),    // 'Product identifier',
                        reference: 'product_identifier',
                        msgTarget: 'side',
                        bind: '{theInternetSource.product_identifier}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('prod_id_position'),    // 'Prod id position',
                        reference: 'prod_id_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.prod_id_position}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('prod_id_length'),    // 'Prod id length',
                        reference: 'prod_id_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.prod_id_length}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('area_type'),    // 'Area type',
                        reference: 'area_type',
                        msgTarget: 'side',
                        bind: '{theInternetSource.area_type}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('area_position'),    // 'Area position',
                        reference: 'area_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.area_position}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('area_length'),    // 'Area length',
                        reference: 'area_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.area_length}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                        reference: 'preproc_type',
                        msgTarget: 'side',
                        bind: '{theInternetSource.preproc_type}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('product_release'),    // 'Product release',
                        reference: 'product_release',
                        msgTarget: 'side',
                        bind: '{theInternetSource.product_release}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('release_position'),    // 'Release position',
                        reference: 'release_position',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.release_position}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('release_length'),    // 'Release length',
                        reference: 'release_length',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        bind: '{theInternetSource.release_length}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                        reference: 'native_mapset',
                        msgTarget: 'side',
                        bind: '{theInternetSource.native_mapset}'
                    }]
                }]
            }]
        }];

        me.callParent();

    }
});
