
Ext.define("esapp.view.acquisition.product.editEumetcastSource",{
    extend: "Ext.window.Window",

    xtype: 'editeumetcastsource',

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
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'fieldset',
                title: '<b>Eumetcast data source info</b>',
                collapseable: false,
                width: 600,
                margin: '10 5 10 10',
                padding: '10 10 10 10',
                defaults: {
                    width: 575,
                    labelWidth: 140,
                    labelAlign: 'top'
                },
                items: [{
                    xtype: 'displayfield',
                    fieldLabel: 'ID',
                    labelAlign: 'left',
                    labelWidth: 50,
                    reference: 'eumetcast_id',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.eumetcast_id}'
                }, {
                    xtype: 'textareafield',
                    fieldLabel: 'Filter expression',
                    reference: 'filter_expression_jrc',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.filter_expression_jrc}',
                    allowBlank: false,
                    grow: true
                }, {
                    xtype: 'displayfield',
                    fieldLabel: 'Collection name',
                    labelAlign: 'left',
                    reference: 'collection_name',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.collection_name}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: 'Theme',
                    labelAlign: 'left',
                    reference: 'keywords_theme',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.keywords_theme}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: 'Societal benefit area',
                    labelAlign: 'left',
                    reference: 'keywords_societal_benefit_area',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.keywords_societal_benefit_area}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: 'Typical file name',
                    reference: 'typical_file_name',
                    msgTarget: 'side',
                    minHeight: 100,
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.typical_file_name}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: 'Description',
                    reference: 'description',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.description}'
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
                    labelWidth: 140
                },
                items: [{
                    xtype: 'textfield',
                    fieldLabel: 'Format type',
                    reference: 'format_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.format_type}',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'File extension',
                    reference: 'file_extension',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.file_extension}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Delimiter',
                    reference: 'delimiter',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.delimiter}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Date type',
                    reference: 'date_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.date_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Date position',
                    reference: 'date_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.date_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product identifier',
                    reference: 'product_identifier',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.product_identifier}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product ID position',
                    reference: 'prod_id_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.prod_id_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product ID length',
                    reference: 'prod_id_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.prod_id_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area type',
                    reference: 'area_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area position',
                    reference: 'area_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Area length',
                    reference: 'area_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Preproc type',
                    reference: 'preproc_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.preproc_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Product release',
                    reference: 'product_release',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.product_release}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Release position',
                    reference: 'release_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.release_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Release length',
                    reference: 'release_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.release_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Native mapset',
                    reference: 'native_mapset',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.native_mapset}'
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
