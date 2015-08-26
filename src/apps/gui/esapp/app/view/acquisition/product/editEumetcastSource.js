
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

    constrainHeader: true,
    //constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: true,
    autoScroll:true,
    maximizable: false,

    width: 960,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-35 : 625,  // 600,
    maxHeight: 625,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'hbox',

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
                type: 'hbox'
                ,align: 'stretch'
            },
            items: [{
                xtype: 'fieldset',
                title: '<b>'+esapp.Utils.getTranslation('eumetcastdatasourceinfo')+'</b>',    // '<b>Eumetcast data source info</b>',
                collapseable: false,
                width: 475,
                margin: '10 5 10 10',
                padding: '10 10 10 10',
                defaults: {
                    width: 450,
                    labelWidth: 140,
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
                }, {
                    xtype: 'textareafield',
                    fieldLabel: esapp.Utils.getTranslation('filterexpression'),    // 'Filter expression',
                    reference: 'filter_expression_jrc',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.filter_expression_jrc}',
                    allowBlank: false,
                    grow: true
                }, {
                    xtype: 'displayfield',
                    fieldLabel: esapp.Utils.getTranslation('collectionname'),    // 'Collection name',
                    labelAlign: 'left',
                    reference: 'collection_name',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.collection_name}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: esapp.Utils.getTranslation('theme'),    // 'Theme',
                    labelAlign: 'left',
                    reference: 'keywords_theme',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.keywords_theme}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: esapp.Utils.getTranslation('socialbenefitarea'),    // 'Societal benefit area',
                    labelAlign: 'left',
                    reference: 'keywords_societal_benefit_area',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.keywords_societal_benefit_area}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: esapp.Utils.getTranslation('tipicalfilename'),    // 'Typical file name',
                    reference: 'typical_file_name',
                    msgTarget: 'side',
                    minHeight: 100,
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.typical_file_name}'
                }, {
                    xtype: 'displayfield',
                    fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                    reference: 'description',
                    msgTarget: 'side',
                    shrinkWrap: 2,
                    bind: '{theEumetcastSource.description}'
                }]
            },{
                xtype: 'fieldset',
                title: '<b>'+esapp.Utils.getTranslation('datasourcedescription')+'</b>',    // '<b>Data source description</b>',
                collapseable: false,
                width: 425,
                margin: '10 10 10 5',
                padding: '10 10 10 10',
                defaults: {
                    width: 400,
                    labelWidth: 140
                },
                items: [{
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('format_type'),    // 'Format type',
                    reference: 'format_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.format_type}',
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('file_extension'),    // 'File extension',
                    reference: 'file_extension',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.file_extension}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('delimiter'),    // 'Delimiter',
                    reference: 'delimiter',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.delimiter}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('date_type'),    // 'Date type',
                    reference: 'date_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.date_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('date_position'),    // 'Date position',
                    reference: 'date_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.date_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('product_identifier'),    // 'Product identifier',
                    reference: 'product_identifier',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.product_identifier}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('prod_id_position'),    // 'Product ID position',
                    reference: 'prod_id_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.prod_id_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('prod_id_length'),    // 'Product ID length',
                    reference: 'prod_id_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.prod_id_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('area_type'),    // 'Area type',
                    reference: 'area_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('area_position'),    // 'Area position',
                    reference: 'area_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('area_length'),    // 'Area length',
                    reference: 'area_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.area_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                    reference: 'preproc_type',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.preproc_type}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('product_release'),    // 'Product release',
                    reference: 'product_release',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.product_release}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('release_position'),    // 'Release position',
                    reference: 'release_position',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.release_position}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('release_length'),    // 'Release length',
                    reference: 'release_length',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.release_length}'
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                    reference: 'native_mapset',
                    msgTarget: 'side',
                    bind: '{theEumetcastSource.native_mapset}'
                }]
            }]
        }]
    }],

    buttons: [{
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
    }]
});
