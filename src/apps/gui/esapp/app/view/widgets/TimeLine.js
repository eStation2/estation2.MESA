
Ext.define("esapp.view.widgets.TimeLine",{
    "extend": "Ext.container.Container",
    "controller": "widgets-timeline",
    "viewModel": {
        "type": "widgets-timeline"
    },
    xtype: 'time-line-chart',

    requires: [
        'esapp.view.widgets.TimeLineModel',
        'esapp.view.widgets.TimeLineController'
        //,'Highcharts.StockChart'
    ],
    id: 'time-line_chart',
    layout: 'fit',
    product_date_format: null,

    initComponent: function () {
        var me = this;

        me.id = this.id;
        me.border= false;
        me.bodyBorder = false;
        me.layout = this.layout;

        //me.listeners = {
        //    afterrender: function () {
        //        me.timelinechart = new Highcharts.StockChart({
        //            chart: {
        //                renderTo: me.id,
        //                //reference : 'time-line_chart' + me.getView().id,
        //                margin: [8, 30, 10, 30],
        //                spacingBottom: 10,
        //                spacingTop: 8,
        //                spacingLeft: 5,
        //                spacingRight: 30,
        //                height: 115,
        //                width:580
        //            },
        //            credits: {
        //                enabled: false
        //            },
        //            exporting: {
        //                enabled: false
        //            },
        //            scrollbar: {
        //                enabled: false
        //            },
        //
        //            rangeSelector: {
        //                selected: 1,
        //                inputEnabled: true,
        //                buttons: [{
        //                    type: 'ytd',
        //                    text: 'YTD'
        //                }, {
        //                    type: 'year',
        //                    count: 1,
        //                    text: '1y'
        //                }],
        //                buttonTheme: { // styles for the buttons
        //                    fill: 'none',
        //                    stroke: 'none',
        //                    'stroke-width': 0,
        //                    r: 8,
        //                    style: {
        //                        color: '#039',
        //                        fontWeight: 'bold'
        //                    },
        //                    states: {
        //                        hover: {
        //                        },
        //                        select: {
        //                            fill: '#039',
        //                            style: {
        //                                color: 'white'
        //                            }
        //                        }
        //                        // disabled: { ... }
        //                    }
        //                },
        //                inputStyle: {
        //                    color: '#039',
        //                    fontWeight: 'bold'
        //                },
        //                labelStyle: {
        //                    color: 'silver',
        //                    fontWeight: 'bold'
        //                }
        //            },
        //
        //            navigator: {
        //                height: 20,
        //                margin: 5,
        //                adaptToUpdatedData: false
        //            },
        //
        //            tooltip: {
        //                followPointer: true,
        //                formatter: function () {
        //                    return Highcharts.dateFormat('%d %b %Y', this.x, true);
        //                }
        //            },
        //            xAxis: {
        //                height: 35,
        //                dateTimeLabelFormats: me.dateTimeLabelFormats
        //                //labels: {
        //                //    formatter: function () {
        //                //        return Highcharts.dateFormat('%b', this.value, true);
        //                //    }
        //                //}
        //            },
        //
        //            yAxis: [{
        //                showFirstLabel: false,
        //                showLastLabel: false,
        //                labels: {
        //                    align: 'right',
        //                    x: -3
        //                },
        //                max: 1,
        //                //top: '65%',
        //                height: 25 // '40%',
        //                //offset: 0,
        //                //lineWidth: 2
        //            }],
        //
        //            series: [{
        //                type: 'column',
        //                name: 'Date',
        //                data: [],
        //                yAxis: 0,
        //                turboThreshold: 0
        //                // ,dataGrouping: {
        //                //     units: groupingUnits
        //                // }
        //            }]
        //        });
        //    }
        //};

        me.callParent();
    }
    ,createTimeLineChart: function () {
        var me = this;

        //console.info(me.product_date_format);
        if (me.product_date_format == 'MMDD'){
            me.dateTimeLabelFormats = {
                day: "%d-%b",
                week: "%d-%b",
                month: "%b",
                year: "%b'%y"
            };
            me.tooltipFormater = function () {
                return Highcharts.dateFormat('%d %b', this.x, true);
            }
        }
        else {
            me.dateTimeLabelFormats = {
                millisecond: '%H:%M:%S.%L',
                second: '%H:%M:%S',
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%e. %b',
                week: '%e. %b',
                month: '%b \'%y',
                year: '%Y'
            };
            me.tooltipFormater = function () {
                return Highcharts.dateFormat('%d %b %Y', this.x, true);
            }
        }

        me.timelinechart = new Highcharts.StockChart({
            chart: {
                renderTo: me.id,
                // //reference : 'time-line_chart' + me.getView().id,
                // margin: [3, 3, 3, 3],
                // padding: [2, 2, 2, 2],
                // margin: [8, 30, 15, 30],
                spacingBottom: 2,
                spacingTop: 8,
                spacingLeft: 5,
                spacingRight: 20
                // height: 115
                // width:580
            },
            credits: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            scrollbar: {
                enabled: true,
                liveRedraw: false
            },

            plotOptions: {
                series: {
                    cursor: 'pointer'
                }
            },
            rangeSelector: {
                // allButtonsEnabled: true,
                selected: 4,
                buttons: [{
                    type: 'month',
                    count: 1,
                    text: '1m'
                }, {
                    type: 'month',
                    count: 2,
                    text: '2m'
                }, {
                    type: 'month',
                    count: 3,
                    text: '3m'
                }, {
                    type: 'month',
                    count: 6,
                    text: '6m'
                }, {
                    type: 'year',
                    count: 1,
                    text: '1y'
                }, {
                    type: 'ytd',
                    text: 'YTD'
                }],
                buttonTheme: { // styles for the buttons
                    fill: 'none',
                    stroke: 'none',
                    'stroke-width': 0,
                    r: 8,
                    style: {
                        color: '#039',
                        fontWeight: 'bold'
                    },
                    states: {
                        hover: {
                        },
                        select: {
                            fill: '#039',
                            style: {
                                color: 'white'
                            }
                        }
                        // disabled: { ... }
                    }
                },
                height: 27,
                inputEnabled: true,
                inputBoxWidth: 100,
                inputBoxHeight: 16,
                inputStyle: {
                    color: '#039',
                    fontWeight: 'bold'
                },
                labelStyle: {
                    color: 'silver',
                    fontWeight: 'bold'
                }
            },

            navigator: {
                height: 25
                // margin: 5,
                // ,adaptToUpdatedData: false   # do not adapt to changes manually made to From-To input fields.
            },

            tooltip: {
                followPointer: true,
                formatter: me.tooltipFormater
            },
            xAxis: {
                height: 25,
                dateTimeLabelFormats: me.dateTimeLabelFormats
                //labels: {
                //    formatter: function () {
                //        return Highcharts.dateFormat('%b', this.value, true);
                //    }
                //}
            },

            yAxis: [{
                showFirstLabel: false,
                showLastLabel: false,
                labels: {
                    align: 'right',
                    x: -3
                },
                max: 1,
                height: 25
                //offset: 0,
                //lineWidth: 2
            }],

            series: [{
                type: 'column',
                name: 'Date',
                data: [],
                yAxis: 0,
                turboThreshold: 18000   // from 1982-2030 ~50 years daily products
                // ,dataGrouping: {
                //     units: groupingUnits
                // }
            }]
        });

        //me.callParent();
    }
});
