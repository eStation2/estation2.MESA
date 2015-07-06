
Ext.define("esapp.view.system.PCModeAdmin",{
    "extend": "Ext.window.Window",
    "controller": "system-pcmodeadmin",
    "viewModel": {
        "type": "system-pcmodeadmin"
    },
    xtype: "pcmodeadmin",

    requires: [
        'esapp.view.system.PCModeAdminController',
        'esapp.view.system.PCModeAdminModel',

        'Ext.layout.container.Center'
    ],

    title: 'Change Mode',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    width:170,
    height:160,
    border:true,
    frame:true,
    bodyStyle: 'padding:5px 5px 0',
    autoScroll: true,

    params: {
       currentmode: null
    },

    initComponent: function () {
        var me = this,
            nominal = false,
            recovery = false;

        if (me.params.currentmode == 'Nominal') nominal = true;
        else recovery = true;

        me.bbar = ['->',
            {
                xtype: 'button',
                text: 'Save',
                id: 'changemodebtn',
                iconCls: 'fa fa-save fa-2x',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: true,
                handler: 'changeMode'
            }
        ];

        me.items = [{
            xtype: 'fieldset',
            defaultType: 'radio',
            padding: 5,
            //margin: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%',
                hideEmptyLabel: true
            },
            items: [{
                xtype: 'radiogroup',
                id: 'modesradiogroup',
                columns: 1,
                vertical: true,
                items: [{
                    boxLabel: '<b>Nominal mode</b>',
                    id: 'nominalradio',
                    name: 'mode',
                    inputValue: 'nominal',
                    checked: nominal
                }, {
                    boxLabel: '<b>Recovery mode</b>',
                    id: 'recoveryradio',
                    name: 'mode',
                    inputValue: 'recovery',
                    checked: recovery
                }],
                listeners: {
                    change: function(){
                        var nominalradio = Ext.getCmp('nominalradio'),
                            recoveryradio = Ext.getCmp('recoveryradio'),
                            changemodebtn = Ext.getCmp('changemodebtn');

                        if (me.params.currentmode == 'Nominal' && recoveryradio.getValue())
                            changemodebtn.enable();
                        else if (me.params.currentmode == 'Recovery' && nominalradio.getValue())
                            changemodebtn.enable();
                        else changemodebtn.disable();
                    }
                }
            }]
        }];

        me.callParent();

    }
});
