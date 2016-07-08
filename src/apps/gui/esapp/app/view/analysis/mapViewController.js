Ext.define('esapp.view.analysis.mapViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-mapview'

    ,addProductLayer: function(productcode, productversion, mapsetcode, subproductcode, legendid, colorschemeHTML, legendHTML, legendHTMLVertical, productname) {
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
        me.getView().legendHTML = legendHTML;
        me.getView().legendHTMLVertical = legendHTMLVertical;


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
                                    me.getView().productdate = this.date;
                                    me.getView().getController().updateProductLayer();
                                    //var outmask = me.lookupReference('outmaskbtn_'+ me.getView().id.replace(/-/g,'_')).pressed;
                                    //if (outmask){
                                    //    me.getView().getController().outmaskFeature();
                                    //}

                                    //me.getView().getController().updateProductLayer(productcode,
                                    //    productversion,
                                    //    mapsetcode,
                                    //    subproductcode,
                                    //    legendid,
                                    //    this.date);
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
                //me.getView().productdate = me.getView().productdate.replace(pattern,'$3-$2-$1');
                //var dt = new Date(me.getView().productdate.replace(pattern,'$3-$2-$1'));
                var productdateHTML = ' - <b class="smalltext">' + me.getView().productdate.replace(pattern,'$3-$2-$1') + '</b>';
                var mapviewTitle = productname + versiontitle + mapsetcodeHTML + productdateHTML;
                me.getView().setTitle(mapviewTitle);

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

        me.getView().productlayer = new ol.layer.Tile({       // Image
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            layertype: 'raster',
            type: 'base',
            visible: true,
            source: new ol.source.TileWMS({    // ImageWMS
                url: 'analysis/getproductlayer',
                type: 'base',
                wrapX: false,
                noWrap: true,
                crossOrigin: '', // 'anonymous',
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

        // Show legend panel with selected legend and show view legend toggle button.
        var maplegendhtml = me.lookupReference('product-legend' + me.getView().id);
        maplegendhtml.setHtml(legendHTMLVertical);

        var maplegendpanel = me.lookupReference('product-legend_panel_' + me.getView().id);
        maplegendpanel.show();

        var maplegend_togglebtn = me.lookupReference('legendbtn_'+ me.getView().id.replace(/-/g,'_')); //  + me.getView().id);
        maplegend_togglebtn.show();
        maplegend_togglebtn.toggle();

        var outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.getView().id.replace(/-/g,'_')); //  + me.getView().id);
        if (me.getView().getController().outmaskingPossible(me.getView().map)){
            outmask_togglebtn.show();
        }
        else outmask_togglebtn.hide();
    }

    ,updateProductLayer: function() {
        var params = {};
        var outmask = false; // this.lookupReference('outmaskbtn_'+ this.getView().id.replace(/-/g,'_')).pressed;
        //console.info(this.lookupReference('outmaskbtn_'+ this.getView().id.replace(/-/g,'_')));
        //console.info(outmask);
        //console.info(this.getView().selectedfeature);

        // Does not work passing the WKT. Gives error: 414 Request-URI Too Long
        // The requested URL's length exceeds the capacity limit for this server.
        if (outmask && this.getView().selectedfeature){
            var wkt = new ol.format.WKT();
            var wktstr = wkt.writeFeature(this.getView().selectedfeature);
            wktstr = wktstr.replace(/,/g, ', ');  // not a good idea in general
            params = {
                productcode: this.getView().productcode,
                productversion: this.getView().productversion,
                subproductcode: this.getView().subproductcode,
                mapsetcode: this.getView().mapsetcode,
                legendid: this.getView().legendid,
                date: this.getView().productdate,
                outmask:true,
                selectedfeature: wktstr,
                'FORMAT': 'image/png'
            };
        }
        else {
            params = {
                productcode: this.getView().productcode,
                productversion: this.getView().productversion,
                subproductcode: this.getView().subproductcode,
                mapsetcode: this.getView().mapsetcode,
                legendid: this.getView().legendid,
                date: this.getView().productdate,
                'FORMAT': 'image/png'
                //,REASPECT:'TRUE'
            };
        }

        //function geoserverWms(method, url, params) {
        //    var options = {
        //      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        //      params: params,
        //      responseType: 'buffer'
        //    }
        //    var result = HTTP.call(method, url, options);
        //    console.log('Content:', result.content);
        //    return result.content.toString('base64');
        //}

        function imagePostFunction(image, src) {
            var img = image.getImage();
            if (typeof window.btoa === 'function') {
              var xhr = new XMLHttpRequest();
              //console.log("src",src);
              //GET ALL THE PARAMETERS OUT OF THE SOURCE URL
              var dataEntries = src.split("&");
              var url;
              var params = "";
              for (var i = 0 ; i< dataEntries.length ; i++){
                  //console.log("dataEntries[i]",dataEntries[i]);
                  if (i===0){
                  url = dataEntries[i];
                  }
                  else{
                  params = params + "&"+dataEntries[i];
                  }
              }
              //console.log("params",params);
              xhr.open('POST', url, true);

              xhr.responseType = 'arraybuffer';
              xhr.onload = function(e) {
                if (this.status === 200) {
                  //console.log("this.response",this.response);
                  var uInt8Array = new Uint8Array(this.response);
                  var i = uInt8Array.length;
                  var binaryString = new Array(i);
                  while (i--) {
                    binaryString[i] = String.fromCharCode(uInt8Array[i]);
                  }
                  var data = binaryString.join('');
                  var type = xhr.getResponseHeader('content-type');
                  if (type.indexOf('image') === 0) {
                    img.src = 'data:' + type + ';base64,' + window.btoa(data);
                  }
                }
              };
              //SET THE PROPER HEADERS AND FINALLY SEND THE PARAMETERS
              xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
              //xhr.setRequestHeader("Content-length", params.length);
              //xhr.setRequestHeader("Connection", "close");
              xhr.send(params);
            } else {
              img.src = src;
            }
        }

        this.getView().productlayer = new ol.layer.Tile({
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            layertype: 'raster',
            type: 'base',
            visible: true,
            //maxGetUrlProperty: 10,
            source: new ol.source.TileWMS({
                url: 'analysis/getproductlayer',
                crossOrigin: '',  // 'anonymous',
                attributions: [new ol.Attribution({
                    html: '&copy; <a href="https://ec.europa.eu/jrc/">'+esapp.Utils.getTranslation('estation2')+'</a>'
                })],
                params: params,
                serverType: 'mapserver' /** @type {ol.source.wms.ServerType}  ('mapserver') */
                //,tileLoadFunction: function(image, src) {
                //   imagePostFunction(image, src);
                //}
                //,tileLoadFunction: function (image, src) {
                //    var img = image.getImage();
                //    var query = src.replace(url + '?', '');
                //    var params = getQueryParams(query); // A separate function to decode the query string into a JSON object.
                //    if (typeof window.btoa === 'function') {
                //        Meteor.call('geoserverWms', 'POST', url, params, function(err, result) {
                //            if (err) {
                //                return console.error('err:', err);
                //            }
                //            // console.log(result);
                //            var type = 'image/png';
                //            img.src = 'data:' + type + ';base64,' + result;
                //        });
                //    } else {
                //      img.src = src;
                //    }
                //}
            })
        });


        var productlayer_idx = this.getView().getController().findlayer(this.getView().map, 'productlayer');
        if (productlayer_idx != -1)
            this.getView().map.getLayers().removeAt(productlayer_idx);
        //this.getView().map.removeLayer(this.getView().map.getLayers().a[0]);
        //this.getView().map.addLayer(this.getView().productlayer);
        this.getView().map.getLayers().insertAt(0, this.getView().productlayer);

        var versiontitle = '';
        if (this.getView().productversion !== 'undefined'){
            versiontitle = ' <b class="smalltext">' + this.getView().productversion + '</b>';
        }

        var mapsetcodeHTML = ' - <b class="smalltext">' + this.getView().mapsetcode + '</b>';

        var pattern = /(\d{4})(\d{2})(\d{2})/;
        //this.getView().productdate = clickeddate.replace(pattern,'$3-$2-$1');
        var productdateHTML = ' - <b class="smalltext">' + this.getView().productdate.replace(pattern,'$3-$2-$1') + '</b>';

        //var mapviewTitle = this.getView().productname + versiontitle + ' - <b class="smalltext">' + this.getView().productdate + '</b>';
        var mapviewTitle = this.getView().productname + versiontitle + mapsetcodeHTML + productdateHTML;

        this.getView().setTitle(mapviewTitle);

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

    ,saveMap: function(btn, event) {
        var me = this.getView();
        var filename = me.getTitle();
        var mapviewwin = btn.up().up();
        //var mapimage_url = '';
        var addlegend = false;

        if (filename == null || filename.trim() == '')
            filename = 'estation2map.png'
        else {
            filename = filename.replace(/<\/?[^>]+(>|$)/g, "");
            filename = filename + '.png';
        }

        //if(typeof Promise !== "undefined" && Promise.toString().indexOf("[native code]") !== -1){
        //   console.info('Browser supports Promise natively!');
        //}
        //else {
        //   console.info('NOT SUPPORT OF Promise natively!');
        //}


        //var maplegendhtml = mapviewwin.lookupReference('product-legend' + mapviewwin.id);
        var maplegendpanel = mapviewwin.lookupReference('product-legend_panel_' + mapviewwin.id);
        if (maplegendpanel.hidden == false) {
            var maplegendhtml = document.getElementById('product-legend' + mapviewwin.id);
            //console.info('<div>'+mapviewwin.legendHTML+'</div>');
            html2canvas(maplegendhtml, {
                onrendered: function(canvas) {
                    addlegend = true;
                    //maplegendimage = canvas.toDataURL("image/png");
                    maplegendpanel.legendHTML_ImageObj.src = canvas.toDataURL("image/png");
                    createDownloadMapImage(addlegend);

                    //var image = canvas.toDataURL("image/png");
                    //filename = 'legend_' + filename;
                    ////console.info(mapleggendimage_url);
                    //
                    //if (Ext.fly('downloadlegendlink')) {
                    //    Ext.fly('downloadlegendlink').destroy();
                    //}
                    //var downloadlegendlink = document.createElement('a');
                    //downloadlegendlink.id = 'downloadlegendlink';
                    //downloadlegendlink.name = downloadlegendlink.id;
                    //downloadlegendlink.className = 'x-hidden';
                    //document.body.appendChild(downloadlegendlink);
                    //downloadlegendlink.setAttribute('download', filename);
                    //downloadlegendlink.setAttribute('href', image);
                    //downloadlegendlink.click();
                }
            });

            //domtoimage.toPng(maplegendhtml)
            //    .then(function (mapleggendimage_url) {
            //
            //        filename = 'legend_' + filename;
            //        //console.info(mapleggendimage_url);
            //
            //        if (Ext.fly('downloadlegendlink')) {
            //            Ext.fly('downloadlegendlink').destroy();
            //        }
            //        var downloadlegendlink = document.createElement('a');
            //        downloadlegendlink.id = 'downloadlegendlink';
            //        downloadlegendlink.name = downloadlegendlink.id;
            //        downloadlegendlink.className = 'x-hidden';
            //        document.body.appendChild(downloadlegendlink);
            //        downloadlegendlink.setAttribute('download', filename);
            //        downloadlegendlink.setAttribute('href', mapleggendimage_url);
            //        downloadlegendlink.click();
            //    })
            //    .catch(function (error) {
            //        console.error('oops, something went wrong!', error);
            //    });
        }
        else {
            createDownloadMapImage(addlegend);
        }

        function createDownloadMapImage(addlegend){
            var mapimage_url = '';

            mapviewwin.map.once('postcompose', function(event) {
                var canvas = event.context.canvas;
                //console.info(addlegend);
                if (addlegend) {
                    //console.info(maplegendpanel.legendHTML_ImageObj);
                    var legendposition = maplegendpanel.getPosition(true);
                    var context = canvas.getContext('2d');
                    context.drawImage(maplegendpanel.legendHTML_ImageObj, legendposition[0], legendposition[1]+15);
                }
                //console.info(Ext.fly('ol-scale-line-inner'));
                //
                //var scalewidth = parseInt(Ext.fly('ol-scale-line-inner').css('width'));
                //var scalenumber = Ext.fly('ol-scale-line-inner').text();
                //var ctx = event.context;
                //ctx.beginPath();
                //
                ////Scale Text
                //ctx.lineWidth=1;
                //ctx.font = "20px Arial";
                //ctx.strokeText(scalenumber,10,canvas.height-25);
                //
                ////Scale Dimensions
                //ctx.lineWidth=5;
                //ctx.moveTo(10,canvas.height-20);
                //ctx.lineTo(parseInt(scalewidth)+10,canvas.height-20);
                //ctx.stroke();

                mapimage_url = canvas.toDataURL('image/png');
            });

            mapviewwin.map.renderSync();
            if (Ext.fly('downloadlink')) {
                Ext.fly('downloadlink').destroy();
            }
            var downloadlink = document.createElement('a');
            downloadlink.id = 'downloadlink';
            downloadlink.name = downloadlink.id;
            downloadlink.className = 'x-hidden';
            document.body.appendChild(downloadlink);
            downloadlink.setAttribute('download', filename);
            downloadlink.setAttribute('href', mapimage_url);
            downloadlink.click();
            //downloadlink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        }

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

    ,toggleLegend: function(btn, event) {
        var mapviewwin = btn.up().up();
        var maplegendpanel = mapviewwin.lookupReference('product-legend_panel_' + mapviewwin.id);
        var maplegendhtml = mapviewwin.lookupReference('product-legend' + mapviewwin.id);

        if (btn.pressed) {
            //console.info(mapviewwin.legendHTMLVertical);
            maplegendhtml.setHtml(mapviewwin.legendHTMLVertical);
            //maplegendpanel.doConstrain();
            maplegendpanel.show();
        }
        else {
            maplegendhtml.setHtml(mapviewwin.legendHTML);
            //maplegendpanel.doConstrain();
            maplegendpanel.show();
            //maplegendpanel.hide();
        }
    }

    ,toggleOutmask: function(btn, event) {
        var mapviewwin = btn.up().up();

        if (btn.pressed) {
            if (Ext.isDefined(mapviewwin.selectedfeature)){
                mapviewwin.getController().outmaskFeature();
//                mapviewwin.getController().updateProductLayer();
            }
        }
        else {
            //mapviewwin.map.removeLayer("Outmask");
            mapviewwin.getController().removeOutmaskLayer();
            mapviewwin.getController().updateProductLayer();
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

    ,outmaskingPossible: function (map){
        var possible = false,
            productlayerexists = false,
            vectorlayerexists = false;

        map.getLayers().getArray().forEach(function (layer,idx){
            var layer_type = layer.get("layertype")
            if(layer_type == 'raster'){
              productlayerexists = true;
            }
            else if(layer_type == 'vector'){
              vectorlayerexists = true;
            }
        });
        if (productlayerexists && vectorlayerexists)
            possible = true;

        return possible;
    }

    ,removeOutmaskLayer: function (){
        var me = this;
        me.getView().map.getLayers().getArray().forEach(function (layer,idx){
            var layer_name = layer.get("name")
            if(layer_name == 'Outmask'){
                me.getView().map.removeLayer(layer);
            }
        });
    }

    ,outmaskFeature: function(){
        var me = this;

        function isFunction(possibleFunction) {
          return typeof(possibleFunction) === typeof(Function);
        }

        if ( Ext.isDefined(me.getView().selectedfeature) && me.getView().selectedfeature !== null){
            var selectedFeatureToOutmask = me.getView().selectedfeature;
            var linearRing = null;

            //me.getView().map.removeLayer("Outmask");
            me.getView().getController().removeOutmaskLayer();

            var vecSource = new ol.source.Vector({});
            var outmaskStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'rgba(255, 255, 255, 0.95)',
                    width: 2
                }),
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.95)'
                })
            });

            var vectorLayer = new ol.layer.Vector({
                    name: "Outmask",
                    source: vecSource,
                    style: outmaskStyle
                });

            //me.getView().map.removeLayer(vectorLayer);

            //var extentEGAD = [20.99, -6.00, 52.00, 24.00];
            var extentAfrica = [-27,-36,61,39];
            var outmaskPolygon = ol.geom.Polygon.fromExtent(extentAfrica);

            if (isFunction(selectedFeatureToOutmask.getGeometry().getPolygons)){
                selectedFeatureToOutmask.getGeometry().getPolygons().forEach(function (polygon, idx) {
                    linearRing = new ol.geom.LinearRing(polygon.getCoordinates()[0]);
                    outmaskPolygon.appendLinearRing(linearRing);	//add the linear rings to the inversePolygon defined above
                });
            }
            else { //if (geom instanceof ol.geom.Polygon){ // if polygon then no need to loop add the single linear ring to inversepolygon
                //console.info('single polygon');
                linearRing = new ol.geom.LinearRing(selectedFeatureToOutmask.getGeometry().getCoordinates()[0]);
                outmaskPolygon.appendLinearRing(linearRing);	//add the linear rings to the inversePolygon defined above
            }

            vectorLayer.getSource().addFeature(new ol.Feature(outmaskPolygon));

            me.getView().map.addLayer(vectorLayer);

        }
    }

    ,outmaskFeatureThroughVectorContext: function(){    // NOT WORKING for Multipolygons!!!
        var me = this;

        function isFunction(possibleFunction) {
          return typeof(possibleFunction) === typeof(Function);
        }

        //if (me.getView().selectedfeature != null && isFunction(me.getView().selectedfeature.getGeometry) && isFunction(me.getView().selectedfeature.getGeometry().getPolygons))
        //    console.info(me.getView().selectedfeature.getGeometry().getPolygons());
        //else {
        //    console.info(me.getView().selectedfeature.getGeometry());
        //}

        //// get the pixel position with every move
        //var mousePosition = null;
        //var mapcontainer = me.getView().map;
        //mapcontainer.on('pointermove', function(evt) {
        //  mousePosition = me.getView().map.getEventPixel(evt.originalEvent);
        //  me.getView().map.render();
        //});
        //mapcontainer.on('mouseout', function() {
        //  mousePosition = null;
        //  me.getView().map.render();
        //});
        //
        //// before rendering the layer, do the clipping of a circle around the mouspointer
        //me.getView().productlayer.on('precompose', function(event) {
        //  var ctx = event.context;
        //  var radius = 75;
        //  var pixelRatio = event.frameState.pixelRatio;
        //  ctx.save();
        //  ctx.beginPath();
        //  if (mousePosition) {
        //    // only show a circle around the mouse
        //    ctx.arc(mousePosition[0] * pixelRatio, mousePosition[1] * pixelRatio,
        //        radius * pixelRatio, 0, 2 * Math.PI);
        //    ctx.lineWidth = 5 * pixelRatio;
        //    ctx.strokeStyle = 'rgba(0,0,0,0.5)';
        //    ctx.stroke();
        //  }
        //  ctx.clip();
        //});
        //
        //// after rendering the layer, restore the canvas context
        //me.getView().productlayer.on('postcompose', function(event) {
        //  var ctx = event.context;
        //  ctx.restore();
        //});
        //console.info(me.getView().selectedfeature);
        if ( Ext.isDefined(me.getView().selectedfeature) && me.getView().selectedfeature !== null){
            // A style for the geometry.
            var fillStyle = new ol.style.Fill({color: [0, 0, 0, 0]});

            // before rendering the layer, do the feature clipping  ( http://bl.ocks.org/elemoine/b95420de2db3707f2e89 )
            me.getView().productlayer.on('precompose', function(event) {
                var ctx = event.context;
                var vecCtx = event.vectorContext;

                ctx.save();
                //ctx.beginPath();
                if (isFunction(me.getView().selectedfeature.getGeometry) && isFunction(me.getView().selectedfeature.getGeometry().getPolygons)) {
                    // Using a style is a hack to workaround a limitation in OpenLayers 3,
                    // where a geometry will not be draw if no style has been provided.
                    vecCtx.setFillStrokeStyle(fillStyle, null);
                    //var multipoligon = new ol.geom.MultiPolygon(me.getView().selectedfeature.getGeometry().getPolygons(), 'XY');
                    //vecCtx.drawMultiPolygonGeometry(me.getView().selectedfeature.getGeometry());  // , me.getView().selectedfeature
                    me.getView().selectedfeature.getGeometry().getPolygons().forEach(function (polygon, idx) {
                        vecCtx.drawPolygonGeometry(polygon);
                        ctx.clip();
                    });
                }
                else if (isFunction(me.getView().selectedfeature.getGeometry)){
                    vecCtx.drawPolygonGeometry(me.getView().selectedfeature.getGeometry());
                    ctx.clip();
                }
                else {
                    vecCtx.drawFeature(me.getView().selectedfeature, fillStyle);
                    ctx.clip();
                }

            });

            // after rendering the layer, restore the canvas context
            me.getView().productlayer.on('postcompose', function(event) {
              var ctx = event.context;
              ctx.restore();
            });

            me.getView().map.render();
        }
        //console.info(me.getView().productlayer.getExtent());
        //var extent = [-43.576171875,-22.978515625,52.576171875,62.978515625];
        //var projection = new ol.proj.Projection({
        //  code: 'xkcd-image',
        //  units: 'pixels',
        //  extent: extent
        //});
        //var blanklayer = new ol.layer.Image({
        //    title: 'blanklayer',
        //    layer_id: 'blanklayer',
        //    layerorderidx: 1,
        //    layertype: 'raster',
        //    visible: true,
        //    source: new ol.source.ImageStatic({
        //        url: 'resources/img/Africa_icon.png',
        //        projection: projection,
        //        imageExtent: extent
        //    })
        //});   // {isBaseLayer: false, displayInLayerSwitcher: true}
        //
        //me.getView().map.getLayers().insertAt(1, blanklayer);
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

    ,addVectorLayer: function(menuitem, hidemenu){
        var me = this.getView();
        hidemenu = typeof hidemenu !== 'undefined' ? hidemenu : true;

        if (hidemenu) {
            Ext.ComponentQuery.query('button[name=vbtn-' + this.getView().id + ']')[0].hideMenu();
        }

        if (menuitem.checked) {
            this.addVectorLayerToMapView(menuitem.layerrecord);
        }
        else {
            vectorlayer_idx = me.getController().findlayer(me.map, menuitem.name);
            if (vectorlayer_idx != -1)
                me.map.getLayers().removeAt(vectorlayer_idx);

            if (me.getController().outmaskingPossible(me.map)){
                outmask_togglebtn.show();
            }
            else outmask_togglebtn.hide();
        }
    }

    ,addVectorLayerToMapView: function(layerrecord){
        var me = this.getView();
        var namefield = '',
            vectorlayer_idx = -1,
            //layerrecord = layerrec,
            layertitle = esapp.Utils.getTranslation(layerrecord.get('layername')) + '</BR><b class="smalltext" style="color:darkgrey">' + esapp.Utils.getTranslation(layerrecord.get('provider')) +'</b>'

            //geojsonfile = layerrecord.get('filename'),
            //feature_display_column = layerrecord.get('feature_display_column'),
            //adminlevel = layerrecord.get('layerlevel'),
            //polygon_outlinewidth = layerrecord.get('polygon_outlinewidth'),   // 1,
            //polygon_outlinecolor = layerrecord.get('polygon_outlinecolor'),
            //feature_highlight_outlinecolor = layerrecord.get('feature_highlight_outlinecolor'),
            //feature_highlight_outlinewidth = layerrecord.get('feature_highlight_outlinewidth'),
            //feature_highlight_fillcolor    = layerrecord.get('feature_highlight_fillcolor'),
            //feature_highlight_fillopacity  = layerrecord.get('feature_highlight_fillopacity'),
            //feature_selected_outlinecolor  = layerrecord.get('feature_selected_outlinecolor'),
            //feature_selected_outlinewidth  = layerrecord.get('feature_selected_outlinewidth'),

            outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')); //  + me.getView().id);

        namefield = layerrecord.get('feature_display_column').split(',')[0];

        var fillopacity = (layerrecord.get('feature_highlight_fillopacity')/100).toString().replace(",", ".");
        var highlight_fillcolor_opacity = 'rgba(' + esapp.Utils.HexToRGB(layerrecord.get('feature_highlight_fillcolor')) + ',' + fillopacity + ')'
        var highlightStyleCache = {};
        var collectionFO = new ol.Collection();
        me.featureOverlay = new ol.layer.Vector({      //new ol.FeatureOverlay({
                name: 'highlightfeatureOverlay_'+layerrecord.get('layername'),
                source: new ol.source.Vector({
                  features: collectionFO,
                  useSpatialIndex: false // optional, might improve performance
                }),
                updateWhileAnimating: true, // optional, for instant visual feedback
                updateWhileInteracting: true, // optional, for instant visual feedback

                map: me.map,
                style: function(feature, resolution) {
                    var text = resolution < 5000 ? feature.get(namefield) : '';
                    if (!highlightStyleCache[text]) {
                      highlightStyleCache[text] = [new ol.style.Style({
                          stroke: new ol.style.Stroke({
                              color: layerrecord.get('feature_highlight_outlinecolor'),    // '#319FD3',
                              width: layerrecord.get('feature_highlight_outlinewidth')
                          })
                          ,fill: new ol.style.Fill({
                            color: highlight_fillcolor_opacity    // 'rgba(49,159,211,0.1)'
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

        me.highlight = null;
        me.toplayer = null;
        var displayFeatureInfo = function(pixel) {

            //var toplayer = null;
            //var topfeature = null;
            //var ignorefeature = true;
            var toplayerindex = 6;
            //me.map.getLayers().getArray().forEach(function (layer, idx) {
            //    var this_layer_id = layer.get("layerorderidx")
            //    if (this_layer_id != 0 && layer.getVisible() && this_layer_id <= toplayerindex) {
            //        toplayerindex = idx;
            //    }
            //});
            //toplayer = me.map.getLayers().item(toplayerindex);

            //var topfeaturefound = false;
            var topFeatureLayerIdx = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                if (layer != null){
                    var this_layer_idx = layer.get("layerorderidx");
                    if (this_layer_idx != 0 && layer.getVisible() && this_layer_idx <= toplayerindex) {
                        toplayerindex = this_layer_idx;
                    }
                }
            });

            var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                if (layer != null){
                    var this_layer_idx = layer.get("layerorderidx");
                    if (this_layer_idx != 0 && layer.getVisible() && this_layer_idx == toplayerindex) {
                        me.toplayer = layer;
                        return feature;
                    }
                }
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

            if (esapp.Utils.objectExists(feature)) {

                //if (Ext.isDefined(feature.get('ADM2_NAME'))){
                //    regionname.setHtml(feature.get('ADM0_NAME') + ' - ' +
                //                       feature.get('ADM1_NAME') + ' - ' +
                //                       feature.get('ADM2_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('ADM1_NAME'))){
                //    regionname.setHtml(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('ADM0_NAME'))) {
                //    regionname.setHtml(feature.get('ADM0_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('AREANAME'))){
                //    regionname.setHtml(feature.get('COUNTRY') + ' - ' + feature.get('AREANAME') + ' (' + feature.get('DESIGNATE') + ')');
                //}
                //else if (Ext.isDefined(feature.get('F_LEVEL'))){
                //    regionname.setHtml(feature.get('F_LEVEL') + ' - ' + feature.get('F_CODE') + ' (' + feature.get('OCEAN') + ')');
                //}
                //else if (Ext.isDefined(feature.get('MarRegion'))){
                //    regionname.setHtml(feature.get('MarRegion'));
                //}
                //else {
                    var feature_columns = me.toplayer.get('feature_display_column').split(',');
                    var regionname_html = '';
                    for (var i = 0; i < feature_columns.length; i++) {
                        regionname_html += feature.get(feature_columns[i].trim());
                        if (i != feature_columns.length-1){
                            regionname_html += ' - ';
                        }
                    }
                    regionname.setHtml(regionname_html);
                //}

                //featureTooltip.html = feature.getId() + ': ' + feature.get(namefield);
            } else {
                regionname.setHtml('&nbsp;');
                //featureTooltip.html = '&nbsp;';
            }

            if (me.featureOverlay.getSource().getFeatures() == [] && esapp.Utils.objectExists(feature)) {
                me.featureOverlay.getSource().addFeature(feature);
            }
            if (feature !== me.highlight) {
                if (esapp.Utils.objectExists(me.highlight)) {
                    me.featureOverlay.getSource().removeFeature(me.highlight);
                }
                if (esapp.Utils.objectExists(feature)) {
                    me.featureOverlay.getSource().addFeature(feature);
                }
                me.highlight = feature;
            }
        };


        selectStyleCache = {};
        var collectionSFO = new ol.Collection();
        var selectedFeatureOverlay = new ol.layer.Vector({      //new ol.FeatureOverlay({
          name: 'selectedfeatureOverlay_'+layerrecord.get('layername'),
          source: new ol.source.Vector({
              features: collectionSFO,
              useSpatialIndex: false // optional, might improve performance
          }),
          updateWhileAnimating: true, // optional, for instant visual feedback
          updateWhileInteracting: true, // optional, for instant visual feedback

          map: me.map,
          style: function(feature, resolution) {
            var text = resolution < 5000 ? feature.get(namefield) : '';
            if (!selectStyleCache[text]) {
              selectStyleCache[text] = [new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: layerrecord.get('feature_selected_outlinecolor'),   // '#f00',
                  width: layerrecord.get('feature_selected_outlinewidth')
                })
                ,fill: new ol.style.Fill({
                  color:  'Transparent' // 'rgba(255,0,0,0.1)'
                })
              })];
            }
            return selectStyleCache[text];
          }
        });

        var selectfeature = null;
        var displaySelectedFeatureInfo = function(pixel,displaywkt) {

            //var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            //    return feature;
            //});
            var feature = me.highlight;

            //var regionname = Ext.getCmp('regionname');
            //var admin0name = Ext.getCmp('admin0name');
            //var admin1name = Ext.getCmp('admin1name');
            //var admin2name = Ext.getCmp('admin2name');
            var selectedregion = Ext.getCmp('selectedregionname');

            var wkt_polygon = Ext.getCmp('wkt_polygon');

            if (Ext.isDefined(feature)) {
                //regionname.setValue(feature.get(namefield));

                //if (Ext.isDefined(feature.get('ADM2_NAME'))){
                //    admin0name.setValue(feature.get('ADM0_NAME'));
                //    admin1name.setValue(feature.get('ADM1_NAME'));
                //    admin2name.setValue(feature.get('ADM2_NAME'));
                //    selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME') + ' - ' + feature.get('ADM2_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('ADM1_NAME'))){
                //    admin0name.setValue(feature.get('ADM0_NAME'));
                //    admin1name.setValue(feature.get('ADM1_NAME'));
                //    admin2name.setValue('&nbsp;');
                //    selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('ADM0_NAME'))){
                //    admin0name.setValue(feature.get('ADM0_NAME'));
                //    admin1name.setValue('&nbsp;');
                //    admin2name.setValue('&nbsp;');
                //    selectedregion.setValue(feature.get('ADM0_NAME'));
                //}
                //else if (Ext.isDefined(feature.get('AREANAME'))){
                //    selectedregion.setValue(feature.get('COUNTRY') + ' - ' + feature.get('AREANAME') + ' (' + feature.get('DESIGNATE') + ')');
                //}
                //else if (Ext.isDefined(feature.get('F_LEVEL'))) {
                //    selectedregion.setValue(feature.get('F_LEVEL') + ' - ' + feature.get('F_CODE') + ' (' + feature.get('OCEAN') + ')');
                //}
                //else if (Ext.isDefined(feature.get('MarRegion'))){
                //    selectedregion.setValue(feature.get('MarRegion'));
                //}
                //else {
                    var feature_columns = me.toplayer.get('feature_display_column').split(',');
                    var regionname_html = '';
                    for (var i = 0; i < feature_columns.length; i++) {
                        regionname_html += feature.get(feature_columns[i].trim());
                        if (i != feature_columns.length-1){
                            regionname_html += ' - ';
                        }
                    }
                    selectedregion.setValue(regionname_html);
                //}

                if (displaywkt) {
                    var wkt = new ol.format.WKT();
                    var wktstr = wkt.writeFeature(feature);
                    // not a good idea in general
                    wktstr = wktstr.replace(/,/g, ', ');
                    wkt_polygon.setValue(wktstr);
                }

                Ext.getCmp('fieldset_selectedregion').show();

            } else {
                //regionname.setValue('&nbsp;');
                //admin0name.setValue('&nbsp;');
                //admin1name.setValue('&nbsp;');
                //admin2name.setValue('&nbsp;');
                wkt_polygon.setValue('');
                selectedregion.setValue('&nbsp;');
                Ext.getCmp('fieldset_selectedregion').hide();
            }

            if (feature !== selectfeature) {
                if (selectfeature != null) {
                    selectedFeatureOverlay.getSource().removeFeature(selectfeature);
                }
                if (feature != null) {
                    selectedFeatureOverlay.getSource().addFeature(feature);
                }
                selectfeature = feature;
            }

            if (Ext.isDefined(feature)) {
                me.selectedfeature = feature;

                var outmask = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')).pressed;
                if (outmask){
                    me.getController().outmaskFeature();
                    //me.getController().updateProductLayer();
                }
            }
            else {
                me.selectedfeature = null;
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

        me.map.on('dblclick', function(evt) {
            if (Ext.isDefined(me.selectedfeature)) {
                // Zoom to and center the selected feature
                var polygon = /** @type {ol.geom.SimpleGeometry} */ (me.selectedfeature.getGeometry());
                var size = /** @type {ol.Size} */ (me.map.getSize());
                me.map.getView().fit(
                    polygon,
                    size,
                    {
                        padding: [50, 50, 50, 50],
                        constrainResolution: false
                    }
                );
            }
        });


        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('loadingvectorlayer'),   // 'Loading vector layer...',
            target : Ext.getCmp('mapcontainer_'+me.id)  //  Ext.getCmp(me.id) //
            ,toFrontOnShow: true
            ,useTargetEl:true
        });
        myLoadMask.show();

        var vectorSource = new ol.source.Vector({      // ol.source.GeoJSON({
             // projection: 'EPSG:4326', // 'EPSG:3857',
             // url: 'resources/geojson/countries.geojson'
             url: 'analysis/getvectorlayer?file=' + layerrecord.get('filename')
            ,format: new ol.format.GeoJSON()
            ,wrapX: false   // no repeat of layer when
            ,noWrap: true
        });

        var listenerKey = vectorSource.on('change', function(e) {
          if (vectorSource.getState() == 'ready') {
              // hide loading icon
              myLoadMask.hide();

              // zoom to vectorlayer extent
              var size = /** @type {ol.Size} */ (me.map.getSize());
              me.map.getView().fit(
                  vectorSource.getExtent(),
                  size,
                  {
                      padding: [50, 50, 50, 50],
                      constrainResolution: false
                  }
              );

              // Unregister the "change" listener
              ol.Observable.unByKey(listenerKey);
              // or vectorSource.unByKey(listenerKey) if you don't use the current master branch of ol3

              //layerloaded = true;
          }
          else {
            myLoadMask.hide();
          }
        });

        var styleCache = {};
        var vectorLayer = new ol.layer.Vector({
            title: layertitle,
            layer_id: layerrecord.get('layername'),     // + '_' + me.id.replace(/-/g,'_')
            layerorderidx:layerrecord.get('layerorderidx'),
            feature_display_column: layerrecord.get('feature_display_column'),
            layertype: 'vector',
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
                            color: layerrecord.get('polygon_outlinecolor'), // '#319FD3',
                            width: layerrecord.get('polygon_outlinewidth')
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
        //me.map.removeLayer(this.getView().map.getLayers().a[layerrecord.get('layerorderidx')]);
        //me.map.addLayer(vectorLayer);
        vectorlayer_idx = me.getController().findlayer(me.map, layerrecord.get('layername'));   // + '_' + me.id.replace(/-/g,'_')
        if (vectorlayer_idx != -1)
            me.map.getLayers().removeAt(vectorlayer_idx);

        var layer_idx = layerrecord.get('layerorderidx');
        me.map.getLayers().getArray().forEach(function (layer, idx) {
            var this_layer_id = layer.get("layerorderidx")
            if (this_layer_id > layerrecord.get('layerorderidx')) {
                layer_idx = idx;
            }
            if (this_layer_id == layerrecord.get('layerorderidx')) {
                layer_idx = idx+1;
            }
        });
        me.map.getLayers().insertAt(layer_idx, vectorLayer);
        //console.info('layer inserted at index: ' + layer_idx);

        me.getController().addLayerSwitcher(me.map);

        if (me.getController().outmaskingPossible(me.map)){
            outmask_togglebtn.show();
        }
        else outmask_togglebtn.hide();


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

    ,editLayerDrawProperties: function(callComponent){
        var layerrecord = callComponent.layerrecord;
        var myBorderDrawPropertiesWin = Ext.getCmp('BorderDrawPropertiesWin');
        if (myBorderDrawPropertiesWin!=null && myBorderDrawPropertiesWin!='undefined' ) {
            myBorderDrawPropertiesWin.close();
        }

        //var texteditor = new Ext.grid.GridEditor(new Ext.form.TextField({allowBlank: false,selectOnFocus: true}));
        //var numbereditor = new Ext.grid.GridEditor(new Ext.form.NumberField({allowBlank: false,selectOnFocus: true}));
        //
        //var cedit = new Ext.grid.GridEditor(new Ext.ux.ColorField({allowBlank: false,selectOnFocus: true}));

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

        var BorderDrawPropertiesWin = new Ext.Window({
             id:'BorderDrawPropertiesWin'
            ,title: esapp.Utils.getTranslation('Draw properties ') + esapp.Utils.getTranslation(layerrecord.get('submenu')) + (layerrecord.get('submenu') != '' ? ' ' : '') + esapp.Utils.getTranslation(layerrecord.get('layerlevel'))
            ,width:420
            ,plain: true
            ,modal: true
            ,resizable: true
            ,closable:true
            ,layout: {
                 type: 'fit'
            }
            ,items:[{
                xtype: 'propertygrid',
                //nameField: 'Property',
                //width: 400,
                nameColumnWidth: 230,
                sortableColumns: false,
                source: {
                    polygon_outlinecolor: esapp.Utils.convertRGBtoHex(layerrecord.get('polygon_outlinecolor')),
                    polygon_outlinewidth: layerrecord.get('polygon_outlinewidth'),
                    feature_highlight_outlinecolor: esapp.Utils.convertRGBtoHex(layerrecord.get('feature_highlight_outlinecolor')),
                    feature_highlight_outlinewidth: layerrecord.get('feature_highlight_outlinewidth'),
                    feature_highlight_fillopacity: layerrecord.get('feature_highlight_fillopacity'),
                    feature_highlight_fillcolor: esapp.Utils.convertRGBtoHex(layerrecord.get('feature_highlight_fillcolor')),
                    feature_selected_outlinecolor: esapp.Utils.convertRGBtoHex(layerrecord.get('feature_selected_outlinecolor')),
                    feature_selected_outlinewidth: layerrecord.get('feature_selected_outlinewidth')
                },
                sourceConfig: {
                    polygon_outlinecolor: {
                        displayName: esapp.Utils.getTranslation('outlinecolour'),   // 'Outline colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,render_to: BorderDrawPropertiesWin
                            //,trigger: 'foo'
                            //listeners: {
                            //    select: function(picker, selColor) {
                            //        alert(selColor);
                            //    }
                            //}
                            //,floating: false,
                            //,constrain: true
                        }
                        ,renderer: colorrenderer
                        //,renderer: function(v){
                        //    var color = v ? 'green' : 'red';
                        //    return '<span style="color: ' + color + ';">' + v + '</span>';
                        //}
                    },
                    polygon_outlinewidth: {
                        displayName: esapp.Utils.getTranslation('oulinewidth'),   // 'Outline width',
                        type: 'number'
                    },
                    feature_highlight_outlinecolor: {
                        displayName: esapp.Utils.getTranslation('highlightoutlinecolour'),   // 'Highlight outline colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: colorrenderer
                    },
                    feature_highlight_outlinewidth: {
                        displayName: esapp.Utils.getTranslation('highlightoutlinewidth'),   // 'Highlight outline width',
                        type: 'number'
                    },
                    feature_highlight_fillcolor: {
                        displayName: esapp.Utils.getTranslation('highlightfillcolour'),   // 'Highlight fill colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: colorrenderer
                    },
                    feature_selected_outlinecolor: {
                        displayName: esapp.Utils.getTranslation('selectedfeatureoutlinecolour'),   // 'Selected feature outline colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: colorrenderer
                    },
                    feature_highlight_fillopacity: {
                        displayName: esapp.Utils.getTranslation('highlightfillopacity'),   // 'Highlight fill opacity',
                        editor: {
                            xtype: 'combobox',
                            store: [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],
                            forceSelection: true
                        }
                    },
                    feature_selected_outlinewidth: {
                        displayName: esapp.Utils.getTranslation('selectedfeatureoutlinewidth'),   // 'Selected feature outline width',
                        type: 'number'
                    }
                },
                //customEditors: {
                //    myProp: new Ext.grid.GridEditor(combo, {})
                //},
                //customRenders: {
                //    myProp: function(value){
                //        var record = combo.findRecord(combo.valueField, value);
                //        return record ? record.get(combo.displayField) : combo.valueNotFoundText;
                //    }
                //},
                listeners: {
                    propertychange: function( source, recordId, value, oldValue, eOpts ){
                        //console.info(source);
                        //console.info(recordId);
                        //console.info(value);
                        //console.info(oldValue.toLowerCase());
                        if (value != oldValue)
                            layerrecord.set(recordId, value)
                    }
                }
            }]

        });
        BorderDrawPropertiesWin.show();
        BorderDrawPropertiesWin.alignTo(callComponent.getEl(),"l-tr", [-6, 0]);  // See: http://www.extjs.com/deploy/dev/docs/?class=Ext.Window&member=alignTo
    }

    ,createLayersMenuItems: function(mainmenuitem) {
        var me = this.getView();

        //console.info(this.getStore('layers'));
        //this.getStore('layers').load({
        //    callback:function(records, options, success){
        //        console.info(this);
        //        console.info(records);
        //        console.info(this.find('layercode', 'africa'));
        //
        //        //records.forEach(function(layer) {
        //        //    // layer.get('selected')
        //        //    console.info(layer);
        //        //  records.find('layercode', 'africa')
        //        //});
        //    }
        //});

        var layersStore = this.getStore('layers');

        layersStore.clearFilter(true);
        layersStore.filterBy(function (record, id) {
            if (record.get("menu") == mainmenuitem && record.get("enabled")) {
                return true;
            }
            return false;
        });

        layersStore.setSorters([
            {property: 'menu', direction: 'ASC'},
            {property: 'submenu', direction: 'ASC', transform:  function (submenu) { return submenu.toLowerCase(); }},
            {property: 'layerlevel', direction: 'ASC'}]);
        layersStore.sort();
        //console.info(layersStore);

        var MainMenuItems = [];
        var SubMenuItems = [];
        var SubMenus = {};
        var currentSubmenu = '';
        var newSubMenu = {};
        var MenuItem = {};
        var counter = 0;

        layersStore.each(function(layer) {
            //console.info(layer);
            counter +=1
            if (layer.get('submenu')!= '' && layer.get('submenu') != currentSubmenu) {
                currentSubmenu = layer.get('submenu');
                if (SubMenuItems.length != 0){
                    newSubMenu.menu.items = SubMenuItems;
                    //SubMenus.push(newSubMenu);
                    MainMenuItems.push(newSubMenu);
                    SubMenuItems = [];
                }
                newSubMenu = {
                    text: esapp.Utils.getTranslation(layer.get('submenu')),   //'Africa',
                    name: layer.get('submenu'),      // 'africa',
                    menu: {
                        defaults: {
                            checked: false,
                            hideOnClick: false,
                            showSeparator: false,
                            cls: "x-menu-no-icon",
                            style: {
                                'margin-left': '5px'
                            }
                        },
                        items: []
                    }
                }
            }

            var containerItems = [];
            var checkboxCmp = Ext.create('Ext.form.field.Checkbox', {
                //boxLabel: esapp.Utils.getTranslation(layer.get('submenu')) + (layer.get('submenu') != '' ? ' ' : '') + esapp.Utils.getTranslation(layer.get('layerlevel')),
                boxLabel: esapp.Utils.getTranslation(layer.get('layername')) + '</BR><b class="smalltext" style="color:darkgrey">' + esapp.Utils.getTranslation(layer.get('provider')) +'</b>',
                flex: 1,
                margin: '0 5 0 5',
                layerrecord: layer,
                name: layer.get('layername'),
                level: layer.get('layerlevel'),
                geojsonfile: layer.get('filename'),
                checked: layer.get('open_in_mapview'),
                linecolor: layer.get('polygon_outlinecolor'),
                layerorderidx: layer.get('layerorderidx'),
                handler: 'addVectorLayer'
            });
            containerItems.push(checkboxCmp);
            containerItems.push({xtype: 'component', html: '<div style="border-left:1px solid #ababab;height:100%; display: inline-block;"></div>'});
            containerItems.push({
                xtype: 'button',
                cls: 'my-custom-button',
                layerrecord: layer,
                level: layer.get('layerlevel'),
                width: 30,
                text: '',
                tooltip: esapp.Utils.getTranslation('tipeditlayerdrawproperties'),   // 'Edit layer draw properties.',
                iconCls: 'edit16',
                handler: 'editLayerDrawProperties'
                //listeners: {click: function(){ console.info('open fishingareas layer')} }
            });
            MenuItem = {
                xtype: 'container',
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                overCls: 'over-item-cls',
                items: containerItems
            }

            if (layer.get('submenu')== ''){
                MainMenuItems.push(MenuItem);
            }
            else {
                SubMenuItems.push(MenuItem);
            }

            if (layer.get('submenu')!= '' && layersStore.data.length == counter) {
                if (SubMenuItems.length != 0) {
                    newSubMenu.menu.items = SubMenuItems;
                    //SubMenus.push(newSubMenu);
                    MainMenuItems.push(newSubMenu);
                }
            }
        });

        layersStore.clearFilter(true);

        return MainMenuItems;

    }

    ,createLayersMenu: function() {
        var me = this.getView();

        var borderVectorLayerItems = this.createLayersMenuItems('border');
        var marineVectorLayerMenuItems = this.createLayersMenuItems('marine');
        var otherVectorLayerMenuItems = this.createLayersMenuItems('other');

        Ext.data.StoreManager.lookup('LayersStore').load();

        var layersmenubutton = {
            xtype: 'button',
            //text: 'Add Layer',
            name:'vbtn-'+me.id,
            iconCls: 'layer-vector-add', // 'layers'
            scale: 'medium',
            floating: false,  // usually you want this set to True (default)
            collapseDirection: 'left',
            menu: {
                hideOnClick: false,
                iconAlign: '',
                defaults: {
                    hideOnClick: false,
                    cls: "x-menu-no-icon",
                    floating: false,
                    collapseDirection: 'left'
                },
                items: [{
                    text: esapp.Utils.getTranslation('borderlayers'),   // 'Border layers (FAO Gaul 2015)',
                    name: 'gaul2015',
                    //handler: 'editDrawPropertiesAdminLevels',
                    menu: {
                        defaults: {
                            hideOnClick: false,
                            cls: "x-menu-no-icon",
                            //scale: 'medium',
                            floating: false,
                            collapseDirection: 'left'
                        },
                        plain: true,
                        items: borderVectorLayerItems
                    }
                },{
                    text: esapp.Utils.getTranslation('marinelayers'),   // 'Marine vector layers',
                    name: 'marine',
                    menu: {
                        defaults: {
                            hideOnClick: false,
                            cls: "x-menu-no-icon",
                            //scale: 'medium',
                            floating: false,
                            collapseDirection: 'left'
                        },
                        plain: true,
                        items: marineVectorLayerMenuItems
                    }
                },{
                    text: esapp.Utils.getTranslation('otherlayers'),   // 'Other vector layers',
                    name: 'other',
                    menu: {
                        defaults: {
                            hideOnClick: false,
                            cls: "x-menu-no-icon",
                            //scale: 'medium',
                            floating: false,
                            collapseDirection: 'left'
                        },
                        plain: true,
                        items: otherVectorLayerMenuItems
                    }
                }]
            }
        };


        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            dock: 'top',
            autoShow: true,
            alwaysOnTop: true,
            floating: false,
            hidden: false,
            border: false,
            shadow: false,
            padding:0,
            items: [{
                text: '<div style="font-size: 11px;">' + esapp.Utils.getTranslation('productnavigator') + '</div>', // 'Product navigator',
                iconCls: 'africa',
                scale: 'medium',
                //style: {
                //    "font-size": '10px'
                //},
                handler: 'openProductNavigator'
            }
            ,layersmenubutton
            ,{
                xtype: 'container',
                width: 300,
                height: 38,
                top: 0,
                align:'left',
                defaults: {
                    style: {
                        "font-size": '10px'
                    }
                },
                items: [{
                    xtype: 'box',
                    height: 17,
                    top:0,
                    html: '<div id="region_name_' + me.id + '" style="text-align:left; font-size: 10px; font-weight: bold;"></div>'
                },{
                    xtype: 'box',
                    height: 15,
                    top:17,
                    html: '<div id="mouse-position_' + me.id + '"></div>'
                }]
            },'->', {
                //id: 'outmaskbtn_'+me.id,
                reference: 'outmaskbtn_'+me.id.replace(/-/g,'_'),
                hidden: true,
                iconCls: 'africa-orange24',
                scale: 'medium',
                enableToggle: true,
                handler: 'toggleOutmask'
            },{
                //id: 'legendbtn_'+me.id,
                reference: 'legendbtn_'+me.id.replace(/-/g,'_'),
                hidden: true,
                iconCls: 'legends',
                scale: 'medium',
                enableToggle: true,
                handler: 'toggleLegend'
            },{
                iconCls: 'fa fa-save fa-2x',
                style: { color: 'lightblue' },
                scale: 'medium',
                handler: 'saveMap',
                href: '',
                download: 'estationmap.png'
            },{
                //text: 'Unlink',
                enableToggle: true,
                iconCls: 'unlink',
                scale: 'medium',
                handler: 'toggleLink'
            }]
        });

    }

    ,loadDefaultLayers: function(){
        var me = this.getView();
        var layersStore = this.getStore('layers');
        layersStore.clearFilter(true);
        layersStore.filterBy(function (record, id) {
            if (record.get("enabled")) {
                return true;
            }
            return false;
        });

        layersStore.each(function(layer) {
            if (layer.get('open_in_mapview')) {
                me.getController().addVectorLayerToMapView(layer)
                //var task = new Ext.util.DelayedTask(function() {
                //    me.getController().addVectorLayerToMapView(layer);
                //});
                //task.delay(3000);
            }
        });
    }
});
