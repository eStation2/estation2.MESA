
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
        'Ext.slider.Single',
        'Ext.grid.property.Grid',
        'Ext.picker.Color'
    ],

    //title: '<span class="panel-title-style">MAP title</span>',
    header: {
        titlePosition: 2,
        titleAlign: 'center'
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closeable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,

    width:700,
    height: Ext.getBody().getViewSize().height < 750 ? Ext.getBody().getViewSize().height-80 : 800,  // 600,

    minWidth:600,
    minHeight:350,

    // glyph : 'xf080@FontAwesome',
    margin: '0 0 0 0',
    layout: {
        type: 'border'
    },

    layers: [],
    projection: 'EPSG:4326',
    productdate: null,

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

    //listeners:{
    //  beforerender: function(){
    //      var me = this;
    //  }
    //},
    initComponent: function () {
        var me = this;

        me.layers = [];
        me.frame = false;
        me.border= true;
        me.bodyBorder = false;

        me.controller.createLayersMenu();


        me.mapView = new ol.View({
            projection:"EPSG:4326",
            displayProjection:"EPSG:4326",
            center: [20, -4.7],  // ol.proj.transform([21, 4], 'EPSG:4326', 'EPSG:3857'),
            zoom: 3.5
        });

        me.name ='mapviewwindow_' + me.id;

        me.items = [{
            region: 'center',
            items: [{
                xtype: 'container',
                reference:'mapcontainer_'+me.id,
                id:'mapcontainer_'+me.id,
                html: '<div id="mapview_' + me.id + '"></div>'
            }, {
                xtype: 'slider',
                // cls: 'custom-slider',
                id: 'opacityslider' + me.id,
                fieldLabel: '',
                labelStyle: {color: 'lightgray'},
                labelSeparator: '',
                labelWidth: 3,
                hideLabel: false,
                hideEmptyLabel: false,
                border: false,
                autoShow: true,
                floating: true,
                // alignTarget : me,
                defaultAlign: 'tl-tl',  // 'tr-c?',
                alwaysOnTop: true,
                constrain: true,
                width: 150,
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
            }, {
                title: "",
                id: 'product-legend_panel_' + me.id,
                reference: 'product-legend_panel_' + me.id,
                //x:10,
                autoWidth: true,
                autoHeight: true,
                layout: 'fit',
                hidden: true,
                floating: true,
                defaultAlign: 'bl-bl',
                closable: true,
                closeAction: 'hide',
                draggable: true,
                constrain: true,
                alwaysOnTop: true,
                autoShow: false,
                frame: false,
                frameHeader : false,
                border: false,
                shadow: false,
                //bodyStyle:  'background:transparent;',
                header: {
                    style: 'background:transparent;'
                },
                // Do not use default Panel dragging: use window type dragging
                // initDraggable: Ext.window.Window.prototype.initDraggable,
                // simpleDrag: true,
                listeners: {
                    close: function(){
                        var maplegend_togglebtn = me.lookupReference('legendbtn_'+me.id.replace(/-/g,'_')); //  + me.getView().id);
                        maplegend_togglebtn.show();
                        maplegend_togglebtn.toggle();
                    }
                },
                items: [{
                    xtype: 'container',
                    id: 'product-legend' + me.id,
                    reference: 'product-legend' + me.id,
                    //minWidth: 400,
                    layout: 'fit',
                    html: ''
                }]
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
                    className: 'ol-custom-mouse-position',
                    target:  document.getElementById('mouse-position_'+ me.id), // Ext.get('mouse-position_'+ me.id), //
                    undefinedHTML: '&nbsp;'
                });
                //console.info(me.getController());
                //this.layers = me.getController().addProductLayer();
                //var blanklayer = new ol.layer.Vector("none");   // {isBaseLayer: false, displayInLayerSwitcher: true}

                //var select = new ol.interaction.Select({
                //  wrapX: false
                //});

                this.scaleline = new ol.control.ScaleLine({
                  units: 'metric'       // 'degrees'  'nautical mile'
                });

                this.map = new ol.Map({
                    target: 'mapview_'+ this.id,
                    projection: me.projection,
                    displayProjection:"EPSG:4326",
                    //interactions: ol.interaction.defaults().extend([select]),
                    //layers: [blanklayer],
                    view: this.up().commonMapView,
                    controls: ol.control.defaults({
                        attribution:false,
                        attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
                            collapsible: false // false to show always without the icon.
                        })
                    }).extend([mousePositionControl, this.scaleline])
                });


                this.productlayer = new ol.layer.Tile({       // Image
                    layer_id: 'productlayer',
                    layerorderidx: 0,
                    type: 'base',
                    visible: false
                });
                this.map.getLayers().insertAt(0, this.productlayer);


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
                this.updateLayout();
            }
            ,move: function () {
                this.getController().redrawTimeLine(this);
                this.updateLayout();
            }
            ,maximize: function () {
                this.updateLayout();
            }
            ,restore: function () {
                //console.info(this.getPosition());
                //this.setPosition(this.getPosition()+1);
                this.updateLayout();
                var maplegendpanel = me.lookupReference('product-legend_panel_' + this.id);
                maplegendpanel.doConstrain();
            }
        };

        me.callParent();
    }
});
