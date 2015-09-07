Ext.define('esapp.view.analysis.mapViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-mapview'

    ,addProductLayer: function(productcode, productversion, mapsetcode, subproductcode, legendid, productname) {
        var me = this;
        var params = {
               productcode:productcode,
               mapsetcode:mapsetcode,
               productversion:productversion,
               subproductcode:subproductcode
        };
        me.getView().productcode = productcode;
        me.getView().productversion = productversion;
        me.getView().mapsetcode = mapsetcode;
        me.getView().subproductcode = subproductcode;
        me.getView().legendid = legendid;
        me.getView().productname = productname;

        Ext.Ajax.request({
            method: 'GET',
            url:'analysis/gettimeline',
            params: params,
            loadMask:esapp.Utils.getTranslation('loadingdata'),  // 'Loading data...',
            scope: me,
            success:function(response, request ){
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                var dataLength = responseJSON.total,
                    data = [],
                    i = 0,
                    color = '#ff0000';

                for (i; i < dataLength; i += 1) {
                    if (i == dataLength-1) {
                        me.getView().productdate = responseJSON.timeline[i]['date'];
                    }

                    if (responseJSON.timeline[i]['present'] == "true") {
                        color = '#08a355';
                        data.push({
                            x: responseJSON.timeline[i]['datetime'], // the date
                            y: 1,
                            color: color,
                            date: responseJSON.timeline[i]['date'],
                            events: {
                                click: function () {
                                    me.getView().getController().updateProductLayer(productcode,
                                        productversion,
                                        mapsetcode,
                                        subproductcode,
                                        legendid,
                                        this.date);
                                }
                            }
                        });
                    }
                    else {
                        color ='#ff0000';
                        data.push({
                            x: responseJSON.timeline[i]['datetime'], // the date
                            y: 1,
                            color: color,
                            date: responseJSON.timeline[i]['date']
                        });
                    }
                }
                var mapview_timelinechart_container = me.lookupReference('time-line-chart' + me.getView().id);
                mapview_timelinechart_container.timelinechart.series[0].setData(data, false);

                // Set the MapView window title to the selected product and date
                var versiontitle = '';
                if (productversion !== 'undefined'){
                    versiontitle = ' <b class="smalltext">' + productversion + '</b>';
                }
                var mapsetcodeHTML = ' - <b class="smalltext">' + me.getView().mapsetcode + '</b>';

                var pattern = /(\d{4})(\d{2})(\d{2})/;
                me.getView().productdate = me.getView().productdate.replace(pattern,'$3-$2-$1');
                //var dt = new Date(me.getView().productdate.replace(pattern,'$3-$2-$1'));
                var productdateHTML = ' - <b class="smalltext">' + me.getView().productdate + '</b>';
                var mapwvieTitle = productname + versiontitle + mapsetcodeHTML + productdateHTML;
                me.getView().setTitle(mapwvieTitle);

                // Show product time line
                var mapviewtimeline = me.lookupReference('product-time-line_' + me.getView().id);
                mapviewtimeline.setHidden(false);
                mapviewtimeline.expand();
                me.getView().getController().redrawTimeLine(me.getView());
                //me.getView().center();

            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function ( result, request) {}
        });


        //var mapviewtimeline = this.getView().getDockedItems('toolbar[dock="bottom"]')[0];
        //var searchtimeline = 'container[id="product-time-line_' + this.getView().id + '"]'
        //var mapviewtimeline = this.getView().down(searchtimeline);
        //var mapviewtimeline = me.lookupReference('product-time-line_' + me.getView().id);
        //mapviewtimeline.setHidden(false);
        //mapviewtimeline.expand();

        me.getView().productlayer = new ol.layer.Image({
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            type: 'base',
            visible: true,
            source: new ol.source.ImageWMS({
                url: 'analysis/getproductlayer',
                type: 'base',
                crossOrigin: 'anonymous',
                attributions: [new ol.Attribution({
                    html: '&copy; <a href="https://ec.europa.eu/jrc/">'+esapp.Utils.getTranslation('estation2')+'</a>'
                })],
                params: {
                    productcode:productcode,
                    productversion:productversion,
                    subproductcode:subproductcode,
                    mapsetcode:mapsetcode,
                    legendid:legendid,
                    'FORMAT': 'image/png'
                },
                serverType: 'mapserver' /** @type {ol.source.wms.ServerType}  ('mapserver') */
            })
        });

        var productlayer_idx = me.getView().getController().findlayer(me.getView().map, 'productlayer');
        if (productlayer_idx != -1)
            me.getView().map.getLayers().removeAt(productlayer_idx);
        //me.getView().map.removeLayer(me.getView().map.getLayers().a[0]);
        //me.getView().map.addLayer(me.getView().productlayer);
        me.getView().map.getLayers().insertAt(0, me.getView().productlayer);

        me.getView().getController().addLayerSwitcher(me.getView().map);
    }

    ,updateProductLayer: function(productcode, productversion, mapsetcode, subproductcode, legendid, clickeddate) {
        this.getView().productlayer = new ol.layer.Image({
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            type: 'base',
            visible: true,
            source: new ol.source.ImageWMS({
                url: 'analysis/getproductlayer',
                crossOrigin: 'anonymous',
                attributions: [new ol.Attribution({
                    html: '&copy; <a href="https://ec.europa.eu/jrc/">'+esapp.Utils.getTranslation('estation2')+'</a>'
                })],
                params: {
                    productcode:productcode,
                    productversion:productversion,
                    subproductcode:subproductcode,
                    mapsetcode:mapsetcode,
                    legendid:legendid,
                    date:clickeddate,
                    'FORMAT': 'image/png'
                },
                serverType: 'mapserver' /** @type {ol.source.wms.ServerType}  ('mapserver') */
            })
        });
        var productlayer_idx = this.getView().getController().findlayer(this.getView().map, 'productlayer');
        if (productlayer_idx != -1)
            this.getView().map.getLayers().removeAt(productlayer_idx);
        //this.getView().map.removeLayer(this.getView().map.getLayers().a[0]);
        //this.getView().map.addLayer(this.getView().productlayer);
        this.getView().map.getLayers().insertAt(0, this.getView().productlayer);

        var versiontitle = '';
        if (productversion !== 'undefined'){
            versiontitle = ' <b class="smalltext">' + productversion + '</b>';
        }

        var mapsetcodeHTML = ' - <b class="smalltext">' + this.getView().mapsetcode + '</b>';

        var pattern = /(\d{4})(\d{2})(\d{2})/;
        this.getView().productdate = clickeddate.replace(pattern,'$3-$2-$1');
        var productdateHTML = ' - <b class="smalltext">' + this.getView().productdate + '</b>';

        //var mapwvieTitle = this.getView().productname + versiontitle + ' - <b class="smalltext">' + this.getView().productdate + '</b>';
        var mapwvieTitle = this.getView().productname + versiontitle + mapsetcodeHTML + productdateHTML;

        this.getView().setTitle(mapwvieTitle);

    }

    ,redrawTimeLine: function (mapview) {
        var mapviewtimeline = mapview.lookupReference('product-time-line_' + mapview.id);
        var mapview_timelinechart_container = mapview.lookupReference('time-line-chart' + mapview.id);
        var timeline_container_size = mapviewtimeline.getSize();
        mapview_timelinechart_container.timelinechart.container.width = timeline_container_size.width;
        mapview_timelinechart_container.timelinechart.setSize(timeline_container_size.width-15, timeline_container_size.height, false);
        //mapview_timelinechart_container.timelinechart.reflow();
        mapview_timelinechart_container.timelinechart.redraw();
        mapview_timelinechart_container.doLayout();
    }

    ,toggleLink: function(btn, event) {
        var mapviewwin = btn.up().up();

        if (btn.pressed) {
            mapviewwin.map.setView(mapviewwin.mapView);
            //btn.setText('Link');
            btn.setIconCls('link');
        }
        else {
            mapviewwin.map.setView(mapviewwin.up().commonMapView);
            //btn.setText('Unlink');
            btn.setIconCls('unlink');
        }
    }

    ,openProductNavigator: function(btn, event) {
        var productNavigatorWin = Ext.getCmp(btn.up().up().getId()+'-productnavigator');
        //var productNavigatorWin = btn.up().up().up('window[id='+btn.up().up().getId()+'-productnavigator]');
        //if (Ext.isObject(productNavigatorWin)) {}
        if (!productNavigatorWin){
            productNavigatorWin = new esapp.view.analysis.ProductNavigator({mapviewid:btn.up().up().getId()});
        }
        productNavigatorWin.show();
        //var productsgridstore = productNavigatorWin.lookupReference('productsGrid').getStore('products');
        //if (productsgridstore.isStore) {
        //    productsgridstore.load({loadMask:true});
        //}
    }

    ,findlayer: function (map, layer_id){
        var layer_idx = -1;
        map.getLayers().getArray().forEach(function (layer,idx){
            var this_layer_id = layer.get("layer_id")
            if(this_layer_id == layer_id){
              layer_idx = idx;
            }
        });
        return layer_idx;
    }

    ,addLayerSwitcher: function (map){
        var layerswitcherexists = false;
        var mControls = map.getControls().a;

        for (var a = 0; a < mControls.length; a++) {
            if( mControls[a] instanceof ol.control.LayerSwitcher){
                layerswitcherexists = true;
            }
        }
        if (!layerswitcherexists) {
            var layerSwitcher = new ol.control.LayerSwitcher({
                tipLabel: esapp.Utils.getTranslation('layers')   // 'Layers' // Optional label for button
            });
            map.addControl(layerSwitcher);
        }
    }

    ,addVectorLayer: function(menuitem){
        // ToDo: Open a new window from which the user can select an in the eStation2 existing or upload a vector layer.
        // ToDo: Have the user set vector layer setting before adding the layer to the map.
        // For now a predefined GeoJSON layer with fixed settings is added.
        //console.info(Ext.ComponentQuery.query('button[name=vbtn-'+this.getView().id+']'));
        //Ext.ComponentQuery.query('button[name=vbtn-'+this.getView().id+']').collapse();

        //this.getView().lookupReference('vbtn-'+this.getView().id).collapse();

        var me = this.getView();
        var geojsonfile = menuitem.geojsonfile,
            namefield = '',
            adminlevel = menuitem.level,
            vectorlayer_idx = -1,
            layertitle = menuitem.boxLabel,
            linecolor = menuitem.linecolor;

        if (menuitem.name == 'admin0'){
            namefield = 'ADM0_NAME';
        }
        else if (menuitem.name == 'admin1'){
            namefield = 'ADM1_NAME';
        }
        else if (menuitem.name == 'admin2'){
            namefield = 'ADM2_NAME';
        }

        if (menuitem.checked) {
            //console.info(Ext.getCmp(me.id));
            //var mapViewContainer = this.getView().lookupReference('mapcontainer_'+me.id);
            var myLoadMask = new Ext.LoadMask({
                msg    : esapp.Utils.getTranslation('loadingvectorlayer'),   // 'Loading vector layer...',
                target : Ext.getCmp(me.id)
            });
            myLoadMask.show();


            var vectorSource = new ol.source.GeoJSON({
                projection: 'EPSG:4326', // 'EPSG:3857',  //
                //url: 'resources/geojson/countries.geojson'
                //url: 'resources/geojson/' + geojsonfile,
                url: 'analysis/getvectorlayer?file=' + geojsonfile
            });

            var listenerKey = vectorSource.on('change', function(e) {
              if (vectorSource.getState() == 'ready') {
                // hide loading icon
                myLoadMask.hide();
                // and unregister the "change" listener
                ol.Observable.unByKey(listenerKey);
                // or vectorSource.unByKey(listenerKey) if
                // you don't use the current master branch
                // of ol3
              }
              else {
                myLoadMask.hide();
              }
            });

            var styleCache = {};
            var vectorLayer = new ol.layer.Vector({
                title: layertitle,
                layer_id: menuitem.name,
                layerorderidx: menuitem.layerorderidx,
                visible: true,
                source: vectorSource,
                style: function (feature, resolution) {
                    var text = resolution < 5000 ? feature.get(namefield) : '';
                    if (!styleCache[text]) {
                        styleCache[text] = [new ol.style.Style({
                            //fill: new ol.style.Fill({
                            //  color: 'rgba(255, 255, 255, 0.6)'
                            //}),
                            cursor: "pointer",
                            stroke: new ol.style.Stroke({
                                color: linecolor, // '#319FD3',
                                width: 1
                            })
                            //,text: new ol.style.Text({
                            //  font: '12px Calibri,sans-serif',
                            //  text: text,
                            //  fill: new ol.style.Fill({
                            //    color: '#000'
                            //  }),
                            //  stroke: new ol.style.Stroke({
                            //    color: '#fff',
                            //    width: 3
                            //  })
                            //})
                        })];
                    }
                    return styleCache[text];
                }
            });

            //me.layers.push(vectorLayer);
            //me.map.removeLayer(this.getView().map.getLayers().a[menuitem.layerorderidx]);
            //me.map.addLayer(vectorLayer);
            vectorlayer_idx = me.getController().findlayer(me.map, menuitem.name);
            if (vectorlayer_idx != -1)
                me.map.getLayers().removeAt(vectorlayer_idx);

            var layer_idx = menuitem.layerorderidx;
            me.map.getLayers().getArray().forEach(function (layer, idx) {
                var this_layer_id = layer.get("layerorderidx")
                if (this_layer_id > menuitem.layerorderidx) {
                    layer_idx = idx;
                }
            });
            me.map.getLayers().insertAt(layer_idx, vectorLayer);

            me.getController().addLayerSwitcher(me.map);


            var highlightStyleCache = {};

            var featureOverlay = new ol.FeatureOverlay({
              map: me.map,
              style: function(feature, resolution) {
                var text = resolution < 5000 ? feature.get(namefield) : '';
                if (!highlightStyleCache[text]) {
                  highlightStyleCache[text] = [new ol.style.Style({
                    stroke: new ol.style.Stroke({
                      color: '#319FD3',     // '#f00',
                      width: 2
                    })
                    ,fill: new ol.style.Fill({
                      color: 'rgba(49,159,211,0.1)'    // 'rgba(255,0,0,0.1)'
                    })
                    //,text: new ol.style.Text({
                    //  font: '12px Calibri,sans-serif',
                    //  text: text,
                    //  fill: new ol.style.Fill({
                    //    color: '#000'
                    //  }),
                    //  stroke: new ol.style.Stroke({
                    //    color: '#f00',
                    //    width: 3
                    //  })
                    //})
                  })];
                }
                return highlightStyleCache[text];
              }
            });

            var highlight;
            var displayFeatureInfo = function(pixel) {

                var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                    return feature;
                });

                //var featureTooltip = Ext.create('Ext.tip.ToolTip', {
                //    //target: Ext.getCmp(me.id), // feature,
                //    alwaysOnTop: true,
                //    anchor: 'right',
                //    trackMouse: true,
                //    html: 'Tracking while you move the mouse'
                //});
                //featureTooltip.setTarget(feature);
                ///** Create an overlay to anchor the popup to the map. */
                //var overlay = new ol.Overlay({
                //  element: featureTooltip.getEl()  // undefined!!!!!!
                //});
                //
                ////me.map.overlays.push(overlay);
                //me.map.addOverlay(overlay);
                //overlay.setPosition(pixel);

                var regionname = Ext.get('region_name_' + me.id);

                if (feature) {
                    //regionname.setHtml(feature.get(namefield));
                    if (adminlevel == 'admin0') {
                        regionname.setHtml(feature.get('ADM0_NAME'));
                    }
                    else if (adminlevel == 'admin1') {
                        regionname.setHtml(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    }
                    else if (adminlevel == 'admin2') {
                        regionname.setHtml(feature.get('ADM0_NAME') + ' - ' +
                                           feature.get('ADM1_NAME') + ' - ' +
                                           feature.get('ADM2_NAME'));
                    }
                    //featureTooltip.html = feature.getId() + ': ' + feature.get(namefield);
                } else {
                    regionname.setHtml('&nbsp;');
                    //featureTooltip.html = '&nbsp;';
                }

                if (feature !== highlight) {
                    if (highlight) {
                        featureOverlay.removeFeature(highlight);
                    }
                    if (feature) {
                        featureOverlay.addFeature(feature);
                    }
                    highlight = feature;
                }
            };

            selectStyleCache = {};
            var selectedFeatureOverlay = new ol.FeatureOverlay({
              map: me.map,
              style: function(feature, resolution) {
                var text = resolution < 5000 ? feature.get(namefield) : '';
                if (!selectStyleCache[text]) {
                  selectStyleCache[text] = [new ol.style.Style({
                    stroke: new ol.style.Stroke({
                      color: '#f00',
                      width: 2
                    })
                    ,fill: new ol.style.Fill({
                      color: 'rgba(255,0,0,0.1)'
                    })
                  })];
                }
                return selectStyleCache[text];
              }
            });

            var selectfeature;
            var displaySelectedFeatureInfo = function(pixel,displaywkt) {

                var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                    return feature;
                });

                var regionname = Ext.getCmp('regionname');
                var admin0name = Ext.getCmp('admin0name');
                var admin1name = Ext.getCmp('admin1name');
                var admin2name = Ext.getCmp('admin2name');
                var selectedregion = Ext.getCmp('selectedregionname');

                var wkt_polygon = Ext.getCmp('wkt_polygon');

                if (feature) {
                    regionname.setValue(feature.get(namefield));
                    if (adminlevel == 'admin0') {
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue('&nbsp;');
                        admin2name.setValue('&nbsp;');
                        selectedregion.setValue(feature.get('ADM0_NAME'));
                    }
                    else if (adminlevel == 'admin1') {
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue(feature.get('ADM1_NAME'));
                        admin2name.setValue('&nbsp;');
                        selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    }
                    else if (adminlevel == 'admin2') {
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue(feature.get('ADM1_NAME'));
                        admin2name.setValue(feature.get('ADM2_NAME'));
                        selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME') + ' - ' + feature.get('ADM2_NAME'));
                    }

                    if (displaywkt) {
                        var wkt = new ol.format.WKT();
                        var wktstr = wkt.writeFeature(feature);
                        // not a good idea in general, just for this demo
                        wktstr = wktstr.replace(/,/g, ', ');
                        wkt_polygon.setValue(wktstr);
                    }

                    Ext.getCmp('fieldset_selectedregion').show();

                } else {
                    regionname.setValue('&nbsp;');
                    admin0name.setValue('&nbsp;');
                    admin1name.setValue('&nbsp;');
                    admin2name.setValue('&nbsp;');
                    wkt_polygon.setValue('&nbsp;');
                    selectedregion.setValue('&nbsp;');
                    Ext.getCmp('fieldset_selectedregion').hide();
                }

                if (feature !== selectfeature) {
                    if (selectfeature) {
                        selectedFeatureOverlay.removeFeature(selectfeature);
                    }
                    if (feature) {
                        selectedFeatureOverlay.addFeature(feature);
                    }
                    selectfeature = feature;
                }

            };

            me.map.on('pointermove', function(evt) {
              if (evt.dragging) {
                return;
              }
              var pixel = me.map.getEventPixel(evt.originalEvent);
              displayFeatureInfo(pixel,false);
            });

            me.map.on('click', function(evt) {
                //var coordinate = evt.coordinate;
                //overlay.setPosition(coordinate);
                displaySelectedFeatureInfo(evt.pixel, true);
            });

        }
        else {
            vectorlayer_idx = me.getController().findlayer(me.map, menuitem.name);
            if (vectorlayer_idx != -1)
                me.map.getLayers().removeAt(vectorlayer_idx);
        }





        //me.mon(Ext.select('ol-viewport'), 'mousemove', function(evt){
        //    var pixel = me.map.getEventPixel(evt.originalEvent);
        //    displayFeatureInfo(pixel);
        //}, me);

        //(me.map.getViewport()).on('mousemove', function(evt) {
        //    var pixel = me.map.getEventPixel(evt.originalEvent);
        //    displayFeatureInfo(pixel);
        //});


        //var select = null;  // ref to currently selected interaction
        //
        //// select interaction working on "singleclick"
        //var selectSingleClick = new ol.interaction.Select();
        //
        //// select interaction working on "click"
        //var selectClick = new ol.interaction.Select({
        //  condition: ol.events.condition.click
        //});
        //
        //// select interaction working on "pointermove"
        //var selectPointerMove = new ol.interaction.Select({
        //  condition: ol.events.condition.pointerMove
        //});
        //
        //var value = 'click';
        ////if (select !== null) {
        ////    me.map.removeInteraction(select);
        ////}
        //if (value == 'singleclick') {
        //    select = selectSingleClick;
        //} else if (value == 'click') {
        //    select = selectClick;
        //    select.on('select', function(evt) {
        //        displayFeatureInfo(evt.pixel);
        //    });
        //} else if (value == 'pointermove') {
        //    select = selectPointerMove;
        //    select.on('select', function(evt) {
        //        if (evt.dragging) {
        //            return;
        //        }
        //        var pixel = me.map.getEventPixel(evt.originalEvent);
        //        displayFeatureInfo(pixel);
        //        //$('#status').html('&nbsp;' + e.target.getFeatures().getLength() +
        //        //    ' selected features (last operation selected ' + e.selected.length +
        //        //    ' and deselected ' + e.deselected.length + ' features)');
        //    });
        //} else {
        //    select = null;
        //}
        //if (select !== null) {
        //    me.map.addInteraction(select);
        //}

    }
});
