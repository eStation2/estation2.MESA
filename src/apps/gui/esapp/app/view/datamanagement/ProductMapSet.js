
Ext.define("esapp.view.datamanagement.ProductMapSet",{
    "extend": "Ext.grid.Panel",

    //"controller": "datamanagement-productmapset",
    //
    //"viewModel": {
    //    "type": "datamanagement-productmapset"
    //},

    "xtype"  : 'productmapsetgrid',

    requires: [
        //'esapp.view.datamanagement.ProductMapSetModel',
        //'esapp.view.datamanagement.ProductMapSetController'

        ,'Ext.grid.column.Widget'
        ,'Ext.grid.column.Action'
    ],
    store : {
        model: 'ProductMapSet'
    },
    session: false,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },

    //layout: 'fit',

    //selType: 'cellmodel',
    //selModel: {listeners:{}},

    //listeners: {
    //    cellclick : function(view, cell, cellIndex, record, row, rowIndex, e) {
    //        //e.stopPropagation();
    //        return false;
    //    }
    //},

    bufferedRenderer: true,

    hideHeaders: true,
    columnLines: false,
    rowLines: false,
    minHeight: 60,

    //listeners: {
    //    beforerender:  function () {
    //        //console.info('ProductMapSet: beforerender event called');
    //        var me = this,
    //            record = me.getWidgetRecord();
    //        Ext.suspendLayouts();
    //        if (record.getData() != null && record.getData().hasOwnProperty('productmapsets')) {
    //            var productmapsets = record.getData().productmapsets;
    //            var newstore = Ext.create('Ext.data.JsonStore', {
    //                model: 'ProductMapSet',
    //                data: productmapsets
    //            });
    //            me.setStore(newstore);
    //        }
    //        Ext.resumeLayouts(true);
    //    }
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
            header: '', // 'Mapset',
            dataIndex: 'descriptive_name',
            width: 205
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            menuDisabled: true,
            stopSelection: false,
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: esapp.Utils.getTranslation('tipcompletedatasetmapset'),    // 'Complete all data sets for this product\'s mapset',
                scope: me,
                handler: function (grid, rowIndex) {
                    var rec = grid.getStore().getAt(rowIndex);

                    var sendRequestWin = new esapp.view.datamanagement.sendRequest({
                        params: {
                            level: 'mapset',
                            record: rec
                        }
                    });
                    sendRequestWin.show();
                }
            }]
        }, {
            header: '',
            xtype: 'widgetcolumn',
            width: 725,
            widget: {
                xtype: 'mapsetdatasetgrid',
                widgetattached: false
            },
            onWidgetAttach: function(col, widget, record) {
                Ext.suspendLayouts();
                if (!widget.widgetattached) {
                    widget.getStore().setData(record.getData().mapsetdatasets);
                    var sorters = widget.getStore().getSorters();
                    sorters.add('display_index');

                    widget.widgetattached = true;
                }
                Ext.resumeLayouts(true);

                //me.updateLayout();
                //var mapsetdatasets = record.getData().mapsetdatasets;
                //var newstore = Ext.create('Ext.data.JsonStore', {
                //    model: 'MapSetDataSet',
                //    data: mapsetdatasets
                //});
                //widget.setStore(newstore);

            }
        }];

        me.callParent();
    }

});