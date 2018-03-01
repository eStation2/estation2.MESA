/**
 * This class is the main view for the application. It is specified in app.js as the
 * "autoCreateViewport" property. That setting automatically applies the "viewport"
 * plugin to promote that instance of this class to the body element.
 */

Ext.define('esapp.view.main.Main', {
    extend: 'Ext.container.Viewport',
    //extend: 'Ext.container.Container',

    xtype: 'app-main',
    requires: [
        'esapp.view.main.MainModel',
        'esapp.view.main.MainController',

        //'esapp.view.header.Header',
        //'esapp.view.dashboard.Dashboard',
        //'esapp.view.acquisition.Acquisition',
        //'esapp.view.processing.Processing',
        //'esapp.view.datamanagement.DataManagement',
        //'esapp.view.analysis.analysisMain',
        //'esapp.view.system.systemsettings',
        //'esapp.view.help.help',
        'esapp.view.widgets.LoginView',
        'esapp.view.widgets.LoginViewECAS',
        'Ext.layout.container.Center',
        'Ext.form.field.ComboBox'
    ],
    controller: 'app-main',

    //plugins: 'viewport',

    viewModel: {
        type: 'app-main'
    },
    autoRender : true,

    layout: {
        type: 'border'
    },
    //ptype:'lazyitems',

    initComponent: function () {
        var me = this;

        // console.info('Type installation:' + esapp.globals['typeinstallation']);

        me.dashboard = {
            title: esapp.Utils.getTranslation('dashboard'),  // 'Dashboard',
            id:'dashboardtab',
            xtype:'container',
            autoScroll: true,
            layout : 'center',
            bodyCls:'dashboard-panel-body',
            items: [{
                xtype: 'dashboard-main'
            }],
            listeners: {
               activate: function (dashboardtab) {
                   var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                   headerlogos.setHidden(false);
                   //dashboardtab.up().down('container[id=acquisitionmaintab]').doLayout();
                   //dashboardtab.up().down('container[id=datamanagementmaintab]').doLayout();
                   //Ext.getCmp('dashboard-panel').getController().setupDashboard();
                   if (Ext.isObject(dashboardtab.down('panel[id=dashboardpc2]'))){
                        dashboardtab.down('panel[id=dashboardpc2]').getController().checkStatusServices();
                   }
               }
            }
        };

        me.acquisition = {
            title: esapp.Utils.getTranslation('acquisition'),  // 'Acquisition',
            id:'acquisitionmaintab',
            xtype:'container',
            closable: false,
            autoScroll: true,
            layout: 'fit',
            items: [{
                // html: '<img alt="Mockup Acquisition" width="100%" height="100%" src="../resources/img/mockup_acquisition.png">'
                xtype : 'acquisition-main',
                id:'acquisitionmain'
            }],
            listeners: {
               activate: function (acquisitiontab) {
                    var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                    headerlogos.setHidden(false);

                    var acquisitionmain = acquisitiontab.down('panel[name=acquisitionmain]');
                    acquisitionmain.getController().checkStatusServices();

                    var productgridstore  = Ext.data.StoreManager.lookup('ProductsActiveStore');
                    var acqgridsstore = Ext.data.StoreManager.lookup('DataAcquisitionsStore');
                    var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');
                    var eumetcastsourcestore = Ext.data.StoreManager.lookup('EumetcastSourceStore');
                    var internetsourcestore = Ext.data.StoreManager.lookup('InternetSourceStore');

                    var myLoadMask = new Ext.LoadMask({
                        msg    : esapp.Utils.getTranslation('loading'), // 'Loading...',
                        target : this
                    });

                    if (eumetcastsourcestore.isStore && !eumetcastsourcestore.isLoaded()) {
                        eumetcastsourcestore.load();
                    }
                    if (internetsourcestore.isStore && !internetsourcestore.isLoaded()) {
                        internetsourcestore.load();
                    }

                    if (ingestiongridstore.isStore && !ingestiongridstore.isLoaded() ){
                        myLoadMask.show();
                        ingestiongridstore.load({
                            callback: function(records, options, success){
                                myLoadMask.hide();
                                if (acqgridsstore.isStore && !acqgridsstore.isLoaded()) {
                                    myLoadMask.show();
                                    acqgridsstore.load({
                                        callback: function(records, options, success) {
                                            myLoadMask.hide();
                                            if (productgridstore.isStore && !productgridstore.isLoaded()) {
                                                myLoadMask.show();
                                                productgridstore.load({
                                                    callback: function(records, options, success){
                                                        myLoadMask.hide();
                                                    }
                                                });
                                            }
                                        }
                                    });
                                }
                            }
                        });
                    }

                   //Ext.util.Observable.capture(acquisitionmain, function(e){console.log(e);});
                   //acquisitionmain.getView().getFeature('productcategories').expandAll();
                   //acquisitionmain.getView().refresh();
               },
               beforedeactivate: function (acquisitiontab) {
                   var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("datasetchart-") != -1}');
                   Ext.each(completenessTooltips, function(item) {
                       item.hide();
                   });
               }
            }
        };

        me.processing = {
            title: esapp.Utils.getTranslation('processing'),  // 'Processing',
            id:'processingmaintab',
            xtype:'container',
            autoScroll: true,
            layout: 'fit',
            items: [{
               xtype  : 'processing-main',
               id:'processingmain'
            }],
            listeners: {
               activate: function (processingtab) {
                   var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                   headerlogos.setHidden(false);
                   processingtab.down('panel[name=processingmain]').getController().checkStatusServices();
               }
            }
        };

        me.datamanagement = {
            title: esapp.Utils.getTranslation('datamanagement'),  // 'Data Management',
            id:'datamanagementmaintab',
            xtype:'container',
            autoScroll: true,
            layout: 'fit',
            items: [{
               xtype  : 'datamanagement-main',
               id:'datamanagementmain'
            }],
            listeners: {
               activate: function (datamanagementtab) {
                    var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                    headerlogos.setHidden(false);

                    var datasetsstore  = Ext.data.StoreManager.lookup('DataSetsStore');
                    if (datasetsstore.isStore && !datasetsstore.isLoaded()) {
                        datasetsstore.load();
                    }

                   //var datamanagementmain = datamanagementtab.down('panel[name=datamanagementmain]');
                   //
                   ////datamanagementmain.getView().getFeature('prodcat').expandAll();
                   //datamanagementmain.getView().refresh();
               },
               beforedeactivate: function (acquisitiontab) {
                   var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("datasetchart-") != -1}');
                   Ext.each(completenessTooltips, function(item) {
                       item.hide();
                   });
               }
            }
        };

        me.analysis = {
            title: esapp.Utils.getTranslation('analysis'),  // 'Analysis',
            id:'analysistab',
            xtype:'container',
            autoScroll: true,
            layout : 'fit',
            disabled: false,
            hidden: false,
            items: [{
                xtype  : 'analysis-main',
                id:'analysismain',
                hidden: false
            }],
            listeners: {
                activate: function (analysistab) {
                    // Ext.util.Observable.capture(analysistab, function(e){console.log(analysistab.id + ': ' + e);});
                    if (esapp.globals['typeinstallation'] == 'jrc_online'){
                        if (analysistab.layoutCounter > 0){
                            // Ext.getCmp('headerlogos').collapse();
                        }
                    }
                    else if (esapp.globals['typeinstallation'] != 'windows'){
                        var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                        headerlogos.setHidden(true);
                    }
                    // console.info('analysis tab activated!');
                    // var timeseriesChartSelectionWindow = this.down().lookupReference('timeserieschartselection');
                    // timeseriesChartSelectionWindow.fireEvent('align');
               }
            }
        };

        me.system = {
            title: esapp.Utils.getTranslation('system'),  // 'System',
            id:'systemtab',
            xtype:'container',
            autoScroll: true,
            layout : 'center',
            items: [{
               xtype  : 'systemsettings',
               id:'systemsettingsview'
            }],
            listeners: {
               activate: function (systemtab) {
                    var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                    headerlogos.setHidden(false);

                    var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
                    var formpanel = Ext.getCmp('systemsettingsview');
                    var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                        scope: formpanel,
                        loadmask: true,
                        failure: function(record, operation) {
                            //console.info('failure');
                        },
                        success: function(record, operation) {
                            if (operation.success){
                                formpanel.loadRecord(systemsettingsrecord);
                                formpanel.updateRecord();
                            }
                        }
                    });
               }
            }
        };

        me.help =  {
            title: esapp.Utils.getTranslation('help'),  // 'Help',
            xtype: 'container',
            autoScroll: true,
            layout : 'center',
            items: [{
               xtype  : 'help',
               id:'helpview'
            }],
            listeners: {
                activate: function (helptab) {
                    if (esapp.globals['typeinstallation'] == 'jrc_online'){
                        Ext.getCmp('headerlogos').expand();
                    }
                    else {
                        var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
                        headerlogos.setHidden(false);
                    }
                }
            }
        };


        if (esapp.globals['typeinstallation'] == 'jrc_online'){
            me.loginview = 'loginviewECAS';

            me.northheader = {
                region: 'north',
                id: 'headerlogos',
                // xtype:'container',
                minHeight: 165,
                maxHeight: 165,
                titleAlign: 'center',
                items:[{
                    xtype : 'headerLogos'
                }],
                split: true,
                alwaysOnTop: true,
                hideCollapseTool: true,
                header: false,
                collapsible: true,
                collapsed: false,
                autoScroll:false,
                floatable: false,

                listeners: {
                    collapse: function (headercontainer) {
                        // Ext.util.Observable.capture(headercontainer, function(e){console.log(headercontainer.id + ': ' + e);});
                        headercontainer.header =  true;
                        headercontainer.setTitle('<span class="panel-title-style">'+esapp.Utils.getTranslation('Joint Research Centre - eStation 2 - EARTH OBSERVATION PROCESSING SERVICE')+'</span>');
                    },
                    expand: function (headercontainer) {
                        headercontainer.header =  false;
                        headercontainer.setTitle('');
                    },
                    focusenter: function(){
                        // Ext.getCmp('headerlogos').collapse();
                    }
                }
            }
        }
        else if (esapp.globals['typeinstallation'] == 'windows'){
            me.loginview = 'loginview';

            me.northheader = {
                region: 'north',
                id: 'headerlogos',
                // xtype:'container',
                height: 68,
                titleAlign: 'center',
                items:[{
                    xtype : 'headerLogos'
                }],
                split: true,
                alwaysOnTop: true,
                hideCollapseTool: true,
                header: false,
                collapsible: true,
                collapsed: false,
                autoScroll:false,
                floatable: false,

                listeners: {
                    collapse: function (headercontainer) {
                        // Ext.util.Observable.capture(headercontainer, function(e){console.log(headercontainer.id + ': ' + e);});
                        headercontainer.header =  true;
                        headercontainer.setTitle('<span class="panel-title-style">'+esapp.Utils.getTranslation('eStation 2 - EARTH OBSERVATION PROCESSING SERVICE')+'</span>');
                    },
                    expand: function (headercontainer) {
                        headercontainer.header =  false;
                        headercontainer.setTitle('');
                    },
                    focusenter: function(){
                        // Ext.getCmp('headerlogos').collapse();
                    }
                }
            }
        }
        else {
            me.loginview = 'loginview';

            me.northheader = {
                region: 'north',
                id: 'headerlogos',
                xtype: 'container',
                title: '',
                height: 71,
                items: [{
                    xtype: 'headerLogos'
                }],
                split: false,
                collapsible: false,
                collapsed: false
            }
        }


        me.maintabpanel = Ext.create('Ext.tab.Panel', {
            region: 'center',
            xtype: 'tabpanel',
            id: 'maintabpanel',
            layout: 'fit',
            deferredRender: false,
            layoutOnTabChange: true,
            // activeTab: 'dashboardtab',     // first tab initially active
            // defaults:{hideMode: 'offsets'}, // For performance resons to pre-render in the background.

            listeners: {
                afterrender: function (tabpanel) {
                    var bar = tabpanel.tabBar;
                    bar.insert(tabpanel.tabBar.items.length, [{
                        xtype: 'component',
                        flex: 1
                    }, {
                        xtype: me.loginview     // 'loginview'
                    }, {
                        xtype: 'combo',
                        id: 'languageCombo',
                        name: 'languageCombo',
                        store: 'LanguagesStore',
                        displayField: 'langdescription',
                        valueField: 'langcode',
                        emptyText: esapp.Utils.getTranslation('select'),  // 'Select...',
                        labelWidth: 50,
                        labelAlign: 'left',
                        publishes: ['langcode'],
                        typeAhead: true,
                        queryMode: 'local',
                        width: 120,
                        listeners: {
                            select: function (languagecombo, record) {
                                //console.info(languagecombo.getValue());
                                window.location = '?lang=' + languagecombo.getValue();
                            }
                        }
                    }]);
                    //console.info('language: ' + esapp.globals['selectedLanguage']);
                    Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
                }
            }
        });

        if (esapp.globals['typeinstallation'] == 'windows'){
            me.maintabpanel.add(me.analysis);
            me.maintabpanel.add(me.system);
            me.maintabpanel.add(me.help);
            // me.maintabpanel.setActiveTab('analysistab');
        }
        else if (esapp.globals['typeinstallation'] == 'jrc_online'){
            me.maintabpanel.add(me.analysis);
            // me.maintabpanel.add(me.system);
            me.maintabpanel.add(me.help);
        }
        else {
            me.maintabpanel.add(me.dashboard);
            me.maintabpanel.add(me.acquisition);
            me.maintabpanel.add(me.processing);
            me.maintabpanel.add(me.datamanagement);
            me.maintabpanel.add(me.analysis);
            me.maintabpanel.add(me.system);
            me.maintabpanel.add(me.help);
            // me.maintabpanel.setActiveTab('dashboardtab');
        }

        me.items = [
            me.northheader,
            me.maintabpanel
        ];
            // //},{
            // //    region: 'west',
            // //    stateId: 'navigation-panel',
            // //    id: 'versioninfo-west-panel', // see Ext.getCmp() below
            // //    title: '<span class="panel-title-style">eStation 2.0</span>',
            // //    split: false,
            // //    width: 2,
            // //    collapsible: false,
            // //    collapsed: true,
            // //    hideCollapseTool: true
            // },{
            //     region: 'center',
            //     xtype: 'tabpanel',
            //     id: 'maintabpanel',
            //     layout: 'fit',
            //     deferredRender: false,
            //     layoutOnTabChange: true,
            //     activeTab: 'dashboardtab',     // first tab initially active
            //
            //     // defaults:{hideMode: 'offsets'}, // For performance resons to pre-render in the background.
            //
            //     listeners: {
            //         afterrender: function(tabpanel) {
            //             var bar = tabpanel.tabBar;
            //             bar.insert(tabpanel.tabBar.items.length, [{
            //                 xtype: 'component',
            //                 flex: 1
            //             }, {
            //                 xtype: 'loginview'
            //             }, {
            //                 xtype: 'combo',
            //                 id:'languageCombo',
            //                 name:'languageCombo',
            //                 store: 'LanguagesStore',
            //                 displayField:'langdescription',
            //                 valueField: 'langcode',
            //                 emptyText:esapp.Utils.getTranslation('select'),  // 'Select...',
            //                 labelWidth: 50,
            //                 labelAlign: 'left',
            //                 publishes: ['langcode'],
            //                 typeAhead: true,
            //                 queryMode: 'local',
            //                 width:120,
            //                 listeners: {
            //                     select: function (languagecombo, record){
            //                         //console.info(languagecombo.getValue());
            //                         window.location = '?lang='+languagecombo.getValue();
            //                     }
            //                 }
            //             }]);
            //             //console.info('language: ' + esapp.globals['selectedLanguage']);
            //             Ext.getCmp("languageCombo").setValue(esapp.globals['selectedLanguage']);
            //         }
            //     },
            //
            //     items: [{
            //         title: esapp.Utils.getTranslation('dashboard'),  // 'Dashboard',
            //         id:'dashboardtab',
            //         xtype:'container',
            //         autoScroll: true,
            //         layout : 'center',
            //         bodyCls:'dashboard-panel-body',
            //         items: [{
            //             xtype: 'dashboard-main'
            //         }],
            //         listeners: {
            //            activate: function (dashboardtab) {
            //                var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                headerlogos.setHidden(false);
            //                //dashboardtab.up().down('container[id=acquisitionmaintab]').doLayout();
            //                //dashboardtab.up().down('container[id=datamanagementmaintab]').doLayout();
            //                //Ext.getCmp('dashboard-panel').getController().setupDashboard();
            //                if (Ext.isObject(dashboardtab.down('panel[id=dashboardpc2]'))){
            //                     dashboardtab.down('panel[id=dashboardpc2]').getController().checkStatusServices();
            //                }
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('acquisition'),  // 'Acquisition',
            //         id:'acquisitionmaintab',
            //         xtype:'container',
            //         closable: false,
            //         autoScroll: true,
            //         layout: 'fit',
            //         items: [{
            //             // html: '<img alt="Mockup Acquisition" width="100%" height="100%" src="../resources/img/mockup_acquisition.png">'
            //             xtype : 'acquisition-main',
            //             id:'acquisitionmain'
            //         }],
            //         listeners: {
            //            activate: function (acquisitiontab) {
            //                var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                headerlogos.setHidden(false);
            //
            //                var acquisitionmain = acquisitiontab.down('panel[name=acquisitionmain]');
            //                acquisitionmain.getController().checkStatusServices();
            //
            //                //Ext.util.Observable.capture(acquisitionmain, function(e){console.log(e);});
            //
            //                //acquisitionmain.getView().getFeature('productcategories').expandAll();
            //                //acquisitionmain.getView().refresh();
            //            },
            //            beforedeactivate: function (acquisitiontab) {
            //                var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("datasetchart-") != -1}');
            //                Ext.each(completenessTooltips, function(item) {
            //                    item.hide();
            //                });
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('processing'),  // 'Processing',
            //         id:'processingmaintab',
            //         xtype:'container',
            //         autoScroll: true,
            //         layout: 'fit',
            //         items: [{
            //            xtype  : 'processing-main',
            //            id:'processingmain'
            //         }],
            //         listeners: {
            //            activate: function (processingtab) {
            //                var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                headerlogos.setHidden(false);
            //                processingtab.down('panel[name=processingmain]').getController().checkStatusServices();
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('datamanagement'),  // 'Data Management',
            //         id:'datamanagementmaintab',
            //         xtype:'container',
            //         autoScroll: true,
            //         layout: 'fit',
            //         items: [{
            //            xtype  : 'datamanagement-main',
            //            id:'datamanagementmain'
            //         }],
            //         listeners: {
            //            activate: function (datamanagementtab) {
            //                var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                headerlogos.setHidden(false);
            //
            //                //var datamanagementmain = datamanagementtab.down('panel[name=datamanagementmain]');
            //                //
            //                ////datamanagementmain.getView().getFeature('prodcat').expandAll();
            //                //datamanagementmain.getView().refresh();
            //            },
            //            beforedeactivate: function (acquisitiontab) {
            //                var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("datasetchart-") != -1}');
            //                Ext.each(completenessTooltips, function(item) {
            //                    item.hide();
            //                });
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('analysis'),  // 'Analysis',
            //         id:'analysistab',
            //         xtype:'container',
            //         autoScroll: true,
            //         layout : 'fit',
            //         disabled: false,
            //         hidden: false,
            //         items: [{
            //             xtype  : 'analysis-main',
            //             id:'analysismain',
            //             hidden: false
            //         }],
            //         listeners: {
            //            activate: function (analysistab) {
            //                var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                headerlogos.setHidden(true);
            //                //analysistab.down().render();
            //                //analysistab.down().fireEvent('focusenter');
            //                //analysistab.down().controller.newMapView();
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('system'),  // 'System',
            //         id:'systemtab',
            //         xtype:'container',
            //         autoScroll: true,
            //         layout : 'center',
            //         items: [{
            //            xtype  : 'systemsettings',
            //            id:'systemsettingsview'
            //         }],
            //         listeners: {
            //            activate: function (systemtab) {
            //                 var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                 headerlogos.setHidden(false);
            //
            //                 var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
            //                 var formpanel = Ext.getCmp('systemsettingsview');
            //                 var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
            //                     scope: formpanel,
            //                     loadmask: true,
            //                     failure: function(record, operation) {
            //                         //console.info('failure');
            //                     },
            //                     success: function(record, operation) {
            //                         if (operation.success){
            //                             formpanel.loadRecord(systemsettingsrecord);
            //                             formpanel.updateRecord();
            //                         }
            //                     }
            //                 });
            //            }
            //         }
            //     }, {
            //         title: esapp.Utils.getTranslation('help'),  // 'Help',
            //         xtype: 'container',
            //         autoScroll: true,
            //         layout : 'center',
            //         items: [{
            //            xtype  : 'help',
            //            id:'helpview'
            //         }],
            //         listeners: {
            //             activate: function (helptab) {
            //                 var headerlogos = Ext.ComponentQuery.query('container[id=headerlogos]')[0];
            //                 headerlogos.setHidden(false);
            //             }
            //         }
            //     }]
            // }];

        me.callParent();

        if (esapp.globals['typeinstallation'] == 'windows'){
            me.maintabpanel.setActiveTab('analysistab');
        }
        else if (esapp.globals['typeinstallation'] == 'jrc_online'){
            me.maintabpanel.setActiveTab('analysistab');
        }
        else {
            me.maintabpanel.setActiveTab('dashboardtab');
        }
    }
});