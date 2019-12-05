
Ext.define("esapp.view.analysis.userWorkspaceAdmin",{
    extend: "Ext.grid.Panel",
 
    requires: [
        "esapp.view.analysis.userWorkspaceAdminController",
        "esapp.view.analysis.userWorkspaceAdminModel",

        "Ext.grid.column.Action"
    ],
    
    controller: "analysis-userworkspaceadmin",
    viewModel: {
        type: "analysis-userworkspaceadmin"
    },

    xtype  : 'userworkspaceadmin',

    title: esapp.Utils.getTranslation('my_saved_workspaces'),
    header: {
        hidden: false,
        titlePosition: 0,
        titleAlign: 'center',
        focusable: true
    },

    autoShow : false,
    hidden: true,

    floating: true,
    closable: true,
    closeAction: 'hide',
    maximizable: false,
    collapsible: false,
    resizable: false,
    autoScroll: true,

    //height: Ext.getBody().getViewSize().height < 400 ? Ext.getBody().getViewSize().height-10 : 400,
    height: 400,
    width: 550,
    layout: 'fit',

    border:false,
    frame: false,
    bodyBorder: true,
    // defaultAlign: 'tc-bc',
    // bind: '{userworkspaces}',

    selModel : {
        allowDeselect : true,
        mode:'MULTI'
    },

    hideHeaders: false,
    enableColumnMove:false,
    enableColumnResize:true,
    sortableColumns:true,
    multiColumnSort: false,
    columnLines: true,
    rowLines: true,
    cls: 'newpanelstyle',

    config: {
        forceStoreLoad: false,
        dirtyStore: false,
        refworkspaces: false
    },

    initComponent: function () {
        var me = this;

        me.selModel.listeners = {
            selectionchange: function(){
                if (this.getSelection().length < 1){
                    me.lookupReference('exportworkspaces').disable(true);
                }
                else {
                    me.lookupReference('exportworkspaces').enable(true);
                }
            }
        }

        if(me.refworkspaces){
            if (esapp.getUser() == 'undefined' || esapp.getUser() == null){
                me.width = 275;
            }
            else {
                me.width = 420;
            }

            me.setBind({
                store: '{refworkspaces}'
            });
        }
        else {
            me.width = 550;
            me.setBind({
                store: '{userworkspaces}'
            });
        }

        if(me.refworkspaces){
            me.title = esapp.Utils.getTranslation('reference_workspaces');
        }
        else {
            me.title = esapp.Utils.getTranslation('my_saved_workspaces');
        }

        me.hidden = true;

        me.viewConfig = {
            // defaultAlign: 'tc-bc',
            stripeRows: false,
            enableTextSelection: true,
            draggable: false,
            markDirty: false,
            disableSelection: false,
            trackOver: true,
            forceFit: true
        };

        // Ext.util.Observable.capture(me, function(e){console.log('graphTemplateAdmin - ' + me.id + ': ' + e);});

        me.mon(me, {
            loadstore: function() {
                if(me.refworkspaces){
                    if (me.forceStoreLoad || !me.getViewModel().getStore('refworkspaces').getSource().isLoaded() || me.dirtyStore) {
                        // me.getViewModel().getStore('refworkspaces').getSource().proxy.extraParams = {userid: esapp.getUser().userid};
                        me.getViewModel().getStore('refworkspaces').getSource().load({
                            callback: function (records, options, success) {
                            }
                        });
                        me.forceStoreLoad = false;
                        me.dirtyStore = false;
                    }
                }
                else {
                    if (me.forceStoreLoad || !me.getViewModel().getStore('userworkspaces').getSource().isLoaded() || me.dirtyStore) {
                        me.getViewModel().getStore('userworkspaces').getSource().proxy.extraParams = {userid: esapp.getUser().userid};
                        me.getViewModel().getStore('userworkspaces').getSource().load({
                            callback: function (records, options, success) {
                            }
                        });
                        me.forceStoreLoad = false;
                        me.dirtyStore = false;
                    }
                }
            }
        });

        me.listeners = {
            show: function(){
                if(me.refworkspaces){
                    if (esapp.getUser() == 'undefined' || esapp.getUser() == null){
                        me.lookupReference('open_by_default_column').setHidden(true);
                        me.setWidth(275);
                    }
                    else {
                        me.lookupReference('open_by_default_column').setHidden(false);
                        me.setWidth(420);
                    }
                }
                me.fireEvent('loadstore');
                me.fireEvent('align');
                me.updateLayout();
            },
            align: function() {
                // me.alignTo(me.owner, 'tc-bc');
                me.alignTo(me.owner);
                me.updateLayout();
            },
            focusleave: function(){
                me.hide();
            }
        };

        me.tools = [
        {
            type: 'refresh',
            align: 'c-c',
            tooltip: esapp.Utils.getTranslation('refreshworkspaceslist'),    // 'Refresh workspaces list',
            callback: function() {
                me.forceStoreLoad = true;
                me.fireEvent('loadstore');
            }
        }];

        me.bbar = Ext.create('Ext.toolbar.Toolbar', {
            focusable: true,
            items: [{
                xtype: 'button',
                text: esapp.Utils.getTranslation('openselected'),    // 'Open selected',
                reference: 'openworkspaces',
                iconCls: 'fa fa-folder-open-o fa-2x',
                style: {color: 'green'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'openWorkspaces'
            },{
                xtype: 'button',
                text: esapp.Utils.getTranslation('newworkspace'),    // 'New',
                reference: 'newworkspace',
                iconCls: 'fa fa-plus-circle fa-2x',
                style: {color: 'green'},
                hidden: me.refworkspaces ? true : false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'newWorkspace'
            },'->',{
                xtype: 'button',
                text: esapp.Utils.getTranslation('export_workspaces'),    // 'Export',
                reference: 'exportworkspaces',
                iconCls: 'fa fa-download fa-2x',
                style: {color: 'blue'},
                hidden: me.refworkspaces ? true : false,
                disabled: true,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'exportWorkspaces'
            },{
                xtype: 'button',
                text: esapp.Utils.getTranslation('import'),    // 'Import',
                reference: 'importworkspaces',
                iconCls: 'fa fa-upload fa-2x',
                style: {color: 'orange'},
                hidden: me.refworkspaces ? true : false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'importWorkspaces'
            }]
        });

        // me.defaultListenerScope = true;

        me.columns = [{
            text: esapp.Utils.getTranslation('workspacename'),  // 'Workspace name',
            width: 250,
            dataIndex: 'workspacename',
            cellWrap: true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight: true,
            draggable: false,
            groupable: false,
            hideable: false
        },{
            xtype: 'actioncolumn',
            text: esapp.Utils.getTranslation('open_in_default_ws'),  // 'Open in default WS',
            reference: 'open_by_default_column',
            width: 145,
            align: 'center',
            cellWrap: true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight: true,
            draggable: false,
            groupable: false,
            // hidden: me.refworkspaces ? true : false,
            hidden: (me.refworkspaces && (esapp.getUser() == 'undefined' || esapp.getUser() == null) ? true : false),
            items: [{
                getClass: function (v, meta, rec) {
                    if (rec.get('showindefault')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function (v, meta, rec) {
                    //if (rec.get('selected')) {
                    //    return esapp.Utils.getTranslation('deactivateproduct');   // 'Deactivate Product';
                    //} else {
                    //    return esapp.Utils.getTranslation('activateproduct');   // 'Activate Product';
                    //}
                },
                handler: function (grid, rowIndex, colIndex, icon, e, record) {
                    var refworkspacestore  = Ext.data.StoreManager.lookup('RefWorkspacesStore');
                    var userworkspacestore  = Ext.data.StoreManager.lookup('UserWorkspacesStore');

                    if (record.get('showindefault')){
                        record.set('showindefault', false);

                        refworkspacestore.sync();
                        userworkspacestore.sync();

                        me.show(true);
                    }
                    else {
                        record.set('showindefault', true);

                        grid.getStore().getData().each(function (workspace) {
                            if (workspace != record){
                                workspace.set('showindefault', false);
                            }
                        });

                        if (grid.getStore().config.source == 'RefWorkspacesStore'){
                            userworkspacestore.getData().each(function (workspace) {
                                workspace.set('showindefault', false);
                            });
                        }
                        else {
                            refworkspacestore.getData().each(function (workspace) {
                                workspace.set('showindefault', false);
                            });
                        }
                        refworkspacestore.sync();
                        userworkspacestore.sync();
                        // me.updateLayout();
                        me.show(true);
                    }
                }
            }]
        // },{
        //     text    : 'Open in default WS',
        //     xtype   : 'widgetcolumn',
        //     // flex    : 1,
        //     width: 150,
        //     dataIndex: 'showindefault',
        //     onWidgetAttach: function (column, widget, record) {
        //         widget.down("[inputValue=${record.get('showindefault')}]").setValue(true);
        //     },
        //     widget   : {
        //         xtype: 'radiogroup',
        //         // hideLabel:true,
        //         columns: 1,
        //         vertical: true,
        //         // simpleValue: true,  // set simpleValue to true to enable value binding
        //         // bind: '{showindefault}',
        //         dataIndex: 'showindefault',
        //         items: [
        //             { name: 'showindefault'}
        //         ]
        //     }
        },{
            xtype: 'actioncolumn',
            // header: esapp.Utils.getTranslation('delete'),   // 'Delete',
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false,
            width: 60,
            align: 'center',
            stopSelection: false,
            hidden: me.refworkspaces ? true : false,

            items: [{
                width:'45',
                disabled: false,
                getClass: function(v, meta, rec) {
                    return 'delete';
                },
                getTip: function(v, meta, rec) {
                    return esapp.Utils.getTranslation('delete_workspace') + ': ' + rec.get('workspacename');   // 'Delete workspace'
                },
                handler: 'deleteWorkspace'
            }]
        }];

        me.callParent();

    }
});
