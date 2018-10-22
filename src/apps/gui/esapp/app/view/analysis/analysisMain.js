
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

        'Ext.layout.container.Card',
        'Ext.form.field.ComboBox'
    ],

    id: 'analysismain',
    name: 'analysismain',
    reference: 'analysismain',

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
            afterrender: function(tabpanel) {
                // console.info(esapp.getUser());
                var bar = tabpanel.tabBar;
                bar.insert(tabpanel.tabBar.items.length, [{
                    xtype: 'component',
                    html: '&nbsp'
                }, {
                    xtype: 'toolbar',
                    padding: '6px 0px 0px 0px',
                    margin: 0,
                    style: {
                        backgroundColor:'transparent'
                    },
                    layout: {
                        pack: 'bottom',
                        type: 'hbox'
                    },
                    items: [{
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
        };

        me.items = [{
            xtype: 'analysisworkspace',
            reference: 'defaultworkspace',
            workspaceid: 'defaultworkspace',
            workspacename: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
            title: esapp.Utils.getTranslation('default_workspace'),     // 'Default workspace',
            closable: false,
            pinable: false,
            pinned: false    // no pin icon, so not pinnable because the default workspace will always be opened.
        }];

        me.callParent();
    }
});
