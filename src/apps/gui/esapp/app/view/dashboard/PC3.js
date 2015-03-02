
Ext.define("esapp.view.dashboard.PC3",{
    "extend": "Ext.panel.Panel",
    "controller": "dashboard-pc3",
    "viewModel": {
        "type": "dashboard-pc3"
    },
    xtype  : 'dashboard-pc3',

    requires: [
        'esapp.view.widgets.ServiceMenuButton',

        'Ext.layout.container.Border',
        'Ext.Img'
    ],

    name:'dashboardpc3',
    id: 'dashboardpc3',

    title: '<span class="panel-title-style">Analysis (PC3)</span>',

    disabled:false,
    activePC:false,

    layout: 'border',
    bodyBorder: true,
    bodyPadding:0,
    flex:1,

    initComponent: function () {
        var me = this;

        me.bodyPadding = 0;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            layout: {
                    type: 'vbox',
                    align: 'middle'
            },
            padding: '5 5 10 5',
            // cls:'active-panel-body-style',
            defaults: {
                width: 160,
                textAlign: 'left',
                disabled: true
            },
            items: [
            {
                xtype: 'servicemenubutton',
                service: 'eumetcast',
                text: 'Eumetcast',
                //listeners : {
                //    beforerender: 'checkStatusServices'
                //},
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'internet',
                text: 'Internet',
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'ingest',
                text: 'Ingest',
                handler: 'checkStatusServices'
            }, ' ',
            {
                xtype: 'servicemenubutton',
                service: 'processing',
                text: 'Processing',
                handler: 'checkStatusServices'
            }, '-',
            {
                xtype: 'splitbutton',
                name: 'datasyncbtn',
                text: 'Data Syncronization',
                iconCls: 'fa fa-cog fa-2x',  //  fa-spin 'icon-loop', // icomoon fonts
                style: { color: 'gray' },
                scale: 'medium',
                width: 215,
                handler: 'checkStatusServices',
                menu: Ext.create('Ext.menu.Menu', {
                    width: 200,
                    margin: '0 0 10 0',
                    floating: true,
                    items: [
                        {   xtype: 'checkbox',
                            boxLabel: 'Disable Auto Sync',
                            name: 'enabledisableautosync',
//                            glyph: 'xf04b@FontAwesome',
//                            cls:'menu-glyph-color-green',
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
                text: 'DB Syncronization',
                iconCls: 'fa fa-cog fa-2x',  //  fa-spin 'icon-loop', // icomoon fonts
                style: { color: 'grey' },
                scale: 'medium',
                width: 215,
                handler: 'checkStatusServices',
                menu: Ext.create('Ext.menu.Menu', {
                    width: 200,
                    margin: '0 0 10 0',
                    floating: true,
                    items: [
                        {   xtype: 'checkbox',
                            boxLabel: 'Disable Auto Sync',
                            name: 'enabledisableautodbsync',
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
                cls: 'panel-text-style'
            },{
                xtype: 'container',
                html: '<b>2.0.1</b>'
            },{
                xtype: 'container',
                html: 'Mode:',
                cls: 'panel-text-style',
                width: 140
            },{
                xtype: 'container',
                html: '<b>Nominal mode</b>'
            },{
                xtype: 'container',
                html: 'PostgreSQL Status:',
                cls: 'panel-text-style',
                width: 140
            },{
                xtype: 'image',
                src: 'resources/img/icons/check-square-o.png'
            },{
                xtype: 'container',
                html: 'Internet connection:',
                cls: 'panel-text-style',
                width: 140
            },{
                xtype: 'image',
                src: 'resources/img/icons/check-square-o.png'
            }]
        },{
            region: 'south',
            title: '&nbsp;Disk status',
            split:false,
            collapsible:true,
            collapsed: true,
            // flex:1,
            iconCls: 'x-tool-okay', // 'fa fa-check-circle-o fa-2x', // fa-check-square fa-chevron-circle-down fa-check-circle fa-check
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
        }

        me.callParent();
    }
});
