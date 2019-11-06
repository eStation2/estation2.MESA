
Ext.define("esapp.view.acquisition.editEumetcastSource",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-editeumetcastsource",
    "viewModel": {
        "type": "acquisition-editeumetcastsource"
    },

    requires: [
        'esapp.view.acquisition.editEumetcastSourceController',
        'esapp.view.acquisition.editEumetcastSourceModel',

        'Ext.layout.container.Center'
    ],
    xtype: 'editeumetcastsource',

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
    resizable: false,
    autoScroll:true,
    maximizable: false,

    //width: 1100,
    height: Ext.getBody().getViewSize().height < 730 ? Ext.getBody().getViewSize().height-50 : 730,  // 600,
    maxHeight: 730,

    frame: true,
    border: false,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'hbox',

    session:true,

    params: {
        create: false,
        view: true,
        edit: false,
        eumetcastsourcerecord: null,
        data_source_id: null,
        orig_eumetcast_id: ''
    },

    initComponent: function () {
        var me = this;

        // me.title = esapp.Utils.getTranslation('editeumetcastdatasource');

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editeumetcastdatasource') + '</span>');
        }
        else if (me.params.view){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('vieweumetcastdatasource') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('neweumetcastdatasource') + '</span>');
        }

        me.buttons = [
        //     {
        //     text: 'TEST',
        //     // iconCls: 'fa fa-save fa-2x',
        //     style: {color: 'lightblue'},
        //     scale: 'medium',
        //     disabled: false,
        //     formBind: true,
        //     hidden: me.params.view ? true : false,
        //     handler: 'onTestClick'
        // },
            '->',{
            text: esapp.Utils.getTranslation('save'),    // 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            hidden: me.params.view ? true : false,
            handler: 'onSaveClick'
        // }, {
        //     text: esapp.Utils.getTranslation('cancel'),    // 'Cancel',
        //     scale: 'medium',
        //     handler: 'onCancelClick'
        }];

        var formattypes = new Ext.data.Store({
            model   : 'esapp.model.FormatType',
            data: [
                { format_type:'delimited', format_type_descr:'Delimited'},
                { format_type:'fixed', format_type_descr:'Fixed'}
            ]
        });
        var areatypes = new Ext.data.Store({
            model   : 'esapp.model.AreaType',
            data: [
                { area_type:'global', area_type_descr:'Global'},
                { area_type:'region', area_type_descr:'Region'},
                { area_type:'segment', area_type_descr:'Segment'},
                { area_type:'tile', area_type_descr:'Tile'}
            ]
        });

        var preproctypes = new Ext.data.Store({
            model   : 'esapp.model.PreprocType',
            data: [
                { preproc_type:'MSG_MPE', preproc_type_descr:'MSG MPE'},
                { preproc_type:'MPE_UMARF', preproc_type_descr:'MPE UMARF'},
                { preproc_type:'MODIS_HDF4_TILE', preproc_type_descr:'MODIS HDF4 TILE'},
                { preproc_type:'MERGE_TILE', preproc_type_descr:'MERGE TILE'},
                { preproc_type:'LSASAF_HDF5', preproc_type_descr:'LSASAF HDF5'},
                { preproc_type:'PML_NETCDF', preproc_type_descr:'PML NETCDF'},
                { preproc_type:'UNZIP', preproc_type_descr:'UNZIP'},
                { preproc_type:'BZIP2', preproc_type_descr:'BZIP2'},
                { preproc_type:'GEOREF_NETCDF', preproc_type_descr:'GEOREF NETCDF'},
                { preproc_type:'BZ2_HDF4', preproc_type_descr:'BZ2 HDF4'},
                { preproc_type:'HDF5_ZIP', preproc_type_descr:'HDF5 ZIP'},
                { preproc_type:'HDF5_GLS', preproc_type_descr:'HDF5 GLS'},
                { preproc_type:'HDF5_GLS_NC', preproc_type_descr:'HDF5 GLS NC'},
                { preproc_type:'NASA_FIRMS', preproc_type_descr:'NASA FIRMS'},
                { preproc_type:'GZIP', preproc_type_descr:'GZIP'},
                { preproc_type:'NETCDF', preproc_type_descr:'NETCDF'},
                { preproc_type:'JRC_WBD_GEE', preproc_type_descr:'JRC WBD GEE'},
                { preproc_type:'ECMWF_MARS', preproc_type_descr:'ECMWF MARS'},
                { preproc_type:'ENVI_2_GTIFF', preproc_type_descr:'ENVI TO GTIFF'},
                { preproc_type:'CPC_BINARY', preproc_type_descr:'CPC BINARY'},
                { preproc_type:'GSOD', preproc_type_descr:'GSOD'},
                { preproc_type:'NETCDF_S3_WRR_ZIP', preproc_type_descr:'NETCDF S3 WRR ZIPPED'},
                { preproc_type:'NETCDF_S3_WRR', preproc_type_descr:'NETCDF S3 WRR'},
                { preproc_type:'NETCDF_GPT_SUBSET', preproc_type_descr:'NETCDF GPT SUBSET'},
                { preproc_type:'NETCDF_S3_WST', preproc_type_descr:'NETCDF S3 WST'},
                { preproc_type:'NETCDF_S3_WST_ZIP', preproc_type_descr:'NETCDF S3 WST ZIPPED'},
                { preproc_type:'TARZIP', preproc_type_descr:'TARZIP'},
                { preproc_type:'NETCDF_AVISO', preproc_type_descr:'NETCDF AVISO'},
                { preproc_type:'SNAP_SUBSET_NC', preproc_type_descr:'SNAP SUBSET NC'}
            ]
        });

        me.listeners = {
            afterrender: function(){
                if (me.params.create){
                    me.lookupReference('eumetcast_id').setValue('');
                }
            },
            beforeclose: function(){
                // console.info('beforeclose');
                // console.info(Ext.data.StoreManager.lookup('EumetcastSourceStore').getUpdatedRecords());
                if (Ext.data.StoreManager.lookup('EumetcastSourceStore').getUpdatedRecords() !== []){
                    Ext.data.StoreManager.lookup('EumetcastSourceStore').rejectChanges();
                }
                Ext.data.StoreManager.lookup('EumetcastSourceStore').load();
            }
        };

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
                    width: 425,
                    margin: '10 5 10 10',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 400,
                        labelWidth: 120,
                        labelAlign: 'top',
                        disabled: me.params.view ? true : false
                    },
                    items: [{
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('id'),    // 'ID',
                        labelAlign: 'left',
                        labelWidth: 60,
                        reference: 'eumetcast_id',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.eumetcast_id}',
                        allowBlank: false
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                        reference: 'description',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        minHeight: 160,
                        grow: true,
                        bind: '{theEumetcastSource.description}'
                        //dataIndex: 'description'
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
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('tipicalfilename'),    // 'Typical file name',
                        reference: 'typical_file_name',
                        msgTarget: 'side',
                        minHeight: 80,
                        shrinkWrap: 2,
                        grow: true,
                        bind: '{theEumetcastSource.typical_file_name}'
                        //dataIndex: 'typical_file_name'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('frequency'),    // 'Frequency',
                        reference: 'frequency',
                        msgTarget: 'side',
                        shrinkWrap: 2,
                        bind: '{theEumetcastSource.frequency}'
                        //dataIndex: 'collection_name'
                    // }, {
                    //     xtype: 'displayfield',
                    //     fieldLabel: esapp.Utils.getTranslation('collectionname'),    // 'Collection name',
                    //     labelAlign: 'top',
                    //     reference: 'collection_name',
                    //     msgTarget: 'side',
                    //     shrinkWrap: 2,
                    //     bind: '{theEumetcastSource.collection_name}'
                    //     //dataIndex: 'collection_name'
                    // }, {
                    //     xtype: 'displayfield',
                    //     fieldLabel: esapp.Utils.getTranslation('theme'),    // 'Theme',
                    //     labelAlign: 'top',
                    //     reference: 'keywords_theme',
                    //     msgTarget: 'side',
                    //     shrinkWrap: 2,
                    //     bind: '{theEumetcastSource.keywords_theme}'
                    //     //dataIndex: 'keywords_theme'
                    // }, {
                    //     xtype: 'displayfield',
                    //     fieldLabel: esapp.Utils.getTranslation('socialbenefitarea'),    // 'Societal benefit area',
                    //     labelAlign: 'top',
                    //     reference: 'keywords_societal_benefit_area',
                    //     msgTarget: 'side',
                    //     shrinkWrap: 2,
                    //     bind: '{theEumetcastSource.keywords_societal_benefit_area}'
                    //     //dataIndex: 'keywords_societal_benefit_area'
                    }]
                },{
                    xtype: 'fieldset',
                    title: '<b>'+esapp.Utils.getTranslation('datasourcedescription')+'</b>',    // '<b>Data source description</b>',
                    collapsible: false,
                    width: 375,
                    margin: '10 10 10 5',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 290,
                        labelWidth: 130,
                        disabled: me.params.view ? true : false
                    },
                    items: [{
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('format_type'),    // 'Format type',
                        reference: 'format_type',
                        bind: '{theEumetcastSource.format_type}',
                        store: formattypes,
                        // store: {
                        //     type: 'formattypes'
                        // },
                        valueField: 'format_type',
                        displayField: 'format_type_descr',
                        allowBlank: true,
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectaformattype')    // 'Select a format type...'
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
                        width: 350,
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
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('product_identifier'),    // 'Product identifier',
                        reference: 'product_identifier',
                        labelAlign: 'top',
                        msgTarget: 'side',
                        bind: '{theEumetcastSource.product_identifier}',
                        height: 30,
                        width: 350,
                        grow: true
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('area_type'),    // 'Area type',
                        reference: 'area_type',
                        bind: '{theEumetcastSource.area_type}',
                        store: areatypes,
                        // store: {
                        //     type: 'areatypes'
                        // },
                        valueField: 'area_type',
                        displayField: 'area_type_descr',
                        allowBlank: true,
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectanareatype')    // 'Select an area type...'
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                        reference: 'preproc_type',
                        bind: '{theEumetcastSource.preproc_type}',
                        store: preproctypes,
                        // store: {
                        //     type: 'preproctypes'
                        // },
                        valueField: 'preproc_type',
                        displayField: 'preproc_type_descr',
                        // itemTpl: '<div class=""><span>{preproc_type}</span>{preproc_type_descr}</div>',
                        width: 350,
                        allowBlank: true,
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectanapreproctype')    // 'Select a pre-processing type...'
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                        reference: 'native_mapset',
                        bind: '{theEumetcastSource.native_mapset}',
                        // store: mapsets,
                        store: {
                            type: 'mapsets'
                        },
                        valueField: 'mapsetcode',
                        displayField: 'descriptive_name',
                        // itemTpl: '<div class=""><span>{mapsetcode}</span>{descriptive_name}</div>',
                        width: 350,
                        allowBlank: true,
                        typeAhead: false,
                        queryMode: 'local',
                        msgTarget: 'side',
                        emptyText: esapp.Utils.getTranslation('selectanamapset')    // 'Select a mapset...'
                    }]
                }]
            }]
        }];

        me.callParent();

    }
});
