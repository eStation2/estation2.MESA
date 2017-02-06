
Ext.define("esapp.view.system.ThemaAdmin",{
    "extend": "Ext.window.Window",
    "controller": "system-themaadmin",
    "viewModel": {
        "type": "system-themaadmin"
    },
    xtype: "themaadmin",

    requires: [
        'esapp.view.system.ThemaAdminController',
        'esapp.view.system.ThemaAdminModel',

        'Ext.layout.container.Center'
    ],

    title: esapp.Utils.getTranslation('changethema'),    // 'Change Thema',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    width:550,
    layout: 'fit',
    border:true,
    frame:true,
    bodyStyle: 'padding:5px 5px 0',
    autoScroll: true,
    defaultAlign: 'b-c',

    store: 'themas',

    params: {
       currentthema: null
    },

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('changethema');    // 'Change Thema',

        me.bbar = ['->',
            {
                xtype: 'button',
                text: esapp.Utils.getTranslation('save'),    // 'Save',
                id: 'changethemabtn',
                iconCls: 'fa fa-save fa-2x',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: true,
                handler: 'changeThema'
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
                labelWidth: 85,
                labelAlign: 'left',
                labelSeparator: ' '
            },
            items: [{
                xtype: 'radiogroup',
                id: 'themasradiogroup',
                text: esapp.Utils.getTranslation('availablethemas'),    // "Available thema's",
                columns: 1,
                vertical: true,
                listeners: {
                    change: function(themasradiogrp, newvalue){
                        var changethemabtn = Ext.getCmp('changethemabtn');
                        if (me.params.currentthema == newvalue.thema)
                            changethemabtn.disable();
                        else changethemabtn.enable();
                    }
                }
            }]
        }];

        me.controller.setupThemas();

        me.callParent();

    }
});
