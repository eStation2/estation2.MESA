
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
        'esapp.model.Dashboard',

        //'esapp.view.dashboard.PC1',
        //'esapp.view.dashboard.PC2',
        ////'esapp.view.dashboard.PC3',
        //'esapp.view.dashboard.Connection',

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

        me.title = '<span class="dashboard-header-title-style">' + esapp.Utils.getTranslation('mesa_full_estation') + '</span>';

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
                handler: function(){
                    var reload=true;
                    me.getController().setupDashboard(reload);
                }
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

        me.items = [
            pcs_container,
            {
                xtype: 'container',
                html: '&nbsp;',
                height: 30
            }
        ];

        me.controller.setupDashboard();

        me.callParent();
    }
});
