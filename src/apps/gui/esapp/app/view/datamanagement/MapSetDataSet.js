
Ext.define("esapp.view.datamanagement.MapSetDataSet",{
    "extend": "Ext.grid.Panel",

    //"controller": "datamanagement-mapsetdataset",
    //
    //"viewModel": {
    //    "type": "datamanagement-mapsetdataset"
    //},

    "xtype"  : 'mapsetdatasetgrid',

    requires: [
        //'esapp.view.datamanagement.MapSetDataSetModel',
        //'esapp.view.datamanagement.MapSetDataSetController',

        'esapp.view.widgets.datasetCompletenessChart',

        'Ext.grid.column.Action'
        // 'Ext.grid.column.Widget'
    ],

    // store: 'mapsetdatasets',
    store : {
        model: 'esapp.model.MapSetDataSet'
        ,sorters: [{property: 'display_index', direction: 'ASC'}]
    },

    // selModel: {listeners:{}},
    // selModel: {
    //    selType: 'rowmodel',
    //    mode: 'SINGLE'
    // },
    // selModel: null,
    // bufferedRenderer: true,

    // viewConfig: {
    //     stripeRows: false,
    //     enableTextSelection: true,
    //     draggable: false,
    //     markDirty: false,
    //     resizable: false,
    //     disableSelection: true,
    //     trackOver: false,
    //     preserveScrollOnRefresh: false,
    //     preserveScrollOnReload: false,
    //     focusable: false,
    //     forceFit: true
    // },

    hideHeaders: true,
    columnLines: false,
    rowLines:false,
    // focusable: false,
    // forceFit: true,
    scrollToTop: false,
    alwaysOnTop: true,
    focusOnToFront: false,
    // maxHeight: 360,
    // scrollable: 'vertical',

    margin: '0 0 10 0',    // (top, right, bottom, left).
    // minHeight: 55,

    // layout: 'fit',

    initComponent: function () {
        var me = this;

        me.viewConfig = {
            stripeRows: false,
            enableTextSelection: true,
            draggable: false,
            markDirty: false,
            resizable: false,
            disableSelection: true,
            trackOver: false,
            preserveScrollOnRefresh: true,
            preserveScrollOnReload: true,
            focusable: true,
            forceFit: true,
            listeners: {
                render: function (view) {
                    // console.info(view);
                    view.tooltip = Ext.create('Ext.tip.ToolTip', {
                        id: view.getId() + '_completness_tooltip',
                        // The overall target element.
                        target: view.getEl(),
                        // triggerElement: view.getEl(),
                        // Each grid row causes its own seperate show and hide.
                        delegate: view.itemSelector,
                        // Render immediately so that tip.body can be referenced prior to the first show.
                        // renderTo: Ext.getBody(),
                        maxHeight: 350,
                        autoScroll: true,
                        // autoRender: true,
                        hidden: false,
                        disabled: true,
                        trackMouse: true,
                        mouseOffset: [-5, 0],
                        autoHide: false,
                        showDelay: 100,
                        // hideDelay: 5000,
                        // dismissDelay: 5000, // auto hide after 5 seconds
                        closable: true,
                        anchorToTarget: false,
                        // anchor: 'left',
                        padding: 5,
                        listeners: {
                            close: function (tip) {
                                // tip.disable();
                                tip.hide();
                            },
                            // Change content dynamically depending on which element triggered the show.
                            beforeshow: function (tip) {
                                // console.info(tip.triggerElement);
                                if (esapp.Utils.objectExists(tip.triggerElement)) {
                                    var datasetinterval = '',
                                        datasetForTipText,
                                        tooltipintervals,
                                        mapsetdatasetrecord = view.getRecord(tip.triggerElement),   // view.dataSource.getData().items[0],   //  view.dataSource.data.items[0], //
                                        completeness = mapsetdatasetrecord.get('datasetcompleteness');

                                    var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
                                    Ext.each(completenessTooltips, function (item) {
                                        // item.disable();
                                        if (item != tip) {
                                            item.hide();
                                        }
                                    });

                                    datasetForTipText = '<b>' + esapp.Utils.getTranslation('dataset_intervals_for') + ':</br>' +
                                        mapsetdatasetrecord.get('productcode') + ' - ' +
                                        mapsetdatasetrecord.get('version') + ' - ' +
                                        (mapsetdatasetrecord.get('mapset_descriptive_name') || mapsetdatasetrecord.get('mapsetname')) + ' - ' +
                                        mapsetdatasetrecord.get('subproductcode') + '</b></br></br>';

                                    tooltipintervals = datasetForTipText;
                                    if (mapsetdatasetrecord.get('frequency_id') == 'singlefile' && completeness.totfiles == 1 && completeness.missingfiles == 0) {
                                        datasetinterval = '<span style="color:#81AF34">' + esapp.Utils.getTranslation('singlefile') + '</span>';
                                        tooltipintervals += datasetinterval;
                                    }
                                    else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
                                        datasetinterval = '<span style="color:#808080">' + esapp.Utils.getTranslation('notanydata') + '</span>';
                                        tooltipintervals += datasetinterval;
                                    }
                                    else {
                                        completeness.intervals.forEach(function (interval) {
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
                                            datasetinterval = '<span style="color:' + color + '">' + esapp.Utils.getTranslation('from') + ' ' + interval.fromdate + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.todate + ' - ' + intervaltype + '</span></br>';
                                            tooltipintervals += datasetinterval;
                                        });
                                    }

                                    tip.update(tooltipintervals);
                                }

                                // tip.on('show', function(){
                                //     Ext.defer(tip.hide, 20000, tip);
                                // }, tip, {single: true});
                            }
                        }
                    });
                    // createTooltip(grid.getView());
                    // Ext.util.Observable.capture(view, function(e){console.log(view.id + ': ' + e);});
                }
            }
        };

        me.listeners = {
            // render: function(grid){
            //     console.info(grid.getView());
            //     view.tooltip = Ext.create('Ext.tip.ToolTip', {
            //         id: view.getId() + '_completness_tooltip',
            //         // The overall target element.
            //         target: view.getEl(),
            //         // triggerElement: view.getEl(),
            //         // Each grid row causes its own seperate show and hide.
            //         delegate: view.itemSelector,
            //         // Render immediately so that tip.body can be referenced prior to the first show.
            //         // renderTo: Ext.getBody(),
            //         maxHeight: 350,
            //         autoScroll: true,
            //         // autoRender: true,
            //         hidden: false,
            //         disabled: true,
            //         trackMouse: true,
            //         mouseOffset : [-5,0],
            //         autoHide: false,
            //         showDelay: 100,
            //         // hideDelay: 5000,
            //         // dismissDelay: 5000, // auto hide after 5 seconds
            //         closable: true,
            //         anchorToTarget: false,
            //         // anchor: 'left',
            //         padding: 5,
            //         listeners: {
            //             close: function(tip) {
            //                 // tip.disable();
            //                 tip.hide();
            //             },
            //             // Change content dynamically depending on which element triggered the show.
            //             beforeshow: function (tip) {
            //                 // console.info(tip.triggerElement);
            //                 if (esapp.Utils.objectExists(tip.triggerElement)){
            //                     var datasetinterval = '',
            //                         datasetForTipText,
            //                         tooltipintervals,
            //                         mapsetdatasetrecord = view.getRecord(tip.triggerElement),   // view.dataSource.getData().items[0],   //  view.dataSource.data.items[0], //
            //                         completeness = mapsetdatasetrecord.get('datasetcompleteness');
            //
            //                     var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
            //                     Ext.each(completenessTooltips, function(item) {
            //                        // item.disable();
            //                         if (item != tip){
            //                             item.hide();
            //                         }
            //                     });
            //
            //                     datasetForTipText = '<b>' + esapp.Utils.getTranslation('dataset_intervals_for') + ':</br>' +
            //                         mapsetdatasetrecord.get('productcode') + ' - ' +
            //                         mapsetdatasetrecord.get('version') + ' - ' +
            //                         (mapsetdatasetrecord.get('mapset_descriptive_name') || mapsetdatasetrecord.get('mapsetname')) + ' - ' +
            //                         mapsetdatasetrecord.get('subproductcode') + '</b></br></br>';
            //
            //                     tooltipintervals = datasetForTipText;
            //                     if (mapsetdatasetrecord.get('frequency_id')=='singlefile' && completeness.totfiles == 1 && completeness.missingfiles == 0){
            //                         datasetinterval = '<span style="color:#81AF34">'+ esapp.Utils.getTranslation('singlefile') + '</span>';
            //                         tooltipintervals += datasetinterval;
            //                     }
            //                     else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
            //                         datasetinterval = '<span style="color:#808080">'+ esapp.Utils.getTranslation('notanydata') + '</span>';
            //                         tooltipintervals += datasetinterval;
            //                     }
            //                     else {
            //                         completeness.intervals.forEach(function (interval) {
            //                             var color, intervaltype = '';
            //                             if (interval.intervaltype == 'present') {
            //                                 color = '#81AF34'; // green
            //                                 intervaltype = esapp.Utils.getTranslation('present');
            //                             }
            //                             if (interval.intervaltype == 'missing') {
            //                                 color = '#FF0000'; // red
            //                                 intervaltype = esapp.Utils.getTranslation('missing');
            //                             }
            //                             if (interval.intervaltype == 'permanent-missing') {
            //                                 color = '#808080'; // gray
            //                                 intervaltype = esapp.Utils.getTranslation('permanent-missing');
            //                             }
            //                             datasetinterval = '<span style="color:'+color+'">' + esapp.Utils.getTranslation('from') + ' ' + interval.fromdate + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.todate + ' - ' + intervaltype + '</span></br>';
            //                             tooltipintervals += datasetinterval;
            //                         });
            //                     }
            //
            //                     tip.update(tooltipintervals);
            //                 }
            //
            //                 // tip.on('show', function(){
            //                 //     Ext.defer(tip.hide, 20000, tip);
            //                 // }, tip, {single: true});
            //             }
            //         }
            //     });
            //     // createTooltip(grid.getView());
            //     // Ext.util.Observable.capture(view, function(e){console.log(view.id + ': ' + e);});
            // },
            rowmousedown: function(view, record, element, rowIndex, e, eOpts){
                // console.info('rowclick');
                // console.info(view);
                // // view.fireEvent('scrolltoselection');
                //
                // console.info('scrolltoselection');
                // // var record = view.getSelection();
                // console.info(record);
                // if (record.length > 0)
                //     view.ensureVisible(record[0], {focus: true});
                // view.focusRow(record);

                var widgettooltip = Ext.getCmp(view.getId() + '_completness_tooltip');
                var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
                Ext.each(completenessTooltips, function(item) {
                    if (item != widgettooltip){
                        item.hide();
                    }
                });
                if (esapp.Utils.objectExists(widgettooltip)){
                    widgettooltip.trackMouse = false;
                }

            },
            // scrolltoselection: function (view) {
            //     console.info('scrolltoselection');
            //
            //     var record = view.getSelection();
            //     console.info(record);
            //     if (record.length > 0)
            //         view.ensureVisible(record[0], {focus: true});
            // },
            itemmouseenter: function(view, record, el, rowidx){
                var widgettooltip = Ext.getCmp(view.getId() + '_completness_tooltip');
                // console.info('itemmouseenter');
                // console.info(view);
                // console.info(record);
                // console.info(el);
                // console.info(rowidx);
                // console.info(widgettooltip);
                // view.focusRow(rowidx);
                // view.getRow(rowidx).scrollIntoView();
                widgettooltip.trackMouse = true;
                if (widgettooltip.disabled){
                    widgettooltip.enable();
                }
            },
            itemmouseleave: function(view){
                // console.info('itemmouseleave');
                var widgettooltip = Ext.getCmp(view.getId() + '_completness_tooltip');
                if (!widgettooltip.disabled && widgettooltip.trackMouse){
                    widgettooltip.disable();
                }
            }
            // ,rowfocus: {}
        };

        // function createTooltip(view) {
        //     view.tooltip = Ext.create('Ext.tip.ToolTip', {
        //         id: view.getId() + '_completness_tooltip',
        //         // The overall target element.
        //         target: view.getEl(),
        //         // triggerElement: view.getEl(),
        //         // Each grid row causes its own seperate show and hide.
        //         delegate: view.itemSelector,
        //         // Render immediately so that tip.body can be referenced prior to the first show.
        //         // renderTo: Ext.getBody(),
        //         maxHeight: 350,
        //         autoScroll: true,
        //         // autoRender: true,
        //         hidden: false,
        //         disabled: true,
        //         trackMouse: true,
        //         mouseOffset : [-5,0],
        //         autoHide: false,
        //         showDelay: 100,
        //         // hideDelay: 5000,
        //         // dismissDelay: 5000, // auto hide after 5 seconds
        //         closable: true,
        //         anchorToTarget: false,
        //         // anchor: 'left',
        //         padding: 5,
        //         listeners: {
        //             close: function(tip) {
        //                 // tip.disable();
        //                 tip.hide();
        //             },
        //             // Change content dynamically depending on which element triggered the show.
        //             beforeshow: function (tip) {
        //                 // console.info(tip.triggerElement);
        //                 if (esapp.Utils.objectExists(tip.triggerElement)){
        //                     var datasetinterval = '',
        //                         datasetForTipText,
        //                         tooltipintervals,
        //                         mapsetdatasetrecord = view.getRecord(tip.triggerElement),   // view.dataSource.getData().items[0],   //  view.dataSource.data.items[0], //
        //                         completeness = mapsetdatasetrecord.get('datasetcompleteness');
        //
        //                     var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
        //                     Ext.each(completenessTooltips, function(item) {
        //                        // item.disable();
        //                         if (item != tip){
        //                             item.hide();
        //                         }
        //                     });
        //
        //                     datasetForTipText = '<b>' + esapp.Utils.getTranslation('dataset_intervals_for') + ':</br>' +
        //                         mapsetdatasetrecord.get('productcode') + ' - ' +
        //                         mapsetdatasetrecord.get('version') + ' - ' +
        //                         (mapsetdatasetrecord.get('mapset_descriptive_name') || mapsetdatasetrecord.get('mapsetname')) + ' - ' +
        //                         mapsetdatasetrecord.get('subproductcode') + '</b></br></br>';
        //
        //                     tooltipintervals = datasetForTipText;
        //                     if (mapsetdatasetrecord.get('frequency_id')=='singlefile' && completeness.totfiles == 1 && completeness.missingfiles == 0){
        //                         datasetinterval = '<span style="color:#81AF34">'+ esapp.Utils.getTranslation('singlefile') + '</span>';
        //                         tooltipintervals += datasetinterval;
        //                     }
        //                     else if (completeness.totfiles < 2 && completeness.missingfiles < 2) {
        //                         datasetinterval = '<span style="color:#808080">'+ esapp.Utils.getTranslation('notanydata') + '</span>';
        //                         tooltipintervals += datasetinterval;
        //                     }
        //                     else {
        //                         completeness.intervals.forEach(function (interval) {
        //                             var color, intervaltype = '';
        //                             if (interval.intervaltype == 'present') {
        //                                 color = '#81AF34'; // green
        //                                 intervaltype = esapp.Utils.getTranslation('present');
        //                             }
        //                             if (interval.intervaltype == 'missing') {
        //                                 color = '#FF0000'; // red
        //                                 intervaltype = esapp.Utils.getTranslation('missing');
        //                             }
        //                             if (interval.intervaltype == 'permanent-missing') {
        //                                 color = '#808080'; // gray
        //                                 intervaltype = esapp.Utils.getTranslation('permanent-missing');
        //                             }
        //                             datasetinterval = '<span style="color:'+color+'">' + esapp.Utils.getTranslation('from') + ' ' + interval.fromdate + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.todate + ' - ' + intervaltype + '</span></br>';
        //                             tooltipintervals += datasetinterval;
        //                         });
        //                     }
        //
        //                     tip.update(tooltipintervals);
        //                 }
        //
        //                 // tip.on('show', function(){
        //                 //     Ext.defer(tip.hide, 20000, tip);
        //                 // }, tip, {single: true});
        //             }
        //         }
        //     });
        // }

        me.defaults = {
            menuDisabled: true,
            draggable:false,
            groupable:false,
            hideable: false,
            variableRowHeight: true
        };

        me.columns = [{
            // header: '', // 'Sub Product Code',
            // dataIndex: 'subproductcode',
            xtype:'templatecolumn',
            header: '', // 'Productcode',
            // tpl: new Ext.XTemplate(
            //         '<b>{descriptive_name}</b>' +
            //         '</br>' +
            //         '<b class="smalltext" style="color:darkgrey;">{subproductcode}</b>' +
            //         '</br>'
            //     ),
            tpl: new Ext.XTemplate(
                '<b>{descriptive_name}</b>' +
                '</br>' +
                '<b class="smalltext"style="color:darkgrey;">{productcode}</b>' +
                '<tpl if="version != \'undefined\'">',
                '<b class="smalltext" style="color:darkgrey;"> - {version} </b>',
                '</tpl>',
                '<b class="smalltext"style="color:darkgrey;"> - {subproductcode}</b>'
                // '<BR>(display_index: <b style="color:black">{display_index}</b>)'
            ),

            width: 250,
            cellWrap:true
        }, {
            // header: '', // 'Status',
            width: 360,
            xtype: 'templatecolumn',
            // dataIndex: 'datasetcompletenessimage',
            tpl: new Ext.XTemplate(
                    '<img style="cursor: pointer;" src="{datasetcompletenessimage}" />'
                )
            ,listeners: {
                click: function(view){
                    var widgettooltip = Ext.getCmp(view.getId() + '_completness_tooltip');
                    var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
                    Ext.each(completenessTooltips, function(item) {
                       // item.disable();
                        if (item != widgettooltip){
                            item.hide();
                        }
                    });
                    if (esapp.Utils.objectExists(widgettooltip)){
                        widgettooltip.trackMouse = false;
                        // widgettooltip.enable();
                        // widgettooltip.show();
                    }
                }
            }

        // }, {
        //     header: '', // 'Status',
        //     xtype: 'widgetcolumn',
        //     width: 360,
        //     widget: {
        //         xtype: 'datasetchart',
        //         height:40,
        //         widgetattached: false
        //     },
        //     onWidgetAttach: function(col, widget, record) {
        //         Ext.suspendLayouts();
        //         if (!widget.widgetattached) {
        //             widget.drawCompletenessChart(record);
        //             widget.widgetattached = true;
        //         }
        //         Ext.resumeLayouts(true);
        //     }
        },{
            xtype: 'actioncolumn',
            width: 65,
            align:'center',
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