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
                                    var outmask = me.lookupReference('outmaskbtn_'+ me.getView().id.replace(/-/g,'_')).pressed;
                                    if (outmask){
                                        me.getView().getController().outmaskFeature();
                                    }

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

    //,updateProductLayer: function(productcode, productversion, mapsetcode, subproductcode, legendid, clickeddate) {
    ,updateProductLayer: function() {
        var params = {};
        var outmask = this.lookupReference('outmaskbtn_'+ this.getView().id.replace(/-/g,'_')).pressed;
        //console.info(this.lookupReference('outmaskbtn_'+ this.getView().id.replace(/-/g,'_')));
        //console.info(outmask);
        //console.info(this.getView().selectedfeature);

        // Does not work passing the WKT. Gives error: 414 Request-URI Too Long
        // The requested URL's length exceeds the capacity limit for this server.
        //if (outmask && this.getView().selectedfeature){
        //    var wkt = new ol.format.WKT();
        //    var wktstr = wkt.writeFeature(this.getView().selectedfeature);
        //    wktstr = wktstr.replace(/,/g, ', ');  // not a good idea in general
        //    params = {
        //        productcode: this.getView().productcode,
        //        productversion: this.getView().productversion,
        //        subproductcode: this.getView().subproductcode,
        //        mapsetcode: this.getView().mapsetcode,
        //        legendid: this.getView().legendid,
        //        date: this.getView().productdate,
        //        outmask:true,
        //        selectedfeature: wktstr,
        //        'FORMAT': 'image/png'
        //    };
        //}
        //else {
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
        //}
        // console.info(params);

        this.getView().productlayer = new ol.layer.Tile({
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            layertype: 'raster',
            type: 'base',
            visible: true,
            source: new ol.source.TileWMS({
                url: 'analysis/getproductlayer',
                crossOrigin: '',  // 'anonymous',
                attributions: [new ol.Attribution({
                    html: '&copy; <a href="https://ec.europa.eu/jrc/">'+esapp.Utils.getTranslation('estation2')+'</a>'
                })],
                params: params,

                //params: {
                //    productcode:productcode,
                //    productversion:productversion,
                //    subproductcode:subproductcode,
                //    mapsetcode:mapsetcode,
                //    legendid:legendid,
                //    date:clickeddate,
                //    'FORMAT': 'image/png'
                //},
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
        var mapimage_url = '';

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
        //console.info(maplegendpanel);
        if (maplegendpanel.hidden == false) {
            var maplegendhtml = document.getElementById('product-legend' + mapviewwin.id);
        //    console.info('<div>'+mapviewwin.legendHTML+'</div>');
        //    console.info(maplegendhtml);

            html2canvas(maplegendhtml, {
                        onrendered: function(canvas) {
                            var image = canvas.toDataURL("image/png");
                            filename = 'legend_' + filename;
                            //console.info(mapleggendimage_url);

                            if (Ext.fly('downloadlegendlink')) {
                                Ext.fly('downloadlegendlink').destroy();
                            }
                            var downloadlegendlink = document.createElement('a');
                            downloadlegendlink.id = 'downloadlegendlink';
                            downloadlegendlink.name = downloadlegendlink.id;
                            downloadlegendlink.className = 'x-hidden';
                            document.body.appendChild(downloadlegendlink);
                            downloadlegendlink.setAttribute('download', filename);
                            downloadlegendlink.setAttribute('href', image);
                            downloadlegendlink.click();
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


        mapviewwin.map.once('postcompose', function(event) {
            var canvas = event.context.canvas;
            //console.info(Ext.fly('ol-scale-line-inner'));

            var scalewidth = parseInt(Ext.fly('ol-scale-line-inner').css('width'));
            var scalenumber = Ext.fly('ol-scale-line-inner').text();
            var ctx = event.context;
            ctx.beginPath();

            //Scale Text
            ctx.lineWidth=1;
            ctx.font = "20px Arial";
            ctx.strokeText(scalenumber,10,canvas.height-25);

            //Scale Dimensions
            ctx.lineWidth=5;
            ctx.moveTo(10,canvas.height-20);
            ctx.lineTo(parseInt(scalewidth)+10,canvas.height-20);
            ctx.stroke();

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
            //console.info(mapviewwin.selectedfeature);
            if (Ext.isDefined(mapviewwin.selectedfeature)){
                mapviewwin.getController().outmaskFeature();
            }
        }
        else {
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

    ,outmaskFeature: function(){
        var me = this;

        function isFunction(possibleFunction) {
          return typeof(possibleFunction) === typeof(Function);
        }

        if (me.getView().selectedfeature != null && isFunction(me.getView().selectedfeature.getGeometry) && isFunction(me.getView().selectedfeature.getGeometry().getPolygons))
            console.info(me.getView().selectedfeature.getGeometry().getPolygons());
        else {
            console.info(me.getView().selectedfeature.getGeometry());
        }

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
                    // Using a style is a hack to workaround a limitation in
                    // OpenLayers 3, where a geometry will not be draw if no
                    // style has been provided.
                    vecCtx.setFillStrokeStyle(fillStyle, null);
                    //var multipoligon = new ol.geom.MultiPolygon(me.getView().selectedfeature.getGeometry().getPolygons(), 'XY');
                    //console.info(multipoligon);
                    //vecCtx.drawMultiPolygonGeometry(me.getView().selectedfeature.getGeometry());  // , me.getView().selectedfeature

                    me.getView().selectedfeature.getGeometry().getPolygons().forEach(function (polygon, idx) {
                        //console.info(polygon);
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

    ,addVectorLayer: function(menuitem){
        // ToDo: Open a new window from which the user can select an in the eStation2 existing or upload a vector layer.
        // ToDo: Have the user set vector layer setting before adding the layer to the map.
        // For now a predefined GeoJSON layer with fixed settings is added.

        //console.info(Ext.ComponentQuery.query('button[name=vbtn-'+this.getView().id+']')[0]);
        Ext.ComponentQuery.query('button[name=vbtn-'+this.getView().id+']')[0].hideMenu();
        //this.getView().lookupReference('vbtn-'+this.getView().id).hideMenu();

        //console.info(menuitem);
        var me = this.getView();
        var namefield = '',
            vectorlayer_idx = -1,
            layerrecord = menuitem.layerrecord,
            layertitle = menuitem.boxLabel,

            geojsonfile = layerrecord.get('filename'),
            feature_display_column = layerrecord.get('feature_display_column'),
            adminlevel = layerrecord.get('layerlevel'),
            polygon_outlinewidth = layerrecord.get('polygon_outlinewidth'),   // 1,
            polygon_outlinecolor = layerrecord.get('polygon_outlinecolor'),
            feature_highlight_outlinecolor = layerrecord.get('feature_highlight_outlinecolor'),
            feature_highlight_outlinewidth = layerrecord.get('feature_highlight_outlinewidth'),
            feature_highlight_fillcolor    = layerrecord.get('feature_highlight_fillcolor'),
            feature_highlight_fillopacity  = layerrecord.get('feature_highlight_fillopacity'),
            feature_selected_outlinecolor  = layerrecord.get('feature_selected_outlinecolor'),
            feature_selected_outlinewidth  = layerrecord.get('feature_selected_outlinewidth')
            ;

        var outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')); //  + me.getView().id);

        if (menuitem.level == 'admin0'){
            namefield = 'ADM0_NAME';
            linewidth = 2;
        }
        else if (menuitem.level == 'admin1'){
            namefield = 'ADM1_NAME';
            linewidth = 2;
        }
        else if (menuitem.level == 'admin2'){
            namefield = 'ADM2_NAME';
            linewidth = 1;
        }

        if (menuitem.checked) {
            //console.info(menuitem);
            //var mapViewContainer = this.getView().lookupReference('mapcontainer_'+me.id);
            var myLoadMask = new Ext.LoadMask({
                //floating: false,
                alwaysOnTop: true,
                msg    : esapp.Utils.getTranslation('loadingvectorlayer'),   // 'Loading vector layer...',
                target : Ext.getCmp(me.id) // Ext.getCmp('mapcontainer_'+me.id)  //
            });
            myLoadMask.show();


            var vectorSource = new ol.source.Vector({      // ol.source.GeoJSON({
                //projection: 'EPSG:4326', // 'EPSG:3857',  //
                //url: 'resources/geojson/countries.geojson'
                //url: 'resources/geojson/' + geojsonfile,
                 url: 'analysis/getvectorlayer?file=' + geojsonfile
                ,format: new ol.format.GeoJSON()
                ,wrapX: false   // no repeat of layer when
                ,noWrap: true
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
                                color: polygon_outlinecolor, // '#319FD3',
                                width: polygon_outlinewidth
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

            if (me.getController().outmaskingPossible(me.map)){
                outmask_togglebtn.show();
            }
            else outmask_togglebtn.hide();

            var fillopacity = (feature_highlight_fillopacity/100).toString().replace(",", ".");
            var highlight_fillcolor_opacity = 'rgba(' + esapp.Utils.HexToRGB(feature_highlight_fillcolor) + ',' + fillopacity + ')'
            var highlightStyleCache = {};
            var collectionFO = new ol.Collection();
            var featureOverlay = new ol.layer.Vector({      //new ol.FeatureOverlay({
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
                      color: feature_highlight_outlinecolor,    // '#319FD3',     //  '#FFFFFF',    // '#f00',
                      width: feature_highlight_outlinewidth
                    })
                    ,fill: new ol.style.Fill({
                      color: highlight_fillcolor_opacity    // 'rgba(49,159,211,0.1)'    // 'rgba(255,255,255,1)'    // 'rgba(255,0,0,0.1)'
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

            var highlight = null;
            var displayFeatureInfo = function(pixel) {

                var toplayer = null;
                var topfeature = null;
                var ignorefeature = true;
                var toplayerindex = 4;
                me.map.getLayers().getArray().forEach(function (layer, idx) {
                    var this_layer_id = layer.get("layerorderidx")
                    if (this_layer_id != 0 && layer.getVisible() && this_layer_id <= toplayerindex) {
                        toplayerindex = idx;
                    }
                });
                toplayer = me.map.getLayers().item(toplayerindex);

                var feature = me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
                    if (layer == toplayer){
                        topfeature = feature;
                    }
                    //if (topfeature == null){
                    //    toplayer = layer;
                    //    topfeature = feature;
                    //}
                    //if (highlight != null){
                    //    if (feature == highlight){
                    //        console.info('ignore highlight!');
                    //        ignorefeature = false;
                    //    }
                    //}
                    //if (selectfeature != null){
                    //    if (feature == selectfeature){
                    //        console.info('ignore selectfeature!');
                    //        ignorefeature = false;
                    //    }
                    //}
                    //if (!ignorefeature && toplayer != null && layer != null && layer.get("layerorderidx") > toplayer.get("layerorderidx")){
                    //    toplayer = layer;
                    //    topfeature = feature;
                    //}
                    return topfeature;
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

                    //var region = '';
                    if (Ext.isDefined(feature.get('ADM2_NAME'))){
                        regionname.setHtml(feature.get('ADM0_NAME') + ' - ' +
                                           feature.get('ADM1_NAME') + ' - ' +
                                           feature.get('ADM2_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('ADM1_NAME'))){
                        regionname.setHtml(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('ADM0_NAME'))) {
                        regionname.setHtml(feature.get('ADM0_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('AREANAME'))){
                        regionname.setHtml(feature.get('COUNTRY') + ' - ' + feature.get('AREANAME') + ' (' + feature.get('DESIGNATE') + ')');
                    }
                    else if (Ext.isDefined(feature.get('F_LEVEL'))){
                        regionname.setHtml(feature.get('F_LEVEL') + ' - ' + feature.get('F_CODE') + ' (' + feature.get('OCEAN') + ')');
                    }
                    else if (Ext.isDefined(feature.get('MarRegion'))){
                        regionname.setHtml(feature.get('MarRegion'));
                    }
                    else {
                        var feature_columns = feature_display_column.split(',');
                        var regionname_html = '';
                        for (var i = 0; i < feature_columns.length; i++) {
                            regionname_html += feature.get(feature_columns[i].trim());
                            if (i != feature_columns.length-1){
                                regionname_html += ' - ';
                            }
                        }
                        regionname.setHtml(regionname_html);
                    }
                    //if (adminlevel == 'admin0') {
                    //    regionname.setHtml(feature.get('ADM0_NAME'));
                    //}
                    //else if (adminlevel == 'admin1') {
                    //    regionname.setHtml(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    //}
                    //else if (adminlevel == 'admin2') {
                    //    regionname.setHtml(feature.get('ADM0_NAME') + ' - ' +
                    //                       feature.get('ADM1_NAME') + ' - ' +
                    //                       feature.get('ADM2_NAME'));
                    //}
                    //featureTooltip.html = feature.getId() + ': ' + feature.get(namefield);
                } else {
                    regionname.setHtml('&nbsp;');
                    //featureTooltip.html = '&nbsp;';
                }

                if (feature !== highlight) {
                    if (highlight) {
                        featureOverlay.getSource().removeFeature(highlight);
                    }
                    if (feature) {
                        featureOverlay.getSource().addFeature(feature);
                    }
                    highlight = feature;
                }
            };

            selectStyleCache = {};
            var collectionSFO = new ol.Collection();
            var selectedFeatureOverlay =new ol.layer.Vector({      //new ol.FeatureOverlay({
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
                      color: feature_selected_outlinecolor,   // '#f00',
                      width: feature_selected_outlinewidth
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
                var feature = highlight;

                var regionname = Ext.getCmp('regionname');
                var admin0name = Ext.getCmp('admin0name');
                var admin1name = Ext.getCmp('admin1name');
                var admin2name = Ext.getCmp('admin2name');
                var selectedregion = Ext.getCmp('selectedregionname');

                var wkt_polygon = Ext.getCmp('wkt_polygon');

                if (Ext.isDefined(feature)) {
                    regionname.setValue(feature.get(namefield));

                    if (Ext.isDefined(feature.get('ADM2_NAME'))){
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue(feature.get('ADM1_NAME'));
                        admin2name.setValue(feature.get('ADM2_NAME'));
                        selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME') + ' - ' + feature.get('ADM2_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('ADM1_NAME'))){
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue(feature.get('ADM1_NAME'));
                        admin2name.setValue('&nbsp;');
                        selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('ADM0_NAME'))){
                        admin0name.setValue(feature.get('ADM0_NAME'));
                        admin1name.setValue('&nbsp;');
                        admin2name.setValue('&nbsp;');
                        selectedregion.setValue(feature.get('ADM0_NAME'));
                    }
                    else if (Ext.isDefined(feature.get('AREANAME'))){
                        selectedregion.setValue(feature.get('COUNTRY') + ' - ' + feature.get('AREANAME') + ' (' + feature.get('DESIGNATE') + ')');
                    }
                    else if (Ext.isDefined(feature.get('F_LEVEL'))) {
                        selectedregion.setValue(feature.get('F_LEVEL') + ' - ' + feature.get('F_CODE') + ' (' + feature.get('OCEAN') + ')');
                    }
                    else if (Ext.isDefined(feature.get('MarRegion'))){
                        selectedregion.setValue(feature.get('MarRegion'));
                    }
                    else {
                        var feature_columns = feature_display_column.split(',');
                        var regionname_html = '';
                        for (var i = 0; i < feature_columns.length; i++) {
                            regionname_html += feature.get(feature_columns[i].trim());
                            if (i != feature_columns.length-1){
                                regionname_html += ' - ';
                            }
                        }
                        selectedregion.setValue(regionname_html);
                    }

                    //if (adminlevel == 'admin0') {
                    //    admin0name.setValue(feature.get('ADM0_NAME'));
                    //    admin1name.setValue('&nbsp;');
                    //    admin2name.setValue('&nbsp;');
                    //    selectedregion.setValue(feature.get('ADM0_NAME'));
                    //}
                    //else if (adminlevel == 'admin1') {
                    //    admin0name.setValue(feature.get('ADM0_NAME'));
                    //    admin1name.setValue(feature.get('ADM1_NAME'));
                    //    admin2name.setValue('&nbsp;');
                    //    selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME'));
                    //}
                    //else if (adminlevel == 'admin2') {
                    //    admin0name.setValue(feature.get('ADM0_NAME'));
                    //    admin1name.setValue(feature.get('ADM1_NAME'));
                    //    admin2name.setValue(feature.get('ADM2_NAME'));
                    //    selectedregion.setValue(feature.get('ADM0_NAME') + ' - ' + feature.get('ADM1_NAME') + ' - ' + feature.get('ADM2_NAME'));
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
                    regionname.setValue('&nbsp;');
                    admin0name.setValue('&nbsp;');
                    admin1name.setValue('&nbsp;');
                    admin2name.setValue('&nbsp;');
                    wkt_polygon.setValue('&nbsp;');
                    selectedregion.setValue('&nbsp;');
                    Ext.getCmp('fieldset_selectedregion').hide();
                }

                if (feature !== selectfeature) {
                    //if (Ext.isDefined(selectfeature)) {
                    if (selectfeature != null) {
                        selectedFeatureOverlay.getSource().removeFeature(selectfeature);
                    }
                    if (feature != null) {
                        selectedFeatureOverlay.getSource().addFeature(feature);
                    }
                    selectfeature = feature;
                }

                //var styleCache = {};
                //var text = '';
                //if (!styleCache[text]) {
                //    styleCache[text] = [new ol.style.Style({
                //        fill: new ol.style.Fill({
                //          color: 'rgba(255, 255, 255, 1)'
                //        }),
                //        cursor: "pointer",
                //        stroke: new ol.style.Stroke({
                //            color: '#FFFFFF',
                //            width: 1
                //        })
                //    })];
                //}
                //vectorLayer.setStyle(styleCache[text]);

                if (Ext.isDefined(feature)) {
                    me.selectedfeature = feature;
                    //// Zoom to and center the selected feature
                    //var polygon = /** @type {ol.geom.SimpleGeometry} */ (feature.getGeometry());
                    //var size = /** @type {ol.Size} */ (me.map.getSize());
                    //me.map.getView().fitGeometry(
                    //    polygon,
                    //    size,
                    //    {
                    //        padding: [50, 50, 50, 50],
                    //        //padding: [170, 50, 30, 150],
                    //        constrainResolution: false
                    //    }
                    //);

                    var outmask = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')).pressed;
                    if (outmask){
                        me.getController().outmaskFeature();
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
        //console.info(callComponent);
        //console.info(callComponent.layerrecord);
        var layerrecord = callComponent.layerrecord;
        var myBorderDrawPropertiesWin = Ext.getCmp('BorderDrawPropertiesWin');
        if (myBorderDrawPropertiesWin!=null && myBorderDrawPropertiesWin!='undefined' ) {
            myBorderDrawPropertiesWin.close();
        }

        //var texteditor = new Ext.grid.GridEditor(new Ext.form.TextField({allowBlank: false,selectOnFocus: true}));
        //var numbereditor = new Ext.grid.GridEditor(new Ext.form.NumberField({allowBlank: false,selectOnFocus: true}));
        //
        //var cedit = new Ext.grid.GridEditor(new Ext.ux.ColorField({allowBlank: false,selectOnFocus: true}));
        var crenderer = function(color) {
            renderTpl = color;

            if (color.trim()==''){
                renderTpl = 'transparent';
            }
            else {
                renderTpl = '<span style="background:rgb('+esapp.Utils.HexToRGB(color)+'); color:'+esapp.Utils.invertHexToRGB(color)+';">'+esapp.Utils.HexToRGB(color)+'</span>';
            }
            return renderTpl;
        };


        var BorderDrawPropertiesWin = new Ext.Window({
             id:'BorderDrawPropertiesWin'
            ,title: esapp.Utils.getTranslation('Draw properties ') + esapp.Utils.getTranslation(layerrecord.get('submenu')) + (layerrecord.get('submenu') != '' ? ' ' : '') + esapp.Utils.getTranslation(layerrecord.get('layerlevel'))
            ,width:420
            //,height:180
            ,plain: true
            ,modal: true
            ,resizable: true
            //,shadow:false
            //,stateful :false
            ,closable:true
            ,layout: {
                 type: 'fit'
            }
            //,layout: {
            //     type: 'hbox',
            //     align:'stretch'
            //}
            //,tools:[{
               //id:'refresh',
               //qtip: esapp.Utils.getTranslation('qtip_reload_adminlevels_list'), // 'Reload Administrative levels',
               //scope:this,
               //handler:function() {
               //    //Ext.getCmp('adminlevelslist').store.load();
               //}
            //}]
            ,items:[{
                //xtype: 'image',
                //src: 'resources/img/adminleveldrawproperties.png'

                xtype: 'propertygrid',
                //nameField: 'Property',
                //width: 400,
                nameColumnWidth: 230,
                sortableColumns: false,
                source: {
                    polygon_outlinecolor: layerrecord.get('polygon_outlinecolor'),
                    polygon_outlinewidth: layerrecord.get('polygon_outlinewidth'),
                    feature_highlight_outlinecolor: layerrecord.get('feature_highlight_outlinecolor'),
                    feature_highlight_outlinewidth: layerrecord.get('feature_highlight_outlinewidth'),
                    feature_highlight_fillcolor: layerrecord.get('feature_highlight_fillcolor'),
                    feature_highlight_fillopacity: layerrecord.get('feature_highlight_fillopacity'),
                    feature_selected_outlinecolor: layerrecord.get('feature_selected_outlinecolor'),
                    feature_selected_outlinewidth: layerrecord.get('feature_selected_outlinewidth')
                },
                sourceConfig: {
                    polygon_outlinecolor: {
                        displayName: 'Outline colour',
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
                        ,renderer: crenderer
                        //,renderer: function(v){
                        //    var color = v ? 'green' : 'red';
                        //    return '<span style="color: ' + color + ';">' + v + '</span>';
                        //}
                    },
                    polygon_outlinewidth: {
                        displayName: 'Outline width',
                        type: 'number'
                    },
                    feature_highlight_outlinecolor: {
                        displayName: 'Highlight outline colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: crenderer
                    },
                    feature_highlight_outlinewidth: {
                        displayName: 'Highlight outline width',
                        type: 'number'
                    },
                    feature_highlight_fillcolor: {
                        displayName: 'Highlight fill colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: crenderer
                    },
                    feature_highlight_fillopacity: {
                        displayName: 'Highlight fill opacity',
                        editor: {
                            xtype: 'combobox',
                            store: [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],
                            forceSelection: true
                        }
                    },
                    feature_selected_outlinecolor: {
                        displayName: 'Selected feature outline colour',
                        editor: {
                            xtype: 'mycolorpicker'
                            //,floating: false
                        }
                        ,renderer: crenderer
                    },
                    feature_selected_outlinewidth: {
                        displayName: 'Selected feature outline width',
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
            if (record.get("menu") == mainmenuitem) {
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
                boxLabel: esapp.Utils.getTranslation(layer.get('layername')),
                flex: 1,
                margin: '0 5 0 5',
                layerrecord: layer,
                name: layer.get('layername'),
                level: layer.get('layerlevel'),
                geojsonfile: layer.get('filename'),
                checked: false,
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
                tooltip: 'Edit layer draw properties.',
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

        //var layersStore = this.getStore('layers');
        //
        //layersStore.clearFilter(true);
        //layersStore.filterBy(function (record, id) {
        //    if (record.get("menu") == 'border') {
        //        return true;
        //    }
        //    return false;
        //    // case-insensitive match of 'africa' in the layercode
        //    //return record.get('layercode').toLowerCase().indexOf('africa') > -1;
        //});
        //console.info(layersStore);
        //
        //
        //var marineVectorlayersMenuItems = [];
        //var containerItems = [];
        //var checkboxCmp = Ext.create('Ext.form.field.Checkbox', {
        //    boxLabel: esapp.Utils.getTranslation('fishingareas'), // 'Fishing Areas',
        //    flex: 1,
        //    margin: '0 5 0 5',
        //    name: 'fisharea',
        //    level: 'fisharea',
        //    geojsonfile: 'AFR_MARINE/AFR_FAO_FISH_AREA.geojson',
        //    checked: false,
        //    linecolor: '#000',
        //    layerorderidx: 1,
        //    handler: 'addVectorLayer'
        //});
        //containerItems.push(checkboxCmp);
        ////containerItems.push({
        ////    xtype: 'button',
        ////    cls: 'my-custom-button',
        ////    textAlign: 'left',
        ////    checkboxCmp: checkboxCmp,
        ////    name: 'fisharea',
        ////    level: 'fisharea',
        ////    geojsonfile: 'AFR_MARINE/AFR_FAO_FISH_AREA.geojson',
        ////    checked: false,
        ////    linecolor: '#000',
        ////    layerorderidx: 1,
        ////    flex: 1,
        ////    margin: '0 0 0 0',
        ////    padding: '0 0 0 0',
        ////    text: esapp.Utils.getTranslation('fishingareas'),
        ////    listeners: {
        ////        click: function(button, event, eOpts){
        ////            var checkboxCmp = button.checkboxCmp;
        ////            if (checkboxCmp) {
        ////                checkboxCmp.setValue(!checkboxCmp.getValue());
        ////            }
        ////            console.info('open fishingareas layer')
        ////        }
        ////    } // me.addVectorLayer}
        ////});
        //containerItems.push({xtype: 'component', html: '<div style="border-left:1px solid #ababab;height:100%; display: inline-block;"></div>'});
        //containerItems.push({
        //    xtype: 'button',
        //    cls: 'my-custom-button',
        //    level: 'fisharea',
        //    width: 30,
        //    text: '',
        //    tooltip: 'Edit layer draw properties.',
        //    iconCls: 'edit16',
        //    handler: 'editDrawPropertiesAdminLevels'
        //    //listeners: {click: function(){ console.info('open fishingareas layer')} }
        //});  // me.editDrawPropertiesAdminLevels
        //
        //marineVectorlayersMenuItems.push({
        //    xtype: 'container',
        //    layout: {
        //        type: 'hbox',
        //        align: 'stretch'
        //    },
        //    overCls: 'over-item-cls',
        //    items: containerItems
        //});
        //
        //var containerItems2 = [];
        //var checkboxCmp2 = Ext.create('Ext.form.field.Checkbox', {
        //    boxLabel: esapp.Utils.getTranslation('sea_exclusive_economic_zone'), // 'Sea Exclusive economic zone (EEZ)',
        //    flex: 1,
        //    margin: '0 5 0 5',
        //    name: 'eez',
        //    level: 'eez',
        //    geojsonfile: 'AFR_MARINE/AFR_EEZ_IHO_union_v2.geojson',
        //    checked: false,
        //    linecolor: '#000',
        //    layerorderidx: 1,
        //    handler: 'addVectorLayer'
        //});
        //containerItems2.push(checkboxCmp2);
        //containerItems2.push({xtype: 'component', html: '<div style="border-left:1px solid #ababab;height:100%; display: inline-block;"></div>'});
        //containerItems2.push({
        //    xtype: 'button',
        //    cls: 'my-custom-button',
        //    level: 'eez',
        //    width: 30,
        //    text: '',
        //    tooltip: 'Edit layer draw properties.',
        //    iconCls: 'edit16',
        //    handler: 'editDrawPropertiesAdminLevels'
        //    //listeners: {click: function(){ console.info('open Sea Exclusive economic zone layer')} }
        //});  // me.editDrawPropertiesAdminLevels
        //
        //marineVectorlayersMenuItems.push({
        //    xtype: 'container',
        //    layout: {
        //        type: 'hbox',
        //        align: 'stretch'
        //    },
        //    overCls: 'over-item-cls',
        //    items: containerItems2
        //});
        //
        //
        //var containerItems3 = [];
        //var checkboxCmp3 = Ext.create('Ext.form.field.Checkbox', {
        //    boxLabel: esapp.Utils.getTranslation('protectedareas'), // 'Protected areas',
        //    boxLabelAlign : 'before',
        //    flex: 1,
        //    margin: '0 5 0 5',
        //    name: 'protectedareas',
        //    level: 'protectedareas',
        //    geojsonfile: 'AFR_PA/AFR_PA_ID.geojson',
        //    checked: false,
        //    linecolor: '#000',
        //    layerorderidx: 1,
        //    handler: 'addVectorLayer'
        //});
        ////containerItems3.push({xtype: 'component', html: '<div style="border-left:1px solid #ababab;height:100%; display: inline-block;"></div>'});
        //containerItems3.push({
        //    xtype: 'button',
        //    cls: 'my-custom-button',
        //    level: 'protectedareas',
        //    width: 18,
        //    margin: '0 0 0 0',
        //    text: '',
        //    tooltip: 'Edit layer draw properties.',
        //    iconCls: 'edit16',
        //    handler: 'editDrawPropertiesAdminLevels'
        //    //listeners: {click: function(){ console.info('open Sea Exclusive economic zone layer')} }
        //});  // me.editDrawPropertiesAdminLevels
        //containerItems3.push(checkboxCmp3);
        //
        //var paVectorlayerMenuItem = {
        //    xtype: 'container',
        //    cls: "x-menu-no-icon",
        //    margin: '0 0 0 2',
        //    padding: '0 0 0 0',
        //    layout: {
        //        type: 'hbox',
        //        align: 'stretch'
        //    },
        //    overCls: 'over-item-cls',
        //    items: containerItems3
        //};
        //
        //var borderlayerItems = [{
        //    text: 'Africa',
        //    name: 'africa',
        //    menu: {
        //        defaults: {
        //            checked: false,
        //            hideOnClick: false,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //
        //        items: AfricaMenuItems
        //        //    [{
        //        //    xtype: 'checkbox',
        //        //    boxLabel: esapp.Utils.getTranslation('adminlevel0'), // 'Africa level 0',
        //        //    //text: 'Administative level 0',
        //        //    name: 'admin0',
        //        //    level: 'admin0',
        //        //    geojsonfile: 'AFR_0_g2015_2014.geojson',  // 'AFR_G2014_2013_0.geojson', //
        //        //    linecolor: '#319FD3',    // rgb(49, 159, 211)  or like in EMMA rgb(255, 0, 255)
        //        //    layerorderidx: 4,
        //        //    handler: 'addVectorLayer'
        //        //}, {
        //        //    xtype: 'checkbox',
        //        //    boxLabel: esapp.Utils.getTranslation('adminlevel1'), // 'Africa level 1',
        //        //    //text: 'Administative level 1',
        //        //    name: 'admin1',
        //        //    level: 'admin1',
        //        //    geojsonfile: 'AFR_1_g2015_2014.geojson',  // 'AFR_G2014_2013_0.geojson',  //
        //        //    linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',    // rgb(255, 204, 0)
        //        //    layerorderidx: 3,
        //        //    handler: 'addVectorLayer'
        //        //}, {
        //        //    xtype: 'checkbox',
        //        //    boxLabel: esapp.Utils.getTranslation('adminlevel2'), // 'Africa level 2',
        //        //    //text: 'Administative level 1',
        //        //    name: 'admin2',
        //        //    level: 'admin2',
        //        //    geojsonfile: 'AFR_2_g2015_2014.geojson',    // 'AFR_2_g2015_2014_singlepart.geojson',       // 'AFR_G2014_2013_2.geojson',
        //        //    linecolor: '#ffcc99',    // rgb(255, 204, 153)
        //        //    layerorderidx: 1,
        //        //    handler: 'addVectorLayer'
        //        //}]
        //    }
        //}, {
        //    text: 'AGRHYMET',
        //    name: 'agrhymet',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'agrhymet0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_CRA_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'agrhymet1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_CRA_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'agrhymet2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_CRA_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}, {
        //    text: 'BDMS',
        //    name: 'bdms',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'bdms0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_BDMS_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'bdms1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_BDMS_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'bdms2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_BDMS_2_g2015_2014.geojson',    // 'RIC_BDMS_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}, {
        //    text: 'CICOS',
        //    name: 'cicos',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'cicos0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_CICOS_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'cicos1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_CICOS_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'cicos2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_CICOS_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}, {
        //    text: 'ICPAC',
        //    name: 'icpac',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'icpac0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_ICPAC_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'icpac1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_ICPAC_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'icpac2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_ICPAC_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}, {
        //    text: 'MOI',
        //    name: 'moi',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'MOI ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'moi0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_MOI_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'MOI ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'moi1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_MOI_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'MOI ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'moi2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_MOI_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}, {
        //    text: 'University of Ghana',
        //    name: 'UoG',
        //    menu: {
        //        //hideOnClick: true,
        //        defaults: {
        //            checked: false,
        //            hideOnClick: true,
        //            showSeparator: false,
        //            cls: "x-menu-no-icon",
        //            style: {
        //                'margin-left': '5px'
        //            }
        //        },
        //        items: [{
        //            xtype: 'checkbox',
        //            boxLabel: 'UoG ' + esapp.Utils.getTranslation('level0'), // level 0',
        //            name: 'UoG0',
        //            level: 'admin0',
        //            geojsonfile: 'RIC_UOG_0_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#319FD3',
        //            layerorderidx: 4,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'UoG ' + esapp.Utils.getTranslation('level1'), // level 0',
        //            name: 'UoG1',
        //            level: 'admin1',
        //            geojsonfile: 'RIC_UOG_1_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //            layerorderidx: 3,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }, {
        //            xtype: 'checkbox',
        //            boxLabel: 'UoG ' + esapp.Utils.getTranslation('level2'), // level 0',
        //            name: 'UoG2',
        //            level: 'admin2',
        //            geojsonfile: 'RIC_UOG_2_g2015_2014.geojson',
        //            //checked: false,
        //            linecolor: '#000',   // '#ffcc99',
        //            layerorderidx: 2,
        //            //showSeparator: false,
        //            //cls: "x-menu-no-icon",
        //            handler: 'addVectorLayer'
        //        }]
        //    }
        //}];

        var borderVectorLayerItems = this.createLayersMenuItems('border');
        var marineVectorLayerMenuItems = this.createLayersMenuItems('marine');
        var otherVectorLayerMenuItems = this.createLayersMenuItems('other');

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
                    text: esapp.Utils.getTranslation('marinevectorlayers'),   // 'Marine vector layers',
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

        //var layersmenubutton = {
        //        xtype: 'button',
        //        //text: 'Add Layer',
        //        name:'vbtn-'+me.id,
        //        iconCls: 'layer-vector-add', // 'layers'
        //        scale: 'medium',
        //        //width: 100,
        //        //margin: '0 0 10 0',
        //        floating: false,  // usually you want this set to True (default)
        //        collapseDirection: 'left',
        //        menu: {
        //            hideOnClick: true,
        //            iconAlign: '',
        //            defaults: {
        //                hideOnClick: true,
        //                iconAlign: ''
        //            },
        //            items: [{
        //                text: esapp.Utils.getTranslation('borderlayers'),   // 'Border layers (FAO Gaul 2015)',
        //                name: 'gaul2015',
        //                iconCls: 'edit16',  // 'editvectordrawproperties', // 'layers'
        //                tooltip: 'Edit draw properties of the administrative levels.',
        //                scale: 'small',
        //                floating: false,
        //                collapseDirection: 'left',
        //                handler: 'editDrawPropertiesAdminLevels',
        //                menu: {
        //                    //hideOnClick: true,
        //                    //showSeparator : false,
        //                    defaults: {
        //                        hideOnClick: true,
        //                        cls: "x-menu-no-icon",
        //                        scale: 'medium',
        //                        floating: false,
        //                        collapseDirection: 'left'
        //                    },
        //                    //style: {
        //                    //    'margin-left': '0px'
        //                    //},
        //                    items: [{
        //                        text: 'Africa',
        //                        name: 'africa',
        //                        //cls: "x-menu-no-icon",
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: esapp.Utils.getTranslation('adminlevel0'), // 'Africa level 0',
        //                                //text: 'Administative level 0',
        //                                name: 'admin0',
        //                                level: 'admin0',
        //                                geojsonfile: 'AFR_0_g2015_2014.geojson',  // 'AFR_G2014_2013_0.geojson', //
        //                                //checked: false,
        //                                linecolor: '#319FD3',    // rgb(49, 159, 211)  or like in EMMA rgb(255, 0, 255)
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                //hideOnClick: true,
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: esapp.Utils.getTranslation('adminlevel1'), // 'Africa level 1',
        //                                //text: 'Administative level 1',
        //                                name: 'admin1',
        //                                level: 'admin1',
        //                                geojsonfile: 'AFR_1_g2015_2014.geojson',  // 'AFR_G2014_2013_0.geojson',  //
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',    // rgb(255, 204, 0)
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: esapp.Utils.getTranslation('adminlevel2'), // 'Africa level 2',
        //                                //text: 'Administative level 1',
        //                                name: 'admin2',
        //                                level: 'admin2',
        //                                geojsonfile: 'AFR_2_g2015_2014.geojson',    // 'AFR_2_g2015_2014_singlepart.geojson',       // 'AFR_G2014_2013_2.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc99',    // rgb(255, 204, 153)
        //                                layerorderidx: 1,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                        //}, {
        //                        //    text: 'ACMAD',
        //                        //    name: 'acmad',
        //                        //    //iconCls: 'layer-vector-add', // 'layers'
        //                        //    scale: 'medium',
        //                        //    floating: false,
        //                        //    collapseDirection: 'left',
        //                        //    menu: {
        //                        //        hideOnClick: true,
        //                        //        defaults: {
        //                        //            hideOnClick: true
        //                        //        },
        //                        //        style: {
        //                        //            'margin-left': '0px'
        //                        //        },
        //                        //        items: [{
        //                        //            xtype: 'checkbox',
        //                        //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level0'), // level 0',
        //                        //            name: 'acmad0',
        //                        //            level: 'admin0',
        //                        //            geojsonfile: 'AFR_0_g2015_2014.geojson',
        //                        //            checked: false,
        //                        //            linecolor: '#319FD3',
        //                        //            layerorderidx: 3,
        //                        //            showSeparator: false,
        //                        //            cls: "x-menu-no-icon",
        //                        //            handler: 'addVectorLayer'
        //                        //        }, {
        //                        //            xtype: 'checkbox',
        //                        //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level1'), // level 0',
        //                        //            name: 'acmad1',
        //                        //            level: 'admin1',
        //                        //            geojsonfile: 'AFR_1_g2015_2014.geojsonn',
        //                        //            checked: false,
        //                        //            linecolor: '#ffcc00',
        //                        //            layerorderidx: 2,
        //                        //            showSeparator: false,
        //                        //            cls: "x-menu-no-icon",
        //                        //            handler: 'addVectorLayer'
        //                        //        }, {
        //                        //            xtype: 'checkbox',
        //                        //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level2'), // level 0',
        //                        //            name: 'acmad2',
        //                        //            level: 'admin2',
        //                        //            geojsonfile: 'AFR_2_g2015_2014.geojson',
        //                        //            checked: false,
        //                        //            linecolor: '#ffcc99',
        //                        //            layerorderidx: 1,
        //                        //            showSeparator: false,
        //                        //            cls: "x-menu-no-icon",
        //                        //            handler: 'addVectorLayer'
        //                        //        }]
        //                        //    }
        //                    }, {
        //                        text: 'AGRHYMET',
        //                        name: 'agrhymet',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'agrhymet0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_CRA_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'agrhymet1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_CRA_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'AGRHYMET ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'agrhymet2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_CRA_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }, {
        //                        text: 'BDMS',
        //                        name: 'bdms',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'bdms0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_BDMS_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'bdms1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_BDMS_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'BDMS ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'bdms2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_BDMS_2_g2015_2014.geojson',    // 'RIC_BDMS_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }, {
        //                        text: 'CICOS',
        //                        name: 'cicos',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'cicos0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_CICOS_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'cicos1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_CICOS_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'CICOS ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'cicos2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_CICOS_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }, {
        //                        text: 'ICPAC',
        //                        name: 'icpac',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'icpac0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_ICPAC_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'icpac1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_ICPAC_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'ICPAC ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'icpac2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_ICPAC_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }, {
        //                        text: 'MOI',
        //                        name: 'moi',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'MOI ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'moi0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_MOI_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'MOI ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'moi1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_MOI_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'MOI ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'moi2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_MOI_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }, {
        //                        text: 'University of Ghana',
        //                        name: 'UoG',
        //                        //iconCls: 'layer-vector-add', // 'layers'
        //                        //scale: 'medium',
        //                        //floating: false,
        //                        //collapseDirection: 'left',
        //                        menu: {
        //                            //hideOnClick: true,
        //                            defaults: {
        //                                checked: false,
        //                                hideOnClick: true,
        //                                showSeparator: false,
        //                                cls: "x-menu-no-icon",
        //                                style: {
        //                                    'margin-left': '5px'
        //                                }
        //                            },
        //                            items: [{
        //                                xtype: 'checkbox',
        //                                boxLabel: 'UoG ' + esapp.Utils.getTranslation('level0'), // level 0',
        //                                name: 'UoG0',
        //                                level: 'admin0',
        //                                geojsonfile: 'RIC_UOG_0_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#319FD3',
        //                                layerorderidx: 4,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'UoG ' + esapp.Utils.getTranslation('level1'), // level 0',
        //                                name: 'UoG1',
        //                                level: 'admin1',
        //                                geojsonfile: 'RIC_UOG_1_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#ffcc00',   // '#9e9a9a',  // '#ffcc00',
        //                                layerorderidx: 3,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }, {
        //                                xtype: 'checkbox',
        //                                boxLabel: 'UoG ' + esapp.Utils.getTranslation('level2'), // level 0',
        //                                name: 'UoG2',
        //                                level: 'admin2',
        //                                geojsonfile: 'RIC_UOG_2_g2015_2014.geojson',
        //                                //checked: false,
        //                                linecolor: '#000',   // '#ffcc99',
        //                                layerorderidx: 2,
        //                                //showSeparator: false,
        //                                //cls: "x-menu-no-icon",
        //                                handler: 'addVectorLayer'
        //                            }]
        //                        }
        //                    }]
        //                }
        //            },{
        //                text: esapp.Utils.getTranslation('marinevectorlayers'),   // 'Marine vector layers',
        //                name: 'marine',
        //                //iconCls: 'layer-vector-add', // 'layers'
        //                scale: 'medium',
        //                floating: false,
        //                collapseDirection: 'left',
        //                menu: {
        //                    //hideOnClick: true,
        //                    defaults: {
        //                        hideOnClick: true
        //                    },
        //                    //style: {
        //                    //    'margin-left': '0px'
        //                    //},
        //                    plain: true,
        //
        //                    items: marineVectorlayersMenuItems
        //
        //                    //items: [
        //                    //    {
        //                    //    xtype: 'checkbox',
        //                    //    boxLabel: esapp.Utils.getTranslation('fishingareas'), // 'Fishing Areas',
        //                    //    name: 'fisharea',
        //                    //    level: 'fisharea',
        //                    //    geojsonfile: 'AFR_MARINE/AFR_FAO_FISH_AREA.geojson',
        //                    //    checked: false,
        //                    //    linecolor: '#000',
        //                    //    layerorderidx: 1,
        //                    //    showSeparator: false,
        //                    //    cls: "x-menu-no-icon",
        //                    //    hideOnClick: true,
        //                    //    handler: 'addVectorLayer'
        //                    //}, {
        //                    //    xtype: 'checkbox',
        //                    //    boxLabel: esapp.Utils.getTranslation('sea_exclusive_economic_zone'), // 'Sea Exclusive economic zone (EEZ)',
        //                    //    name: 'eez',
        //                    //    level: 'eez',
        //                    //    geojsonfile: 'AFR_MARINE/AFR_EEZ_IHO_union_v2.geojson',
        //                    //    checked: false,
        //                    //    linecolor: '#000',
        //                    //    layerorderidx: 1,
        //                    //    showSeparator: false,
        //                    //    cls: "x-menu-no-icon",
        //                    //    hideOnClick: true,
        //                    //    handler: 'addVectorLayer'
        //                    //}]
        //                }
        //            }, paVectorlayerMenuItem
        //            //{
        //            //    xtype: 'checkbox',
        //            //    boxLabel: esapp.Utils.getTranslation('protectedareas'), // 'Protected areas',
        //            //    name: 'protectedareas',
        //            //    level: 'protectedareas',
        //            //    geojsonfile: 'AFR_PA/AFR_PA_ID.geojson',
        //            //    checked: false,
        //            //    linecolor: '#000',
        //            //    layerorderidx: 1,
        //            //    showSeparator: false,
        //            //    cls: "x-menu-no-icon",
        //            //    hideOnClick: true,
        //            //    handler: 'addVectorLayer'
        //            //}
        //            ]
        //        }
        //};
    }
});
