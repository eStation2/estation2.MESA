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
        titleAlign: 'left',
        cls: 'mapview-header'
        // style: {
        //     // "border-width": "2px 7px 1px 7px !important",
        //     "line-height": "13px!important"
        // }
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,
    focusable: true,

    width: 613,  // 603,

    height: 415,    // Ext.getBody().getViewSize().height < 700 ? Ext.getBody().getViewSize().height-100 : 415,

    minWidth:613,
    minHeight:415,

    x: 20,
    y: 20,

    margin: '0 0 0 0',
    shadow: false,
    layout: {
        type: 'border'
    },
    componentCls: 'rounded-box-win',
    // componentCls: 'newpanelstyle',

    bodyStyle: {
        background: '#d3d1d1 !important'
    },

    publishes: ['titleData'],       // , 'logoData'
    config: {
        titleData: null,
        // logoData: null,
        productcode: '',
        productname: '',
        productsensor: '',
        productdate: '',
        link_product_layer: true,
        showlegend: true,
        showObjects: false,
        showtoolbar: true,
        showgraticule: false,
        showtimeline: true,
        nozoom: false,
        isTemplate: false,
        isNewTemplate: true,
        map_tpl_id: null,
        parent_tpl_id: null,
        templatename: '',
        workspace: null,
        layers: [],
        draw: null,
        projection: 'EPSG:4326',
        defaultzoomfactor: 1
    },
    bind:{
        titleData:'{titleData}'
        // ,logoData:'{logoData}'
    },

    initComponent: function () {
        var me = this;
        me.frame = false;
        me.border= false;
        me.bodyBorder = false;

        me.highlight = null;
        me.toplayer = null;
        me.selectedarea = '';
        me.selectedfeature = null;
        me.featureOverlay = null;
        me.selectedFeatureOverlay = null;
        me.selectedFeatureFromDrawLayer = false;

        me.title = '<span id="mapview_title_productname_' + me.id + '"></span>'+ '<span id="mapview_title_templatename_' + me.id + '" class="map-templatename"></span>';
        // me.height = Ext.getBody().getViewSize().height < 670 ? Ext.getBody().getViewSize().height-100 : 670;


        if (me.templatename == '' && me.isTemplate){
            // me.isTemplate = false;
            me.setIsTemplate(false);
            me.setIsNewTemplate(true);
        }

        me.tools = [{
            type: 'gear',
            tooltip: esapp.Utils.getTranslation('maptoolsmenu'), // 'Map tools menu',
            callback: function (mapwin) {
                // toggle hide/show toolbar, without the adjusting the map size, with repositioning the object.
                var mapLegendObj = me.lookupReference('product-legend_' + me.id.replace(/-/g,'_')),
                    titleObj = me.lookupReference('title_obj_' + me.id),
                    disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                    logoObj = me.lookupReference('logo_obj_' + me.id),
                    scalelineObj = me.lookupReference('scale-line_' + me.id),
                    mapObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));

                if (mapObjectToggleBtn.pressed) {
                    disclaimerObj.disclaimerPosition = disclaimerObj.getPosition(true);
                    titleObj.titlePosition = titleObj.getPosition(true);
                    logoObj.logoPosition = logoObj.getPosition(true);
                }
                if (!scalelineObj.hidden) {
                    scalelineObj.scalelinePosition = scalelineObj.getPosition(true);
                }

                // var sizeWinBody = [];
                var mapToolbar = mapwin.getDockedItems('toolbar[dock="top"]')[0];
                // var widthToolbar = mapToolbar.getWidth();
                // var heightToolbar = mapToolbar.getHeight();
                // console.info(heightToolbar);
                if (mapToolbar.hidden == false) {
                    mapwin.setHeight(mapwin.height-39);
                    mapToolbar.setHidden(true);
                    if (mapObjectToggleBtn.pressed) {
                        disclaimerObj.setPosition(disclaimerObj.disclaimerPosition);
                        titleObj.setPosition(titleObj.titlePosition);
                        logoObj.setPosition(logoObj.logoPosition);
                    }
                    if (!scalelineObj.hidden) {
                        scalelineObj.setPosition(scalelineObj.scalelinePosition);
                    }
                    // sizeWinBody = [document.getElementById(mapwin.id + "-body").offsetWidth, document.getElementById(mapwin.id + "-body").offsetHeight+heightToolbar];
                }
                else {
                    mapwin.setHeight(mapwin.height+39);
                    mapToolbar.setHidden(false);
                    // sizeWinBody = [document.getElementById(mapwin.id + "-body").offsetWidth, document.getElementById(mapwin.id + "-body").offsetHeight-heightToolbar];
                }
                // mapwin.map.setSize(sizeWinBody);
                mapwin.map.updateSize();
            }
        }];

        me.controller.createToolBar();

        me.mapView = new ol.View({
            projection:me.projection,
            displayProjection:me.projection,
            center: [16.4, -0.5],   // [20, -4.7],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
            resolution: 0.1,
            minResolution: 0.0001,
            maxResolution: 0.25,
            zoomFactor: 1.1+0.1*me.defaultzoomfactor   // (cioe' nel range 1.1 -> 2.1)
            // zoom: 22,
            // minZoom: 12,
            // maxZoom: 100,
            // zoomFactor: 1.12 // 1.0+(0.075*1)
        });
        me.mapView.setZoom(1.5);
        me.zoomFactorSliderValue = me.defaultzoomfactor;

        me.name ='mapviewwindow_' + me.id;

        me.items = [{
            region: 'center',
            layout: 'fit',
            items: [{
                xtype: 'container',
                reference: 'mapcontainer_' + me.id,
                id: 'mapcontainer_' + me.id,
                layout: 'fit',
                margin: 0
                // ,html: '<div id="mapview_' + me.id + '"></div>'
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
                alwaysOnTop: false,
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

                        btn.setPosition(me.getWidth() - 42, 120);
                    }
                },
                menu: {
                    // maxWidth: 200,
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
                        value: 1,
                        //step: 1,
                        increment: 1,
                        minValue: 1,
                        maxValue: 10,
                        tipText: function (thumb) {
                            return Ext.String.format('<b>{0}</b>', thumb.value);
                        },
                        listeners: {
                            changecomplete: function(menuitem, value, oldvalue){
                                //me.up().commonMapView.setProperties({zoomFactor: 1.1+(0.01*value)});
                                //me.up().commonMapView.set('zoomFactor', 1.1+(0.01*value), false);
                                var mapview_linked = true;
                                var mapViewWindows = Ext.ComponentQuery.query('mapview-window');
                                var properties = null;

                                mapview_linked = !me.lookupReference('toggleLink_btn_'+me.id.replace(/-/g,'_')).pressed;
                                if (mapview_linked){
                                    me.up().zoomFactorValue = value;
                                    me.up().zoomFactorSliderValue = value;

                                    properties = me.up().commonMapView.getProperties();
                                    properties['projection'] = me.projection;
                                    properties['displayProjection'] = me.projection;
                                    // properties['resolution'] = 0.1;
                                    properties['minResolution'] = 0.0001;
                                    properties['maxResolution'] = 0.25;
                                    properties['zoomFactor'] = 1.1+0.1*value;
                                    me.up().commonMapView = new ol.View(properties);
                                    // me.up().commonMapView.setProperties(properties)

                                    me.map.setView(me.up().commonMapView);
                                    if (esapp.Utils.objectExists(me.up().map)){
                                        me.up().map.setView(me.up().commonMapView);
                                    }

                                    Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                                        var mapview_window_linked = !mapview_window.lookupReference('toggleLink_btn_'+mapview_window.id.replace(/-/g,'_')).pressed;
                                        if (me != mapview_window && mapview_window_linked){
                                           mapview_window.map.setView(me.up().commonMapView);
                                           mapview_window.lookupReference('zoomfactorslider_' + mapview_window.id.replace(/-/g,'_')).setValue(value);
                                        }
                                    });
                                }
                                else {
                                    // me.mapView = new ol.View({
                                    //     projection:"EPSG:4326",
                                    //     displayProjection:"EPSG:4326",
                                    //     center: me.mapView.getCenter(),      // me.up().commonMapView.getCenter(),    // [20, -2],   // [20, -4.7],
                                    //     resolution: 0.1,
                                    //     minResolution: 0.0001,
                                    //     maxResolution: 0.25,
                                    //     zoomFactor: 1.1+0.1*value   // (cioe' nel range 1.1 -> 2.1)
                                    //     // zoom: me.up().commonMapView.getZoom(),
                                    //     // minZoom: 12,
                                    //     // maxZoom: 100,
                                    //     // zoomFactor: 1.1+(0.01*value)
                                    // });
                                    // me.mapView.set('zoomFactor', 1.1+0.1*value, false);

                                    properties = me.mapView.getProperties();
                                    properties['projection'] = me.projection;
                                    properties['displayProjection'] = me.projection;
                                    // properties['resolution'] = 0.1;
                                    properties['minResolution'] = 0.0001;
                                    properties['maxResolution'] = 0.25;
                                    properties['zoomFactor'] = 1.1+0.1*value;
                                    me.mapView = new ol.View(properties);

                                    me.zoomFactorSliderValue = value;
                                    me.map.setView(me.mapView);
                                }

                                // if (mapview_linked){
                                //     Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                                //         var mapview_window_linked = !mapview_window.lookupReference('toggleLink_btn_'+mapview_window.id.replace(/-/g,'_')).pressed;
                                //         if (me != mapview_window && mapview_window_linked){
                                //            mapview_window.map.setView(me.up().commonMapView);
                                //            mapview_window.lookupReference('zoomfactorslider_' + mapview_window.id.replace(/-/g,'_')).setValue(value);
                                //         }
                                //     });
                                // }
                            }
                        }
                    }]
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
                alwaysOnTop: false,
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
                        btn.setPosition(me.getWidth() - 42, 155);
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
                id: 'product-legend_' + me.id.replace(/-/g,'_'),
                reference: 'product-legend_' + me.id.replace(/-/g,'_'),
                showlegend: me.showlegend
            }, {
                xtype: 'maptitleobject',
                id: 'title_obj_' + me.id,
                reference: 'title_obj_' + me.id
            }, {
                xtype: 'mapdisclaimerobject',
                // id: 'disclaimer_obj_' + me.id,
                reference: 'disclaimer_obj_' + me.id
            }, {
                xtype: 'maplogoobject',
                // id: 'logo_obj_' + me.id,
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
            hidden: me.showtimeline ? false : true,
            hideMode : 'display',    //'display', 'visibility' 'offsets'
            frame:  false,
            shadow: false,
            border: false,
            bodyBorder: true,
            // style: {
            //     "border-top": '1px solid black;'
            // },
            header : false,
            collapsible: true,
            collapsed: me.showtimeline ? false : true,
            // collapseFirst: true,
            collapseDirection: 'bottom',
            collapseMode : "mini",  // The Panel collapses without a visible header.
            //headerPosition: 'left',
            // hideCollapseTool: false,        // me.productcode != '' ? false : true,
            split: true,
            splitterResize : false,
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'right',
                items: [{
                    xtype: 'button',
                    reference: 'refreshTimeLineBtn_' + me.id,
                    //scope: me,
                    tooltip: esapp.Utils.getTranslation('refresh_timeline'), // 'Refresh timeline'
                    iconCls: 'fa fa-refresh',
                    //style: { color: 'orange' },
                    glyph: null,
                    scale: null, // 'small',
                    padding: 0,
                    width: 21,
                    hidden: false,
                    handler: 'refreshTimeLine'
                }, {
                    xtype: 'splitbutton',
                    id: 'playBtn_' + me.id,
                    //reference: 'playBtn_' + me.id,
                    tooltip: esapp.Utils.getTranslation('play_visible_timeline'), // 'View product dates in visible timeline. Set delay below.'
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
                    tooltip: esapp.Utils.getTranslation('pause'), // 'Pause'
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
                    tooltip: esapp.Utils.getTranslation('stop'), // 'Stop'
                    iconCls: 'fa fa-stop',
                    style: {color: 'red'},
                    glyph: null,
                    scale: 'small',
                    hidden: true,
                    handler: 'stop'
                }, ' ', {
                    xtype: 'button',
                    id: 'dateLinkToggleBtn_' + me.id,
                    tooltip: esapp.Utils.getTranslation('link_unlink_timeline_from_other_mapview'), // 'Unlink/link the timeline from other mapviews.'
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
                beforerender: function(timeline){
                    // Ext.util.Observable.capture(timeline, function(e){console.log('timeline - ' + timeline.id + ': ' + e);});
                }
                ,beforeshow: function () {
                    me.setHeight(me.height+125);
                }
                ,show: function (timeline) {
                    // console.info(me);
                    var mapviewtimeline = me.lookupReference('product-time-line_' + me.id);
                    if (me.showtimeline) {
                        // mapviewtimeline.fireEvent('beforeexpand');
                        mapviewtimeline.fireEvent('expand');
                        // mapviewtimeline.expand();
                        // me.getController().redrawTimeLine(me);
                    }
                    // console.info('show');
                    // console.info(timeline);
                }
                ,beforeexpand: function () {
                    // console.info('beforeexpand Height to: ' + me.height+125);
                    me.setHeight(me.height+125);
                    // me.map.updateSize();
                }
                ,expand: function () {
                    // var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight-133];
                    // me.map.setSize(size);
                    me.map.updateSize();
                    // console.info('Expanding map size: ' + size);
                    me.getController().redrawTimeLine();
                }
                ,beforecollapse: function () {
                    var mapLegendObj = me.lookupReference('product-legend_' + me.id.replace(/-/g,'_')),
                        titleObj = me.lookupReference('title_obj_' + me.id),
                        disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                        logoObj = me.lookupReference('logo_obj_' + me.id),
                        scalelineObj = me.lookupReference('scale-line_' + me.id),
                        mapObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));

                    if (mapObjectToggleBtn.pressed) {
                        disclaimerObj.disclaimerPosition = disclaimerObj.getPosition(true);
                        titleObj.titlePosition = titleObj.getPosition(true);
                        logoObj.logoPosition = logoObj.getPosition(true);
                    }
                    if (!scalelineObj.hidden) {
                        scalelineObj.scalelinePosition = scalelineObj.getPosition(true);
                    }
                    if (!mapLegendObj.hidden) {
                        mapLegendObj.legendPosition = mapLegendObj.getPosition(true);
                    }
                    // console.info('beforecollapse Height to: ' + me.height-125);
                    me.setHeight(me.height-125);
                }
                ,collapse: function () {
                    var mapLegendObj = me.lookupReference('product-legend_' + me.id.replace(/-/g,'_')),
                        titleObj = me.lookupReference('title_obj_' + me.id),
                        disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                        logoObj = me.lookupReference('logo_obj_' + me.id),
                        scalelineObj = me.lookupReference('scale-line_' + me.id),
                        mapObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));

                    if (mapObjectToggleBtn.pressed) {
                        disclaimerObj.setPosition(disclaimerObj.disclaimerPosition);
                        titleObj.setPosition(titleObj.titlePosition);
                        logoObj.setPosition(logoObj.logoPosition);
                    }
                    if (!scalelineObj.hidden) {
                        scalelineObj.setPosition(scalelineObj.scalelinePosition);
                    }
                    if (!mapLegendObj.hidden) {
                        mapLegendObj.setPosition(mapLegendObj.legendPosition);
                    }
                    // var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight-8];   // -8
                    // me.map.setSize(size);
                    me.map.updateSize();
                    // console.info('Collapsing map size: ' + size);
                }
            }
            ,items: [{
                xtype: 'time-line-chart',
                id: 'time-line-chart' + me.id,
                reference: 'time-line-chart' + me.id,
                layout: 'fit'
            }]
        }];


        me.listeners = {
             beforedestroy: function(){
                // To fix the error: mapView.js?_dc=1506608907564:56 Uncaught TypeError: binding.destroy is not a function
                me.bind = null;
            }

            ,afterrender: function () {
                // Ext.util.Observable.capture(me, function(e){console.log('mapView - ' + me.id + ': ' + e);});

                var mousePositionControl = new ol.control.MousePosition({
                    coordinateFormat: function(coord) {
                        var stringifyFunc = ol.coordinate.createStringXY(3);
                        return ol.coordinate.toStringHDMS(coord) + ' (' + stringifyFunc(coord) + ')';
                    },
                    projection: me.projection,
                    // comment the following two lines to have the mouse position be placed within the map.
                    // className: 'ol-full-screen',
                    className: 'ol-custom-mouse-position',
                    target:  document.getElementById('mouse-position_'+ me.id), // Ext.get('mouse-position_'+ me.id), //
                    undefinedHTML: '&nbsp;'
                });

                me.map = new ol.Map({
                    target: 'mapcontainer_'+ me.id,
                    projection: me.projection,
                    displayProjection:"EPSG:4326",
                    //interactions: ol.interaction.defaults().extend([select]),
                    interactions : ol.interaction.defaults({doubleClickZoom :false}),
                    //layers: [blanklayer],
                    view: me.up().commonMapView,
                    controls: ol.control.defaults({
                        attribution:false,
                        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                            collapsible: false // false to show always without the icon.
                        })
                    }).extend([mousePositionControl])
                });

                // var graticule = new ol.Graticule({
                //     strokeStyle: new ol.style.Stroke({
                //       color: 'rgba(255,120,0,0.9)',
                //       width: 2,
                //       lineDash: [0.5, 4]
                //     }),
                //     showLabels: true,
                //     labelled: true
                // });
                // graticule.setMap(me.map);

                me.map.addInteraction(new ol.interaction.MouseWheelZoom({
                    duration: 25
                }));

                me.map.on('pointermove', function(evt) {
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

                me.map.on('click', function(evt) {
                    //var coordinate = evt.coordinate;
                    //overlay.setPosition(coordinate);
                    var drawgeometry_togglebtn = me.lookupReference('drawgeometry_'+me.id.replace(/-/g,'_'));
                    //if (!drawgeometry_togglebtn.pressed && me.map.getLayers().getArray().length > 2) {
                    if (!drawgeometry_togglebtn.pressed) {
                        me.getController().displaySelectedFeatureInfo(evt.pixel, true);
                    }
                });

                me.map.on('dblclick', function(evt) {
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


                me.productlayer = new ol.layer.Tile({       // Image
                    layer_id: 'productlayer',
                    layerorderidx: 100,
                    type: 'base',
                    visible: false
                });
                me.map.getLayers().insertAt(0, me.productlayer);


                me.drawfeatures = new ol.Collection();
                me.drawvectorlayer_source = new ol.source.Vector({
                    features: me.drawfeatures,
                    wrapX: false
                });
                me.drawvectorlayer = new ol.layer.Vector({
                    source: me.drawvectorlayer_source,
                    layer_id: 'drawvectorlayer',
                    layerorderidx: 1,
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
                me.map.getLayers().insertAt(10, me.drawvectorlayer);

                var featureOverlayStyle = (function() {
                    var styles = {};
                    styles['Polygon'] = [
                      new ol.style.Style({
                        fill: new ol.style.Fill({
                          color: [255, 255, 255, 0.2]    // 'Transparent'  //
                        })
                      }),
                      new ol.style.Style({
                        stroke: new ol.style.Stroke({
                          color: [0, 153, 255, 1],
                          width: 2
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
                          color: [0, 153, 255, 1],
                          width: 2
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
                          radius: 6,
                          fill: new ol.style.Fill({
                            color: [0, 153, 255, 1]
                          }),
                          stroke: new ol.style.Stroke({
                            color: [255, 0, 0, 0.75],
                            width: 2
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

                me.highlightfeatureOverlay_drawvectorlayer = new ol.layer.Vector({      //new ol.FeatureOverlay({
                    layer_id: 'highlightfeatureOverlay_drawvectorlayer',
                    source: new ol.source.Vector({
                        features: new ol.Collection(),
                        useSpatialIndex: false, // optional, might improve performance
                        wrapX: false,
                        noWrap: true
                    }),
                    updateWhileAnimating: true, // optional, for instant visual feedback
                    updateWhileInteracting: true, // optional, for instant visual feedback

                    map: me.map,
                    style: featureOverlayStyle
                });
                me.map.getLayers().insertAt(50, me.highlightfeatureOverlay_drawvectorlayer);

                var feature_selected_outlinecolor = '#FF0000'
                   ,feature_selected_outlinewidth = 2;
                var selectedFeatureOverlayStyle = (function() {
                    var styles = {};
                    styles['Polygon'] = [
                      new ol.style.Style({
                        fill: new ol.style.Fill({
                          color: 'Transparent'  // [255, 255, 255, 0.5]
                        })
                      }),
                      new ol.style.Style({
                        stroke: new ol.style.Stroke({
                          color: feature_selected_outlinecolor,         // layerrecord.get('feature_selected_outlinecolor'), // [255, 0, 0, 1],
                          width: feature_selected_outlinewidth          // layerrecord.get('feature_selected_outlinewidth')  // 3
                        })
                      })
                    ];
                    styles['MultiPolygon'] = styles['Polygon'];

                    styles['LineString'] = [
                      new ol.style.Style({
                        stroke: new ol.style.Stroke({
                          color: feature_selected_outlinecolor,         // layerrecord.get('feature_selected_outlinecolor'), // [255, 0, 0, 1],
                          width: feature_selected_outlinewidth          // layerrecord.get('feature_selected_outlinewidth')  // 3
                        })
                      })
                    ];
                    styles['MultiLineString'] = styles['LineString'];

                    styles['Point'] = [
                      new ol.style.Style({
                        image: new ol.style.Circle({
                          radius: 6,
                          fill: new ol.style.Fill({
                            color: 'Transparent'  // [0, 153, 255, 1]
                          }),
                          stroke: new ol.style.Stroke({
                            color: feature_selected_outlinecolor,       // layerrecord.get('feature_selected_outlinecolor'),   //[255, 0, 0, 0.75],
                            width: feature_selected_outlinewidth        // layerrecord.get('feature_highlight_outlinewidth')
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

                me.selectedfeatureOverlay_drawvectorlayer = new ol.layer.Vector({      //new ol.FeatureOverlay({
                    layer_id: 'selectedfeatureOverlay_drawvectorlayer',
                    source: new ol.source.Vector({
                        features: new ol.Collection(),
                        useSpatialIndex: false, // optional, might improve performance
                        wrapX: false,
                        noWrap: true
                    }),
                    updateWhileAnimating: true, // optional, for instant visual feedback
                    updateWhileInteracting: true, // optional, for instant visual feedback

                    map: me.map,
                    style: selectedFeatureOverlayStyle
                });
                me.map.getLayers().insertAt(60, me.selectedfeatureOverlay_drawvectorlayer);

                // me.el is not created until after the Window is rendered so you need to add the mon after rendering:
                me.mon(me.el, {
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
                                // var selectedregion = Ext.getCmp('selectedregionname');
                                // var wkt_polygon = Ext.getCmp('wkt_polygon');
                                var selectedregion = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('selectedregionname');
                                var wkt_polygon = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('wkt_polygon');
                                //me.selectedFeatureOverlay.getSource().removeFeature(me.selectedfeature);
                                me.drawvectorlayer.getSource().removeFeature(me.selectedfeature);
                                wkt_polygon.setValue('');
                                selectedregion.setValue('&nbsp;');
                                // Ext.getCmp('fieldset_selectedregion').hide();
                                me.selectedFeatureOverlay.getSource().clear();
                                me.selectedfeature = null;
                                me.getController().outmaskingPossible();
                            }
                        }
                    }
                });


                var mapLegendObj = me.lookupReference('product-legend_' + me.id.replace(/-/g,'_')),
                    titleObj = me.lookupReference('title_obj_' + me.id),
                    disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                    logoObj = me.lookupReference('logo_obj_' + me.id),
                    scalelineObj = me.lookupReference('scale-line_' + me.id),
                    mapObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_')),
                    mapviewLinkToggleBtn = me.lookupReference('toggleLink_btn_'+ me.id.replace(/-/g,'_'));

                if (me.isNewTemplate && me.workspace.workspaceid == "defaultworkspace"){
                    // Link Mapview window
                    mapviewLinkToggleBtn.toggle(false);
                }
                else {
                    // Unlink Mapview window
                    mapviewLinkToggleBtn.toggle(true);  // ('pressed', false);
                    // mapviewLinkToggleBtn.setIconCls('fa fa-chain-broken fa-2x red');
                }

                if (!me.nozoom){
                    if (esapp.Utils.objectExists(me.zoomextent) && me.zoomextent != null && me.zoomextent.trim() != ''){
                        // var taskZoom = new Ext.util.DelayedTask(function() {
                            var extent = me.zoomextent.split(",").map(Number);
                            var mapsize = (me.mapsize != null && me.mapsize.trim() != '') ? me.mapsize.split(",").map(Number) : [790, 778]; // /** @type {ol.Size} */ (me.map.getSize());
                            var mapcenter = (me.mapcenter != null && me.mapcenter.trim() != '') ? me.mapcenter.split(",").map(Number) : me.map.getView().getCenter();

                            // me.map.setView(me.mapView);
                            me.map.setSize(mapsize);
                            me.map.getView().setCenter(mapcenter);
                            me.map.getView().fit(extent, me.map.getSize(), {constrainResolution: false}); // Zoom to saved extent   , {size: me.map.getSize()}
                        // });
                        // taskZoom.delay(50);
                    }
                }

                var mapviewtimeline = me.lookupReference('product-time-line_' + me.id);
                if (esapp.Utils.objectExists(me.productcode) && me.productcode != ''){
                    mapviewtimeline.show();
                }
                else {
                    mapviewtimeline.hide();
                }

                if (esapp.Utils.objectExists(me.mapviewSize)){
                    me.setSize(me.mapviewSize[0],me.mapviewSize[1]);
                }
                if (esapp.Utils.objectExists(me.mapviewPosition)){
                    me.setPosition(me.mapviewPosition);
                }

                var mapToolbar = me.getDockedItems('toolbar[dock="top"]')[0];
                if (me.showtoolbar) {
                    mapToolbar.show();
                }
                else {
                    mapToolbar.hide();
                }

                if (esapp.Utils.objectExists(me.disclaimerObjPosition)){
                    disclaimerObj.disclaimerPosition = me.disclaimerObjPosition;
                    disclaimerObj.setHtml(me.disclaimerObjContent);
                    disclaimerObj.setContent(me.disclaimerObjContent);
                }

                if (esapp.Utils.objectExists(me.logosObjPosition)) {
                    logoObj.logoPosition = me.logosObjPosition;
                    // me.setLogoData(me.logosObjContent);
                    // logoObj.setLogoData(me.logosObjContent);
                    logoObj.getViewModel().data.logoData = me.logosObjContent;
                    logoObj.setLogoData(me.logosObjContent);
                }
                if (esapp.Utils.objectExists(me.scalelineObjPosition)) {
                    scalelineObj.scalelinePosition = me.scalelineObjPosition;
                }

                if (esapp.Utils.objectExists(me.titleObjPosition)){
                    titleObj.titlePosition = me.titleObjPosition;
                }
                if (esapp.Utils.objectExists(me.titleObjContent) && (me.titleObjContent.trim() != '' )){
                    titleObj.setTpl([]);    // empty template which must be an array
                    titleObj.setTpl(me.titleObjContent);
                    // titleObj.tpl.push(me.titleObjContent);
                    // titleObj.tpl.set(me.titleObjContent, true);
                }
                // else {
                //     titleObj.setTpl(['<div><span style="color:rgb(0,0,0); font-size: 20px; font-weight: bold;">{selected_area}</span></div><div><span style="color:rgb(0,0,0); font-size: 20px;">{product_name}</span></div><div><span style="color:rgb(51,102,255); font-size: 20px;">{product_date}</span></div>']);
                // }

                if (me.showObjects){
                    var taskToggleObjects = new Ext.util.DelayedTask(function() {
                        //console.info(mapObjectToggleBtn);
                        mapObjectToggleBtn.toggle(true);
                        me.getController().toggleObjects(mapObjectToggleBtn);
                    });
                    taskToggleObjects.delay(0);
                }

                Ext.fly('mapview_title_templatename_' + me.id).dom.innerHTML = me.templatename;
                //me.setTitle('<div id="mapview_title_templatename_' + me.id + '" class="map-templatename">' + me.templatename + '</div>');

                if (esapp.Utils.objectExists(me.productcode) && me.productcode != ''){
                    mapLegendObj.legendPosition = me.legendObjPosition;
                    mapLegendObj.legendLayout = me.legendlayout;
                    mapLegendObj.showlegend = me.showlegend;

                    // Ext.data.StoreManager.lookup('DataSetsStore').each(function(rec){
                    //     if (rec.get('productcode')== me.productcode && rec.get('version')== me.productversion ){
                    //         me.productsensor = rec.get('prod_descriptive_name');
                    //         if (esapp.Utils.objectExists(rec.get('productmapsets'))) {
                    //             rec.get('productmapsets').forEach(function (mapset) {
                    //                 if (mapset.mapsetcode == me.mapsetcode) {
                    //                     mapset.mapsetdatasets.forEach(function (mapsetdataset) {
                    //                         if (mapsetdataset.subproductcode == me.subproductcode) {
                    //                             me.productname = mapsetdataset.descriptive_name;
                    //                             me.date_format = mapsetdataset.date_format;
                    //                             me.frequency_id = mapsetdataset.frequency_id;
                    //                         }
                    //                     }, this);
                    //                 }
                    //             }, this);
                    //         }
                    //     }
                    // },this);

                    var productRec = Ext.data.StoreManager.lookup('DataSetsStore').findRecord('productid', me.productcode + '_' + me.productversion);
                    // console.info(productRec);
                    if (esapp.Utils.objectExists(productRec)) {
                        me.productsensor = productRec.get('prod_descriptive_name');
                        if (esapp.Utils.objectExists(productRec.get('productmapsets'))) {
                            productRec.get('productmapsets').forEach(function (mapset) {
                                if (mapset.mapsetcode == me.mapsetcode) {
                                    mapset.mapsetdatasets.forEach(function (mapsetdataset) {
                                        if (mapsetdataset.subproductcode == me.subproductcode) {
                                            me.productname = mapsetdataset.descriptive_name;
                                            me.date_format = mapsetdataset.date_format;
                                            me.frequency_id = mapsetdataset.frequency_id;
                                        }
                                    }, this);
                                }
                            }, this);
                        }
                    }

                    Ext.data.StoreManager.lookup('ColorSchemesStore').each(function(rec){
                        if (rec.get('legend_id')== me.legendid){
                            //me.colorschemeHTML = rec.get('colorschemeHTML');
                            me.legendHTML = rec.get('legendHTML');
                            me.legendHTMLVertical = rec.get('legendHTMLVertical');
                        }
                    },this);

                    var taskAddProductLayer = new Ext.util.DelayedTask(function() {
                        me.getController().addProductLayer(
                            me.productcode,
                            me.productversion,
                            me.mapsetcode,
                            me.subproductcode,
                            me.productdate,
                            me.legendid,
                            me.legendHTML,
                            me.legendHTMLVertical,
                            me.productname,
                            me.date_format,
                            me.frequency_id,
                            me.productsensor
                        );
                    });
                    taskAddProductLayer.delay(1000);
                }

                if (me.vectorLayers != null && me.vectorLayers.trim() != '') {
                    me.getController().loadLayersByID(me.vectorLayers.split(",").map(Number));
                }

                if (me.outmask && esapp.Utils.objectExists(me.outmaskFeature) && me.outmaskFeature != '' ){
                    var mapOutmaskToggleBtn = me.lookupReference('outmaskbtn_'+me.id.replace(/-/g,'_'));
                    var format = new ol.format.WKT();
                    me.selectedfeature = format.readFeature(me.outmaskFeature, {
                        dataProjection: 'EPSG:4326',
                        featureProjection: 'EPSG:4326'
                    });

                    mapOutmaskToggleBtn.toggle(true);
                    me.getController().toggleOutmask(mapOutmaskToggleBtn);
                }

                if (!me.isTemplate && me.isNewTemplate) {
                    me.getController().loadDefaultLayers();
                }

                //Ext.EventManager.on(me,'keypress',function(e){ alert( e.getKey() ) });
            }

            // The resize handle is necessary to set the map size!
            ,resize: function () {
                var size = [];
                if (me.productname == '' && me.productdate == '') {
                    size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight];
                }
                else {
                    if (me.lookupReference('product-time-line_' + me.id).collapsed != 'bottom' && !me.lookupReference('product-time-line_' + me.id).collapsed) {
                        size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight-133];
                    }
                    else {
                        size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight];
                    }
                }
                // size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight];
                // size = [document.getElementById('mapcontainer_'+me.id).offsetWidth, document.getElementById('mapcontainer_'+me.id).offsetHeight];
                // console.info('resize map size final: ' + size);
                me.map.setSize(size);
                me.map.updateSize();

                me.getController().redrawTimeLine();

                if (!me.lookupReference('opacityslider_' + me.id.replace(/-/g,'_')).hidden) {
                    me.lookupReference('opacityslider_' + me.id.replace(/-/g, '_')).setPosition(me.getWidth() - 42, 155);
                }
                //me.lookupReference('opacityslider_' + me.id.replace(/-/g,'_')).doConstrain();

                me.lookupReference('zoomFactorBtn_' + me.id.replace(/-/g, '_')).setPosition(me.getWidth() - 42, 120);
                me.updateLayout();
            }

            ,move: function () {
                me.getController().redrawTimeLine();
                // var productNavigatorBtn = me.lookupReference('productNavigatorBtn_'+me.id.replace(/-/g,'_'));
                // if (!me.mapViewProductNavigator.hidden){
                //     me.mapViewProductNavigator.hide();
                // }
                me.updateLayout();
                //console.info(me.getPosition(true));
            }

            ,maximize: function () {
                me.updateLayout();
            }

            ,restore: function () {
                //console.info(me.getPosition());
                //me.setPosition(me.getPosition()+1);
                me.updateLayout();
                var maplegendpanel = me.lookupReference('product-legend_panel_' + me.id);
                if (maplegendpanel != null){
                    maplegendpanel.doConstrain();
                }
            }

            ,close: function(){
                // var productNavigatorBtn = me.lookupReference('productNavigatorBtn_'+me.id.replace(/-/g,'_'));
                // if (!me.mapViewProductNavigator.hidden){
                //     me.mapViewProductNavigator.destroy();
                // }
                me.destroy();
            }

        };

        me.callParent();

    }
});
