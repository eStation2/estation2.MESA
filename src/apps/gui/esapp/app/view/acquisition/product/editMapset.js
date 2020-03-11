
Ext.define("esapp.view.acquisition.product.editMapset",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-editmapset",
    "viewModel": {
        "type": "acquisition-product-editmapset"
    },

    requires: [
        'esapp.view.acquisition.product.editMapsetController',
        'esapp.view.acquisition.product.editMapsetModel',

        'Ext.layout.container.Center'
    ],
    xtype: 'editmapset',

    title: esapp.Utils.getTranslation('editmapset'),
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    constrainHeader: true,
    //constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: false,
    autoScroll:true,
    maximizable: false,

    //width: 1100,
    height: Ext.getBody().getViewSize().height < 825 ? Ext.getBody().getViewSize().height-35 : 825,  // 600,
    maxHeight: 825,

    frame: true,
    border: false,
    bodyStyle: 'padding:5px 0px 0',

    viewConfig:{forceFit:true},
    layout:'fit',

    // session:true,

    params: {
        create: false,
        view: true,
        edit: false,
        mapsetrecord: null,
        mapsetcode: null
    },

    config: {
        projection: 'EPSG:4326',    // 'EPSG:3857',
        displayprojection: 'EPSG:4326',
        defaultzoomfactor: 1,
        layers: [],
        draw: null,
        drawnFeature: null,
        highlight: null
    },

    initComponent: function () {
        var me = this;
        var user = esapp.getUser();
        var labelwidth = 150;

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editmapset') + '</span>');
        }
        else if (me.params.view){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('viewmapset') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newmapset') + '</span>');
        }

        // Ext.util.Observable.capture(me, function(e){console.log(e);});

        me.bbar = [{
            text: esapp.Utils.getTranslation('save'),    // 'Save',
            iconCls: 'fa fa-save fa-2x',
            style: { color: 'lightblue' },
            scale: 'medium',
            disabled: false,
            formBind: true,
            hidden: me.params.view ? true : false,
            handler: 'onSaveClick'
        }];


        // var geometrytypes = Ext.create('Ext.data.ArrayStore', {
        //     fields: ['geometrytype','geometryname'],
        //     data: [
        //         // ['Polygon', 'Polygon'],
        //         // ['LineString', 'LineString'],
        //         // ['Point', 'Point'],
        //         //['Circle', 'Circle'],
        //         // ['Square', 'Square'],
        //         ['Box', 'Box']
        //         // ['None', 'None']
        //     ]
        // });
        //
        // var geometrytypescombo = Ext.create('Ext.form.field.ComboBox', {
        //     id: 'geometrytypes' + me.id,
        //     hideLabel: true,
        //     store: geometrytypes,
        //     displayField: 'geometryname',
        //     valueField: 'geometrytype',
        //     value: 'Box',
        //     typeAhead: true,
        //     queryMode: 'local',
        //     triggerAction: 'all',
        //     emptyText: esapp.Utils.getTranslation('select_geometry'),     // 'Select a geometry...',
        //     selectOnFocus: false,
        //     width: 100,
        //     indent: true,
        //     cls: "x-menu-no-icon",
        //     hidden: true,
        //     listeners: {
        //         change: function(newValue , oldValue , eOpts ){
        //             me.map.removeInteraction(me.draw);
        //             me.getController().addDrawInteraction(newValue);
        //         }
        //     }
        // });


        me.listeners = {
            show: function(){
                // console.info(me.params.create);
                if (me.params.create){
                    me.lookupReference('mapsetcode').setValue('');

                    me.map.updateSize();

                    me.drawvectorlayer.getSource().clear();
                    me.drawnFeature = null;
                    me.getController().addDrawInteraction();
                }
                // else {
                //     console.info(me.params.mapsetrecord);
                //     console.info(me.params.mapsetrecord.get('bboxcode'));
                //     console.info(me.params.mapsetrecord.get('mapsetcode'));
                //     if (me.params.mapsetrecord.get('bboxcode') == me.params.mapsetrecord.get('mapsetcode')){
                //         me.lookupReference('predefined_bbox').setValue(null);
                //         console.info(me.lookupReference('predefined_bbox'));
                //         console.info('predefined_bbox NULL');
                //     }
                // }
            },

            beforerender: function(){
                var taskBbox = new Ext.util.DelayedTask(function() {
                    var bboxcode = me.params.mapsetrecord.get('bboxcode');
                    var bboxstore = Ext.data.StoreManager.lookup('BboxStore');
                    // var bboxstore = me.lookupReference('predefined_bbox').getStore();

                    if (bboxstore.findRecord('bboxcode', bboxcode, 0, true, false, false)){
                        me.lookupReference('predefined_bbox').setValue(bboxcode);
                        me.lookupReference('bboxcodename').disable();
                    }

                    // bboxstore.getData().each(function(rec){
                    //     if (rec.get('bboxcode') == bboxcode){
                    //        console.info(me.lookupReference('predefined_bbox'));
                    //        me.lookupReference('predefined_bbox').setValue(bboxcode);
                    //     }
                    // });
                });
                taskBbox.delay(1000);
            },

            afterrender: function(){
                var online = window.navigator.onLine;

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

                me.drawfeatures = new ol.Collection();
                me.drawvectorlayer_source = new ol.source.Vector({
                    features: me.drawfeatures,
                    wrapX: false
                });

                var listenerKey = me.drawvectorlayer_source.on('change', function(e) {
                  if (me.drawvectorlayer_source.getState() == 'ready') {
                    var featureCount = me.drawvectorlayer_source.getFeatures().length;
                    // console.info(featureCount);
                    if(featureCount >= 1){
                         me.map.removeInteraction(me.draw);
                         me.draw = null;
                         // console.info(me.drawvectorlayer_source.getFeatures());
                         // console.info(me.drawvectorlayer_source.getFeatures()[0]);
                         me.drawnFeature = me.drawvectorlayer_source.getFeatures()[0];

                         // console.info(me.drawnFeature.getGeometry().getCoordinates()[0]);
                         var coordinates = me.drawnFeature.getGeometry().getCoordinates()[0];

                         var upper_left_long = coordinates[0][0];
                         var upper_left_lat = coordinates[0][1];
                         var lower_right_long = coordinates[2][0];
                         var lower_right_lat = coordinates[2][1];
                         if (me.lookupReference('upper_left_long').getValue() != upper_left_long){
                             me.lookupReference('upper_left_long').setValue(upper_left_long);
                         }
                         if (me.lookupReference('upper_left_lat').getValue() != upper_left_lat){
                             me.lookupReference('upper_left_lat').setValue(upper_left_lat);
                         }
                         if (me.lookupReference('lower_right_long').getValue() != lower_right_long){
                             me.lookupReference('lower_right_long').setValue(lower_right_long);
                         }
                         if (me.lookupReference('lower_right_lat').getValue() != lower_right_lat){
                             me.lookupReference('lower_right_lat').setValue(lower_right_lat);
                         }

                         me.getController().saveFootprintImage();
                    }
                    else {
                        me.getController().addDrawInteraction();
                        me.drawnFeature = null;
                    }
                    // ol.Observable.unByKey(listenerKey);
                    // use vectorSource.unByKey(listenerKey) instead
                    // if you do use the "master" branch of ol3
                  }
                });

                me.drawvectorlayer = new ol.layer.Vector({
                    source: me.drawvectorlayer_source,
                    layer_id: 'drawvectorlayer',
                    layerorderidx: 1,
                    layertype: 'drawvector',
                    feature_display_column: 'NAME',
                    style: new ol.style.Style({
                      fill: new ol.style.Fill({
                        color: 'rgba(253, 191, 111, 0.75)'
                      }),
                      stroke: new ol.style.Stroke({
                        color: '#FDBF6F',
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

                me.africacountryborders = new ol.layer.Vector({
                    source: new ol.source.Vector({      // ol.source.GeoJSON({
                        // projection: 'EPSG:4326', // 'EPSG:3857',
                        url: 'analysis/getvectorlayer?file=AFR_0_g2015_2014.geojson'
                        ,format: new ol.format.GeoJSON()
                        ,wrapX: false   // no repeat of layer when
                        ,noWrap: true
                    }),
                    visible: true,
                    style: new ol.style.Style({
                      fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.5)'
                      }),
                      stroke: new ol.style.Stroke({
                        color: '#000000',
                        width: 1
                      }),
                      image: new ol.style.Circle({
                        radius: 5,
                        fill: new ol.style.Fill({
                          color: '#ffcc33'
                        })
                      })
                    })
                });

                me.globalcountryborders = new ol.layer.Vector({
                    source: new ol.source.Vector({      // ol.source.GeoJSON({
                        // projection: 'EPSG:4326', // 'EPSG:3857',
                        url: 'analysis/getvectorlayer?file=countries.geojson'
                        ,format: new ol.format.GeoJSON()
                        ,wrapX: false   // no repeat of layer when
                        ,noWrap: true
                    }),
                    visible: false,
                    style: new ol.style.Style({
                      fill: new ol.style.Fill({
                        color: 'rgba(255, 255, 255, 0.5)'
                      }),
                      stroke: new ol.style.Stroke({
                        color: '#000000',
                        width: 1
                      }),
                      image: new ol.style.Circle({
                        radius: 5,
                        fill: new ol.style.Fill({
                          color: '#ffcc33'
                        })
                      })
                    })
                });

                me.overviewmapView = new ol.View({
                    projection: me.projection,
                    displayProjection: me.displayprojection
                    // zoom: 1,
                    // zoomFactor: 1.1+0.1*5,
                    // center: [20, -5]   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
                });
                // me.overviewmapView.calculateExtent([120,120]);

                me.overviewMap = new ol.Map({
                    target: 'footprint_image',
                    projection: me.projection,
                    displayProjection: me.displayprojection,
                    interactions : [],
                    view: me.overviewmapView,
                    controls: [],
                    layers: [
                        // new ol.layer.Tile({
                        //   source: new ol.source.OSM({
                        //     'url': 'https://{a-c}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png' +
                        //         '?apikey=65d35027bef048f79bbd786edabc39c4'
                        //   })
                        // }),
                        me.drawvectorlayer,
                        me.africacountryborders,
                        me.globalcountryborders
                    ]
                });

                // var overviewMapControl = new ol.control.OverviewMap({
                //     // see in overviewmap-custom.html to see the custom CSS used
                //     className: 'ol-overviewmap ol-custom-overviewmap',
                //     // mapOptions: {
                //     //     projection:"EPSG:4326",
                //     //     // restrictedExtent: nyc,
                //     //     maxResolution: 0.0015,
                //     //     numZoomLevels: 5
                //     // },
                //     layers: [
                //         // new ol.layer.Tile({
                //         //   source: new ol.source.OSM({
                //         //     'url': 'https://{a-c}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png' +
                //         //         '?apikey=65d35027bef048f79bbd786edabc39c4'
                //         //   })
                //         // }),
                //         new ol.layer.Vector({
                //             source: new ol.source.Vector({      // ol.source.GeoJSON({
                //                 // projection: 'EPSG:4326', // 'EPSG:3857',
                //                 url: 'analysis/getvectorlayer?file=AFR_0_g2015_2014.geojson'
                //                 ,format: new ol.format.GeoJSON()
                //                 ,wrapX: false   // no repeat of layer when
                //                 ,noWrap: true
                //             }),
                //             style: new ol.style.Style({
                //               fill: new ol.style.Fill({
                //                 color: 'rgba(255, 255, 255, 0.5)'
                //               }),
                //               stroke: new ol.style.Stroke({
                //                 color: '#000000',
                //                 width: 1
                //               }),
                //               image: new ol.style.Circle({
                //                 radius: 5,
                //                 fill: new ol.style.Fill({
                //                   color: '#ffcc33'
                //                 })
                //               })
                //             })
                //         }),
                //         me.drawvectorlayer
                //     ],
                //     collapseLabel: '\u00BB',
                //     label: '\u00AB',
                //     collapsed: false,
                //     collapsible: false,
                //     target: 'footprint_image',
                //     view: me.overviewmapView
                // });

                // var modify = new ol.interaction.Modify({
                //     features: me.drawfeatures,
                //     // the SHIFT key must be pressed to delete vertices, so
                //     // that new vertices can be drawn at the same position
                //     // of existing vertices
                //     deleteCondition: function(event) {
                //       return ol.events.condition.shiftKeyOnly(event) &&
                //           ol.events.condition.singleClick(event);
                //     }
                // });

                me.mapView = new ol.View({
                    projection: me.projection,
                    displayProjection: me.displayprojection,
                    center: [16.4, -0.5],   // [20, -4.7],   // ol.proj.transform([20, 4.5], 'EPSG:3857', 'EPSG:4326'),
                    // resolution: 0.1,
                    // minResolution: 0.0001,
                    // maxResolution: 0.25,
                    zoomFactor: 1.1+0.1*me.defaultzoomfactor   // (cioe' nel range 1.1 -> 2.1)
                    // zoom: 1
                    // minZoom: 12,
                    // maxZoom: 100,
                    // zoomFactor: 1.12 // 1.0+(0.075*1)
                });
                me.mapView.setZoom(10);

                me.map = new ol.Map({
                    target: 'mapbboxcontainer_'+ me.id,
                    projection: me.projection,
                    displayProjection: me.displayprojection,
                    interactions : ol.interaction.defaults({doubleClickZoom: true}),
                    view: me.mapView,
                    controls: ol.control.defaults({
                        attribution:false,
                        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                            collapsible: false // false to show always without the icon.
                        })
                    }).extend([mousePositionControl])
                });

                // Create the graticule component
                var graticule = new ol.Graticule({
                    // the style to use for the lines, optional.
                    strokeStyle: new ol.style.Stroke({
                      color: 'rgba(255,120,0,0.9)',
                      width: 1,
                      lineDash: [0.5, 4]
                    })
                });
                graticule.setMap(me.map);

                // me.map.addInteraction(new ol.interaction.MouseWheelZoom({
                //     duration: 25
                // }));

                // me.map.on('pointermove', function(evt) {
                //     if (evt.dragging) {
                //         return;
                //     }
                //     var pixel = me.map.getEventPixel(evt.originalEvent);
                //     me.getController().displayFeatureInfo(pixel, false);
                // });

                me.backgroundlayer = new ol.layer.Tile({
                      visible: true,
                      type: 'base',
                      projection: me.projection,
                      source: new ol.source.TileWMS({
                          url: 'analysis/getbackgroundlayer',   // 'http://demo.boundlessgeo.com/geoserver/wms',
                          params: {
                              layername:'naturalearth',
                              'LAYERS': 'HYP_HR_SR_OB_DR'       // 'ne:NE1_HR_LC_SR_W_DR'
                          },
                          wrapX: false,
                          noWrap: true
                    })
                 });

                me.osmlayer = new ol.layer.Tile({       // Image
                    // layer_id: 'OSMlayer',
                    // layerorderidx: 100,
                    // type: 'base',
                    // visible: true,
                    source: new ol.source.OSM({
                        wrapX: false,
                        noWrap: true
                    })
                });

                if(online){
                    me.backgroundlayer = me.osmlayer;
                }
                me.map.getLayers().insertAt(0, me.backgroundlayer);

                me.drawvectorlayer.setMap(me.map);
                // me.map.getLayers().insertAt(10, me.drawvectorlayer);

                // me.map.addInteraction(modify);  bboxcode

                me.getController().drawBBOX();

            },

            beforeclose: function(){
                if (Ext.data.StoreManager.lookup('MapsetsStore').getUpdatedRecords() !== []){
                    Ext.data.StoreManager.lookup('MapsetsStore').rejectChanges();
                }
                Ext.data.StoreManager.lookup('MapsetsStore').load();
            }
        };

        me.items = [{
            xtype: 'form',
            //bind: '{theMapset}',     // NO BIND otherwise does not work with formula on store.
            reference: 'mapsetform',
            border: false,
            // use the Model's validations for displaying form errors
            // modelValidation: true,
            fieldDefaults: {
                labelAlign: 'left',
                labelStyle: 'font-weight: bold;',
                msgTarget: 'side',
                preventMark: false
            },
            layout: {
                type: 'hbox'
                ,align: 'stretch'
            },
            items: [{
                xtype: 'fieldset',
                title: '<b>'+esapp.Utils.getTranslation('mapsetdefinition')+'</b>',    // '<b>Mapset definition</b>',
                collapsible: false,
                width: 610,
                margin: '10 5 10 10',
                padding: '10 10 10 10',
                defaults: {
                    width: 580,
                    labelWidth: labelwidth,
                    labelAlign: 'left',
                    // disabled: me.params.view ? true : false
                    editable: me.params.view ? false : true
                },
                items: [{
                    xtype: 'container',
                    layout: {
                        type: 'hbox'
                        , align: 'stretch'
                    },
                    margin: '0 5 10 0',
                    items: [{
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('mapsetcode'),    // 'Mapset code',
                        reference: 'mapsetcode',
                        labelWidth: 100,
                        flex: 1.5,
                        msgTarget: 'side',
                        bind: '{theMapset.mapsetcode}',
                        allowBlank: false,
                        disabled: (me.params.edit &&  esapp.Utils.objectExists(user) && user.userlevel != 1) ? true : false
                    }, {
                        xtype: 'combobox',
                        fieldLabel: esapp.Utils.getTranslation('definedby'),
                        reference: 'defined_by',
                        labelWidth: 100,
                        width: 100 + 100,
                        flex: 1,
                        margin: '0 0 10 30',
                        allowBlank: false,
                        bind: '{theMapset.defined_by}',
                        store: {
                            type: 'definedby'
                        },
                        valueField: 'defined_by',
                        displayField: 'defined_by_descr',
                        typeAhead: false,
                        queryMode: 'local',
                        emptyText: esapp.Utils.getTranslation('select'),    // 'Select...'
                        hidden: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? false : true
                    }]
                }, {
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('name'),    // 'Name',
                    reference: 'descriptive_name',
                    labelWidth: 100,
                    msgTarget: 'side',
                    bind: '{theMapset.descriptive_name}',
                    allowBlank: false
                }, {
                    xtype: 'htmleditor',
                    fieldLabel: esapp.Utils.getTranslation('description'),    // 'Description',
                    labelAlign: 'top',
                    reference: 'description',
                    msgTarget: 'side',
                    bind: {
                        value: '{theMapset.description}'
                    },
                    height: 130,
                    minHeight: 130,
                    scrollable: true,
                    allowBlank: true,
                    grow: true,
                    growMax: 130,
                    layout: 'fit',
                    resizable: true,
                    resizeHandles: 's',
                    style: 'background: white;',
                    hidden: false,
                    enableAlignments: false,
                    enableColors: true,
                    enableFont: true,
                    enableFontSize: true,
                    enableFormat: true,
                    enableLinks: false,
                    enableLists: false,
                    enableSourceEdit: true,
                    readOnly: me.params.view ? true : false
                },{
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('projection'),
                    reference: 'projection',
                    labelWidth: 100,
                    width: 200 + 100,
                    // margin: '0 0 5 80',
                    allowBlank: false,
                    disabled: me.params.view ? true : false,
                    bind: '{theMapset.proj_code}',
                    store: {
                        type: 'projections'
                    },
                    valueField: 'proj_code',
                    displayField: 'descriptive_name',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: esapp.Utils.getTranslation('select')    // 'Select...'
                // }, {
                //     xtype: 'textareafield',
                //     fieldLabel: esapp.Utils.getTranslation('coordinatesystem'),    // 'Coordinate System',
                //     labelAlign: 'top',
                //     reference: 'srs_wkt',
                //     allowBlank: false,
                //     bind: '{theMapset.srs_wkt}',
                //     msgTarget: 'side',
                //     minHeight: 120,
                //     shrinkWrap: 2,
                //     grow: true,
                //     growMax: 120,
                //     layout: 'fit',
                //     resizable: true,
                //     resizeHandles: 's',
                //     style: 'background: white;'
                }, {
                    xtype: 'container',
                    layout: {
                        type: 'vbox'
                        ,align: 'stretch'
                    },
                    items: [{
                        xtype: 'container',
                        layout: {
                            type: 'hbox'
                            , align: 'stretch'
                        },
                        items: [{
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('resolution'),
                            reference: 'resolution',
                            labelAlign: 'top',
                            labelWidth: 100,
                            width: 190,
                            padding: '0 10 0 0',
                            allowBlank: false,
                            disabled: me.params.view ? true : false,
                            bind: '{theMapset.resolutioncode}',
                            store: {
                                type: 'resolutions'
                            },
                            valueField: 'resolutioncode',
                            displayField: 'descriptive_name',
                            typeAhead: false,
                            forceSelection: true,
                            queryMode: 'local',
                            emptyText: esapp.Utils.getTranslation('select'),    // 'Select...'
                            listeners: {
                                select: function (ele, rec) {
                                    me.lookupReference('pixel_shift_lat').setValue(rec.get('pixel_shift_lat'));
                                    me.lookupReference('pixel_shift_long').setValue(rec.get('pixel_shift_long'));
                                    me.getController().drawBBOX();
                                }
                            }
                        }, {
                            xtype: 'displayfield',
                            fieldLabel: esapp.Utils.getTranslation('pixel_size_long'),
                            labelAlign: 'top',
                            reference: 'pixel_shift_long',
                            allowBlank: false,
                            padding: '0 10 0 0',
                            cls: 'greenbold',
                            width: 150,
                            bind: '{theMapset.pixel_shift_long}'
                        }, {
                            xtype: 'checkboxfield',
                            boxLabel: esapp.Utils.getTranslation('center_of_pixel'),
                            labelAlign: 'top',
                            reference: 'center_of_pixel',
                            inputValue: '0',
                            padding: '20 10 0 0',
                            width: 150,
                            bind: '{theMapset.center_of_pixel}',
                            listeners: {
                                change: function (ele, rec) {
                                    me.getController().drawBBOX();
                                }
                            }
                        },{
                            xtype: 'hiddenfield',
                            fieldLabel: esapp.Utils.getTranslation('pixel_size_lat'),
                            labelAlign: 'top',
                            reference: 'pixel_shift_lat',
                            allowBlank: false,
                            padding: '0 10 0 0',
                            cls: 'greenbold',
                            width: 150,
                            bind: '{theMapset.pixel_shift_lat}'
                        }]
                    },{
                        xtype: 'container',
                        layout: {
                            type: 'vbox'
                            ,align: 'stretch'
                        },
                        margin: '10 0 0 0',
                        items: [{
                            xtype: 'displayfield',
                            fieldLabel: esapp.Utils.getTranslation('pixel_size_x'),
                            labelAlign: 'left',
                            labelWidth: labelwidth,
                            reference: 'pixel_size_x',
                            allowBlank: false,
                            padding: '10 10 0 0',
                            margin: '0 0 0 0',
                            cls:'greenbold',
                            width: 250,
                            bind: '{theMapset.pixel_size_x}'

                        }, {
                            xtype: 'displayfield',
                            fieldLabel: esapp.Utils.getTranslation('pixel_size_y'),
                            labelAlign: 'left',
                            labelWidth: labelwidth,
                            reference: 'pixel_size_y',
                            allowBlank: false,
                            padding: '5 10 0 0',
                            margin: '0 0 0 0',
                            cls: 'greenbold',
                            width: 250,
                            bind: '{theMapset.pixel_size_y}'
                        // }, {
                        //     xtype: 'numberfield',
                        //     reference: 'pixel_size_x',
                        //     fieldLabel: esapp.Utils.getTranslation('pixel_size_x'),
                        //     width: 100 + labelwidth,
                        //     allowBlank: true,
                        //     maxValue: 99999999.99999,
                        //     minValue: -99999999.99999,
                        //     allowDecimals: true,
                        //     decimalPrecision: 5,
                        //     decimalSeparator: '.',
                        //     hideTrigger: false,
                        //     bind: '{theMapset.pixel_size_x}'
                        // }, {
                        //     xtype: 'numberfield',
                        //     reference: 'pixel_size_y',
                        //     fieldLabel: esapp.Utils.getTranslation('pixel_size_y'),
                        //     width: 100 + labelwidth,
                        //     allowBlank: true,
                        //     maxValue: 99999999.99999,
                        //     minValue: -99999999.99999,
                        //     allowDecimals: true,
                        //     decimalPrecision: 5,
                        //     decimalSeparator: '.',
                        //     hideTrigger: false,
                        //     bind: '{theMapset.pixel_size_y}'
                        }]
                    }]
                }, {
                    // xtype: 'container',
                    xtype: 'fieldset',
                    title: esapp.Utils.getTranslation('boundingbox'),
                    reference: 'boundingbox_fieldset',
                    collapsible: false,
                    margin: '15 10 5 0',
                    padding: '0 5 0 10',
                    layout: {
                        type: 'hbox'
                        ,align: 'stretch'
                    },
                    items: [{
                        xtype: 'container',
                        flex: 1,
                        layout: {
                            type: 'vbox'
                        },
                        padding: '0 5 0 0',
                        defaults: {
                            // disabled: me.params.view ? true : false,
                            editable: me.params.view ? false : true,
                            labelWidth: labelwidth
                        },

                        items: [{
                            xtype: 'textfield',
                            fieldLabel: esapp.Utils.getTranslation('bboxcodename'),    // 'Name',
                            reference: 'bboxcodename',
                            labelWidth: 100,
                            labelAlign: 'top',
                            msgTarget: 'side',
                            bind: '{theMapset.bboxcode}',
                            allowBlank: false
                        }, {
                            xtype: 'checkboxfield',
                            boxLabel: esapp.Utils.getTranslation('set_as_predefinedbbox'),
                            labelAlign: 'top',
                            reference: 'predefinedbbox',
                            inputValue: '0',
                            width: 200,
                            disabled: me.params.view ? true : false,
                            bind: '{theMapset.predefined}'
                        }, {
                            xtype: 'numberfield',
                            reference: 'upper_left_long',
                            fieldLabel: esapp.Utils.getTranslation('upper_left_long'),
                            width: 100 + labelwidth,
                            margin: '20 10 5 0',
                            allowBlank: false,
                            maxValue: 99999999.999,
                            minValue: -99999999.999,
                            allowDecimals: true,
                            decimalPrecision: 3,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theMapset.upper_left_long}',
                            listeners: {
                                change: 'drawBBOX',
                                keypress: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                },
                                spin: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                }
                            }
                        }, {
                            xtype: 'numberfield',
                            reference: 'lower_right_long',
                            fieldLabel: esapp.Utils.getTranslation('lower_right_long'),
                            width: 100 + labelwidth,
                            allowBlank: false,
                            maxValue: 99999999.999,
                            minValue: -99999999.999,
                            allowDecimals: true,
                            decimalPrecision: 3,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theMapset.lower_right_long}',
                            listeners: {
                                change: 'drawBBOX',
                                keypress: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                },
                                spin: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                }
                            }
                        }, {
                            xtype: 'numberfield',
                            reference: 'upper_left_lat',
                            fieldLabel: esapp.Utils.getTranslation('upper_left_lat'),
                            width: 100 + labelwidth,
                            allowBlank: false,
                            maxValue: 99999999.999,
                            minValue: -99999999.999,
                            allowDecimals: true,
                            decimalPrecision: 3,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theMapset.upper_left_lat}',
                            listeners: {
                                change: 'drawBBOX',
                                keypress: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                },
                                spin: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                }
                            }
                        }, {
                            xtype: 'numberfield',
                            reference: 'lower_right_lat',
                            fieldLabel: esapp.Utils.getTranslation('lower_right_lat'),
                            allowBlank: false,
                            width: 100 + labelwidth,
                            maxValue: 99999999.999,
                            minValue: -99999999.999,
                            allowDecimals: true,
                            decimalPrecision: 3,
                            decimalSeparator: '.',
                            hideTrigger: false,
                            bind: '{theMapset.lower_right_lat}',
                            listeners: {
                                change: 'drawBBOX',
                                keypress: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                },
                                spin: function(){
                                    var bboxcodename = me.lookupReference('bboxcodename');

                                    me.lookupReference('predefined_bbox').setValue(null);
                                    bboxcodename.enable();
                                    bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());
                                }
                            }
                        }]
                    }, {
                        xtype: 'container',
                        flex: 1.1,
                        layout: {
                            type: 'vbox'
                        },
                        padding: '0 10 0 0',
                        defaults: {
                            disabled: me.params.view ? true : false,
                            labelWidth: labelwidth
                        },
                        items: [{
                            xtype: 'combobox',
                            fieldLabel: esapp.Utils.getTranslation('predefined_bbox'),
                            reference: 'predefined_bbox',
                            labelAlign: 'top',
                            labelWidth: 100,
                            width: 250,
                            padding: '0 10 10 0',
                            // bind: '{theMapset.bboxcode}',
                            store: {
                                type: 'bbox'
                            },
                            editable: true,
                            valueField: 'bboxcode',
                            displayField: 'descriptive_name',
                            allowBlank: true,
                            typeAhead: true,
                            forceSelection: false,
                            queryMode: 'local',
                            // valueNotFoundText: 'value not found',
                            emptyText: esapp.Utils.getTranslation('select'),    // 'Select...'
                            listeners: {
                                select: function (ele, rec) {
                                    var bboxcodename = me.lookupReference('bboxcodename');
                                    bboxcodename.disable();

                                    bboxcodename.setValue(rec.get('bboxcode'));

                                    // empty values first to not have the bbox drawn 4 times
                                    me.lookupReference('upper_left_long').setValue(null);
                                    me.lookupReference('lower_right_long').setValue(null);
                                    me.lookupReference('upper_left_lat').setValue(null);
                                    me.lookupReference('lower_right_lat').setValue(null);

                                    me.lookupReference('upper_left_long').setValue(rec.get('upper_left_long'));
                                    me.lookupReference('lower_right_long').setValue(rec.get('lower_right_long'));
                                    me.lookupReference('upper_left_lat').setValue(rec.get('upper_left_lat'));
                                    me.lookupReference('lower_right_lat').setValue(rec.get('lower_right_lat'));
                                }
                            }
                        }, {
                            xtype: 'fieldset',
                            title: esapp.Utils.getTranslation('footprint_image'),
                            reference: 'footprint_image_fieldset',
                            flex: 1.2,
                            // width: 250,
                            height: 200,
                            layout: 'center',
                            collapsible: false,
                            // margin: '5 5 15 5',
                            padding: '10 10 10 10',
                            items: [{
                                // xtype: 'imagecomponent',
                                xtype: 'container',
                                id: 'footprint_image',
                                reference: 'footprint_image',
                                // bind: {
                                //     src: '{theMapset.footprint_image}'
                                // },
                                height: 155,
                                width: 180,
                                layout: 'center',
                                border: 1,
                                style: {
                                    borderColor: 'black',
                                    borderStyle: 'solid'
                                }
                            }]
                        }]
                    }]
                }]
            },{
                xtype: 'panel',
                title: '<b>'+esapp.Utils.getTranslation('draw_boundary_box')+'</b>',    // '<b>Draw boundary box</b>',
                collapsible: false,
                width: 600,
                // height: 490,
                layout: 'fit',
                frame: false,
                border: true,
                margin: '10 10 10 5',
                // padding: '10 10 10 10',
                tbar: Ext.create('Ext.toolbar.Toolbar', {
                    // dock: 'top',
                    autoShow: true,
                    alwaysOnTop: true,
                    floating: false,
                    hidden: false,
                    border: false,
                    shadow: false,
                    padding: 0,
                    items: [{
                        xtype: 'container',
                        autoWidth: true,
                        height: 37,
                        margin: '5 5 5 150',
                        // top: 0,
                        align: 'center',
                        defaults: {
                            style: {
                                "font-size": '14px',
                                "line-height": '18px'
                            }
                        },
                        items: [{
                            xtype: 'box',
                            height: 20,
                            top: 25,
                            html: '<div id="mouse-position_' + me.id + '"></div>'
                        }]
                    }, '->',
                    {
                        xtype: 'button',
                        text: esapp.Utils.getTranslation('reset'),   // 'Reset',
                        glyph: 'xf0e2@FontAwesome',
                        cls: 'red',
                        // iconCls: 'fa fa-undo',
                        style: {color: 'red'},
                        margin: '5 10 5 5',
                        //cls: 'x-menu-no-icon button-gray',
                        width: 80,
                        handler: function () {
                            var bboxcodename = me.lookupReference('bboxcodename');

                            me.lookupReference('predefined_bbox').setValue(null);
                            bboxcodename.enable();
                            bboxcodename.setValue(me.lookupReference('mapsetcode').getValue());

                            me.drawvectorlayer.getSource().clear();
                            me.drawnFeature = null;
                            me.getController().addDrawInteraction();
                        }

                        // {
                        // xtype: 'button',
                        // reference: 'drawgeometry_' + me.id.replace(/-/g, '_'),
                        // hidden: false,
                        // iconCls: 'polygon-gray',
                        // scale: 'medium',
                        // floating: false,  // usually you want this set to True (default)
                        // enableToggle: true,
                        // arrowVisible: false,
                        // arrowAlign: 'right',
                        // collapseDirection: 'left',
                        // menuAlign: 'tr-tl',
                        // handler: 'toggleDrawGeometry',
                        // listeners: {
                        //     afterrender: function (me) {
                        //         // Register the new tip with an element's ID
                        //         Ext.tip.QuickTipManager.register({
                        //             target: me.getId(), // Target button's ID
                        //             title: '',
                        //             text: esapp.Utils.getTranslation('draw_bbox')
                        //         });
                        //     }
                        //     , mouseover: function (btn, y, x) {
                        //         btn.showMenu();
                        //     }
                        // },
                        // menu: {
                        //     hideOnClick: true,
                        //     alwaysOnTop: true,
                        //     //iconAlign: '',
                        //     width: 125,
                        //     defaults: {
                        //         hideOnClick: true,
                        //         //cls: "x-menu-no-icon",
                        //         padding: 2
                        //     },
                        //     items: [
                        //         geometrytypescombo,
                        //         {
                        //             //xtype: 'button',
                        //             text: esapp.Utils.getTranslation('reset'),   // 'Reset',
                        //             glyph: 'xf0e2@FontAwesome',
                        //             cls: 'red',
                        //             // iconCls: 'fa fa-undo',
                        //             style: {color: 'red'},
                        //             //cls: 'x-menu-no-icon button-gray',
                        //             width: 60,
                        //             handler: function () {
                        //                 me.drawvectorlayer.getSource().clear();
                        //             }
                        //         }
                        //     ]
                        // }
                    }]
                }),
                items: [{
                    xtype: 'container',
                    id: 'mapbboxcontainer_' + me.id,
                    reference: 'mapbboxcontainer_' + me.id,
                    layout: 'fit',
                    margin: 0
                }]
            }]
        }];

        me.callParent();

    }

});
