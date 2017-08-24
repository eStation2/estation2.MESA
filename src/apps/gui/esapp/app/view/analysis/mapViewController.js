Ext.define('esapp.view.analysis.mapViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-mapview'

    ,setMapTemplateName: function(){
        var me = this;
        var newMapTemplateName = '';

        if (me.getView().isNewTemplate){
            // open dialog asking to give a unique map template name
            // If Save as... then the mapView has a templatename which will be proposed
            // Ext.MessageBox.prompt( title , message , [fn] , [scope] , [multiline] , [value] )
            if (esapp.Utils.objectExists(me.getView().templatename) && me.getView().templatename != ''){
                newMapTemplateName = me.getView().templatename + ' - copy';
            }
            Ext.MessageBox.prompt(esapp.Utils.getTranslation('map_tpl_name'), esapp.Utils.getTranslation('map_tpl_save_message') + ':', function(btn, text){   // 'Map Template Name'   'Please give a unique name for the new map template'
                if (btn == 'ok'){
                    // process text value and close...
                    me.getView().templatename = text;
                    me.saveMapTemplate();
                    if (me.getView().getTitle() != null){
                        Ext.fly('mapview_title_templatename_' + me.getView().id).dom.innerHTML = text;
                        //me.getView().setTitle('<div class="map-templatename">' + text + '</div>' + me.getView().getTitle());
                    }
                    me.getView().isTemplate = true;
                }
            }, this, false, newMapTemplateName);
        }
        else {
            me.saveMapTemplate();
        }
    }

    ,saveMapTemplate: function(){
        var me = this.getView(),
            mapLegendObj = me.lookupReference('product-legend_' + me.id),
            titleObj = me.lookupReference('title_obj_' + me.id),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logoObj = me.lookupReference('logo_obj_' + me.id),
            scalelineObj = me.lookupReference('scale-line_' + me.id),
            mapObjectToggleBtn = me.lookupReference('objectsbtn_'+ me.id.replace(/-/g,'_')),
            mapLegendToggleBtn = me.lookupReference('legendbtn_' + me.id.replace(/-/g, '_')),
            mapviewSize = me.getSize().width + "," + me.getSize().height;

        var mapTemplate = {
            newtemplate: me.isNewTemplate,
            userid: esapp.getUser().userid,
            //isTemplate: true,
            templatename: me.templatename,
            mapviewPosition: me.getPosition(true).toString(),
            mapviewSize: mapviewSize,
            productcode: me.productcode,
            subproductcode: me.subproductcode,
            productversion: me.productversion,
            mapsetcode: me.mapsetcode,
            legendid: me.legendid,
            legendlayout:  mapLegendObj.legendLayout,
            legendObjPosition: me.productcode != '' && mapLegendObj.html != '' ? mapLegendObj.getPosition(true).toString() : mapLegendObj.legendPosition.toString(),
            showlegend: mapLegendToggleBtn.pressed,
            titleObjPosition: titleObj.rendered ? titleObj.getPosition(true).toString() : titleObj.titlePosition.toString(),
            titleObjContent: titleObj.tpl.html,
            disclaimerObjPosition: disclaimerObj.rendered ? disclaimerObj.getPosition(true).toString() : disclaimerObj.disclaimerPosition.toString(),
            disclaimerObjContent: disclaimerObj.getContent(),
            logosObjPosition: logoObj.rendered ? logoObj.getPosition(true).toString() : logoObj.logoPosition.toString(),
            logosObjContent: Ext.encode(logoObj.getLogoData()),
            showObjects: mapObjectToggleBtn.pressed,
            scalelineObjPosition: scalelineObj.getPosition(true).toString(),
            vectorLayers: '',
            outmaskFeature: '',
            auto_open: false
        }
        //console.info(mapTemplate);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/savemaptemplate',
            params: mapTemplate,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                Ext.toast({html: responseJSON.message, title: esapp.Utils.getTranslation('save_map_tpl'), width: 300, align: 't'});     // "Save Map template"
            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (result, request) {
                Ext.toast({html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_map_tpl'), width: 300, align: 't'});     // "ERROR saving the Map template"
            }
        });

        me.isNewTemplate = false;
    }

    ,play: function(){
        var me = this.getView();
        var dates = [];
        var addDate = false;
        var timelinechart = me.lookupReference('time-line-chart' + me.id).timelinechart;
        // Get from and to dates from timeline rangeSelector input fields
        var startDate = Highcharts.dateFormat('%Y%m%d', timelinechart.rangeSelector.minInput.HCTime);
        var endDate = Highcharts.dateFormat('%Y%m%d', timelinechart.rangeSelector.maxInput.HCTime);
        //var zoomStartEpochTime = chart.xAxis[0].getExtremes().min;
        //var zoomEndEpochTime = chart.xAxis[0].getExtremes().max;
        //me.task = null;

        Ext.getCmp('playBtn_' + me.id).hide();
        Ext.getCmp('stopBtn_' + me.id).show();

        // Get all the dates in the range
        for (var i = 0; i < me.timeline.length; i += 1) {
            if (me.timeline[i]['date'] >= String(startDate)) addDate = true;
            if (me.timeline[i]['date'] >= String(endDate)) addDate = false;
            if (addDate) {
                dates.push(
                    me.timeline[i]['date']
                );
            }
        }
        //console.info(dates);
        var counter = 0,
            runner = new Ext.util.TaskRunner(),
            interval = Ext.getCmp('playInterval_' + me.id).getValue() || 2500;

        me.task = runner.newTask({
            run: function() {
                //console.info('refreshing product layer with new date');
                me.productdate = dates[counter];
                if (counter == dates.length -1) counter = 0;
                else counter +=1;
                me.getController().updateProductLayer();
                me.productdate_linked = null;
                me.getController().updateProductInOtherMapViews();

            },
            interval: interval
        });
        me.task.start();
    }

    ,pause: function(){
        var me = this;
    }

    ,stop: function(){
        var me = this.getView();
        // Stop the while loop in the play function
        Ext.getCmp('playBtn_' + me.id).show();
        Ext.getCmp('stopBtn_' + me.id).hide();
        //me.task.stop();
        me.task.destroy();
        me.task = null;
    }

    ,refreshTitleData: function(){
        var me = this.getView();
        var pattern = /(\d{4})(\d{2})(\d{2})/;
        var mydate = me.productdate.replace(pattern,'$3-$2-$1');
        var mapTitleObj = Ext.getCmp('title_obj_' + me.id);

        if (me.date_format == 'MMDD') {
            mydate = new Date(me.productdate.replace(pattern,'$2/$3/$1'));
            mydate.setHours(mydate.getHours()+5);   // add some hours so otherwise Highcharts.dateFormat assigns a day before if the hour is 00:00.
            mydate = Highcharts.dateFormat('%d %b', mydate, true);
        }

        me.setTitleData({
            'selected_area': me.selectedarea,
            'product_name': me.productname,
            'product_date': mydate
        });

        mapTitleObj.changesmade =true;
        mapTitleObj.fireEvent('refreshimage');
    }

    ,addProductLayer: function(productcode, productversion, mapsetcode, subproductcode, legendid, legendHTML, legendHTMLVertical, productname, date_format, frequency_id) {
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
        //me.getView().legendHTML = legendHTML;
        //me.getView().legendHTMLVertical = legendHTMLVertical;
        me.getView().date_format = date_format;
        me.getView().frequency_id = frequency_id;

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

                me.getView().timeline = responseJSON.timeline;

                //console.info(me.lookupReference('time-line-chart' + me.getView().id));
                me.lookupReference('time-line-chart' + me.getView().id).product_date_format = date_format;
                me.lookupReference('time-line-chart' + me.getView().id).createTimeLineChart();

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
                                    me.getView().productdate_linked = null;
                                    me.getView().getController().updateProductLayer();
                                    me.getView().getController().updateProductInOtherMapViews();
                                    //var outmask = me.lookupReference('outmaskbtn_'+ me.getView().id.replace(/-/g,'_')).pressed;
                                    //if (outmask){
                                    //    me.getView().getController().outmaskFeature();
                                    //}
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

                // Set the MapView window title to the selected product and date
                var versiontitle = '';
                if (productversion !== 'undefined'){
                    versiontitle = ' <b class="smalltext">' + productversion + '</b>';
                }
                var mapsetcodeHTML = ' - <b class="smalltext">' + me.getView().mapsetcode + '</b>';

                var pattern = /(\d{4})(\d{2})(\d{2})/;
                //me.getView().productdate = me.getView().productdate.replace(pattern,'$3-$2-$1');
                //var dt = new Date(me.getView().productdate.replace(pattern,'$3-$2-$1'));
                var productdateHTML = ' - <b class="" style="color: #ffffff; font-size: 20px;">' + me.getView().productdate.replace(pattern,'$3-$2-$1') + '</b>';
                if (date_format == 'MMDD') {
                    var mydate = new Date(me.getView().productdate.replace(pattern,'$2/$3/$1'));
                    mydate.setHours(mydate.getHours()+5);   // add some hours so otherwise Highcharts.dateFormat assigns a day before if the hour is 00:00.
                    productdateHTML = ' - <b class="" style="color: #ffffff; font-size: 20px;">' + Highcharts.dateFormat('%d %b', mydate, true) + '</b>';
                }
                var mapviewTitle = productname + versiontitle + mapsetcodeHTML + productdateHTML;

                Ext.fly('mapview_title_productname_' + me.getView().id).dom.innerHTML = mapviewTitle;
                //me.getView().setTitle(mapviewTitle);
                me.getView().getController().refreshTitleData();


                // Set the timeline data, its rangeselector selected button and show product time line
                var mapviewtimeline = me.lookupReference('product-time-line_' + me.getView().id);
                var mapview_timelinechart_container = me.lookupReference('time-line-chart' + me.getView().id);
                mapview_timelinechart_container.timelinechart.series[0].setData(data, false);
                // console.info(mapview_timelinechart_container.timelinechart);
                // console.info(data);
                mapviewtimeline.show();
                mapviewtimeline.fireEvent('expand');
                if (frequency_id == 'e1day'){
                    mapview_timelinechart_container.timelinechart.rangeSelector.setSelected(1);
                    mapview_timelinechart_container.timelinechart.rangeSelector.clickButton(1); // setSelected(2);
                    // mapview_timelinechart_container.timelinechart.rangeSelector.updateButtonStates();
                }
                // else {
                //     mapview_timelinechart_container.timelinechart.rangeSelector.setSelected(4);
                //     mapview_timelinechart_container.timelinechart.rangeSelector.clickButton(4);
                // }

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

        me.getView().productlayer = new ol.layer.Tile({       // ol.layer.Tile   or  ol.layer.Image
            title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
            layer_id: 'productlayer',
            layerorderidx: 0,
            layertype: 'raster',
            type: 'base',
            visible: true,
            source: new ol.source.TileWMS({    // ol.source.TileWMS or ol.source.ImageWMS
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
        var mapLegendObj = me.lookupReference('product-legend_' + me.getView().id);
        mapLegendObj.legendHTML = legendHTML;
        mapLegendObj.legendHTMLVertical = legendHTMLVertical;
        mapLegendObj.hide();    // Hide first to always trigger the show event!
        mapLegendObj.show();
        // mapLegendObj.fireEvent('show');

        var maplegend_togglebtn = me.lookupReference('legendbtn_' + me.getView().id.replace(/-/g, '_')); //  + me.getView().id);
        maplegend_togglebtn.show();

        var opacityslider_togglebtn = me.lookupReference('opacityslider_' + me.getView().id.replace(/-/g, '_'));
        opacityslider_togglebtn.show();
        // opacityslider_togglebtn.setPosition(me.getView().getWidth() - 48, 150);


        if (mapLegendObj.showlegend ) {
            //maplegend_togglebtn.toggle();
            maplegend_togglebtn.setPressed(true);
        }

        this.outmaskingPossible();
        //var outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.getView().id.replace(/-/g,'_')); //  + me.getView().id);
        //if (me.getView().getController().outmaskingPossible(me.getView().map)){
        //    outmask_togglebtn.show();
        //}
        //else outmask_togglebtn.hide();

    }

    ,updateProductLayer: function() {
        var me = this.getView();
        var params = {};

        //var outmask = false; // this.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')).pressed;
        //console.info(this.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')));
        //console.info(outmask);
        //console.info(me.selectedfeature);
        //
        //// Does not work passing the WKT. Gives error: 414 Request-URI Too Long
        //// The requested URL's length exceeds the capacity limit for this server.
        //if (outmask && me.selectedfeature){
        //    var wkt = new ol.format.WKT();
        //    var wktstr = wkt.writeFeature(me.selectedfeature);
        //    wktstr = wktstr.replace(/,/g, ', ');  // not a good idea in general
        //    params = {
        //        productcode: me.productcode,
        //        productversion: me.productversion,
        //        subproductcode: me.subproductcode,
        //        mapsetcode: me.mapsetcode,
        //        legendid: me.legendid,
        //        date: me.productdate,
        //        outmask:true,
        //        selectedfeature: wktstr,
        //        'FORMAT': 'image/png'
        //    };
        //}

        if (esapp.Utils.objectExists(me.productdate_linked)){
            var pattern = /(\d{4})(\d{2})(\d{2})/;
            //if (me.date_format == 'MMDD') {
            //    me.productdate_linked = me.productdate_linked.replace(pattern, '$2$3');
            //}

            me.productdate = null;
            for (var i = 0; i < me.timeline.length; i += 1) {
                if (me.timeline[i]['present'] == 'true') {
                    if (me.date_format == 'MMDD') {
                        if (me.timeline[i]['date'].replace(pattern, '$2$3') >= me.productdate_linked.replace(pattern, '$2$3')) {
                            me.productdate = me.timeline[i]['date'];
                            break;
                        }
                    }
                    else if (me.timeline[i]['date'] >= me.productdate_linked) {
                        me.productdate = me.timeline[i]['date'];
                        break;
                    }
                    else if (i == me.timeline.length-1) {
                        me.productdate = me.timeline[i]['date'];
                        break;
                    }
                }
            }
        }

        params = {
            productcode: me.productcode,
            productversion: me.productversion,
            subproductcode: me.subproductcode,
            mapsetcode: me.mapsetcode,
            legendid: me.legendid,
            date: me.productdate,
            'FORMAT': 'image/png'
            //,REASPECT:'TRUE'
        };

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
        //
        //function imagePostFunction(image, src) {
        //    var img = image.getImage();
        //    if (typeof window.btoa === 'function') {
        //      var xhr = new XMLHttpRequest();
        //      //console.log("src",src);
        //      //GET ALL THE PARAMETERS OUT OF THE SOURCE URL
        //      var dataEntries = src.split("&");
        //      var url;
        //      var params = "";
        //      for (var i = 0 ; i< dataEntries.length ; i++){
        //          //console.log("dataEntries[i]",dataEntries[i]);
        //          if (i===0){
        //          url = dataEntries[i];
        //          }
        //          else{
        //          params = params + "&"+dataEntries[i];
        //          }
        //      }
        //      //console.log("params",params);
        //      xhr.open('POST', url, true);
        //
        //      xhr.responseType = 'arraybuffer';
        //      xhr.onload = function(e) {
        //        if (this.status === 200) {
        //          //console.log("this.response",this.response);
        //          var uInt8Array = new Uint8Array(this.response);
        //          var i = uInt8Array.length;
        //          var binaryString = new Array(i);
        //          while (i--) {
        //            binaryString[i] = String.fromCharCode(uInt8Array[i]);
        //          }
        //          var data = binaryString.join('');
        //          var type = xhr.getResponseHeader('content-type');
        //          if (type.indexOf('image') === 0) {
        //            img.src = 'data:' + type + ';base64,' + window.btoa(data);
        //          }
        //        }
        //      };
        //      //SET THE PROPER HEADERS AND FINALLY SEND THE PARAMETERS
        //      xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        //      //xhr.setRequestHeader("Content-length", params.length);
        //      //xhr.setRequestHeader("Connection", "close");
        //      xhr.send(params);
        //    } else {
        //      img.src = src;
        //    }
        //}
        if (me.productdate != null){
            me.productlayer = new ol.layer.Tile({       // ol.layer.Tile   or  ol.layer.Image
                title: esapp.Utils.getTranslation('productlayer'),  // 'Product layer',
                layer_id: 'productlayer',
                layerorderidx: 0,
                layertype: 'raster',
                type: 'base',
                visible: true,
                //maxGetUrlProperty: 10,
                source: new ol.source.TileWMS({     // ol.source.TileWMS or ol.source.ImageWMS
                    url: 'analysis/getproductlayer',
                    crossOrigin: '',  // 'anonymous',
                    wrapX: false,
                    noWrap: true,
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


            var productlayer_idx = me.getController().findlayer(me.map, 'productlayer');
            if (productlayer_idx != -1)
                me.map.getLayers().removeAt(productlayer_idx);
            //me.map.removeLayer(me.map.getLayers().a[0]);
            //me.map.addLayer(me.productlayer);
            me.map.getLayers().insertAt(0, me.productlayer);

            var versiontitle = '';
            if (me.productversion !== 'undefined'){
                versiontitle = ' <b class="smalltext">' + me.productversion + '</b>';
            }

            var mapsetcodeHTML = ' - <b class="smalltext">' + me.mapsetcode + '</b>';

            var pattern = /(\d{4})(\d{2})(\d{2})/;
            //me.productdate = clickeddate.replace(pattern,'$3-$2-$1');
            var productdateHTML = ' - <b class="" style="color: #ffffff; font-size: 20px;">' + me.productdate.replace(pattern,'$3-$2-$1') + '</b>';
            if (me.date_format == 'MMDD') {
                var mydate = new Date(me.productdate.replace(pattern,'$2/$3/$1'));
                mydate.setHours(mydate.getHours()+5);   // add some hours so otherwise Highcharts.dateFormat assigns a day before if the hour is 00:00.
                productdateHTML = ' - <b class="" style="color: #ffffff; font-size: 20px;">' + Highcharts.dateFormat('%d %b', mydate, true) + '</b>';
            }
            //var mapviewTitle = me.productname + versiontitle + ' - <b class="smalltext">' + me.productdate + '</b>';
            var mapviewTitle = me.productname + versiontitle + mapsetcodeHTML + productdateHTML;
            Ext.fly('mapview_title_productname_' + me.id).dom.innerHTML = mapviewTitle;
            //me.setTitle(mapviewTitle);

            me.getController().refreshTitleData();
        }
    }

    ,updateProductInOtherMapViews: function () {
        var me = this.getView();
        var mapViewWindows = Ext.ComponentQuery.query('mapview-window');
        me.productdate_linked = null;

        if (me.link_product_layer){
            Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                //if (me == mapview_window) console.info('this mapview skip');
                if (me != mapview_window && mapview_window.link_product_layer && esapp.Utils.objectExists(mapview_window.productcode)){
                    mapview_window.productdate_linked = me.productdate;
                    mapview_window.getController().updateProductLayer();
                }
            });
        }
    }

    ,redrawTimeLine: function (mapview) {
        var mapviewtimeline = mapview.lookupReference('product-time-line_' + mapview.id);
        var mapview_timelinechart_container = mapview.lookupReference('time-line-chart' + mapview.id);
        //var timeline_container_size = mapviewtimeline.getSize();

        if (mapviewtimeline.hidden == false){
            // console.info('mapviewtimeline.hidden=false');
            // mapviewtimeline.setHeight(145);
            mapview_timelinechart_container.timelinechart.container.width = mapviewtimeline.getSize().width;
            mapview_timelinechart_container.timelinechart.setSize(mapviewtimeline.getSize().width-35, mapviewtimeline.getSize().height, false);
            //mapview_timelinechart_container.timelinechart.reflow();
            mapview_timelinechart_container.timelinechart.redraw();
            mapview_timelinechart_container.updateLayout();

            mapview.map.setSize([document.getElementById(mapview.id + "-body").offsetWidth, document.getElementById(mapview.id + "-body").offsetHeight+130]);
        }
        // else {
        //     console.info('mapviewtimeline.hidden=true');
        //     mapview.map.setSize([document.getElementById(mapview.id + "-body").offsetWidth, document.getElementById(mapview.id + "-body").offsetHeight-130]);
        // }
    }

    ,saveMap: function(btn, event) {
        var me = this.getView(),
            filename = '',
            mapviewwin = btn.up().up(),
            mapimage_url = '',

            ObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_')),

            legendObj = me.lookupReference('product-legend_' + me.id),
            titleObj = me.lookupReference('title_obj_' + me.id),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logosObj = me.lookupReference('logo_obj_' + me.id),
            scalelineObj = me.lookupReference('scale-line_' + me.id),

            legendObjPosition = [],
            titleObjPosition = [],
            disclaimerObjPosition = [],
            logosObjPosition = [],
            scalelineObjPosition = []
            //titleObjDomClone = Ext.clone(titleObj.getEl().dom),
            //disclaimerObjDomClone = Ext.clone(disclaimerObj.getEl().dom),
            //logosObjDomClone = Ext.clone(logosObj.getEl().dom)
        ;

        scalelineObj.fireEvent('refreshimage');
        scalelineObjPosition = scalelineObj.getPosition(true);

        filename = me.productname + " " + me.productversion + " " + me.mapsetcode + " " + me.productdate
        if (filename == null || filename.trim() == '')
            filename = 'eStation2map.png'
        else {
            filename = filename.replace(/<\/?[^>]+(>|$)/g, "");
            filename = filename + '.png';
        }

        if (!legendObj.hidden) {
            // legendObj.fireEvent('refreshimage');
            legendObjPosition = legendObj.getPosition(true);
        }
        if (ObjectToggleBtn.pressed) {
            titleObjPosition = titleObj.getPosition(true);
            disclaimerObjPosition = disclaimerObj.getPosition(true);
            logosObjPosition = logosObj.getPosition(true);
        }
        // console.info('legendObjPosition: ' + legendObjPosition);
        // console.info('titleObjPosition: ' + titleObjPosition);
        // console.info('disclaimerObjPosition: ' + disclaimerObjPosition);
        // console.info('logosObjPosition: ' + logosObjPosition);

        var task = new Ext.util.DelayedTask(function() {
            me.map.once('postcompose', function(event) {
                var canvas = event.context.canvas,
                    context = canvas.getContext('2d');
                if (!legendObj.hidden) {
                    context.drawImage(legendObj.legendHTML_ImageObj, legendObjPosition[0], legendObjPosition[1]);
                }

                if (ObjectToggleBtn.pressed) {
                    context.drawImage(titleObj.title_ImageObj, titleObjPosition[0], titleObjPosition[1]);
                    context.drawImage(disclaimerObj.disclaimer_ImageObj, disclaimerObjPosition[0], disclaimerObjPosition[1]);
                    context.drawImage(logosObj.logos_ImageObj, logosObjPosition[0], logosObjPosition[1]);
                }

                context.drawImage(scalelineObj.scaleline_ImageObj, scalelineObjPosition[0], scalelineObjPosition[1]);

                mapimage_url = canvas.toDataURL('image/png');

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

            });
            me.map.renderSync();


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

        });
        task.delay(750);

        //if(typeof Promise !== "undefined" && Promise.toString().indexOf("[native code]") !== -1){
        //   console.info('Browser supports Promise natively!');
        //}
        //else {
        //   console.info('NOT SUPPORT OF Promise natively!');
        //}
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

    ,toggleDateLink: function(btn, event) {
        var mapviewwin = this.getView();

        if (btn.pressed) {
            mapviewwin.link_product_layer = false;
            btn.setIconCls('calendar_unlinked');
        }
        else {
            mapviewwin.link_product_layer = true;
            btn.setIconCls('calendar_linked');
        }
    }

    ,toggleLink: function(btn, event) {
        var mapviewwin = btn.up().up();

        if (btn.pressed) {
            mapviewwin.map.setView(mapviewwin.mapView);
            mapviewwin.lookupReference('zoomfactorslider_' + mapviewwin.id.replace(/-/g,'_')).setValue(mapviewwin.zoomFactorSliderValue);
            //btn.setText('Link');
            //btn.setIconCls('link');
            btn.setIconCls('fa fa-chain-broken fa-2x red');
        }
        else {
            mapviewwin.map.setView(mapviewwin.up().commonMapView);
            mapviewwin.lookupReference('zoomfactorslider_' + mapviewwin.id.replace(/-/g,'_')).setValue(mapviewwin.up().zoomFactorSliderValue);
            //btn.setText('Unlink');
            //btn.setIconCls('unlink');
            btn.setIconCls('fa fa-link fa-2x gray');
        }
    }

    ,toggleLegend: function(btn, event) {
        var mapviewwin = btn.up().up();
        //var maplegendpanel = mapviewwin.lookupReference('product-legend_panel_' + mapviewwin.id);
        var mapLegendObj = mapviewwin.lookupReference('product-legend_' + mapviewwin.id);

        if (btn.pressed) {
            mapLegendObj.showlegend = true;
            mapLegendObj.show();
        }
        else {
            mapLegendObj.legendPosition = mapLegendObj.getPosition(true);
            mapLegendObj.showlegend = false;
            mapLegendObj.hide();
        }
    }

    ,toggleObjects: function(btn, event) {
        var mapviewwin = btn.up().up(),
            titleObj = mapviewwin.lookupReference('title_obj_' + mapviewwin.id),
            disclaimerObj = mapviewwin.lookupReference('disclaimer_obj_' + mapviewwin.id),
            logoObj = mapviewwin.lookupReference('logo_obj_' + mapviewwin.id);

        if (btn.pressed) {
            titleObj.show();
            disclaimerObj.show();
            logoObj.show();
            btn.setStyle({ color: 'green' });
        }
        else {
            titleObj.titlePosition = titleObj.getPosition(true);
            disclaimerObj.disclaimerPosition = disclaimerObj.getPosition(true);
            logoObj.logoPosition = logoObj.getPosition(true);
            titleObj.hide();
            disclaimerObj.hide();
            logoObj.hide();
            btn.setStyle({ color: 'black' });
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

    ,toggleDrawGeometry: function(btn, event) {
        var mapviewwin = btn.up().up();

        if (btn.pressed) {
            mapviewwin.map.removeInteraction(mapviewwin.draw);
            mapviewwin.getController().addDrawInteraction();
            btn.setIconCls('polygon');
            // btn.showMenu();
        }
        else {
            mapviewwin.map.removeInteraction(mapviewwin.draw);
            btn.setIconCls('polygon-gray');
            btn.hideMenu();
        }
        mapviewwin.getController().outmaskingPossible();
    }

    ,addDrawInteraction: function(geometrytype){
        var me = this.getView();
        var value = Ext.getCmp('geometrytypes' + me.id).value;
        me.draw = null;

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
                maxPoints = 2;
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
                //features: me.drawfeatures,
                type: /** @type {ol.geom.GeometryType} */ (value),
            geometryFunction: geometryFunction,
                maxPoints: maxPoints
            });
            me.map.addInteraction(me.draw);



            //var overlayStyle = (function() {
            //    var styles = {};
            //    styles['Polygon'] = [
            //      new ol.style.Style({
            //        fill: new ol.style.Fill({
            //          color: 'Transparent'  // [255, 255, 255, 0.5]
            //        })
            //      }),
            //      new ol.style.Style({
            //        stroke: new ol.style.Stroke({
            //          color: [255, 0, 0, 1],
            //          width: 3
            //        })
            //      }),
            //      new ol.style.Style({
            //        stroke: new ol.style.Stroke({
            //          color: [0, 153, 255, 1],
            //          width: 3
            //        })
            //      })
            //    ];
            //    styles['MultiPolygon'] = styles['Polygon'];
            //
            //    styles['LineString'] = [
            //      new ol.style.Style({
            //        stroke: new ol.style.Stroke({
            //          color: [255, 0, 0, 1],
            //          width: 3
            //        })
            //      }),
            //      new ol.style.Style({
            //        stroke: new ol.style.Stroke({
            //          color: [0, 153, 255, 1],
            //          width: 3
            //        })
            //      })
            //    ];
            //    styles['MultiLineString'] = styles['LineString'];
            //
            //    styles['Point'] = [
            //      new ol.style.Style({
            //        image: new ol.style.Circle({
            //          radius: 7,
            //          fill: new ol.style.Fill({
            //            color: [0, 153, 255, 1]
            //          }),
            //          stroke: new ol.style.Stroke({
            //            color: [255, 0, 0, 0.75],
            //            width: 1.5
            //          })
            //        }),
            //        zIndex: 100000
            //      })
            //    ];
            //    styles['MultiPoint'] = styles['Point'];
            //
            //    styles['GeometryCollection'] = styles['Polygon'].concat(styles['Point']);
            //
            //    return function(feature) {
            //      return styles[feature.getGeometry().getType()];
            //    };
            //})();

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

    ,outmaskingPossible: function (){
        var me = this.getView(),
            possible = false,
            productlayerexists = false,
            vectorlayerexists = false,
            outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_')) //  + me.getView().id);
        ;

        me.map.getLayers().getArray().forEach(function (layer,idx){
            var layer_type = layer.get("layertype");
            //console.info(layer.get("layer_id"));
            //console.info(layer.get("layertype"));
            //console.info(layer);
            if(layer_type == 'raster'){
              productlayerexists = true;
            }
            else if(layer_type == 'vector'){
              vectorlayerexists = true;
            }
            else if(layer_type == 'drawvector' && me.drawvectorlayer.getSource().getFeatures().length > 0){
              vectorlayerexists = true;
            }
        });
        if (productlayerexists && vectorlayerexists)
            possible = true;

        //return possible;

        if (possible){
            outmask_togglebtn.show();
        }
        else {
            outmask_togglebtn.hide();
            this.removeOutmaskLayer();
        }
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
        var me = this.getView();

        function isFunction(possibleFunction) {
          return typeof(possibleFunction) === typeof(Function);
        }

        if ( Ext.isDefined(me.selectedfeature) && me.selectedfeature !== null && !me.selectedfeature.getGeometry().getType().match("Point|LineString")){
            var selectedFeatureToOutmask = me.selectedfeature;
            var linearRing = null;

            this.removeOutmaskLayer();

            var vecSource = new ol.source.Vector({
                wrapX: false,
                noWrap: true
            });
            var outmaskStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'rgba(255, 255, 255, 1)',
                    width: 2
                }),
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 1)'
                })
            });

            var vectorLayer = new ol.layer.Vector({
                    name: "Outmask",
                    source: vecSource,
                    style: outmaskStyle
                });

            //var extentEGAD = [20.99, -6.00, 52.00, 24.00];
            //var extentAfrica = [-27,-36,61,39];
            var extentWorld = [-165,-60,165,60];
            var outmaskPolygon = ol.geom.Polygon.fromExtent(extentWorld);

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

            me.map.addLayer(vectorLayer);

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

            //if (me.getController().outmaskingPossible(me.map)){
            //    outmask_togglebtn.show();
            //}
            //else outmask_togglebtn.hide();
        }
    }

    ,addVectorLayerToMapView: function(layerrecord){
        var me = this.getView();
        var namefield = layerrecord.get('feature_display_column').split(',')[0]
            ,vectorlayer_idx = -1
            ,layertitle = esapp.Utils.getTranslation(layerrecord.get('layername')) + '</BR><b class="smalltext" style="color:darkgrey">' + esapp.Utils.getTranslation(layerrecord.get('provider')) +'</b>';
            //,outmask_togglebtn = me.lookupReference('outmaskbtn_'+ me.id.replace(/-/g,'_'));

            //,fillopacity = (layerrecord.get('feature_highlight_fillopacity')/100).toString().replace(",", ".")
            //,highlight_fillcolor_opacity = 'rgba(' + esapp.Utils.HexToRGB(layerrecord.get('feature_highlight_fillcolor')) + ',' + fillopacity + ')';
            //namefield = layerrecord.get('feature_display_column').split(',')[0];
            //geojsonfile = layerrecord.get('filename'),
            //feature_display_column = layerrecord.get('feature_display_column'),
            //adminlevel = layerrecord.get('layerlevel'),


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
              // var size = /** @type {ol.Size} */ (me.map.getSize());
              // me.map.getView().fit(
              //     vectorSource.getExtent(),
              //     size,
              //     {
              //         padding: [50, 50, 50, 50],
              //         constrainResolution: false
              //     }
              // );

              // Unregister the "change" listener
              ol.Observable.unByKey(listenerKey);
              // or vectorSource.unByKey(listenerKey) if you don't use the current master branch of ol3
          }
          else {
            myLoadMask.hide();
          }
        });

        var layerStyle = (function() {
            var styles = {};
            styles['Polygon'] = [
              new ol.style.Style({
                fill: new ol.style.Fill({
                  color: layerrecord.get('polygon_fillcolor')   // 'Transparent'  // [255, 255, 255, 0.5]
                })
              }),
              new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: layerrecord.get('polygon_outlinecolor'), // [255, 0, 0, 1],
                  width: layerrecord.get('polygon_outlinewidth')
                })
              })
              //,new ol.style.Style({
              //  stroke: new ol.style.Stroke({
              //    color: [0, 153, 255, 1],
              //    width: 3
              //  })
              //})
            ];
            styles['MultiPolygon'] = styles['Polygon'];

            styles['LineString'] = [
              new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: layerrecord.get('polygon_outlinecolor'), // [255, 0, 0, 1],
                  width: layerrecord.get('polygon_outlinewidth')
                })
              })
              //,new ol.style.Style({
              //  stroke: new ol.style.Stroke({
              //    color: [0, 153, 255, 1],
              //    width: 3
              //  })
              //})
            ];
            styles['MultiLineString'] = styles['LineString'];

            styles['Point'] = [
              new ol.style.Style({
                image: new ol.style.Circle({
                  radius: 5,
                  fill: new ol.style.Fill({
                    color: layerrecord.get('polygon_fillcolor')  // [0, 153, 255, 1]
                  }),
                  stroke: new ol.style.Stroke({
                    color: layerrecord.get('polygon_outlinecolor'),   //[255, 0, 0, 0.75],
                    width: layerrecord.get('polygon_outlinewidth')
                  })
                }),
                zIndex: 100000
              })
            ];
            styles['MultiPoint'] = styles['Point'];

            styles['GeometryCollection'] = styles['Polygon'].concat(styles['Point']);

            return function(feature) {
              return styles[feature.getGeometry().getType()];
            };
        })();

        var styleCache = {};
        var vectorLayer = new ol.layer.Vector({
            title: layertitle,
            layer_id: layerrecord.get('layername'),     // + '_' + me.id.replace(/-/g,'_')
            layerorderidx:layerrecord.get('layerorderidx'),
            feature_display_column: layerrecord.get('feature_display_column'),
            layertype: 'vector',
            visible: true,
            source: vectorSource,
            style: layerStyle
            //style: function (feature, resolution) {
            //    var text = resolution < 5000 ? feature.get(namefield) : '';
            //    //var styleCache = {};
            //    if (!styleCache[text]) {
            //        styleCache[text] = [new ol.style.Style({
            //            //fill: new ol.style.Fill({
            //            //  color: 'rgba(255, 255, 255, 0.6)'
            //            //}),
            //            cursor: "pointer",
            //            stroke: new ol.style.Stroke({
            //                color: layerrecord.get('polygon_outlinecolor'), // '#319FD3',
            //                width: layerrecord.get('polygon_outlinewidth')
            //            })
            //            //,text: new ol.style.Text({
            //            //  font: '12px Calibri,sans-serif',
            //            //  text: text,
            //            //  fill: new ol.style.Fill({
            //            //    color: '#000'
            //            //  }),
            //            //  stroke: new ol.style.Stroke({
            //            //    color: '#fff',
            //            //    width: 3
            //            //  })
            //            //})
            //        })];
            //    }
            //    return styleCache[text];
            //}
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

        this.outmaskingPossible();
        //if (me.getController().outmaskingPossible(me.map)){
        //    outmask_togglebtn.show();
        //}
        //else outmask_togglebtn.hide();


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

    ,displayFeatureInfo: function(pixel) {
        var me = this.getView();
        var toplayeridx = 10;
        var topfeature;

        me.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            if (layer != null){
                var this_layer_idx = layer.get("layerorderidx");
                if (this_layer_idx != 100 && layer.getVisible()  && this_layer_idx < toplayeridx) {
                    toplayeridx = this_layer_idx;
                    me.toplayer = layer;
                    topfeature = feature
                }
            }
        });

        var regionname = Ext.get('region_name_' + me.id);

        if (esapp.Utils.objectExists(topfeature)) {
            if (topfeature !== me.highlight) {
                var feature_columns = me.toplayer.get('feature_display_column').split(',');
                var regionname_html = '';
                for (var i = 0; i < feature_columns.length; i++) {
                    regionname_html += topfeature.get(feature_columns[i].trim());
                    if (i != feature_columns.length - 1) {
                        regionname_html += ' - ';
                    }
                }
                if (regionname_html == 'undefined' && me.toplayer.get('layer_id') == 'drawvectorlayer'){
                    regionname_html = esapp.Utils.getTranslation('drawn') + " " + topfeature.getGeometry().getType();      // "Drawn "
                }
                regionname.setHtml(regionname_html);

                me.featureOverlay.getSource().clear();
                me.featureOverlay.getSource().addFeature(topfeature);
                me.highlight = topfeature;
            }
        } else {
             me.featureOverlay.getSource().clear();
             regionname.setHtml('&nbsp;');
             me.highlight = null;
        }

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
    }

    ,displaySelectedFeatureInfo: function(pixel,displaywkt) {
        var me = this.getView();
        var feature = me.highlight;
        var selectedregion = Ext.getCmp('selectedregionname');
        var wkt_polygon = Ext.getCmp('wkt_polygon');
        //var regionname = Ext.getCmp('regionname');
        //var admin0name = Ext.getCmp('admin0name');
        //var admin1name = Ext.getCmp('admin1name');
        //var admin2name = Ext.getCmp('admin2name');

        if (esapp.Utils.objectExists(feature)) {
            if (feature !== me.selectedfeature) {
                var feature_columns = me.toplayer.get('feature_display_column').split(',');
                var regionname_html = '';
                for (var i = 0; i < feature_columns.length; i++) {
                    regionname_html += feature.get(feature_columns[i].trim());
                    if (i != feature_columns.length-1){
                        regionname_html += ' - ';
                    }
                }
                me.selectedFeatureFromDrawLayer = false;
                if (regionname_html == 'undefined' && me.toplayer.get('layer_id') == 'drawvectorlayer'){
                    me.selectedFeatureFromDrawLayer = true;
                    regionname_html = esapp.Utils.getTranslation('drawn') + " " + feature.getGeometry().getType();     // "Drawn "
                }
                selectedregion.setValue(regionname_html);

                me.selectedarea = regionname_html;
                me.getController().refreshTitleData();

                if (displaywkt) {
                    var wkt = new ol.format.WKT();
                    var wktstr = wkt.writeFeature(feature);
                    //var wktstr = wkt.writeGeometry(feature);
                    // not a good idea in general
                    wktstr = wktstr.replace(/,/g, ', ');
                    wkt_polygon.setValue(wktstr);
                }

                Ext.getCmp('fieldset_selectedregion').show();

                me.selectedFeatureOverlay.getSource().clear();
                me.selectedFeatureOverlay.getSource().addFeature(feature);
                me.selectedfeature = feature;
                //if (me.selectedfeature != null) {
                //    me.selectedFeatureOverlay.getSource().removeFeature(me.selectedfeature);
                //}

                var outmask = me.lookupReference('outmaskbtn_' + me.id.replace(/-/g, '_')).pressed;
                if (outmask) {
                    me.getController().outmaskFeature();
                }
            }
        } else {
            //regionname.setValue('&nbsp;');
            //admin0name.setValue('&nbsp;');
            //admin1name.setValue('&nbsp;');
            //admin2name.setValue('&nbsp;');
            wkt_polygon.setValue('');
            selectedregion.setValue('&nbsp;');
            Ext.getCmp('fieldset_selectedregion').hide();
            me.selectedFeatureOverlay.getSource().clear();
            me.selectedfeature = null;
        }
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
            ,title: esapp.Utils.getTranslation('Draw properties ') + esapp.Utils.getTranslation(layerrecord.get('layername'))   // esapp.Utils.getTranslation(layerrecord.get('menu')) + ' ' + (layerrecord.get('submenu') != '' ? layerrecord.get('submenu') + ' ' : ' ') + esapp.Utils.getTranslation(layerrecord.get('layername'))
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
            {property: 'layername', direction: 'ASC'}]);
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
                            //hideOnClick: false,
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
                maxWidth: 250,
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

    ,createToolBar: function() {
        var me = this.getView();

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
            menuAlign: 'tl-tr',
            arrowVisible: false,
            alwaysOnTop: true,
            menu: {
                hideOnClick: false,
                iconAlign: '',
                alwaysOnTop: true,
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

        var geometrytypes = Ext.create('Ext.data.ArrayStore', {
            fields: ['geometrytype','geometryname'],
            data: [
                ['Polygon', 'Polygon'],
                ['LineString', 'LineString'],
                ['Point', 'Point'],
                //['Circle', 'Circle'],
                ['Square', 'Square'],
                ['Box', 'Box'],
                ['None', 'None']
            ]
        });

        var geometrytypescombo = Ext.create('Ext.form.field.ComboBox', {
            id: 'geometrytypes' + me.id,
            hideLabel: true,
            store: geometrytypes,
            displayField: 'geometryname',
            valueField: 'geometrytype',
            value: 'Polygon',
            typeAhead: true,
            queryMode: 'local',
            triggerAction: 'all',
            emptyText: esapp.Utils.getTranslation('select_geometry'),     // 'Select a geometry...',
            selectOnFocus: false,
            width: 100,
            indent: true,
            cls: "x-menu-no-icon",
            listeners: {
                change: function(newValue , oldValue , eOpts ){
                    me.map.removeInteraction(me.draw);
                    me.getController().addDrawInteraction(newValue);
                }
            }
        });


        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            dock: 'top',
            autoShow: true,
            alwaysOnTop: true,
            floating: false,
            hidden: false,
            border: false,
            shadow: false,
            padding: 0,
            defaults: {
                margin: 2
            },
            items: [{
                text: '<div style="font-size: 11px;">' + esapp.Utils.getTranslation('productnavigator') + '</div>', // 'PRODUCT',
                // iconCls: 'africa',
                scale: 'medium',
                cls: 'nopadding-btn',
                // style: {padding: 0},
                // padding: 0,
                // margin: 2,
                handler: 'openProductNavigator'
            }
            ,layersmenubutton
            ,{
                iconCls: 'download_png',
                scale: 'medium',
                handler: 'saveMap',
                href: '',
                download: 'estationmap.png',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('download_map_as_png')
                        });
                    }
                }
            },{
                xtype: 'splitbutton',
                reference: 'saveMapTemplate_'+me.id.replace(/-/g,'_'),
                iconCls: 'fa fa-save fa-2x',
                style: {color: 'lightblue'},
                cls: 'nopadding-splitbtn',
                scale: 'medium',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                handler: 'setMapTemplateName',
                menu: {
                    hideOnClick: false,
                    alwaysOnTop: true,
                    //iconAlign: '',
                    width: 165,
                    defaults: {
                        hideOnClick: true,
                        //cls: "x-menu-no-icon",
                        padding: 2
                    },
                    items: [{
                            //xtype: 'button',
                            text: esapp.Utils.getTranslation('save_as'),    // 'Save as...',
                            iconCls: 'fa fa-save fa-lg lightblue',
                            style: { color: 'lightblue' },
                            //cls: 'x-menu-no-icon button-gray',
                            width: 165,
                            handler: function(){
                                me.isNewTemplate = true;
                                me.getController().setMapTemplateName();
                            }
                    }]
                }
            },{
                xtype: 'container',
                // layout: 'fit',
                autoWidth: true,
                minWidth: 220,
                // width: 350,
                height: 35,
                top: 0,
                align:'left',
                defaults: {
                    style: {
                        "font-size": '10px',
                        "line-height": '14px'
                    }
                },
                items: [{
                    xtype: 'box',
                    // autoWidth: true,
                    // minWidth: 250,
                    height: 25,
                    top:0,
                    html: '<div id="region_name_' + me.id + '" style="line-height:14px; text-align:left; font-size: 10px; font-weight: bold;"></div>'
                },{
                    xtype: 'box',
                    height: 10,
                    top:25,
                    html: '<div id="mouse-position_' + me.id + '"></div>'
                }]
            },'->', {
                // xtype: 'button',
                // id: 'zoomFactorBtn_' + me.id,
                // //reference: 'zoomFactorBtn_' + me.id,
                // iconCls: 'fa fa-search',
                // style: {
                //     color: 'lightblue',
                //     "font-size": '1.70em'
                // },
                // glyph: null,
                // scale: 'medium',
                // hidden: false,
                // arrowVisible: false,
                // arrowAlign: 'right',
                // collapseDirection: 'left',
                // menuAlign: 'tr-tl',
                // listeners: {
                //     // mouseover: function(btn){
                //     //     btn.showMenu();
                //     // },
                //     afterrender: function (me) {
                //         // Register the new tip with an element's ID
                //         Ext.tip.QuickTipManager.register({
                //             target: me.getId(), // Target button's ID
                //             title: '',
                //             text: esapp.Utils.getTranslation('zoom_factor')
                //         });
                //     }
                // },
                // menu: {
                //     maxWidth: 200,
                //     hideOnClick: false,
                //     listeners: {
                //         mouseout: function(menuitem){
                //             menuitem.up().hideMenu();
                //         }
                //     },
                //     items: [{
            //             xtype: 'slider',  // 'numberfield',
            //             //id: 'zoomFactor_slider_' + me.id,
            //             reference: 'zoomfactorslider_' + me.id.replace(/-/g,'_'),
            //             fieldLabel: '<b>'+esapp.Utils.getTranslation('zoom_factor')+'</b>',
            //             labelAlign: 'top',
            //             hideLabel: false,
            //             hideOnClick: false,
            //             width: 180,
            //             maxWidth: 180,
            //             allowDecimals: false,
            //             value: 5,
            //             //step: 1,
            //             increment: 1,
            //             minValue: 1,
            //             maxValue: 10,
            //             tipText: function (thumb) {
            //                 return Ext.String.format('<b>{0}</b>', thumb.value);
            //             },
            //             listeners: {
            //                 changecomplete: function(menuitem, value, oldvalue){
            //                     //console.info(me.lookupReference('toggleLink_btn_'+me.id.replace(/-/g,'_')));
            //                     // console.info('changecomplete called from '+me.id);
            //                     //me.up().commonMapView.setProperties({zoomFactor: 1.1+(0.01*value)});
            //                     //me.up().commonMapView.set('zoomFactor', 1.1+(0.01*value), false);
            //                     var mapview_linked = true;
            //                     var mapViewWindows = Ext.ComponentQuery.query('mapview-window');
            //
            //                     mapview_linked = !me.lookupReference('toggleLink_btn_'+me.id.replace(/-/g,'_')).pressed;
            //                     if (mapview_linked){
            //                         me.up().zoomFactorValue = value;
            //                         me.up().commonMapView =  new ol.View({
            //                             projection:"EPSG:4326",
            //                             displayProjection:"EPSG:4326",
            //                             center: me.up().commonMapView.getCenter(),    // [20, -2],   // [20, -4.7],
            //                             resolution: 0.1,
            //                             minResolution: 0.0001,
            //                             maxResolution: 0.25,
            //                             zoomFactor: 1.1+0.1*value   // (cioe' nel range 1.1 -> 2.1)
            //                             // zoom: me.up().commonMapView.getZoom()-(2*value),
            //                             // minZoom: 15-(2*value),
            //                             // maxZoom: 110,
            //                             // zoomFactor: 1.1+(0.01*value)
            //                         });
            //                         me.up().zoomFactorSliderValue = value;
            //                         me.map.setView(me.up().commonMapView);
            //                         if (esapp.Utils.objectExists(me.up().map)){
            //                             me.up().map.setView(me.up().commonMapView);
            //                         }
            //                     }
            //                     else {
            //                         me.mapView = new ol.View({
            //                             projection:"EPSG:4326",
            //                             displayProjection:"EPSG:4326",
            //                             center: me.up().commonMapView.getCenter(),    // [20, -2],   // [20, -4.7],
            //                             resolution: 0.1,
            //                             minResolution: 0.0001,
            //                             maxResolution: 0.25,
            //                             zoomFactor: 1.1+0.1*value   // (cioe' nel range 1.1 -> 2.1)
            //                             // zoom: me.up().commonMapView.getZoom(),
            //                             // minZoom: 12,
            //                             // maxZoom: 100,
            //                             // zoomFactor: 1.1+(0.01*value)
            //                         });
            //                         me.zoomFactorSliderValue = value;
            //                         me.map.setView(me.mapView);
            //                     }
            //
            //                     if (mapview_linked){
            //                         Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
            //                             var mapview_window_linked = !mapview_window.lookupReference('toggleLink_btn_'+mapview_window.id.replace(/-/g,'_')).pressed;
            //                             if (me != mapview_window && mapview_window_linked){
            //                                mapview_window.map.setView(me.up().commonMapView);
            //                                mapview_window.lookupReference('zoomfactorslider_' + mapview_window.id.replace(/-/g,'_')).setValue(value);
            //                             }
            //                         });
            //                     }
            //
            //                 }
            //             }
            //         }]
            //     }
            //     ,handler: function(btn , y , x ){
            //
            //         // if (btn.pressed) {
            //         //     btn.showMenu();
            //         // }
            //         // else {
            //         //     btn.hideMenu();
            //         // }
            //     }
            // },{
                xtype: 'button',
                reference: 'drawgeometry_'+me.id.replace(/-/g,'_'),
                hidden: false,
                iconCls: 'polygon-gray',
                scale: 'medium',
                floating: false,  // usually you want this set to True (default)
                enableToggle: true,
                arrowVisible: false,
                arrowAlign: 'right',
                collapseDirection: 'left',
                menuAlign: 'tr-tl',
                handler: 'toggleDrawGeometry',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('draw_geometries')
                        });
                    }
                    // mouseover: function(btn , y , x ){
                    //     if (btn.pressed) {
                    //         btn.showMenu();
                    //     }
                    //     else {
                    //         btn.hideMenu();
                    //     }
                    // }
                },
                menu: {
                    hideOnClick: false,
                    alwaysOnTop: true,
                    //iconAlign: '',
                    width: 125,
                    defaults: {
                        hideOnClick: false,
                        //cls: "x-menu-no-icon",
                        padding: 2
                    },
                    items: [
                        geometrytypescombo,
                        {
                            //xtype: 'button',
                            text: 'Save as layer...',
                            iconCls: 'fa fa-save fa-lg lightblue',
                            style: { color: 'lightblue' },
                            //cls: 'x-menu-no-icon button-gray',
                            width: 60,
                            handler: function(){
                                // Open a small modal panel asking to name the layer file
                                var writer = new ol.format.GeoJSON();
                                var geojsonStr = '';
                                var drawnLayerName = esapp.Utils.getTranslation('drawn_layer'); // 'Drawn layer';

                                me.drawvectorlayer.getSource().getFeatures().forEach(function (feat,idx){
                                    feat.setProperties({NAME: feat.getGeometry().getType()});
                                });
                                geojsonStr =  writer.writeFeatures(me.drawvectorlayer.getSource().getFeatures());


                                //console.info(me.drawvectorlayer.getSource().getFeatures());
                                if (me.drawvectorlayer.getSource().getFeatures().length == 0){
                                    Ext.toast({html: esapp.Utils.getTranslation('please_draw_geom_to_save'), title: esapp.Utils.getTranslation('no_geom_to_save'), width: 300, align: 't'});    // 'Please draw at least one geometry to save as a layer.' "No geometries drawn to save!"
                                }
                                else {
                                    Ext.MessageBox.prompt(esapp.Utils.getTranslation('drawn_layer_name'), esapp.Utils.getTranslation('drawn_layer_save_message') + ': ', function(btn, text){   // 'Drawn layer Name'  'Please give a name to drawn layer'
                                        if (btn == 'ok'){
                                            //alert(geojsonStr) map_tpl_save_message
                                            params = {
                                                layerfilename: text,    //  + '.geojson',
                                                drawnlayerfeaturesGEOSON: geojsonStr
                                            };

                                            esapp.Utils.download({
                                                method: 'GET',
                                                url: 'layers/savedrawnlayer',
                                                params: params
                                            });

                                            var task = new Ext.util.DelayedTask(function() {
                                                var layersgridstore  = Ext.data.StoreManager.lookup('LayersStore');
                                                if (layersgridstore.isStore) {
                                                    layersgridstore.load({
                                                        callback: function(records, options, success) {
                                                        }
                                                    });
                                                }
                                            });
                                            task.delay(500);
                                        }
                                    }, this, false, drawnLayerName);
                                }
                            }
                        },{
                            //xtype: 'button',
                            text: esapp.Utils.getTranslation('reset'),   // 'Reset',
                            iconCls: 'fa fa-undo fa-lg red',
                            //style: { color: 'red' },
                            //cls: 'x-menu-no-icon button-gray',
                            width: 60,
                            handler: function(){
                                me.drawvectorlayer.getSource().clear();
                            }
                        }
                    ]
                }
            },{
                //id: 'outmaskbtn_'+me.id,
                reference: 'outmaskbtn_'+me.id.replace(/-/g,'_'),
                hidden: true,
                iconCls: 'africa-orange24',
                scale: 'medium',
                enableToggle: true,
                handler: 'toggleOutmask',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('outmask_selected_geometry')
                        });
                    }
                }
            },{
                reference: 'objectsbtn_'+me.id.replace(/-/g,'_'),
                hidden: false,
                iconCls: 'fa fa-object-group',
                style: {
                    "font-size": '1.70em'
                },
                scale: 'medium',
                enableToggle: true,
                handler: 'toggleObjects',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('show_hide_title_logo_discalaimer_objects')
                        });
                    }
                }
            },{
                //id: 'legendbtn_'+me.id,
                reference: 'legendbtn_'+me.id.replace(/-/g,'_'),
                hidden: true,
                iconCls: 'legends',
                scale: 'medium',
                enableToggle: true,
                handler: 'toggleLegend',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('show_hide_legend')
                        });
                    }
                }
            },{
                reference: 'toggleLink_btn_'+me.id.replace(/-/g,'_'),
                //text: 'Unlink',
                enableToggle: true,
                iconCls: 'fa fa-link fa-2x',
                style: {color: 'gray'},
                //iconCls: 'unlink',
                scale: 'medium',
                handler: 'toggleLink',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('link_unlink_mapview')
                        });
                    }
                }
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
