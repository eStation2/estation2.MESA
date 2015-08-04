
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
    bufferedRenderer: true,

    //listeners: {
    //    beforerender:  function () {
    //        var me = this,
    //            record = me.getWidgetRecord();
    //        Ext.suspendLayouts();
    //        var daStore = me.getViewModel().get('productingestions');
    //        if (daStore) {
    //            daStore.setFilters({
    //                property: 'productid'
    //                , value: record.id
    //                , anyMatch: true
    //            });
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
                height:50
            },
            onWidgetAttach: function(column, widget, record) {
                //widget.setId('dschart_' + record.get('productcode') + '_' + record.get('version').replace('.', '') + '_' + record.get('mapsetcode') + '_' + record.get('subproductcode'));

                var completeness = record.getAssociatedData().completeness;
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
