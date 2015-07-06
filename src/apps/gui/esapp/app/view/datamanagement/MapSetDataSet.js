
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
                height:30
            },
            onWidgetAttach: function(widget, record) {
                // console.info(record.getAssociatedData()); // get all associated data, including deep nested
                // console.info(record);
                // console.info(record.getData().datasetcompleteness); // get completeness model!
                var widgetchart = widget.down('cartesian');
                var completeness = record.getData().datasetcompleteness;

                var storefields = ['dataset'];
                var series_yField = [];
                for (var index = 1; index <= completeness.intervals.length; ++index) {
                    storefields.push('data'+index);
                    series_yField.push('data'+index);
                }

                var datasetdata = [];
                var dataObj = {dataset: ''};
                var seriestitles = [];
                var seriestitle = '';
                var seriescolors = [];
                var i = 1;

                if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
                    dataObj["data1"] = '100'; // 100%
                    datasetdata.push(dataObj);
                    seriestitle = '<span style="color:#808080">Not any data</span>';
                    seriestitles.push(seriestitle);
                    seriescolors.push('#808080'); // gray

                    // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                    widgetchart.surfaceMap.chart[0].getItems()[0].setText('Not any data');
                    widgetchart.surfaceMap.chart[0].getItems()[1].setText('');
                    widgetchart.surfaceMap.chart[0].getItems()[2].setText('');
                    widgetchart.surfaceMap.chart[0].getItems()[3].setText('');
                }
                else {
                    completeness.intervals.forEach(function (interval) {
                        if (interval.intervalpercentage<1.5)
                            dataObj["data" + i] = 2;
                        else
                            dataObj["data" + i] = interval.intervalpercentage;
                        ++i;

                        var color = '';
                        if (interval.intervaltype == 'present')
                            color = '#81AF34'; // green
                        if (interval.intervaltype == 'missing')
                            color = '#FF0000'; // red
                        if (interval.intervaltype == 'permanent-missing')
                            color = '#808080'; // gray
                        seriescolors.push(color);

                        seriestitle = '<span style="color:'+color+'">From ' + interval.fromdate + ' to ' + interval.todate + ' - ' + interval.intervaltype + '</span>';
                        seriestitles.push(seriestitle);
                    });
                    datasetdata.push(dataObj);

                    // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                    widgetchart.surfaceMap.chart[0].getItems()[0].setText('Files: '+completeness.totfiles);
                    var missingFilesText = '';
                    if(completeness.missingfiles>0)
                       missingFilesText = 'Missing: ' + completeness.missingfiles;
                    widgetchart.surfaceMap.chart[0].getItems()[1].setText(missingFilesText);
                    widgetchart.surfaceMap.chart[0].getItems()[2].setText(completeness.firstdate);
                    widgetchart.surfaceMap.chart[0].getItems()[3].setText(completeness.lastdate);
                }

                var newstore = Ext.create('Ext.data.JsonStore', {
                    fields: storefields,
                    data: datasetdata
                });

                widgetchart.setStore(newstore);

                var widgetchartaxis = widgetchart.getAxes();
                widgetchartaxis[0].setFields(series_yField);

                var widgetchartseries = widgetchart.getSeries();
                widgetchartseries[0].setColors(seriescolors);
                widgetchartseries[0].setYField(series_yField);

                // update legendStore with new series, otherwise setTitles,
                // which updates also the legend names will go in error.
                widgetchart.refreshLegendStore();
                widgetchartseries[0].setTitle(seriestitles);
                widgetchart.redraw();
            }
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: 'Complete data set',
                scope: me,
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