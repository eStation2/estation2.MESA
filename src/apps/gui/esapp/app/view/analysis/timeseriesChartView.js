
Ext.define("esapp.view.analysis.timeseriesChartView",{
    "extend": "Ext.window.Window",
    "controller": "analysis-timeserieschartview",
    "viewModel": {
        "type": "analysis-timeserieschartview"
    },

    xtype: 'timeserieschart-window',

    requires: [
        'esapp.view.analysis.timeseriesChartViewModel',
        'esapp.view.analysis.timeseriesChartViewController',
        'esapp.view.analysis.mapDisclaimerObject',
        "esapp.view.analysis.mapLogoObject",

        'Ext.window.Window',
        'Ext.toolbar.Toolbar'
    ],

    title: '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>',
    header: {
        titlePosition: 2,
        titleAlign: "left",
        cls: 'graphview-header'
    },
    constrainHeader: true,
    //constrain: true,
    autoShow : false,
    closable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: true,
    collapsible: true,
    resizable: true,
    shadow: false,
    componentCls: 'rounded-box-win',

    width:700,
    height: Ext.getBody().getViewSize().height < 600 ? Ext.getBody().getViewSize().height-80 : 600,
    minWidth:400,
    minHeight:350,
    x: 50,
    y: 5,

    // glyph : 'xf080@FontAwesome',

    margin: '0 0 0 0',
    layout: {
        type: 'fit'
    },

    config: {
        workspace: null,
        isNewTemplate: true,
        isTemplate: false,
        graph_tpl_id: null,
        parent_tpl_id: null,
        graph_tpl_name: '',
        link_region_change: false,

        tsgraph: null,
        selectedTimeseries: null,
        yearTS: null,
        tsFromPeriod: null,
        tsToPeriod: null,
        yearsToCompare: null,
        tsFromSeason: null,
        tsToSeason: null,
        selectedregionname: null,
        wkt_geom: null,
        graphtype: null,
        timeseriesChart: {},
        timeseriesGraph: {}
    },

    listeners: {
        beforerender: function () {
            var me = this;

            if (me.graphtype != 'scatter'){
                var selectedProductsAndTimeFramePanel = me.getController().createSelectedProductsAndTimeFramePanel();
                me.add(selectedProductsAndTimeFramePanel);

                selectedProductsAndTimeFramePanel.down('timeseriesproductselection').fireEvent('beforerender');
            }
        },
        afterrender: function () {
            var me = this,
                disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
                logoObj = me.lookupReference('logo_obj_' + me.id),
                graphObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));

            // if (me.isTemplate){
                if (esapp.Utils.objectExists(me.graphviewsize)){
                    me.setSize(me.graphviewsize[0],me.graphviewsize[1]);
                }
                if (esapp.Utils.objectExists(me.graphviewposition)){
                   me.setPosition(me.graphviewposition);
                }

                me.updateLayout();

                if (esapp.Utils.objectExists(me.disclaimerObjPosition) && esapp.Utils.objectExists(me.disclaimerObjContent)) {
                    disclaimerObj.disclaimerPosition = me.disclaimerObjPosition;
                    disclaimerObj.setHtml(me.disclaimerObjContent);
                    disclaimerObj.setContent(me.disclaimerObjContent);
                }

                if (esapp.Utils.objectExists(me.logosObjPosition)) {
                    logoObj.logoPosition = me.logosObjPosition;
                    if (esapp.Utils.objectExists(me.logosObjContent)) {
                        logoObj.getViewModel().data.logoData = me.logosObjContent;
                    }
                }

                // titleObj.titlePosition = me.titleObjPosition;
                // if (me.titleObjContent != null && me.titleObjContent.trim() != ''){
                //     titleObj.setTpl([]);    // empty template which must be an array
                //     titleObj.setTpl(me.titleObjContent);
                //     // titleObj.tpl.push(me.titleObjContent);
                //     // titleObj.tpl.set(me.titleObjContent, true);
                // }
                // if (me.showObjects){
                //     var taskToggleObjects = new Ext.util.DelayedTask(function() {
                //         graphObjectToggleBtn.toggle(true);
                //         me.getController().toggleObjects(graphObjectToggleBtn);
                //     });
                //     taskToggleObjects.delay(1000);
                // }

                me.getController().generateChart();
            // }
            // else {
            //     me.getController().generateChart();
            // }
        }
        // The resize handle is necessary to set the map!
        ,resize: function () {
            var me = this;
            if( me.tsgraph instanceof Highcharts.Chart){
                me.tsgraph.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tsgraph.redraw();
            }
        }
        ,move: function () {
            var me = this;
            if( me.tsgraph instanceof Highcharts.Chart){
                me.tsgraph.setSize(document.getElementById(this.id + "-body").offsetWidth, document.getElementById(this.id + "-body").offsetHeight);
                me.tsgraph.redraw();
            }
        }
    },

    initComponent: function () {
        var me = this;
        // Ext.util.Observable.capture(me, function(e){console.log('grapview - ' + me.id + ': ' + e);});

        // me.title = '<span class="panel-title-style">'+esapp.Utils.getTranslation('timeseries')+'</span>';
        me.title = '<span id="graphview_title_' + me.id + '">'+esapp.Utils.getTranslation('timeseries')+'</span>' +
                   '<span id="graphview_title_templatename_' + me.id + '" class="graph-templatename"></span>';

        //me.height = Ext.getBody().getViewSize().height-80;
        me.frame = false;
        me.border= false;
        me.bodyBorder = false;

        me.link_region_change = false;
        me.wkt_geom = this.wkt_geom;

        me.tools = [
        {
            type: 'gear',
            tooltip: esapp.Utils.getTranslation('graphshowhidetools'),  // 'Show/hide graph tools menu',
            callback: function (tswin) {
                // toggle hide/show toolbar and adjust map size.
                var winBodyWidth = tswin.getWidth()-5;
                var winBodyHeight = tswin.getHeight()-45;
                var tsToolbar = tswin.getDockedItems('toolbar[dock="top"]')[0];
                var widthToolbar = tsToolbar.getWidth();
                var heightToolbar = tsToolbar.getHeight();
                if (tsToolbar.hidden == false) {
                    tsToolbar.setHidden(true);
                    winBodyWidth = document.getElementById(tswin.id + "-body").offsetWidth;
                    winBodyHeight =  document.getElementById(tswin.id + "-body").offsetHeight; //+heightToolbar;
                }
                else {
                    tsToolbar.setHidden(false);
                    winBodyWidth = document.getElementById(tswin.id + "-body").offsetWidth;
                    winBodyHeight = document.getElementById(tswin.id + "-body").offsetHeight-heightToolbar;
                }
                tswin.tsgraph.setSize(winBodyWidth, winBodyHeight);
                tswin.tsgraph.redraw();
            }
        }];

        me.tbar = Ext.create('Ext.toolbar.Toolbar', {
            id: 'tbar_'+me.id,
            reference: 'tbar_'+me.id,
            dock: 'top',
            autoShow: true,
            alwaysOnTop: true,
            floating: false,
            hidden: false,
            border: false,
            shadow: false,
            padding:0,
            defaults: {
                margin: 2
            },
            items: [{
                text: '<div style="font-size: 11px;">' + esapp.Utils.getTranslation('PRODUCTS').toUpperCase() + '</div>',   // 'Products',
                reference: 'changeSelectedProductsAndTimeframe_'+me.id.replace(/-/g,'_'),
                tooltip: esapp.Utils.getTranslation('change_selected_products'), //  'Change Selected products',
                iconCls: 'fa fa-calendar fa-2x',
                style: {color: '#748FFC'},
                scale: 'medium',
                disabled: (me.graphtype == 'scatter'),
                // hidden:  ((esapp.getUser() == 'undefined' || esapp.getUser() == null) || !me.isTemplate ? true : false),
                handler: 'changeSelectedProductsAndTimeFrame'
            // }, {
            //     xtype: 'button',
            //     tooltip: esapp.Utils.getTranslation('change_timeframe'),   //  'Change Time frame',
            //     iconCls: 'fa fa-calendar fa-2x',
            //     style: {color: '#748FFC'},
            //     enableToggle: false,
            //     scale: 'medium',
            //     hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
            //     handler: 'changeSelectedProductsAndTimeFrame'
            },{
                // text: esapp.Utils.getTranslation('properties'),    // 'Graph properties',
                tooltip: esapp.Utils.getTranslation('graph_edit_properties'), //  'Edit graph properties',
                iconCls: 'chart-curve_edit',
                scale: 'medium',
                disabled: (me.graphtype == 'scatter'),
                handler: 'openChartProperties'
            }, {
                xtype: 'tbseparator'
            }, ' ', {
                // text: esapp.Utils.getTranslation('values'),    // downloadtimeseries = 'Download timeseries',
                tooltip: esapp.Utils.getTranslation('graph_download_values'),   //  'Download time series values',
                iconCls: 'download-values_excel',   // 'fa fa-file-excel-o fa-2x',    // 'fa fa-download fa-2x',
                style: { color: 'green' },
                scale: 'medium'
                ,handler: 'tsDownload'
            },{
                // text: esapp.Utils.getTranslation('savechart'),    // 'Save graph',
                tooltip: esapp.Utils.getTranslation('graph_download_png'),   //  'Download graph as PNG',
                iconCls: 'download_png',    // 'fa fa-floppy-o fa-2x',
                scale: 'medium'
                ,handler: 'saveChartAsPNG'
            },{
                xtype: 'splitbutton',
                reference: 'saveGraphTemplate_'+me.id.replace(/-/g,'_'),
                tooltip: esapp.Utils.getTranslation('graph_save_graph_tpl'),   //  'Save graph as template',
                iconCls: 'fa fa-save fa-2x',
                style: {color: 'lightblue'},
                cls: 'nopadding-splitbtn',
                scale: 'medium',
                hidden:  (esapp.getUser() == 'undefined' || esapp.getUser() == null ? true : false),
                arrowVisible: (!me.isNewTemplate ? true : false),
                handler: 'setGraphTemplateName',
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target button's ID
                            title: '',
                            text: esapp.Utils.getTranslation('save_graph_template')
                        });
                    }
                },
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
                        tooltip: esapp.Utils.getTranslation('graph_tpl_save_as'),   //  'Save graph as template',
                        glyph: 'xf0c7@FontAwesome',
                        cls:'lightblue',
                        // iconCls: 'fa fa-save fa-lg lightblue',
                        style: { color: 'lightblue' },
                        //cls: 'x-menu-no-icon button-gray',
                        width: 165,
                        handler: function(){
                            me.isNewTemplate = true;
                            me.getController().setGraphTemplateName();
                        }
                    }]
                }

            },
            '->',
            {
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
                xtype: 'button',
                tooltip: esapp.Utils.getTranslation('change_selected_region'),   //  'Change selected region',
                iconCls: 'change-region-unlink',
                // style: {color: '#748FFC'},
                enableToggle: true,
                pressed: false,
                margin: 0,
                scale: 'medium',
                handler: 'toggleRegionLink'
            },
            ' ',
            {
                xtype: 'button',
                tooltip: esapp.Utils.getTranslation('graph_refresh'),   //  'Refresh graph',
                iconCls: 'fa fa-refresh fa-2x',
                hidden: false,
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'refreshChart'
            }]
        });


        me.name ='tsgraphwindow_' + me.id;

        me.items = [{
            xtype: 'container',
            layout:'fit',
            reference:'tsgraph_'+me.id,
            id: 'tsgraph_' + me.id
        }, {
            xtype: 'mapdisclaimerobject',
            id: 'disclaimer_obj_' + me.id,
            reference: 'disclaimer_obj_' + me.id,
            alwaysOnTop: false
        }, {
            xtype: 'maplogoobject',
            id: 'logo_obj_' + me.id,
            reference: 'logo_obj_' + me.id,
            alwaysOnTop: false
        }];

        me.callParent();
    }
});
