
Ext.define("esapp.view.dashboard.PC3",{
    "extend": "Ext.panel.Panel",
    "controller": "dashboard-pc3",
    "viewModel": {
        "type": "dashboard-pc3"
    },
    xtype  : 'dashboard-pc3',

    requires: [
        'esapp.view.dashboard.PC3Controller',
        'esapp.view.dashboard.PC3Model',
        'esapp.view.widgets.ServiceMenuButton',

        'Ext.layout.container.Border',
        'Ext.Img'
    ],

    name:'dashboardpc3',
    id: 'dashboardpc3',

    title: '<span class="panel-title-style">Analysis (PC3)</span>',

    setdisabled:false,
    activePC:false,

    layout: 'border',
    bodyBorder: true,
    bodyPadding:0,
    flex:1,

    initComponent: function () {
        var me = this;

        me.bodyPadding = 0;

        if (me.activePC) {
            me.toolbarCls = 'active-panel-body-style';
            me.textCls = 'panel-text-style';
        }
        else {
            me.toolbarCls = '';
            me.textCls = 'panel-text-style-gray';
        }

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            layout: {
                type: 'vbox',
                align: 'middle'
            },
            padding: '5 5 10 5',
            cls: me.toolbarCls,
            defaults: {
                width: 160,
                textAlign: 'left',
                disabled: me.setdisabled
            },
            items: [
            {
                xtype: 'servicemenubutton',
                service: 'eumetcast',
                text: 'Eumetcast',
                //disabled: me.setdisabled,
                //listeners : {
                //    beforerender: 'checkStatusServices'
                //},
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'internet',
                text: 'Internet',
                //disabled: me.setdisabled,
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'ingest',
                text: 'Ingest',
                //disabled: me.setdisabled,
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'processing',
                text: 'Processing',
                //disabled: me.setdisabled,
                handler: 'checkStatusServices'
            }, '-',
            {
                xtype: 'servicemenubutton',
                service: 'system',
                text: 'System',
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'splitbutton',
                name: 'datasyncbtn',
                text: 'Data Synchronization',
                iconCls: 'data-sync',   // 'fa fa-exchange fa-2x',  //  fa-spin 'icon-loop', // icomoon fonts
                //style: { color: 'blue' },
                scale: 'medium',
                width: 225,
                //disabled: me.disabled,
                handler: 'checkStatusServices',
                menu: Ext.create('Ext.menu.Menu', {
                    width: 200,
                    margin: '0 0 10 0',
                    floating: true,
                    items: [
                        {   xtype: 'checkbox',
                            boxLabel: 'Disable Auto Sync',
                            name: 'enabledisableautosync',
                            checked   : true,
                            handler: 'execEnableDisableAutoSync'
                        },
                        {   text: 'Execute Now',
                            name: 'executenow',
                            glyph: 'xf04b@FontAwesome',
                            cls:'menu-glyph-color-green',
                            handler: 'execManualSync'
                        }
                    ]
                })
            },{
                xtype: 'splitbutton',
                name: 'dbsyncbtn',
                text: 'DB Synchronization',
                iconCls: 'db-sync',       // 'fa fa-database fa-2x',  //  fa-spin 'icon-loop', // icomoon fonts
                //style: { color: 'blue' },
                scale: 'medium',
                width: 225,
                //disabled: me.disabled,
                handler: 'checkStatusServices',
                menu: Ext.create('Ext.menu.Menu', {
                    width: 200,
                    margin: '0 0 10 0',
                    floating: true,
                    items: [
                        {   xtype: 'checkbox',
                            boxLabel: 'Disable Auto Sync',
                            name: 'enabledisableautodbsync',
                            checked   : true,
//                            glyph: 'xf04b@FontAwesome',
//                            cls:'menu-glyph-color-green',
                            handler: 'execEnableDisableAutoDBSync'
                        },
                        {   text: 'Execute Now',
                            name: 'executenow',
                            glyph: 'xf04b@FontAwesome',
                            cls:'menu-glyph-color-green',
                            handler: 'execManualDBSync'
                        }
                    ]
                })
            }]
        });

        me.items = [{
            xtype: 'panel',
            region: 'center',
            layout: {
                type: 'table',
                columns: 2,
                tableAttrs: {
                    style: {
                        width: '100%',
                        padding:0
                    }
                }
            },
            bodyPadding:10,
            items: [{
                xtype: 'container',
                html: 'Active version',
                cls: me.textCls
            },{
                xtype: 'container',
                html: '<b></b>'
                //html: '<b>2.0.1</b>'
            },{
                xtype: 'container',
                html: 'Mode:',
                cls: me.textCls,
                width: 140
            },{
                xtype: 'container',
                html: ''
                //html: '<b>Nominal mode</b>'
            },{
                xtype: 'container',
                html: 'PostgreSQL Status:',
                cls: me.textCls,
                width: 140
            },{
                xtype: 'image'
                //,src: 'resources/img/icons/check-square-o.png'
            },{
                xtype: 'container',
                html: 'Internet connection:',
                cls: me.textCls,
                width: 140
            },{
                xtype: 'image'
                //,src: 'resources/img/icons/check-square-o.png'
            }]
        },{
            region: 'south',
            title: '&nbsp;Disk status',
            split:false,
            collapsible:true,
            collapsed: true,
            // flex:1,
            iconCls: 'x-tool-unknown',  // 'x-tool-notokay', // 'x-tool-okay', //
            iconAlign : 'left',
            height: 240,
            minHeight: 200,
            maxHeight: 240,
            layout: 'fit',
            style: {
                color: 'white'
            },
            items: [{
                xtype: 'image',
                src: 'resources/img/RAID_Monitor.png',
                width: 265,
                height: 158
            }]

        }];

        if (me.activePC) {
            me.items[0].bodyCls = 'active-panel-body-style';
            //me.bodyCls = 'active-panel-body-style';
            me.controller.checkStatusServices();
        }
        else {
            me.items[0].bodyCls = '';
            //me.bodyCls = '';
        }

        me.callParent();
    }
});
