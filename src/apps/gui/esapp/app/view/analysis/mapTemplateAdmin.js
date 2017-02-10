
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

    "xtype"  : 'usermaptpl',

    id: 'userMapTemplates',
    reference: 'userMapTemplates',
    //title: '',
    header: {
        hidden: true
        //titlePosition: 0,
        //titleAlign: 'center'
        //,iconCls: 'maptemplate'
    },
    //constrainHeader: Ext.getBody(),

    //modal: false,
    closable: false,
    closeAction: 'hide',
    maximizable: false,
    //resizable: false,
    //autoScroll: true,
    //height: Ext.getBody().getViewSize().height < 400 ? Ext.getBody().getViewSize().height-10 : 400,
    //autoWidth: false,
    //autoHeight: false,
    //maxHeight: 300,
    height: 300,
    width: 500,

    border:false,
    frame: false,
    bodyBorder: true,
    //bodyCls: 'rounded-box',
    layout: {
        type  : 'fit',
        padding: 0
    },

    bind: '{usermaptemplates}',
    //session:true,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: false,
        trackOver: true,
        forceFit:true
    },

    selModel : {
        allowDeselect : true,
        mode:'MULTI'
        //,listeners: {}
    },

    //cls: 'grid-color-yellow',
    hideHeaders: false,
    collapsible: false,
    enableColumnMove:false,
    enableColumnResize:true,
    sortableColumns:true,
    multiColumnSort: false,
    columnLines: true,
    rowLines: true,
    cls: 'newpanelstyle',

    initComponent: function () {
        var me = this;
        //Ext.util.Observable.capture(me, function(e){console.log('mapTemplateAdmin - ' + me.id + ': ' + e);});

        me.mon(me, {
            loadstore: function() {
                me.getViewModel().getStore('usermaptemplates').proxy.extraParams = {userid: esapp.getUser().userid};
                me.getViewModel().getStore('usermaptemplates').load({
                    callback: function(records, options, success) {
                        //console.info(records);
                        //console.info(options);
                        //console.info(success);
                    }
                });
            }
        });

        me.listeners = {
            focusleave: function(){
                this.hide();
            }
        };

        me.tools = [
        {
            type: 'refresh',
            align: 'c-c',
            tooltip: 'Refresh map template list',   //esapp.Utils.getTranslation('refreshmaptpllist'),    // 'Refresh map template list',
            callback: 'loadUserMapTplStore'
        }];

        me.bbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                xtype: 'button',
                text: 'Open selected',  // esapp.Utils.getTranslation('openselected'),    // 'Open selected',
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
            text: 'Map template name',  // esapp.Utils.getTranslation('maptemplatename'),  // 'Map template name',
            width: 300,
            dataIndex: 'templatename',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        }, {
            xtype: 'actioncolumn',
            header: 'Auto open template',   // esapp.Utils.getTranslation('autoopentpl'),  // 'Auto open template',
            menuDisabled: true,
            sortable: true,
            variableRowHeight: true,
            draggable: false,
            groupable: false,
            hideable: false,
            width: 100,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                style: {"line-height": "70px"},
                getClass: function (v, meta, rec) {
                    if (rec.get('auto_open')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function (v, meta, rec) {
                    if (rec.get('auto_open')) {
                        return 'Do not auto open template';  // esapp.Utils.getTranslation('tip_no_autoopentpl');     // 'Do not auto open template';
                    } else {
                        return 'Auto open template';    // esapp.Utils.getTranslation('tip_autoopentpl');     // 'Auto open template';
                    }
                },
                handler: function (grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('auto_open') ? 'deactivated' : 'activated');
                    rec.get('auto_open') ? rec.set('auto_open', false) : rec.set('auto_open', true);
                }
            }]
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
                    return esapp.Utils.getTranslation('Delete Map template: ') + ' ' + rec.get('templatename');
                },
                handler: 'deleteMapTemplate'
            }]
        }];

        me.callParent();

    }
});
