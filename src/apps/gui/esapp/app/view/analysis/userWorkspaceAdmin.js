
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
    // alwaysOnTop: true,

    //height: Ext.getBody().getViewSize().height < 400 ? Ext.getBody().getViewSize().height-10 : 400,
    //autoWidth: false,
    //autoHeight: false,
    //maxHeight: 300,
    height: 300,
    width: 375,

    border:false,
    frame: false,
    bodyBorder: true,
    defaultAlign: 'tl-bc',
    bind: '{userworkspaces}',

    selModel : {
        allowDeselect : true,
        mode:'SINGLE'
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
        dirtyStore: false
    },

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('my_saved_workspaces');

        me.hidden = true;

        me.viewConfig = {
            defaultAlign: 'tl-r',
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
        });

        me.listeners = {
            show: function(){
                me.fireEvent('loadstore');
                me.fireEvent('align');
            },
            align: function() {
                me.alignTo(me.owner, 'tl-r');
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
                name: 'openworkspaces',
                iconCls: 'fa fa-folder-open-o fa-2x',
                style: {color: 'green'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'openWorkspaces'
            },{
                xtype: 'button',
                text: esapp.Utils.getTranslation('newworkspace'),    // 'New workspace',
                name: 'newworkspace',
                iconCls: 'fa fa-plus-circle fa-2x',
                style: {color: 'green'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'newWorkspace'
            }]
        });

        me.columns = [{
            text: esapp.Utils.getTranslation('workspacename'),  // 'Workspace name',
            width: 270,
            dataIndex: 'workspacename',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        },{
            xtype: 'actioncolumn',
            header: esapp.Utils.getTranslation('delete'),   // 'Delete',
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false,
            width: 80,
            align: 'center',
            stopSelection: false,

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
