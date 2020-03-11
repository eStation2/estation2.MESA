
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

    title: esapp.Utils.getTranslation('changemode'),    // 'Change Mode',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    width:200,
    height:190,
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
            recovery = false,
            maintenance = false;

        me.title = esapp.Utils.getTranslation('changemode');    // 'Change Mode',

        if (me.params.currentmode == 'nominal') nominal = true;
        else if (me.params.currentmode == 'recovery') recovery = true;
        else if (me.params.currentmode == 'maintenance') maintenance = true;

        me.bbar = ['->',
            {
                xtype: 'button',
                text: esapp.Utils.getTranslation('save'),    // 'Save',
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
                    boxLabel: '<b>'+esapp.Utils.getTranslation('nominalmode')+'</b>',
                    id: 'nominalradio',
                    name: 'mode',
                    inputValue: 'nominal',
                    checked: nominal
                }, {
                    boxLabel: '<b>'+esapp.Utils.getTranslation('recoverymode')+'</b>',
                    id: 'recoveryradio',
                    name: 'mode',
                    inputValue: 'recovery',
                    checked: recovery
                }, {
                    boxLabel: '<b>'+esapp.Utils.getTranslation('maintenancemode')+'</b>',
                    id: 'maintenanceradio',
                    name: 'mode',
                    inputValue: 'maintenance',
                    checked: maintenance
                }],
                listeners: {
                    change: function(){
                        var nominalradio = Ext.getCmp('nominalradio'),
                            recoveryradio = Ext.getCmp('recoveryradio'),
                            maintenanceradio = Ext.getCmp('maintenanceradio'),
                            changemodebtn = Ext.getCmp('changemodebtn');

                        if (me.params.currentmode == 'nominal' && (recoveryradio.getValue() || maintenanceradio.getValue()))
                            changemodebtn.enable();
                        else if (me.params.currentmode == 'recovery' && (nominalradio.getValue() || maintenanceradio.getValue()))
                            changemodebtn.enable();
                        else if (me.params.currentmode == 'maintenance' && (nominalradio.getValue() || recoveryradio.getValue()))
                            changemodebtn.enable();
                        else changemodebtn.disable();
                    }
                }
            }]
        }];

        me.callParent();

    }
});
