
Ext.define("esapp.view.widgets.datasetCompletenessChart",{
    "extend": "Ext.container.Container",

    requires: [
        'esapp.view.widgets.datasetCompletenessChartModel',
        'esapp.view.widgets.datasetCompletenessChartController',

        'Ext.data.JsonStore'
    ],

    "controller": "widgets-datasetcompletenesschart",
    "viewModel": {
        "type": "widgets-datasetcompletenesschart"
    },
    xtype: 'datasetchart',
    //id: 'dschart',

    //configs with auto generated getter/setter methods
    config: {
        //id: '',
        firstdate:'',
        lastdate:'',
        totfiles:0,
        missingfiles:0,
        series: [],
        tooltipintervals: ''
    },

    hideMode : 'display',
    margin:0,
    bodyPadding:0,
    height: 45,
    width: 350,
    bufferedRenderer: true,

    initComponent: function() {
        var me = this,
            fontsize = 10;

        //me.id = 'dschart_' + this.id;
        //widget.id = record.get('productid') + '_' + record.get('mapsetcode') + '_' + record.get('subproductcode');

        //me.items = {
        //    xtype: 'container',
        //
        //}
        me.listeners = {
            beforerender: function () {
                //console.info('datasetCompletenessChart: beforerender event called');
                //var record = me.getWidgetRecord();
                //console.info(record);
                //me.setId('dschart_' + record.get('productcode') + '_' + record.get('version').replace('.', '') + '_' + record.get('mapsetcode') + '_' + record.get('subproductcode'));
                //me.id = 'dschart_' + this.id;
            },
            afterrender: function () {
                //console.info('datasetCompletenessChart: afterrender event called');
                var missingFilesText = '';
                if(me.missingfiles>0)
                   missingFilesText = 'Missing: ' + me.missingfiles;

                var totFilesText = '';
                if(me.totfiles>0)
                   totFilesText = 'Files: ' + me.totfiles;
                else
                    totFilesText = '<span style="color:#808080">Not any data</span>';   // 'Not any data';
                //console.info(me.id);
                //if (Ext.getCmp(me.id)) {
                    me.datasetcompletenesschart = new Highcharts.Chart({
                        chart: {
                            renderTo: me.getId(),
                            type: 'bar',
                            height: 45,
                            width: 350,
                            spacing: [5, 20, 0, 20]
                        },
                        credits: {
                            enabled: false
                        },
                        exporting: {
                            enabled: false
                        },
                        title: {
                            text: ''
                        },
                        tooltip: {
                            //shared: true
                            enabled: false
                        },
                        labels: {
                            items: [{
                                html: me.firstdate,
                                style: {
                                    left: '-20px',
                                    top: '-3px',
                                    color: '#0000',
                                    fontSize: '10px'
                                }
                            }, {
                                html: totFilesText,
                                style: {
                                    left: '80px',
                                    top: '-4px',
                                    color: '#0000',
                                    fontSize: '10px'
                                }
                            }, {
                                html: missingFilesText,
                                style: {
                                    left: '170px',
                                    top: '-4px',
                                    color: '#FF0000',
                                    fontSize: '10px'
                                }
                            }, {
                                html: me.lastdate,
                                style: {
                                    left: '260px',
                                    top: '-3px',
                                    color: '#0000',
                                    fontSize: '10px'
                                }
                            }]
                        },

                        xAxis: {
                            title: {
                                text: ''
                            },
                            labels: {
                                enabled: false
                            },
                            gridLineWidth: 0,
                            lineWidth: 0,
                            tickWidth: 0
                            , categories: ['datasetcompleteness']
                        },
                        yAxis: {
                            min: 0,
                            max: 100,
                            reversedStacks: false,
                            gridLineWidth: 0,
                            lineWidth: 0,
                            title: {
                                text: ''
                            },
                            labels: {
                                enabled: false
                            }
                        },
                        legend: {
                            enabled: false
                        },
                        plotOptions: {
                            series: {
                                stacking: 'normal'
                            }
                        },
                        series: me.series
                        //series: [{
                        //    color: '#81AF34',
                        //    data: [50]
                        //}, {
                        //    color: '#808080',
                        //    data: [10]
                        //}, {
                        //    color: '#81AF34',
                        //    data: [2]
                        //}, {
                        //    color: '#808080',
                        //    data: [8]
                        //}, {
                        //    color: '#FF0000',
                        //    data: [30]
                        //}]
                    });
                //}

                var tip = Ext.create('Ext.tip.ToolTip', {
                    target: me.getId(),
                    trackMouse: true,
                    html:  me.tooltipintervals // Tip content
                });
            }
        }

        me.callParent();

    }
});
