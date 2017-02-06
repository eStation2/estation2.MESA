
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

    dvb_status:null,
    tellicast_status:null,
    fts_status:null,

    initComponent: function () {
        var me = this;
        me.title = '<span class="panel-title-style">' + esapp.Utils.getTranslation('receivingstation') + '</span>';
        me.bodyPadding = 0;

        me.dvb_statusCls = '';
        if (me.dvb_status == true || me.dvb_status == 'true')
            me.dvb_statusCls = 'statusok';
        else if (me.dvb_status == false || me.dvb_status == 'false')
            me.dvb_statusCls = 'statusnotok';
        else if (me.dvb_status == null )
            me.dvb_statusCls = 'statuserror';

        me.tellicast_statusCls = '';
        if (me.tellicast_status == true || me.tellicast_status == 'true')
            me.tellicast_statusCls = 'statusok';
        else if (me.tellicast_status == false || me.tellicast_status == 'false')
            me.tellicast_statusCls = 'statusnotok';
        else if (me.tellicast_status == null )
            me.tellicast_statusCls = 'statuserror';

        me.fts_statusCls = '';
        if (me.fts_status == true || me.fts_status == 'true')
            me.fts_statusCls = 'statusok';
        else if (me.fts_status == false || me.fts_status == 'false')
            me.fts_statusCls = 'statusnotok';
        else if (me.fts_status == null )
            me.fts_statusCls = 'statuserror';


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
            defaults: {
                margin:'0 0 10 0',
                flex: 1
            },
            items: [{
                xtype: 'box',
                html: esapp.Utils.getTranslation('services')+':</br></br>',
                cls: 'panel-textheader-style',
                colspan:2
            },{
                xtype: 'box',
                html: 'DVB',
                cls: 'panel-text-style',
                width: 120
            },{
                xtype: 'box',
                height:26,
                cls: me.dvb_statusCls,
                width: 120
            },{
                xtype: 'box',
                html: 'Tellicast',
                cls: 'panel-text-style',
                width: 120
            },{
                xtype: 'box',
                height:26,
                cls: me.tellicast_statusCls,
                width: 120
            },{
                xtype: 'box',
                html: 'FTS',
                cls: 'panel-text-style',
                width: 120
            },{
                xtype: 'box',
                height:26,
                cls: me.fts_statusCls,
                width: 120
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
