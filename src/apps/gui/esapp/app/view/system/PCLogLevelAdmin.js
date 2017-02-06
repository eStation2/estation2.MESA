
Ext.define("esapp.view.system.PCLogLevelAdmin",{
    "extend": "Ext.window.Window",
    "controller": "system-pclogleveladmin",
    "viewModel": {
        "type": "system-pclogleveladmin"
    },
    xtype: "logleveladmin",

    requires: [
        'esapp.view.system.PCLogLevelAdminController',
        'esapp.view.system.PCLogLevelAdminModel',

        'Ext.layout.container.Center'
    ],

    title: esapp.Utils.getTranslation('changeloglevel'),    // 'Change Log level',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    width:225,
    layout: 'fit',
    border:true,
    frame:true,
    bodyStyle: 'padding:5px 5px 0',
    autoScroll: true,
    defaultAlign: 'b-c',

    store: 'loglevels',

    params: {
       currentloglevel: null
    },

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('changeloglevel');    // 'Change Log level',

        me.bbar = ['->',
            {
                xtype: 'button',
                text: esapp.Utils.getTranslation('save'),    // 'Save',
                id: 'changeloglevelbtn',
                iconCls: 'fa fa-save fa-2x',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: true,
                handler: 'changeLogLevel'
            }
        ];

        me.items = [{
            xtype: 'fieldset',
            defaultType: 'radio',
            padding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%',
                hideEmptyLabel: true
            },
            fieldDefaults: {
                labelWidth: 90,
                labelAlign: 'left',
                labelSeparator: ' '
            },
            items: [{
                xtype: 'radiogroup',
                id: 'loglevelsradiogroup',
                text: esapp.Utils.getTranslation('availableloglevels'),    // "Available loglevel's",
                columns: 1,
                vertical: true,
                listeners: {
                    change: function(loglevelsradiogrp, newvalue){
                        var changeloglevelbtn = Ext.getCmp('changeloglevelbtn');
                        if (me.params.currentloglevel == newvalue.loglevel)
                            changeloglevelbtn.disable();
                        else changeloglevelbtn.enable();
                    }
                }
            }]
        }];

        me.callParent();

        me.controller.setupLogLevels();
    }
});
