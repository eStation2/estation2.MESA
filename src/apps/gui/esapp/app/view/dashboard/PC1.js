
Ext.define("esapp.view.dashboard.PC1",{
    "extend": "Ext.panel.Panel",
    "controller": "dashboard-pc1",
    "viewModel": {
        "type": "dashboard-pc1"
    },
    xtype  : 'dashboard-pc1',

    requires: [
        'Ext.layout.container.Border',
        'Ext.layout.container.HBox',
        'Ext.layout.container.Column',
        'Ext.layout.container.Table',
        // 'Ext.layout.container.Accordion',
        'Ext.Img'
    ],

    name:'dashboardpc1',
    id: 'dashboardpc1',

    title: '<span class="panel-title-style">Acquisition (PC1)</span>',
    disabled:false,

    layout: 'border',
    bodyBorder: true,
    bodyPadding:0,
    flex:1,

//    margin: '0 0 0 0',
//    layout: {
//        type: 'vbox',
//        pack: 'start',
//        align: 'stretch'
//    },
//    bodyBorder: false,
//    bodyPadding:0,
//    defaults: {
//        border: false
//    },

    initComponent: function () {
        var me = this;

        me.bodyPadding = 0;

        me.items = [{
            xtype: 'panel',
            region: 'center',
//            flex:2,
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
                html: 'Services:</br></br>',
                cls: 'panel-textheader-style',
                colspan:2
            },{
                xtype: 'container',
                html: 'DVB:',
                cls: 'panel-text-style',
                width: '70%',
                align: 'right'
            },{
                xtype: 'container',
                html: 'status okay',
                cls: 'panel-text-style'
            },{
                xtype: 'container',
                html: 'Tellicast:',
                cls: 'panel-text-style',
                align: 'right'
            },{
                xtype: 'container',
                html: 'status okay',
                cls: 'panel-text-style'
            },{
                xtype: 'container',
                html: 'EFTS:',
                cls: 'panel-text-style',
                align: 'right'
            },{
                xtype: 'container',
                html: 'status okay',
                cls: 'panel-text-style'
            }]
        },{
            region: 'south',
            title: '&nbsp;Disk status',
            split:false,
            collapsible:true,
            collapsed: true,
            // flex:1.5,
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


//            xtype:'panel',
//            layout: 'accordion',
//            height: 200,
//            width: '100%',
//            bodyPadding:0,
//            items:[{
//                xtype: 'panel', // << fake hidden panel
//                hidden: true,
//                collapsed: false
//            },{
//                title: 'Disk status',
//                // layout: 'hbox',
//                collapsed: false,
//                bodyPadding:3,
//                iconCls: 'x-tool-okay',
//                items: [{
//                    xtype: 'image',
//                    src: 'resources/img/RAID_Monitor.png',
//                    // colspan: 2,
//                    width: 265,
//                    height: 158
//                }]
//            }]
        }];

        me.callParent();
    }
});
