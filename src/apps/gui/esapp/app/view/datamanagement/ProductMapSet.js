
Ext.define("esapp.view.datamanagement.ProductMapSet",{
    "extend": "Ext.grid.Panel",

    "controller": "datamanagement-productmapset",

    "viewModel": {
        "type": "datamanagement-productmapset"
    },

    "xtype"  : 'productmapsetgrid',

    requires: [
        'esapp.view.datamanagement.ProductMapSetModel',
        'esapp.view.datamanagement.ProductMapSetController'

        ,'Ext.grid.column.Widget'
        ,'Ext.grid.column.Action'
    ],

    store : null,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },
    hideHeaders: true,
    columnLines: false,
    rowLines:false,
    bufferedRenderer: true,
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
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: esapp.Utils.getTranslation('tipcompletedatasetmapset'),    // 'Complete all data sets for this product\'s mapset',
                //scope: me,
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
                xtype: 'mapsetdatasetgrid'
                // ,height:80
            },
            onWidgetAttach: function(widget, record) {
                Ext.suspendLayouts();
                var mapsetdatasets = record.getData().mapsetdatasets;
                // console.info(mapsetdatasets);
                var newstore = Ext.create('Ext.data.JsonStore', {
                    model: 'MapSetDataSet',
                    data: mapsetdatasets
                });
                widget.setStore(newstore);
                Ext.resumeLayouts(true);
            }
        }];

        me.callParent();
    }

});