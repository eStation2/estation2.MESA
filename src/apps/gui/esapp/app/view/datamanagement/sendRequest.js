
Ext.define("esapp.view.datamanagement.sendRequest",{
    "extend": "Ext.window.Window",
    "controller": "datamanagement-sendrequest",
    "viewModel": {
        "type": "datamanagement-sendrequest"
    },
    xtype: "sendrequest",

    requires: [
        'esapp.view.datamanagement.sendRequestController',
        'esapp.view.datamanagement.sendRequestModel'

        // 'Ext.layout.container.Center',
        // 'Ext.XTemplate'
    ],

    title: esapp.Utils.getTranslation('getrequestfile'),     // 'Send request',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    // constrainHeader: true,
    // constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: true,
    autoScroll: true,
    maximizable: false,
    width:600,
    height: 650,
    bodyStyle: 'padding:5px 5px 5px 5px',
    defaultAlign: 'c-c',

    border:true,
    frame:true,
    // layout: 'fit',

    params: {
       level: null,
       record: null
    },

    listeners: {
        afterrender: 'getRequest'
    },

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('getmissingfiles');     // 'Get request file',

        me.bbar = ['->', {
            text: esapp.Utils.getTranslation('cancel'),    // 'Cancel',
            scale: 'medium',
            handler: 'onCancelClick'
        },{
            text: esapp.Utils.getTranslation('saverequestfile'),    //'Save Request file',
            iconCls: 'fa fa-floppy-o fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            handler: 'onSaveClick'
        },{
            reference: 'getmissingfiles-btn',
            text: esapp.Utils.getTranslation('getmissingfiles'),
            iconCls: 'fa fa-cloud-download fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: true,
            handler: 'createRequestJob'
        }];

        var decadFrequency = new Ext.data.Store({
            fields: [
                {name: 'yearsid'},
                {name: 'years'}
            ],
            data: [
                { yearsid:'1', years:'1 ' + esapp.Utils.getTranslation('year')},
                { yearsid:'2', years:'2 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'3', years:'3 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'4', years:'4 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'5', years:'5 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'10', years:'10 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'15', years:'15 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'20', years:'20 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'25', years:'25 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'30', years:'30 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'35', years:'35 ' + esapp.Utils.getTranslation('years')}
            ]
        });

        var dailyFrequency = new Ext.data.Store({
            fields: [
                {name: 'yearsid'},
                {name: 'years'}
            ],
            data: [
                { yearsid:'1', years:'1 ' + esapp.Utils.getTranslation('year')},
                { yearsid:'2', years:'2 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'3', years:'3 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'4', years:'4 ' + esapp.Utils.getTranslation('years')},
                { yearsid:'5', years:'5 ' + esapp.Utils.getTranslation('years')}
            ]
        });

        var highFrequency = new Ext.data.Store({
            fields: [
                {name: 'dayid'},
                {name: 'days'}
            ],
            data: [
                { dayid:'1', days:'1 ' + esapp.Utils.getTranslation('day')},
                { dayid:'2', days:'2 ' + esapp.Utils.getTranslation('days')},
                { dayid:'3', days:'3 ' + esapp.Utils.getTranslation('days')},
                { dayid:'4', days:'4 ' + esapp.Utils.getTranslation('days')},
                { dayid:'5', days:'5 ' + esapp.Utils.getTranslation('days')},
                { dayid:'6', days:'6 ' + esapp.Utils.getTranslation('days')}
            ]
        });


        me.items = [{
            xtype: 'fieldset',
            title: '<b>'+esapp.Utils.getTranslation('set_time_back_missing_data')+'</b>',    // '<b>Set how much time to go back to get missing data</b>',
            collapsible: false,
            width: 550,
            margin: '10 10 0 5',
            padding: '10 10 0 10',
            defaults: {
                width: 360,
                labelWidth: 250,
                layout: 'hbox'
            },
            items: [{
                xtype: 'combobox',
                fieldLabel: esapp.Utils.getTranslation('get_data_for_dekad_products'),    // 'Years back for dekad products',
                // labelAlign: 'top',
                reference: 'dekad_frequency',
                allowBlank: false,
                store: decadFrequency,
                value: '5',
                valueField: 'yearsid',
                displayField: 'years',
                typeAhead: false,
                queryMode: 'local',
                msgTarget: 'side',
                emptyText: esapp.Utils.getTranslation('selectayear')    // 'Select a year...'
            }, {
                xtype: 'combobox',
                fieldLabel: esapp.Utils.getTranslation('get_data_for_daily_products'),    // 'Years back for daily products',
                // labelAlign: 'top',
                reference: 'daily_frequency',
                allowBlank: false,
                store: dailyFrequency,
                value: '1',
                valueField: 'yearsid',
                displayField: 'years',
                typeAhead: false,
                queryMode: 'local',
                msgTarget: 'side',
                emptyText: esapp.Utils.getTranslation('selectayear')    // 'Select a year...'
            }, {
                width: 530,
                items:[{
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('get_data_for_high_frequency_products'),    // 'Days back for high frequency products',
                    labelWidth: 250,
                    reference: 'high_frequency',
                    allowBlank: false,
                    store: highFrequency,
                    width: 360,
                    value: '3',
                    valueField: 'dayid',
                    displayField: 'days',
                    typeAhead: false,
                    queryMode: 'local',
                    msgTarget: 'side',
                    emptyText: esapp.Utils.getTranslation('selectadays')    // 'Select days...'
                }, {
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('apply'),    //'Apply',
                    scale: 'medium',
                    disabled: false,
                    // width: 120,
                    margin: '0 0 5 50',
                    padding: '5 5 5 5',
                    handler: 'getRequest'
                }]
            }]
        },{
            xtype:'box',
            reference: 'requestcontent',
            layout: 'fit',
            autoScroll: true,
            hidden: false,
            margin: 10,
            html:'<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>'
        }];

        me.callParent();

    }
});
