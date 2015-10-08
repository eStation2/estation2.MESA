
Ext.define("esapp.view.dashboard.Dashboard",{
    "extend": "Ext.panel.Panel",

    "controller": "dashboard-dashboard",

    "viewModel": {
        "type": "dashboard-dashboard"
    },

    xtype  : 'dashboard-main',

    requires: [
        'esapp.view.dashboard.DashboardController',
        'esapp.view.dashboard.DashboardModel',

        'esapp.view.dashboard.PC1',
        'esapp.view.dashboard.PC2',
        //'esapp.view.dashboard.PC3',
        'esapp.view.dashboard.Connection',

        'Ext.layout.container.HBox',
        'Ext.layout.container.VBox',
        'Ext.layout.container.Center'
    ],

    name:'dashboardmain',
    id: 'dashboard-panel',

    title: '<span class="dashboard-header-title-style">' + esapp.Utils.getTranslation('mesa_full_estation') + '</span>',
    titleAlign: 'center',
    header: {
        cls: 'dashboard-header-style'
    },

    store: 'dashboard',

    width: 1250,
    height: 650,

    layout: {
        type: 'vbox',
        pack: 'start'
        ,align: 'stretch'
    },
    frame: false,
    border: true,
    bodyPadding: '20 30 30 30',

    //listeners: {
    //    beforerender: 'loadDashboardStore'
    //},

    initComponent: function () {
        var pcs_container;
        var ups_status;
        var me = this;

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [
            // {
            //    xtype: 'button',
            //    text: 'Add Product',
            //    name: 'addproduct',
            //    iconCls: 'fa fa-plus-circle fa-2x',
            //    style: { color: 'green' },
            //    hidden: false,
            //    // glyph: 'xf055@FontAwesome',
            //    scale: 'medium',
            //    handler: 'selectProduct'
            //}, {
            //    text: 'Eumetcast Sources',
            //    handler: function (btn) {
            //        var EumetcastSourceAdminWin = new esapp.view.acquisition.product.EumetcastSourceAdmin({
            //            params: {
            //                assigntoproduct: false
            //            }
            //        });
            //        EumetcastSourceAdminWin.show();
            //    },
            //}, {
            //    text: 'Internet Sources',
            //    handler: function (btn) {
            //        var InternetSourceAdminWin = new esapp.view.acquisition.product.InternetSourceAdmin({
            //            params: {
            //                assigntoproduct: false
            //            }
            //        });
            //        InternetSourceAdminWin.show();
            //    },
            //},
            '->', // same as { xtype: 'tbfill' }
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'setupDashboard'
            }]
        });

        pcs_container = new Ext.container.Container({
            id: 'pcs_container',
            name: 'pcs_container',
            reference: 'pcs_container',
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
            }
        });

//        ups_status = {
//            xtype: 'panel',
//            name: 'ups-status',
//            title: '<span class="dashboard-header-title-style">' + esapp.Utils.getTranslation('ups-powerstatus') + '</span>',
//            titleAlign: 'center',
//            header: {
//                cls: 'dashboard-header-style'
//            },
//            frameHeader:false,
//            frame: false,
//            border: true,
//            layout: {
//                type: 'hbox',
//                pack: 'start',
//                align: 'stretch'
//            },
//            items: [{
//               xtype: 'container',
//               flex:1.5
//            },{
//                xtype: 'container',
//                flex:1,
//                layout: {
//                    type: 'table',
//                    columns: 2,
//                    tableAttrs: {
//                        style: {
//                            width: '80%'
//                        }
//                    }
//                },
//                height: 120,
//                defaults: {
//                    cls: 'panel-text-style'
//                },
//                items: [{
////                    xtype: 'container',
////                    html: 'UPS/power status',
////                    colspan:2
////                },{
//                    xtype: 'container',
//                    html: 'Power source:',
//                    width: '70%'
//                },{
//                    xtype: 'container',
//                    html: 'AC Utility'
//                },{
//                    xtype: 'container',
//                    html: 'Battery Capacity:',
//                    align: 'right'
//                },{
//                    xtype: 'container',
//                    layout: 'column',
//                    height: 50,
//                    items: [{
//                        xtype: 'container',
//                        html: '<br>80%',
//                        cls: 'panel-text-style',
//                        align: 'center'
//                    },{
//                        xtype: 'image',
//                        src: 'resources/img/battery/BatteryBG_14.png', // Battery cilinder icon
//                        width: 64,
//                        height: 32
//                    }]
//                },{
//                    xtype: 'container',
//                    html: 'Estimated Runtime:',
//                    align: 'right'
//                },{
//                    xtype: 'container',
//                    layout: 'column',
//                    height: 30,
//                    items: [{
//                        xtype: 'container',
//                        html: '240 min &nbsp&nbsp',
//                        cls: 'panel-text-style'
//                    },{
//                        xtype: 'image',
//                        src: 'resources/img/icons/clock-o.png'
//                    }]
//                }]
//            },{
//               xtype: 'container',
//               flex:1.5
//            }]
//        };

        me.items = [
            pcs_container,
            {
                xtype: 'container',
                html: '&nbsp;', // 'To create some space between the PCs container and UPS status container'
                height: 30
            }
            //,ups_status
        ];

        me.controller.setupDashboard();

        me.callParent();
    }
});
