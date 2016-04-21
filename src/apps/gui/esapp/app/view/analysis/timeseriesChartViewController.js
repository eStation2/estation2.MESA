Ext.define('esapp.view.analysis.timeseriesChartViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartview',

    getTimeseries: function(callback){
        var me = this.getView();
        //var timeseries = {};

        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('generatingtimeseries'), // 'Generating requested time series...',
            target : Ext.getCmp('tschart_'+me.id)
            ,toFrontOnShow: true
            ,useTargetEl:true
        });
        myLoadMask.show();

        Ext.Ajax.request({
            url:"analysis/gettimeseries",
            timeout : 300000,
            scope: this,
            params:{
                selectedTimeseries: me.selectedTimeseries,
                yearTS: me.yearTS,
                tsFromPeriod: Ext.Date.format(me.tsFromPeriod, 'Y-m-d'),
                tsToPeriod: Ext.Date.format(me.tsToPeriod, 'Y-m-d'),
                WKT:me.wkt
            },
            method: 'POST',
            success: function ( result, request ) {
                myLoadMask.hide();
                me.timeseriesGraph = Ext.util.JSON.decode(result.responseText);
                this.setChartDrawProperties();
                callback(this);
           },
           failure: function ( result, request) {
               myLoadMask.hide();
               //return timeseries
           }
        });
    },

    setChartDrawProperties: function() {
        var me = this.getView();

        me.timeseriesGraph.title = Ext.getCmp('selectedregionname').getValue();
        me.timeseriesGraph.chart_title_font_size = 34;
        me.timeseriesGraph.chart_title_font_color = esapp.Utils.convertRGBtoHex('0 0 0');

        me.timeseriesGraph.subtitle = '';
        if (me.yearTS != '') {
            me.timeseriesGraph.subtitle = me.yearTS;
        }
        else {
            me.timeseriesGraph.subtitle = esapp.Utils.getTranslation('from') + ' ' + Ext.Date.format(me.tsFromPeriod, 'Y-m-d') + '  ' + esapp.Utils.getTranslation('to') + ' ' + Ext.Date.format(me.tsToPeriod, 'Y-m-d');
        }
        me.timeseriesGraph.chart_subtitle_font_size = 24;
        me.timeseriesGraph.chart_subtitle_font_color = esapp.Utils.convertRGBtoHex('#666666');

        me.timeseriesGraph.filename = me.timeseriesGraph.title + '_' + me.timeseriesGraph.subtitle.toString().replace(' ', '_');

        me.timeseriesGraph.xaxe_font_size = 16;
        me.timeseriesGraph.xaxe_font_color = esapp.Utils.convertRGBtoHex('111 111 111');

        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            me.timeseriesGraph.yaxes[yaxescount].yaxe_title_font_size = 10;  // '30px'
            me.timeseriesGraph.yaxes[yaxescount].title_color = '221 21 221';
        }

        me.timeseriesGraph.legend_title_font_size = 28;     // '18px',
        me.timeseriesGraph.legend_title_font_color = '255 13 78';    //'black'

        console.info(me.timeseriesGraph);
    },

    createChart: function(mecallback) {
        var me = mecallback.getView();
        var json = me.timeseriesGraph;

        console.info(json);

        var plotBackgroundImage = '';
        var categories = [];
        //var categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        if (json.data_available) {
            //var cats = json.xaxis.categories;
            //for (var i = 0; i < cats.length; i++) {
            //    var year = cats[i].substring(0,4);
            //    var month = cats[i].substring(4,6);
            //    var day = cats[i].substring(6,8);
            //    categories[i] = Date.UTC(year, month-1, day); // Date.UTC(year, month-1, day);
            //}
        } else {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }

        //var xaxis_labelstyle = {
        //        color: '#000',
        //        font: 'bold 20px Arial, Verdana, Helvetica, sans-serif',
        //        margin: '0 0 0 0'
        //    }
        var xAxisLabels = {};
        if (json.showYearInTicks) {      //  === 'true'
            xAxisLabels = {
                enabled: 1,
                autoRotation: [-2, -5],
                autoRotationLimit: -5,
                //rotation: 1,
                y: 28,
                style: {
                    color: json.xaxe_font_color,   // '#000',
                    font: 'Arial, Verdana, Helvetica, sans-serif',
                    "font-weight": 'bold',
                    fontSize: json.xaxe_font_size-6,   // '20px',
                    margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value) + '<br/>' + Highcharts.dateFormat('\'%y', this.value);
                }
            };
        } else {
            xAxisLabels = {
                enabled: 1,
                //rotation: 0,
                y: 28,
                //step: 3,
                style: {
                    color: json.xaxe_font_color,   // '#000',
                    font: 'Arial, Verdana, Helvetica, sans-serif',
                    "font-weight": 'bold',
                    fontSize: json.xaxe_font_size,   // '26px',
                    margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value);
                }
            };
        }

        for (var tscount = 0; tscount < json.timeseries.length; tscount++) {

            var tscolor = json.timeseries[tscount].color;
            var tstype = json.timeseries[tscount].type;
            var tsname = json.timeseries[tscount].name;

            if (tsname.indexOf('transparent') == -1) { // Not a transparent timeseries
                if (tstype == 'area') {
                    tscolor = json.timeseries[tscount].fillColor;
                }
                tscolor = esapp.Utils.convertRGBtoHex(tscolor);

                if (tstype == 'area') {
                    json.timeseries[tscount].fillColor = tscolor;
                }
                else {
                    json.timeseries[tscount].color = tscolor;
                }

                //if (tscolor.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
                //    var rgbarr = [];
                //    if (esapp.Utils.is_array(tscolor)) {
                //        rgbarr = tscolor;
                //    }
                //    else {
                //        rgbarr = tscolor.split(" "); // toString().replace(/,/g,' ');
                //    }
                //
                //    var tsR = rgbarr[0];
                //    var tsG = rgbarr[1];
                //    var tsB = rgbarr[2];
                //    tscolor = esapp.Utils.RGBtoHex(tsR, tsG, tsB);
                //
                //    if (tstype == 'area') {
                //        json.timeseries[tscount].fillColor = tscolor;
                //    }
                //    else {
                //        json.timeseries[tscount].color = tscolor;
                //    }
                //}
            }
        }

        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < json.yaxes.length; yaxescount++) {
            var opposite = false;
            if (json.yaxes[yaxescount].opposite === 'true')
                opposite = true;

            var unit = json.yaxes[yaxescount].unit;
            if (unit == null)
                unit = ''
            else unit = ' (' + unit + ')'

            var min = json.yaxes[yaxescount].min;
            if (min != null)
                min = parseFloat(json.yaxes[yaxescount].min)

            var max = json.yaxes[yaxescount].max;
            if (max != null)
                max = parseFloat(json.yaxes[yaxescount].max)


            json.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(json.yaxes[yaxescount].title_color);

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
            //    json.yaxes[yaxescount].title_color = titlecolor;
            //}

            var yaxe = {
                id: json.yaxes[yaxescount].id,
                tickAmount: 8,
                gridLineWidth: 1,
                labels: {
                    format: '{value} ',
                    style: {
                        color: json.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        font: 'Arial, Verdana, Helvetica, sans-serif',
                        "font-weight": 'bold',
                        fontSize: json.yaxes[yaxescount].yaxe_title_font_size    // '30px'
                    }
                },
                title: {
                    text: json.yaxes[yaxescount].title + unit,
                    style: {
                        color: json.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        font: 'Arial, Verdana, Helvetica, sans-serif',
                        "font-weight": 'bold',
                        fontSize: json.yaxes[yaxescount].yaxe_title_font_size    // '30px'
                    }
                },
                opposite: opposite,
                min: min,
                max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += '_' + json.yaxes[yaxescount].title;
        }
        me.filename += timeseries_names;

        //var Yaxes = [{ // Primary yAxis
        //    labels: {
        //        format: '{value}°C',
        //        style: {
        //            color: Highcharts.getOptions().colors[2]
        //        }
        //    },
        //    title: {
        //        text: 'Temperature',
        //        style: {
        //            color: Highcharts.getOptions().colors[2]
        //        }
        //    },
        //    opposite: true
        //
        //}, { // Secondary yAxis
        //    gridLineWidth: 0,
        //    title: {
        //        text: 'Rainfall',
        //        style: {
        //            color: Highcharts.getOptions().colors[0]
        //        }
        //    },
        //    labels: {
        //        format: '{value} mm',
        //        style: {
        //            color: Highcharts.getOptions().colors[0]
        //        }
        //    }
        //}, { // Tertiary yAxis
        //    gridLineWidth: 0,
        //    title: {
        //        text: 'Sea-Level Pressure',
        //        style: {
        //            color: Highcharts.getOptions().colors[1]
        //        }
        //    },
        //    labels: {
        //        format: '{value} mb',
        //        style: {
        //            color: Highcharts.getOptions().colors[1]
        //        }
        //    },
        //    opposite: true
        //}];

        var timeseries = json.timeseries;
        //var timeseries = [{
        //    name: 'Rainfall',
        //    type: 'column',
        //    yAxis: 1,
        //    data: [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4],
        //    tooltip: {
        //        valueSuffix: ' mm'
        //    }
        //
        //}, {
        //    name: 'Sea-Level Pressure',
        //    type: 'spline',
        //    yAxis: 2,
        //    data: [1016, 1016, 1015.9, 1015.5, 1012.3, 1009.5, 1009.6, 1010.2, 1013.1, 1016.9, 1018.2, 1016.7],
        //    marker: {
        //        enabled: false
        //    },
        //    dashStyle: 'shortdot',
        //    tooltip: {
        //        valueSuffix: ' mb'
        //    }
        //
        //}, {
        //    name: 'Temperature',
        //    type: 'spline',
        //    data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6],
        //    tooltip: {
        //        valueSuffix: ' °C'
        //    }
        //}];

        var spacingRight = 10;
        if (json.yaxes.length == 1) {
            spacingRight = 40;
        }


        me.tschart = new Highcharts.Chart({
            //colors: ['#006600', '#000000', '#0070CC', '#00008A', '#8C8C8C', '#1EB611', '#FF9655', '#FFF263', '#6AF9C4'],
            chart: {
                renderTo: 'tschart_' + me.id,
                className: 'chartfitlayout',
                zoomType: 'xy',
                spacingRight: spacingRight,
                //margin: chartMargin, // [35, 15, 65, 65],  // for legend on the bottom of the chart
                //marginTop:top,
                //marginRight: marginright,
                marginBottom: 150,
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
                }
            },
            title: {
                text: json.title,
                align: 'center',
                //y: 50,
                style: {
                    color: json.chart_title_font_color,   // '#000',
                    font: 'Arial, Verdana, Helvetica, sans-serif',
                    "font-weight": 'bold',
                    fontSize: json.chart_title_font_size    // '34px'
                }
            },
            subtitle: {
                text: json.subtitle,
                align: 'center',
                //y: 65,
                style: {
                    color: json.chart_subtitle_font_color,    // '#666666',
                    font: 'Arial, Verdana, Helvetica, sans-serif',
                    "font-weight": 'bold',
                    fontSize: json.chart_subtitle_font_size // '24px'
                }
            },
            xAxis: [{
                type: 'datetime',
                //tickmarkPlacement: 'on', // on between  - For categorized axes only!
                startOnTick: false,
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
            }],
            yAxis: Yaxes,
            tooltip: {
                shared: true,
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
                    font: 'Arial, Verdana, Helvetica, sans-serif',
                    "font-weight": 'bold',
                    fontSize: json.legend_title_font_size,     // '18px',
                    color: json.legend_title_font_color     //'black'
                }

            },
            series: timeseries
        });

        me.tschart.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tschart.redraw();
    },

    generateChart: function(){
        this.getTimeseries(this.createChart);
    },
    refreshChart: function(){
        var me = this.getView();
        var timeseriesselections = Ext.getCmp('analysismain').getController().getTimeseriesSelections();
        me.selectedTimeseries = timeseriesselections.selectedTimeseries;
        me.yearTS = timeseriesselections.yearTS;
        me.tsFromPeriod = timeseriesselections.tsFromPeriod;
        me.tsToPeriod = timeseriesselections.tsToPeriod;
        me.wkt = timeseriesselections.wkt;

        me.tschart.destroy();
        //this.createChart(this);
        this.getTimeseries(this.createChart);
    },
    openChartProperties: function(callComponent) {
        var me = this;
        //var layerrecord = callComponent.layerrecord;

        //var texteditor = new Ext.grid.GridEditor(new Ext.form.TextField({allowBlank: false,selectOnFocus: true}));
        //var numbereditor = new Ext.grid.GridEditor(new Ext.form.NumberField({allowBlank: false,selectOnFocus: true}));
        //
        //var cedit = new Ext.grid.GridEditor(new Ext.ux.ColorField({allowBlank: false,selectOnFocus: true}));
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

        var drawproperties = Ext.create('Ext.panel.Panel', {
            title: 'Edit chart draw properties',
            width: 450,
            autoHeight: true,
            margin: '0 0 10 0',
            maximizable: false,
            collapsible: true,
            resizable: true,
            //constrainHeader: true,
            //autoWidth: true,
            //autoHeight: true,
            layout: 'fit',
            hidden: true,
            floating: true,
            defaultAlign: 'bl-bl',
            closable: true,
            closeAction: 'hide',
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
                    //nameField: 'Property',
                    //width: 400,
                    nameColumnWidth: 180,
                    sortableColumns: false,
                    source: {
                        chart_width: '',
                        chart_height: '',
                        chart_title: '',   // layerrecord.get('polygon_outlinecolor'),
                        chart_title_colour: '',
                        chart_title_font_size: '',
                        chart_subtitle: '',
                        chart_subtitle_colour: '',
                        chart_subtitle_font_size: '',

                        yaxe1_title: '',
                        yaxe1_font_size: '',
                        yaxe1_colour: '',
                        yaxe1_min: '',
                        yaxe1_max: '',

                        yaxe2_title: '',
                        yaxe2_font_size: '',
                        yaxe2_colour: '',
                        yaxe2_min: '',
                        yaxe2_max: '',

                        legend_font_size: '',
                        xaxe_font_size: ''
                    },
                    sourceConfig: {
                        chart_width: {
                            displayName: 'Chart width (in px)',
                            type: 'number'
                        },
                        chart_height: {
                            displayName: 'Chart height (in px)',
                            type: 'number'
                        },
                        chart_title: {
                            displayName: 'Title',
                            type: 'text'
                        },
                        chart_title_colour: {
                            displayName: 'Title colour',
                            editor: {
                                xtype: 'mycolorpicker'
                            }
                            ,renderer: crenderer
                        },
                        chart_title_font_size: {
                            displayName: 'Title font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        chart_subtitle: {
                            displayName: 'Sub title',
                            type: 'text'    // 'number'
                        },
                        chart_subtitle_colour: {
                            displayName: 'Sub title colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        chart_subtitle_font_size: {
                            displayName: 'Sub title font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe1_title: {
                            displayName: 'yAxe 1 title',
                            type: 'text'
                        },
                        yaxe1_font_size: {
                            displayName: 'yAxe 1 font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe1_colour: {
                            displayName: 'yAxe 1 colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        yaxe1_min: {
                            displayName: 'yAxe 1 min',
                            type: 'number'
                        },
                        yaxe1_max: {
                            displayName: 'yAxe 1 max',
                            type: 'number'
                        },
                        yaxe2_title: {
                            displayName: 'yAxe 2 title',
                            type: 'text'
                        },
                        yaxe2_font_size: {
                            displayName: 'yAxe 2 font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        yaxe2_colour: {
                            displayName: 'yAxe 2 colour',
                            editor: {
                                xtype: 'mycolorpicker'
                                //,floating: false
                            }
                            ,renderer: crenderer
                        },
                        yaxe2_min: {
                            displayName: 'yAxe 2 min',
                            type: 'number'
                        },
                        yaxe2_max: {
                            displayName: 'yAxe 2 max',
                            type: 'number'
                        },
                        legend_font_size: {
                            displayName: 'Legend font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        },
                        xaxe_font_size: {
                            displayName: 'xAxe font size',
                            editor: {
                                xtype: 'combobox',
                                store: [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72],
                                forceSelection: true
                            }
                        }
                    },
                    //customEditors: {
                    //    myProp: new Ext.grid.GridEditor(combo, {})
                    //},
                    //customRenders: {
                    //    myProp: function(value){
                    //        var record = combo.findRecord(combo.valueField, value);
                    //        return record ? record.get(combo.displayField) : combo.valueNotFoundText;
                    //    }
                    //},
                    listeners: {
                        propertychange: function( source, recordId, value, oldValue, eOpts ){
                            //console.info(source);
                            //console.info(recordId);
                            //console.info(value);
                            //console.info(oldValue.toLowerCase());
                            //if (value != oldValue)
                                //layerrecord.set(recordId, value)
                        }
                    }
                },
                {   title: esapp.Utils.getTranslation('Timeseries draw properties'),
                    xtype: 'grid'

                }
            ]
        });
        me.getView().add(drawproperties);
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

        // Get the cart's SVG code
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
        image.src = 'data:image/svg+xml;base64,' + window.btoa(svg);


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

    ,_saveChart: function() {
        // FROM : http://willkoehler.net/2014/11/07/client-side-solution-for-downloading-highcharts-charts-as-images.html

        function download(canvas, filename) {
            download_in_ie(canvas, filename) || download_with_link(canvas, filename);
        }

        // Works in IE10 and newer
        function download_in_ie(canvas, filename) {
            return(navigator.msSaveOrOpenBlob && navigator.msSaveOrOpenBlob(canvas.msToBlob(), filename));
        }

        // Works in Chrome and FF. Safari just opens image in current window, since .download attribute is not supported
        function download_with_link(canvas, filename) {
            var a = document.createElement('a')
            a.download = filename
            a.href = canvas.toDataURL("image/png")
            document.body.appendChild(a);
            a.click();
            a.remove();
        }

        var chart = this.getView().tschart;

        var render_width = 1000;
        var render_height = render_width * chart.chartHeight / chart.chartWidth;

        var svg = chart.getSVG({
            exporting: {
                sourceWidth: chart.chartWidth,
                sourceHeight: chart.chartHeight
            }
        });

        var canvas = document.createElement('canvas');
        canvas.height = render_height;
        canvas.width = render_width;

        canvg(canvas, svg, {
            scaleWidth: render_width,
            scaleHeight: render_height,
            ignoreDimensions: true
        });

        download(canvas, this.getView().filename + '.png');

    }
});
