
Ext.define("esapp.view.dashboard.Dashboard",{
    "extend": "Ext.panel.Panel",

    "controller": "dashboard-dashboard",

    "viewModel": {
        "type": "dashboard-dashboard"
    },

    xtype  : 'dashboard-main',

    requires: [
        'esapp.view.dashboard.PC1',
        'esapp.view.dashboard.PC2',
        'esapp.view.dashboard.PC3',
        'esapp.view.dashboard.Connection',

        'Ext.layout.container.HBox',
        'Ext.layout.container.VBox',
        'Ext.layout.container.Center'
    ],

    name:'dashboardmain',
    id: 'dashboard-panel',

    title: '<span class="dashboard-header-title-style">MESA Full eStation</span>',
    titleAlign: 'center',
    header: {
        cls: 'dashboard-header-style'
    },

    width: 1250,
    height: 850,

    layout: {
        type: 'vbox',
        pack: 'start'
        ,align: 'stretch'
    },
    frame: false,
    border: true,
    bodyPadding: '20 30 30 30',
    // padding: 15,

    initComponent: function () {
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [
            '->', // same as { xtype: 'tbfill' }
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler:  function(btn) {
                }
            }]
        });

        me.items = [{
            xtype: 'container',
            layout: {
                type: 'hbox',
                pack: 'start',
                align: 'stretch'
            },
            width: 1200,
            height: 500,
            defaults: {
                titleAlign: 'center',
                frame: true,
                border: false,
                bodyPadding: 10
            },
            items: [{
                xtype: 'dashboard-pc1'
            }, {
                xtype: 'dashboard-connection',
                connected: true
            }, {
                xtype: 'dashboard-pc2',
                disabled:false,
                activePC:true
            }, {
                xtype: 'dashboard-connection',
                connected: true
            }, {
                xtype: 'dashboard-pc3',
                disabled:false,
                activePC:false
            }]
        },{
            xtype: 'container',
            html: '&nbsp;', // 'Here will come some lines connecting the UPS to the PCs<BR>'
            height: 30
        },{
            xtype: 'panel',
            name: 'ups-status',
            title: '<span class="dashboard-header-title-style">UPS/power status</span>',
            titleAlign: 'center',
            header: {
                cls: 'dashboard-header-style'
            },
            frameHeader:false,
            frame: false,
            border: true,
            layout: {
                type: 'hbox',
                pack: 'start',
                align: 'stretch'
            },
            items: [{
               xtype: 'container',
               flex:1.5
            },{
                xtype: 'container',
                flex:1,
                layout: {
                    type: 'table',
                    columns: 2,
                    tableAttrs: {
                        style: {
                            width: '80%'
                        }
                    }
                },
                height: 130,
                defaults: {
                    cls: 'panel-text-style'
                },
                items: [{
//                    xtype: 'container',
//                    html: 'UPS/power status',
//                    colspan:2
//                },{
                    xtype: 'container',
                    html: 'Power source:',
                    width: '70%'
                },{
                    xtype: 'container',
                    html: 'AC Utility'
                },{
                    xtype: 'container',
                    html: 'Battery Capacity:',
                    align: 'right'
                },{
                    xtype: 'container',
                    layout: 'column',
                    height: 50,
                    items: [{
                        xtype: 'container',
                        html: '<br>80%',
                        cls: 'panel-text-style',
                        align: 'center'
                    },{
                        xtype: 'image',
                        src: 'resources/img/battery/BatteryBG_14.png', // Battery cilinder icon
                        width: 64,
                        height: 32
                    }]
                },{
                    xtype: 'container',
                    html: 'Estimated Runtime:',
                    align: 'right'
                },{
                    xtype: 'container',
                    layout: 'column',
                    height: 30,
                    items: [{
                        xtype: 'container',
                        html: '240 min &nbsp&nbsp',
                        cls: 'panel-text-style'
                    },{
                        xtype: 'image',
                        src: 'resources/img/icons/clock-o.png'
                    }]
                }]
            },{
               xtype: 'container',
               flex:1.5
            }]
        }];

        me.callParent();
    }
});
