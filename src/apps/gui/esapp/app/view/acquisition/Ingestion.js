
Ext.define("esapp.view.acquisition.Ingestion",{
    "extend": "Ext.grid.Panel",

    "controller": "ingestion",

    "viewModel": {
        "type": "ingestion"
    },

    "xtype"  : 'ingestiongrid',

    requires: [
        'esapp.view.acquisition.IngestionModel',
        'esapp.view.acquisition.IngestionController',
        'esapp.view.acquisition.logviewer.LogView',

        'esapp.view.widgets.datasetCompletenessChart',

        'Ext.grid.column.Action',
        'Ext.grid.column.Widget'
        //'Ext.grid.column.Check'
    ],

    //mixins: [],
    //events: ['my_event_name'],
    //register handler for 'my_event_name' event
    //    component.on('my_event_name', function(cmp, btn) {
    //            alert(this.getString()); // invoke miixin  method
    //        }, frm);
    //    store: 'IngestionsStore',
    //    bind: '{ProductAcquisitionsGrid.selection.Ingestions}',
    //    bind: '{ingestions}',

    bind:{
        store:'{productingestions}'
    },
    //session: true,

    viewConfig: {
        stripeRows: false,
        enableTextSelection: true,
        draggable: false,
        markDirty: false,
        resizable: false,
        disableSelection: true,
        trackOver: false
    },
    cls: 'grid-color-azur',

    hideHeaders: true,
    columnLines: false,
    rowLines:false,

    //bufferedRenderer: true,
    //autoHeight: false,
    //plugins: [{
    //    ptype: 'bufferedrenderer',
    //    trailingBufferZone: 20,  // Keep 20 rows rendered in the table behind scroll
    //    leadingBufferZone: 50   // Keep 50 rows rendered in the table ahead of scroll
    //}],

    //listeners: {
        //rowclick:  function (gridview, record) {
            //console.info('row clicked');
            //console.info(gridview);
            //console.info(gridview.grid.getWidgetColumn());
            //console.info(Ext.getCmp(gridview.grid.getWidgetColumn().getWidget().getId()+ '_tooltip'));
        //}
        //beforerender:  function () {
        //    var me = this,
        //        record = me.getWidgetRecord();
        //    Ext.suspendLayouts();
        //    var daStore = me.getViewModel().get('productingestions');
        //    if (daStore) {
        //        daStore.setFilters({
        //            property: 'productid'
        //            , value: record.id
        //            , anyMatch: true
        //        });
        //    }
        //    Ext.resumeLayouts(true);
        //}
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
            dataIndex: 'mapsetname',
            //bind: '{ingestions.mapset}',
            width: 160
        }, {
            header: '', // 'Sub Product Code',
            dataIndex: 'subproductcode',
            //bind: '{ingestions.subproductcode}',
            width: 90
        }, {
            header: '', // 'Completeness',
            xtype: 'widgetcolumn',
            //dataIndex: 'completeness',
            //bind: '{ingestions.completeness}',
            width: 360,
            variableRowHeight:true,
            widget: {
                xtype: 'datasetchart',
                height:40,
                widgetattached: false
            },
            onWidgetAttach: function(widget, record) {
                var widgetchart = widget.down('cartesian');
                var completeness = record.getAssociatedData().completeness;

                var storefields = ['dataset'];
                var series_yField = [];
                if (record.get('nodisplay') == 'no_minutes_display'){
                    storefields.push('data1');
                    series_yField.push('data1');
                }
                else {
                    for (var index = 1; index <= completeness.intervals.length; ++index) {
                        storefields.push('data' + index);
                        series_yField.push('data' + index);
                    }
                }

                var datasetdata = [];
                var dataObj = {dataset: ''};
                var seriestitles = [];
                var seriestitle = '';
                var seriescolors = [];
                var i = 1;

                var ingestionForTipText = '<b>' + 'Data set intervals for' + ':</br>' +
                    record.get('productcode') + ' - ' +
                    record.get('version') + ' - ' +
                    record.get('mapsetname') + ' - ' +
                    record.get('subproductcode') + '</b></br></br>';

                seriestitles.push(ingestionForTipText);

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
                }
                else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
                    dataObj["data1"] = '100'; // 100%
                    datasetdata.push(dataObj);
                    seriestitle = '<span style="color:#808080">' + esapp.Utils.getTranslation('notanydata') + '</span>';
                    seriestitles.push(seriestitle);
                    seriescolors.push('#808080'); // gray

                    // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                    widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('notanydata'));
                    widgetchart.surfaceMap.chart[0].getItems()[1].setText('');
                    widgetchart.surfaceMap.chart[0].getItems()[2].setText('');
                    widgetchart.surfaceMap.chart[0].getItems()[3].setText('');
                }
                else {
                    completeness.intervals.forEach(function (interval) {
                        if (interval.intervalpercentage < 1.5)
                            dataObj["data" + i] = 2;
                        else
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

                        seriestitle = '<span style="color:' + color + '">' + esapp.Utils.getTranslation('from') + ' ' + interval.fromdate + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.todate + ' - ' + intervaltype + '</span></br>';
                        seriestitles.push(seriestitle);
                    });
                    datasetdata.push(dataObj);

                    // Update the 4 sprites (these are not reachable through getSprites() on the chart)
                    widgetchart.surfaceMap.chart[0].getItems()[0].setText(esapp.Utils.getTranslation('files') + ': ' + completeness.totfiles);
                    var missingFilesText = '';
                    if (completeness.missingfiles > 0)
                        missingFilesText = esapp.Utils.getTranslation('Missing') + ': ' + completeness.missingfiles;
                    widgetchart.surfaceMap.chart[0].getItems()[1].setText(missingFilesText);
                    widgetchart.surfaceMap.chart[0].getItems()[2].setText(completeness.firstdate);
                    widgetchart.surfaceMap.chart[0].getItems()[3].setText(completeness.lastdate);
                }

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
                widgetchart.redraw();
                //widgetchartseries[0].setTitle(seriestitles);
                //widget.setTooltipintervals(seriestitles);
            }

        },{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden: false,
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
                        return esapp.Utils.getTranslation('deactivateingestion');   // 'Deactivate Ingestion';
                    } else {
                        return esapp.Utils.getTranslation('activateingestion');   // 'Activate Ingestion';
                    }
                },
                handler: function(grid, rowIndex, colIndex) {
                    var rec = grid.getStore().getAt(rowIndex),
                        action = (rec.get('activated') ? 'deactivated' : 'activated');
                    //Ext.toast({ html: action + ' ' + rec.get('productcode') + ' ' + rec.get('mapsetcode') + ' ' + rec.get('subproductcode'), title: 'Action', width: 300, align: 't' });
                    rec.get('activated') ? rec.set('activated', false) : rec.set('activated', true);
                }
            }]

//            header: '', // 'Active',
//            xtype: 'checkcolumn',
//            dataIndex: 'activated',
////            bind: '{ingestions.activated}',
//            width: 65,
//            disabled: true,
//            stopSelection: false
//        },{
//            xtype: 'actioncolumn',
//            width: 65,
//            height:40,
//            align:'center',
//            items: [{
//                //icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
//                iconCls:'log-icon',
//                width:32,
//                height:32,
//                tooltip: 'Show log of this Ingestion',
//                scope: me,
//                // handler: me.onRemoveClick
//                handler: function (grid, rowIndex, colIndex, icon) {
//                    //console.info(grid.up());
//                    var rec = grid.getStore().getAt(rowIndex);
//                    var logViewWin = new esapp.view.acquisition.logviewer.LogView({
//                        params: {
//                            logtype: 'ingest',
//                            record: rec
//                        }
//                    });
//                    logViewWin.show();
//                }
//            }]
        }];

        me.callParent();
    }

});
