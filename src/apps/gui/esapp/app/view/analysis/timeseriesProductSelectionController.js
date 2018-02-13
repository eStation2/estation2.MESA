Ext.define('esapp.view.analysis.timeseriesProductSelectionController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeseriesproductselection'

    ,getTSDrawProperties: function(TSrecord){
        var myNewRecord = null;
        var tsdrawprobs_record = null;
        var tsDrawPropertiesStore  = Ext.data.StoreManager.lookup('TSDrawPropertiesStore');
        // var tsDrawPropertiesStore = this.getStore('timeseriesdrawproperties');
        // tsDrawPropertiesStore.getSource().load();    // there is no load method for a chained store


        if (!tsDrawPropertiesStore.isLoaded()){
            var user = esapp.getUser();
            if (user != 'undefined' && user != null){
                tsDrawPropertiesStore.proxy.extraParams = {userid: user.userid, graph_tpl_name: 'default'};
            }
            tsDrawPropertiesStore.load({
                callback: function(records, options, success) {
                    tsDrawPropertiesStore.clearFilter(true);
                    tsDrawPropertiesStore.filterBy(function (record, id) {
                        if (record.get("productcode") == TSrecord.get('productcode') && record.get("version") == TSrecord.get('version') && record.get("subproductcode") == TSrecord.get('subproductcode')) {
                            return true;
                        }
                        return false;
                    });

                    tsdrawprobs_record = tsDrawPropertiesStore.findRecord('productcode', TSrecord.get('productcode'));
                }
            });
            esapp.Utils.sleepFor(350);
        }
        else {
            tsDrawPropertiesStore.clearFilter(true);
            tsDrawPropertiesStore.filterBy(function (record, id) {
                if (record.get("productcode") == TSrecord.get('productcode') && record.get("version") == TSrecord.get('version') && record.get("subproductcode") == TSrecord.get('subproductcode')) {
                    return true;
                }
                return false;
            });

            tsdrawprobs_record = tsDrawPropertiesStore.findRecord('productcode', TSrecord.get('productcode'));
        }
        if (tsdrawprobs_record == null) {
            var newcharttype = 'line',
                newyaxes_id = TSrecord.get('productcode') + ' - ' + TSrecord.get('version');

            tsDrawPropertiesStore.clearFilter(true);
            tsDrawPropertiesStore.filterBy(function (record, id) {
                if (record.get("productcode") == TSrecord.get('productcode') && record.get("version") == TSrecord.get('version')) {
                    return true;
                }
                return false;
            });

            var similarTSrecord = tsDrawPropertiesStore.getAt(0);
            if (similarTSrecord != null) {
                newcharttype = similarTSrecord.get('charttype');
                newyaxes_id = similarTSrecord.get('yaxe_id');
            }

            //myNewRecord = new tsDrawPropertiesStore.recordType({
            myNewRecord = new esapp.model.TSDrawProperties({
                productcode: TSrecord.get('productcode'),
                subproductcode: TSrecord.get('subproductcode'),
                version: TSrecord.get('version'),
                tsname_in_legend: TSrecord.get('productcode') + ' - ' + TSrecord.get('version') + ' - ' + TSrecord.get('subproductcode'),
                charttype: newcharttype,
                linestyle: 'Solid',
                linewidth: 2,
                color: esapp.Utils.convertRGBtoHex('0 0 0'),
                yaxe_id: newyaxes_id
            });

            tsDrawPropertiesStore.add(myNewRecord);
            tsdrawprobs_record = myNewRecord;
        }

        return tsdrawprobs_record;
    }

    ,editTSDrawProperties: function(gridview, recordID){
        var TSrecord = gridview.store.getAt(recordID);
        var tsdrawprobs_record = this.getTSDrawProperties(TSrecord);

        var myTSDrawPropertiesWin = Ext.getCmp('TSDrawPropertiesWin');
        if (myTSDrawPropertiesWin!=null && myTSDrawPropertiesWin!='undefined' ) {
            myTSDrawPropertiesWin.destroy();
        }
        myTSDrawPropertiesWin = null;

        var colorrenderer = function(color) {
            renderTpl = color;

            if (color.trim()==''){
                renderTpl = 'transparent';
            }
            else {
                renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
            }
            return renderTpl;
        };

        var source = {
            yaxe_id: tsdrawprobs_record.get('yaxe_id'),
            tsname_in_legend: tsdrawprobs_record.get('tsname_in_legend'),
            charttype: tsdrawprobs_record.get('charttype'),
            linestyle: tsdrawprobs_record.get('linestyle'),
            linewidth: tsdrawprobs_record.get('linewidth'),
            color: esapp.Utils.convertRGBtoHex(tsdrawprobs_record.get('color'))
        };

        var TSDrawPropertiesWin = new Ext.Window({
             id:'TSDrawPropertiesWin'
            ,title: esapp.Utils.getTranslation('ts_draw_properties_for') + ' '   // 'Time series draw properties for'
                    + tsdrawprobs_record.get('productcode')
                    + ' - ' + tsdrawprobs_record.get('version')
                    + ' - ' +  tsdrawprobs_record.get('subproductcode')
            ,width:450
            ,plain: true
            ,modal: true
            ,resizable: true
            ,closable:true
            ,closeAction: 'destroy'
            ,layout: {
                 type: 'fit'
            },
            listeners: {
                close: function(){
                    //console.info('closing window and removing filter');
                    // tsDrawPropertiesStore.clearFilter(true);
                    tsdrawprobs_record = null;
                    this.destroy();
                }
            }
            ,items:[{
                xtype: 'propertygrid',
                //nameField: 'Property',
                //width: 400,
                nameColumnWidth: 160,
                sortableColumns: false,
                source: source,
                sourceConfig: {
                    yaxe_id: {
                        displayName: esapp.Utils.getTranslation('yaxes_id'),   // 'Yaxe ID',
                        editor: {}
                        //type: 'text',
                        // editor: {
                        //     xtype: 'textfield',
                        //     selectOnFocus:false
                        // }
                    },
                    tsname_in_legend: {
                        displayName: esapp.Utils.getTranslation('tsname_in_legend'),   // 'Time series name in legend',
                        //type: 'text',
                        editor: {
                            xtype: 'textfield',
                            selectOnFocus:false
                        }
                    },
                    charttype: {
                        displayName: esapp.Utils.getTranslation('charttype'),   // 'Chart type',
                        editor: {
                            xtype: 'combobox',
                            store: ['line', 'column'],
                            forceSelection: true
                        }
                    },
                    linestyle: {
                        displayName: esapp.Utils.getTranslation('linestyle'),   // 'Line style',
                        editor: {
                            xtype: 'combobox',
                            store: ['Solid',
                                    'ShortDash',
                                    'ShortDot',
                                    'ShortDashDot',
                                    'ShortDashDotDot',
                                    'Dot',
                                    'Dash',
                                    'LongDash',
                                    'DashDot',
                                    'LongDashDot',
                                    'LongDashDotDot'],
                            forceSelection: true
                        }
                    },
                    linewidth: {
                        displayName: esapp.Utils.getTranslation('linewidth'),   // Line width',
                        type: 'number'
                    },
                    color: {
                        displayName: esapp.Utils.getTranslation('color'),   // 'Colour',
                        editor: {
                            xtype: 'mycolorpicker'
                        }
                        ,renderer: colorrenderer
                    }
                },
                listeners: {
                    propertychange: function( source, recordId, value, oldValue, eOpts ){

                        if (value != oldValue) {
                            var user = esapp.getUser();
                            if (user != 'undefined' && user != null){

                                var tsdrawprobs = {
                                    productcode: tsdrawprobs_record.get('productcode'),
                                    subproductcode: tsdrawprobs_record.get('subproductcode'),
                                    version: tsdrawprobs_record.get('version'),
                                    tsname_in_legend: source.tsname_in_legend,
                                    color: source.color,
                                    charttype: source.charttype,
                                    linestyle: source.linestyle,
                                    linewidth: source.linewidth,
                                    yaxe_id: source.yaxe_id,
                                    userid: user.userid,
                                    graph_tpl_name: 'default'
                                };

                                Ext.Ajax.request({
                                    url:"analysis/gettimeseriesdrawproperties/update",
                                    timeout : 300000,
                                    //scope: me,
                                    params:tsdrawprobs,
                                    method: 'POST',
                                    success: function ( result, request ) {
                                        //console.info(Ext.util.JSON.decode(result.responseText));
                                    },
                                    failure: function ( result, request) {
                                    }
                                });
                                // tsdrawprobs_record.set(recordId, value)
                                // tsdrawprobs_record.store.sync();
                            }
                        }
                    },
                    beforeedit: function( editor, e, opts ) {
                        if( e.record.get( 'name' )=='yaxe_id') {
                            return false;
                        }
                    }
                }
            }]

        });
        TSDrawPropertiesWin.show();
        TSDrawPropertiesWin.alignTo(gridview.getEl(),"r-tr", [-6, 0]);  // See: http://www.extjs.com/deploy/dev/docs/?class=Ext.Window&member=alignTo

    }

    ,TimeseriesProductsGridRowClick: function(gridview, record, colIndex, icon, e, rec) {
        var me = this.getView();
        var gridSelectedTS = 'selected-timeseries-mapset-dataset-grid_'+ me.graphtype;
        var selectedTimeseriesStore = Ext.getCmp(gridSelectedTS).getStore();
        var yearsData = [];
        //var record = me.getSelection()[0];
        var newrecord = Ext.clone(record);
        var addProduct = true;

        //record.get('selected') ? record.set('selected', false) : record.set('selected', true);
        //record.get('selected') ? selectedTimeseriesStore.add(record) : selectedTimeseriesStore.remove(record);
        //
        if (me.graphtype == 'xy'){
            var yAxes = [];
            var tsdrawprobs_new_selected_record = this.getTSDrawProperties(record);
            yAxes.push(tsdrawprobs_new_selected_record.get('yaxe_id'));
            if (selectedTimeseriesStore.count() > 0){
                selectedTimeseriesStore.getData().each(function(selectedproduct) {
                    var yaxeid = me.getController().getTSDrawProperties(selectedproduct).get('yaxe_id');
                    if (!Ext.Array.contains(yAxes, yaxeid)){
                        yAxes.push(yaxeid);
                    }
                });
            }
            if (yAxes.length > 4){
                Ext.toast({
                    html: esapp.Utils.getTranslation('more_than_4_yaxes_message'),    // "You have selected products that will create more than 4 y-Axes in the Profile Graph, which is not supported!<BR><BR>Last selected product is not added.",
                    title: esapp.Utils.getTranslation('more_than_4_yaxes_title'), // 'Warning! More than 4 Y-axes!'
                    width: 300,
                    align: 't',
                    hideDuration: 1500
                });
                addProduct = false;
            }
        }

        if (addProduct){
            if (selectedTimeseriesStore.count() > 0){
                var recordExists = false;
                selectedTimeseriesStore.getData().each(function(product) {
                    if (product.get('productmapsetid') == record.get('productmapsetid') && product.get('subproductcode') == record.get('subproductcode')){
                        recordExists = true;
                    }
                });
                if (!recordExists){
                    if (!me.multiplevariables){
                        selectedTimeseriesStore.removeAll();
                    }
                    newrecord.set('selected', true);
                    selectedTimeseriesStore.add(newrecord);
                }
                //var  recordExists = selectedTimeseriesStore.findRecord('productmapsetid', record.get('productmapsetid'), 0, true);
                //console.info(recordExists);
                //if (recordExists != null ){
                //    console.info(recordExists.get('subproductcode'));
                //    console.info(record.get('subproductcode'));
                //    if (!(recordExists.get('subproductcode') == record.get('subproductcode'))){
                //        record.set('selected', true);
                //        selectedTimeseriesStore.add(record);
                //    }
                //}
            }
            else {
                if (!me.multiplevariables){
                    selectedTimeseriesStore.removeAll();
                }
                newrecord.set('selected', true);
                selectedTimeseriesStore.add(newrecord);
            }

            if (me.multipleyears || me.year){
                selectedTimeseriesStore.getData().each(function(product) {
                    yearsData = esapp.Utils.union_arrays(yearsData, product.get('years'));

                    //alltimeseriesmapsetdatasets.push(product);
                    //// First loop the mapsets to get the by the user selected mapset if the product has > 1 mapsets.
                    //var datasets = product.get('productmapsets')[0].timeseriesmapsetdatasets;
                    ////var datasets = product.get(children)[0].children;
                    //datasets.forEach(function(datasetObj) {
                    //    //yearsData = Ext.Object.merge(yearsData, datasetObj.years);
                    //    yearsData = esapp.Utils.union_arrays(yearsData, datasetObj.years);
                    //    alltimeseriesmapsetdatasets.push(datasetObj);
                    //});
                });

                var currentYearsData = [];
                me.getViewModel().get('years').getData().each(function(year) {
                    currentYearsData.push(year.get('year'));
                });

                if (!me.multiplevariables){  // only 1 product allowed so remove years from currentYearsData that are not in yearsData
                    // me.getViewModel().get('years').removeAll();
                    var tmpYearsData = [];
                    currentYearsData.forEach(function(year, idx) {
                        if (!Ext.Array.contains(yearsData, year)){
                            // currentYearsData.splice(idx, 1); // remove one item at idx
                            me.getViewModel().get('years').getData().each(function(yearInStore) {
                                if (year == yearInStore.get('year')){
                                    me.getViewModel().get('years').remove(yearInStore);
                                }
                            });
                        }
                        else {
                            tmpYearsData.push(year);
                        }
                    });
                    currentYearsData = tmpYearsData;
                }
                yearsData.forEach(function(year) {      // Add the years not present in currentYearsData
                    if (!Ext.Array.contains(currentYearsData, year)){
                        me.getViewModel().get('years').add({'year': year});
                    }
                });
            }

            // var yearsDataDict = [];
            // yearsData.forEach(function(year) {
            //     yearsDataDict.push({'year': year});
            // });
            //
            // //if (!record.get('selected') && Ext.isObject(Ext.getCmp('ts_selectyearstocompare_'+me.graphtype).searchPopup)){
            // //    Ext.getCmp('ts_selectyearstocompare_'+me.graphtype).searchPopup.lookupReference('searchGrid').getSelectionModel().deselectAll();
            // //}
            // //Ext.getCmp('timeserieschartselection').getViewModel().getStore('years').setData(yearsDataDict);
            // me.getViewModel().get('years').setData(yearsDataDict);

            //Ext.getCmp('selected-timeseries-mapset-dataset-grid').show();
            //Ext.getCmp('ts_timeframe').show();
            //Ext.getCmp('gettimeseries_btn').setDisabled(false);
            //console.info(me.graphtype);
            if (me.graphtype == 'matrix'){
                this.getColorSchemes(record);
            }
        }
    }

    ,getColorSchemes: function(record) {
        var me = this.getView();
        var colorSchemesStore = this.getStore('productcolorschemes');    //    Ext.getCmp('colorschemesMatrixTSProductGrid').getStore();   //
        var selectedproduct = {
            productcode:record.get('productcode'),
            productversion:record.get('version'),
            mapsetcode:record.get('mapsetcode'),
            subproductcode:record.get('subproductcode'),
            productname:record.get('product_descriptive_name'),
            date_format:record.get('date_format')
        };
        //console.info(me.up().up());
        //Ext.getCmp('colorschemesMatrixTSProductGrid').hide();
        Ext.getCmp('colorschemesMatrixTSProductGrid').getStore().removeAll();

        colorSchemesStore.load({
            params: selectedproduct,
            callback:function(records, options, success){
                if (records.length>0){
                    var nodefault = true;
                    for (var i = 0; i < records.length; i++) {
                        if (records[i].get('default_legend') == 'true' || records[i].get('default_legend')) {
                            nodefault = false;
                            me.up().up().legend_id = records[i].get('legend_id');
                        }

                    }
                    if (nodefault) {
                        records[0].set('default_legend', true);
                        records[0].set('defaulticon', 'x-grid3-radio-col-on');
                        //me.up().up().legend_id = records[0].get('legend_id');
                    }
                    Ext.getCmp('colorschemesMatrixTSProductGrid').getStore().add(records);
                    Ext.getCmp('colorschemesMatrixTSProductGrid').getStore().sort('default_legend','DESC');
                    Ext.getCmp('colorschemesMatrixTSProductGrid').show();
                }
            }
        });

        //console.info(colorSchemesStore);
        //console.info(this.getStore('productcolorschemes'));
    },

    //onRadioColumnAction:function(view, rowIndex, colIndex, item, e, record ) {
    onRadioColumnAction:function(view, record ) {
        //var me = this.getView();

        switch(record.get('defaulticon')) {
            case 'x-grid3-radio-col':
                    view.getStore('colorschemes').each(function(rec){
                        //if (view.getStore().indexOf(rec) != rowIndex) {
                            rec.set('default_legend', false);
                            rec.set('defaulticon', 'x-grid3-radio-col');
                        //}
                    },this);

                    record.set('default_legend', true);
                    record.set('defaulticon', 'x-grid3-radio-col-on');
                    view.getStore().sort('default_legend','DESC');
                    //me.up().up().legend_id = record.get('legend_id');
                    //console.info(record);
                    //console.info(me.up().up());
                break;
            default:
        }
    }


    //,__TimeseriesProductsGridRowClick: function(gridview, record){
    //    //var selectedTimeSeriesProducts = gridview.getSelectionModel().selected.items;
    //    //var alltimeseriesmapsetdatasets = [];
    //
    //    //var selectedTimeseriesStore = Ext.getCmp('selected-timeseries-mapset-dataset-grid').getStore();
    //    //var me = this.getView();
    //    //console.info(gridview);
    //    //console.info(record);
    //    var gridSelectedTS = 'selected-timeseries-mapset-dataset-grid_xy';
    //    if (gridview.up().graphtype == 'cumulative'){
    //        gridSelectedTS = 'selected-timeseries-mapset-dataset-grid_cum';
    //    }
    //    var selectedTimeseriesStore = Ext.getCmp(gridSelectedTS).getStore();
    //    //var selectedTimeseriesStore = gridview.up().up().up().lookupReference(gridSelectedTS).getStore();
    //    var yearsData = [];
    //
    //    record.get('selected') ? record.set('selected', false) : record.set('selected', true);
    //    record.get('selected') ? selectedTimeseriesStore.add(record) : selectedTimeseriesStore.remove(record);
    //
    //    selectedTimeseriesStore.getData().each(function(product) {
    //        yearsData = esapp.Utils.union_arrays(yearsData, product.get('years'));
    //
    //        //alltimeseriesmapsetdatasets.push(product);
    //        //// First loop the mapsets to get the by the user selected mapset if the product has > 1 mapsets.
    //        //var datasets = product.get('productmapsets')[0].timeseriesmapsetdatasets;
    //        ////var datasets = product.get(children)[0].children;
    //        //datasets.forEach(function(datasetObj) {
    //        //    //yearsData = Ext.Object.merge(yearsData, datasetObj.years);
    //        //    yearsData = esapp.Utils.union_arrays(yearsData, datasetObj.years);
    //        //    alltimeseriesmapsetdatasets.push(datasetObj);
    //        //});
    //    });
    //    var yearsDataDict = [];
    //    yearsData.forEach(function(year) {
    //        yearsDataDict.push({'year': year});
    //    });
    //
    //    if (!record.get('selected') && Ext.isObject(Ext.getCmp('ts_selectyearstocompare').searchPopup)){
    //        Ext.getCmp('ts_selectyearstocompare').searchPopup.lookupReference('searchGrid').getSelectionModel().deselectAll();
    //    }
    //    Ext.getCmp('timeserieschartselection').getViewModel().getStore('years').setData(yearsDataDict);
    //
    //    //this.getStore('years').setData(yearsDataDict);
    //    //var productmapset = record.get('productmapsets')[0];
    //    //this.getStore('selectedtimeseriesmapsetdatasets').setData(alltimeseriesmapsetdatasets); // NOTE: Works only if Model does not have idProperty defined, otherwise only the last element is added.
    //    //Ext.getCmp('selected-timeseries-mapset-dataset-grid').getStore().setData(alltimeseriesmapsetdatasets);
    //
    //    //if (selectedTimeseriesStore.length == 0) {
    //    //    //Ext.getCmp('selected-timeseries-mapset-dataset-grid').hide();
    //    //    gridview.up().up().up().lookupReference('selected-timeseries-mapset-dataset-grid').hide();
    //    //    Ext.getCmp('ts_timeframe').hide();
    //    //    Ext.getCmp('gettimeseries_btn').setDisabled(true);
    //    //    //Ext.getCmp('gettimeseries_btn2').setDisabled(true);
    //    //}
    //    //else {
    //    //    //Ext.getCmp('selected-timeseries-mapset-dataset-grid').show();
    //    //    gridview.up().up().up().lookupReference('selected-timeseries-mapset-dataset-grid').show();
    //    //    Ext.getCmp('ts_timeframe').show();
    //    //    Ext.getCmp('gettimeseries_btn').setDisabled(false);
    //    //    //Ext.getCmp('gettimeseries_btn2').setDisabled(false);
    //    //}
    //}
});
