
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
                tooltip: 'Complete all data sets for this product\'s mapset',
                scope: me,
                handler: function (grid, rowIndex) {
                    Ext.toast({
                        html: 'Show window which proposes places to send a request to complete all data sets for this product\'s mapset',
                        title: 'Request to complete all data sets for this product\'s mapset',
                        width: 200,
                        align: 't'
                    });
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