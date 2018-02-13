Ext.define('esapp.view.analysis.timeseriesChartSelectionController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartselection'


    ,getTimeseriesSelections: function(graphtype){
        //var timeseriesgrid = this.getView().lookupReference('timeseries-mapset-dataset-grid');
        //var timeseriesgrid = Ext.getCmp('timeseries-mapset-dataset-grid');
        //var selectedTimeSeries = timeseriesgrid.getSelectionModel().selected.items;
        var selectedTimeSeries = null,
            wkt_polygon = this.getView().lookupReference('wkt_polygon'),
            timeseriesselected = [],
            timeseriesselections = null,
            yearTS = '',
            tsFromPeriod = '',
            tsToPeriod = '',
            yearsToCompare = '',
            tsFromSeason = null,
            tsToSeason = null,
            postfix_graphtype = graphtype,
            ts_from_season = '',
            ts_to_season = '',
            legend_id = null;

        //if (graphtype == 'cumulative'){
        //    postfix_graphtype = '_cum'
        //}
        if (graphtype == 'matrix'){
            //console.info(Ext.getCmp('colorschemesMatrixTSProductGrid').getStore());
            //var legend_id = Ext.getCmp('selected-timeseries-mapset-dataset-grid_'+postfix_graphtype).up().legend_id;
            Ext.getCmp('colorschemesMatrixTSProductGrid').getStore().each(function(rec){
                if (rec.get('default_legend')) {
                    legend_id = rec.get('legend_id');
                }
            },this);
        }

        //selectedTimeSeries = this.getView().down().lookupReference('selected-timeseries-mapset-dataset-grid'+postfix_graphtype).getStore().getData();
        selectedTimeSeries = Ext.getCmp('selected-timeseries-mapset-dataset-grid_'+postfix_graphtype).getStore().getData();
        //console.info(this.getView().down('timeseriesproductselection').lookupReference('selected-timeseries-mapset-dataset-grid'+postfix_graphtype));

        if (wkt_polygon.getValue().trim() == '') {
            Ext.Msg.show({
               title: esapp.Utils.getTranslation('selectapolygon'),    // 'Select a polygon!',
               msg: esapp.Utils.getTranslation('pleaseselectapolygon'),    // 'Please select or draw a polygon in a MapView!',
               width: 300,
               buttons: Ext.Msg.OK,
               animEl: '',
               icon: Ext.Msg.WARNING
            });
            return timeseriesselections;
        }

        if (selectedTimeSeries.length >0){
            if ( Ext.isObject(Ext.getCmp('radio-year_'+postfix_graphtype)) && Ext.getCmp('radio-year_'+postfix_graphtype).getValue()){
                if (Ext.getCmp("YearTimeseries_"+postfix_graphtype).getValue()== null || Ext.getCmp("YearTimeseries_"+postfix_graphtype).getValue() == '') {
                    Ext.getCmp("YearTimeseries_"+postfix_graphtype).validate();
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
                yearTS = Ext.getCmp("YearTimeseries_"+postfix_graphtype).getValue();

                ts_from_season = Ext.getCmp("ts_from_season_"+postfix_graphtype).getValue();
                ts_to_season = Ext.getCmp("ts_to_season_"+postfix_graphtype).getValue();
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

                tsFromSeason = Ext.getCmp("ts_from_season_"+postfix_graphtype).getValue();
                tsToSeason = Ext.getCmp("ts_to_season_"+postfix_graphtype).getValue();
            }
            else if (Ext.isObject(Ext.getCmp('radio-fromto_'+postfix_graphtype)) && Ext.getCmp('radio-fromto_'+postfix_graphtype).getValue()){
                if (Ext.getCmp("ts_from_period_"+postfix_graphtype).getValue()== null || Ext.getCmp("ts_from_period_"+postfix_graphtype).getValue() == '') {
                    Ext.getCmp("ts_from_period_"+postfix_graphtype).validate();
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
                if (Ext.getCmp("ts_to_period_"+postfix_graphtype).getValue()== null || Ext.getCmp("ts_to_period_"+postfix_graphtype).getValue() == '') {
                    Ext.getCmp("ts_to_period_"+postfix_graphtype).validate();
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
                tsFromPeriod = Ext.getCmp("ts_from_period_"+postfix_graphtype).getValue();
                tsToPeriod = Ext.getCmp("ts_to_period_"+postfix_graphtype).getValue();
            }
            else if (Ext.isObject(Ext.getCmp('radio-compareyears_'+postfix_graphtype)) && Ext.getCmp('radio-compareyears_'+postfix_graphtype).getValue()){
                var selectedYears = Ext.getCmp("ts_selectyearstocompare_"+postfix_graphtype).getStore().getData();

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

                ts_from_season = Ext.getCmp("ts_from_seasoncompare_"+postfix_graphtype).getValue();
                ts_to_season = Ext.getCmp("ts_to_seasoncompare_"+postfix_graphtype).getValue();
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

                tsFromSeason = Ext.getCmp("ts_from_seasoncompare_"+postfix_graphtype).getValue();
                tsToSeason = Ext.getCmp("ts_to_seasoncompare_"+postfix_graphtype).getValue();
            }
            else if (Ext.isObject(Ext.getCmp('radio-multiyears_'+postfix_graphtype)) && Ext.getCmp('radio-multiyears_'+postfix_graphtype).getValue()){
                var multiYearsGrid = Ext.getCmp("ts_selectmultiyears_"+postfix_graphtype);
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
                yearsToCompare = [];
                selectedMultiYears.forEach(function(year) {
                    yearsToCompare.push(year.get('year'));
                });

                ts_from_season = Ext.getCmp("ts_from_seasonmulti_"+postfix_graphtype).getValue();
                ts_to_season = Ext.getCmp("ts_to_seasonmulti_"+postfix_graphtype).getValue();
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

                tsFromSeason = Ext.getCmp("ts_from_seasonmulti_"+postfix_graphtype).getValue();
                tsToSeason = Ext.getCmp("ts_to_seasonmulti_"+postfix_graphtype).getValue();
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
            });
            //console.info(timeseriesselected);
            timeseriesselected = Ext.util.JSON.encode(timeseriesselected);
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
            graphtype: graphtype,
            selectedTimeseries: timeseriesselected,
            yearTS: yearTS,
            tsFromPeriod: tsFromPeriod,
            tsToPeriod: tsToPeriod,
            yearsToCompare: yearsToCompare,
            tsFromSeason: tsFromSeason,
            tsToSeason: tsToSeason,
            wkt_geom: wkt_polygon.getValue()
        };

        return timeseriesselections
    }

    ,generateTimeseriesChart: function(btn){
        var TSChartWinConfig = this.getTimeseriesSelections(btn.graphtype);
        if (TSChartWinConfig != null){
            var newTSChartWin = new esapp.view.analysis.timeseriesChartView(TSChartWinConfig);

            Ext.getCmp('analysismain').add(newTSChartWin);
            newTSChartWin.show();
        }
    }
});
