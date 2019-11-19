Ext.define('esapp.view.analysis.timeseriesProductSelectionController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeseriesproductselection'

    ,refreshLayouts:function() {
        var me = this.getView();
        var gridSelectedTS = me.lookupReference('selected-timeseries-mapset-dataset-grid_'+ me.idpostfix);
        var colorschemesMatrixTS = me.lookupReference('colorschemesMatrixTSProductGrid_'+me.idpostfix);
        me.updateLayout();

        gridSelectedTS.updateLayout();
        if (me.graphtype == 'matrix'){
           colorschemesMatrixTS.updateLayout();
        }

    }

    ,createNewTSDrawPropertiesRecord: function(TSrecord){
        var me = this.getView();
        var myNewRecord = null;
        // var tsDrawPropertiesStore  = Ext.data.StoreManager.lookup('TSDrawPropertiesStore');
        var tsDrawPropertiesStore = me.getViewModel().getStore('timeseriesdrawproperties');

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
        tsDrawPropertiesStore.sync();
        return myNewRecord;
    }

    ,getTSDrawProperties: function(TSrecord){
        var me = this.getView();
        var user = esapp.getUser();
        var myNewRecord = null;
        var tsdrawprobs_record = null;
        // var tsDrawPropertiesStore  = Ext.data.StoreManager.lookup('TSDrawPropertiesStore');
        var tsDrawPropertiesStore = me.getViewModel().getStore('timeseriesdrawproperties');
        // tsDrawPropertiesStore.getSource().load();    // there is no load method for a chained store

        if (!tsDrawPropertiesStore.isLoaded()){
            if (user != 'undefined' && user != null){
                tsDrawPropertiesStore.proxy.extraParams = {
                    userid: user.userid,
                    istemplate: me.isTemplate,
                    graph_type: me.graphtype,
                    graph_tpl_id: me.isTemplate ? me.tplChartView.graph_tpl_id : '-1',
                    graph_tpl_name: me.isTemplate ? me.tplChartView.graph_tpl_name : 'default'
                };
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
                    if (tsdrawprobs_record == null) {
                        tsdrawprobs_record = me.getController().createNewTSDrawPropertiesRecord(TSrecord);
                    }
                }
            });
            // esapp.Utils.sleepFor(500);

            return tsdrawprobs_record;
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
            if (tsdrawprobs_record == null) {
                tsdrawprobs_record = me.getController().createNewTSDrawPropertiesRecord(TSrecord);
            }
            return tsdrawprobs_record;
        }
    }

    ,editTSDrawProperties: function(gridview, recordID){
        var me = this.getView();
        var TSrecord = gridview.store.getAt(recordID);
        gridview.tsdrawprobs_record = this.getTSDrawProperties(TSrecord);

        // var myTSDrawPropertiesWin = Ext.getCmp('TSDrawPropertiesWin');
        // if (myTSDrawPropertiesWin!=null && myTSDrawPropertiesWin!='undefined' ) {
        //     myTSDrawPropertiesWin.destroy();
        // }
        // myTSDrawPropertiesWin = null;

        // var colorrenderer = function(color) {
        //     renderTpl = color;
        //
        //     if (color.trim()==''){
        //         renderTpl = 'transparent';
        //     }
        //     else {
        //         renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
        //     }
        //     return renderTpl;
        // };

        var source = {
            yaxe_id: gridview.tsdrawprobs_record.get('yaxe_id'),
            tsname_in_legend: gridview.tsdrawprobs_record.get('tsname_in_legend'),
            charttype: gridview.tsdrawprobs_record.get('charttype'),
            linestyle: gridview.tsdrawprobs_record.get('linestyle'),
            linewidth: gridview.tsdrawprobs_record.get('linewidth'),
            color: esapp.Utils.convertRGBtoHex(gridview.tsdrawprobs_record.get('color'))
        };
        var title = esapp.Utils.getTranslation('ts_draw_properties_for') + ' '   // 'Time series draw properties for'
                    + gridview.tsdrawprobs_record.get('productcode')
                    + ' - ' + gridview.tsdrawprobs_record.get('version')
                    + ' - ' +  gridview.tsdrawprobs_record.get('subproductcode')


        var myTSDrawPropertiesWin =  me.lookupReference('TSDrawPropertiesWin_'+me.id);
        if (esapp.Utils.objectExists(myTSDrawPropertiesWin)) {
            myTSDrawPropertiesWin.setTitle(title);
            myTSDrawPropertiesWin.down('propertygrid').setSource(source);
            myTSDrawPropertiesWin.show();
            myTSDrawPropertiesWin.alignTo(gridview.getEl(),"r-tr", [-6, 0]);  // See: http://www.extjs.com/deploy/dev/docs/?class=Ext.Window&member=alignTo
        }
        else {
            var TSDrawPropertiesWin = new Ext.Window({
                 reference:'TSDrawPropertiesWin_'+me.id
                ,title: title
                ,width:450
                ,plain: true
                ,modal: true
                ,resizable: true
                ,closable:true
                ,closeAction: 'hide'
                ,layout: {
                     type: 'fit'
                },
                listeners: {
                    close: function(){
                        //console.info('closing window and removing filter');
                        // tsDrawPropertiesStore.clearFilter(true);
                        gridview.tsdrawprobs_record = null;
                        // this.destroy();
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
                                xtype: 'mycolorselector'
                            }
                            ,renderer: esapp.Utils.colorrenderer
                        }
                    },
                    listeners: {
                        propertychange: function( source, recordId, value, oldValue, eOpts ){
                            if (value != oldValue) {
                                // var user = esapp.getUser();
                                // if (user != 'undefined' && user != null){
                                //
                                //     var tsdrawprobs = {
                                //         productcode: tsdrawprobs_record.get('productcode'),
                                //         subproductcode: tsdrawprobs_record.get('subproductcode'),
                                //         version: tsdrawprobs_record.get('version'),
                                //         tsname_in_legend: source.tsname_in_legend,
                                //         color: source.color,
                                //         charttype: source.charttype,
                                //         linestyle: source.linestyle,
                                //         linewidth: source.linewidth,
                                //         yaxe_id: source.yaxe_id,
                                //         userid: user.userid,
                                //         istemplate: me.isTemplate,
                                //         graph_type: me.graphtype,
                                //         graph_tpl_id: me.isTemplate ? me.tplChartView.parent_tpl_id : '-1',
                                //         graph_tpl_name: me.isTemplate ? me.tplChartView.graph_tpl_name : 'default'
                                //     };
                                //
                                //     Ext.Ajax.request({
                                //         url:"analysis/gettimeseriesdrawproperties/update",
                                //         timeout : 300000,
                                //         //scope: me,
                                //         params:tsdrawprobs,
                                //         method: 'POST',
                                //         success: function ( result, request ) {
                                //             //console.info(Ext.util.JSON.decode(result.responseText));
                                //         },
                                //         failure: function ( result, request) {
                                //         }
                                //     });
                                //     // tsdrawprobs_record.set(recordId, value)
                                //     // tsdrawprobs_record.store.sync();
                                // }
                                gridview.tsdrawprobs_record.set(recordId, value)
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
            me.add(TSDrawPropertiesWin);
            TSDrawPropertiesWin.show();
            TSDrawPropertiesWin.alignTo(gridview.getEl(),"r-tr", [-6, 0]);  // See: http://www.extjs.com/deploy/dev/docs/?class=Ext.Window&member=alignTo
        }
    }

    ,getSelectedTSDrawProperties: function(){
        var me = this.getView(),
        // selectedTimeSeries = me.lookupReference("selected-timeseries-mapset-dataset-grid_"+me.idpostfix).getStore().getData(),
        tsdrawprops = [];
        Ext.util.JSON.decode(me.tplChartView.selectedTimeseries).forEach( function (product){
            var productrecord = new esapp.model.SelectedTimeseriesMapSetDataSet({
                productcode : product.productcode,
                version : product.version,
                subproductcode : product.subproductcode,
                mapsetcode : product.mapsetcode,
                cumulative : product.cumulative,
                difference : product.difference,
                reference : product.reference,
                colorramp : product.colorramp,
                legend_id : product.legend_id,
                zscore : product.zscore
            });

            var prod_tsdrawprobs = me.getController().getTSDrawProperties(productrecord);
            prod_tsdrawprobs = {
                productcode: prod_tsdrawprobs.get('productcode'),
                subproductcode: prod_tsdrawprobs.get('subproductcode'),
                version: prod_tsdrawprobs.get('version'),
                tsname_in_legend: prod_tsdrawprobs.get('tsname_in_legend'),
                charttype: prod_tsdrawprobs.get('charttype'),
                color: prod_tsdrawprobs.get('color'),
                linestyle: prod_tsdrawprobs.get('linestyle'),
                linewidth: prod_tsdrawprobs.get('linewidth'),
                yaxe_id: prod_tsdrawprobs.get('yaxe_id')
            }
            tsdrawprops.push(prod_tsdrawprobs);
        });

        tsdrawprops = Ext.util.JSON.encode(tsdrawprops);
        return tsdrawprops
    }

    ,getSelections: function(){
        var me = this.getView(),
            selectedTimeSeries = null,
            timeseriesselected = [],
            timeseriesselections = null,
            yearTS = '',
            tsFromPeriod = '',
            tsToPeriod = '',
            yearsToCompare = '',
            tsFromSeason = null,
            tsToSeason = null,
            ts_from_season = '',
            ts_to_season = '',
            legend_id = null,
            tsdrawprops = [];

        if (me.graphtype == 'matrix'){
            me.lookupReference("colorschemesMatrixTSProductGrid_"+me.idpostfix).getStore().each(function(rec){
                if (rec.get('default_legend')) {
                    legend_id = rec.get('legend_id');
                }
            },this);
        }
        selectedTimeSeries = me.lookupReference("selected-timeseries-mapset-dataset-grid_"+me.idpostfix).getStore().getData();


        if (selectedTimeSeries.length >0){
            if ( Ext.isObject(me.lookupReference('radio_year')) && me.lookupReference('radio_year').getValue()){
                if (me.lookupReference("YearTimeseries").getValue()== null || me.lookupReference("YearTimeseries").getValue() == '') {
                    me.lookupReference("YearTimeseries").validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('pleaseselectayear'),    // 'Please select a year!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                yearTS = me.lookupReference("YearTimeseries").getValue();

                ts_from_season = me.lookupReference("ts_from_season").getValue();
                ts_to_season = me.lookupReference("ts_to_season").getValue();
                if (( (ts_from_season == null) && (ts_to_season != null) ) ||
                    ( (ts_to_season == null) && (ts_from_season != null) )
                ) {
                    ts_from_season.validate();
                    ts_to_season.validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_give_seasons_date'),    // 'Please give Seasons "From" and "To" date!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }

                tsFromSeason = me.lookupReference("ts_from_season").getValue();
                tsToSeason = me.lookupReference("ts_to_season").getValue();
            }
            else if (Ext.isObject(me.lookupReference('radio_fromto')) && me.lookupReference('radio_fromto').getValue()){
                if (me.lookupReference("ts_from_period").getValue()== null || me.lookupReference("ts_from_period").getValue() == '') {
                    me.lookupReference("ts_from_period").validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('pleaseselectafromdate'),    // 'Please select a "From date"!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                if (me.lookupReference("ts_to_period").getValue()== null || me.lookupReference("ts_to_period").getValue() == '') {
                    me.lookupReference("ts_to_period").validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('pleaseselectatodate'),    // 'Please select a "To date"!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                tsFromPeriod = me.lookupReference("ts_from_period").getValue();
                tsToPeriod = me.lookupReference("ts_to_period").getValue();
            }
            else if (Ext.isObject(me.lookupReference('radio_compareyears')) && me.lookupReference('radio_compareyears').getValue()){
                var selectedYears = me.lookupReference("ts_selectyearstocompare").getStore().getData();

                if (selectedYears.length < 1){
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_select_one_or_more_years'),    // 'Please select one or more years!',
                       width: 400,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                yearsToCompare = [];
                selectedYears.each(function(year) {
                    yearsToCompare.push(year.get('year'));
                });

                ts_from_season = me.lookupReference("ts_from_seasoncompare").getValue();
                ts_to_season = me.lookupReference("ts_to_seasoncompare").getValue();
                if (( (ts_from_season == null) && (ts_to_season != null) ) ||
                    ( (ts_to_season == null) && (ts_from_season != null) )
                ) {
                    ts_from_season.validate();
                    ts_to_season.validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_give_seasons_date'),    // 'Please give Seasons "From" and "To" date!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }

                tsFromSeason = me.lookupReference("ts_from_seasoncompare").getValue();
                tsToSeason = me.lookupReference("ts_to_seasoncompare").getValue();
            }
            else if (Ext.isObject(me.lookupReference('radio_multiyears')) && me.lookupReference('radio_multiyears').getValue()){
                var multiYearsGrid = me.lookupReference("ts_selectmultiyears");
                var selectedMultiYears = multiYearsGrid.getSelection();
                //console.info(selectedMultiYears);

                if (selectedMultiYears.length < 1){
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_select_one_or_more_years'),    // 'Please select one or more years!',
                       width: 400,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                if (me.graphtype == 'ranking' && selectedMultiYears.length < 2){
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_select_min_two_years'),    // 'Please select more then one year to rank!',
                       width: 400,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }
                yearsToCompare = [];
                selectedMultiYears.forEach(function(year) {
                    yearsToCompare.push(year.get('year'));
                });

                ts_from_season = me.lookupReference("ts_from_seasonmulti").getValue();
                ts_to_season = me.lookupReference("ts_to_seasonmulti").getValue();
                if (( (ts_from_season == null) && (ts_to_season != null) ) ||
                    ( (ts_to_season == null) && (ts_from_season != null) )
                ) {
                    ts_from_season.validate();
                    ts_to_season.validate();
                    Ext.Msg.show({
                       title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                       msg: esapp.Utils.getTranslation('please_give_seasons_date'),    // 'Please give Seasons "From" and "To" date!',
                       width: 300,
                       buttons: Ext.Msg.OK,
                       animEl: '',
                       icon: Ext.Msg.WARNING
                    });
                    return timeseriesselections;
                }

                tsFromSeason = me.lookupReference("ts_from_seasonmulti").getValue();
                tsToSeason = me.lookupReference("ts_to_seasonmulti").getValue();
            }
            else {
                Ext.Msg.show({
                   title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
                   msg: esapp.Utils.getTranslation('pleaseselectatimeframe'),    // 'Please select a "From date"!',
                   width: 300,
                   buttons: Ext.Msg.OK,
                   animEl: '',
                   icon: Ext.Msg.WARNING
                });
                return timeseriesselections;
            }

            selectedTimeSeries.each(function(product) {
                var productObj = {
                    "productcode": product.get('productcode'),
                    "version": product.get('version'),
                    "subproductcode": product.get('subproductcode'),
                    "mapsetcode": product.get('mapsetcode'),
                    "date_format": product.get('date_format'),
                    "frequency_id": product.get('frequency_id'),
                    "cumulative": product.get('cumulative'),
                    "difference": product.get('difference'),
                    "reference": product.get('reference'),
                    "colorramp": product.get('colorramp') ? product.get('colorramp') : false,
                    "legend_id": legend_id,
                    "zscore": product.get('zscore') ? product.get('zscore') : false     // checkbox gives no value when not checked so no value is passed. Forse false in this case.
                };
                //console.info(product);
                timeseriesselected.push(productObj);

                var prod_tsdrawprobs = me.getController().getTSDrawProperties(product);
                prod_tsdrawprobs = {
                    productcode: prod_tsdrawprobs.get('productcode'),
                    subproductcode: prod_tsdrawprobs.get('subproductcode'),
                    version: prod_tsdrawprobs.get('version'),
                    tsname_in_legend: prod_tsdrawprobs.get('tsname_in_legend'),
                    charttype: prod_tsdrawprobs.get('charttype'),
                    color: prod_tsdrawprobs.get('color'),
                    linestyle: prod_tsdrawprobs.get('linestyle'),
                    linewidth: prod_tsdrawprobs.get('linewidth'),
                    yaxe_id: prod_tsdrawprobs.get('yaxe_id')
                }
                tsdrawprops.push(prod_tsdrawprobs);
            });

            //console.info(timeseriesselected);
            timeseriesselected = Ext.util.JSON.encode(timeseriesselected);
            tsdrawprops = Ext.util.JSON.encode(tsdrawprops);
        }
        else {
            Ext.Msg.show({
               title: esapp.Utils.getTranslation('mandatoryfield'),    // 'Mandatory field',
               msg: esapp.Utils.getTranslation('pleaseselectatimeseries'),    // 'Please select one or more times series!',
               width: 300,
               buttons: Ext.Msg.OK,
               animEl: '',
               icon: Ext.Msg.WARNING
            });
            return timeseriesselections;
        }

        timeseriesselections = {
            graphtype: me.graphtype,
            selectedTimeseries: timeseriesselected,
            yearTS: yearTS,
            tsFromPeriod: tsFromPeriod,
            tsToPeriod: tsToPeriod,
            yearsToCompare: yearsToCompare,
            tsFromSeason: tsFromSeason,
            tsToSeason: tsToSeason,
            tsdrawprops: tsdrawprops
        };

        return timeseriesselections

    }

    ,setTemplateSelections: function(){
        var me = this.getView();
        var timeseriesProductsStore = Ext.getStore('TimeseriesProductsStore');
		if (!timeseriesProductsStore.isLoaded() || timeseriesProductsStore.count() < 1) {
			timeseriesProductsStore.proxy.extraParams = {force: true};
			timeseriesProductsStore.reload({
				callback: function (records, options, success) {
					setSelections(me);
				}
			});						
		}
		else {
			setSelections(me);
		}
		
		function setSelections(me){
			if (esapp.Utils.objectExists(me.tplChartView)){
				// Loop tplSelectedTimeseries and find product record in timeseriesProductsStore.
				// When product record found, clone record and change settings to template product settings
				// Call this.TimeseriesProductsGridRowClick(newrecord)
				Ext.util.JSON.decode(me.tplChartView.selectedTimeseries).forEach( function (product){
					var prodrec = null;
					prodrec = timeseriesProductsStore.queryBy(function(record,id){
						return (record.get('productcode') == product.productcode &&
								record.get('version') == product.version &&
								record.get('subproductcode') == product.subproductcode &&
								record.get('mapsetcode') == product.mapsetcode
							);
					}).items;
					var newrecord = Ext.clone(prodrec[0]);
					if (esapp.Utils.objectExists(newrecord)) {
                        newrecord.set('cumulative', product.cumulative);
                        newrecord.set('difference', product.difference);
                        newrecord.set('reference', product.reference);
                        newrecord.set('colorramp', product.colorramp);
                        newrecord.set('legend_id', product.legend_id);
                        newrecord.set('zscore', product.zscore);

                        me.getController().TimeseriesProductsGridRowClick(null, newrecord);
                    }
				});

				if (me.tplChartView.yearTS != ''){
					me.lookupReference('radio_year').setValue(true);
					me.lookupReference("YearTimeseries").setValue(me.tplChartView.yearTS);
					if (me.tplChartView.tsFromSeason != '' && me.tplChartView.tsToSeason != ''){
						me.lookupReference("ts_from_season").setValue(me.tplChartView.tsFromSeason);
						me.lookupReference("ts_to_season").setValue(me.tplChartView.tsToSeason);
					}
				}
				if (me.tplChartView.tsFromPeriod != ''){
					me.lookupReference('radio_fromto').setValue(true);
					me.lookupReference("ts_from_period").setValue(me.tplChartView.tsFromPeriod);
					me.lookupReference("ts_to_period").setValue(me.tplChartView.tsToPeriod);
				}
				if (me.tplChartView.yearsToCompare != ''){
					me.lookupReference('radio_multiyears').setValue(true);
					var multiYearsGrid = me.lookupReference("ts_selectmultiyears");
					var selectedYearRecords = [];
					me.getViewModel().get('years').getData().each(function(yearInStore) {
						if (Ext.Array.contains(me.tplChartView.yearsToCompare, yearInStore.get('year'))){
							selectedYearRecords.push(yearInStore);
							// console.info(yearInStore);
						}
					});
					if (selectedYearRecords.length > 0){
						multiYearsGrid.getSelectionModel().select(selectedYearRecords);
					}

					if (me.tplChartView.tsFromSeason != '' && me.tplChartView.tsToSeason != ''){
						me.lookupReference("ts_from_seasonmulti").setValue(me.tplChartView.tsFromSeason);
						me.lookupReference("ts_to_seasonmulti").setValue(me.tplChartView.tsToSeason);
					}
				}
			}
		}
    }

    ,TimeseriesProductsGridRowClick: function(grid, record) {
        var me = this.getView();
        var selectedTimeseriesStore = me.getViewModel().getStore('selectedtimeseriesmapsetdatasets')
        var yearsData = [];
        var newrecord = Ext.clone(record);
        var addProduct = true;
        // var gridSelectedTS = me.lookupReference('selected-timeseries-mapset-dataset-grid_'+ me.idpostfix);
        // var selectedTimeseriesStore = Ext.getCmp(gridSelectedTS).getStore();
        // var record = me.getSelection()[0];
        // record.get('selected') ? record.set('selected', false) : record.set('selected', true);
        // record.get('selected') ? selectedTimeseriesStore.add(record) : selectedTimeseriesStore.remove(record);

        if (me.graphtype == 'xy'){
            var yAxes = [];
            var tsdrawprobs_new_selected_record = this.getTSDrawProperties(record);

            // esapp.Utils.sleepFor(1200);
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

            this.refreshLayouts();
        }
    }

    ,getColorSchemes: function(record) {
        var me = this.getView();
        // var colorSchemesStore = this.getStore('productcolorschemes');    //    Ext.getCmp('colorschemesMatrixTSProductGrid').getStore();   //
        var colorSchemesStore = me.getViewModel().getStore('productcolorschemes');
        var selectedproduct = {
            productcode:record.get('productcode'),
            productversion:record.get('version'),
            mapsetcode:record.get('mapsetcode'),
            subproductcode:record.get('subproductcode'),
            productname:record.get('product_descriptive_name'),
            date_format:record.get('date_format')
        };

        colorSchemesStore.load({
            params: selectedproduct,
            callback:function(records, options, success){
                if (records.length>0){
                    var nodefault = true;
                    var counter = 0;

                    for (var i = 0; i < records.length; i++) {
                        if (records[i].get('default_legend') == 'true' || records[i].get('default_legend')) {
                            // If there are more then one legend defined as default, set default to false
                            // to all default legends except the 1st encountered.
                            counter += 1;
                            if (counter >= 2){
                                records[i].set('default_legend', false);
                                records[i].set('defaulticon', 'x-grid3-radio-col');
                            }
                            nodefault = false;
                            me.up().up().legend_id = records[i].get('legend_id');
                        }

                    }
                    if (nodefault) {
                        records[0].set('default_legend', true);
                        records[0].set('defaulticon', 'x-grid3-radio-col-on');
                    }

                    colorSchemesStore.sort('default_legend','DESC');
                    me.lookupReference('colorschemesMatrixTSProductGrid_'+me.idpostfix).show();
                    me.getController().refreshLayouts();
                }
            }
        });

    }

    ,onRadioColumnAction:function(view, record ) {

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
                break;
            default:
        }
    }
});
