
Ext.define("esapp.view.acquisition.Ingestion", {
    "extend": "Ext.grid.Panel",

    "controller": "ingestion",

    "viewModel": {
        "type": "ingestion"
    },

    "xtype": 'ingestiongrid',

    requires: [
        'esapp.view.acquisition.IngestionModel',
        'esapp.view.acquisition.IngestionController',
        'esapp.view.acquisition.logviewer.LogView',
        'esapp.view.acquisition.selectMapsetForIngest',

        'esapp.view.widgets.datasetCompletenessChart',

        'Ext.grid.column.Action',
        'Ext.grid.column.Widget'
        //'Ext.grid.column.Check'
    ],

    bind: {
        store: '{productingestions}'
    },

    cls: 'grid-color-azur',

    hideHeaders: true,
    columnLines: false,
    rowLines: false,
    collapsible: false,
    bufferedRenderer: false,
    forceFit: true,
    focusable: false,
    minHeight: 55,

    layout: 'fit',

    // selType: 'cellmodel',
    // selModel: {listeners:{}},

    initComponent: function () {
        var me = this;
        //Ext.util.Observable.capture(this, function(e){console.log('Ingestion - ' + this.id + ': ' + e);});

        // me.listeners = {
        //     afterrender: function(){
        //         me.view.refresh();
        //     }
        // };

        me.viewConfig = {
            stripeRows: false,
            enableTextSelection: true,
            draggable: false,
            markDirty: false,
            resizable: false,
            disableSelection: true,
            trackOver: false,
            forceFit: true,
            preserveScrollOnRefresh: false,
            focusable: false,
            loadMask: false,
            getRowClass: function(record) {
                return 'wordwrap';
            }
            ,listeners: {
                render: function(view){
                    createTooltip(view);
                    // Ext.util.Observable.capture(view, function(e){console.log(view.id + ': ' + e);});
                },
                rowclick: function(view){
                    // console.info('rowclick');
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
                },
                itemmouseenter: function(view){
                    // console.info('itemmouseenter');
                    var widgettooltip = Ext.getCmp(view.getId() + '_completness_tooltip');
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
                },
                rowfocus: {}
            }
        };

        function createTooltip(view) {
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
                mouseOffset : [-5,0],
                autoHide: false,
                showDelay: 100,
                // hideDelay: 5000,
                // dismissDelay: 10000, // auto hide after 10 seconds
                closable: true,
                anchorToTarget: false,
                // anchor: 'left',
                padding: 5,
                listeners: {
                    close: function(tip) {
                        // tip.disable();
                        tip.hide();
                    },
                    // Change content dynamically depending on which element triggered the show.
                    beforeshow: function (tip) {
                        // Ext.util.Observable.capture(tip.triggerElement, function(e){console.log(tip.id + ': ' + e);});
                        if (esapp.Utils.objectExists(tip.triggerElement)) {
                            var datasetinterval = '',
                                datasetForTipText,
                                tooltipintervals,
                                mapsetdatasetrecord = view.getRecord(tip.triggerElement),   // view.dataSource.getData().items[0], //  view.dataSource.data.items[0], //
                                completeness = mapsetdatasetrecord.get('completeness') || mapsetdatasetrecord.getCompleteness(); // mapsetdatasetrecord.getAssociatedData().completeness;
                            // completeness = mapsetdatasetrecord.get('completeness');

                            if (mapsetdatasetrecord.get('mapsetcode')!='') {

                                var completenessTooltips = Ext.ComponentQuery.query('tooltip{id.search("_completness_tooltip") != -1}');
                                Ext.each(completenessTooltips, function(item) {
                                   // item.disable();
                                    if (item != tip){
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
                                    completeness.intervals().getData().items.forEach(function (interval) {
                                        // console.info(interval);
                                        var color, intervaltype = '';
                                        if (interval.get('intervaltype') == 'present') {
                                            color = '#81AF34'; // green
                                            intervaltype = esapp.Utils.getTranslation('present');
                                        }
                                        if (interval.get('intervaltype') == 'missing') {
                                            color = '#FF0000'; // red
                                            intervaltype = esapp.Utils.getTranslation('missing');
                                        }
                                        if (interval.get('intervaltype') == 'permanent-missing') {
                                            color = '#808080'; // gray
                                            intervaltype = esapp.Utils.getTranslation('permanent-missing');
                                        }
                                        datasetinterval = '<span style="color:' + color + '">' + esapp.Utils.getTranslation('from') + ' ' + interval.get('fromdate') + ' ' + esapp.Utils.getTranslation('to') + ' ' + interval.get('todate') + ' - ' + intervaltype + '</span></br>';
                                        tooltipintervals += datasetinterval;
                                    });
                                }

                                tip.update(tooltipintervals);
                                // tip.on('show', function(){
                                //     Ext.defer(tip.hide, 10000, tip);
                                // }, tip, {single: true});

                            }
                            else {
                                tip.update(esapp.Utils.getTranslation('no_mapset_defined_for_subproduct'));    // 'No mapset defined for this ingest subproduct! Please assign a mapset by clicking on the + icon.'
                                // tip.disable();
                            }
                        }
                    }
                }
            });
            // view.tooltip.enable();

            // var task = new Ext.util.DelayedTask(function() {
            //     view.tooltip.show();
            // });
            // task.delay(500);

            // Ext.Function.defer(view.tooltip.show(), 1000, this);
            // Ext.Function.defer(view.tooltip.enable(), 1000, this);
        }

        me.defaults = {
            menuDisabled: true,
            draggable:false,
            groupable:false,
            hideable: false
        };

        me.columns = [{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: true,
            hidden: Ext.getCmp('lockunlock').pressed ? false : true,
            width: 35,
            minWidth: 35,
            maxWidth: 35,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    return 'add16';
                },
                getTip: function(v, meta, rec) {
                    return esapp.Utils.getTranslation('add_mapset_for')+' '+rec.get('subproductcode');
                },
                handler: function(grid, rowIndex, colIndex) {
                    var record = grid.getStore().getAt(rowIndex);
                    //console.info(record);
                    // get supproduct info and open choose mapset window
                    var productcode = record.get('productcode');
                    var version = record.get('version');
                    var subproductcode = record.get('subproductcode');

                    // var selectMapsetForIngestWin = new esapp.view.acquisition.selectMapsetForIngest({
                    //     productcode: productcode,
                    //     productversion: version,
                    //     subproductcode: subproductcode
                    // });
                    var selectMapsetForIngestWin = new esapp.view.acquisition.product.MapsetAdmin({
                        assigntoproduct: true,
                        productcode: productcode,
                        productversion: version,
                        subproductcode: subproductcode
                    });
                    selectMapsetForIngestWin.show();

                }
            }]
        },{
            header: '', // 'Sub Product Code',
            dataIndex: 'subproductcode',
            //bind: '{ingestions.subproductcode}',
            width: 150,
            minWidth: 150
        }, {
            header: '', // 'Mapset',
            dataIndex: 'mapsetname',
            //bind: '{ingestions.mapset}',
            width: 200,
            minWidth: 200,
            cellWrap:true
        },{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: true,
            hidden: Ext.getCmp('lockunlock').pressed ? false : true,
            width: 35,
            minWidth: 35,
            maxWidth: 35,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    //if (rec.get('defined_by')=='USER') {
                    if (rec.get('mapsetcode')!='') {
                         return 'delete16';
                    } else {
                        return ' hide-actioncolumn';  // 'x-hide-display';
                    }
                },
                getTip: function(v, meta, rec) {
                    //if (rec.get('defined_by')=='USER') {
                        return esapp.Utils.getTranslation('delete_mapset_for')+' <b>'+rec.get('subproductcode')+'</b>';
                    //}
                },
                //isDisabled: function(view, rowIndex, colIndex, item, record) {
                //    // Returns true if 'defined_by' is 'JRC'
                //    if (record.get('defined_by')=='JRC') {
                //        return true;
                //    }
                //},
                handler: function(grid, rowIndex, colIndex) {
                    var record = grid.getStore().getAt(rowIndex);
                    var productcode = record.get('productcode');
                    var version = record.get('version');
                    var subproductcode = record.get('subproductcode');
                    var mapsetcode = record.get('mapsetcode');

                    Ext.Msg.show({
                        title:esapp.Utils.getTranslation('deletemapsetforingestmsgtitle'),
                        message: esapp.Utils.getTranslation('deletemapsetforingestmessage')+'</BR><b>'+ productcode+' - '+ version+' - '+ subproductcode+'</b>?',
                        buttons: Ext.Msg.YESNO,
                        icon: Ext.Msg.WARNING,     // Ext.Msg.QUESTION,
                        fn: function(btn) {
                            if (btn === 'yes') {
                                Ext.Ajax.request({
                                    method: 'GET',
                                    url: 'deleteingestmapset',
                                    params: {
                                        productcode: productcode,
                                        version: version,
                                        subproductcode: subproductcode,
                                        mapsetcode: mapsetcode
                                    },
                                    success: function(response, opts){
                                        var result = Ext.JSON.decode(response.responseText);
                                        if (result.success){
                                            var ingestiongridstore = Ext.data.StoreManager.lookup('IngestionsStore');

                                            if (ingestiongridstore.isStore) {
                                                ingestiongridstore.load({
                                                    callback: function(records, options, success){

                                                    }
                                                });
                                            }
                                            Ext.toast({ html: esapp.Utils.getTranslation('mapset')+' <b>'+ mapsetcode+'<b> '+esapp.Utils.getTranslation('deletedforingest')+'</BR><b>'+ productcode+' - '+ version+' - '+ subproductcode+'</b>!', title: esapp.Utils.getTranslation('deletedmapsetforingestconfirmtitle'), width: 300, align: 't' });
                                        }
                                    },
                                    failure: function(response, opts) {
                                        console.info(response.status);
                                    }
                                });
                            } else if (btn === 'no') {
                                //console.log('No pressed');
                            }
                        }
                    });
                }
            }]
        }, {
            // header: '', // 'Completeness',
            width: 360,
            xtype: 'templatecolumn',
            // dataIndex: 'datasetcompletenessimage',
            // style: {cursor: 'pointer'},
            tpl: new Ext.XTemplate(
                    '<img style="cursor: pointer;" src="{datasetcompletenessimage}" />'
                ),
            listeners: {
                click: function(view){
                    // console.info(view);
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
        //     header: '', // 'Completeness',
        //     xtype: 'widgetcolumn',
        //     //dataIndex: 'completeness',
        //     //bind: '{ingestions.completeness}',
        //     width: 360,
        //     minWidth: 360,
        //     padding:15,
        //     //bodyPadding:15,
        //     variableRowHeight:true,
        //     widget: {
        //         xtype: 'datasetchart',
        //         height:45,
        //         widgetattached: false
        //     },
        //     onWidgetAttach: function(col, widget, record) {
        //         var widgetchart = widget.down('cartesian');
        //         if (!widget.widgetattached) {
        //             if (record.data.mapsetcode != '') {
        //                 widget.drawCompletenessChart(record);
        //                 widget.widgetattached = true;
        //             }
        //             else {
        //                 widgetchart.setHidden(true);
        //             }
        //         }
        //         //Ext.resumeLayouts(true);
        //         me.updateLayout();
        //     }
        },{
            xtype: 'actioncolumn',
            // header: 'Active',
            hideable: false,
            hidden: false,
            width: 55,
            align: 'center',
            stopSelection: false,
            items: [{
                // scope: me,
                disabled: false,
                getClass: function(v, meta, rec) {
                    if (rec.get('mapsetcode')!='') {
                        if (rec.get('activated')) {
                            return 'activated';
                        } else {
                            return 'deactivated';
                        }
                    } else {
                        return ' hide-actioncolumn';  // 'x-hide-display';
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
