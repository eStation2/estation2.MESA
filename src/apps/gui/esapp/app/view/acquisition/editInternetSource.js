
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
    xtype: 'editinternetsource',

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
    resizable: false,
    autoScroll:true,
    maximizable: false,

    //width: 975,
    height: Ext.getBody().getViewSize().height < 840 ? Ext.getBody().getViewSize().height-50 : 840,  // 725,
    maxHeight: 840,

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
        internetsourcerecord: null,
        data_source_id: null,
        orig_internet_id: ''
    },

    initComponent: function () {
        var me = this;

        // me.title = esapp.Utils.getTranslation('editinternetdatasource');

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editinternetdatasource') + '</span>');
        }
        else if (me.params.view){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('viewinternetdatasource') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newinternetdatasource') + '</span>');
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
            text: 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            hidden: me.params.view ? true : false,
            handler: 'onSaveClick'
        // }, {
        //     text: 'Cancel',
        //     scale: 'medium',
        //     handler: 'onCancelClick'
        }];

        var internettype = new Ext.data.Store({
            model   : 'esapp.model.InternetType',
            data: [
                { internet_type_id:'ftp', internet_type_name:'FTP', internet_type_descr:'' },
                { internet_type_id:'ftp_tmpl', internet_type_name:'FTP TEMPLATE', internet_type_descr:'' },
                { internet_type_id:'http_tmpl', internet_type_name:'HTTP TEMPLATE', internet_type_descr:'' },
                { internet_type_id:'http_multi_tmpl', internet_type_name:'HTTP MULTIPLE TEMPLATE', internet_type_descr:'' },
                { internet_type_id:'http_tmpl_vito', internet_type_name:'HTTP TEMPLATE VITO', internet_type_descr:'' },
                { internet_type_id:'http_tmpl_theia', internet_type_name:'HTTP TEMPLATE THEIA', internet_type_descr:'' },
                { internet_type_id:'http_coda_eum', internet_type_name:'COPERNICUS ONLINE DATA ACCESS', internet_type_descr:'' },
                { internet_type_id:'motu_client', internet_type_name:'MOTU CLIENT API', internet_type_descr:'' },
                { internet_type_id:'sentinel_sat', internet_type_name:'SENTINEL SAT API', internet_type_descr:'' },
                { internet_type_id:'jeodpp', internet_type_name:'JEODPP API', internet_type_descr:'' },
                { internet_type_id:'local', internet_type_name:'LOCAL', internet_type_descr:'' },
                { internet_type_id:'offline', internet_type_name:'OFFLINE ACCESS', internet_type_descr:'' }
            ]
        });

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
                // console.info(me);
                // console.info(me.params.create);
                if (me.params.create){
                    me.lookupReference('internet_id').setValue('');
                }
            },
            beforeclose: function(){
                // console.info('beforeclose');
                // console.info(Ext.data.StoreManager.lookup('InternetSourceStore').getUpdatedRecords());
                if (Ext.data.StoreManager.lookup('InternetSourceStore').getUpdatedRecords() !== []){
                    Ext.data.StoreManager.lookup('InternetSourceStore').rejectChanges();
                }
                Ext.data.StoreManager.lookup('InternetSourceStore').load();
            }
        };

        me.items = [{
            xtype: 'form',
            reference: 'internetsourceform',
            border: false,
            // use the Model's validations for displaying form errors
            // modelValidation: true,
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
                    width: 500,
                    margin: '10 5 10 10',
                    padding: '10 10 10 10',
                    defaults: {
                        width: 475,
                        labelWidth: 120,
                        labelAlign: 'left',
                        disabled: me.params.view ? true : false
                    },
                    items: [{
                        xtype: 'textfield',      // (me.params.create || me.params.edit) ? 'textfield' : 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('id'),    // 'ID',
                        labelWidth: 60,
                        reference: 'internet_id',
                        msgTarget: 'side',
                        bind: '{theInternetSource.internet_id}',
                        allowBlank: false
                    },{
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('name'),    // 'Name',
                        labelWidth: 60,
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
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('type'),    // 'Type',
                        labelWidth: 60,
                        width: 300,
                        reference: 'type',
                        msgTarget: 'side',
                        store: internettype,
                        // store: {
                        //     type: 'internettype'
                        // },
                        valueField: 'internet_type_id',
                        displayField: 'internet_type_name',
                        bind: '{theInternetSource.type}',
                        allowBlank: false,
                        typeAhead: false,
                        queryMode: 'local',
                        emptyText: esapp.Utils.getTranslation('selectatype')    // 'Select a type...'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('url'),    // 'URL',
                        reference: 'url',
                        labelAlign: 'top',
                        msgTarget: 'side',
                        bind: '{theInternetSource.url}',
                        height: 30,
                        grow: true
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('user_name'),    // 'User name',
                        labelWidth: 80,
                        reference: 'user_name',
                        msgTarget: 'side',
                        bind: '{theInternetSource.user_name}'
                    }, {
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('password'),    // 'Password',
                        labelWidth: 80,
                        reference: 'password',
                        msgTarget: 'side',
                        bind: '{theInternetSource.password}'
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('https_params'),    // 'https parameters',
                        reference: 'https_params',
                        labelAlign: 'top',
                        msgTarget: 'side',
                        bind: '{theInternetSource.https_params}',
                        height: 30,
                        grow: true
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('include_files_expression'),    // 'Include files expression',
                        labelAlign: 'top',
                        reference: 'include_files_expression',
                        msgTarget: 'side',
                        bind: '{theInternetSource.include_files_expression}',
                        height: 30,
                        grow: true
                    }, {
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('files_filter_expression'),    // 'Files filter expression',
                        labelAlign: 'top',
                        reference: 'files_filter_expression',
                        msgTarget: 'side',
                        bind: '{theInternetSource.files_filter_expression}',
                        height: 30,
                        grow: true
                    //}, {
                    //    xtype: 'textfield',
                    //    fieldLabel: esapp.Utils.getTranslation('status'),    // 'Status',
                    //    reference: 'status',
                    //    msgTarget: 'side',
                    //    bind: '{theInternetSource.status}'
                    //}, {
                    //    xtype: 'textfield',
                    //    fieldLabel: esapp.Utils.getTranslation('defined_by'),    // 'Defined by',
                    //    reference: 'defined_by',
                    //    msgTarget: 'side',
                    //    bind: '{theInternetSource.defined_by}'
                    // },
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('pull_frequency'),    // 'Pull frequency',
                        reference: 'pull_frequency',
                        msgTarget: 'side',
                        maxValue: 99999999,
                        minValue: 0,
                        allowDecimals: true,
                        hideTrigger: false,
                        width: 230,
                        bind: '{theInternetSource.pull_frequency}'
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('frequency'),    // 'Frequency',
                        reference: 'frequency_id',
                        allowBlank: false,
                        store: {
                            type: 'frequencies'
                        },
                        width: 475,
                        bind: '{theInternetSource.frequency_id}',
                        valueField: 'frequency_id',
                        displayField: 'description',
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
                        // allowOnlyWhitespace: false,
                        allowBlank: true,
                        maxValue: 99999999,
                        // minValue: -99999999,
                        allowDecimals: true,
                        hideTrigger: false,
                        width: 230,
                        bind: '{theInternetSource.start_date}'
                    }, {
                        xtype: 'numberfield',
                        fieldLabel: esapp.Utils.getTranslation('end_date'),    // 'End date',
                        reference: 'end_date',
                        msgTarget: 'side',
                        emptyText: '',
                        // allowOnlyWhitespace: false,
                        allowBlank: true,
                        maxValue: 99999999,
                        // minValue: -99999999,
                        allowDecimals: true,
                        hideTrigger: false,
                        width: 230,
                        bind: '{theInternetSource.end_date}'
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
                        bind: '{theInternetSource.format_type}',
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
                        width: 350,
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
                        xtype: 'textareafield',
                        fieldLabel: esapp.Utils.getTranslation('product_identifier'),    // 'Product identifier',
                        labelAlign: 'top',
                        reference: 'product_identifier',
                        msgTarget: 'side',
                        bind: '{theInternetSource.product_identifier}',
                        height: 30,
                        width: 350,
                        grow: true
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('area_type'),    // 'Area type',
                        reference: 'area_type',
                        bind: '{theInternetSource.area_type}',
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                        reference: 'preproc_type',
                        bind: '{theInternetSource.preproc_type}',
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
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                        reference: 'native_mapset',
                        bind: '{theInternetSource.native_mapset}',
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
