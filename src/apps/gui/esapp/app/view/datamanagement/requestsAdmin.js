
Ext.define("esapp.view.datamanagement.requestsAdmin",{
    extend: "Ext.grid.Panel",
 
    requires: [
        "esapp.view.datamanagement.requestsAdminController",
        "esapp.view.datamanagement.requestsAdminModel",

        "Ext.grid.column.Action"
    ],
    
    controller: "datamanagement-requestsadmin",
    viewModel: {
        type: "datamanagement-requestsadmin"
    },

    xtype  : 'requestsadmin',

    title: esapp.Utils.getTranslation('myrequests'),
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
    height: 300,
    width: 700,

    border:false,
    frame: false,
    bodyBorder: true,
    defaultAlign: 'tl-bc',
    bind: '{requests}',

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

        me.title = esapp.Utils.getTranslation('myrequests');

        me.hidden = true;

        me.viewConfig = {
            defaultAlign: 'tl-bc',
            stripeRows: false,
            enableTextSelection: true,
            draggable: false,
            markDirty: false,
            disableSelection: false,
            trackOver: true,
            forceFit: true
        };

        me.mon(me, {
            loadstore: function() {
                if (me.forceStoreLoad || !me.getViewModel().getStore('requests').isLoaded() || me.dirtyStore) {
                    // me.getViewModel().getStore('requests').proxy.extraParams = {userid: esapp.getUser().userid};
                    me.getViewModel().getStore('requests').load({
                        callback: function (records, options, success) {
                            // console.info(records);
                        }
                    });
                    me.forceStoreLoad = false;
                    me.dirtyStore = false;
                    // console.info(me.getViewModel().getStore('requests'));
                }
            }
        });

        me.listeners = {
            afterrender: function(){
                me.alignTarget = me.owner;
            },
            show: function(){
                me.fireEvent('loadstore');
            },
            focusleave: function(){
                me.hide();
            }
        };

        me.tools = [
        {
            type: 'refresh',
            align: 'c-c',
            tooltip: esapp.Utils.getTranslation('refreshrequestslist'),    // 'Refresh requests list',
            callback: function() {
                me.forceStoreLoad = true;
                me.fireEvent('loadstore');
            }
        }];

        // me.bbar = Ext.create('Ext.toolbar.Toolbar', {
        //     // focusable: true,
        //     items: [{
        //         xtype: 'button',
        //         text: esapp.Utils.getTranslation('openselected'),    // 'Open selected',
        //         name: 'addlayer',
        //         iconCls: 'fa fa-folder-open-o fa-2x',
        //         style: {color: 'green'},
        //         hidden: false,
        //         // glyph: 'xf055@FontAwesome',
        //         scale: 'medium',
        //         handler: 'openMapTemplates'
        //     }]
        // });

        me.columns = [{
            xtype: 'actioncolumn',
            header: esapp.Utils.getTranslation('status'),   // 'Status',
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false,
            width: 65,
            align: 'center',
            stopSelection: false,

            items: [{
                width:'45',
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (rec.get('status')=='running'){
                        // return 'fa fa-pause-circle-o fa-2x green';
                        return 'pause'
                    }
                    else if (rec.get('status')=='paused'){
                        // return 'fa fa-play-circle-o fa-2x orange';
                        return 'play'
                    }
                    else {
                        // return 'fa fa-exclamation-circle fa-2x red';
                        return 'exclamation'
                    }
                },
                getTip: function(v, meta, rec) {
                    return esapp.Utils.getTranslation('request_status') + ': ' + rec.get('status');   // 'Request status'
                },
                handler: 'runPauseRequest'
            }]
        },{
            text: esapp.Utils.getTranslation('level'),  // 'Request ID',
            width: 65,
            dataIndex: 'level',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        },{
            text: esapp.Utils.getTranslation('productcode'),  // 'Request ID',
            width: 110,
            dataIndex: 'productcode',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        },{
            text: esapp.Utils.getTranslation('version'),  // 'Request ID',
            width: 80,
            dataIndex: 'version',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        },{
            text: esapp.Utils.getTranslation('subproductcode'),  // 'Request ID',
            width: 135,
            dataIndex: 'subproductcode',
            cellWrap:true,
            menuDisabled: true,
            sortable: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        },{
            text: esapp.Utils.getTranslation('mapsetcode'),  // 'Request ID',
            width: 145,
            dataIndex: 'mapsetcode',
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
            width: 65,
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
                    return esapp.Utils.getTranslation('delete_request') + ': ' + rec.get('requestid');   // 'Delete request'
                },
                handler: 'deleteRequest'
            }]
        }];

        me.callParent();

    }
});
