
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

        'Ext.grid.column.Action'
        //'Ext.grid.column.Check'
    ],

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
    cls: 'grid-color-yellow',
    hideHeaders: true,
    columnLines: false,
    rowLines: false,

    bufferedRenderer: true,

    //listeners: {
    //    beforerender:  function () {
    //        var me = this,
    //            record = me.getWidgetRecord();
    //        Ext.suspendLayouts();
    //        var daStore = me.getViewModel().get('productdatasources');
    //        if (daStore) {
    //            daStore.setFilters({
    //                property: 'productid'
    //                , value: record.id
    //                , anyMatch: true
    //            });
    //        }
    //        Ext.resumeLayouts(true);
    //    }
    //    //,mouseenter: {
    //        //element: 'el',
    //        //fn: function(){
    //        //    this.suspendEvents();
    //        //}
    //    //}
    //},

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
        }, {
            // text: '', // 'Latest Acquired',
            width: 110,
            dataIndex: 'time_latest_copy',
            hidden: true
        }, {
            // text: '', // 'Latest Acquired',
            width: 110,
            dataIndex: 'time_latest_exec',
            hidden: true
        }, {
            xtype: 'actioncolumn',
            // header: 'Store Native',
            hideable: true,
            hidden:true,
            width: 100,
            align: 'center',
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (rec.get('store_original_data')) {
                        return 'activated';
                    } else {
                        return 'deactivated';
                    }
                },
                getTip: function(v, meta, rec) {
                    if (rec.get('store_original_data')) {
                        return esapp.Utils.getTranslation('tipdeactivatestoreoriginalget');     // 'Deactivate store original data for this Get';
                    } else {
                        return esapp.Utils.getTranslation('tipactivatestoreoriginalget');     // 'Activate store original data for this Get';
                    }
                },
                handler: function(grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('store_original_data') ? 'deactivated' : 'activated');
                    // Ext.toast({ html: action + ' ' + rec.get('productcode'), title: 'Action', width: 300, align: 't' });
                    rec.get('store_original_data') ? rec.set('store_original_data', false) : rec.set('store_original_data', true);
                }
            }]
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
                        return esapp.Utils.getTranslation('tipdeactivateget');     // 'Deactivate Get';
                    } else {
                        return esapp.Utils.getTranslation('tipactivateget');     // 'Activate Get';
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
            height:40,
            align:'center',
            items: [{
                //icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                iconCls:'log-icon',
                width:32,
                height:32,
                tooltip: esapp.Utils.getTranslation('showgetlog'),     // 'Show log of this Get',
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
