
Ext.define("esapp.view.datamanagement.MapSetDataSet",{
    "extend": "Ext.grid.Panel",

    "controller": "datamanagement-mapsetdataset",

    "viewModel": {
        "type": "datamanagement-mapsetdataset"
    },

    "xtype"  : 'mapsetdatasetgrid',

    requires: [
        'esapp.view.datamanagement.MapSetDataSetModel',
        'esapp.view.datamanagement.MapSetDataSetController',

        'Ext.grid.column.Action',
        'Ext.grid.column.Widget'
    ],

    store: null,

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

    listeners: {
        beforerender:  function () {
            //console.info('MapSetDataSet: beforerender event called');
            var me = this,
                record = me.getWidgetRecord();
            Ext.suspendLayouts();
            if (record.getData() != null && record.getData().hasOwnProperty('mapsetdatasets')) {
                var mapsetdatasets = record.getData().mapsetdatasets;
                var newstore = Ext.create('Ext.data.JsonStore', {
                    model: 'MapSetDataSet',
                    data: mapsetdatasets
                });
                me.setStore(newstore);
            }
            Ext.resumeLayouts(true);
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
            header: '', // 'Sub Product Code',
            dataIndex: 'subproductcode',
            width: 210
        }, {
            header: '', // 'Status',
            xtype: 'widgetcolumn',
            width: 360,
            widget: {
                xtype: 'datasetchart',
                height:50
            },
            onWidgetAttach: function(column, widget, record) {
                var completeness = record.getData().datasetcompleteness;
                //var completeness = record.getAssociatedData().completeness;

                var series = [];
                var serieObj = {color: '', data: []};
                var seriestitles = [];
                var seriestitle = '';

                if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
                    series = [{
                            color: '#808080', // gray
                            data: [100]
                        }];
                    widget.setSeries(series);
                    widget.setTotfiles(0);
                    seriestitle = '<span style="color:#808080">Not any data</span>';
                    widget.setTooltipintervals(seriestitle);
                }
                else {
                    completeness.intervals.forEach(function (interval) {
                        var data = 0;
                        if (interval.intervalpercentage<1.5)
                            data = 2;
                        else
                            data = interval.intervalpercentage;

                        var color = '';
                        if (interval.intervaltype == 'present')
                            color = '#81AF34'; // green
                        if (interval.intervaltype == 'missing')
                            color = '#FF0000'; // red
                        if (interval.intervaltype == 'permanent-missing')
                            color = '#808080'; // gray

                        serieObj = {color: color, data: [data]};

                        series.push(serieObj);
                        seriestitle = '<span style="color:'+color+'">From ' + interval.fromdate + ' to ' + interval.todate + ' - ' + interval.intervaltype + '</span></br>';
                        seriestitles.push(seriestitle);
                    });


                    widget.setSeries(series);
                    widget.setFirstdate(completeness.firstdate);
                    widget.setLastdate(completeness.lastdate);
                    widget.setTotfiles(completeness.totfiles);
                    widget.setTooltipintervals(seriestitles);
                    if(completeness.missingfiles>0)
                        widget.setMissingfiles(completeness.missingfiles);
                }

            }
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: 'Complete data set',
                //scope: me,
                handler: function (grid, rowIndex) {
                    Ext.toast({
                        html: 'Show window which proposes places to send a request to complete the selected data set',
                        title: 'Request to complete data set',
                        width: 200,
                        align: 't'
                    });
                }
            }]
        }];

        me.callParent();
    }
});