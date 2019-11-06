Ext.define('esapp.view.acquisition.product.editMapsetController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-product-editmapset'

    ,onSaveClick: function () {
        var me = this.getView(),
            form = this.lookupReference('mapsetform');

        // console.info(me.params.mapsetrecord);
        if (form.isValid()) {
            if (Ext.data.StoreManager.lookup('MapsetsStore').getUpdatedRecords() !== []){
                Ext.data.StoreManager.lookup('MapsetsStore').sync({
                    success: function () {
                        // console.log('success');
                        if (!me.params.edit) {
                            me.params.edit = true;
                            Ext.toast({html: esapp.Utils.getTranslation('mapsetcreated'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
                            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editmapset') + '</span>');
                        }
                        else {
                            Ext.toast({html: esapp.Utils.getTranslation('mapsetupdated'), title: esapp.Utils.getTranslation('saved'), width: 200, align: 't'});
                        }
                    },
                    failure: function () {
                        // console.log('failure');
                        if (!me.params.edit) {
                            Ext.toast({html: esapp.Utils.getTranslation('errorcreatingmapset'), title: esapp.Utils.getTranslation('error'), width: 200, align: 't'});
                        }
                        else {
                            Ext.toast({html: esapp.Utils.getTranslation('errorupdatingmapset'), title: esapp.Utils.getTranslation('error'), width: 200, align: 't'});
                        }
                    },
                    callback: function () {
                        // console.log('callback');
                    }
                });
            }
        }
    }


    ,drawBBOX: function(){
        var me = this.getView();
        var footprintimage = me.lookupReference('footprint_image');
        var footprint_image_fieldset = me.lookupReference('footprint_image_fieldset');

        var upper_left_long = me.lookupReference('upper_left_long').getValue();
        var upper_left_lat = me.lookupReference('upper_left_lat').getValue();
        var lower_right_long = me.lookupReference('lower_right_long').getValue();
        var lower_right_lat = me.lookupReference('lower_right_lat').getValue();
        var pixel_size = me.lookupReference('pixel_shift_long').getValue();
        var center_of_pixel = me.lookupReference('center_of_pixel').getValue();

        var image_width = Math.abs(Math.round((lower_right_long - upper_left_long)/pixel_size));
        var image_height = Math.abs(Math.round((upper_left_lat - lower_right_lat)/pixel_size));

        if (!(upper_left_long == -180 && lower_right_long == 180) && center_of_pixel){
            image_width += 1;
        }
        if (!(upper_left_lat == 80 && lower_right_lat == -60) && center_of_pixel){
            image_height += 1;
        }

        var bbox = [{
            "lng": upper_left_long,
            "lat": upper_left_lat
        },{
            "lng": lower_right_long,
            "lat": lower_right_lat
        }];

        // console.info(bbox);

        // A ring must be closed, that is its last coordinate should be the same as its first coordinate.
        var ring = [
            [bbox[0].lng, bbox[0].lat], [bbox[1].lng, bbox[0].lat],
            [bbox[1].lng, bbox[1].lat], [bbox[0].lng, bbox[1].lat],
            [bbox[0].lng, bbox[0].lat]
        ];

        if (upper_left_long != null && upper_left_lat != null && lower_right_long != null && lower_right_lat != null){
            // A polygon is an array of rings, the first ring is
            // the exterior ring, the others are the interior rings.
            var polygon = new ol.geom.Polygon([ring]);
            // polygon.transform('EPSG:4326', 'EPSG:3857');  //  display this polygon in a map with a view whose projection is Web Mercator (EPSG:3857)

            // Create feature with polygon.
            var feature = new ol.Feature(polygon);

            if (me.drawnFeature != null){
                // me.drawvectorlayer_source.removeFeature(me.drawnFeature);
                me.drawvectorlayer_source.clear();
                me.drawnFeature = null;
            }

            me.drawvectorlayer_source.addFeature(feature);
            me.drawnFeature = feature;

            me.lookupReference('pixel_size_x').setValue(image_width);
            me.lookupReference('pixel_size_y').setValue(image_height);

            if (upper_left_long < -42 || upper_left_lat > 48 || lower_right_long > 81 || lower_right_lat < -58){
                me.africacountryborders.setVisible(false);
                me.globalcountryborders.setVisible(true);
                me.overviewmapView.setCenter([0, 0]);
                me.overviewmapView.setZoom(0);
                me.mapView.setCenter([0, -5]);
                me.mapView.setZoom(4);
                footprintimage.setWidth(270);
                footprintimage.setHeight(135);
            }
            else {
                me.africacountryborders.setVisible(true);
                me.globalcountryborders.setVisible(false);
                me.overviewmapView.setCenter([20, -5]);
                me.overviewmapView.setZoom(1);
                me.mapView.setCenter([16.4, -0.5]);
                me.mapView.setZoom(10);
                footprintimage.setWidth(180);
                footprintimage.setHeight(155);
            }
            me.overviewMap.updateSize();
            me.map.updateSize();
        }
    }

    ,addDrawInteraction: function(geometrytype){
        var me = this.getView();
        var value = 'Box';  // Ext.getCmp('geometrytypes' + me.id).value;
        me.map.removeInteraction(me.draw);
        me.draw = null;
        me.map.updateSize();
        //var source = new ol.source.Vector({wrapX: false});
        //
        //var drawvectorlayer = new ol.layer.Vector({
        //    source: source,
        //    layer_id: 'drawvectorlayer',
        //    style: new ol.style.Style({
        //      fill: new ol.style.Fill({
        //        color: 'rgba(255, 255, 255, 0.2)'
        //      }),
        //      stroke: new ol.style.Stroke({
        //        color: '#ffcc33',
        //        width: 2
        //      }),
        //      image: new ol.style.Circle({
        //        radius: 7,
        //        fill: new ol.style.Fill({
        //          color: '#ffcc33'
        //        })
        //      })
        //    })
        //});
        //
        //var productlayer_idx = me.getController().findlayer(me.map, 'drawvectorlayer');
        //if (productlayer_idx != -1)
        //    me.map.getLayers().removeAt(productlayer_idx);
        //me.map.getLayers().insertAt(10, drawvectorlayer);

        if (value !== 'None') {
            var geometryFunction, maxPoints;
            if (value === 'Square') {
                value = 'Circle';
                geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
            } else if (value === 'Box') {
                value = 'LineString';
                maxPoints = 1;
                geometryFunction = function(coordinates, geometry) {
                    if (!geometry) {
                        geometry = new ol.geom.Polygon(null);
                    }
                    var start = coordinates[0];
                    var end = coordinates[1];
                    geometry.setCoordinates([
                        [start, [start[0], end[1]], end, [end[0], start[1]], start]
                    ]);
                    return geometry;
                };
            }
            me.draw = new ol.interaction.Draw({
                source: me.drawvectorlayer_source,
                type: /** @type {ol.geom.GeometryType} */ (value),
                geometryFunction: geometryFunction,
                maxPoints: maxPoints
            });
            me.map.addInteraction(me.draw);

            //var selectDrawfeatures = new ol.interaction.Select({
            //    wrapX: false,
            //    style: overlayStyle
            //});
            //this.map.addInteraction(selectDrawfeatures);

            //var modifyDrawfeatures = new ol.interaction.Modify({
            //    //features: this.drawfeatures,
            //    features: me.drawvectorlayer_source.getFeatures(),
            //    style: overlayStyle,
            //    // the SHIFT key must be pressed to delete vertices, so
            //    // that new vertices can be drawn at the same position
            //    // of existing vertices
            //    deleteCondition: function(event) {
            //      return ol.events.condition.shiftKeyOnly(event) &&
            //          ol.events.condition.singleClick(event);
            //    }
            //});
            //me.map.addInteraction(modifyDrawfeatures);
        }
    }


    ,saveFootprintImage: function() {
        var me = this.getView(),
            // filename = me.params.mapsetcode,
            // footprintimage_url = '',
            footprintimage_base64 = ''
        ;

        // if (filename == null || filename.trim() == '')
        //     filename = 'eStation2_mapset.png'
        // else {
        //     filename = filename.replace(/<\/?[^>]+(>|$)/g, "");
        //     filename = filename + '.png';
        // }

        var taskSaveFootprintImage = new Ext.util.DelayedTask(function() {
            me.overviewMap.once('postcompose', function(event) {
                var canvas = event.context.canvas,
                    context = canvas.getContext('2d', { alpha: false });

                context.fillStyle = "rgba(255, 255, 255, 1)";
                context.strokeStyle = "#000000";
                context.strokeRect(0, 0, canvas.width, canvas.height);
                // // works with images
                context.globalAlpha = 1;
                // footprintimage_url = canvas.toDataURL('image/png');
                footprintimage_base64 = canvas.toDataURL();
                // console.log(footprintimage_base64);
            });
            me.overviewMap.renderSync();

            me.params.mapsetrecord.set('footprint_image', footprintimage_base64);
            // me.footprint_image = footprintimage_base64;
            // me.lookupReference('footprint_image').src = footprintimage_base64;

            // if (Ext.fly('downloadlink')) {
            //     Ext.fly('downloadlink').destroy();
            // }
            // var downloadlink = document.createElement('a');
            // downloadlink.id = 'downloadlink';
            // downloadlink.name = downloadlink.id;
            // downloadlink.className = 'x-hidden';
            // document.body.appendChild(downloadlink);
            // downloadlink.setAttribute('download', filename);
            // downloadlink.setAttribute('href', footprintimage_url);
            // downloadlink.click();
            //
            // footprintimage_url = null;
            footprintimage_base64 = null;
        });
        taskSaveFootprintImage.delay(1000);
    }

    // ,toggleDrawGeometry: function(btn, event) {
    //     var me = this.getView();    // btn.up().up();
    //
    //     if (btn.pressed) {
    //         me.map.removeInteraction(me.draw);
    //         me.getController().addDrawInteraction();
    //         btn.setIconCls('polygon');
    //         // btn.showMenu();
    //     }
    //     else {
    //         me.map.removeInteraction(me.draw);
    //         btn.setIconCls('polygon-gray');
    //         btn.hideMenu();
    //     }
    // }
    //
    // ,findHighlightLayer: function (map, layer_id, highlight){
    //     var highlightlayer = null,
    //         layerNamePrefix = 'selectedfeatureOverlay_';
    //     if (highlight){
    //         layerNamePrefix = 'highlightfeatureOverlay_';
    //     }
    //     // else debugger;
    //     map.getLayers().getArray().forEach(function (layer,idx){
    //         var this_layer_id = layer.get("layer_id");
    //         // console.info(this_layer_id + ' idx: ' + idx);
    //         if(this_layer_id == layerNamePrefix + layer_id){
    //           highlightlayer = layer;
    //         }
    //     });
    //     return highlightlayer;
    // }
    //
    // ,displayFeatureInfo: function(pixel) {
    //     var me = this.getView();
    //     var toplayeridx = 10;
    //     var topfeature;
    //     var toplayer_id = '';
    //
    //     me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
    //         if (layer != null){
    //             // console.info(layer.get("layerorderidx"));
    //             var this_layer_idx = layer.get("layerorderidx");
    //             if (this_layer_idx != 100 && layer.getVisible()  && this_layer_idx < toplayeridx) {
    //                 toplayeridx = this_layer_idx;
    //                 me.toplayer = layer;
    //                 topfeature = feature;
    //                 toplayer_id = layer.get("layer_id");
    //             }
    //         }
    //     });
    //
    //     // console.info(topfeature);
    //     // console.info(toplayer_id);
    //     var featureOverlay = me.getController().findHighlightLayer(me.map, toplayer_id, true);
    //     if (esapp.Utils.objectExists(topfeature)) {
    //         if (topfeature !== me.highlight) {
    //             if (featureOverlay != null){
    //                 if (esapp.Utils.objectExists(me.featureOverlay)) {
    //                     me.featureOverlay.getSource().clear();
    //                 }
    //                 featureOverlay.getSource().clear();
    //                 featureOverlay.getSource().addFeature(topfeature);
    //                 me.featureOverlay = featureOverlay;
    //             }
    //             me.highlight = topfeature;
    //         }
    //     } else {
    //         if (esapp.Utils.objectExists(me.featureOverlay)) {
    //             me.featureOverlay.getSource().clear();
    //         }
    //         me.highlight = null;
    //     }
    //
    //     //var featureTooltip = Ext.create('Ext.tip.ToolTip', {
    //     //    //target: Ext.getCmp(me.id), // feature,
    //     //    alwaysOnTop: true,
    //     //    anchor: 'right',
    //     //    trackMouse: true,
    //     //    html: 'Tracking while you move the mouse'
    //     //});
    //     //featureTooltip.setTarget(feature);
    //     ///** Create an overlay to anchor the popup to the map. */
    //     //var overlay = new ol.Overlay({
    //     //  element: featureTooltip.getEl()  // undefined!!!!!!
    //     //});
    //     //
    //     ////me.map.overlays.push(overlay);
    //     //me.map.addOverlay(overlay);
    //     //overlay.setPosition(pixel);
    // }
});
