
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

    width:660,
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
                text: '<div style="font-size: 11px;">' + esapp.Utils.getTranslation('productnavigator') + '</div>', // 'Product navigator',
                iconCls: 'africa',
                scale: 'medium',
                //style: {
                //    "font-size": '10px'
                //},
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
                    iconAlign: '',
                    defaults: {
                        hideOnClick: true,
                        iconAlign: ''
                    },
                    items: [{
                        text: 'Africa',
                        name: 'africa',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: esapp.Utils.getTranslation('adminlevel0'), // 'Administative level 0',
                                //text: 'Administative level 0',
                                name: 'admin0',
                                level: 'admin0',
                                geojsonfile: 'AFR_G2014_2013_0.geojson', // 'AFR_0_g2015_2014.geojson',  //
                                checked: false,
                                linecolor: '#319FD3',    // rgb(49, 159, 211)  or like in EMMA rgb(255, 0, 255)
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                hideOnClick: true,
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: esapp.Utils.getTranslation('adminlevel1'), // 'Administative level 1',
                                //text: 'Administative level 1',
                                name: 'admin1',
                                level: 'admin1',
                                geojsonfile: 'AFR_G2014_2013_0.geojson',  // 'AFR_1_g2015_2014.geojson',  //
                                checked: false,
                                linecolor: '#ffcc00',    // rgb(255, 204, 0)
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            //}, {
                            //    xtype: 'checkbox',
                            //    boxLabel: esapp.Utils.getTranslation('adminlevel2'), // 'Administative level 1',
                            //    //text: 'Administative level 1',
                            //    name: 'admin2',
                            //    level: 'admin2',
                            //    geojsonfile: 'AFR_G2014_2013_2.geojson',
                            //    checked: false,
                            //    linecolor: '#ffcc99',    // rgb(255, 204, 153)
                            //    layerorderidx: 1,
                            //    showSeparator: false,
                            //    cls: "x-menu-no-icon",
                            //    handler: 'addVectorLayer'
                            }]
                        }
                    //}, {
                    //    text: 'ACMAD',
                    //    name: 'acmad',
                    //    //iconCls: 'layer-vector-add', // 'layers'
                    //    scale: 'medium',
                    //    floating: false,
                    //    collapseDirection: 'left',
                    //    menu: {
                    //        hideOnClick: true,
                    //        defaults: {
                    //            hideOnClick: true
                    //        },
                    //        style: {
                    //            'margin-left': '0px'
                    //        },
                    //        items: [{
                    //            xtype: 'checkbox',
                    //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level0'), // level 0',
                    //            name: 'acmad0',
                    //            level: 'admin0',
                    //            geojsonfile: 'AFR_0_g2015_2014.geojson',
                    //            checked: false,
                    //            linecolor: '#319FD3',
                    //            layerorderidx: 3,
                    //            showSeparator: false,
                    //            cls: "x-menu-no-icon",
                    //            handler: 'addVectorLayer'
                    //        }, {
                    //            xtype: 'checkbox',
                    //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level1'), // level 0',
                    //            name: 'acmad1',
                    //            level: 'admin1',
                    //            geojsonfile: 'AFR_1_g2015_2014.geojsonn',
                    //            checked: false,
                    //            linecolor: '#ffcc00',
                    //            layerorderidx: 2,
                    //            showSeparator: false,
                    //            cls: "x-menu-no-icon",
                    //            handler: 'addVectorLayer'
                    //        }, {
                    //            xtype: 'checkbox',
                    //            boxLabel: 'ACMAD '+esapp.Utils.getTranslation('level2'), // level 0',
                    //            name: 'acmad2',
                    //            level: 'admin2',
                    //            geojsonfile: 'AFR_2_g2015_2014.geojson',
                    //            checked: false,
                    //            linecolor: '#ffcc99',
                    //            layerorderidx: 1,
                    //            showSeparator: false,
                    //            cls: "x-menu-no-icon",
                    //            handler: 'addVectorLayer'
                    //        }]
                    //    }
                    }, {
                        text: 'AGRHYMET',
                        name: 'agrhymet',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'AGRHYMET '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'agrhymet0',
                                level: 'admin0',
                                geojsonfile: 'RIC_CRA_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'AGRHYMET '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'agrhymet1',
                                level: 'admin1',
                                geojsonfile: 'RIC_CRA_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'AGRHYMET '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'agrhymet2',
                                level: 'admin2',
                                geojsonfile: 'RIC_CRA_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }, {
                        text: 'BDMS',
                        name: 'bdms',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'BDMS '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'bdms0',
                                level: 'admin0',
                                geojsonfile: 'RIC_BDMS_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'BDMS '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'bdms1',
                                level: 'admin1',
                                geojsonfile: 'RIC_BDMS_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'BDMS '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'bdms2',
                                level: 'admin2',
                                geojsonfile: 'RIC_BDMS_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }, {
                        text: 'CICOS',
                        name: 'cicos',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'CICOS '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'cicos0',
                                level: 'admin0',
                                geojsonfile: 'RIC_CICOS_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'CICOS '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'cicos1',
                                level: 'admin1',
                                geojsonfile: 'RIC_CICOS_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'CICOS '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'cicos2',
                                level: 'admin2',
                                geojsonfile: 'RIC_CICOS_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }, {
                        text: 'ICPAC',
                        name: 'icpac',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'ICPAC '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'icpac0',
                                level: 'admin0',
                                geojsonfile: 'RIC_ICPAC_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'ICPAC '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'icpac1',
                                level: 'admin1',
                                geojsonfile: 'RIC_ICPAC_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'ICPAC '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'icpac2',
                                level: 'admin2',
                                geojsonfile: 'RIC_ICPAC_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }, {
                        text: 'MOI',
                        name: 'moi',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'MOI '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'moi0',
                                level: 'admin0',
                                geojsonfile: 'RIC_MOI_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'MOI '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'moi1',
                                level: 'admin1',
                                geojsonfile: 'RIC_MOI_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'MOI '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'moi2',
                                level: 'admin2',
                                geojsonfile: 'RIC_MOI_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }, {
                        text: 'University of Ghana',
                        name: 'UoG',
                        //iconCls: 'layer-vector-add', // 'layers'
                        scale: 'medium',
                        floating: false,
                        collapseDirection: 'left',
                        menu: {
                            hideOnClick: true,
                            defaults: {
                                hideOnClick: true
                            },
                            style: {
                                'margin-left': '0px'
                            },
                            items: [{
                                xtype: 'checkbox',
                                boxLabel: 'UoG '+esapp.Utils.getTranslation('level0'), // level 0',
                                name: 'UoG0',
                                level: 'admin0',
                                geojsonfile: 'RIC_UOG_0_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#319FD3',
                                layerorderidx: 3,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'UoG '+esapp.Utils.getTranslation('level1'), // level 0',
                                name: 'UoG1',
                                level: 'admin1',
                                geojsonfile: 'RIC_UOG_1_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc00',
                                layerorderidx: 2,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }, {
                                xtype: 'checkbox',
                                boxLabel: 'UoG '+esapp.Utils.getTranslation('level2'), // level 0',
                                name: 'UoG2',
                                level: 'admin2',
                                geojsonfile: 'RIC_UOG_2_g2015_2014.geojson',
                                checked: false,
                                linecolor: '#ffcc99',
                                layerorderidx: 1,
                                showSeparator: false,
                                cls: "x-menu-no-icon",
                                handler: 'addVectorLayer'
                            }]
                        }
                    }]
                }
            },{
                xtype: 'container',
                width: 260,
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
