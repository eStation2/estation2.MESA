
Ext.define("esapp.view.analysis.mapView",{
    "extend": "Ext.window.Window",
    "controller": "analysis-mapview",
    "viewModel": {
        "type": "analysis-mapview"
    },
    xtype: 'mapview-window',

    requires: [
        'esapp.view.analysis.mapViewModel',
        'esapp.view.analysis.mapViewController',
        'esapp.view.widgets.TimeLine',
        'esapp.view.analysis.mapTitleObject',
        'esapp.view.analysis.mapDisclaimerObject',
        "esapp.view.analysis.mapLogoObject",
        'esapp.view.analysis.mapLegendObject',
        'esapp.view.analysis.mapScaleLineObject',

        'Ext.window.Window',
        'Ext.toolbar.Toolbar',
        'Ext.slider.Single',
        'Ext.grid.property.Grid',
        'Ext.picker.Color',
        'Ext.util.TaskRunner'
    ],

    header: {
        titlePosition: 2,
        titleAlign: 'left'
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closeable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,

    width:800,
    height: Ext.getBody().getViewSize().height < 850 ? Ext.getBody().getViewSize().height-100 : 850,

    minWidth:630,
    minHeight:550,

    // glyph : 'xf080@FontAwesome',
    margin: '0 0 0 0',
    shadow: false,
    layout: {
        type: 'border'
    },

    isTemplate: false,
    layers: [],
    projection: 'EPSG:4326',
    link_product_layer: true,

    publishes: ['titleData', 'logoData'],
    config: {
        titleData: null,
        logoData: null,
        showTimeline: true,
        isNewTemplate: true
    },
    bind:{
        titleData:'{titleData}',
        logoData:'{logoData}'
    },

    initComponent: function () {
        var me = this;
        me.link_product_layer = true;
        me.layers = [];
        me.draw = null;
        me.frame = false;
        me.border= false;
        me.bodyBorder = false;
        me.highlight = null;
        me.toplayer = null;
        me.productname = '';
        me.productdate = '';
        me.selectedarea = '';
        me.selectedfeature = null;
        me.featureOverlay = null;
        me.selectedFeatureOverlay = null;
        me.selectedFeatureFromDrawLayer = false;

        me.title = '<span id="mapview_title_templatename_' + me.id + '" class="map-templatename"></span><span id="mapview_title_productname_' + me.id + '"></span>';
        me.height = Ext.getBody().getViewSize().height < 850 ? Ext.getBody().getViewSize().height-100 : 850;

        me.controller.createToolBar();


        me.tools = [
        {
            type: 'gear',
            tooltip: esapp.Utils.getTranslation('maptoolsmenu'), // 'Map tools menu',
            callback: function (mapwin) {
                // toggle hide/show toolbar and adjust map size.
                var sizeWinBody = [];
                var mapToolbar = mapwin.getDockedItems('toolbar[dock="top"]')[0];
                var widthToolbar = mapToolbar.getWidth();
                var heightToolbar = mapToolbar.getHeight();
                if (mapToolbar.hidden == false) {
                    mapToolbar.setHidden(true);
                    sizeWinBody = [document.getElementById(mapwin.id + "-body").offsetWidth, document.getElementById(mapwin.id + "-body").offsetHeight+heightToolbar];
                }
                else {
                    mapToolbar.setHidden(false);
                    sizeWinBody = [document.getElementById(mapwin.id + "-body").offsetWidth, document.getElementById(mapwin.id + "-body").offsetHeight-heightToolbar];
                }
                mapwin.map.setSize(sizeWinBody);
            }
        }];

        me.mapView = new ol.View({
            projection:"EPSG:4326",
            displayProjection:"EPSG:4326",
            center: [15, 2],   // [20, -4.7],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
            resolution: 0.1,
            minResolution: 0.0001,
            maxResolution: 0.25,
            zoomFactor: 1.1+0.1*5   // (cioe' nel range 1.1 -> 2.1)
            // zoom: 22,
            // minZoom: 12,
            // maxZoom: 100,
            // zoomFactor: 1.12 // 1.0+(0.075*1)
        });
        me.zoomFactorSliderValue = 5;

        me.name ='mapviewwindow_' + me.id;

        me.items = [{
            region: 'center',
            items: [{
                xtype: 'container',
                reference: 'mapcontainer_' + me.id,
                id: 'mapcontainer_' + me.id,
                html: '<div id="mapview_' + me.id + '"></div>'
            },{
                xtype: 'button',
                id: 'zoomFactorBtn_' + me.id.replace(/-/g,'_'),
                reference: 'zoomFactorBtn_' + me.id.replace(/-/g,'_'),
                iconCls: 'fa fa-search',
                cls: 'nobackgroundcolor',
                style: {
                    color: 'black',
                    "font-size": '1.70em'
                },
                glyph: null,
                scale: 'medium',
                hidden: false,
                arrowVisible: false,
                arrowAlign: 'right',
                collapseDirection: 'left',
                menuAlign: 'tr-tl',
                border: false,
                autoShow: true,
                floating: true,
                shadow: false,
                // alignTarget : me,
                defaultAlign: 'tr-tr',  // 'c-c',
                alwaysOnTop: true,
                constrain: true,
                enableToggle: true,
                padding: 0,

                listeners: {
                    // mouseover: function(btn){
                    //     btn.showMenu();
                    // },
                    afterrender: function (btn) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: btn.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('zoom_factor')
                        });

                        btn.setPosition(me.getWidth() - 48, 120);
                    }
                },
                menu: {
                    maxWidth: 200,
                    hideOnClick: false,
                    listeners: {
                        mouseout: function(menuitem){
                            menuitem.up().hideMenu();
                        }
                    },
                    items: [{
                        xtype: 'slider',  // 'numberfield',
                        //id: 'zoomFactor_slider_' + me.id,
                        reference: 'zoomfactorslider_' + me.id.replace(/-/g,'_'),
                        fieldLabel: '<b>'+esapp.Utils.getTranslation('zoom_factor')+'</b>',
                        labelAlign: 'top',
                        hideLabel: false,
                        hideOnClick: false,
                        width: 180,
                        maxWidth: 180,
                        allowDecimals: false,
                        value: 5,
                        //step: 1,
                        increment: 1,
                        minValue: 1,
                        maxValue: 10,
                        tipText: function (thumb) {
                            return Ext.String.format('<b>{0}</b>', thumb.value);
                        },
                        listeners: {
                            changecomplete: function(menuitem, value, oldvalue){
                                //console.info(me.lookupReference('toggleLink_btn_'+me.id.replace(/-/g,'_')));
                                // console.info('changecomplete called from '+me.id);
                                //me.up().commonMapView.setProperties({zoomFactor: 1.1+(0.01*value)});
                                //me.up().commonMapView.set('zoomFactor', 1.1+(0.01*value), false);
                                var mapview_linked = true;
                                var mapViewWindows = Ext.ComponentQuery.query('mapview-window');

                                mapview_linked = !me.lookupReference('toggleLink_btn_'+me.id.replace(/-/g,'_')).pressed;
                                if (mapview_linked){
                                    me.up().zoomFactorValue = value;
                                    me.up().commonMapView =  new ol.View({
                                        projection:"EPSG:4326",
                                        displayProjection:"EPSG:4326",
                                        center: me.up().commonMapView.getCenter(),    // [20, -2],   // [20, -4.7],
                                        resolution: 0.1,
                                        minResolution: 0.0001,
                                        maxResolution: 0.25,
                                        zoomFactor: 1.1+0.1*value   // (cioe' nel range 1.1 -> 2.1)
                                        // zoom: me.up().commonMapView.getZoom()-(2*value),
                                        // minZoom: 15-(2*value),
                                        // maxZoom: 110,
                                        // zoomFactor: 1.1+(0.01*value)
                                    });
                                    me.up().zoomFactorSliderValue = value;
                                    me.map.setView(me.up().commonMapView);
                                    if (esapp.Utils.objectExists(me.up().map)){
                                        me.up().map.setView(me.up().commonMapView);
                                    }
                                }
                                else {
                                    me.mapView = new ol.View({
                                        projection:"EPSG:4326",
                                        displayProjection:"EPSG:4326",
                                        center: me.up().commonMapView.getCenter(),    // [20, -2],   // [20, -4.7],
                                        resolution: 0.1,
                                        minResolution: 0.0001,
                                        maxResolution: 0.25,
                                        zoomFactor: 1.1+0.1*value   // (cioe' nel range 1.1 -> 2.1)
                                        // zoom: me.up().commonMapView.getZoom(),
                                        // minZoom: 12,
                                        // maxZoom: 100,
                                        // zoomFactor: 1.1+(0.01*value)
                                    });
                                    me.zoomFactorSliderValue = value;
                                    me.map.setView(me.mapView);
                                }

                                if (mapview_linked){
                                    Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                                        var mapview_window_linked = !mapview_window.lookupReference('toggleLink_btn_'+mapview_window.id.replace(/-/g,'_')).pressed;
                                        if (me != mapview_window && mapview_window_linked){
                                           mapview_window.map.setView(me.up().commonMapView);
                                           mapview_window.lookupReference('zoomfactorslider_' + mapview_window.id.replace(/-/g,'_')).setValue(value);
                                        }
                                    });
                                }

                            }
                        }
                    }]
                }
                ,handler: function(btn , y , x ){

                    // if (btn.pressed) {
                    //     btn.showMenu();
                    // }
                    // else {
                    //     btn.hideMenu();
                    // }
                }
            }, {
                xtype: 'button',
                id: 'opacityslider_' + me.id.replace(/-/g,'_'),
                reference: 'opacityslider_' + me.id.replace(/-/g,'_'),
                border: false,
                autoShow: false,
                floating: true,
                shadow: false,
                // alignTarget : me,
                defaultAlign: 'tr-tr',  // 'c-c',
                alwaysOnTop: true,
                constrain: true,
                // width: 150,
                // value: 100,

                hidden: true,
                cls: 'nobackgroundcolor',
                iconCls: 'transparencyicon',
                // style: {
                //     "font-size": '1.70em'
                // },
                scale: 'medium',
                enableToggle: true,
                arrowVisible: false,
                collapseDirection: 'left',
                menuAlign: 'tr-tl',
                padding: 0,
                // handler: 'toggleObjects',
                listeners: {
                    afterrender: function (btn) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: btn.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('opacity_slider')  // 'Product layer opacity slider'
                        });
                        btn.setPosition(me.getWidth() - 48, 155);
                    }
                },
                menu: {
                    hideOnClick: false,
                    alwaysOnTop: true,
                    //iconAlign: '',
                    // width: 150,
                    defaults: {
                        hideOnClick: false,
                        //cls: "x-menu-no-icon",
                        padding: 2
                    },
                    items: [{
                        xtype: 'slider',
                        // cls: 'custom-slider',
                        fieldLabel: null,
                        labelStyle: {color: 'lightgray'},
                        labelSeparator: '',
                        labelWidth: 3,
                        hideLabel: true,
                        hideEmptyLabel: true,
                        //border: false,
                        //autoShow: true,
                        //floating: true,
                        //shadow: false,
                        ////alignTarget : me,
                        //defaultAlign: 'tr-tr',  // 'c-c',
                        //alwaysOnTop: true,
                        //constrain: true,
                        width: 150,
                        value: 100,
                        increment: 10,
                        minValue: 0,
                        maxValue: 100,
                        tipText: function (thumb) {
                            return Ext.String.format('<b>{0}%</b>', thumb.value);
                        },
                        listeners: {
                            afterrender: function () {
                                //this.setPosition(me.getWidth()-165, 5);
                            },
                            change: function (slider, newValue, thumb, eOpts) {
                                var _layers = me.map.getLayers();
                                _layers.a[0].setOpacity(newValue / 100)
                            }
                        }
                    }]
                }
            }, {
                xtype: 'mapscalelineobject',
                id: 'scale-line_' + me.id,
                reference: 'scale-line_' + me.id,
                mapView: me
            }, {
                xtype: 'maplegendobject',
                id: 'product-legend_' + me.id,
                reference: 'product-legend_' + me.id
            }, {
                xtype: 'maptitleobject',
                id: 'title_obj_' + me.id,
                reference: 'title_obj_' + me.id
            }, {
                xtype: 'mapdisclaimerobject',
                id: 'disclaimer_obj_' + me.id,
                reference: 'disclaimer_obj_' + me.id
            }, {
                xtype: 'maplogoobject',
                id: 'logo_obj_' + me.id,
                reference: 'logo_obj_' + me.id
            }]
        },{
            region: 'south',
            id: 'product-time-line_' + me.id,
            reference: 'product-time-line_' + me.id,
            align:'left',
            alwaysOnTop: true,
            autoWidth:true,
            margin:0,
            padding:0,
            height: 125,
            maxHeight: 125,
            hidden: true,
            hideMode : 'visibility',    //'display',
            frame:  false,
            shadow: false,
            border: false,
            bodyBorder: true,
            // style: {
            //     "border-top": '1px solid black;'
            // },

            header : false,
            collapsible: true,
            collapsed: false,
            collapseFirst: false,
            collapseDirection: 'top',
            collapseMode : "mini",  // The Panel collapses without a visible header.
            //headerPosition: 'left',
            hideCollapseTool: true,
            split: true,
            splitterResize : false,
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'right',
                items: [{
                    xtype: 'splitbutton',
                    id: 'playBtn_' + me.id,
                    //reference: 'playBtn_' + me.id,
                    iconCls: 'fa fa-play',
                    style: { color: 'green' },
                    glyph: null,
                    scale: 'small',
                    hidden: false,
                    arrowAlign: 'bottom',
                    handler: 'play',
                    menu: {
                        hideOnClick: false,
                        alwaysOnTop: true,
                        width: 45,
                        items: [{
                            xtype: 'numberfield',
                            id: 'playInterval_' + me.id,
                            hideLabel: true,
                            width: 45,
                            // maxWidth: 45,
                            allowDecimals: false,
                            value: 3000,
                            step: 500,
                            minValue: 1000,
                            maxValue: 10000,
                            listeners: {
                                afterrender: function (me) {
                                    // Register the new tip with an element's ID
                                    Ext.tip.QuickTipManager.register({
                                        target: me.getId(), // Target button's ID
                                        title: '',
                                        text: esapp.Utils.getTranslation('interval_in_ms') // 'Interval in milliseconds'
                                    });
                                }
                            }
                        }]
                    }
                }, {
                    xtype: 'button',
                    id: 'pauseBtn_' + me.id,
                    //reference: 'pauseBtn_' + me.id,
                    iconCls: 'fa fa-pause',
                    style: { color: 'orange' },
                    glyph: null,
                    scale: 'small',
                    hidden: true,
                    handler: 'pause'
                }, {
                    xtype: 'button',
                    id: 'stopBtn_' + me.id,
                    //reference: 'stopBtn_' + me.id,   // Give an error in Ext.mixin.Bindable method applyReference: Invalid reference "stopBtn_mapview-window-1262" for stopBtn_mapview-window-1262 - not a valid identifier
                    iconCls: 'fa fa-stop',
                    style: {color: 'red'},
                    glyph: null,
                    scale: 'small',
                    hidden: true,
                    handler: 'stop'
                }, ' ', {
                    xtype: 'button',
                    id: 'dateLinkToggleBtn_' + me.id,
                    enableToggle: true,
                    //scope: me,
                    iconCls: 'calendar_linked',
                    //style: { color: 'orange' },
                    glyph: null,
                    scale: 'medium',
                    hidden: false,
                    handler: 'toggleDateLink'
                }]
            }],
            listeners: {
                show: function () {
                    // var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight-this.height];
                    // me.map.setSize(size);
                    // console.info('Show timeline call redraw');
                    me.getController().redrawTimeLine(me);
                },
                expand: function () {
                    // var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight-this.height];
                    // me.map.setSize(size);
                    // console.info('Expand timeline call redraw');
                    me.getController().redrawTimeLine(me);
                }
                // ,collapse: function () {
                //     // var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight];
                //     // me.map.setSize(size);
                //     console.info('Collapse timeline call redraw');
                //     // me.getController().redrawTimeLine(me);
                // }
            }
            ,items: [{
                xtype: 'time-line-chart',
                id: 'time-line-chart' + me.id,
                reference: 'time-line-chart' + me.id,
                layout: 'fit'
            }]
        }];

        me.listeners = {
            afterrender: function () {
                //Ext.util.Observable.capture(me, function(e){console.log('mapView - ' + me.id + ': ' + e);});

                var mousePositionControl = new ol.control.MousePosition({
                    coordinateFormat: function(coord) {
                        var stringifyFunc = ol.coordinate.createStringXY(3);
                        return ol.coordinate.toStringHDMS(coord) + ' (' + stringifyFunc(coord) + ')';
                    },
                    projection: 'EPSG:4326',
                    // comment the following two lines to have the mouse position be placed within the map.
                    // className: 'ol-full-screen',
                    className: 'ol-custom-mouse-position',
                    target:  document.getElementById('mouse-position_'+ me.id), // Ext.get('mouse-position_'+ me.id), //
                    undefinedHTML: '&nbsp;'
                });


                this.map = new ol.Map({
                    target: 'mapview_'+ this.id,
                    projection: me.projection,
                    displayProjection:"EPSG:4326",
                    //interactions: ol.interaction.defaults().extend([select]),
                    interactions : ol.interaction.defaults({doubleClickZoom :false}),
                    //layers: [blanklayer],
                    view: this.up().commonMapView,
                    controls: ol.control.defaults({
                        attribution:false,
                        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                            collapsible: false // false to show always without the icon.
                        })
                    }).extend([mousePositionControl])
                });

                this.map.addInteraction(new ol.interaction.MouseWheelZoom({
                    duration: 25
                }));

                this.map.on('pointermove', function(evt) {
                    if (evt.dragging) {
                        return;
                    }
                    //if (me.map.getLayers().getArray().length > 2) {
                        var pixel = me.map.getEventPixel(evt.originalEvent);
                        me.getController().displayFeatureInfo(pixel, false);
                    //}
                    //me.map.getLayers().getArray().forEach(function (layer,idx){
                    //    var this_layer_id = layer.get("layer_id")
                    //    if (this_layer_id == 'drawvectorlayer')
                    //        console.info(this_layer_id);
                    //});
                });

                this.map.on('click', function(evt) {
                    //var coordinate = evt.coordinate;
                    //overlay.setPosition(coordinate);
                    var drawgeometry_togglebtn = me.lookupReference('drawgeometry_'+me.id.replace(/-/g,'_'));
                    //if (!drawgeometry_togglebtn.pressed && me.map.getLayers().getArray().length > 2) {
                    if (!drawgeometry_togglebtn.pressed) {
                        me.getController().displaySelectedFeatureInfo(evt.pixel, true);
                    }
                });

                this.map.on('dblclick', function(evt) {
                    var drawgeometry_togglebtn = me.lookupReference('drawgeometry_'+me.id.replace(/-/g,'_'));
                    //if (!drawgeometry_togglebtn.pressed && me.map.getLayers().getArray().length > 2) {
                    if (!drawgeometry_togglebtn.pressed) {
                        if (esapp.Utils.objectExists(me.selectedfeature)) {
                            // Zoom to and center the selected feature
                            var polygon = /** @type {ol.geom.SimpleGeometry} */ (me.selectedfeature.getGeometry());
                            // console.info(polygon.getType());
                            if (polygon.getType() != 'Point') {
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
                        }
                    }
                });


                this.productlayer = new ol.layer.Tile({       // Image
                    layer_id: 'productlayer',
                    layerorderidx: 100,
                    type: 'base',
                    visible: false
                });
                this.map.getLayers().insertAt(0, this.productlayer);


                this.drawfeatures = new ol.Collection();
                this.drawvectorlayer_source = new ol.source.Vector({
                    features: this.drawfeatures,
                    wrapX: false
                });
                this.drawvectorlayer = new ol.layer.Vector({
                    source: this.drawvectorlayer_source,
                    layer_id: 'drawvectorlayer',
                    layerorderidx: 0,
                    layertype: 'drawvector',
                    feature_display_column: 'NAME',
                    style: new ol.style.Style({
                      fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.2)'
                      }),
                      stroke: new ol.style.Stroke({
                        color: '#ffcc33',
                        width: 2
                      }),
                      image: new ol.style.Circle({
                        radius: 5,
                        fill: new ol.style.Fill({
                          color: '#ffcc33'
                        })
                      })
                    })
                });
                this.map.getLayers().insertAt(10, this.drawvectorlayer);

                //me.getController().addLayerSwitcher(me.map);
                //var selectDrawfeatures = new ol.interaction.Select({
                //    wrapX: false,
                //    style: overlayStyle
                //});
                //this.map.addInteraction(selectDrawfeatures);
                //
                //var modifyDrawfeatures = new ol.interaction.Modify({
                //    //features: this.drawfeatures,
                //    features: selectDrawfeatures.getFeatures(),
                //    style: overlayStyle,
                //    // the SHIFT key must be pressed to delete vertices, so
                //    // that new vertices can be drawn at the same position
                //    // of existing vertices
                //    deleteCondition: function(event) {
                //      return ol.events.condition.shiftKeyOnly(event) &&
                //          ol.events.condition.singleClick(event);
                //    }
                //});
                //this.map.addInteraction(modifyDrawfeatures);
                //
                //
                // var fillopacity = (10/100).toString().replace(",", ".")
                //     ,highlight_fillcolor_opacity = 'rgba(' + esapp.Utils.HexToRGB('#319FD3') + ',' + fillopacity + ')'
                //     ,pointfillopacity = (80/100).toString().replace(",", ".")
                //     ,pointhighlight_fillcolor_opacity = 'rgba(' + esapp.Utils.HexToRGB('#319FD3') + ',' + pointfillopacity + ')'
                //     ,feature_highlight_outlinecolor = '#319FD3'
                //     ,feature_highlight_outlinewidth = 2;
                // var featureOverlayStyle = (function() {
                //     var styles = {};
                //     styles['Polygon'] = [
                //       new ol.style.Style({
                //         fill: new ol.style.Fill({
                //           color: highlight_fillcolor_opacity    // 'Transparent'  // [255, 255, 255, 0.5]
                //         })
                //       }),
                //       new ol.style.Style({
                //         stroke: new ol.style.Stroke({
                //           color: feature_highlight_outlinecolor, // [255, 0, 0, 1],
                //           width: feature_highlight_outlinewidth
                //         })
                //       })
                //       //,new ol.style.Style({
                //       //  stroke: new ol.style.Stroke({
                //       //    color: [0, 153, 255, 1],
                //       //    width: 3
                //       //  })
                //       //})
                //     ];
                //     styles['MultiPolygon'] = styles['Polygon'];
                //
                //     styles['LineString'] = [
                //       new ol.style.Style({
                //         stroke: new ol.style.Stroke({
                //           color: feature_highlight_outlinecolor, // [255, 0, 0, 1],
                //           width: feature_highlight_outlinewidth
                //         })
                //       })
                //       //,new ol.style.Style({
                //       //  stroke: new ol.style.Stroke({
                //       //    color: [0, 153, 255, 1],
                //       //    width: 3
                //       //  })
                //       //})
                //     ];
                //     styles['MultiLineString'] = styles['LineString'];
                //
                //     styles['Point'] = [
                //       new ol.style.Style({
                //         image: new ol.style.Circle({
                //           radius: 6,
                //           fill: new ol.style.Fill({
                //             color: pointhighlight_fillcolor_opacity  // [0, 153, 255, 1]
                //           }),
                //           stroke: new ol.style.Stroke({
                //             color: feature_highlight_outlinecolor,   //[255, 0, 0, 0.75],
                //             width: feature_highlight_outlinewidth
                //           })
                //         }),
                //         zIndex: 100000
                //       })
                //     ];
                //     styles['MultiPoint'] = styles['Point'];
                //
                //     styles['GeometryCollection'] = styles['Polygon'].concat(styles['Point']);
                //
                //     return function(feature) {
                //       return styles[feature.getGeometry().getType()];
                //     };
                // })();
                //
                // this.featureOverlay = new ol.layer.Vector({      //new ol.FeatureOverlay({
                //         name: 'highlightfeatureOverlay_',       // + layerrecord.get('layername'),
                //         source: new ol.source.Vector({
                //             features: new ol.Collection(),
                //             useSpatialIndex: false, // optional, might improve performance
                //             wrapX: false,
                //             noWrap: true
                //         }),
                //         updateWhileAnimating: true, // optional, for instant visual feedback
                //         updateWhileInteracting: true, // optional, for instant visual feedback
                //
                //         map: this.map,
                //         style: featureOverlayStyle
                //         //style: function (feature, resolution) {
                //         //    var text = resolution < 5000 ? feature.get(namefield) : '';
                //         //    //var highlightStyleCache = {};
                //         //    if (!highlightStyleCache[text]) {
                //         //        highlightStyleCache[text] = [new ol.style.Style({
                //         //            stroke: new ol.style.Stroke({
                //         //                color: layerrecord.get('feature_highlight_outlinecolor'),    // '#319FD3',
                //         //                width: layerrecord.get('feature_highlight_outlinewidth')
                //         //            })
                //         //            , fill: new ol.style.Fill({
                //         //                color: highlight_fillcolor_opacity    // 'rgba(49,159,211,0.1)'
                //         //            })
                //         //            //,text: new ol.style.Text({
                //         //            //  font: '12px Calibri,sans-serif',
                //         //            //  text: text,
                //         //            //  fill: new ol.style.Fill({
                //         //            //    color: '#000'
                //         //            //  }),
                //         //            //  stroke: new ol.style.Stroke({
                //         //            //    color: '#f00',
                //         //            //    width: 3
                //         //            //  })
                //         //            //})
                //         //        })];
                //         //    }
                //         //    return highlightStyleCache[text];
                //         //}
                //     });
                //
                //
                // var feature_selected_outlinecolor = '#FF0000'
                //    ,feature_selected_outlinewidth = 2;
                // var selectedFeatureOverlayStyle = (function() {
                //     var styles = {};
                //     styles['Polygon'] = [
                //       new ol.style.Style({
                //         fill: new ol.style.Fill({
                //           color: 'Transparent'  // [255, 255, 255, 0.5]
                //         })
                //       }),
                //       new ol.style.Style({
                //         stroke: new ol.style.Stroke({
                //           color: feature_selected_outlinecolor,         // layerrecord.get('feature_selected_outlinecolor'), // [255, 0, 0, 1],
                //           width: feature_selected_outlinewidth          // layerrecord.get('feature_selected_outlinewidth')  // 3
                //         })
                //       })
                //     ];
                //     styles['MultiPolygon'] = styles['Polygon'];
                //
                //     styles['LineString'] = [
                //       new ol.style.Style({
                //         stroke: new ol.style.Stroke({
                //           color: feature_selected_outlinecolor,         // layerrecord.get('feature_selected_outlinecolor'), // [255, 0, 0, 1],
                //           width: feature_selected_outlinewidth          // layerrecord.get('feature_selected_outlinewidth')  // 3
                //         })
                //       })
                //     ];
                //     styles['MultiLineString'] = styles['LineString'];
                //
                //     styles['Point'] = [
                //       new ol.style.Style({
                //         image: new ol.style.Circle({
                //           radius: 6,
                //           fill: new ol.style.Fill({
                //             color: 'Transparent'  // [0, 153, 255, 1]
                //           }),
                //           stroke: new ol.style.Stroke({
                //             color: feature_selected_outlinecolor,       // layerrecord.get('feature_selected_outlinecolor'),   //[255, 0, 0, 0.75],
                //             width: feature_selected_outlinewidth        // layerrecord.get('feature_highlight_outlinewidth')
                //           })
                //         }),
                //         zIndex: 100000
                //       })
                //     ];
                //     styles['MultiPoint'] = styles['Point'];
                //
                //     styles['GeometryCollection'] = styles['Polygon'].concat(styles['Point']);
                //
                //     return function(feature) {
                //       return styles[feature.getGeometry().getType()];
                //     };
                // })();
                //
                // var selectStyleCache = {};
                // this.selectedFeatureOverlay = new ol.layer.Vector({      //new ol.FeatureOverlay({
                //     name: 'selectedfeatureOverlay',        //  + layerrecord.get('layername'),
                //     source: new ol.source.Vector({
                //         features: new ol.Collection(),
                //         useSpatialIndex: false, // optional, might improve performance
                //         wrapX: false,
                //         noWrap: true
                //     }),
                //     updateWhileAnimating: true, // optional, for instant visual feedback
                //     updateWhileInteracting: true, // optional, for instant visual feedback
                //
                //     map: this.map,
                //     style: selectedFeatureOverlayStyle
                //     //style: function (feature, resolution) {
                //     //    var text = resolution < 5000 ? feature.get(namefield) : '';
                //     //    //var selectStyleCache = {};
                //     //    if (!selectStyleCache[text]) {
                //     //        selectStyleCache[text] = [new ol.style.Style({
                //     //            stroke: new ol.style.Stroke({
                //     //                color: layerrecord.get('feature_selected_outlinecolor'),   // '#f00',
                //     //                width: layerrecord.get('feature_selected_outlinewidth')
                //     //            })
                //     //            , fill: new ol.style.Fill({
                //     //                color: 'Transparent' // 'rgba(255,0,0,0.1)'
                //     //            })
                //     //        })];
                //     //    }
                //     //    return selectStyleCache[text];
                //     //}
                // });



                // this.el is not created until after the Window is rendered so you need to add the mon after rendering:
                this.mon(this.el, {
                    mouseout: function() {
                        //console.info(me);
                        if (esapp.Utils.objectExists(me.featureOverlay) && esapp.Utils.objectExists(me.highlight)){
                            me.featureOverlay.getSource().clear();
                            me.highlight = null;
                            //me.featureOverlay.getSource().removeFeature(me.highlight);
                        }
                    },
                    keydown: function(e) {
                        if(e.getKey() == 46){ //delete key pressed
                            //delete feature from draw vector layer if selected feature is a feature from the draw vector layer
                            if (me.selectedfeature != null && me.selectedFeatureFromDrawLayer) {
                                var selectedregion = Ext.getCmp('selectedregionname');
                                var wkt_polygon = Ext.getCmp('wkt_polygon');
                                //me.selectedFeatureOverlay.getSource().removeFeature(me.selectedfeature);
                                me.drawvectorlayer.getSource().removeFeature(me.selectedfeature);
                                wkt_polygon.setValue('');
                                selectedregion.setValue('&nbsp;');
                                Ext.getCmp('fieldset_selectedregion').hide();
                                me.selectedFeatureOverlay.getSource().clear();
                                me.selectedfeature = null;
                                me.getController().outmaskingPossible();
                            }
                        }
                    }
                });


                if (me.isTemplate){
                    var mapLegendObj = me.lookupReference('product-legend_' + me.id),
                        titleObj = me.lookupReference('title_obj_' + me.id),
                        disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                        logoObj = me.lookupReference('logo_obj_' + me.id),
                        scalelineObj = me.lookupReference('scale-line_' + me.id),
                        mapObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));

                    me.setPosition(me.mapviewPosition);
                    me.setSize(me.mapviewSize[0],me.mapviewSize[1]);

                    //disclaimerObj.suspendEvents();
                    disclaimerObj.disclaimerPosition = me.disclaimerObjPosition;
                    disclaimerObj.setHtml(me.disclaimerObjContent);
                    disclaimerObj.setContent(me.disclaimerObjContent);

                    //logoObj.suspendEvents();
                    logoObj.logoPosition = me.logosObjPosition;
                    me.setLogoData(me.logosObjContent);

                    scalelineObj.scalelinePosition = me.scalelineObjPosition;
                    //mapLegendObj.suspendEvents();
                    mapLegendObj.legendPosition = me.legendObjPosition;
                    mapLegendObj.legendLayout = me.legendlayout;
                    mapLegendObj.showlegend = me.showlegend;

                    //titleObj.suspendEvents();
                    titleObj.titlePosition = me.titleObjPosition;
                    if (me.titleObjContent != null && me.titleObjContent.trim() != ''){
                        titleObj.setTpl(me.titleObjContent);
                    }
                    // console.info(titleObj);
                    // titleObj.tpl.set(me.titleObjContent, true);

                    if (me.showObjects){
                        var task = new Ext.util.DelayedTask(function() {
                            //console.info(mapObjectToggleBtn);
                            mapObjectToggleBtn.toggle(true);
                            me.getController().toggleObjects(mapObjectToggleBtn);
                        });
                        task.delay(500);
                    }

                    Ext.fly('mapview_title_templatename_' + me.id).dom.innerHTML = me.templatename;
                    //me.setTitle('<div id="mapview_title_templatename_' + me.id + '" class="map-templatename">' + me.templatename + '</div>');

                    if (me.productcode != ''){
                        var task = new Ext.util.DelayedTask(function() {
                            Ext.data.StoreManager.lookup('DataSetsStore').each(function(rec){
                                // console.info(rec);
                                if (rec.get('productcode')==me.productcode &&
                                    rec.get('version')==me.productversion ){
                                    //console.info(rec.get('productmapsets'));
                                    rec.get('productmapsets').forEach(function(mapset){
                                        if (mapset.mapsetcode==me.mapsetcode){
                                            mapset.mapsetdatasets.forEach(function(mapsetdataset){
                                                if (mapsetdataset.subproductcode==me.subproductcode){
                                                    // console.info(mapsetdataset);
                                                    me.productname = mapsetdataset.descriptive_name;
                                                    me.date_format = mapsetdataset.date_format;
                                                    me.frequency_id = mapsetdataset.frequency_id;
                                                }
                                            },this);
                                        }
                                    },this);
                                }
                            },this);

                            Ext.data.StoreManager.lookup('ColorSchemesStore').each(function(rec){
                                if (rec.get('legend_id')==me.legendid){
                                    //me.colorschemeHTML = rec.get('colorschemeHTML');
                                    me.legendHTML = rec.get('legendHTML');
                                    me.legendHTMLVertical = rec.get('legendHTMLVertical');
                                }
                            },this);

                            me.getController().addProductLayer(me.productcode,
                                                               me.productversion,
                                                               me.mapsetcode,
                                                               me.subproductcode,
                                                               me.legendid,
                                                               me.legendHTML,
                                                               me.legendHTMLVertical,
                                                               me.productname,
                                                               me.date_format,
                                                               me.frequency_id
                            );
                        });
                        task.delay(500);
                    }
                }
                else {
                    this.getController().loadDefaultLayers();
                }

                //Ext.EventManager.on(this,'keypress',function(e){ alert( e.getKey() ) });
            }
            // The resize handle is necessary to set the map!
            ,resize: function () {
                var size = [];
                if (this.productname == '' && this.productdate == '') {
                    size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                }
                else {
                    size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight - 135];
                }
                // console.info('map size: ' + size);
                this.map.setSize(size);

                this.getController().redrawTimeLine(this);

                if (!this.lookupReference('opacityslider_' + this.id.replace(/-/g,'_')).hidden) {
                    this.lookupReference('opacityslider_' + this.id.replace(/-/g, '_')).setPosition(this.getWidth() - 48, 155);
                }
                //this.lookupReference('opacityslider_' + this.id.replace(/-/g,'_')).doConstrain();

                this.lookupReference('zoomFactorBtn_' + this.id.replace(/-/g, '_')).setPosition(this.getWidth() - 48, 120);
                this.updateLayout();
            }
            ,move: function () {
                this.getController().redrawTimeLine(this);
                //this.updateLayout();
                //console.info(this.getPosition(true));
            }
            ,maximize: function () {
                this.updateLayout();
            }
            ,restore: function () {
                //console.info(this.getPosition());
                //this.setPosition(this.getPosition()+1);
                this.updateLayout();
                var maplegendpanel = me.lookupReference('product-legend_panel_' + this.id);
                if (maplegendpanel != null){
                    maplegendpanel.doConstrain();
                }
            }

        };

        me.callParent();

    }
});
