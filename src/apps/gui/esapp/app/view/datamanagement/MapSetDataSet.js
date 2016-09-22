
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

        'esapp.view.widgets.datasetCompletenessChart',

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
                height:40,
                widgetattached: false
            },
            onWidgetAttach: function(col, widget, record) {
                //console.info('DM - completeness widget.widgetattached');
                //console.info(widget.widgetattached);

                var widgetchart = widget.down('cartesian');
                if (!widget.widgetattached) {
                    //console.info('DM - create completeness widget');
                    // console.info(record.getAssociatedData()); // get all associated data, including deep nested
                    var completeness = record.getData().datasetcompleteness;  // get completeness model!
                    var storefields = ['dataset'];
                    var series_yField = [];
                    var datasetdata = [];
                    var dataObj = {dataset: ''};
                    var seriestitles = [];
                    var seriestitle = '';
                    var seriescolors = [];
                    var i = 1;

                    var datasetForTipText = '<b>' + 'Data set intervals for' + ':</br>' +
                        record.get('productcode') + ' - ' +
                        record.get('version') + ' - ' +
                        record.get('mapset_descriptive_name') + ' - ' +
                        record.get('subproductcode') + '</b></br></br>';


                    if (record.get('nodisplay') == 'no_minutes_display' || record.getData().frequency_id=='singlefile'){
                        storefields.push('data1');
                        series_yField.push('data1');
                    }
                    else {
                        for (var index = 1; index <= completeness.intervals.length; ++index) {
                            storefields.push('data' + index);
                            series_yField.push('data' + index);
                        }
                    }

                    seriestitles.push(datasetForTipText);

                    widget.spriteXposition = 100;
                    if (record.get('nodisplay')  == 'no_minutes_display'){
                        dataObj["data1"] = '100'; // 100%
                        datasetdata.push(dataObj);
                        seriestitle = '<span style="color:#f78b07">' + esapp.Utils.getTranslation('no_minutes_display') + '</span>';
                        seriestitles.push(seriestitle);
                        seriescolors.push('#f78b07'); // orange

                        // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                        widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('no_minutes_display'));
                        widgetchart.surfaceMap.chart[0].getItems()[1].setText('');
                        widgetchart.surfaceMap.chart[0].getItems()[2].setText('');
                        widgetchart.surfaceMap.chart[0].getItems()[3].setText('');
                        widget.spriteXposition = 30;
                    }
                    else if (record.getData().frequency_id=='singlefile' && completeness.totfiles == 1 && completeness.missingfiles == 0){

                        dataObj["data1"] = '100'; // 100%
                        datasetdata.push(dataObj);
                        seriestitle = '<span style="color:#81AF34">'+ esapp.Utils.getTranslation('singlefile') + '</span>';
                        seriestitles.push(seriestitle);
                        seriescolors.push('#81AF34'); // green

                        // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                        widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('files') + ': ' + completeness.totfiles);
                        var missingFilesText = '';
                        if(completeness.missingfiles>0)
                           missingFilesText = esapp.Utils.getTranslation('Missing') + ': ' + completeness.missingfiles;
                        widgetchart.surfaceMap.chart[0].getItems()[1].setText(missingFilesText);
                        widgetchart.surfaceMap.chart[0].getItems()[2].setText('');
                        widgetchart.surfaceMap.chart[0].getItems()[3].setText('');
                    }
                    else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
                        dataObj["data1"] = '100'; // 100%
                        datasetdata.push(dataObj);
                        seriestitle = '<span style="color:#808080">'+ esapp.Utils.getTranslation('notanydata') + '</span>';
                        seriestitles.push(seriestitle);
                        seriescolors.push('#808080'); // gray

                        // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                        widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('notanydata'));
                        widgetchart.surfaceMap.chart[0].getItems()[1].setText('');
                        widgetchart.surfaceMap.chart[0].getItems()[2].setText('');
                        widgetchart.surfaceMap.chart[0].getItems()[3].setText('');
                    }
                    else {
                        var tot_percentage = 0;
                        var biggest_intervalpercentage = 0;
                        var i_biggest = 1;
                        completeness.intervals.forEach(function (interval) {
                            interval.intervalpercentage = Math.floor(interval.intervalpercentage);
                            if (interval.intervalpercentage < 0) {
                                interval.intervalpercentage = interval.intervalpercentage * (-1);
                            }

                            if (interval.intervalpercentage > biggest_intervalpercentage) {
                                biggest_intervalpercentage = interval.intervalpercentage
                                i_biggest = i;
                            }
                            tot_percentage = tot_percentage + interval.intervalpercentage;
                            dataObj["data" + i] = interval.intervalpercentage;
                            ++i;

                            var color, intervaltype = '';
                            if (interval.intervaltype == 'present') {
                                color = '#81AF34'; // green
                                intervaltype = esapp.Utils.getTranslation('present');
                            }
                            if (interval.intervaltype == 'missing') {
                                color = '#FF0000'; // red
                                intervaltype = esapp.Utils.getTranslation('missing');
                            }
                            if (interval.intervaltype == 'permanent-missing') {
                                color = '#808080'; // gray
                                intervaltype = esapp.Utils.getTranslation('permanent-missing');
                            }
                            seriescolors.push(color);

                            seriestitle = '<span style="color:'+color+'">' + esapp.Utils.getTranslation('from') + ' ' + interval.fromdate + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.todate + ' - ' + intervaltype + '</span></br>';
                            seriestitles.push(seriestitle);
                        });
                        var fill_to_onehunderd = 100 - tot_percentage;
                        if (fill_to_onehunderd > 0) // add to last data to fill up to 100%
                            dataObj["data" + i_biggest] = dataObj["data" + i_biggest] + fill_to_onehunderd;
                        else {
                            dataObj["data" + i_biggest] = dataObj["data" + i_biggest] - (-fill_to_onehunderd);
                            dataObj["data" + i_biggest] = -dataObj["data" + i_biggest]>0 ? -dataObj["data" + i_biggest] : dataObj["data" + i_biggest];
                        }
                        datasetdata.push(dataObj);

                        // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                        widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('files') + ': ' + completeness.totfiles);
                        var missingFilesText = '';
                        if(completeness.missingfiles>0)
                           missingFilesText = esapp.Utils.getTranslation('Missing') + ': ' + completeness.missingfiles;
                        widgetchart.surfaceMap.chart[0].getItems()[1].setText(missingFilesText);
                        widgetchart.surfaceMap.chart[0].getItems()[2].setText(completeness.firstdate);
                        widgetchart.surfaceMap.chart[0].getItems()[3].setText(completeness.lastdate);
                        //if (completeness.lastdate.length < 6)
                        //    widgetchart.surfaceMap.chart[0].getItems()[3].attr.textAlign = "right";
                    }

                    widgetchart.surfaceMap.chart[0].getItems()[0].x = widget.spriteXposition;
                    widgetchart.surfaceMap.chart[0].getItems()[0].attr.x = widget.spriteXposition;

                    widget.tooltipintervals = seriestitles;

                    //if (!widget.widgetattached) {
                    //    widget.widgetattached = true;
                    //    var tip = Ext.create('Ext.tip.ToolTip', {
                    //        id: widget.getId() + '_tooltip',
                    //        target: widget.getId(),
                    //        disabled: true,
                    //        trackMouse: false,
                    //        autoHide: false,
                    //        dismissDelay: 5000, // auto hide after 5 seconds
                    //        closable: true,
                    //        anchor: 'left',
                    //        padding: 10,
                    //        html: widget.tooltipintervals, // Tip content
                    //        listeners: {
                    //            close: function() {
                    //                this.disable();
                    //            }
                    //        }
                    //    });
                    //}
                    //console.info(datasetdata);

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
                    //widgetchart.refreshLegendStore();
                    //widgetchart.redraw();
                    //widgetchartseries[0].setTitle(seriestitles);
                    //widget.setTooltipintervals(seriestitles);

                    widget.widgetattached = true;
                }

                //widgetchart.redraw();
                //me.updateLayout();
            }
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            menuDisabled: true,
            stopSelection: false,
            items: [{
                icon: 'resources/img/icons/download.png',
                tooltip: esapp.Utils.getTranslation('tipcompletedataset'),    // 'Complete data set',
                scope: me,
                handler: function (grid, rowIndex) {
                        var rec = grid.getStore().getAt(rowIndex);

                        var sendRequestWin = new esapp.view.datamanagement.sendRequest({
                            params: {
                                level: 'dataset',
                                record: rec
                            }
                        });
                        sendRequestWin.show();
                }
            }]
        }];

        me.callParent();
    }
});