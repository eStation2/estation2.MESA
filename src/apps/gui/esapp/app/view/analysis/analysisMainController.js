Ext.define('esapp.view.analysis.analysisMainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-analysismain'

    ,loadUserMapTemplatesStore: function(btn){
        //console.info(btn.down().down());

        btn.down().down().getStore('usermaptemplates').load({
            extraParams: {
                userid: esapp.getUser().userid
            },
            callback:function(){

            }
        });
        btn.down().down().show();

        //var mapTemplate = {
        //    userid: 'jurvtk',
        //    isTemplate: true,
        //    templatename: '',
        //    mapviewPosition: [10, 5],
        //    mapviewSize: [1000, 900],
        //    productcode: 'vgt-fapar',
        //    subproductcode: 'fapar',
        //    productversion: 'V2.0',
        //    mapsetcode: 'SPOTV-Africa-1km',
        //    legendid: 99,
        //    legendlayout: 'vertical',
        //    legendObjPosition: [5, 210],
        //    showlegend: true,
        //    titleObjPosition: [35, 20],
        //    titleObjContent: '<font size="3" style="color: rgb(0, 0, 0);"><b>{selected_area}</b></font><div><font size="3" style="color: rgb(0, 0, 0);"><b>{product_name}&nbsp;</b></font><div><font size="3"><b>Decade of <font color="#3366ff">{product_date}</font></b></font></div></div>',
        //    disclaimerObjPosition: [330, 695],
        //    disclaimerObjContent: '<font size="1">​Geographical map, WGS 84 - Resolution 5km</font><div><font size="1">Sources: 1) Image NDVI &nbsp;2) Vectors FAO GAUL 2015</font></div>',
        //    logosObjPosition: [585, 677],
        //    logosObjContent: [
        //        { src:'resources/img/logo/MESA_logo.png', width:'65', height:'50' },
        //        { src:'resources/img/logo/AfricanUnion_logo.jpg', width:'65', height:'50' },
        //        { src:'resources/img/logo/logo_en.gif', width:'65', height:'50' }
        //    ],
        //    showObjects: true,
        //    scalelineObjPosition: [0, 710],
        //    vectorLayers: '',
        //    outmask: false,
        //    outmaskFeature: ''
        //}
        //var newMapViewWin = new esapp.view.analysis.mapView(mapTemplate);
        //
        //this.getView().add(newMapViewWin);
        //newMapViewWin.show();


        //var mapTemplate2 = {
        //    userid: 'jurvtk',
        //    isTemplate: true,
        //    templatename: '',
        //    mapviewPosition: [868, 10],
        //    mapviewSize: [1000, 900],
        //    productcode: 'vgt-fapar',
        //    subproductcode: 'fapar',
        //    productversion: 'V1.4',
        //    mapsetcode: 'SPOTV-Africa-1km',
        //    legendid: 99,
        //    legendlayout: 'horizontal',
        //    legendObjPosition: [5, 230],
        //    showlegend: false,
        //    titleObjPosition: [5, 150],
        //    titleObjContent: '<font size="3" style="color: rgb(0, 0, 0);"><b>{selected_area} - {product_name}&nbsp;</b></font><div><font size="3"><b>Decade of <font color="#3366ff">{product_date}</font></b></font></div>',
        //    disclaimerObjPosition: [5, 550],
        //    disclaimerObjContent: '<font size="1">​Geographical map, WGS 84 - Resolution 5km</font><div><font size="1">Sources: 1) Image NDVI &nbsp;2) Vectors FAO GAUL 2015</font></div>',
        //    logosObjPosition: [300, 560],
        //    logosObjContent: '',
        //    showObjects: false,
        //    scalelineObjPosition: [100, 560],
        //    vectorLayers: '',
        //    outmask: false,
        //    outmaskFeature: ''
        //}
        //var newMapViewWin2 = new esapp.view.analysis.mapView(mapTemplate2);
        //
        //this.getView().add(newMapViewWin2);
        //newMapViewWin2.show();
    }

    ,newMapView: function() {
        var newMapViewWin = new esapp.view.analysis.mapView({
            epsg: 'EPSG:4326'
        });
        this.getView().add(newMapViewWin);
        newMapViewWin.show();
    }

    ,layerAdmin: function(){
        var newLayerAdminWin = new esapp.view.analysis.layerAdmin();
        this.getView().add(newLayerAdminWin);
        newLayerAdminWin.show();
        this.getView().lookupReference('analysismain_layersbtn').disable();
    }

    ,showTimeseriesChartSelection: function(){
        var timeseriesChartSelectionWindow = this.getView().lookupReference('timeserieschartselection');
        timeseriesChartSelectionWindow.show();
        timeseriesChartSelectionWindow.fireEvent('align');
    }

    ,toggleBackgroundlayer: function(btn, event) {
        var analysismain = btn.up().up();
        var i, ii;
        var me = this.getView();

        if (!esapp.Utils.objectExists(analysismain.map)){
            me.map = new ol.Map({
                layers: me.backgroundLayers,
                // renderer: _getRendererFromQueryString(),
                projection:"EPSG:4326",
                displayProjection:"EPSG:4326",
                target: 'backgroundmap_'+ me.id,
                //overlays: [overlay],
                view: me.commonMapView,
                controls: ol.control.defaults({
                    zoom: false,
                    attribution:false,
                    attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                      collapsible: true // false to show always without the icon.
                    })
                }).extend([me.scaleline])   // me.mousePositionControl,
            });
        }

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

    ,_loadTimeseriesProductsGrid: function() {

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
    }

    ,_TimeseriesProductsGridRowClick: function(gridview, record){
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
    }

    ,_getTimeseriesSelections: function(){
        var timeseriesgrid = this.getView().lookupReference('timeseries-mapset-dataset-grid');
        var selectedTimeSeries = timeseriesgrid.getSelectionModel().selected.items;
        var wkt_polygon = this.getView().lookupReference('wkt_polygon');
        var timeseriesselected = [];
        var timeseriesselections = null;
        var yearTS = '';
        var tsFromPeriod = '';
        var tsToPeriod = '';

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
                //console.info(product);
                //product.set('description', 'JURRIAAN CHANGES ALL DESCRIPTIONS!!!!!!')
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
            charttype: 'default',
            country:'',
            region: ''
        };

        return timeseriesselections
    }

    ,_generateTimeseriesChart: function(btn){

        var TSChartWinConfig = this.getTimeseriesSelections();
        if (TSChartWinConfig != null){
            var newTSChartWin = new esapp.view.analysis.timeseriesChartView(TSChartWinConfig);

            this.getView().add(newTSChartWin);
            newTSChartWin.show();
        }
    }

    ,_editTSDrawProperties: function(gridview, recordID){
        var source = {};
        var myNewRecord = null;
        var TSrecord = gridview.store.getAt(recordID);
        var tsDrawPropertiesStore = this.getStore('timeseriesdrawproperties');

        if (!tsDrawPropertiesStore.isLoaded())
            tsDrawPropertiesStore.load();

        tsDrawPropertiesStore.clearFilter(true);
        tsDrawPropertiesStore.filterBy(function (record, id) {
            if (record.get("productcode") == TSrecord.get('productcode') && record.get("version") == TSrecord.get('version') && record.get("subproductcode") == TSrecord.get('subproductcode')) {
                return true;
            }
            return false;
        });

        var tsdrawprobs_record = tsDrawPropertiesStore.findRecord('productcode', TSrecord.get('productcode'));

        //console.info(tsdrawprobs_record);
        if (tsdrawprobs_record == null){
            var newtitle = '',
                newunit = '',
                newmin = null,
                newmax = null,
                newoposite = false,
                newcharttype = 'line',
                newyaxes_id = TSrecord.get('productcode') + ' - ' + TSrecord.get('version'),
                newtitle_color = esapp.Utils.convertRGBtoHex('0 0 0');

            tsDrawPropertiesStore.clearFilter(true);
            tsDrawPropertiesStore.filterBy(function (record, id) {
                if (record.get("productcode") == TSrecord.get('productcode') && record.get("version") == TSrecord.get('version')) {
                    return true;
                }
                return false;
            });

            var similarTSrecord = tsDrawPropertiesStore.getAt(0);
            if (similarTSrecord != null){
                newtitle = similarTSrecord.get('title');
                newunit = similarTSrecord.get('unit');
                newmin = similarTSrecord.get('min');
                newmax = similarTSrecord.get('max');
                newoposite = similarTSrecord.get('oposite');
                newcharttype = similarTSrecord.get('charttype');
                newyaxes_id = similarTSrecord.get('yaxes_id');
                newtitle_color = similarTSrecord.get('title_color');
            }

            //myNewRecord = new tsDrawPropertiesStore.recordType({
            myNewRecord = new esapp.model.TSDrawProperties({
                productcode: TSrecord.get('productcode'),
                subproductcode: TSrecord.get('subproductcode'),
                version: TSrecord.get('version'),
                title: newtitle,
                unit: newunit,
                min: newmin,
                max: newmax,
                oposite: newoposite,
                tsname_in_legend: TSrecord.get('productcode') + ' - ' + TSrecord.get('version') + ' - ' + TSrecord.get('subproductcode'),
                charttype: newcharttype,
                linestyle: 'Solid',
                linewidth: 2,
                color: esapp.Utils.convertRGBtoHex('0 0 0'),
                yaxes_id: newyaxes_id,
                title_color: newtitle_color,
                aggregation_type: 'mean',
                aggregation_min: null,
                aggregation_max: null
            });

            tsDrawPropertiesStore.add(myNewRecord);
            tsdrawprobs_record = myNewRecord;

            createTSDrawPropertiesWin();

        }
        else {
            createTSDrawPropertiesWin();
        }

        //var texteditor = new Ext.grid.GridEditor(new Ext.form.TextField({allowBlank: false,selectOnFocus: true}));
        //var numbereditor = new Ext.grid.GridEditor(new Ext.form.NumberField({allowBlank: false,selectOnFocus: true}));
        //var cedit = new Ext.grid.GridEditor(new Ext.ux.ColorField({allowBlank: false,selectOnFocus: true}));

        function createTSDrawPropertiesWin(){
            var myTSDrawPropertiesWin = Ext.getCmp('TSDrawPropertiesWin');
            if (myTSDrawPropertiesWin!=null && myTSDrawPropertiesWin!='undefined' ) {
                myTSDrawPropertiesWin.close();
            }

            var colorrenderer = function(color) {
                renderTpl = color;

                if (color.trim()==''){
                    renderTpl = 'transparent';
                }
                else {
                    renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
                }
                return renderTpl;
            }

            source = {
                yaxes_id: tsdrawprobs_record.get('yaxes_id'),
                tsname_in_legend: tsdrawprobs_record.get('tsname_in_legend'),
                //oposite: tsdrawprobs_record.get('oposite'),
                //unit: tsdrawprobs_record.get('unit'),
                charttype: tsdrawprobs_record.get('charttype'),
                linestyle: tsdrawprobs_record.get('linestyle'),
                linewidth: tsdrawprobs_record.get('linewidth'),
                color: esapp.Utils.convertRGBtoHex(tsdrawprobs_record.get('color'))
                //aggregation_type: tsdrawprobs_record.get('aggregation_type'),
                //aggregation_min: tsdrawprobs_record.get('aggregation_min'),
                //aggregation_max: tsdrawprobs_record.get('aggregation_max')
            }

            var TSDrawPropertiesWin = new Ext.Window({
                 id:'TSDrawPropertiesWin'
                ,title: esapp.Utils.getTranslation('Time series draw properties for ') + tsdrawprobs_record.get('productcode') + ' - ' + tsdrawprobs_record.get('version') + ' - ' +  tsdrawprobs_record.get('subproductcode')
                ,width:450
                ,plain: true
                ,modal: true
                ,resizable: true
                ,closable:true
                ,layout: {
                     type: 'fit'
                },
                listeners: {
                    close: function(){
                        //console.info('closing window and removing filter');
                        tsDrawPropertiesStore.clearFilter(true);
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
                        yaxes_id: {
                            displayName: esapp.Utils.getTranslation('yaxes_id'),   // 'Yaxe ID',
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:false
                            }
                        },
                        tsname_in_legend: {
                            displayName: esapp.Utils.getTranslation('tsname_in_legend'),   // 'Time series name in legend',
                            //type: 'text',
                            editor: {
                                xtype: 'textfield',
                                selectOnFocus:false
                            }
                        },

                        //oposite: {
                        //    displayName: esapp.Utils.getTranslation('oposite'),   // 'Oposite',
                        //    type: 'boolean'
                        //},
                        //unit: {
                        //    displayName: esapp.Utils.getTranslation('unit'),   // 'Unit',
                        //    //type: 'text',
                        //    editor: {
                        //        xtype: 'textfield',
                        //        selectOnFocus:false
                        //    }
                        //},
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
                        //,aggregation_type: {
                        //    displayName: esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                        //    editor: {
                        //        xtype: 'combobox',
                        //        store: ['mean', 'count'],
                        //        forceSelection: true
                        //    }
                        //},
                        //aggregation_min: {
                        //    displayName: esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                        //    type: 'number'
                        //},
                        //aggregation_max: {
                        //    displayName: esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                        //    type: 'number'
                        //}
                    },
                    listeners: {
                        propertychange: function( source, recordId, value, oldValue, eOpts ){
                            if (value != oldValue)
                                tsdrawprobs_record.set(recordId, value)
                        }
                    }
                }]

            });
            TSDrawPropertiesWin.show();
            TSDrawPropertiesWin.alignTo(gridview.getEl(),"r-tr", [-6, 0]);  // See: http://www.extjs.com/deploy/dev/docs/?class=Ext.Window&member=alignTo
        }
    }
});
