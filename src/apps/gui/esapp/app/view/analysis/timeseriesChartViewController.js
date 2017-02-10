Ext.define('esapp.view.analysis.timeseriesChartViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartview',

    getTimeseries: function(callback){
        var me = this.getView();
        //var chartpropertiesStore = this.getStore('chartproperties');

        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('generatingtimeseries'), // 'Generating requested time series...',
            target : Ext.getCmp('tschart_'+me.id)
            ,toFrontOnShow: true
            ,useTargetEl:true
        });
        myLoadMask.show();

        //console.info(me.yearsToCompare);
        var selectedYears = me.yearsToCompare;
        if (me.yearsToCompare != '')
            selectedYears = Ext.util.JSON.encode(me.yearsToCompare);

        Ext.Ajax.request({
            url:"analysis/gettimeseries",
            timeout : 300000,
            scope: me,
            params:{
                charttype: me.charttype,
                selectedTimeseries: me.selectedTimeseries,
                yearTS: me.yearTS,
                tsFromPeriod: Ext.Date.format(me.tsFromPeriod, 'Y-m-d'),
                tsToPeriod: Ext.Date.format(me.tsToPeriod, 'Y-m-d'),
                yearsToCompare: selectedYears,
                tsFromSeason: Ext.Date.format(me.tsFromSeason, 'm-d'),
                tsToSeason: Ext.Date.format(me.tsToSeason, 'm-d'),
                WKT:me.wkt
            },
            method: 'POST',
            success: function ( result, request ) {
                myLoadMask.hide();
                me.timeseriesGraph = Ext.util.JSON.decode(result.responseText);
                callback(me);
                //chartpropertiesStore.load({
                //    params: {
                //        charttype: me.charttype
                //    },
                //    callback:function(){
                //        me.getController().setChartDrawProperties(callback);
                //
                //        callback(me);
                //    }
                //});
            },
            failure: function ( result, request) {
               myLoadMask.hide();
            }
        });
    },

    setDefaultChartDrawProperties: function() {
        var me = this.getView();
        var chartpropertiesStore = this.getStore('chartproperties');
        me.timeseriesChart = {};
        me.timeseriesChart.localRefresh = false;

        me.timeseriesChart.title = Ext.getCmp('selectedregionname').getValue();
        me.timeseriesChart.subtitle = '';
        //if (Ext.isObject(Ext.getCmp('radio-year')) &&  Ext.getCmp('radio-year').getValue() && me.yearTS != '') {
        if (me.yearTS != '') {
            me.timeseriesChart.subtitle = me.yearTS;
        }
        //else if (Ext.getCmp('radio-compareyears').getValue() && me.yearsToCompare != '') {
        else if (me.yearsToCompare != '') {
            //me.yearsToCompare = Ext.util.JSON.decode(me.yearsToCompare);
            if (me.yearsToCompare.length == 1){
                me.yearsToCompare.forEach(function(year){
                    me.timeseriesChart.subtitle = year;
                })
                if ( me.tsFromSeason != null && me.tsToSeason != null){
                    me.timeseriesChart.subtitle = 'Season ' +  Ext.Date.format(me.tsFromSeason, 'm/d') + ' - ' + Ext.Date.format(me.tsToSeason, 'm/d') + ' of ' + me.timeseriesChart.subtitle;
                }
            }
        }
        //else if ( Ext.getCmp('radio-fromto').getValue() ){
        else if ( me.tsFromPeriod != '' && me.tsToPeriod != ''){

            me.timeseriesChart.subtitle = esapp.Utils.getTranslation('from') + ' ' + Ext.Date.format(me.tsFromPeriod, 'Y-m-d') + '  ' + esapp.Utils.getTranslation('to') + ' ' + Ext.Date.format(me.tsToPeriod, 'Y-m-d');
        }
        else if ( me.tsFromSeason != null && me.tsToSeason != null){
            me.timeseriesChart.subtitle = 'Season ' +  Ext.Date.format(me.tsFromSeason, 'm/d') + ' - ' + Ext.Date.format(me.tsToSeason, 'm/d');
        }


        me.timeseriesChart.filename = me.timeseriesChart.title + '_' + me.timeseriesChart.subtitle.toString().replace(' ', '_');

        chartpropertiesStore.each(function(chartproperties) {   // Should always be 1 record!!
            me.timeseriesChart.chart_title_font_size = chartproperties.get('chart_title_font_size');
            me.timeseriesChart.chart_title_font_color = esapp.Utils.convertRGBtoHex(chartproperties.get('chart_title_font_color'));

            me.timeseriesChart.chart_subtitle_font_size = chartproperties.get('chart_subtitle_font_size');
            me.timeseriesChart.chart_subtitle_font_color = esapp.Utils.convertRGBtoHex(chartproperties.get('chart_subtitle_font_color'));

            me.timeseriesChart.xaxe_font_size = chartproperties.get('xaxe_font_size');
            me.timeseriesChart.xaxe_font_color = esapp.Utils.convertRGBtoHex(chartproperties.get('xaxe_font_color'));

            me.timeseriesChart.yaxe1_font_size = chartproperties.get('yaxe1_font_size');
            me.timeseriesChart.yaxe2_font_size = chartproperties.get('yaxe2_font_size');
            me.timeseriesChart.yaxe3_font_size = chartproperties.get('yaxe3_font_size');

            //for (var yaxescount = 0; yaxescount < me.timeseriesChart.yaxes.length; yaxescount++) {
            //    if (yaxescount == 0) me.timeseriesChart.yaxes[yaxescount].yaxe_title_font_size = chartproperties.get('yaxe1_font_size');
            //    if (yaxescount == 1) me.timeseriesChart.yaxes[yaxescount].yaxe_title_font_size = chartproperties.get('yaxe2_font_size');
            //    //if (yaxescount == 2) me.timeseriesChart.yaxes[yaxescount].yaxe_title_font_size = chartproperties.get('yaxe3_font_size');
            //}

            me.timeseriesChart.legend_title_font_size = chartproperties.get('legend_font_size');
            me.timeseriesChart.legend_title_font_color = esapp.Utils.convertRGBtoHex(chartproperties.get('legend_font_color'));

            me.timeseriesChart.width = chartproperties.get('chart_width');
            me.timeseriesChart.height = chartproperties.get('chart_height');
        });

        //callback(me);
    },

    createDefaultChart: function(mecallback) {
        //var me = mecallback.getView();
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];
        //var categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        if (me.timeseriesGraph.data_available) {
            //var cats = me.timeseriesGraph.xaxis.categories;
            //for (var i = 0; i < cats.length; i++) {
            //    var year = cats[i].substring(0,4);
            //    var month = cats[i].substring(4,6);
            //    var day = cats[i].substring(6,8);
            //    categories[i] = Date.UTC(year, month-1, day); // Date.UTC(year, month-1, day);
            //}
        } else {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }

        var xAxisLabels = {};
        if (me.timeseriesGraph.showYearInTicks) {      //  === 'true'
            xAxisLabels = {
                enabled: 1,
                //autoRotation: [-3, -5],
                autoRotationLimit: -40,
                //step: 2,
                //autoRotation: [0,-90],
                y: 34,
                padding: 10,
                //useHTML: false,
                //reserveSpace: false,
                style: {
                    color: me.timeseriesChart.xaxe_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    //fontSize: me.timeseriesChart.xaxe_font_size-6,
                    "fontSize": me.timeseriesChart.xaxe_font_size + 'px'
                    ,margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value) + '<br/>' + Highcharts.dateFormat('\'%y', this.value);
                }
            };
        } else {
            xAxisLabels = {
                enabled: 1,
                y: 34,
                //step: 3,
                style: {
                    color: me.timeseriesChart.xaxe_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.xaxe_font_size + 'px',
                    margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value);
                }
            };
        }

        var xAxis = [];
        if (me.yearsToCompare != '' && me.yearsToCompare.length > 1) {
            var xAxe = {};
            var xaxeVisible = true;
            var minPeriod =  '/01/01';    //      Ext.Date.format(me.tsFromSeason, 'm-d');
            var maxPeriod = '/12/31';     //      Ext.Date.format(me.tsToSeason, 'm-d');

            me.yearsToCompare.forEach(function(year){
                if (me.tsFromSeason != null && me.tsToSeason != null){
                    minPeriod = new Date(year + Ext.Date.format(me.tsFromSeason, '/m/d')).getTime();
                    maxPeriod = new Date(year + Ext.Date.format(me.tsToSeason, '/m/d')).getTime();
                    if (Ext.Date.format(me.tsToSeason, 'm') < Ext.Date.format(me.tsFromSeason, 'm')){
                        maxPeriod = new Date(year+1 + Ext.Date.format(me.tsToSeason, '/m/d')).getTime();
                    }
                }
                else {
                    minPeriod = new Date(year + '/01/01').getTime();
                    maxPeriod = new Date(year + '/12/31').getTime();
                }

                xAxe = {
                    id: year.toString(),
                    visible: xaxeVisible,
                    type: 'datetime',
                    startOnTick: false,
                    endOnTick: true,
                    //offset: 25,
                    lineWidth: 2,
                    labels: xAxisLabels,
                    tickInterval: 30 * 24 * 3600 * 1000,
                    min: minPeriod,
                    max: maxPeriod
                };
                xaxeVisible = false;
                xAxis.push(xAxe);
            })
            //console.info(xAxis);
        }
        else {
            xAxis = [{
                type: 'datetime',
                //tickmarkPlacement: 'on',      // on between  - For categorized axes only!
                startOnTick: false,
                lineWidth: 2,
                labels: xAxisLabels,
                tickInterval: 30 * 24 * 3600 * 1000

                //labels: {
                //    enabled: 1,
                //    y:28,
                //    //step: 1,
                //    style: xaxis_labelstyle,
                //    formatter: function() {
                //        return Highcharts.dateFormat('%b', this.value);
                //    }
                //}
                //,minorTickInterval: 3
                //dateTimeLabelFormats: {
                //    day: '%e %b'
                //},
                //categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            }]
        }

        if (me.charttype == 'cumulative' && !me.timeseriesChart.localRefresh) {
            var TimeseriesCumulatedAverages = null;
            var TimeseriesCumulatedData = null;
            var aboveAvgColor = '#0000ff';
            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                //if (timeserie.cumulative) {
                    //me.timeseriesGraph.cumulative = true;
                    timeserie.type = 'line';
                    timeserie.dashStyle = 'Solid';
                    timeserie.lineWidth = 2;

                    var cumulated = 0;
                    timeserie.data.forEach(function (datarecord) {
                        datarecord[1] += cumulated;
                        cumulated = datarecord[1];
                    })

                    //TimeseriesCumulatedData = Ext.clone(timeserie.data);
                    //aboveAvgColor = timeserie.color;
                    //
                    //me.timeseriesGraph.timeseries.forEach(function (AVGtimeserie) {
                    //    if (AVGtimeserie.cumulative && AVGtimeserie.yAxis == timeserie.yAxis && AVGtimeserie.average == true) {
                    //        AVGtimeserie.type = 'line';
                    //        AVGtimeserie.dashStyle = 'Solid';
                    //        AVGtimeserie.lineWidth = 1;
                    //        var cumulated = 0;
                    //        AVGtimeserie.data.forEach(function (datarecord) {
                    //            datarecord[1] += cumulated;
                    //            cumulated = datarecord[1];
                    //        })
                    //        TimeseriesCumulatedAverages = Ext.clone(AVGtimeserie.data);
                    //    }
                    //});

                    if (timeserie.difference == true) {
                        TimeseriesCumulatedAverages = Ext.clone(timeserie.data);
                    }
                    else if (timeserie.reference == true){
                        //console.info(timeserie);
                        TimeseriesCumulatedData = Ext.clone(timeserie.data);
                        aboveAvgColor = timeserie.color;
                    }
                //}
            });


            if (TimeseriesCumulatedData != null && TimeseriesCumulatedAverages != null) {
                var i = 0, cumulatedPositive = [], cumulatedNegative = [], cumulatedMinValue = [], newDataValue = [];

                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedData[i]);
                    newDataValue[1] = TimeseriesCumulatedAverages[i][1] - TimeseriesCumulatedData[i][1];
                    if (newDataValue[1] > 0) newDataValue[1] = 0;
                    else newDataValue[1] = newDataValue[1] * -1;
                    cumulatedPositive.push(newDataValue);
                    //newDataValue = [];
                }
                //console.info(aboveAvgColor);
                aboveAvgColor = esapp.Utils.convertRGBtoHex(aboveAvgColor);
                var aboveAvg = {
                    data: cumulatedPositive,
                    fillColor: aboveAvgColor,
                    color: aboveAvgColor,
                    id: "Above",
                    name: "Above",
                    type: "area",
                    showInLegend: true,
                    enableMouseTracking: false
                }

                //newDataValue = [];
                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedData[i]);
                    newDataValue[1] = TimeseriesCumulatedAverages[i][1] - TimeseriesCumulatedData[i][1];
                    if (newDataValue[1] < 0) newDataValue[1] = 0;
                    cumulatedNegative.push(newDataValue);
                    //newDataValue = [];
                }

                var belowAvg = {
                    data: cumulatedNegative,
                    fillColor: "#ff0000",
                    color: "#ff0000",
                    id: "Below",
                    name: "Below",
                    type: "area",
                    showInLegend: true,
                    enableMouseTracking: false
                }

                //newDataValue = [];
                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedAverages[i]);
                    if (TimeseriesCumulatedData[i][1] < TimeseriesCumulatedAverages[i][1]) {
                        newDataValue = TimeseriesCumulatedData[i];
                    }
                    cumulatedMinValue.push(newDataValue);
                    //newDataValue = [];
                }
                //console.info(cumulatedMinValue);

                var transparentAvg = {
                    data: cumulatedMinValue,
                    fillColor: "rgba(255,255,255,0)",
                    color: "#ffffff",
                    id: "Cum transparent",
                    name: "Cum transparent",
                    type: "area",
                    showInLegend: false,
                    enableMouseTracking: false
                }

                me.timeseriesGraph.timeseries.push(aboveAvg);
                me.timeseriesGraph.timeseries.push(belowAvg);
                me.timeseriesGraph.timeseries.push(transparentAvg);
                //console.info(me.timeseriesGraph.timeseries);
            }
        }

        me.timeseriesGraph.timeseries.forEach(function (timeserie) {
            timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        });

        //for (var tscount = 0; tscount < me.timeseriesGraph.timeseries.length; tscount++) {
        //    var tscolor = me.timeseriesGraph.timeseries[tscount].color;
        //    var tstype = me.timeseriesGraph.timeseries[tscount].type;
        //    var tsname = me.timeseriesGraph.timeseries[tscount].name;
        //
        //    if (tsname.indexOf('transparent') == -1) { // Not a transparent timeseries
        //        if (tstype == 'area') {
        //            tscolor = me.timeseriesGraph.timeseries[tscount].fillColor;
        //        }
        //        tscolor = esapp.Utils.convertRGBtoHex(tscolor);
        //
        //        if (tstype == 'area') {
        //            me.timeseriesGraph.timeseries[tscount].fillColor = tscolor;
        //        }
        //        else {
        //            me.timeseriesGraph.timeseries[tscount].color = tscolor;
        //        }
        //
        //        //if (tscolor.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
        //        //    var rgbarr = [];
        //        //    if (esapp.Utils.is_array(tscolor)) {
        //        //        rgbarr = tscolor;
        //        //    }
        //        //    else {
        //        //        rgbarr = tscolor.split(" "); // toString().replace(/,/g,' ');
        //        //    }
        //        //
        //        //    var tsR = rgbarr[0];
        //        //    var tsG = rgbarr[1];
        //        //    var tsB = rgbarr[2];
        //        //    tscolor = esapp.Utils.RGBtoHex(tsR, tsG, tsB);
        //        //
        //        //    if (tstype == 'area') {
        //        //        me.timeseriesGraph.timeseries[tscount].fillColor = tscolor;
        //        //    }
        //        //    else {
        //        //        me.timeseriesGraph.timeseries[tscount].color = tscolor;
        //        //    }
        //        //}
        //    }
        //}

        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
                opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min == null || min == '' || min == 'null'){
                min = null
            }
            else {
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max == null || max == '' || max == 'null') {
                max = null
            }
            else {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }

            //if (me.timeseriesGraph.cumulative){
            //    min = null;
            //    max = null;
            //}

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            if (yaxescount == 0) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe1_font_size;
            if (yaxescount == 1) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe2_font_size;
            if (yaxescount == 2) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe3_font_size;


            //if (titlecolor.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
            //    var rgb_arr = [];
            //    if (esapp.Utils.is_array(titlecolor)) {
            //        rgb_arr = titlecolor;
            //    }
            //    else {
            //        rgb_arr = titlecolor.split(" "); // toString().replace(/,/g,' ');
            //    }
            //    var R = rgb_arr[0];
            //    var G = rgb_arr[1];
            //    var B = rgb_arr[2];
            //    titlecolor = esapp.Utils.RGBtoHex(R, G, B);
            //    me.timeseriesGraph.yaxes[yaxescount].title_color = titlecolor;
            //}

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                //tickAmount: 8,
                gridLineWidth: 1,
                offset: 10,
                labels: {
                    format: '{value} ',
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                opposite: opposite
                ,min: min
                ,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }

        me.filename = timeseries_names + me.timeseriesChart.title.replace(' ', '_') + '_' + me.timeseriesChart.subtitle.toString().replace(' ', '_');

        var timeseries = me.timeseriesGraph.timeseries;
        //console.info(timeseries);

        var spacingRight = 10;
        if (me.timeseriesGraph.yaxes.length == 1) {
            spacingRight = 40;
        }


        me.tschart = new Highcharts.Chart({
            //colors: ['#006600', '#000000', '#0070CC', '#00008A', '#8C8C8C', '#1EB611', '#FF9655', '#FFF263', '#6AF9C4'],
            chart: {
                renderTo: 'tschart_' + me.id,
                className: 'chartfitlayout',
                zoomType: 'xy',
                spacingRight: spacingRight,
                alignTicks: false,
                //margin: chartMargin, // [35, 15, 65, 65],  // for legend on the bottom of the chart
                //marginTop:top,
                //marginRight: marginright,
                //marginBottom: 160,
                //marginLeft:left,
                plotBackgroundImage: plotBackgroundImage
            },
            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },
            //exporting: {
            //    //chartOptions: { // specific options for the exported image
            //    //    plotOptions: {
            //    //        series: {
            //    //            dataLabels: {
            //    //                enabled: false
            //    //            }
            //    //        }
            //    //    }
            //    //},
            //    scale: 1,
            //    fallbackToExportServer: false
            //},
            credits: {
                enabled: false
            },
            plotOptions: {
                series: {
                    marker: {
                        enabled: false,
                        states: {
                            hover: {
                                enabled: true,
                                radius: 4,
                                radiusPlus: 0
                                // lineWidthPlus: 2,
                            }
                        }
                    },
                    states: {
                        hover: {
                            halo: {
                                size: 0
                            },
                            lineWidthPlus: 1
                        }
                    }
                },
                column: {
                    pointPadding: 0,
                    //pointWidth: 15,
                    borderWidth: 0,
                    groupPadding: 0,
                    shadow: false
                },
                area: {
                    stacking: 'normal',
                    lineWidth: 1
                }
            },
            title: {
                text: me.timeseriesChart.title,
                align: 'center',
                //y: 50,
                style: {
                    color: me.timeseriesChart.chart_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_title_font_size + 'px'
                }
            },
            subtitle: {
                text: me.timeseriesChart.subtitle,
                align: 'center',
                //y: 65,
                style: {
                    color: me.timeseriesChart.chart_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_subtitle_font_size + 'px'
                }
            },
            xAxis: xAxis,
            //xAxis: [{
            //    type: 'datetime',
            //    //tickmarkPlacement: 'on', // on between  - For categorized axes only!
            //    startOnTick: false,
            //    labels: xAxisLabels,
            //    tickInterval: 30 * 24 * 3600 * 1000
            //
            //    //labels: {
            //    //    enabled: 1,
            //    //    y:28,
            //    //    //step: 1,
            //    //    style: xaxis_labelstyle,
            //    //    formatter: function() {
            //    //        return Highcharts.dateFormat('%b', this.value);
            //    //    }
            //    //}
            //    //,minorTickInterval: 3
            //    //dateTimeLabelFormats: {
            //    //    day: '%e %b'
            //    //},
            //    //categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            //}],
            yAxis: Yaxes,
            tooltip: {
                shared: true,
                split: true,
                dateTimeLabelFormats: {
                    millisecond: '',
                    second: '',
                    minute: '',
                    hour: '',
                    day: "",
                    month: '',
                    year: '%e %b %Y'
                }
            },
            legend: {
                layout: 'horizontal',  // horizontal vertical
                align: 'center', // center left right
                verticalAlign: 'bottom',
                //x: 80,
                //y: 55,
                floating: false,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                //borderColor: Highcharts.theme.legendBackgroundColor || '#FFFFFF',
                symbolPadding: 3,
                symbolWidth: 35,
                symbolHeight: 25,
                borderRadius: 3,
                borderWidth: 0,
                itemMarginBottom: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.legend_title_font_size + 'px',     // '18px',
                    color: me.timeseriesChart.legend_title_font_color     //'black'
                }

            },
            series: timeseries
        });

        me.tschart.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tschart.redraw();
        //console.info(me.tschart);
    },

    createRankingChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }

        var xAxisLabels = {
            enabled: 1,
            y: 34,
            style: {
                color: me.timeseriesChart.xaxe_font_color,
                "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                "fontWeight": 'bold',
                "fontSize": me.timeseriesChart.xaxe_font_size + 'px',
                margin: '0 0 0 0'
            }
        };

        var xAxis = [{
                type: 'category',
                tickmarkPlacement: 'between',      // on between  - For categorized axes only!
                startOnTick: true,
                //lineWidth: 2,
                labels: xAxisLabels
            }]

        me.timeseriesGraph.timeseries.forEach(function (timeserie) {
            timeserie.data.forEach(function (dataItem){
                dataItem.color = esapp.Utils.convertRGBtoHex(dataItem.color);
            })
            timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        });


        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
                opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min == null || min == '' || min == 'null'){
                min = null
            }
            else {
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max == null || max == '' || max == 'null') {
                max = null
            }
            else {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            if (yaxescount == 0) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe1_font_size;
            if (yaxescount == 1) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe2_font_size;
            if (yaxescount == 2) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe3_font_size;

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                //tickAmount: 8,
                gridLineWidth: 1,
                offset: 10,
                labels: {
                    format: '{value} ',
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                opposite: opposite
                ,min: min
                ,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }

        me.filename = timeseries_names + me.timeseriesChart.title.replace(' ', '_') + '_' + me.timeseriesChart.subtitle.toString().replace(' ', '_');

        var timeseries = me.timeseriesGraph.timeseries;
        //console.info(timeseries);

        var spacingRight = 10;
        if (me.timeseriesGraph.yaxes.length == 1) {
            spacingRight = 40;
        }


        me.tschart = new Highcharts.Chart({
            chart: {
                renderTo: 'tschart_' + me.id,
                className: 'chartfitlayout',
                zoomType: 'xy',
                spacingRight: spacingRight,
                alignTicks: true,
                plotBackgroundImage: plotBackgroundImage
            },
            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function(event) {
                                var series = me.tschart.series[0];
                                series.data.forEach(function(point) {
                                    point.update({ color: series.color }, true, false);
                                });
                                series.redraw();
                                this.update({ color: '#ff0000' }, true, false);
                            }
                        }
                    }
                }
            },
            title: {
                text: me.timeseriesChart.title,
                align: 'center',
                style: {
                    color: me.timeseriesChart.chart_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_title_font_size + 'px'
                }
            },
            subtitle: {
                text: me.timeseriesChart.subtitle,
                align: 'center',
                style: {
                    color: me.timeseriesChart.chart_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_subtitle_font_size + 'px'
                }
            },
            xAxis: xAxis,
            yAxis: Yaxes,
            tooltip: {
                shared: true,
                split: true,
                dateTimeLabelFormats: {
                    millisecond: '',
                    second: '',
                    minute: '',
                    hour: '',
                    day: "",
                    month: '',
                    year: '%e %b %Y'
                }
            },
            legend: {
                layout: 'horizontal',  // horizontal vertical
                align: 'center', // center left right
                verticalAlign: 'bottom',
                floating: false,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                symbolPadding: 3,
                symbolWidth: 35,
                symbolHeight: 25,
                borderRadius: 3,
                borderWidth: 0,
                itemMarginBottom: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.legend_title_font_size + 'px',     // '18px',
                    color: me.timeseriesChart.legend_title_font_color
                }

            },
            series: timeseries
        });

        me.tschart.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tschart.redraw();
        //console.info(me.tschart);
    },

    createMatrixChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }
        var timeseries = me.timeseriesGraph.timeseries;
        //console.info(timeseries);

        var colorAxis = me.timeseriesGraph.colorAxis;

        var xAxisLabels = {
            enabled: 1,
            y: 34,
            style: {
                color: me.timeseriesChart.xaxe_font_color,
                "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                "fontWeight": 'bold',
                "fontSize": me.timeseriesChart.xaxe_font_size + 'px',
                margin: '0 0 0 0'
            }
        };

        var xAxis = [{
            type: 'datetime',
            //tickmarkPlacement: 'on',      // on between  - For categorized axes only!
            startOnTick: false,
            lineWidth: 2,
            labels: xAxisLabels,
            tickInterval: 30 * 24 * 3600 * 1000
        }];

        //me.timeseriesGraph.timeseries.forEach(function (timeserie) {
        //    timeserie.data.forEach(function (dataItem){
        //        dataItem.color = esapp.Utils.convertRGBtoHex(dataItem.color);
        //    })
        //    timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        //});


        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
                opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            //var min = me.timeseriesGraph.yaxes[yaxescount].min;
            //if (min == null || min == '' || min == 'null'){
            //    min = null
            //}
            //else {
            //    min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            //}
            //var max = me.timeseriesGraph.yaxes[yaxescount].max;
            //if (max == null || max == '' || max == 'null') {
            //    max = null
            //}
            //else {
            //    max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            //}

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            if (yaxescount == 0) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe1_font_size;
            if (yaxescount == 1) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe2_font_size;
            if (yaxescount == 2) me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = me.timeseriesChart.yaxe3_font_size;

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                categories: me.timeseriesGraph.yaxes[yaxescount].categories,
                //tickAmount: 8,
                //gridLineWidth: 1,
                offset: 10,
                labels: {
                    format: '{value} ',
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size + 'px'
                    }
                },
                opposite: opposite
                //,min: min
                //,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }

        me.filename = timeseries_names + me.timeseriesChart.title.replace(' ', '_') + '_' + me.timeseriesChart.subtitle.toString().replace(' ', '_');

        var spacingRight = 10;
        if (me.timeseriesGraph.yaxes.length == 1) {
            spacingRight = 40;
        }

        me.tschart = new Highcharts.Chart({
            chart: {
                //type: 'heatmap',
                renderTo: 'tschart_' + me.id,
                className: 'chartfitlayout',
                //zoomType: 'xy',
                spacingRight: spacingRight,
                //alignTicks: true,
                plotBackgroundImage: plotBackgroundImage
            },
            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },
            credits: {
                enabled: false
            },

            title: {
                text: me.timeseriesChart.title,
                align: 'center',
                style: {
                    color: me.timeseriesChart.chart_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_title_font_size + 'px'
                }
            },
            subtitle: {
                text: me.timeseriesChart.subtitle,
                align: 'center',
                style: {
                    color: me.timeseriesChart.chart_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.chart_subtitle_font_size + 'px'
                }
            },
            xAxis: xAxis,
            yAxis: Yaxes,
            colorAxis: colorAxis,
            tooltip: {
                shared: true,
                split: true,
                dateTimeLabelFormats: {
                    millisecond: '',
                    second: '',
                    minute: '',
                    hour: '',
                    day: "",
                    month: '',
                    year: '%e %b %Y'
                }
            },
            legend: {
                layout: 'horizontal',  // horizontal vertical
                align: 'center', // center left right
                verticalAlign: 'bottom',
                floating: false,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                symbolPadding: 3,
                symbolWidth: 35,
                symbolHeight: 25,
                borderRadius: 3,
                borderWidth: 0,
                itemMarginBottom: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.timeseriesChart.legend_title_font_size + 'px',     // '18px',
                    color: me.timeseriesChart.legend_title_font_color
                }

            },
            series: timeseries
        });

        me.tschart.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tschart.redraw();
        //console.info(me.tschart);
    },

    generateChart: function(){
        var me = this.getView();
        var chartpropertiesStore = this.getStore('chartproperties');

        chartpropertiesStore.load({
            params: {
                charttype: me.charttype
            },
            callback:function(){
                me.getController().setDefaultChartDrawProperties();
                chartpropertiesStore.each(function(chartproperties) {
                    var height = parseInt(chartproperties.get('chart_height'));
                    if (height > Ext.getBody().getViewSize().height-80){
                        height = Ext.getBody().getViewSize().height-80
                    }
                    me.setSize(parseInt(chartproperties.get('chart_width')), height);
                });
                if (me.charttype == 'ranking'){
                    me.getController().getTimeseries(me.getController().createRankingChart);
                }
                else if (me.charttype == 'matrix'){
                    me.getController().getTimeseries(me.getController().createMatrixChart);
                }
                else {
                    me.getController().getTimeseries(me.getController().createDefaultChart);
                }
            }
        });
    },

    refreshChart: function(){
        var me = this.getView();
        var chartpropertiesStore = this.getStore('chartproperties');
        var timeseriesselections = Ext.getCmp('timeserieschartselection').getController().getTimeseriesSelections(me.charttype);
        var chartdrawpropertiespanel = this.lookupReference('chart_draw_properties_' + me.id);

        if (chartdrawpropertiespanel != null){
            chartdrawpropertiespanel.close();
        }

        if (timeseriesselections != null) {
            //console.info(timeseriesselections);
            me.selectedTimeseries = timeseriesselections.selectedTimeseries;
            me.yearTS = timeseriesselections.yearTS;
            me.tsFromPeriod = timeseriesselections.tsFromPeriod;
            me.tsToPeriod = timeseriesselections.tsToPeriod;
            me.yearsToCompare = timeseriesselections.yearsToCompare;
            me.tsFromSeason = timeseriesselections.tsFromSeason;
            me.tsToSeason = timeseriesselections.tsToSeason;
            me.wkt = timeseriesselections.wkt;

            if( me.tschart instanceof Highcharts.Chart) {
                me.tschart.destroy();
            }
            me.tschart = null;

            this.generateChart();
        }
    },

    openChartProperties: function() {
        var me = this.getView(),
            methis = this,
            source = {},
            yaxe1 = {},
            yaxe2 = {},
            yaxe3 = {}

        var crenderer = function(color) {
            renderTpl = color;

            if (color.trim()==''){
                renderTpl = 'transparent';
            }
            else {
                renderTpl = '<span style="background:rgb('+esapp.Utils.HexToRGB(color)+'); color:'+esapp.Utils.invertHexToRGB(color)+';">'+esapp.Utils.HexToRGB(color)+'</span>';
            }
            return renderTpl;
        };

        var fontsizes = Ext.create('Ext.data.Store', {      // [8,9,10,11,12,14,16,18,20,22,24,26,28,30,32,34,36,48,72]
            fields: ['fontsize'],
            data : [
                {'fontsize': 8},
                {'fontsize': 9},
                {'fontsize': 10},
                {'fontsize': 11},
                {'fontsize': 12},
                {'fontsize': 14},
                {'fontsize': 16},
                {'fontsize': 18},
                {'fontsize': 20},
                {'fontsize': 22},
                {'fontsize': 24},
                {'fontsize': 26},
                {'fontsize': 28},
                {'fontsize': 30},
                {'fontsize': 32},
                {'fontsize': 34},
                {'fontsize': 36},
                {'fontsize': 48},
                {'fontsize': 72}
            ]
        });

        var fontsizesCombo = {
            xtype: 'combobox',
            store: fontsizes,
            queryMode: 'local',
            displayField: 'fontsize',
            valueField: 'fontsize',
            forceSelection: true,
            triggerAction: 'all',
            allowBlank: false,
            editable: false
        }

        source = {
            chart_width: me.timeseriesChart.width,
            chart_height: me.timeseriesChart.height,

            chart_title:  me.timeseriesChart.title,
            chart_title_font_color:  esapp.Utils.convertRGBtoHex(me.timeseriesChart.chart_title_font_color),
            chart_title_font_size:  me.timeseriesChart.chart_title_font_size,

            chart_subtitle:  me.timeseriesChart.subtitle,
            chart_subtitle_font_color:  esapp.Utils.convertRGBtoHex(me.timeseriesChart.chart_subtitle_font_color),
            chart_subtitle_font_size:  me.timeseriesChart.chart_subtitle_font_size,

            legend_font_size: me.timeseriesChart.legend_title_font_size,
            legend_font_color: esapp.Utils.convertRGBtoHex(me.timeseriesChart.legend_title_font_color),

            xaxe_font_size: me.timeseriesChart.xaxe_font_size,
            xaxe_font_color: esapp.Utils.convertRGBtoHex(me.timeseriesChart.xaxe_font_color)
        }

        source.yaxe1_id = me.timeseriesGraph.yaxes[0].id;
        source.yaxe1_title = me.timeseriesGraph.yaxes[0].title;
        source.yaxe1_font_size = me.timeseriesChart.yaxe1_font_size;    // from TABLE!
        source.yaxe1_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[0].title_color);
        source.yaxe1_min = me.timeseriesGraph.yaxes[0].min;
        source.yaxe1_max = me.timeseriesGraph.yaxes[0].max;
        source.yaxe1_opposite = me.timeseriesGraph.yaxes[0].opposite;
        source.yaxe1_unit = me.timeseriesGraph.yaxes[0].unit;
        source.yaxe1_aggregation_type = me.timeseriesGraph.yaxes[0].aggregation_type;
        source.yaxe1_aggregation_min = me.timeseriesGraph.yaxes[0].aggregation_min;
        source.yaxe1_aggregation_max = me.timeseriesGraph.yaxes[0].aggregation_max;

        if (me.timeseriesGraph.yaxes.length == 2) {
            source.yaxe2_id = me.timeseriesGraph.yaxes[1].id;
            source.yaxe2_title = me.timeseriesGraph.yaxes[1].title;
            source.yaxe2_font_size = me.timeseriesChart.yaxe2_font_size;    // from TABLE!
            source.yaxe2_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[1].title_color);
            source.yaxe2_min = me.timeseriesGraph.yaxes[1].min;
            source.yaxe2_max = me.timeseriesGraph.yaxes[1].max;
            source.yaxe2_opposite = me.timeseriesGraph.yaxes[1].opposite;
            source.yaxe2_unit = me.timeseriesGraph.yaxes[1].unit;
            source.yaxe2_aggregation_type = me.timeseriesGraph.yaxes[1].aggregation_type;
            source.yaxe2_aggregation_min = me.timeseriesGraph.yaxes[1].aggregation_min;
            source.yaxe2_aggregation_max = me.timeseriesGraph.yaxes[1].aggregation_max;

        } else if (me.timeseriesGraph.yaxes.length == 3) {
            source.yaxe2_id = me.timeseriesGraph.yaxes[1].id;
            source.yaxe2_title = me.timeseriesGraph.yaxes[1].title;
            source.yaxe2_font_size = me.timeseriesChart.yaxe2_font_size;    // from TABLE!
            source.yaxe2_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[1].title_color);
            source.yaxe2_min = me.timeseriesGraph.yaxes[1].min;
            source.yaxe2_max = me.timeseriesGraph.yaxes[1].max;
            source.yaxe2_opposite = me.timeseriesGraph.yaxes[1].opposite;
            source.yaxe2_unit = me.timeseriesGraph.yaxes[1].unit;
            source.yaxe2_aggregation_type = me.timeseriesGraph.yaxes[1].aggregation_type;
            source.yaxe2_aggregation_min = me.timeseriesGraph.yaxes[1].aggregation_min;
            source.yaxe2_aggregation_max = me.timeseriesGraph.yaxes[1].aggregation_max;

            source.yaxe3_id = me.timeseriesGraph.yaxes[2].id;
            source.yaxe3_title = me.timeseriesGraph.yaxes[2].title;
            source.yaxe3_font_size = me.timeseriesChart.yaxe3_font_size;    // from TABLE!
            source.yaxe3_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[2].title_color);
            source.yaxe3_min = me.timeseriesGraph.yaxes[2].min;
            source.yaxe3_max = me.timeseriesGraph.yaxes[2].max;
            source.yaxe3_opposite = me.timeseriesGraph.yaxes[2].opposite;
            source.yaxe3_unit = me.timeseriesGraph.yaxes[2].unit;
            source.yaxe3_aggregation_type = me.timeseriesGraph.yaxes[2].aggregation_type;
            source.yaxe3_aggregation_min = me.timeseriesGraph.yaxes[2].aggregation_min;
            source.yaxe3_aggregation_max = me.timeseriesGraph.yaxes[2].aggregation_max;
        }

        //var cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
        //    clicksToEdit: 1
        //});


        var drawproperties = Ext.create('Ext.panel.Panel', {
            title: esapp.Utils.getTranslation('chart_properties'),     // 'Chart properties',
            reference: 'chart_draw_properties_'+me.id,
            width: 400,
            height: 650,
            //autoHeight: true,
            margin: '0 0 10 0',
            maximizable: false,
            collapsible: true,
            resizable: true,
            layout: 'fit',
            hidden: true,
            floating: true,
            defaultAlign: 'bl-bl',
            closable: true,
            closeAction: 'destroy',
            draggable: true,
            constrain: true,
            alwaysOnTop: true,
            autoShow: false,
            frame: true,
            frameHeader : false,
            border: false,
            shadow: false,
            defaults: {
              //align: 'right'
            },
            items: [
                {   text: esapp.Utils.getTranslation('Chart draw properties'),
                    xtype: 'propertygrid',
                    //plugins: [ cellEditing ],
                    nameColumnWidth: 180,
                    sortableColumns: false,
                    source: source,
                    sourceConfig: {
                        chart_width: {
                            displayName: esapp.Utils.getTranslation('chartwidth'),   // 'Chart width (in px)',
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus:true
                            }
                        },
                        chart_height: {
                            displayName: esapp.Utils.getTranslation('chartheight'),   // 'Chart height (in px)',
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus:true
                            }
                        },
                        chart_title: {
                            displayName: esapp.Utils.getTranslation('title'),   // 'Title',
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:true
                            }
                        },
                        chart_title_font_color: {
                            displayName: esapp.Utils.getTranslation('titlecolor'),   // 'Title color',
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        chart_title_font_size: {
                            displayName: esapp.Utils.getTranslation('titlefontsize'),   // 'Title font size',
                            //type: 'number',
                            editor: fontsizesCombo
                        },
                        chart_subtitle: {
                            displayName: esapp.Utils.getTranslation('subtitle'),   // 'Sub title',
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:true
                            }
                        },
                        chart_subtitle_font_color: {
                            displayName: esapp.Utils.getTranslation('subtitlecolor'),   // 'Sub title color',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        chart_subtitle_font_size: {
                            displayName: esapp.Utils.getTranslation('subtitlefontsize'),   // 'Sub title font size',
                            editor: fontsizesCombo
                        },
                        legend_font_size: {
                            displayName: esapp.Utils.getTranslation('legendfontsize'),   // 'Legend font size',
                            editor: fontsizesCombo
                        },
                        legend_font_color: {
                            displayName: esapp.Utils.getTranslation('legendfontcolor'),   // 'Legend font colour',
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        xaxe_font_size: {
                            displayName: esapp.Utils.getTranslation('xaxefontsize'),   // 'xAxe font size',
                            editor: fontsizesCombo
                        },
                        xaxe_font_color: {
                            displayName: esapp.Utils.getTranslation('xaxefontcolor'),   // 'xAxe font color',
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },


                        yaxe1_id: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('id')
                            //type: null
                            //editor: null,
                            //editable: false,
                            //disabled: true,
                            //cls: 'highlightYaxe',
                            //style: {
                            //    "background-color": '#C1DDF1'
                            //},
                            //listener: {
                            //    afterrender: function(field, eOpts){ console.info('id field rendered'); field.setEditable(false);}
                            //}
                        },
                        yaxe1_title: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('title'),
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:true
                            }
                        },
                        yaxe1_font_size: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('fontsize'),
                            editor: fontsizesCombo
                        },
                        yaxe1_color: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('color'),
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        yaxe1_min: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('min'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus:true
                            }
                        },
                        yaxe1_max: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('max'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus:true
                            }
                        },
                        yaxe1_opposite: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                            type: 'boolean'
                        },
                        yaxe1_unit: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe1_aggregation_type: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                            editor: {
                                xtype: 'combobox',
                                store: ['mean', 'count', 'percent', 'cumulate', 'surface'],
                                forceSelection: true
                            }
                        },
                        yaxe1_aggregation_min: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                            type: 'number'
                        },
                        yaxe1_aggregation_max: {
                            displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                            type: 'number'
                        },


                        yaxe2_id: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('id'),
                            editor: {
                            }
                        },
                        yaxe2_title: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('title'),
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe2_font_size: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('fontsize'),
                            editor: fontsizesCombo
                        },
                        yaxe2_color: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('color'),
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        yaxe2_min: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('min'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe2_max: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('max'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe2_opposite: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                            type: 'boolean'
                        },
                        yaxe2_unit: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe2_aggregation_type: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                            editor: {
                                xtype: 'combobox',
                                store: ['mean', 'count', 'percent', 'cumulate', 'surface'],
                                forceSelection: true
                            }
                        },
                        yaxe2_aggregation_min: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                            type: 'number'
                        },
                        yaxe2_aggregation_max: {
                            displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                            type: 'number'
                        },


                        yaxe3_id: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('id'),
                            editor: {
                            }
                        },
                        yaxe3_title: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('title'),
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe3_font_size: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('fontsize'),
                            editor: fontsizesCombo
                        },
                        yaxe3_color: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('color'),
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        yaxe3_min: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('min'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe3_max: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('max'),
                            //type: 'number',
                            editor: {
                                xtype: 'numberfield',
                                selectOnFocus: true
                            }
                        },
                        yaxe3_opposite: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                            type: 'boolean'
                        },
                        yaxe3_unit: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:true
                            }
                        },
                        yaxe3_aggregation_type: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                            editor: {
                                xtype: 'combobox',
                                store: ['mean', 'count', 'percent', 'cumulate', 'surface'],
                                forceSelection: true
                            }
                        },
                        yaxe3_aggregation_min: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                            type: 'number'
                        },
                        yaxe3_aggregation_max: {
                            displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                            type: 'number'
                        }
                    },

                    listeners: {
                        propertychange: function( source, recordId, value, oldValue, eOpts ){
                            //console.info(source);
                            //console.info(recordId);
                            //console.info(value);
                            //console.info(oldValue.toLowerCase());
                            function saveChartProperty(property, newvalue){
                                var chartpropertiesStore = methis.getStore('chartproperties');
                                chartpropertiesStore.each(function(chartproperties) {
                                    if (chartproperties.data.hasOwnProperty(property)){
                                        //console.info('Property "' + property + '" exists in record!');
                                        chartproperties.set(property, newvalue);
                                    }
                                });
                            }

                            function saveYaxeProperty(yaxe){
                                //console.info(yaxe);
                                // AJAX call to save yaxe!
                                Ext.Ajax.request({
                                    url:"analysis/updateyaxe",
                                    timeout : 300000,
                                    //scope: me,
                                    params:yaxe,
                                    method: 'POST',
                                    success: function ( result, request ) {
                                        //console.info(Ext.util.JSON.decode(result.responseText));
                                    },
                                    failure: function ( result, request) {
                                    }
                                });
                            }

                            if (value != oldValue) {
                                //if (me.charttype == 'default') {
                                    if (recordId == 'chart_width') {
                                        me.timeseriesChart.width = value;
                                        me.setSize(parseInt(me.timeseriesChart.width), parseInt(me.timeseriesChart.height));
                                    }
                                    if (recordId == 'chart_height') {
                                        me.timeseriesChart.height = value;
                                        me.setSize(parseInt(me.timeseriesChart.width), parseInt(me.timeseriesChart.height));
                                    }
                                    if (recordId == 'chart_title') me.timeseriesChart.title = value;
                                    if (recordId == 'chart_title_font_color')  me.timeseriesChart.chart_title_font_color = value;
                                    if (recordId == 'chart_title_font_size')  me.timeseriesChart.chart_title_font_size = value;

                                    if (recordId == 'chart_subtitle')  me.timeseriesChart.subtitle = value;
                                    if (recordId == 'chart_subtitle_font_color')  me.timeseriesChart.chart_subtitle_font_color = value;
                                    if (recordId == 'chart_subtitle_font_size')  me.timeseriesChart.chart_subtitle_font_size = value;

                                    if (recordId == 'legend_font_size')  me.timeseriesChart.legend_title_font_size = value;
                                    if (recordId == 'legend_font_color')  me.timeseriesChart.legend_title_font_color = value;

                                    if (recordId == 'xaxe_font_size')  me.timeseriesChart.xaxe_font_size = value;
                                    if (recordId == 'xaxe_font_color')  me.timeseriesChart.xaxe_font_color = value;

                                    if (recordId == 'yaxe1_title')  {
                                        me.timeseriesGraph.yaxes[0].title = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_font_size')  me.timeseriesChart.yaxe1_font_size = value;    // from TABLE!
                                    if (recordId == 'yaxe1_color')  {
                                        me.timeseriesGraph.yaxes[0].title_color = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_min')  {
                                        me.timeseriesGraph.yaxes[0].min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_max')  {
                                        me.timeseriesGraph.yaxes[0].max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_opposite')  {
                                        me.timeseriesGraph.yaxes[0].opposite = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_unit')  {
                                        me.timeseriesGraph.yaxes[0].unit = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_aggregation_type')  {
                                        me.timeseriesGraph.yaxes[0].aggregation_type = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_aggregation_min')  {
                                        me.timeseriesGraph.yaxes[0].aggregation_min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }
                                    if (recordId == 'yaxe1_aggregation_max')  {
                                        me.timeseriesGraph.yaxes[0].aggregation_max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                    }


                                    if (recordId == 'yaxe2_title')  {
                                        me.timeseriesGraph.yaxes[1].title = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_font_size')  me.timeseriesChart.yaxe2_font_size = value;     // from TABLE!
                                    if (recordId == 'yaxe2_color')  {
                                        me.timeseriesGraph.yaxes[1].title_color = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_min')  {
                                        me.timeseriesGraph.yaxes[1].min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_max')  {
                                        me.timeseriesGraph.yaxes[1].max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_opposite')  {
                                        me.timeseriesGraph.yaxes[1].opposite = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_unit')  {
                                        me.timeseriesGraph.yaxes[1].unit = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_aggregation_type')  {
                                        me.timeseriesGraph.yaxes[1].aggregation_type = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_aggregation_min')  {
                                        me.timeseriesGraph.yaxes[1].aggregation_min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }
                                    if (recordId == 'yaxe2_aggregation_max')  {
                                        me.timeseriesGraph.yaxes[1].aggregation_max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                    }


                                    if (recordId == 'yaxe3_title')  {
                                        me.timeseriesGraph.yaxes[2].title = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_font_size')  me.timeseriesChart.yaxe3_font_size = value;    // from TABLE!
                                    if (recordId == 'yaxe3_color')  {
                                        me.timeseriesGraph.yaxes[2].title_color = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_min')  {
                                        me.timeseriesGraph.yaxes[2].min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_max')  {
                                        me.timeseriesGraph.yaxes[2].max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_opposite')  {
                                        me.timeseriesGraph.yaxes[2].opposite = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_unit')  {
                                        me.timeseriesGraph.yaxes[2].unit = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_aggregation_type')  {
                                        me.timeseriesGraph.yaxes[2].aggregation_type = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_aggregation_min')  {
                                        me.timeseriesGraph.yaxes[2].aggregation_min = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }
                                    if (recordId == 'yaxe3_aggregation_max')  {
                                        me.timeseriesGraph.yaxes[2].aggregation_max = value;
                                        saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                    }

                                    me.timeseriesChart.localRefresh = true;
                                    saveChartProperty(recordId, value);

                                    if (me.charttype == 'ranking'){
                                        me.getController().createRankingChart(me);
                                    }
                                    else if (me.charttype == 'matrix'){
                                        me.getController().createMatrixChart(me);
                                    }
                                    else {
                                        me.getController().createDefaultChart(me);
                                    }

                                //}
                            }
                        },
                        beforeedit: function( editor, e, opts ) {
                            //console.info(e.record.get( 'name' ));
                            if( e.record.get( 'name' )=='yaxe1_id' || e.record.get( 'name' )=='yaxe2_id' || e.record.get( 'name' )=='yaxe3_id') {
                                return false;
                            }
                        }
                    }
                }
            ]
        });

        me.add(drawproperties);
        drawproperties.show();

    },

    saveChart: function() {

        //function saveImageAs (imgOrURL) {
        //    if (typeof imgOrURL == 'object')
        //      imgOrURL = imgOrURL.src;
        //    window.win = open (imgOrURL);
        //    setTimeout('win.document.execCommand("SaveAs")', 500);
        //}

        function download(data, filename) {
          var a = document.createElement('a');
          a.download = filename;
          a.href = data;
          document.body.appendChild(a);
          a.click();
          a.remove();
        }

        var EXPORT_WIDTH = 1200;
        var me = this.getView();
        var chart = me.tschart;

        var render_width = EXPORT_WIDTH;
        var render_height = render_width * chart.chartHeight / chart.chartWidth;

        // Get the cart's SVG code          getSVGForLocalExport() if using modules/offline-exporting.js
        var svg = chart.getSVG({
            exporting: {
              sourceWidth: chart.chartWidth,
              sourceHeight: chart.chartHeight
            }
        });

        // Create a canvas
        var canvas = document.createElement('canvas');
        canvas.height =  render_height;
        canvas.width = render_width;
        //document.body.appendChild(canvas);

        // Create an image and draw the SVG onto the canvas
        var image = new Image;
            image.onload = function() {
                canvas.getContext('2d').drawImage(this, 0, 0, render_width, render_height);
                var data = canvas.toDataURL("image/png");
                download(data, me.filename + '.png');
            };
        //image.src = 'data:image/svg+xml;base64,' + window.btoa(svg);
        image.src = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(svg)));


        //console.info(data);
        // data = data.replace(/^data:image\/(png|jpg);base64,/, "");
        //download(data, me.filename + '.png');

        // console.info(image);
        // saveImageAs(image);
    },

    tsDownload: function() {

        var chart = this.getView().tschart;
        var type = Highcharts.exporting.MIME_TYPES.XLS;
        chart.exportChartLocal({ type: type, filename: this.getView().filename});
    }

    //,_saveChart: function() {
    //    // FROM : http://willkoehler.net/2014/11/07/client-side-solution-for-downloading-highcharts-charts-as-images.html
    //
    //    function download(canvas, filename) {
    //        download_in_ie(canvas, filename) || download_with_link(canvas, filename);
    //    }
    //
    //    // Works in IE10 and newer
    //    function download_in_ie(canvas, filename) {
    //        return(navigator.msSaveOrOpenBlob && navigator.msSaveOrOpenBlob(canvas.msToBlob(), filename));
    //    }
    //
    //    // Works in Chrome and FF. Safari just opens image in current window, since .download attribute is not supported
    //    function download_with_link(canvas, filename) {
    //        var a = document.createElement('a')
    //        a.download = filename
    //        a.href = canvas.toDataURL("image/png")
    //        document.body.appendChild(a);
    //        a.click();
    //        a.remove();
    //    }
    //
    //    var chart = this.getView().tschart;
    //
    //    var render_width = 1000;
    //    var render_height = render_width * chart.chartHeight / chart.chartWidth;
    //
    //    var svg = chart.getSVG({
    //        exporting: {
    //            sourceWidth: chart.chartWidth,
    //            sourceHeight: chart.chartHeight
    //        }
    //    });
    //
    //    var canvas = document.createElement('canvas');
    //    canvas.height = render_height;
    //    canvas.width = render_width;
    //
    //    canvg(canvas, svg, {
    //        scaleWidth: render_width,
    //        scaleHeight: render_height,
    //        ignoreDimensions: true
    //    });
    //
    //    download(canvas, this.getView().filename + '.png');
    //
    //}
});
