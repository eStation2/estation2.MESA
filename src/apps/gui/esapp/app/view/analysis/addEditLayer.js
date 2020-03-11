
Ext.define("esapp.view.analysis.addEditLayer",{
    "extend": "Ext.window.Window",
    "controller": "analysis-addeditlayer",
    "viewModel": {
        "type": "analysis-addeditlayer"
    },

    xtype: "addeditlayer",

    requires: [
        'esapp.view.analysis.addEditLayerModel',
        'esapp.view.analysis.addEditLayerController',

        'Ext.form.field.Hidden',
        'Ext.form.field.File',
        'Ext.form.FieldSet',
        'Ext.form.field.Number',
        'Ext.Action',

        'Ext.ux.colorpick.Field'
    ],

    session:true,

    title: '',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    constrainHeader: true,
    modal: true,
    closable: true,
    closeAction: 'destroy',
    resizable: true,
    autoScroll: true,
    maximizable: false,
    height: Ext.getBody().getViewSize().height < 575 ? Ext.getBody().getViewSize().height-10 : 575,
    maxHeight: 700,

    border: true,
    frame: true,
    fieldDefaults: {
        labelWidth: 120,
        labelAlign: 'left'
    },
    bodyPadding: '10 15 5 15',
    viewConfig: {forceFit:true},
    layout: 'hbox',

    params: {
        new: false,
        view: true,
        edit: false,
        layerrecord: null
    },

    initComponent: function () {
        var me = this;

        var colorrenderer = function(color) {
            var renderTpl = color;

            if (color.trim()==''){
                renderTpl = 'transparent';
            }
            else {
                renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
            }
            return renderTpl;
        };

        if (me.params.edit){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('editlayer') + '</span>');
        }
        else if (me.params.view){
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('viewlayer') + '</span>');
        }
        else {
            me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('newlayer') + '</span>');
        }

        me.listeners = {
            afterrender: function(){
                //console.info(me.getViewModel());
                //console.info(me.getViewModel().getData().layertypes);
                var layermenudata = [
                    {menu: 'border', menuname: esapp.Utils.getTranslation('borderlayers')},
                    {menu: 'marine', menuname: esapp.Utils.getTranslation('marinelayers')},
                    {menu: 'other', menuname: esapp.Utils.getTranslation('otherlayers')}
                ];
                var layertypesdata = [
                    {layertype: 'polygon', layertypename: 'Polygon'},
                    {layertype: 'line', layertypename: 'Line'},
                    {layertype: 'point', layertypename: 'Point'}
                ];
                me.getViewModel().getData().layertypes.setData(layertypesdata);
                me.getViewModel().getData().layermenu.setData(layermenudata);
            }
        };

        me.bbar = ['->',{
            xtype: 'button',
            text: esapp.Utils.getTranslation('import_layer_geojson_file'),
            //scope:me,
            iconCls: 'fa fa-upload fa-2x',    // 'icon-disk',
            style: {color: 'orange'},
            scale: 'medium',
            disabled: false,
            hidden: me.params.view ? true : false,
            handler: 'importLayer'
        },{
            xtype: 'button',
            text: esapp.Utils.getTranslation('save'),
            //scope:me,
            iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
            style: {color: 'lightblue'},
            scale: 'medium',
            disabled: false,
            hidden: me.params.view ? true : false,
            handler: 'saveLayerInfo'
        }];

        me.items = [{
            xtype: 'form',
            reference: 'layersform',
            border: false,
            // use the Model's validations for displaying form errors
            //modelValidation: true,
            fieldDefaults: {
                labelAlign: 'left',
                labelStyle: 'font-weight: bold;',
                msgTarget: 'right',
                preventMark: false
            },
            layout: 'hbox',


            items : [{
                margin:'0 15 5 0',
                xtype: 'fieldset',
                title: '<div class="grid-header-style">' + esapp.Utils.getTranslation('layersettings') + '</div>',
                collapsible: false,
                //width: 630,
                //height:500,
                padding: '10 10 10 10',
                //layout: 'fit',
                defaults: {
                    //autoWidth: true,
                    labelWidth: 120
                },
                items: [{
                    id: 'layername',
                    name: 'layername',
                    //bind: '{me.params.layerrecord.layername}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('layername'),
                    width: 120+430,
                    allowBlank: false,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'layerdescription',
                    name: 'layerdescription',
                    //bind: '{me.params.layerrecord.description}',
                    xtype: 'textareafield',
                    fieldLabel: esapp.Utils.getTranslation('description'),
                    labelAlign: 'top',
                    width: 120+430,
                    allowBlank: true,
                    grow: true,
                    disabled: me.params.view ? true : false
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        id: 'layer_filename',
                        name: 'layer_filename',
                        //bind: '{me.params.layerrecord.filename}',
                        xtype: 'textfield',
                        fieldLabel: esapp.Utils.getTranslation('layerfilename'),
                        labelWidth: 120,
                        width: 120+345,
                        allowBlank: false,
                        disabled: me.params.view ? true : false,
                        editable: false,
                        flex: 2.2
                    },{
                        xtype: 'button',
                        id: 'selectlayer-btn',
                        text: esapp.Utils.getTranslation('selectlayer'),    // 'Select layer',
                        qtip: esapp.Utils.getTranslation('selectlayerfile'),    // Select a .geojson layer file present on the server.
                        flex: 0.8,
                        //iconCls: 'fa fa-pencil-square-o',
                        style: { color: 'white' },
                        hidden: me.params.view ? true : false,
                        //scale: 'medium',
                        //scope:me,
                        handler: 'selectLayer'
                    }]
                }, {
                    id: 'feature_display_column',
                    name: 'feature_display_column',
                    //bind: me.params.layerrecord.feature_display_column,
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('feature_display_attributes'),
                    width: 120+430,
                    allowBlank: true,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'provider',
                    name: 'provider',
                    //bind: '{me.params.layerrecord.provider}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('provider'),
                    width: 120+430,
                    allowBlank: true,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'layertype',
                    name: 'layertype',
                    //bind: '{me.params.layerrecord.layertype}',
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('layertype'),
                    width: 120+120,
                    allowBlank: true,
                    disabled: me.params.view ? true : false,
                    bind: {
                        store: '{layertypes}'
                    },
                    //store: {
                    //    type: 'layertypes'
                    //},
                    valueField: 'layertype',
                    displayField: 'layertypename',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: esapp.Utils.getTranslation('selectalayertype')    // 'Select a layer type...'
                }, {
                    id: 'layerorderidx',
                    name: 'layerorderidx',
                    //bind: '{me.params.layerrecord.layerorderidx}',
                    xtype: 'numberfield',
                    fieldLabel: esapp.Utils.getTranslation('layerorderindex'),
                    width: 120+50,
                    allowBlank: false,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'layermenu',
                    name: 'layermenu',
                    //bind: '{me.params.layerrecord.menu}',
                    xtype: 'combobox',
                    fieldLabel: esapp.Utils.getTranslation('layermenu'),
                    width: 120+185,
                    allowBlank: false,
                    disabled: me.params.view ? true : false,
                    bind: {
                        store: '{layermenu}'
                    },
                    //store: {
                    //    type: 'layermenu'
                    //},
                    valueField: 'menu',
                    displayField: 'menuname',
                    typeAhead: false,
                    queryMode: 'local',
                    emptyText: esapp.Utils.getTranslation('selectamainmenu')    // 'Select a main menu...'

                }, {
                    id: 'layersubmenu',
                    name: 'layersubmenu',
                    //bind: '{me.params.layerrecord.submenu}',
                    xtype: 'textfield',
                    fieldLabel: esapp.Utils.getTranslation('layersubmenu'),
                    width: 120+430,
                    allowBlank: true,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'layerenabled',
                    name: 'layerenabled',
                    //bind: '{me.params.layerrecord.enabled}',
                    xtype: 'checkbox',
                    fieldLabel: esapp.Utils.getTranslation('layeractive'),
                    width: 120+50,
                    allowBlank: false,
                    disabled: me.params.view ? true : false
                }, {
                    id: 'open_in_mapview',
                    name: 'open_in_mapview',
                    //bind: '{me.params.layerrecord.open_in_mapview}',
                    xtype: 'checkbox',
                    fieldLabel: esapp.Utils.getTranslation('by_default_open_layer_in_mapviews'),
                    width: 120+50,
                    allowBlank: false,
                    disabled: me.params.view ? true : false
                    //labelAlign: 'top'
                }]
            },{
                xtype: 'fieldset',
                title: '<div class="grid-header-style">' + esapp.Utils.getTranslation('draw_properties') + '</div>',
                collapsible: false,
                width: 400,
                //height:500,
                padding: '10 5 10 10',
                //layout: 'fit',
                defaults: {
                    //autoWidth: true,
                    labelWidth: 120
                },
                disabled: me.params.view ? true : false,

                items: [{
                    xtype: 'propertygrid',
                    //nameField: 'Property',
                    //width: 400,
                    nameColumnWidth: 230,
                    sortableColumns: false,
                    forceFit: true,
                    source: {
                        polygon_outlinecolor: esapp.Utils.convertRGBtoHex(me.params.layerrecord.get('polygon_outlinecolor')),
                        polygon_outlinewidth: me.params.layerrecord.get('polygon_outlinewidth'),
                        feature_highlight_outlinecolor: esapp.Utils.convertRGBtoHex(me.params.layerrecord.get('feature_highlight_outlinecolor')),
                        feature_highlight_outlinewidth: me.params.layerrecord.get('feature_highlight_outlinewidth'),
                        feature_highlight_fillcolor: esapp.Utils.convertRGBtoHex(me.params.layerrecord.get('feature_highlight_fillcolor')),
                        feature_highlight_fillopacity: me.params.layerrecord.get('feature_highlight_fillopacity'),
                        feature_selected_outlinecolor: esapp.Utils.convertRGBtoHex(me.params.layerrecord.get('feature_selected_outlinecolor')),
                        feature_selected_outlinewidth: me.params.layerrecord.get('feature_selected_outlinewidth')
                    },
                    sourceConfig: {
                        polygon_outlinecolor: {
                            //type: 'colorfield',
                            displayName: esapp.Utils.getTranslation('outline_colour'),     // 'Outline colour',
                            editor: {
                                // xtype: 'mycolorpicker'
                                xtype: 'mycolorselector'
                                //format: '#HEX6'
                            }
                            ,renderer: colorrenderer
                        },
                        polygon_outlinewidth: {
                            displayName: esapp.Utils.getTranslation('outline_width'),     // 'Outline width',
                            type: 'number'
                        },
                        feature_highlight_outlinecolor: {
                            displayName: esapp.Utils.getTranslation('highlight_outline_colour'),     // 'Highlight outline colour',
                            editor: {
                                // xtype: 'mycolorpicker'
                                xtype: 'mycolorselector'
                                //format: '#HEX6'
                            }
                            ,renderer: colorrenderer
                        },
                        feature_highlight_outlinewidth: {
                            displayName: esapp.Utils.getTranslation('highlight_outline_width'),     // 'Highlight outline width',
                            type: 'number'
                        },
                        feature_highlight_fillcolor: {
                            displayName: esapp.Utils.getTranslation('highlight_fill_colour'),     // 'Highlight fill colour',
                            editor: {
                                // xtype: 'mycolorpicker'
                                xtype: 'mycolorselector'
                                //format: '#HEX6'
                            }
                            ,renderer: colorrenderer
                        },
                        feature_highlight_fillopacity: {
                            displayName: esapp.Utils.getTranslation('highlight_fill_opacity'),     // 'Highlight fill opacity',
                            editor: {
                                xtype: 'combobox',
                                store: [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],
                                forceSelection: true
                            }
                        },
                        feature_selected_outlinecolor: {
                            displayName: esapp.Utils.getTranslation('selected_feature_outline_colour'),     // 'Selected feature outline colour',
                            editor: {
                                // xtype: 'mycolorpicker'
                                xtype: 'mycolorselector'
                                //format: '#HEX6'
                            }
                            ,renderer: colorrenderer
                        },
                        feature_selected_outlinewidth: {
                            displayName: esapp.Utils.getTranslation('selected_feature_outline_width'),     // 'Selected feature outline width',
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
                            if (value != oldValue) {
                                me.params.layerrecord.set(recordId, value)
                            }
                        }
                    }
                }]
            }]
        }];

        me.callParent();

        me.controller.setup();

    }
});
