
Ext.define("esapp.view.dashboard.PC1",{
    "extend": "Ext.panel.Panel",
    "controller": "dashboard-pc1",
    "viewModel": {
        "type": "dashboard-pc1"
    },
    xtype  : 'dashboard-pc1',

    requires: [
        'esapp.view.dashboard.PC1Controller',
        'esapp.view.dashboard.PC1Model',

        'Ext.layout.container.Border',
        'Ext.layout.container.HBox',
        'Ext.layout.container.Column',
        'Ext.layout.container.Table',
        // 'Ext.layout.container.Accordion',
        'Ext.Img'
    ],

    name:'dashboardpc1',
    id: 'dashboardpc1',

    title: '<span class="panel-title-style">' + esapp.Utils.getTranslation('receivingstation') + '</span>',
    disabled:false,

    layout: 'border',
    bodyBorder: true,
    bodyPadding:0,
    flex:1,

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
            }]
        //},{
        //    region: 'south',
        //    title: '&nbsp;Disk status',
        //    split:false,
        //    collapsible:true,
        //    collapsed: true,
        //    // flex:1.5,
        //    iconCls: 'x-tool-okay', // 'fa fa-check-circle-o fa-2x', // fa-check-square fa-chevron-circle-down fa-check-circle fa-check
        //    iconAlign : 'left',
        //    height: 240,
        //    minHeight: 200,
        //    maxHeight: 240,
        //    layout: 'fit',
        //    style: {
        //        color: 'white'
        //    },
        //    items: [{
        //        xtype: 'image',
        //        src: 'resources/img/RAID_Monitor.png',
        //        width: 265,
        //        height: 158
        //    }]
        }];

        me.callParent();
    }
});
