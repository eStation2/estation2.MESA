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
            btn.setText('Show Background layer');
            analysismain.map.removeControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                analysismain.backgroundLayers[i].setVisible(!btn.pressed);
            }
        }
        else {
            btn.setText('Hide Background layer');
            analysismain.map.addControl(analysismain.mousePositionControl);
            for (i = 0, ii = analysismain.backgroundLayers.length; i < ii; ++i) {
                //analysismain.backgroundLayers[i].setVisible(analysismain.bingStyles[i] == 'Road');
                analysismain.backgroundLayers[i].setVisible(true);
            }
        }
    }

    ,loadTimeseriesProductsGrid: function() {

        var prodgrid = this.getView().lookupReference('TimeSeriesProductsGrid');
        var myLoadMask = new Ext.LoadMask({
            msg    : 'Loading...',
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
        selectedTimeSeriesProducts.forEach(function(product) {
            // ToDO: First loop the mapsets to get the by the user selected mapset if the product has > 1 mapsets.
            var datasets = product.get('productmapsets')[0].timeseriesmapsetdatasets;
            datasets.forEach(function(datasetObj) {
                timeseriesmapsetdatasets.push(datasetObj);
            });
            //console.info(product.get('productmapsets')[0].timeseriesmapsetdatasets);
        });
        //var productmapset = record.get('productmapsets')[0];

        this.getStore('timeseriesmapsetdatasets').setData(timeseriesmapsetdatasets);

        if (selectedTimeSeriesProducts.length == 0) {
            Ext.getCmp('timeseries-mapset-dataset-grid').hide();
            Ext.getCmp('ts_timeframe').hide();
            Ext.getCmp('gettimeseries_btn').setDisabled(true);
        }
        else {
            Ext.getCmp('timeseries-mapset-dataset-grid').show();
            Ext.getCmp('ts_timeframe').show();
            Ext.getCmp('gettimeseries_btn').setDisabled(false);
        }
    },

    getTimeseries: function(btn){
        var timeseriesgrid = this.getView().lookupReference('timeseries-mapset-dataset-grid');
        var selectedTimeSeries = timeseriesgrid.getSelectionModel().selected.items;
        var wkt_polygon = this.getView().lookupReference('wkt_polygon');
        var yearTS = '';
        var tsFromPeriod = '';
        var tsToPeriod = '';

        if (wkt_polygon.getValue() == '') {
            Ext.Msg.show({
               title: 'Select a polygon!',
               msg: 'Please select or draw a polygon in a MapView!',
               width: 300,
               buttons: Ext.MessageBox.OK,
               animEl: '',
               icon: Ext.MessageBox.WARNING
            });
            return;
        }

        if (selectedTimeSeries.length >0){
            if (Ext.getCmp('radio-year').getValue()){
                if (Ext.getCmp("YearTimeseries").getValue()== null || Ext.getCmp("YearTimeseries").getValue() == '') {
                    Ext.getCmp("YearTimeseries").validate();
                    Ext.Msg.show({
                       title: 'Mandatory field',
                       msg: 'Please select a year!',
                       width: 300,
                       buttons: Ext.MessageBox.OK,
                       animEl: '',
                       icon: Ext.MessageBox.WARNING
                    });
                    return;
                }
                yearTS = Ext.getCmp("YearTimeseries").getValue();
                tsFromPeriod = '';
                tsToPeriod = '';
            }
            if (Ext.getCmp('radio-fromto').getValue()){
                if (Ext.getCmp("ts_from_period").getValue()== null || Ext.getCmp("ts_from_period").getValue() == '') {
                    Ext.getCmp("ts_from_period").validate();
                    Ext.Msg.show({
                       title: 'Mandatory field',
                       msg: 'Please select a "From date"!',
                       width: 300,
                       buttons: Ext.MessageBox.OK,
                       animEl: '',
                       icon: Ext.MessageBox.WARNING
                    });
                    return;
                }
                if (Ext.getCmp("ts_to_period").getValue()== null || Ext.getCmp("ts_to_period").getValue() == '') {
                    Ext.getCmp("ts_to_period").validate();
                    Ext.Msg.show({
                       title: 'Mandatory field',
                       msg: 'Please select a "To date"!',
                       width: 300,
                       buttons: Ext.MessageBox.OK,
                       animEl: '',
                       icon: Ext.MessageBox.WARNING
                    });
                    return;
                }
                tsFromPeriod = Ext.getCmp("ts_from_period").getValue();
                tsToPeriod = Ext.getCmp("ts_to_period").getValue();
                yearTS = '';
            }

            var timeseriesselected = [];
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
               title: 'Mandatory field',
               msg: 'Please select one or more times series!',
               width: 300,
               buttons: Ext.MessageBox.OK,
               animEl: '',
               icon: Ext.MessageBox.WARNING
            });
            return;
        }


        var newTSChartWin = new esapp.view.analysis.timeseriesChartView({
            selectedTimeseries: timeseriesselected,
            yearTS: yearTS,
            tsFromPeriod: tsFromPeriod,
            tsToPeriod: tsToPeriod,
            wkt:wkt_polygon.getValue(),
            country:'',
            region: ''
        });
        this.getView().add(newTSChartWin);
        newTSChartWin.show();
    }

});
