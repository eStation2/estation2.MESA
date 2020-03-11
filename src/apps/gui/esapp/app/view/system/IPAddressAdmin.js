
Ext.define("esapp.view.system.IPAddressAdmin",{
    "extend": "Ext.window.Window",
    "controller": "system-ipaddressadmin",
    "viewModel": {
        "type": "system-ipaddressadmin"
    },
    xtype: "ipaddressadmin",

    requires: [
        'esapp.view.system.IPAddressAdminController',
        'esapp.view.system.IPAddressAdminModel',

        'Ext.layout.container.Center',
        'Ext.form.Panel',
        'Ext.form.FieldSet'
    ],

    title: esapp.Utils.getTranslation('ipaddressadmin'),    // 'IP address administration',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable:false,
    maximizable: false,
    width:365,
    layout: 'fit',
    border:true,
    frame:true,
    bodyStyle: 'padding:5px 5px 0',
    autoScroll: true,
    defaultAlign: 'b-c',

    //store: 'ip_settings',
    session:true,

    initComponent: function () {
        var me = this;

        var systemsettingsstore  = Ext.data.StoreManager.lookup('IPSettingsStore');
        var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
            scope: me,
            failure: function(record, operation) {
                //console.info('failure');
            },
            success: function(record, operation) {
                me.type_install = record.data.type_installation

                var ipadresses_fieldset = Ext.getCmp('ipaddress_settings');
                if (me.type_install == 'Full'){
                    //ipadresses_fieldset.add(ip_pc1);
                    //ipadresses_fieldset.add(ip_pc2);
                    //ip_pc3.items.push(modify_ips_btn);
                    //ipadresses_fieldset.add(ip_pc3);
                }
                else {
                    //ipadresses_fieldset.add(ip_pc1);
                    //ip_pc2.items.push(modify_ips_btn);
                    //ipadresses_fieldset.add(ip_pc2);
                }
            }
        });

        Ext.tip.QuickTipManager.init();

        me.items = [{
            xtype: 'form',
            id: 'ipsettingsform',
            bbar: ['->',
                {
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('save'),    // 'Save',
                    id: 'save_ipaddress_settings_btn',
                    iconCls: 'fa fa-save fa-2x',
                    style: { color: 'lightblue' },
                    scale: 'medium',
                    disabled: true,
                    formBind: true,
                    handler: 'changeIPSettings'
                }
            ],
            fieldDefaults: {
                width: 300,
                labelWidth: 150,
                labelAlign: 'left',
                labelStyle: 'font-weight: bold;',
                msgTarget: 'right',
                preventMark: false
            },
            items:[{
                xtype: 'fieldset',
                title: '', // "IP Address settings",
                id: 'ipaddress_settings',
                collapsible:false,
                padding: 10,
                defaults: {
                    //width: 300,
                    //labelWidth: 150,
                    //labelAlign: 'left',
                    //labelStyle: 'font-weight: bold;',
                    markDirty: true,
                    msgTarget: 'right'
                },
                items:[{
                    id: 'pc1_ip',
                    name: 'pc1_ip',
                    bind: '{ip_settings.ip_pc1}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('ipaddresspc1'),    // 'IP address PC1',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPAddress'
                },{
                    id: 'pc2_ip',
                    name: 'pc2_ip',
                    bind: '{ip_settings.ip_pc2}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('ipaddresspc2'),    // 'IP address PC2',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPAddress'
                },{
                    id: 'pc3_ip',
                    name: 'pc3_ip',
                    bind: '{ip_settings.ip_pc3}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('ipaddresspc3'),    // 'IP address PC3',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPAddress'
                },{
                    id: 'dns_ip',
                    name: 'dns_ip',
                    bind: '{ip_settings.dns_ip}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('dnsipaddress'),    // 'DNS IP address',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPAddress'
                },{
                    id: 'gateway_ip',
                    name: 'gateway_ip',
                    bind: '{ip_settings.gateway_ip}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('gatewayipaddress'),    // 'Gateway IP address',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPAddress'
                },{
                    id: 'lan_access_ip',
                    name: 'lan_access_ip',
                    bind: '{ip_settings.lan_access_ip}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('lanaccessipaddress'),    // 'LAN Access IP address<br>(like 192.168.0.0/24)',
                    //style:'font-weight: bold;',
                    allowBlank: false,
                    vtype:'IPNetmask'
                }]
            }]
        }];

        me.callParent();

        //me.controller.setupLogLevels();
    }
});
