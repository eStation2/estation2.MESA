
Ext.define("esapp.view.acquisition.DataAcquisition",{
    "extend": "Ext.grid.Panel",

    "controller": "dataacquisition",

    "viewModel": {
        "type": "dataacquisition"
    },

    "xtype"  : 'dataacquisitiongrid',

    requires: [
        'esapp.view.acquisition.DataAcquisitionModel',
        'esapp.view.acquisition.DataAcquisitionController',
        'esapp.view.acquisition.logviewer.LogView',

        'Ext.grid.plugin.CellEditing',
        'Ext.grid.column.Action',
        'Ext.grid.column.Check'
    ],

    //store: 'DataAcquisitionsStore',
    //bind: '{ProductAcquisitionsGrid.selection.DataAcquisitions}',
    //bind: '{products.dataacquisitions}',
    //bind: '{dataacquisitions}',

    // get the chained store from view model
    bind:{
        store:'{productdatasources}'
    },

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },
    plugins:[{
        ptype:'cellediting'
    }],
    hideHeaders: true,
    columnLines: false,
    rowLines: false,

    listeners: {
        mouseenter: {
            element: 'el',
            fn: function(){
                this.suspendEvents();
            }
        }
    },

    initComponent: function () {
        var me = this;

        me.defaults = {
            menuDisabled: true,
            variableRowHeight : true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            // text: '', // 'Type',
            width: 105,
            dataIndex: 'type'
            //bind: '{products.dataacquisitions.type}'
            //bind: '{dataacquisitions.type}'
        }, {
            // text: '', // 'Latest Acquired',
            width: 110,
            dataIndex: 'time_latest_copy',
            hidden: true
            //bind: '{products.dataacquisitions.latest}'
            //bind: '{dataacquisitions.latest}'
        }, {
            // text: '', // 'Latest Acquired',
            width: 110,
            dataIndex: 'time_latest_exec',
            hidden: true
            //bind: '{products.dataacquisitions.latest}'
            //bind: '{dataacquisitions.latest}'
        }, {
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden:false,
            // disabled: true,
            width: 65,
            align: 'center',
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (rec.get('activated')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function(v, meta, rec) {
                    if (rec.get('activated')) {
                        return 'Deactivate Get';
                    } else {
                        return 'Activate Get';
                    }
                },
                handler: function(grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('activated') ? 'deactivated' : 'activated');
                    // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                    rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                }
            }]
        },{
            xtype: 'actioncolumn',
            width: 55,
            align:'center',
            items: [{
                icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                tooltip: 'Show log of this Get',
                scope: me,
                handler: function (grid, rowIndex, colIndex, icon) {
                    var rec = grid.getStore().getAt(rowIndex);
                    var logViewWin = new esapp.view.acquisition.logviewer.LogView({
                        params: {
                            logtype: 'get',
                            record: rec
                        }
                    });
                    logViewWin.show();
                }
            }]
        }];

        me.callParent();
    }
});
