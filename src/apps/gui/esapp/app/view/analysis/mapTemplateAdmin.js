
Ext.define("esapp.view.analysis.mapTemplateAdmin",{
    extend: "Ext.grid.Panel",
 
    requires: [
        "esapp.view.analysis.mapTemplateAdminController",
        "esapp.view.analysis.mapTemplateAdminModel",

        "Ext.grid.column.Action"
    ],
    
    controller: "analysis-maptemplateadmin",
    viewModel: {
        type: "analysis-maptemplateadmin"
    },

    xtype  : 'usermaptpl',

    // id: 'userMapTemplates',
    // reference: 'userMapTemplates',
    title: esapp.Utils.getTranslation('map_template'),
    header: {
        hidden: false,
        titlePosition: 0,
        titleAlign: 'center',
        focusable: true
        //,iconCls: 'maptemplate'
    },

    // constrainHeader: Ext.getBody(),
    // constrain: false,
    autoShow : false,
    hidden: true,

    floating: true,
    // floatable: true,
    // alwaysOnTop: true,
    closable: true,
    closeAction: 'hide',
    maximizable: false,
    collapsible: false,
    resizable: false,
    autoScroll: true,
    //height: Ext.getBody().getViewSize().height < 400 ? Ext.getBody().getViewSize().height-10 : 400,
    //autoWidth: false,
    //autoHeight: false,
    //maxHeight: 300,
    height: 300,
    width: 375,

    border:false,
    frame: false,
    bodyBorder: true,
    //bodyCls: 'rounded-box',
    // layout: {
    //     type  : 'fit',
    //     padding: 0
    // },
    // alignTarget: Ext.getCmp('analysismain_maptemplatebtn'),
    defaultAlign: 'tl-bc',
    bind: '{usermaptemplates}',

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
        dirtyStore: false
    },

    initComponent: function () {
        var me = this;

        me.title = esapp.Utils.getTranslation('map_template');

        me.hidden = true;

        me.viewConfig = {
            defaultAlign: 'tl-bc',
            // alignTarget: Ext.getCmp('analysismain_maptemplatebtn'),
            stripeRows: false,
            enableTextSelection: true,
            draggable: false,
            markDirty: false,
            disableSelection: false,
            trackOver: true,
            forceFit: true
        };

        // Ext.util.Observable.capture(me, function(e){console.log('mapTemplateAdmin - ' + me.id + ': ' + e);});

        me.mon(me, {
            loadstore: function() {
                if (me.forceStoreLoad || !me.getViewModel().getStore('usermaptemplates').isLoaded() || me.dirtyStore) {
                    me.getViewModel().getStore('usermaptemplates').proxy.extraParams = {userid: esapp.getUser().userid};
                    me.getViewModel().getStore('usermaptemplates').load({
                        callback: function (records, options, success) {
                        }
                    });
                    me.forceStoreLoad = false;
                    me.dirtyStore = false;
                }
            }
        });

        me.listeners = {
            afterrender: function(){
                me.alignTarget = me.owner;
            },
            show: function(){
                me.fireEvent('loadstore');
                // me.fireEvent('align');
            },
            // align: function() {
            //     // me.alignTo(Ext.getCmp('analysismain').lookupReference('analysismain_maptemplatebtn'), 'tl-bc');
            //     me.alignTo(me.owner, 'tl-bc');
            //     me.updateLayout();
            // },
            focusleave: function(){
                me.hide();
            }
        };

        me.tools = [
        {
            type: 'refresh',
            align: 'c-c',
            tooltip: esapp.Utils.getTranslation('refreshmaptpllist'),    // 'Refresh map template list',
            callback: function() {
                me.forceStoreLoad = true;
                me.fireEvent('loadstore');
            }
        }];

        me.bbar = Ext.create('Ext.toolbar.Toolbar', {
            // focusable: true,
            items: [{
                xtype: 'button',
                text: esapp.Utils.getTranslation('openselected'),    // 'Open selected',
                name: 'addlayer',
                iconCls: 'fa fa-folder-open-o fa-2x',
                style: {color: 'green'},
                hidden: false,
                // glyph: 'xf055@FontAwesome',
                scale: 'medium',
                handler: 'openMapTemplates'
            }]
        });

        me.columns = [{
            text: esapp.Utils.getTranslation('maptemplatename'),  // 'Map template name',
            width: 270,
            dataIndex: 'templatename',
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
                    //if (rec.get('deletable')){
                    //    return 'delete';
                    //}
                },
                getTip: function(v, meta, rec) {
                    return esapp.Utils.getTranslation('delete_map_template') + ': ' + rec.get('templatename');   // 'Delete Map template'
                },
                handler: 'deleteMapTemplate'
            }]
        }];

        me.callParent();

    }
});
