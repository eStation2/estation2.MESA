
Ext.define("esapp.view.acquisition.product.editSubDatasourceDescription",{
    extend: "Ext.window.Window",
    "controller": "acquisition-product-editsubdatasourcedescription",
    "viewModel": {
        "type": "acquisition-product-editsubdatasourcedescription"
    },

    xtype: 'editsubdatasourcedescription',

    requires: [
        'esapp.view.acquisition.product.editSubDatasourceDescriptionController',
        'esapp.view.acquisition.product.editSubDatasourceDescriptionModel',

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
    height: Ext.getBody().getViewSize().height < 440 ? Ext.getBody().getViewSize().height-35 : 440,
    maxHeight: 440,

    frame: true,
    border: true,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'vbox',

    params: {
        create: false,
        edit: false,
        subdatasourcedescrrecord: null
    },

    initComponent: function () {
        var me = this;
        var labelwidth = 120;
        // var user = esapp.getUser();

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editsubdatasourcedescr') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newsubdatasourcedescr') + '</span>');
        }

        me.buttons = [
        //{     text: 'TEST',
        //     // iconCls: 'fa fa-save fa-2x',
        //     style: {color: 'lightblue'},
        //     scale: 'medium',
        //     disabled: false,
        //     formBind: false,
        //     handler: 'onTestClick'
        // },
            '->',{
            text: esapp.Utils.getTranslation('save'),    // 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            handler: 'saveSubDatasourceDescriptionInfo'
        }];


        me.listeners = {
            // beforerender: function(){
            //     Ext.data.StoreManager.lookup('SubDatasourceDescriptionStore').load();
            // },
            // afterrender: function(){
            //
            // },
            beforeclose: function(){
                if (Ext.data.StoreManager.lookup('SubDatasourceDescriptionStore').getUpdatedRecords() !== []){
                    Ext.data.StoreManager.lookup('SubDatasourceDescriptionStore').rejectChanges();
                }
                Ext.data.StoreManager.lookup('SubDatasourceDescriptionStore').load();
            }
        };

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

        var scale_types = new Ext.data.Store({
            model   : 'esapp.model.ScaleType',
            data: [
                { scale_type: 'linear', scale_type_descr: 'Linear'},
                { scale_type: 'log10', scale_type_descr: 'Log10'}
            ]
        });

        me.items = [{
            xtype: 'form',
            reference: 'subdatasourcedescriptionform',
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
                title: '<div class="grid-header-style">' + esapp.Utils.getTranslation('subdatasourcedescriptiondefinition') + '</div>',  // '<b>Ingested Sub Product definition</b>',
                reference: 'subdatasourcedescriptioninfofieldset',
                hidden: false,
                collapsible: false,
                padding: '10 10 10 20',
                margin: '10 10 10 10',
                width: 680,
                defaults: {
                    width: 650,
                    labelWidth: labelwidth,
                    msgTarget: 'side'
                },
                items: [{
                    xtype: 'container',
                    defaults: {
                        labelWidth: labelwidth,
                        padding: '0 10 5 0'
                    },
                    layout: {
                        type: 'hbox'
                        , align: 'stretch'
                    },
                    items: [{
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('datasource'),
                        labelAlign: 'top',
                        reference: 'datasource_descr_id',
                        bind: '{theSubDatasourceDescription.datasource_descr_id}',
                        allowBlank: false,
                        padding: '0 10 10 0',
                        cls:'greenbold',
                        width: 220
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('productcode'),
                        labelAlign: 'top',
                        reference: 'productcode',
                        bind: '{theSubDatasourceDescription.pads_productcode}',
                        allowBlank: false,
                        cls:'greenbold',
                        width: 120
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('version'),
                        labelAlign: 'top',
                        reference: 'version',
                        bind: '{theSubDatasourceDescription.pads_version}',
                        allowBlank: false,
                        cls:'greenbold',
                        width: 65
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: esapp.Utils.getTranslation('subproductcode'),
                        labelAlign: 'top',
                        reference: 'provider',
                        bind: '{theSubDatasourceDescription.subproductcode}',
                        cls:'greenbold',
                        width: 120
                    }]
                }, {
                    xtype: 'container',
                    // defaults: {
                    //     labelWidth: labelwidth,
                    //     padding: '10 10 10 0'
                    // },
                    layout: {
                        type: 'hbox'
                        , align: 'stretch'
                    },
                    items: [{
                        xtype: 'container',
                        defaults: {
                            labelWidth: labelwidth,
                            padding: '0 10 5 0'
                        },
                        layout: {
                            type: 'vbox'
                        },
                        // flex: 1,
                        items: [{
                            xtype: 'combobox',
                            reference: 'data_type',
                            fieldLabel: esapp.Utils.getTranslation('data_type'),    // 'Data type',
                            width: 145 + labelwidth,
                            allowBlank: false,
                            bind: '{theSubDatasourceDescription.data_type_id}',
                            store: {
                                type: 'datatypes'
                            },
                            valueField: 'data_type_id',
                            displayField: 'data_type_id',
                            typeAhead: false,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('selectadatatype')    // 'Select a data type...'
                        }, {
                            xtype: 'combobox',
                            reference: 'scale_type',
                            fieldLabel: esapp.Utils.getTranslation('scale_type'),    // 'Frequency',
                            width: 145 + labelwidth,
                            allowBlank: false,
                            bind: '{theSubDatasourceDescription.scale_type}',
                            store: scale_types,
                            valueField: 'scale_type',
                            displayField: 'scale_type_descr',
                            typeAhead: false,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('selectascaletype')    // 'Select a scale type...'
                        }, {
                            xtype: 'numberfield',
                            reference: 'scale_offset',
                            fieldLabel: esapp.Utils.getTranslation('scale_offset'),    // 'Scale offset',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theSubDatasourceDescription.scale_offset}'
                        }, {
                            xtype: 'numberfield',
                            reference: 'scale_factor',
                            fieldLabel: esapp.Utils.getTranslation('scale_factor'),    // 'Scale factor',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theSubDatasourceDescription.scale_factor}'
                        }, {
                            xtype: 'numberfield',
                            reference: 'no_data',
                            fieldLabel: esapp.Utils.getTranslation('nodata'),    // 'No data value',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            maxValue: 99999999.99999,
                            minValue: -99999999.99999,
                            allowDecimals: true,
                            decimalPrecision: 5,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theSubDatasourceDescription.no_data}'
                        }]
                    }, {
                        xtype: 'container',
                        defaults: {
                            labelWidth: 120,
                            padding: '0 10 5 20'
                        },
                        layout: {
                            type: 'vbox'
                        },
                        // flex: 2,
                        items: [{
                            xtype: 'numberfield',
                            reference: 'mask_min',
                            fieldLabel: esapp.Utils.getTranslation('mask_min'),    // 'Mask min',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            maxValue: 99999999,
                            minValue: -99999999,
                            allowDecimals: true,
                            hideTrigger: false,
                            bind: '{theSubDatasourceDescription.mask_min}'
                        }, {
                            xtype: 'numberfield',
                            reference: 'mask_max',
                            fieldLabel: esapp.Utils.getTranslation('mask_max'),    // 'Mask max',
                            width: 100 + 130,
                            allowBlank: true,
                            maxValue: 99999999,
                            minValue: -99999999,
                            allowDecimals: true,
                            hideTrigger: false,
                            bind: '{theSubDatasourceDescription.mask_max}'
                        }, {
                            xtype: 'textfield',
                            reference: 're_process',
                            fieldLabel: esapp.Utils.getTranslation('re_process'),    // 'Re-process',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            bind: '{theSubDatasourceDescription.re_process}'
                        }, {
                            xtype: 'textfield',
                            reference: 're_extract',
                            fieldLabel: esapp.Utils.getTranslation('re_extract'),    // 'Re-extract',
                            width: 100 + labelwidth,
                            allowBlank: true,
                            bind: '{theSubDatasourceDescription.re_extract}'
                        }, {
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('preproc_type'),    // 'Preproc type',
                            reference: 'preproc_type',
                            bind: '{theSubDatasourceDescription.preproc_type}',
                            store: preproctypes,
                            valueField: 'preproc_type',
                            displayField: 'preproc_type_descr',
                            // itemTpl: '<div class=""><span>{preproc_type}</span>{preproc_type_descr}</div>',
                            width: 180 + labelwidth,
                            allowBlank: true,
                            typeAhead: false,
                            queryMode: 'local',
                            msgTarget: 'side',
                            emptyText: esapp.Utils.getTranslation('selectanapreproctype')    // 'Select a pre-processing type...'
                        }, {
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('native_mapset'),    // 'Native mapset',
                            reference: 'native_mapset',
                            bind: '{theSubDatasourceDescription.native_mapset}',
                            // store: mapsets,
                            store: {
                                type: 'mapsets'
                            },
                            valueField: 'mapsetcode',
                            displayField: 'descriptive_name',
                            // itemTpl: '<div class=""><span>{mapsetcode}</span>{descriptive_name}</div>',
                            width: 230 + labelwidth,
                            allowBlank: true,
                            typeAhead: false,
                            queryMode: 'local',
                            msgTarget: 'side',
                            emptyText: esapp.Utils.getTranslation('selectanamapset')    // 'Select a mapset...'
                        }]
                    }]
                }]
            }]
        }];

        me.callParent();
    }
});
