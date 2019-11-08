
Ext.define("esapp.view.analysis.analysisMain",{
    "extend": "Ext.tab.Panel",
    "controller": "analysis-analysismain",
    "viewModel": {
        "type": "analysis-analysismain"
    },

    xtype  : 'analysis-main',

    requires: [
        'esapp.view.analysis.analysisMainModel',
        'esapp.view.analysis.analysisMainController',
        'esapp.view.analysis.workspace',

        'esapp.TabTitleEditor',
        'Ext.ux.TabReorderer',

        'Ext.layout.container.Card',
        'Ext.form.field.ComboBox'
    ],

    id: 'analysismain',
    name: 'analysismain',
    reference: 'analysismain',

    plugins: ['tabreorderer'],

    layout: {
        type: 'card',
        padding: 0
    },
    frame: false,
    border: false,
    bodyPadding: '1 0 0 0',
    ui: 'workspace',
    tabPosition: 'top',
    // tabRotation: 'default', // 0,

    initComponent: function () {
        var me = this;

        me.vectorLayerPool = [];

        me.listeners = {
            // render: function(c){
            //     c.editor = new Ext.Editor(new Ext.form.TextField({
            //         allowBlank: false,
            //         enterIsSpecial: true
            //     }), {
            //         autoSize: 'width',
            //         completeOnEnter: true,
            //         cancelOnEsc: true,
            //         listeners: {
            //             complete: function(editor, value){
            //                 var item = this.getComponent(editor.boundEl.id.split(this.idDelimiter)[1]);
            //                 item.setTitle(value);
            //             },
            //             scope: c
            //         }
            //     });
            //     c.mon(c.strip, {
            //         dblclick: function(e){
            //             var t = this.findTargets(e);
            //             if(t && t.item && !t.close){
            //                 this.editor.startEdit(t.el, t.item.title);
            //             }
            //         },
            //         scope: c
            //     });
            // },
            beforerender: function(tabpanel) {
                // console.info(esapp.getUser());
                var bar = tabpanel.tabBar;

                // bar.insert(tabpanel.tabBar.items.length, [{
                bar.insert(0, [{
                //     xtype: 'component',
                //     html: '&nbsp'
                // }, {
                    xtype: 'toolbar',
                    padding: '6px 0px 0px 0px',
                    margin:'0px 0px 0px 10px',
                    enableFocusableContainer: true,
                    focusable: true,
                    style: {
                        backgroundColor:'transparent'
                    },
                    layout: {
                        pack: 'bottom',
                        type: 'hbox'
                    },
                    listeners: null,
                    items: [{
                        xtype: 'button',
                        reference: 'analysismain_refworkspacesbtn',
                        text:  esapp.Utils.getTranslation('ref_workspaces'), // 'REF WORKSPACES',
                        // hidden: (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                        scale: 'small',
                        tooltip: esapp.Utils.getTranslation('open_ref_workspace'),    // 'Open a reference workspace',
                        handler: 'showRefWorkspaceAdmin',
                        listeners: {
                            afterrender: function (btn) {
                                btn.refWorkspaceAdminPanel = new esapp.view.analysis.userWorkspaceAdmin({
                                    owner:btn,
                                    refworkspaces: true
                                });
                            }
                        }
                    },{
                        xtype: 'button',
                        reference: 'analysismain_addworkspacebtn',
                        text:  esapp.Utils.getTranslation('my_saved_workspaces'), // 'MY WORKSPACES',
                        hidden: (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                        scale: 'small',
                        // padding: '3px 1px 0px 3px',
                        // iconCls: 'fa fa-plus-circle fa-2x',
                        // style: { color: 'gray'},
                        tooltip: esapp.Utils.getTranslation('add_workspace'),    // 'Add workspace',
                        handler: 'showUserWorkspaceAdmin',
                        listeners: {
                            afterrender: function (btn) {
                                btn.userWorkspaceAdminPanel = new esapp.view.analysis.userWorkspaceAdmin({owner:btn});
                            }
                        }
                    }]
                }]);

                tabpanel.insert(1,{
                    xtype: 'analysisworkspace',
                    reference: 'defaultworkspace',
                    workspaceid: 'defaultworkspace',
                    workspacename: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
                    title: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
                    isNewWorkspace: false,
                    closable: false,
                    pinable: false,
                    pinned: false    // no pin icon, so not pinnable because the default workspace will always be opened.
                });

                // When the browser window is resized
                Ext.on('resize', function() {
                    // console.log('browser window resized');
                    var tschartselectionpanels = Ext.ComponentQuery.query('timeserieschartselection');
                    // console.info(tschartselectionpanels);

                    Ext.Object.each(tschartselectionpanels, function(id, tschartselectionpanel, thisObj) {
                        tschartselectionpanel.fireEvent('align');
                    });

                });

                // if (this.items.length == 1) {
                //     this.getTabBar().hide();
                // }
            }
            ,afterrender: function(tabpanel){
                var task = new Ext.util.DelayedTask(function() {
                    var refworkspacestore  = Ext.data.StoreManager.lookup('RefWorkspacesStore');
                    var userworkspacestore  = Ext.data.StoreManager.lookup('UserWorkspacesStore');
                    var analysisWorkspaces = Ext.ComponentQuery.query('analysisworkspace');
                    // console.info(refworkspacestore.getData());
                    // console.info(userworkspacestore.getData());

                    var defaultws = '';
                    refworkspacestore.getData().each(function (refworkspace) {
                        // console.info(refworkspace.get('showindefault'));
                        if (refworkspace.get('showindefault')){
                            defaultws = refworkspace;
                        }
                    });

                    if (defaultws == ''){
                        userworkspacestore.getData().each(function (userworkspace) {
                            // console.info(userworkspace.get('showindefault'));
                            if (userworkspace.get('showindefault')){
                                defaultws = userworkspace;
                            }
                        });
                    }

                    // console.info(defaultws);
                    if (defaultws != ''){
                        var defaultwsdata = defaultws.getData();
                        var params = {
                            'userid': defaultwsdata['userid'],
                            'workspaceid': defaultwsdata['workspaceid'],
                            'workspacename': defaultwsdata['workspacename'],
                            'pinned': defaultwsdata['pinned'],
                            'showindefault': defaultwsdata['showindefault'],
                            'shownewgraph': defaultwsdata['shownewgraph'],
                            'showbackgroundlayer': defaultwsdata['showbackgroundlayer'],
                            'isrefworkspace': defaultwsdata['isrefworkspace']
                        }

                        Ext.Ajax.request({
                            method: 'POST',
                            url: 'analysis/workspacemapsgraphs',
                            params: params,
                            success: function(response, opts){
                                var result = Ext.JSON.decode(response.responseText);
                                if (result.success){
                                    defaultws.set('maps',result.workspace.maps);
                                    defaultws.set('graphs', result.workspace.graphs);
                                    defaultws.dirty = false;

                                    Ext.Object.each(analysisWorkspaces, function(id, ws, thisObj) {
                                        if (ws.workspaceid == 'defaultworkspace'){
                                            // ws.setTitle(defaultws.get('workspacename'));
                                            ws.setMaps(defaultws.get('maps'));
                                            ws.setGraphs(defaultws.get('graphs'));

                                            ws.getController().closeAllMapsGraphs();
                                            if (ws.maps.length > 0) {
                                                ws.getController().openWorkspaceMaps(ws.maps);
                                            }
                                            if (ws.graphs.length > 0) {
                                                ws.getController().openWorkspaceGraphs(ws.graphs);
                                            }
                                        }
                                    });
                                }
                            },
                            failure: function(response, opts) {
                                console.info(response.status);
                            }
                        });
                    }
                });
                task.delay(0);
            }
        };

        // me.items = [{
        //     xtype: 'analysisworkspace',
        //     reference: 'defaultworkspace',
        //     workspaceid: 'defaultworkspace',
        //     workspacename: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
        //     title: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
        //     isNewWorkspace: false,
        //     closable: false,
        //     pinable: false,
        //     pinned: false    // no pin icon, so not pinnable because the default workspace will always be opened.
        // }];

        me.callParent();
    }
});
