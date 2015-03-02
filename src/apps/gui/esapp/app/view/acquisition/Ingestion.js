
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

        'Ext.grid.plugin.CellEditing',
        'Ext.grid.column.Action',
        'Ext.grid.column.Widget',
        'Ext.grid.column.Check'
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
    rowLines:false,
    //frame: false,
    //border: false,

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
            //margin:0,
            //bodyPadding:0,
            widget: {
                xtype: 'datasetchart',
                height:30
            },
            onWidgetAttach: function(widget, record) {

                var widgetchart = widget.down('cartesian');
                var completeness = record.getAssociatedData().completeness;

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
                    widgetchart.surfaceMap.chart[0].getItems()[1].setText('Missing: '+completeness.missingfiles);
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

//                var data = Ext.util.JSON.decode(completeness);
            }

        },{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden: false,
            // disabled: true,
            // stopSelection: false,
            width: 65,
            align: 'center',
            items: [{
                // scope: me,
                // handler: me.onToggleActivation
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
                        return 'Deactivate Ingestion';
                    } else {
                        return 'Activate Ingestion';
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
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
            items: [{
                icon: 'resources/img/icons/file-extension-log-icon-32x32.png',
                tooltip: 'Show log of this Ingestion',
                scope: me,
                // handler: me.onRemoveClick
                handler: function (grid, rowIndex, colIndex, icon) {
                    var rec = grid.getStore().getAt(rowIndex);
                    var logViewWin = new esapp.view.acquisition.logviewer.LogView({
                        params: {
                            logtype: 'ingest',
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
