
Ext.define("esapp.view.widgets.datasetCompletenessChart",{
    "extend": "Ext.container.Container",
    //"controller": "widgets-datasetcompletenesschart",
    //"viewModel": {
    //    "type": "widgets-datasetcompletenesschart"
    //},
    requires: [
        //'esapp.view.widgets.datasetCompletenessChartModel',
        //'esapp.view.widgets.datasetCompletenessChartController',

        //'Ext.data.JsonStore',
        //'Ext.draw.engine.Svg',
        'Ext.chart.CartesianChart',
        'Ext.chart.axis.Numeric',
        'Ext.chart.axis.Category',
        'Ext.chart.series.Bar'
        //,'Ext.chart.interactions.ItemHighlight'
    ],

    xtype: 'datasetchart',

    //configs with auto generated getter/setter methods
    //config: {
    //    spriteY : 10,
    //    fontsize : 10,
    //    spriteXposition: 100,
    //    series_yField : [],
    //    seriescolors : [],
    //    totfiles: '',
    //    missingfiles: '',
    //    firstdate: '',
    //    lastdate: '',
    //    tooltipintervals: '',
    //    storefields : [],
    //    datasetdata : [],
    //},

    margin:0,
    bodyPadding:0,
    bufferedRenderer: true,

    width: '100%',
    height: 38,
    minWidth : 340,
    hidden: false
    // ,chart_ImageObj: new Image()

    //,constructor:function(config) {
    //    var me = this,
    //        spriteY = 10,
    //        fontsize = 10,
    //        spriteXposition = 100,
    //        series_yField = [],
    //        seriescolors = [],
    //        totfiles = '',
    //        missingfiles = '',
    //        firstdate = '',
    //        lastdate = '',
    //        tooltipintervals = '',
    //        storefields = [],
    //        datasetdata = [];
    //
    //    //me.listeners = {
    //    //    //element: 'el',
    //    //    //click: function() {
    //    //    //    var me = this;
    //    //    //    console.info(me.tooltipintervals);
    //    //    //    var widgettooltip = Ext.getCmp(me.getId() + '_tooltip');
    //    //    //    widgettooltip.enable();
    //    //    //    widgettooltip.show();
    //    //    //},
    //    //    afterrender: function () {
    //    //
    //    //        Ext.create('Ext.tip.ToolTip', {
    //    //            id: me.getId() + '_tooltip',
    //    //            target: me.getId(),
    //    //            //floating: true,
    //    //            //constrain: true,
    //    //            //constrainTo: me,
    //    //            //alwaysOnTop: false,
    //    //            //toFrontOnShow: false,
    //    //            maxHeight: 400,
    //    //            autoScroll: true,
    //    //            disabled: true,
    //    //            trackMouse: false,
    //    //            autoHide: false,
    //    //            dismissDelay: 5000, // auto hide after 5 seconds
    //    //            closable: true,
    //    //            anchorToTarget: true,
    //    //            anchor: 'left',
    //    //            padding: 10,
    //    //            html: me.tooltipintervals, // Tip content
    //    //            listeners: {
    //    //                close: function() {
    //    //                    this.disable();
    //    //                    // Ext.util.Observable.capture(this, function(e){console.log(this.id + ': ' + e);});
    //    //                }
    //    //            }
    //    //        });
    //    //
    //    //        this.getEl().on('click', function() {
    //    //            if (me.tooltipintervals != ''){
    //    //                var widgettooltip = Ext.getCmp(me.getId() + '_tooltip');
    //    //                widgettooltip.html = me.tooltipintervals;
    //    //                widgettooltip.enable();
    //    //                widgettooltip.show();
    //    //                //console.info(me);
    //    //                //me.down('cartesian').updateLayout({defer: true, isRoot: true});
    //    //                //me.down('cartesian').redraw();
    //    //            }
    //    //        });
    //    //    }
    //    //};
    //
    //
    //    me.initConfig(config);
    //
    //    me.callParent([config]);
    //}
    ,initComponent: function() {
        var me = this,
            spriteY = 10,
            fontsize = 10,
            spriteXposition = 100,
            series_yField = [],
            seriescolors = [],
            totfiles = '',
            missingfiles = '',
            firstdate = '',
            lastdate = '',
            //tooltipintervals =  '',
            storefields = [],
            datasetdata = [];

        me.tooltipintervals =  '';

        me.listeners = {
            afterrender: function(){

                me.tooltip =  Ext.create('Ext.tip.ToolTip', {
                    id: me.getId() + '_completness_tooltip',
                    target: me.getId(),
                    //floating: true,
                    //constrain: true,
                    //constrainTo: me,
                    //alwaysOnTop: false,
                    //toFrontOnShow: false,
                    maxHeight: 400,
                    autoScroll: true,
                    disabled: true,
                    trackMouse: false,
                    autoHide: false,
                    dismissDelay: 5000, // auto hide after 5 seconds
                    closable: true,
                    anchorToTarget: true,
                    anchor: 'left',
                    padding: 10,
                    html: me.tooltipintervals, // Tip content
                    listeners: {
                        close: function() {
                            this.disable();
                            // Ext.util.Observable.capture(this, function(e){console.log(this.id + ': ' + e);});
                        }
                    }
                });

                this.getEl().on('click', function() {
                    if (me.tooltipintervals != ''){
                        var widgettooltip = Ext.getCmp(me.getId() + '_tooltip');
                        widgettooltip.html = me.tooltipintervals;
                        widgettooltip.enable();
                        widgettooltip.show();
                        //console.info(me);
                        //me.down('cartesian').updateLayout({defer: true, isRoot: true});
                        //me.down('cartesian').redraw();
                    }
                });
            }
        }

        me.items = [{
            xtype: 'cartesian',
            width: '100%',
            height: 38,
            minWidth: 340,
            // suspendLayout: true,
            // saveDelay: 10,
            //listeners: {
            //    afterlayout: function () {
            //        //console.info(this);
            //        //console.info(this.getImage());
            //    }
            //},
            engine: Ext.draw.engine.Canvas,
            // engine: Ext.draw.engine.Svg,

            colors: [
                '#81AF34', // green
                '#FF0000', // red
                '#808080' // black or gray
            ],

            legend: {
                hidden:true
            },

            innerPadding: {top: 0, left: 0, right: 0, bottom: 0},
            insetPadding: {top: 12, left: 15, right: 15, bottom: 5},
            flipXY: true,

            //store: {
            //    fields: me.storefields,
            //    data: me.datasetdata
            //},

            store: Ext.create('Ext.data.JsonStore', {
                fields: storefields,
                data: datasetdata
            }),

            sprites:  [{
                type: 'text',
                text: totfiles,
                fontSize: fontsize+1,
                fontWeight: 'bold',
                x: me.spriteXposition,
                y: spriteY
            },{
                type: 'text',
                text: missingfiles,
                fontSize: fontsize+1,
                fontWeight: 'bold',
                fillStyle: '#FF0000',
                x: 190,
                y: spriteY
            },{
                type: 'text',
                text: me.firstdate,
                fontSize: me.fontsize,
                fontWeight: 'bold',
                x: 0,
                y: spriteY
            },{
                type: 'text',
                text: me.lastdate,
                fontSize: me.fontsize,
                fontWeight: 'bold',
                textAlign: 'middle',
                x: 286+22,
                y: spriteY
            }],

            axes: [{
                type: 'numeric',
                // fields: ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'],
                //fields: me.series_yField,
                grid: false,
                hidden:true
            }, {
                type: 'category',
                // fields: 'dataset',
                position: 'left',
                grid: false
            }],

            series: [{
                type: 'bar',
                // title: ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'],
                // title: me.seriestitles,
                xField: 'dataset',
                //yField: me.series_yField,
                axis: 'bottom',
                //colors: me.seriescolors,
                stacked: true,
                style: {
                    opacity: 0.80
                }
                //,highlight: {
                //    fillStyle: 'white' // 'transparent'
                //    ,strokeStyle: "black"
                //    ,opacity: 30
                //    ,segment: {
                //        margin: 5
                //    }
                //},
                //,tooltip: {
                //    trackMouse: false,
                //    dismissDelay:60000,
                //    style: 'background: #fff',
                //    renderer: function (storeItem, item) {
                //        var allperiods = '';
                //        var arrayLength = item.series.getTitle().length;
                //        var thisperiodindex = Ext.Array.indexOf(item.series.getYField(), item.field);
                //
                //        for (var i = 0; i < arrayLength; i++) {
                //            if (i == thisperiodindex) {
                //                allperiods = allperiods + '<b>'+item.series.getTitle()[thisperiodindex] + '</b></br>';
                //            }
                //            else {
                //                allperiods = allperiods + item.series.getTitle()[i] + '</br>';
                //            }
                //        }
                //
                //        this.setHtml(allperiods);
                //    }
                //}
            }]
        }];

        me.callParent();

    }

    ,drawCompletenessChart:function(data) {
        var me = this,
            index,
            //dataObj = {dataset: '100'},
            dataObj = {dataset: ''},
            seriestitle = '',
            seriestitles = [],
            i = 1,
            datasetForTipText = '',
            mapsetdatasetrecord = data,
            completeness = data.get('datasetcompleteness') || data.getAssociatedData().completeness,
            mychart = me.down(),

            spriteXposition = 100,
            series_yField = [],
            seriescolors = [],
            totfiles = '',
            missingfiles = '',
            firstdate = '',
            lastdate = '',
            //tooltipintervals =  '',
            storefields = [],
            datasetdata = [];

        datasetForTipText = '<b>' + esapp.Utils.getTranslation('dataset_intervals_for') + ':</br>' +
            mapsetdatasetrecord.get('productcode') + ' - ' +
            mapsetdatasetrecord.get('version') + ' - ' +
            (mapsetdatasetrecord.get('mapset_descriptive_name') || mapsetdatasetrecord.get('mapsetname')) + ' - ' +
            mapsetdatasetrecord.get('subproductcode') + '</b></br></br>';


        if (mapsetdatasetrecord.get('nodisplay') == 'no_minutes_display' || mapsetdatasetrecord.getData().frequency_id=='singlefile'){
            storefields.push('data1');
            series_yField.push('data1');
        }
        else {
            for (index = 1; index <= completeness.intervals.length; ++index) {
                storefields.push('data' + index);
                series_yField.push('data' + index);
            }
        }

        seriestitles.push(datasetForTipText);

        me.spriteXposition = 100;
        if (mapsetdatasetrecord.get('nodisplay')  == 'no_minutes_display'){
            dataObj["data1"] = '100'; // 100%
            datasetdata.push(dataObj);
            seriestitle = '<span style="color:#f78b07">' + esapp.Utils.getTranslation('no_minutes_display') + '</span>';
            seriestitles.push(seriestitle);
            seriescolors.push('#f78b07'); // orange

            // Update the 4 sprites (these are not reachable through getSprites() on the chart)
            totfiles = esapp.Utils.getTranslation('no_minutes_display');
            missingfiles = '';
            firstdate = '';
            lastdate = '';
            spriteXposition = 30;
        }
        else if (mapsetdatasetrecord.getData().frequency_id=='singlefile' && completeness.totfiles == 1 && completeness.missingfiles == 0){

            dataObj["data1"] = '100'; // 100%
            datasetdata.push(dataObj);
            seriestitle = '<span style="color:#81AF34">'+ esapp.Utils.getTranslation('singlefile') + '</span>';
            seriestitles.push(seriestitle);
            seriescolors.push('#81AF34'); // green

            // Update the 4 sprites (these are not reachable through getSprites() on the chart)
            totfiles = esapp.Utils.getTranslation('files') + ': ' + completeness.totfiles;
            if(completeness.missingfiles>0)
                missingfiles = esapp.Utils.getTranslation('Missing') + ': ' + completeness.missingfiles;
            firstdate = '';
            lastdate = '';
        }
        else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
            dataObj["data1"] = '100'; // 100%
            datasetdata.push(dataObj);
            seriestitle = '<span style="color:#808080">'+ esapp.Utils.getTranslation('notanydata') + '</span>';
            seriestitles.push(seriestitle);
            seriescolors.push('#808080'); // gray

            // Update the 4 sprites (these are not reachable through getSprites() on the chart)
            totfiles = esapp.Utils.getTranslation('notanydata');
            missingfiles = '';
            firstdate = '';
            lastdate = '';
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
                //dataObj["data" + i_biggest] = dataObj["data" + i_biggest] + fill_to_onehunderd;
                dataObj["data" + (i - 1)] = dataObj["data" + (i - 1)] + fill_to_onehunderd;
            else {
                dataObj["data" + i_biggest] = dataObj["data" + i_biggest] - (-fill_to_onehunderd);
                dataObj["data" + i_biggest] = -dataObj["data" + i_biggest]>0 ? -dataObj["data" + i_biggest] : dataObj["data" + i_biggest];
            }
            datasetdata.push(dataObj);

            // Update the 4 sprites (these are not reachable through getSprites() on the chart)
            totfiles = esapp.Utils.getTranslation('files') + ': ' + completeness.totfiles;
            if(completeness.missingfiles>0)
                missingfiles = esapp.Utils.getTranslation('Missing') + ': ' + completeness.missingfiles;
            firstdate = completeness.firstdate;
            lastdate = completeness.lastdate;
        }

        if (firstdate.length>10){
            firstdate = firstdate.slice(0, -5);
        }
        if (lastdate.length>10){
            lastdate = lastdate.slice(0, -5);
        }
        me.tooltipintervals = seriestitles;


        // Update the 4 sprites (these are not reachable through getSprites() on the chart)
        mychart.surfaceMap.chart[0].getItems()[0].setText(totfiles);
        mychart.surfaceMap.chart[0].getItems()[1].setText(missingfiles);
        mychart.surfaceMap.chart[0].getItems()[2].setText(firstdate);
        mychart.surfaceMap.chart[0].getItems()[3].setText(lastdate);

        mychart.surfaceMap.chart[0].getItems()[0].x = spriteXposition;
        mychart.surfaceMap.chart[0].getItems()[0].attr.x = spriteXposition;

        mychart.getStore().setFields(storefields);
        mychart.getStore().setData(datasetdata);

        var widgetchartaxis = mychart.getAxes();
        widgetchartaxis[0].setFields(series_yField);

        var widgetchartseries = mychart.getSeries();
        widgetchartseries[0].setColors(seriescolors);
        widgetchartseries[0].setYField(series_yField);

        //console.info(me);
        //me.initConfig(me);
        //me.show();
        //mychart.redraw();
    }
});
