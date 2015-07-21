
Ext.define("esapp.view.acquisition.product.editInternetSource",{
    "extend": "Ext.window.Window",

    xtype: 'editinternetsource',

    requires: [
        'Ext.layout.container.Center'
    ],

    bind: {
        title: '{title}'
    },
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    viewConfig:{forceFit:true},
    layout:'hbox',
    modal: true,
    width: 1100,
    //height: 600,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    frame: true,
    border: true,
    bodyStyle: 'padding:5px 5px 0',
    autoScroll: false,

    //session:true,

    items: [{
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
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'fieldset',
                title: '<b>Internet data source info</b>',
                collapseable: false,
                width: 600,
                margin: '10 5 10 10',
                padding: '10 10 10 10',
                defaults: {
                    width: 575,
                    labelWidth: 120,
                    labelAlign: 'left'
                },
                items: [{
                    xtype: 'textfield',
                    fieldLabel: 'ID',
                    reference: 'internet_id',
                    msgTarget: 'side',
                    bind: '{theInternetSource.internet_id}',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Defined by',
                    reference: 'defined_by',
                    msgTarget: 'side',
                    bind: '{theInternetSource.defined_by}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Name',
                    reference: 'descriptive_name',
                    msgTarget: 'side',
                    bind: '{theInternetSource.descriptive_name}'
                }, {
                    xtype: 'textareafield',
                    fieldLabel: 'Description',
                    labelAlign: 'top',
                    reference: 'description',
                    msgTarget: 'side',
                    bind: '{theInternetSource.description}',
                    grow: true
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Modified by',
                    reference: 'modified_by',
                    msgTarget: 'side',
                    bind: '{theInternetSource.modified_by}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'URL',
                    reference: 'url',
                    msgTarget: 'side',
                    bind: '{theInternetSource.url}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'User name',
                    reference: 'user_name',
                    msgTarget: 'side',
                    bind: '{theInternetSource.user_name}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Password',
                    reference: 'password',
                    msgTarget: 'side',
                    bind: '{theInternetSource.password}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Type',
                    reference: 'type',
                    msgTarget: 'side',
                    bind: '{theInternetSource.type}'
                }, {
                    xtype: 'textareafield',
                    fieldLabel: 'Include files expression',
                    labelAlign: 'top',
                    reference: 'include_files_expression',
                    msgTarget: 'side',
                    bind: '{theInternetSource.include_files_expression}',
                    grow: true
                }, {
                    xtype: 'textareafield',
                    fieldLabel: 'Files filter expression',
                    labelAlign: 'top',
                    reference: 'files_filter_expression',
                    msgTarget: 'side',
                    bind: '{theInternetSource.files_filter_expression}',
                    grow: true
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Status',
                    reference: 'status',
                    msgTarget: 'side',
                    bind: '{theInternetSource.status}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Pull frequency',
                    reference: 'pull_frequency',
                    msgTarget: 'side',
                    bind: '{theInternetSource.pull_frequency}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Frequency',
                    reference: 'frequency_id',
                    msgTarget: 'side',
                    bind: '{theInternetSource.frequency_id}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Start date',
                    reference: 'start_date',
                    msgTarget: 'side',
                    bind: '{theInternetSource.start_date}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'End date',
                    reference: 'end_date',
                    msgTarget: 'side',
                    bind: '{theInternetSource.end_date}'
                }]
            },{
                xtype: 'fieldset',
                title: '<b>Data source description</b>',
                collapseable: false,
                width: 450,
                margin: '10 10 10 5',
                padding: '10 10 10 10',
                defaults: {
                    width: 420,
                    labelWidth: 120
                },
                items: [{
                    xtype: 'textfield',
                    fieldLabel: 'Format type',
                    reference: 'format_type',
                    msgTarget: 'side',
                    bind: '{theInternetSource.format_type}',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'File extension',
                    reference: 'file_extension',
                    msgTarget: 'side',
                    bind: '{theInternetSource.file_extension}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Delimiter',
                    reference: 'delimiter',
                    msgTarget: 'side',
                    bind: '{theInternetSource.delimiter}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Date type',
                    reference: 'date_type',
                    msgTarget: 'side',
                    bind: '{theInternetSource.date_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Date position',
                    reference: 'date_position',
                    msgTarget: 'side',
                    bind: '{theInternetSource.date_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product identifier',
                    reference: 'product_identifier',
                    msgTarget: 'side',
                    bind: '{theInternetSource.product_identifier}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Prod id position',
                    reference: 'prod_id_position',
                    msgTarget: 'side',
                    bind: '{theInternetSource.prod_id_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Prod id length',
                    reference: 'prod_id_length',
                    msgTarget: 'side',
                    bind: '{theInternetSource.prod_id_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area type',
                    reference: 'area_type',
                    msgTarget: 'side',
                    bind: '{theInternetSource.area_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area position',
                    reference: 'area_position',
                    msgTarget: 'side',
                    bind: '{theInternetSource.area_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area length',
                    reference: 'area_length',
                    msgTarget: 'side',
                    bind: '{theInternetSource.area_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Preproc type',
                    reference: 'preproc_type',
                    msgTarget: 'side',
                    bind: '{theInternetSource.preproc_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product release',
                    reference: 'product_release',
                    msgTarget: 'side',
                    bind: '{theInternetSource.product_release}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Release position',
                    reference: 'release_position',
                    msgTarget: 'side',
                    bind: '{theInternetSource.release_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Release length',
                    reference: 'release_length',
                    msgTarget: 'side',
                    bind: '{theInternetSource.release_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Native mapset',
                    reference: 'native_mapset',
                    msgTarget: 'side',
                    bind: '{theInternetSource.native_mapset}'
                }]
            }]
        }]
    }],

    buttons: [{
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
    }]
});
