Ext.define('esapp.view.analysis.timeseriesProductSelectionController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeseriesproductselection'

    ,TimeseriesProductsGridRowClick: function(gridview, record){
        var selectedTimeSeriesProducts = gridview.getSelectionModel().selected.items;
        var alltimeseriesmapsetdatasets = [];
        var yearsData = [];

        //function union_arrays (x, y) {
        //  var obj = {};
        //  for (var i = x.length-1; i >= 0; -- i)
        //     obj[x[i]] = x[i];
        //  for (var i = y.length-1; i >= 0; -- i)
        //     obj[y[i]] = y[i];
        //  var res = []
        //  for (var k in obj) {
        //    if (obj.hasOwnProperty(k))  // <-- optional
        //      res.push(obj[k]);
        //  }
        //  return res;
        //}

        selectedTimeSeriesProducts.forEach(function(product) {
            // ToDO: First loop the mapsets to get the by the user selected mapset if the product has > 1 mapsets.
            var datasets = product.get('productmapsets')[0].timeseriesmapsetdatasets;
            //var datasets = product.get(children)[0].children;
            datasets.forEach(function(datasetObj) {
                //yearsData = Ext.Object.merge(yearsData, datasetObj.years);
                yearsData = esapp.Utils.union_arrays(yearsData, datasetObj.years);
                //console.info(yearsData);
                alltimeseriesmapsetdatasets.push(datasetObj);
            });
            //console.info(product.get('productmapsets')[0].timeseriesmapsetdatasets);
        });
        var yearsDataDict = [];
        yearsData.forEach(function(year) {
            yearsDataDict.push({'year': year});
        });
        Ext.getCmp('timeserieschartselection').getViewModel().getStore('years').setData(yearsDataDict);
        //this.getStore('years').setData(yearsDataDict);

        //var productmapset = record.get('productmapsets')[0];
        this.getStore('timeseriesmapsetdatasets').setData(alltimeseriesmapsetdatasets); // NOTE: Works only if Model does not have idProperty defined, otherwise only the last element is added.

        if (selectedTimeSeriesProducts.length == 0) {
            Ext.getCmp('timeseries-mapset-dataset-grid').hide();
            Ext.getCmp('ts_timeframe').hide();
            Ext.getCmp('gettimeseries_btn').setDisabled(true);
            //Ext.getCmp('gettimeseries_btn2').setDisabled(true);
        }
        else {
            Ext.getCmp('timeseries-mapset-dataset-grid').show();
            Ext.getCmp('ts_timeframe').show();
            Ext.getCmp('gettimeseries_btn').setDisabled(false);
            //Ext.getCmp('gettimeseries_btn2').setDisabled(false);
        }
    }


    ,editTSDrawProperties: function(gridview, recordID){
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
