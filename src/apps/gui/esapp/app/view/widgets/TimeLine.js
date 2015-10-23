
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

    initComponent: function () {
        var me = this;

        me.id = this.id;
        me.border= false;
        me.bodyBorder = false;
        me.layout = this.layout;

        me.listeners = {
            afterrender: function () {
                me.timelinechart = new Highcharts.StockChart({
                    chart: {
                        renderTo: me.id,
                        //reference : 'time-line_chart' + me.getView().id,
                        margin: [8, 25, 15, 25],
                        spacingBottom: 10,
                        spacingTop: 8,
                        spacingLeft: 5,
                        spacingRight: 20,
                        height: 115,
                        width:600
                    },
                    credits: {
                        enabled: false
                    },
                    exporting: {
                        enabled: false
                    },
                    rangeSelector: {
                        selected: 1,
                        inputEnabled: true,
                        buttons: [{
                            type: 'ytd',
                            text: 'YTD'
                        }, {
                            type: 'year',
                            count: 1,
                            text: '1y'
                        }]
                    },

                    navigator: {
                        height: 20,
                        margin: 5,
                        adaptToUpdatedData: false
                    },

                    scrollbar: {
                        enabled: false
                    },
                    tooltip: {
                        followPointer: true,
                        formatter: function () {
                            return Highcharts.dateFormat('%d %b %Y', this.x, true);
                        }
                    },
                    xAxis: {
                        height: 20
                    },

                    yAxis: [{
                        showFirstLabel: false,
                        showLastLabel: false,
                        labels: {
                            align: 'right',
                            x: -3
                        },
                        max: 1,
                        //top: '65%',
                        height: 25 // '40%',
                        //offset: 0,
                        //lineWidth: 2
                    }],

                    series: [{
                        type: 'column',
                        name: 'Date',
                        data: [],
                        yAxis: 0
                        // ,dataGrouping: {
                        //     units: groupingUnits
                        // }
                    }]
                });
            }
        }

        me.callParent();
    }
});
