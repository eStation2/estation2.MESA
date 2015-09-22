Ext.define('esapp.view.dashboard.DashboardController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.dashboard-dashboard',

    selectProduct: function(btn, event) {
        var selectProductWin = new esapp.view.acquisition.product.selectProduct();
        selectProductWin.down('grid').getStore().load();
        selectProductWin.show();
    },

    setupDashboard: function() {
        var me = this.getView();

        var pcs_container = Ext.getCmp('pcs_container');
        pcs_container.removeAll();

        var PC1 = {},
            PC2 = {},
            PC3 = {},
            PC1_connection = {},
            PC23_connection = {};

        var pc1Active = false,
            pc2Active = false,
            pc3Active = false,
            pc1Disabled = true,
            pc2DisabledPartial = true,
            pc3DisabledPartial = true,
            pc2DisabledAll = true,
            pc3DisabledAll = true;

        this.getStore('dashboard').load({
            callback: function(records, options, success){
                records.forEach(function(dashboard) {
                    me.PC2_service_eumetcast = dashboard.get('PC2_service_eumetcast');
                    me.PC2_service_internet = dashboard.get('PC2_service_internet');
                    me.PC2_service_ingest = dashboard.get('PC2_service_ingest');
                    me.PC2_service_processing = dashboard.get('PC2_service_processing');
                    me.PC2_service_system = dashboard.get('PC2_service_system');
                    me.PC2_internet_status = dashboard.get('PC2_internet_status');
                    me.PC2_mode = dashboard.get('PC2_mode');
                    me.PC2_postgresql_status = dashboard.get('PC2_postgresql_status');
                    me.PC2_version = dashboard.get('PC2_version');
                    me.PC2_disk_status = dashboard.get('PC2_disk_status');

                    me.PC3_service_eumetcast = dashboard.get('PC3_service_eumetcast');
                    me.PC3_service_internet = dashboard.get('PC3_service_internet');
                    me.PC3_service_ingest = dashboard.get('PC3_service_ingest');
                    me.PC3_service_processing = dashboard.get('PC3_service_processing');
                    me.PC3_service_system = dashboard.get('PC3_service_system');
                    me.PC3_internet_status = dashboard.get('PC3_internet_status');
                    me.PC3_mode = dashboard.get('PC3_mode');
                    me.PC3_postgresql_status = dashboard.get('PC3_postgresql_status');
                    me.PC3_version = dashboard.get('PC3_version');
                    me.PC3_disk_status = dashboard.get('PC3_disk_status');

                    me.activePC = dashboard.get('activePC');
                    me.PC1_connection = dashboard.get('PC1_connection');
                    me.PC23_connection = dashboard.get('PC23_connection');
                    me.type_installation = dashboard.get('type_installation');
                });

                if (me.type_installation == 'full'){
                    me.setTitle('<span class="dashboard-header-title-style">' + esapp.Utils.getTranslation('mesa_full_estation') + '</span>');  // 'MESA Full eStation',

                    var acquisitiontab = Ext.getCmp('acquisitionmaintab');
                    var processingtab = Ext.getCmp('processingmaintab');
                    var datamanagementtab = Ext.getCmp('datamanagementmaintab');
                    var analysistab = Ext.getCmp('analysistab');
                    var systemtab = Ext.getCmp('systemtab');
                    var maintabpanel = Ext.getCmp('maintabpanel');

                    var indexAcquisitionTab = 1;
                    var indexProcessingTab = 2;
                    var indexDataManagementTab = 3;
                    var indexAnalysisTab = 4; // maintabpanel.getTabBar().items.indexOf(analysistab);
                    var indexSystemTab = 5;

                    if (me.activePC == '') {
                        maintabpanel.getTabBar().items.getAt(indexAcquisitionTab).hide();
                        acquisitiontab.disable();

                        maintabpanel.getTabBar().items.getAt(indexProcessingTab).hide();
                        processingtab.disable();

                        maintabpanel.getTabBar().items.getAt(indexDataManagementTab).hide();
                        datamanagementtab.disable();

                        maintabpanel.getTabBar().items.getAt(indexAnalysisTab).hide();
                        analysistab.disable();

                        maintabpanel.getTabBar().items.getAt(indexSystemTab).show();
                        systemtab.enable();
                        maintabpanel.setActiveTab(indexSystemTab);
                    }
                    if (me.activePC == 'pc1') {
                        pc1Active = true;
                    }
                    if (me.activePC == 'pc2') {
                        pc2Active = true;
                        pc2DisabledAll = false;
                        pc2DisabledPartial = false;
                        pc3DisabledAll = true;

                        maintabpanel.getTabBar().items.getAt(indexAcquisitionTab).show();
                        acquisitiontab.enable();

                        maintabpanel.getTabBar().items.getAt(indexProcessingTab).show();
                        processingtab.enable();

                        maintabpanel.getTabBar().items.getAt(indexDataManagementTab).show();
                        datamanagementtab.enable();

                        if (me.PC2_mode == 'nominal') {
                            maintabpanel.getTabBar().items.getAt(indexAnalysisTab).hide();
                            analysistab.disable();
                        }
                        else if (me.PC2_mode == 'recovery'){
                            maintabpanel.getTabBar().items.getAt(indexAnalysisTab).show();
                            analysistab.enable();
                        }
                    }
                    if (me.activePC == 'pc3') {
                        pc3Active = true;
                        pc3DisabledAll = false;
                        pc2DisabledAll = true;

                        if (me.PC3_mode == 'nominal') {
                            maintabpanel.getTabBar().items.getAt(indexAcquisitionTab).hide();
                            acquisitiontab.disable();

                            maintabpanel.getTabBar().items.getAt(indexProcessingTab).hide();
                            processingtab.disable();

                            maintabpanel.getTabBar().items.getAt(indexDataManagementTab).hide();
                            datamanagementtab.disable();

                            maintabpanel.getTabBar().items.getAt(indexAnalysisTab).show();
                            analysistab.enable();
                        }
                        else if (me.PC3_mode == 'recovery') {
                            pc3DisabledPartial = false;

                            maintabpanel.getTabBar().items.getAt(indexAcquisitionTab).show();
                            acquisitiontab.enable();

                            maintabpanel.getTabBar().items.getAt(indexProcessingTab).show();
                            processingtab.enable();

                            maintabpanel.getTabBar().items.getAt(indexDataManagementTab).show();
                            datamanagementtab.enable();

                            maintabpanel.getTabBar().items.getAt(indexAnalysisTab).show();
                            analysistab.enable();
                        }
                    }

                    me.PC2_modeText = esapp.Utils.getTranslation(me.PC2_mode);
                    me.PC3_modeText = esapp.Utils.getTranslation(me.PC3_mode);

                    PC1 = {
                        xtype: 'dashboard-pc1',
                        setdisabled:pc1Disabled,
                        activePC:pc1Active
                    };

                    PC2 = {
                        xtype: 'dashboard-pc2',
                        name:'dashboardpc2',
                        id: 'dashboardpc2',
                        paneltitle: esapp.Utils.getTranslation('processing_pc2'),
                        setdisabledPartial:pc2DisabledPartial,
                        setdisabledAll:pc2DisabledAll,
                        activePC:pc2Active,
                        activeversion: me.PC2_version,
                        currentmode: me.PC2_modeText,
                        diskstatus: me.PC2_disk_status,
                        dbstatus: me.PC2_postgresql_status,
                        internetconnection: me.PC2_internet_status,
                        service_eumetcast : me.PC2_service_eumetcast,
                        service_internet : me.PC2_service_internet,
                        service_ingest : me.PC2_service_ingest,
                        service_processing : me.PC2_service_processing,
                        service_system : me.PC2_service_system
                    };

                    PC3 = {
                        xtype: 'dashboard-pc2',
                        name:'dashboardpc3',
                        id: 'dashboardpc3',
                        paneltitle: esapp.Utils.getTranslation('processing_pc3'),
                        setdisabledPartial:pc3DisabledPartial,
                        setdisabledAll:pc3DisabledAll,
                        activePC: pc3Active,
                        activeversion: me.PC3_version,
                        currentmode: me.PC3_modeText,
                        diskstatus: me.PC3_disk_status,
                        dbstatus: me.PC3_postgresql_status,
                        internetconnection: me.PC3_internet_status,
                        service_eumetcast : me.PC3_service_eumetcast,
                        service_internet : me.PC3_service_internet,
                        service_ingest : me.PC3_service_ingest,
                        service_processing : me.PC3_service_processing,
                        service_system : me.PC3_service_system
                    };

                    PC1_connection = {
                        xtype: 'dashboard-connection',
                        id: 'pc1_connection',
                        connected: me.PC1_connection,
                        direction: 'left'
                    };

                    PC23_connection = {
                        xtype: 'dashboard-connection',
                        id: 'pc23_connection',
                        connected: me.PC23_connection,
                        direction: 'right'
                    };

                    if (me.activePC == 'pc1') {
                        pcs_container.add(PC2);
                        pcs_container.add(PC1_connection);
                        pcs_container.add(PC1);
                        pcs_container.add(PC23_connection);
                        pcs_container.add(PC3);
                    }
                    else if (me.activePC == 'pc2') {
                        pcs_container.add(PC1);
                        pcs_container.add(PC1_connection);
                        pcs_container.add(PC2);
                        pcs_container.add(PC23_connection);
                        pcs_container.add(PC3);
                    }
                    else if (me.activePC == 'pc3') {
                        pcs_container.add(PC1);
                        pcs_container.add(PC1_connection);
                        pcs_container.add(PC3);
                        pcs_container.add(PC23_connection);
                        pcs_container.add(PC2);
                    }

                }
                else {
                    me.setTitle('<span class="dashboard-header-title-style">' + esapp.Utils.getTranslation('mesa_light_estation') + '</span>');  // 'MESA Light eStation',

                    if (me.activePC == 'pc1') pc1Active = true;
                    if (me.activePC == 'pc2') pc2Active = true;

                    PC1 = {
                        xtype: 'dashboard-pc1',
                        setdisabled:pc1Disabled,
                        activePC:pc1Active
                    };

                    PC2 = {
                        xtype: 'dashboard-pc2',
                        setdisabledPartial:pc2DisabledPartial,
                        setdisabledAll:pc2DisabledAll,
                        activePC:pc2Active
                    };

                    PC1_connection = {
                        xtype: 'dashboard-connection',
                        id: 'pc1_connection',
                        connected: me.pc1_connection,
                        direction: 'right'
                    };

                    pcs_container.add(PC1);
                    pcs_container.add(PC1_connection);
                    pcs_container.add(PC2);
                }
            }
        });

        //this.getStore('dashboard').load();
        //console.info(this.getStore('dashboard').getData());
        //this.getStore('dashboard').getData().each(function(dashboard) {
        //            me.PC2_internet_status = dashboard.get('PC2_internet_status');
        //            me.PC2_mode = dashboard.get('PC2_mode');
        //            me.PC2_postgresql_status = dashboard.get('PC2_postgresql_status');
        //            me.PC2_version = dashboard.get('PC2_version');
        //            me.PC3_internet_status = dashboard.get('PC3_internet_status');
        //            me.PC3_mode = dashboard.get('PC3_mode');
        //            me.PC3_postgresql_status = dashboard.get('PC3_postgresql_status');
        //            me.PC3_version = dashboard.get('PC3_version');
        //            me.activePC = dashboard.get('activePC');
        //            me.pc1_connection = dashboard.get('pc1_connection');
        //            me.pc3_connection = dashboard.get('pc3_connection');
        //            me.type_installation = dashboard.get('type_installation');
        //        });
        //me.PC2_internet_status = true;
        //me.PC2_mode = 'nominal';
        //me.PC2_postgresql_status = true;
        //me.PC2_version = '2.0.1';
        //me.PC3_internet_status = false;
        //me.PC3_mode = 'degradation';
        //me.PC3_postgresql_status = false;
        //me.PC3_version = '2.0.4';
        //me.activePC = 'pc2';
        //me.pc1_connection = true;
        //me.pc3_connection = true;
        //me.type_installation = 'full';

        //var pcs_container = me.getReferences();
        //var pcs_container = me.down('container[name=pcs_container]');

    }
});
