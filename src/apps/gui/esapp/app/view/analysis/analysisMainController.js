Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,newMapView: function() {

        var newMapViewWin = new esapp.view.analysis.mapView({
            epsg: 'EPSG:4326'
        });
        this.getView().add(newMapViewWin);
        newMapViewWin.show();
    }

    ,toggleBackgroundlayer: function(btn, event) {
        var analysismain = btn.up().up();
        var i, ii;
        if (btn.pressed){
            btn.setText(esapp.Utils.getTranslation('hidebackgroundlayer'));
            analysismain.map.addControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                //analysismain.backgroundLayers[i].setVisible(analysismain.bingStyles[i] == 'Road');
                analysismain.backgroundLayers[i].setVisible(true);
            }
        }
        else {
            btn.setText(esapp.Utils.getTranslation('showbackgroundlayer'));
            analysismain.map.removeControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(false);
            }
        }
    }

    ,loadTimeseriesProductsGrid: function() {

        var prodgrid = this.getView().lookupReference('TimeSeriesProductsGrid');
        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('loading'), // 'Loading...',
            target : prodgrid
        });
        myLoadMask.show();

        this.getStore('products').load({
            callback:function(){
                myLoadMask.hide();
            }
        });
    },

    TimeseriesProductsGridRowClick: function(gridview, record){
        var selectedTimeSeriesProducts = gridview.getSelectionModel().selected.items;
        var timeseriesmapsetdatasets = [];
        var yearsData = [];

        function union_arrays (x, y) {
          var obj = {};
          for (var i = x.length-1; i >= 0; -- i)
             obj[x[i]] = x[i];
          for (var i = y.length-1; i >= 0; -- i)
             obj[y[i]] = y[i];
          var res = []
          for (var k in obj) {
            if (obj.hasOwnProperty(k))  // <-- optional
              res.push(obj[k]);
          }
          return res;
        }

        selectedTimeSeriesProducts.forEach(function(product) {
            // ToDO: First loop the mapsets to get the by the user selected mapset if the product has > 1 mapsets.
            var datasets = product.get('productmapsets')[0].timeseriesmapsetdatasets;
            datasets.forEach(function(datasetObj) {
                //yearsData = Ext.Object.merge(yearsData, datasetObj.years);
                yearsData = union_arrays(yearsData, datasetObj.years);
                //console.info(yearsData);
                timeseriesmapsetdatasets.push(datasetObj);
            });
            //console.info(product.get('productmapsets')[0].timeseriesmapsetdatasets);
        });
        var yearsDataDict = [];
        yearsData.forEach(function(year) {
            yearsDataDict.push({'year': year});
        });
        //var productmapset = record.get('productmapsets')[0];
        this.getStore('years').setData(yearsDataDict);
        this.getStore('timeseriesmapsetdatasets').setData(timeseriesmapsetdatasets);
        //console.info(timeseriesmapsetdatasets);

        if (selectedTimeSeriesProducts.length == 0) {
            Ext.getCmp('timeseries-mapset-dataset-grid').hide();
            Ext.getCmp('ts_timeframe').hide();
            Ext.getCmp('gettimeseries_btn').setDisabled(true);
            Ext.getCmp('gettimeseries_btn2').setDisabled(true);
        }
        else {
            Ext.getCmp('timeseries-mapset-dataset-grid').show();
            Ext.getCmp('ts_timeframe').show();
            Ext.getCmp('gettimeseries_btn').setDisabled(false);
            Ext.getCmp('gettimeseries_btn2').setDisabled(false);
        }
    },

    getTimeseriesSelections: function(){
        var timeseriesgrid = this.getView().lookupReference('timeseries-mapset-dataset-grid');
        var selectedTimeSeries = timeseriesgrid.getSelectionModel().selected.items;
        var wkt_polygon = this.getView().lookupReference('wkt_polygon');
        var timeseriesselected = [];
        var timeseriesselections = null;
        var yearTS = '';
        var tsFromPeriod = '';
        var tsToPeriod = '';

        //console.info(selectedTimeSeries);
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
            if (Ext.getCmp('radio-year').getValue()){
                if (Ext.getCmp("YearTimeseries").getValue()== null || Ext.getCmp("YearTimeseries").getValue() == '') {
                    Ext.getCmp("YearTimeseries").validate();
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
                yearTS = Ext.getCmp("YearTimeseries").getValue();
                tsFromPeriod = '';
                tsToPeriod = '';
            }
            else if (Ext.getCmp('radio-fromto').getValue()){
                if (Ext.getCmp("ts_from_period").getValue()== null || Ext.getCmp("ts_from_period").getValue() == '') {
                    Ext.getCmp("ts_from_period").validate();
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
                if (Ext.getCmp("ts_to_period").getValue()== null || Ext.getCmp("ts_to_period").getValue() == '') {
                    Ext.getCmp("ts_to_period").validate();
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
                tsFromPeriod = Ext.getCmp("ts_from_period").getValue();
                tsToPeriod = Ext.getCmp("ts_to_period").getValue();
                yearTS = '';
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

            selectedTimeSeries.forEach(function(product) {
                var productObj = {
                    "productcode": product.get('productcode'),
                    "version": product.get('version'),
                    "subproductcode": product.get('subproductcode'),
                    "mapsetcode": product.get('mapsetcode')
                };

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
            selectedTimeseries: timeseriesselected,
            yearTS: yearTS,
            tsFromPeriod: tsFromPeriod,
            tsToPeriod: tsToPeriod,
            wkt:wkt_polygon.getValue(),
            country:'',
            region: ''
        };

        return timeseriesselections
    },
    generateTimeseriesChart: function(btn){

        var TSChartWinConfig = this.getTimeseriesSelections();
        if (TSChartWinConfig != null){
            var newTSChartWin = new esapp.view.analysis.timeseriesChartView(TSChartWinConfig);

            //var newTSChartWin = new esapp.view.analysis.timeseriesChartView({
            //    selectedTimeseries: timeseriesselected,
            //    yearTS: yearTS,
            //    tsFromPeriod: tsFromPeriod,
            //    tsToPeriod: tsToPeriod,
            //    wkt:wkt_polygon.getValue(),
            //    country:'',
            //    region: ''
            //});
            this.getView().add(newTSChartWin);
            newTSChartWin.show();
        }
    }

});
