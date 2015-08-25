
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

        'Ext.window.Window',
        'Ext.toolbar.Toolbar',
        'Ext.slider.Single'
    ],

    //title: '<span class="panel-title-style">MAP title</span>',
    margin: '0 0 0 0',
    layout: {
        type: 'border'
    },
    width:850,
    height:800,
    minWidth:400,
    minHeight:350,
    // glyph : 'xf080@FontAwesome',
    constrain: true,
    autoShow : false,
    closeable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,

    layers: [],
    projection: 'EPSG:4326',
    productdate: null,

    header: {
        titlePosition: 2,
        titleAlign: "center"
    },

    tools: [
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
    }],

    initComponent: function () {
        var me = this;

        me.layers = [];
        me.frame = false;
        me.border= false;
        me.bodyBorder = false;

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
                text: esapp.Utils.getTranslation('productnavigator'), // 'Product navigator',
                iconCls: 'africa',
                scale: 'medium',
                handler: 'openProductNavigator'
            },{
                xtype: 'button',
                //text: 'Add Layer',
                name:'vbtn-'+me.id,
                iconCls: 'layer-vector-add', // 'layers'
                scale: 'medium',
                //width: 100,
                //margin: '0 0 10 0',
                floating: false,  // usually you want this set to True (default)
                collapseDirection: 'left',
                menu: {
                    hideOnClick: true,
                    defaults: {
                        hideOnClick: true
                    },
                    items: [{
                        xtype: 'checkbox',
                        boxLabel: esapp.Utils.getTranslation('adminlevel0'), // 'Administative level 0',
                        //text: 'Administative level 0',
                        name: 'admin0',
                        level: 'admin0',
                        geojsonfile: 'AFR_G2014_2013_0.geojson',
                        checked: false,
                        linecolor: '#319FD3',    // rgb(49, 159, 211)
                        layerorderidx: 3,
                        showSeparator: false,
                        cls: "x-menu-no-icon",
                        handler: 'addVectorLayer'
                    }, {
                        xtype: 'checkbox',
                        boxLabel: esapp.Utils.getTranslation('adminlevel1'), // 'Administative level 1',
                        //text: 'Administative level 1',
                        name: 'admin1',
                        level: 'admin1',
                        geojsonfile: 'AFR_G2014_2013_1.geojson',
                        checked: false,
                        linecolor: '#ffcc00',    // rgb(255, 204, 0)
                        layerorderidx: 2,
                        showSeparator: false,
                        cls: "x-menu-no-icon",
                        handler: 'addVectorLayer'
                    }, {
                        text: 'RICs',
                        name: 'rics',
                        cls: "x-menu-no-icon",
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'ICPAC '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'icpac0',
                                level: 'admin0',
                                geojsonfile: 'AFR_G2014_2013_0.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'MOI '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'moi0',
                                level: 'admin0',
                                geojsonfile: 'AFR_G2014_2013_0.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'CICOS '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'cicos0',
                                level: 'admin0',
                                geojsonfile: 'AFR_G2014_2013_0.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }]
                }
            },{
                xtype: 'container',
                width: 275,
                height: 38,
                top: 0,
                align:'left',
                defaults: {
                    style: {
                        "font-size": '12px'
                    }
                },
                items: [{
                    xtype: 'box',
                    height: 17,
                    top:0,
                    html: '<div id="region_name_' + me.id + '" style="text-align:center; font-weight: bold;"></div>'
                },{
                    xtype: 'box',
                    height: 17,
                    top:17,
                    html: '<div id="mouse-position_' + me.id + '"></div>'
                }]
            },'->',{
                //text: 'Unlink',
                enableToggle: true,
                iconCls: 'unlink',
                scale: 'medium',
                handler: 'toggleLink'
            }]
        });

        me.mapView = new ol.View({
            projection:"EPSG:4326",
            displayProjection:"EPSG:4326",
            center: [21, 4],  // ol.proj.transform([21, 4], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4
        });

        me.name ='mapviewwindow_' + me.id;

        me.items = [{
            region: 'center',
            items: [{
                xtype: 'container',
                reference:'mapcontainer_'+me.id,
                html: '<div id="mapview_' + me.id + '"></div>'
            }, {
                xtype: 'slider',
                // cls: 'custom-slider',
                id: 'opacityslider' + me.id,
                fieldLabel: '',
                labelStyle: {color: 'lightgray'},
                labelSeparator: ' ',
                labelWidth: 5,
                hideLabel: false,
                hideEmptyLabel: false,
                border: false,
                autoShow: true,
                floating: true,
                // alignTarget : me,
                defaultAlign: 'tr-c?',
                alwaysOnTop: true,
                constrain: true,
                width: 180,
                value: 100,
                increment: 10,
                minValue: 0,
                maxValue: 100,
                tipText: function (thumb) {
                    return Ext.String.format('<b>{0}%</b>', thumb.value);
                },
                listeners: {
                    change: function (slider, newValue, thumb, eOpts) {
                        var _layers = me.map.getLayers();
                        _layers.a[0].setOpacity(newValue / 100)
                    }
                }
            }]
        },{
            region: 'south',
            //xtype: 'panel',
            id: 'product-time-line_' + me.id,
            reference: 'product-time-line_' + me.id,
            //title: 'Time Line',
            align:'left',
            autoWidth:true,
            margin:0,
            height: 115,
            maxHeight: 115,
            hidden: true,
            hideMode : 'display',
            frame:  false,
            border: false,
            bodyBorder: false,
            shadow: false,

            header : false,
            collapsible: true,
            collapsed: true,
            collapseFirst: true,
            collapseDirection: 'top',
            collapseMode : "mini",  // The Panel collapses without a visible header.
            //headerPosition: 'left',
            hideCollapseTool: true,
            split: true,
            splitterResize : false,
            listeners: {
                expand: function () {
                    var size = [document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight];
                    me.map.setSize(size);
                    me.getController().redrawTimeLine(me);
                }
            },
            items: [{
                xtype: 'time-line-chart',
                id: 'time-line-chart' + me.id,
                reference: 'time-line-chart' + me.id,
                layout: 'fit'
            }]
        }];

        me.listeners = {
            afterrender: function () {

                var mousePositionControl = new ol.control.MousePosition({
                    coordinateFormat: function(coord) {
                        var stringifyFunc = ol.coordinate.createStringXY(3);
                        return ol.coordinate.toStringHDMS(coord) + ' (' + stringifyFunc(coord) + ')';
                    },
                    projection: 'EPSG:4326',
                    // comment the following two lines to have the mouse position be placed within the map.
                    // className: 'ol-full-screen',
                    // className: 'custom-mouse-position',
                    target:  document.getElementById('mouse-position_'+ me.id), // Ext.get('mouse-position_'+ me.id), //
                    undefinedHTML: '&nbsp;'
                });
                //console.info(me.getController());
                //this.layers = me.getController().addProductLayer();
                this.map = new ol.Map({
                    target: 'mapview_'+ this.id,
                    projection: me.projection,
                    displayProjection:"EPSG:4326",
                    //layers: this.layers,
                    view: this.up().commonMapView,
                    controls: ol.control.defaults({
                        attribution:false,
                        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                            collapsible: false // false to show always without the icon.
                        })
                    }).extend([mousePositionControl])
                });

                //var layerSwitcher = new ol.control.LayerSwitcher({
                //    tipLabel: 'Layers' // Optional label for button
                //});
                //this.map.addControl(layerSwitcher);

                //this.map.getView().projection = me.projection;
                //console.info(Ext.getCmp('opacityslider'+ this.id));
                //console.info(this.layers[0]);
                //var opacity = new ol.dom.Input(document.getElementById('opacityslider'+ this.id));
                //opacity.bindTo('value', this.layers[0], 'opacity')
                //       .transform(parseFloat, String);

            }
            // The resize handle is necessary to set the map!
            ,resize: function () {
                var size = [document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight];
                this.map.setSize(size);

                this.getController().redrawTimeLine(this);
            }
            ,move: function () {
                this.getController().redrawTimeLine(this);
            }

        };

        me.callParent();
    }
});
