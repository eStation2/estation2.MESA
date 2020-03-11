Ext.define('esapp.view.analysis.timeseriesChartViewController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-timeserieschartview',

    getGraphSettings: function(){
        var me = this.getView(),
            graphObjectToggleBtn = me.lookupReference('objectsbtn_'+ me.id.replace(/-/g,'_')),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logoObj = me.lookupReference('logo_obj_' + me.id),
            graphviewSize = me.getSize().width.toString() + "," + me.getSize().height.toString();

        var selectedYears = me.yearsToCompare;
        if (me.yearsToCompare != '')
            selectedYears = Ext.util.JSON.encode(me.yearsToCompare);

        var graphproperties = {
            "graph_type": me.graphtype,
            "graph_width": me.getSize().width.toString(),
            "graph_height": me.getSize().height.toString(),
            "graph_title": me.graphProperties.title,
            "graph_title_font_size": me.graphProperties.graph_title_font_size,
            "graph_title_font_color": me.graphProperties.graph_title_font_color,
            "graph_subtitle": me.graphProperties.subtitle,
            "graph_subtitle_font_size": me.graphProperties.graph_subtitle_font_size,
            "graph_subtitle_font_color": me.graphProperties.graph_subtitle_font_color,
            "legend_position": 'bottom',
            "legend_font_size": me.graphProperties.legend_title_font_size,
            "legend_font_color": me.graphProperties.legend_title_font_color,
            "xaxe_font_size": me.graphProperties.xaxe_font_size,
            "xaxe_font_color": me.graphProperties.xaxe_font_color
        }
        // delete graphproperties.localRefresh;
        // graphproperties.splice('localRefresh', 1);

        var selectedProductsAndTimeFramePanel = Ext.getCmp(me.getId()+'-select_products_timeframe');
        var tsdrawprops = selectedProductsAndTimeFramePanel.down('timeseriesproductselection').getController().getSelectedTSDrawProperties();

        var graphSettings = {
            newtemplate: me.isNewTemplate,
            userid: esapp.getUser().userid,
            graph_tpl_id: me.graph_tpl_id,
            parent_tpl_id: me.parent_tpl_id,
            graph_tpl_name: me.graph_tpl_name,
            istemplate: me.isTemplate,
            graphviewposition: me.getPosition(true).toString(),
            graphviewsize: graphviewSize,
            graphproperties: Ext.util.JSON.encode(graphproperties),
            yAxes: Ext.util.JSON.encode(me.timeseriesGraph.yaxes),

            graph_type: me.graphtype,
            selectedtimeseries: me.selectedTimeseries,
            tsdrawprops: tsdrawprops,
            yearts: me.yearTS,
            tsfromperiod: me.tsFromPeriod,
            tstoperiod: me.tsToPeriod,
            yearstocompare: selectedYears,
            tsfromseason: me.tsFromSeason,
            tstoseason: me.tsToSeason,
            wkt_geom: me.wkt_geom,
            selectedregionname: me.selectedregionname,

            disclaimerobjposition: (esapp.Utils.objectExists(disclaimerObj) && disclaimerObj.rendered) ? disclaimerObj.getPosition(true).toString() : disclaimerObj.disclaimerPosition.toString(),
            disclaimerobjcontent: disclaimerObj.getContent(),
            logosobjposition: (esapp.Utils.objectExists(logoObj) && logoObj.rendered) ? logoObj.getPosition(true).toString() : logoObj.logoPosition.toString(),
            logosobjcontent: Ext.encode(logoObj.getLogoData()),
            showobjects: graphObjectToggleBtn.pressed,
            showtoolbar: !me.getDockedItems('toolbar[dock="top"]')[0].hidden
        }

        return graphSettings;
    },

    toggleObjects: function(btn, event) {
        var graphviewwin = btn.up().up(),
            // titleObj = graphviewwin.lookupReference('title_obj_' + graphviewwin.id),
            disclaimerObj = graphviewwin.lookupReference('disclaimer_obj_' + graphviewwin.id),
            logoObj = graphviewwin.lookupReference('logo_obj_' + graphviewwin.id);

        if (btn.pressed) {
            graphviewwin.showObjects = true;
            // titleObj.show();
            disclaimerObj.show();
            logoObj.show();
            btn.setStyle({ color: 'green' });
            if (graphviewwin.graphtype == 'matrix'){
                graphviewwin.tsgraph.options.chart.spacingBottom = 75;
            }
            else {
                graphviewwin.tsgraph.options.chart.spacingBottom = 65;
            }
            // graphviewwin.tsgraph.options.chart.marginBottom = 60+graphviewwin.tsgraph.options.chart.spacingBottom;
            // graphviewwin.tsgraph.options.chart.spacingTop = 60;
        }
        else {
            graphviewwin.showObjects = false;
            // titleObj.hide();
            // titleObj.titlePosition = titleObj.getPosition(true);
            disclaimerObj.disclaimerPosition = disclaimerObj.getPosition(true);
            disclaimerObj.hide();
            logoObj.logoPosition = logoObj.getPosition(true);
            logoObj.hide();
            btn.setStyle({ color: 'black' });
            graphviewwin.tsgraph.options.chart.spacingBottom = 10;
            // graphviewwin.tsgraph.options.chart.spacingTop = 10;
        }
        graphviewwin.fireEvent('move');
        // graphviewwin.tsgraph.isDirtyBox = true;  // Not working, does not refresh legend and title!
        // graphviewwin.tsgraph.isDirtyLegend = true;
        // graphviewwin.tsgraph.redraw();
        // console.info(graphviewwin.tsgraph);
    },

    toggleRegionLink: function(btn, event) {
        var me = this.getView();
        var tschartviewwin = btn.up().up();

        if (btn.pressed) {
            var regionselected = this.changeSelectedRegion();
            if (regionselected){
                btn.setIconCls('change-region-link');
                me.link_region_change = true;
            }
        }
        else {
            btn.setIconCls('change-region-unlink');
            me.link_region_change = false;
        }
    },

    createSelectedProductsAndTimeFramePanel: function(){
        var me = this.getView();

        return Ext.create('Ext.panel.Panel', {
            title: esapp.Utils.getTranslation('graphtemplate_products_timeframe_selections'),     // 'Graph template product and time frame selections',
            id: me.getId()+'-select_products_timeframe',
            reference: me.getId()+'-select_products_timeframe',
            width: 765, // document.getElementById(me.id + "-body").offsetWidth-3,
            minHeight: 430, // document.getElementById(me.id + "-body").offsetHeight-3,
            // autoWidth: true,
            // autoHeight: true,
            margin: '2 2 2 5',
            maximizable: false,
            collapsible: true,
            resizable: false,
            // layout: 'fit',
            // forceFit: true,
            hidden: true,
            floating: true,
            defaultAlign: 'tl-tl',
            closable: true,
            closeAction: 'hide',
            draggable: true,
            // constrain: true,
            constrainHeader: true,
            alwaysOnTop: true,
            autoShow: false,
            frame: false,
            frameHeader : false,
            border: false,
            shadow: false,
            componentCls: 'rounded-box',
            header: {
                cls: 'rounded-box-header',
                style: {
                    'background-color': '#A9DEEC !important;',
                    'font-weight':'bold',
                    'color':'#000',
                    'font-size': '13px;'
                }
            },
            dockedItems:  [{
                dock: 'bottom',
                xtype: 'toolbar',
                items : ['->',{
                    text: esapp.Utils.getTranslation('update_graph'), // 'Update graph',
                    // scope:me,
                    iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                    style: { color: 'lightblue' },
                    scale: 'medium',
                    disabled: false,
                    handler: function(){
                        // console.info(me.lookupReference('timeseriesproductselection_'+me.id));
                        var idpostfix = me.isTemplate ? me.id : me.graphtype;
                        var timeseriesselections = me.lookupReference('timeseriesproductselection_'+idpostfix).getController().getSelections();
                        // console.info(timeseriesselections);
                        if (timeseriesselections != null ){
                            me.selectedTimeseries = timeseriesselections.selectedTimeseries;
                            me.tsdrawprops = timeseriesselections.tsdrawprops;
                            me.yearTS = timeseriesselections.yearTS;
                            me.tsFromSeason =  timeseriesselections.tsFromSeason instanceof Date ? Ext.Date.format(timeseriesselections.tsFromSeason, 'm-d') : timeseriesselections.tsFromSeason;
                            me.tsToSeason = timeseriesselections.tsToSeason instanceof Date ? Ext.Date.format(timeseriesselections.tsToSeason, 'm-d') : timeseriesselections.tsToSeason;
                            me.tsFromPeriod = timeseriesselections.tsFromPeriod instanceof Date ? Ext.Date.format(timeseriesselections.tsFromPeriod, 'Y-m-d') : timeseriesselections.tsFromPeriod;
                            me.tsToPeriod = timeseriesselections.tsToPeriod instanceof Date ? Ext.Date.format(timeseriesselections.tsToPeriod, 'Y-m-d') : timeseriesselections.tsToPeriod;
                            me.yearsToCompare = timeseriesselections.yearsToCompare;
                            me.timeseriesGraph.yaxes = null;    // No yaxes passed to getTimeseries forces to refresh the yaxes info on server
                            me.getController().refreshChart();
                            this.up().up().close();     // this=save button up1=toolbar up2=panel
                        }
                    }
                }]
            }],
            listeners: {
                close : function (){
                    me.lookupReference('tbar_'+me.id).enable();
                }
                // focusleave: function(){
                //     this.close();
                // }
            },

            items: [{
                xtype: 'timeseriesproductselection',
                id: me.getId()+'-timeseriesproductselection',
                isTemplate: me.isTemplate,
                tplChartView: me,
                graphtype: me.graphtype,
                cumulative: me.graphtype == 'cumulative' ? true : false,
                ranking: me.graphtype == 'ranking' ? true : false,
                matrix: me.graphtype == 'matrix' ? true : false,
                multiplevariables: (me.graphtype == 'xy' || me.graphtype == 'cumulative') ? true : false,
                fromto: (me.graphtype == 'xy' || me.graphtype == 'cumulative') ? true : false,
                year: me.graphtype == 'cumulative' ? true : false,
                multipleyears: me.graphtype != 'cumulative' ? true : false
            }]
        });
    },

    changeSelectedProductsAndTimeFrame: function(btn){
        var me = this.getView();
        var selectedProductsAndTimeFramePanel = Ext.getCmp(me.getId()+'-select_products_timeframe');
        me.lookupReference('tbar_'+me.id).disable();

        //if (Ext.isObject(selectedProductsAndTimeFramePanel)) {}
        if (!selectedProductsAndTimeFramePanel){
            selectedProductsAndTimeFramePanel = this.createSelectedProductsAndTimeFramePanel();

            me.add(selectedProductsAndTimeFramePanel);
            selectedProductsAndTimeFramePanel.show();
            // selectedProductsAndTimeFramePanel.doConstrain();
        }
        else {
            selectedProductsAndTimeFramePanel.show();
            // selectedProductsAndTimeFramePanel.doConstrain();
        }
    },

    changeSelectedRegion: function(){
        var me = this.getView();
        // var new_wkt_polygon = Ext.getCmp('timeserieschartselection').lookupReference('wkt_polygon').getValue();
        // var new_selectedregionname = Ext.getCmp('timeserieschartselection').lookupReference('selectedregionname').getValue();
        // console.info(me.workspace);
        var new_selectedregionname = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('selectedregionname').getValue();
        var new_wkt_polygon = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('wkt_polygon').getValue();
        var graphpropertiesRecord = this.getStore('graphproperties').getData().items[0].data;
        var response = false;

        if (new_wkt_polygon.trim() == '') {
            Ext.Msg.show({
               title: esapp.Utils.getTranslation('selectapolygon'),    // 'Select a polygon!',
               msg: esapp.Utils.getTranslation('pleaseselectapolygon'),    // 'Please select or draw a polygon in a MapView!',
               width: 300,
               buttons: Ext.Msg.OK,
               animEl: '',
               icon: Ext.Msg.WARNING
            });
        }
        else {
            if (new_wkt_polygon.trim() != me.wkt_geom.trim()){
                me.wkt_geom = new_wkt_polygon;
                me.selectedregionname = new_selectedregionname;
                graphpropertiesRecord.graph_title = new_selectedregionname;
                this.refreshChart();
            }
            response = true;
        }
        return response;
    },

    setGraphTemplateName: function(){
        var me = this;
        var newGraphTemplateName = '';

        if (me.getView().isNewTemplate){
            // open dialog asking to give a unique template name
            // If Save as... then the graphView has a templatename which will be proposed
            // Ext.MessageBox.prompt( title , message , [fn] , [scope] , [multiline] , [value] )
            if (esapp.Utils.objectExists(me.getView().graph_tpl_name) && me.getView().graph_tpl_name != ''){
                newGraphTemplateName = me.getView().graph_tpl_name + ' - copy';
            }
            else {
                // if (esapp.Utils.objectExists(me.getView().selectedregionname) && me.getView().selectedregionname != ''){
                //     newGraphTemplateName = newGraphTemplateName + me.getView().selectedregionname;
                //     if (esapp.Utils.objectExists(me.getView().productversion) && me.getView().productversion != ''){
                //         newGraphTemplateName = newGraphTemplateName + ' - ' + me.getView().productversion;
                //     }
                // }
                if (me.getView().graphtype == 'cumulative'){
                    newGraphTemplateName = esapp.Utils.getTranslation('CUMULATIVE') + ' - ';
                }
                else if (me.getView().graphtype == 'ranking'){
                    newGraphTemplateName = esapp.Utils.getTranslation('RANKING_ZSCORE') + ' - ';
                }
                else if (me.getView().graphtype == 'matrix'){
                    newGraphTemplateName = esapp.Utils.getTranslation('MATRIX') + ' - ';
                }
                else {
                    newGraphTemplateName = esapp.Utils.getTranslation('PROFILE') + ' - ';
                }

            }

            Ext.MessageBox.prompt(esapp.Utils.getTranslation('graph_tpl_name'), esapp.Utils.getTranslation('graph_tpl_save_message') + ':', function(btn, text){   // 'Graph Template Name'   'Please give a unique name for the new graph template'
                if (btn == 'ok'){
                    // process text value and close...
                    me.getView().graph_tpl_name = text;
                    me.saveGraphTemplate();
                }
            }, this, false, newGraphTemplateName);
        }
        else {
            me.saveGraphTemplate();
        }
    },

    saveGraphTemplate: function(){
        var me = this.getView(),
            graphObjectToggleBtn = me.lookupReference('objectsbtn_'+ me.id.replace(/-/g,'_')),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logoObj = me.lookupReference('logo_obj_' + me.id),
            graphviewSize = me.getSize().width.toString() + "," + me.getSize().height.toString();

        var selectedYears = me.yearsToCompare;
        if (me.yearsToCompare != '')
            selectedYears = Ext.util.JSON.encode(me.yearsToCompare);

        me.isTemplate = true;
        var graphTemplate = this.getGraphSettings();

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/savegraphtemplate',
            params: graphTemplate,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);

                if (responseJSON.success){
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('save_graph_tpl'), width: 300, align: 't'});     // "Save Graph template"

                    if (me.getTitle() != null && me.getTitle() != ''){
                        Ext.fly('graphview_title_templatename_' + me.id).dom.innerHTML = me.graph_tpl_name;
                        //me.getView().setTitle('<div class="map-templatename">' + text + '</div>' + me.getView().getTitle());
                    }
                    me.isTemplate = true;
                    if (me.isNewTemplate) {  // Created new template, else existing template is updated so do not set id's
                        me.isNewTemplate = false;
                        me.graph_tpl_id = responseJSON.graph_tpl_id;
                        me.parent_tpl_id = responseJSON.graph_tpl_id;
                        me.lookupReference('saveGraphTemplate_'+me.id.replace(/-/g,'_')).setArrowVisible(true);
                        me.lookupReference('saveGraphTemplate_'+me.id.replace(/-/g,'_')).up().up().updateLayout();
                    }
                    me.workspace.lookupReference('graphtemplateadminbtn_'+me.workspace.id.replace(/-/g,'_')).graphTemplateAdminPanel.setDirtyStore(true);
                    // Ext.getCmp('userGraphTemplates').setDirtyStore(true);
                    me.lookupReference('changeSelectedProductsAndTimeframe_'+me.id.replace(/-/g,'_')).show();
                }
                else {
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_graph_tpl'), width: 300, align: 't'});     // "ERROR saving the Graph template"
                    me.graph_tpl_name = '';
                }

            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_graph_tpl'), width: 300, align: 't'});     // "ERROR saving the Graph template"
                me.graph_tpl_name = '';
            }
        });
    },

    __saveGraphTemplate: function(){
        var me = this.getView(),
            graphObjectToggleBtn = me.lookupReference('objectsbtn_'+ me.id.replace(/-/g,'_')),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logoObj = me.lookupReference('logo_obj_' + me.id),
            graphviewSize = me.getSize().width.toString() + "," + me.getSize().height.toString();

        var selectedYears = me.yearsToCompare;
        if (me.yearsToCompare != '')
            selectedYears = Ext.util.JSON.encode(me.yearsToCompare);

        var graphTemplate = {
            newtemplate: me.isNewTemplate,
            userid: esapp.getUser().userid,
            graph_tpl_name: me.graph_tpl_name,
            graphviewposition: me.getPosition(true).toString(),
            graphviewsize: graphviewSize,
            graphsroperties: Ext.util.JSON.encode(me.graphProperties),

            graph_type: me.graphtype,
            selectedtimeseries: me.selectedTimeseries,
            yearts: me.yearTS,
            tsfromperiod: me.tsFromPeriod,
            tstoperiod: me.tsToPeriod,
            yearstocompare: selectedYears,
            tsfromseason: me.tsFromSeason,
            tstoseason: me.tsToSeason,
            wkt_geom: me.wkt_geom,
            selectedregionname: me.selectedregionname,

            disclaimerObjPosition: disclaimerObj.rendered ? disclaimerObj.getPosition(true).toString() : disclaimerObj.disclaimerPosition.toString(),
            disclaimerObjContent: disclaimerObj.getContent(),
            logosObjPosition: logoObj.rendered ? logoObj.getPosition(true).toString() : logoObj.logoPosition.toString(),
            logosObjContent: Ext.encode(logoObj.getLogoData()),
            showObjects: graphObjectToggleBtn.pressed
        }
        //console.info(graphTemplate);

        Ext.Ajax.request({
            method: 'POST',
            url: 'analysis/savegraphtemplate',
            params: graphTemplate,
            scope: me,
            success: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);

                if (responseJSON.success){
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('save_graph_tpl'), width: 300, align: 't'});     // "Save Graph template"

                    if (me.getTitle() != null && me.getTitle() != ''){
                        Ext.fly('graphview_title_templatename_' + me.id).dom.innerHTML = me.graph_tpl_name;
                        //me.getView().setTitle('<div class="map-templatename">' + text + '</div>' + me.getView().getTitle());
                    }
                    me.isTemplate = true;
                    me.isNewTemplate = false;
                    me.workspace.lookupReference('graphtemplateadminbtn_'+me.workspace.id.replace(/-/g,'_')).graphTemplateAdminPanel.setDirtyStore(true);
                    // Ext.getCmp('userGraphTemplates').setDirtyStore(true);
                    me.lookupReference('changeSelectedProductsAndTimeframe_'+me.id.replace(/-/g,'_')).show();
                }
                else {
                    Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_graph_tpl'), width: 300, align: 't'});     // "ERROR saving the Graph template"
                    me.graph_tpl_name = '';
                }

            },
            //callback: function ( callinfo,responseOK,response ) {},
            failure: function (response, request) {
                var responseJSON = Ext.util.JSON.decode(response.responseText);
                Ext.toast({hideDuration: 2000, html: responseJSON.message, title: esapp.Utils.getTranslation('error_save_graph_tpl'), width: 300, align: 't'});     // "ERROR saving the Graph template"
                me.graph_tpl_name = '';
            }
        });
    },

    getTimeseries: function(callback){
        var me = this.getView();
        var params = {};
        var user = esapp.getUser();
        //var chartpropertiesStore = this.getStore('chartproperties');

        var myLoadMask = new Ext.LoadMask({
            msg    : esapp.Utils.getTranslation('generatingtimeseries'), // 'Generating requested time series...',
            target : Ext.getCmp('tsgraph_'+me.id)
            ,toFrontOnShow: true
            ,useTargetEl:true
        });
        myLoadMask.show();

        var selectedYears = me.yearsToCompare;
        if (me.yearsToCompare != '')
            selectedYears = Ext.util.JSON.encode(me.yearsToCompare);


        params = {
            userid : (user != 'undefined' && user != null) ? user.userid : '',
            istemplate : me.isTemplate,
            graph_tpl_id : esapp.Utils.objectExists(me.graph_tpl_id) ? me.graph_tpl_id : -1,
            graph_tpl_name : me.isTemplate ? me.graph_tpl_name : 'default',
            graphtype: me.graphtype,
            selectedTimeseries: me.selectedTimeseries,
            tsdrawprops: me.tsdrawprops,
            yAxes: Ext.util.JSON.encode(me.timeseriesGraph.yaxes),
            yearTS: me.yearTS,
            tsFromPeriod: me.tsFromPeriod,
            tsToPeriod: me.tsToPeriod,
            yearsToCompare: selectedYears,
            tsFromSeason: me.tsFromSeason,
            tsToSeason:me.tsToSeason,
            WKT:me.wkt_geom
        }

        var requestId = Ext.Ajax.request({
            url:"analysis/gettimeseries",
            timeout : 120000,
            // autoAbort: true,
            scope: me,
            params: params,
            method: 'POST',
            success: function ( result, request ) {
                myLoadMask.hide();
                if (esapp.Utils.objectExists(me)){
                    me.timeseriesGraph = Ext.util.JSON.decode(result.responseText);
                    if (esapp.Utils.objectExists(me.lookupReference('tbar_' + me.id))){
                         me.lookupReference('tbar_' + me.id).enable();

                        // GENERATE REQUESTED GRAPH IN HIGHCHARTS
                        callback(me);
                    }
                }
            },
            failure: function ( result, request) {
                myLoadMask.hide();
                if (esapp.Utils.objectExists(me.lookupReference('tbar_' + me.id))) {
                    me.lookupReference('tbar_' + me.id).enable();
                }
            }
        });
        // Ext.Ajax.abort(requestId);

    },

    setGraphProperties: function() {
        var me = this.getView();
        // var user = esapp.getUser();
        var graphpropertiesStore = this.getStore('graphproperties');
        var graphpropertiesRecord = graphpropertiesStore.getData().items[0].data;

        me.graphProperties = {};
        // me.graphProperties.localRefresh = false;
        // me.selectedregionname = me.isTemplate ? me.selectedregionname : me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('selectedregionname').getValue();

        me.graphProperties.title = esapp.Utils.objectExists(graphpropertiesRecord.graph_title) && graphpropertiesRecord.graph_title != '' ? graphpropertiesRecord.graph_title : me.selectedregionname;
        me.graphProperties.subtitle = '';

        // if (me.graphtype == 'matrix'){
        //     var selectedProductsAndTimeFramePanel = Ext.getCmp(me.getId()+'-select_products_timeframe');
        //     var tsdrawprops = selectedProductsAndTimeFramePanel.down('timeseriesproductselection').getController().getSelectedTSDrawProperties();
        //     me.graphProperties.subtitle = tsdrawprops[0]['tsname_in_legend'];
        // }

        //if (Ext.isObject(Ext.getCmp('radio-year')) &&  Ext.getCmp('radio-year').getValue() && me.yearTS != '') {
        if (me.yearTS != '') {
            me.graphProperties.subtitle = me.yearTS;
            if ( (me.tsFromSeason != null && me.tsFromSeason != "") && (me.tsToSeason != null && me.tsToSeason != "")){
                if (parseInt(me.tsFromSeason.substring(0, 2)) > parseInt(me.tsToSeason.substring(0, 2))) {
                    me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.graphProperties.subtitle + '/' + me.tsFromSeason + '  ' + esapp.Utils.getTranslation('to') + ' ' + (parseInt(me.graphProperties.subtitle)+1) + '/' + me.tsToSeason;
                }
                else {
                    // me.graphProperties.subtitle = esapp.Utils.getTranslation('season') + ' ' +  Ext.Date.format(me.tsFromSeason, 'm/d') + ' - ' + Ext.Date.format(me.tsToSeason, 'm/d') + ' ' + esapp.Utils.getTranslation('of') + ' ' + me.graphProperties.subtitle;
                    me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.graphProperties.subtitle + '/' +me.tsFromSeason + '  ' + esapp.Utils.getTranslation('to') + ' ' + me.graphProperties.subtitle + '/' + me.tsToSeason;
                }
            }
        }
        //else if (Ext.getCmp('radio-compareyears').getValue() && me.yearsToCompare != '') {
        else if (me.yearsToCompare != '') {
            //me.yearsToCompare = Ext.util.JSON.decode(me.yearsToCompare);
            if (me.yearsToCompare.length == 1){
                me.yearsToCompare.forEach(function(year){
                    me.graphProperties.subtitle = year;
                })
                if ( (me.tsFromSeason != null && me.tsFromSeason != "") && (me.tsToSeason != null && me.tsToSeason != "")){
                    if (parseInt(me.tsFromSeason.substring(0, 2)) > parseInt(me.tsToSeason.substring(0, 2))) {      // Ext.Date.format(me.tsFromSeason, 'm')
                        me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.graphProperties.subtitle + '/' + me.tsFromSeason + '  ' + esapp.Utils.getTranslation('to') + ' ' + (parseInt(me.graphProperties.subtitle)+1) + '/' + me.tsToSeason;
                    }
                    else {
                        // me.graphProperties.subtitle = esapp.Utils.getTranslation('season') + ' ' +  Ext.Date.format(me.tsFromSeason, 'm/d') + ' - ' + Ext.Date.format(me.tsToSeason, 'm/d') + ' ' + esapp.Utils.getTranslation('of') + ' ' + me.graphProperties.subtitle;
                        me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.graphProperties.subtitle + '/' + me.tsFromSeason + '  ' + esapp.Utils.getTranslation('to') + ' ' + me.graphProperties.subtitle + '/' + me.tsToSeason;
                    }
                }
            }
            else {
                if ( (me.tsFromSeason != null && me.tsFromSeason != "") && (me.tsToSeason != null && me.tsToSeason != "")){
                    me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.tsFromSeason + '  ' + esapp.Utils.getTranslation('to') + ' ' +  me.tsToSeason;
                }
            }
        }
        //else if ( Ext.getCmp('radio-fromto').getValue() ){
        else if ( me.tsFromPeriod != '' && me.tsToPeriod != ''){
            me.graphProperties.subtitle = esapp.Utils.getTranslation('from') + ' ' + me.tsFromPeriod + '  ' + esapp.Utils.getTranslation('to') + ' ' + me.tsToPeriod;
        }

        // me.graphProperties.filename = me.graphProperties.title + '_' + me.graphProperties.subtitle.toString().replace(' ', '_');

        graphpropertiesStore.each(function(graphproperties) {   // Should always be 1 record!!
            me.graphProperties.graph_title_font_size = graphproperties.get('graph_title_font_size');
            me.graphProperties.graph_title_font_color = esapp.Utils.convertRGBtoHex(graphproperties.get('graph_title_font_color'));

            me.graphProperties.graph_subtitle_font_size = graphproperties.get('graph_subtitle_font_size');
            me.graphProperties.graph_subtitle_font_color = esapp.Utils.convertRGBtoHex(graphproperties.get('graph_subtitle_font_color'));

            me.graphProperties.xaxe_font_size = graphproperties.get('xaxe_font_size');
            me.graphProperties.xaxe_font_color = esapp.Utils.convertRGBtoHex(graphproperties.get('xaxe_font_color'));

            me.graphProperties.legend_title_font_size = graphproperties.get('legend_font_size');
            me.graphProperties.legend_title_font_color = esapp.Utils.convertRGBtoHex(graphproperties.get('legend_font_color'));

            me.graphProperties.width = graphproperties.get('graph_width');
            me.graphProperties.height = graphproperties.get('graph_height');
        });
    },

    createDefaultChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }

        var xAxisLabels = {};
        if (me.timeseriesGraph.showYearInTicks) {
            xAxisLabels = {
                enabled: 1,
                autoRotationLimit: -40,
                y: 25,
                padding: 10,
                //step: 2,
                //autoRotation: [0,-90],
                //useHTML: false,
                //reserveSpace: false,
                style: {
                    color: me.graphProperties.xaxe_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    //fontSize: me.graphProperties.xaxe_font_size-6,
                    "fontSize": me.graphProperties.xaxe_font_size + 'px'
                    ,margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value) + '<br/>' + Highcharts.dateFormat('\'%y', this.value);
                }
            };
        }
        else if (me.timeseriesGraph.moreThenTwoYears){
            xAxisLabels = {
                enabled: 1,
                y: 25,
                style: {
                    color: me.graphProperties.xaxe_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.xaxe_font_size + 'px',
                    margin: '0 0 0 0'
                }
            }
        }
        else {
            xAxisLabels = {
                enabled: 1,
                y: 25,
                style: {
                    color: me.graphProperties.xaxe_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.xaxe_font_size + 'px',
                    margin: '0 0 0 0'
                },
                formatter: function () {
                    return Highcharts.dateFormat('%b', this.value);
                }
            };
        }

        var xAxis = [];
        if (me.yearsToCompare != '' && me.yearsToCompare.length > 1) {
            var xAxe = {};
            var xaxeVisible = true;
            var minPeriod =  '/01/01';    //      Ext.Date.format(me.tsFromSeason, 'm-d');
            var maxPeriod = '/12/31';     //      Ext.Date.format(me.tsToSeason, 'm-d');

            me.yearsToCompare.forEach(function(year){
                if (me.tsFromSeason != null && me.tsFromSeason != '' && me.tsToSeason != null && me.tsToSeason != ''){
                    minPeriod = new Date(year + '/' + me.tsFromSeason.replace('-', '/')).getTime();
                    maxPeriod = new Date(year + '/' + me.tsToSeason.replace('-', '/')).getTime();
                    if (me.tsToSeason.substring(0,2) < me.tsFromSeason.substring(0,2)){
                        maxPeriod = new Date(year+1 + '/' + me.tsToSeason.replace('-', '/')).getTime();
                    }
                }
                else {
                    minPeriod = new Date(year + '/01/01').getTime();
                    maxPeriod = new Date(year + '/12/31').getTime();
                }

                xAxe = {
                    id: year.toString(),
                    visible: xaxeVisible,
                    type: 'datetime',
                    startOnTick: false,
                    endOnTick: true,
                    //offset: 25,
                    lineWidth: 2,
                    labels: xAxisLabels,
                    tickInterval: 30 * 24 * 3600 * 1000,
                    min: minPeriod,
                    max: maxPeriod
                };
                xaxeVisible = false;
                xAxis.push(xAxe);
            })
        }
        else {
            xAxis = [{
                type: 'datetime',
                //tickmarkPlacement: 'on',      // on between  - For categorized axes only!
                startOnTick: false,
                lineWidth: 2,
                labels: xAxisLabels,
                tickInterval: 30 * 24 * 3600 * 1000
            }]
        }

        if (me.graphtype == 'cumulative' && !me.graphProperties.localRefresh) {
            var TimeseriesCumulatedAverages = null;
            var TimeseriesCumulatedData = null;
            var aboveAvgColor = '#009E00';
            var diffProdName = '';
            var refProdName = '';

            var lastItemsToRemove = 0;
            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                if (timeserie.reference == true){
                    for (var i = timeserie.data.length - 1; i >= 0; --i) {
                        if (timeserie.data[i][1] == null) {
                            timeserie.data.splice(i, 1);
                            lastItemsToRemove += 1;
                        }
                        else {
                            break;
                        }
                    }
                }
            });

            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                if (timeserie.reference != true){
                    for (var i = lastItemsToRemove; i >= 1; --i) {
                        timeserie.data.pop();
                    }
                }
            });

            // var nullValueArrayIndexes = [];
            var refNullValuesChangedToDiffValue = false;
            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                if (timeserie.reference == true){
                    timeserie.data.forEach(function (datarecord, idx) {
                        if (datarecord[1] == null) {
                            // nullValueArrayIndexes.push(idx);
                            refNullValuesChangedToDiffValue = true;
                            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                                if (timeserie.difference == true){
                                    datarecord[1]  = timeserie.data[idx][1];
                                }
                            });
                        }
                    });
                }
            });

            me.timeseriesGraph.timeseries.forEach(function (timeserie) {
                //if (timeserie.cumulative) {
                    //me.timeseriesGraph.cumulative = true;
                    timeserie.type = 'line';
                    timeserie.dashStyle = 'Solid';
                    timeserie.lineWidth = 2;

                    var cumulated = 0;
                    timeserie.data.forEach(function (datarecord) {
                        datarecord[1] += cumulated;
                        cumulated = datarecord[1];
                    })

                    if (timeserie.difference == true) {
                        diffProdName = timeserie.name;
                        timeserie.name = timeserie.name + ' ('+esapp.Utils.getTranslation('curr')+')';
                        TimeseriesCumulatedAverages = Ext.clone(timeserie.data);
                    }
                    else if (timeserie.reference == true){
                        refProdName = timeserie.name;
                        timeserie.name = timeserie.name + ' ('+esapp.Utils.getTranslation('ref')+')';
                        TimeseriesCumulatedData = Ext.clone(timeserie.data);
                        // aboveAvgColor = timeserie.color;
                    }
                //}
            });


            if (TimeseriesCumulatedData != null && TimeseriesCumulatedAverages != null) {
                var i = 0, cumulatedPositive = [], cumulatedNegative = [], cumulatedMinValue = [], newDataValue = [];

                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedData[i]);
                    newDataValue[1] = TimeseriesCumulatedAverages[i][1] - TimeseriesCumulatedData[i][1];
                    if (newDataValue[1] > 0) newDataValue[1] = 0;
                    else newDataValue[1] = newDataValue[1] * -1;
                    cumulatedPositive.push(newDataValue);
                }

                aboveAvgColor = esapp.Utils.convertRGBtoHex(aboveAvgColor);
                var aboveAvg = {
                    data: cumulatedPositive,
                    fillColor: "#ff0000",
                    color: "#ff0000",
                    id: "Above",
                    // name: esapp.Utils.getTranslation('above') + ' ' + esapp.Utils.getTranslation('diff'),
                    name: esapp.Utils.getTranslation('curr') + ' < ' + esapp.Utils.getTranslation('ref'),
                    type: "area",
                    showInLegend: true,
                    enableMouseTracking: false
                }

                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedData[i]);
                    newDataValue[1] = TimeseriesCumulatedAverages[i][1] - TimeseriesCumulatedData[i][1];
                    if (newDataValue[1] < 0) newDataValue[1] = 0;
                    cumulatedNegative.push(newDataValue);
                }

                var belowAvg = {
                    data: cumulatedNegative,
                    fillColor: aboveAvgColor,
                    color: aboveAvgColor,
                    id: "Below",
                    // name: esapp.Utils.getTranslation('below') + ' ' + esapp.Utils.getTranslation('diff'),
                    name: esapp.Utils.getTranslation('curr') + ' > ' + esapp.Utils.getTranslation('ref'),
                    type: "area",
                    showInLegend: true,
                    enableMouseTracking: false
                }

                for (i = 0; i < TimeseriesCumulatedData.length; i++) {
                    newDataValue = Ext.clone(TimeseriesCumulatedAverages[i]);
                    if (TimeseriesCumulatedData[i][1] < TimeseriesCumulatedAverages[i][1]) {
                        newDataValue = TimeseriesCumulatedData[i];
                    }
                    cumulatedMinValue.push(newDataValue);
                }

                var transparentAvg = {
                    data: cumulatedMinValue,
                    fillColor: "rgba(255,255,255,0)",
                    color: "#ffffff",
                    id: "Cum transparent",
                    name: "Cum transparent",
                    type: "area",
                    showInLegend: false,
                    enableMouseTracking: false
                }

                me.timeseriesGraph.timeseries.push(aboveAvg);
                me.timeseriesGraph.timeseries.push(belowAvg);
                me.timeseriesGraph.timeseries.push(transparentAvg);
            }
        }

        me.timeseriesGraph.timeseries.forEach(function (timeserie) {
            timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        });

        //for (var tscount = 0; tscount < me.timeseriesGraph.timeseries.length; tscount++) {
        //    var tscolor = me.timeseriesGraph.timeseries[tscount].color;
        //    var tstype = me.timeseriesGraph.timeseries[tscount].type;
        //    var tsname = me.timeseriesGraph.timeseries[tscount].name;
        //
        //    if (tsname.indexOf('transparent') == -1) { // Not a transparent timeseries
        //        if (tstype == 'area') {
        //            tscolor = me.timeseriesGraph.timeseries[tscount].fillColor;
        //        }
        //        tscolor = esapp.Utils.convertRGBtoHex(tscolor);
        //
        //        if (tstype == 'area') {
        //            me.timeseriesGraph.timeseries[tscount].fillColor = tscolor;
        //        }
        //        else {
        //            me.timeseriesGraph.timeseries[tscount].color = tscolor;
        //        }
        //
        //        //if (tscolor.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
        //        //    var rgbarr = [];
        //        //    if (esapp.Utils.is_array(tscolor)) {
        //        //        rgbarr = tscolor;
        //        //    }
        //        //    else {
        //        //        rgbarr = tscolor.split(" "); // toString().replace(/,/g,' ');
        //        //    }
        //        //
        //        //    var tsR = rgbarr[0];
        //        //    var tsG = rgbarr[1];
        //        //    var tsB = rgbarr[2];
        //        //    tscolor = esapp.Utils.RGBtoHex(tsR, tsG, tsB);
        //        //
        //        //    if (tstype == 'area') {
        //        //        me.timeseriesGraph.timeseries[tscount].fillColor = tscolor;
        //        //    }
        //        //    else {
        //        //        me.timeseriesGraph.timeseries[tscount].color = tscolor;
        //        //    }
        //        //}
        //    }
        //}

        var Yaxes = [];
        var timeseries_names = '';
        var gridLineWidth = 1;
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
                me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
                opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min != null && min != ''){
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max != null && max != '') {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }
            // if (me.timeseriesGraph.cumulative){
            //    min = null;
            //    max = null;
            // }

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            //if (titlecolor.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
            //    var rgb_arr = [];
            //    if (esapp.Utils.is_array(titlecolor)) {
            //        rgb_arr = titlecolor;
            //    }
            //    else {
            //        rgb_arr = titlecolor.split(" "); // toString().replace(/,/g,' ');
            //    }
            //    var R = rgb_arr[0];
            //    var G = rgb_arr[1];
            //    var B = rgb_arr[2];
            //    titlecolor = esapp.Utils.RGBtoHex(R, G, B);
            //    me.timeseriesGraph.yaxes[yaxescount].title_color = titlecolor;
            //}

            gridLineWidth = 1;
            if (opposite) {
                gridLineWidth = 1;
            }
            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                //tickAmount: 8,
                gridLineWidth: gridLineWidth,
                // offset: 10,
                labels: {
                    format: '{value} ',
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                showEmpty: false,
                opposite: opposite,
                min: min,
                max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }

        me.filename = timeseries_names + (me.graphtype == 'xy' ? esapp.Utils.getTranslation('PROFILE') : me.graphtype)
        if (esapp.Utils.objectExists(me.graphProperties.title)){
            me.filename += '_' + me.graphProperties.title.replace(' ', '_');
        }
        if (esapp.Utils.objectExists(me.graphProperties.subtitle)){
            me.filename += '_' + me.graphProperties.subtitle.toString().replace(' ', '_');
        }

        var timeseries = me.timeseriesGraph.timeseries;

        var spacingRight = 10;
        if (me.timeseriesGraph.yaxes.length == 1) {
            spacingRight = 30;
        }

        var seriesMarkerEnabled = true;
        if (me.graphtype == 'cumulative'){
            seriesMarkerEnabled = false;
        }
        me.tsgraph = new Highcharts.Chart({
            chart: {
                renderTo: 'tsgraph_' + me.id,
                className: 'chartfitlayout',
                zoomType: 'xy',
                alignTicks: true,
                spacingLeft: 25,
                spacingRight: spacingRight,
                plotBackgroundImage: plotBackgroundImage
                // spacingBottom: 50,      // set when logo and disclamer objects are shown under togglebutton
                // spacingTop: 60,         // set when logo and disclamer objects are shown under togglebutton
                // margin: chartMargin, // [35, 15, 65, 65],  // for legend on the bottom of the chart
                // marginTop:top,
                // marginRight: marginright,
                // marginBottom: 160,
                // marginLeft:left,
            },
            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                series: {
                    connectNulls: false,
                    // pointPlacement: 'on',
                    marker: {
                        enabled: seriesMarkerEnabled,
                        radius: 2,
                        states: {
                            hover: {
                                enabled: true,
                                radius: 4,
                                radiusPlus: 0
                                // lineWidthPlus: 2,
                            }
                        }
                    },
                    states: {
                        hover: {
                            halo: {
                                size: 0
                            },
                            lineWidthPlus: 1
                        }
                    }
                },
                line: {
                    marker: {
                        enabled: true,
                        radius: 2
                    }
                },
                column: {
                    pointPadding: 0,
                    //pointWidth: 15,
                    borderWidth: 0,
                    groupPadding: 0,
                    shadow: false
                },
                area: {
                    stacking: 'normal',
                    lineWidth: 1
                }
            },
            title: {
                text: me.graphProperties.title,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_title_font_size + 'px'
                }
            },
            subtitle: {
                text: me.graphProperties.subtitle,
                align: 'center',
                //y: 65,
                style: {
                    color: me.graphProperties.graph_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_subtitle_font_size + 'px'
                }
            },
            xAxis: xAxis,
            yAxis: Yaxes,
            tooltip: {
                shared: true,
                split: true,
                dateTimeLabelFormats: {
                    millisecond: '',
                    second: '',
                    minute: '',
                    hour: '',
                    day: "",
                    month: '',
                    year: '%e %b %Y'
                }
            },
            legend: {
                layout: 'horizontal',  // horizontal vertical
                align: 'center', // center left right
                verticalAlign: 'bottom',  // top, middle or bottom
                floating: false,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                //borderColor: Highcharts.theme.legendBackgroundColor || '#FFFFFF',
                symbolPadding: 3,
                symbolWidth: 30,
                symbolHeight: 20,
                borderRadius: 3,
                borderWidth: 0,
                itemMarginBottom: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px',     // '18px',
                    color: me.graphProperties.legend_title_font_color     //'black'
                },
                itemHiddenStyle: {
                    color: 'gray'
                }
            },
            series: timeseries
        });

        if (me.showObjects){
            var graphObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));
            graphObjectToggleBtn.toggle(true);
            me.getController().toggleObjects(graphObjectToggleBtn);
        }

        me.tsgraph.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tsgraph.redraw();

        if (me.graphtype == 'cumulative' && refNullValuesChangedToDiffValue){
            Ext.toast({anchor: me, hideDuration: 4000, html: esapp.Utils.getTranslation('warning_cumul_values_changed'), title: '', width: 350, align: 't'});
        }
    },

    createRankingChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }

        var xAxisLabels = {
            enabled: 1,
            autoRotation: [-10, -20, -30, -40, -50, -60, -70, -80, -90],
            // autoRotation: -90,
            // staggerLines: 2,
            // autoRotationLimit: 30,
            // x: 0,
            // y: 25,
            style: {
                margin: '0 0 0 0',
                color: me.graphProperties.xaxe_font_color,
                "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                "fontWeight": 'bold',
                "fontSize": me.graphProperties.xaxe_font_size + 'px'
            }
        };

        var xAxis = [{
                type: 'category',
                tickmarkPlacement: 'between',      // on between  - For categorized axes only!
                startOnTick: true,
                endOnTick: false,
                maxPadding: 0.25,
                labels: xAxisLabels
            }]

        me.timeseriesGraph.timeseries.forEach(function (timeserie) {
            timeserie.data.forEach(function (dataItem){
                dataItem.color = esapp.Utils.convertRGBtoHex(dataItem.color);
            })
            timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        });


        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            // if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
            //     opposite = true;
            // console.info(Ext.util.JSON.decode(me.selectedTimeseries));
            var unit = '';
            if (!Ext.util.JSON.decode(me.selectedTimeseries)[0].zscore) {
                unit = me.timeseriesGraph.yaxes[yaxescount].unit;
                if (unit == null || unit.trim() == '')
                    unit = ''
                else unit = ' (' + unit + ')'
            }
            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min != null){
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max != null) {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                gridLineWidth: 1,
                offset: 10,
                labels: {
                    format: '{value} ',
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                showEmpty:false,
                opposite: opposite
                ,min: min
                ,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }

        me.filename = timeseries_names + (me.graphtype == 'xy' ? esapp.Utils.getTranslation('PROFILE') : me.graphtype)
        if (esapp.Utils.objectExists(me.graphProperties.title)){
            me.filename += '_' + me.graphProperties.title.replace(' ', '_');
        }
        if (esapp.Utils.objectExists(me.graphProperties.subtitle)){
            me.filename += '_' + me.graphProperties.subtitle.toString().replace(' ', '_');
        }

        var timeseries = me.timeseriesGraph.timeseries;
        //console.info(timeseries);

        var spacingRight = 15;
        if (me.timeseriesGraph.yaxes.length == 1) {
            spacingRight = 20;
        }


        me.tsgraph = new Highcharts.Chart({
            chart: {
                // type: 'column',
                renderTo: 'tsgraph_' + me.id,
                className: 'chartfitlayout',
                zoomType: 'xy',
                spacingLeft: 10,
                spacingRight: spacingRight,
                alignTicks: false,
                plotBackgroundImage: plotBackgroundImage
            },
            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },
            credits: {
                enabled: false
            },
            plotOptions: {
                // column: {
                //     pointPadding: 0.2,
                //     borderWidth: 0
                // },
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function(event) {
                                var series = me.tsgraph.series[0];
                                series.data.forEach(function(point) {
                                    point.update({ color: series.color }, true, false);
                                });
                                series.redraw();
                                this.update({ color: '#ff0000' }, true, false);
                            }
                        }
                    }
                }
            },
            title: {
                text: me.graphProperties.title,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_title_font_size + 'px'
                }
            },
            subtitle: {
                text: me.graphProperties.subtitle,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_subtitle_font_size + 'px'
                }
            },
            xAxis: xAxis,
            yAxis: Yaxes,
            tooltip: {
                shared: true,
                split: true,
                dateTimeLabelFormats: {
                    millisecond: '',
                    second: '',
                    minute: '',
                    hour: '',
                    day: "",
                    month: '',
                    year: '%e %b %Y'
                }
            },
            legend: {
                layout: 'horizontal',  // horizontal vertical
                align: 'center', // center left right
                verticalAlign: 'bottom',
                floating: false,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                symbolPadding: 3,
                symbolWidth: 35,
                symbolHeight: 25,
                borderRadius: 3,
                borderWidth: 0,
                itemMarginBottom: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px',     // '18px',
                    color: me.graphProperties.legend_title_font_color
                },
                itemHiddenStyle: {
                    color: 'gray'
                }
            },
            series: timeseries
        });

        if (me.showObjects){
            var graphObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));
            graphObjectToggleBtn.toggle(true);
            me.getController().toggleObjects(graphObjectToggleBtn);
        }
        me.tsgraph.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tsgraph.redraw();
        //console.info(me.tsgraph);
    },

    createMatrixChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];
        var legend = {};

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }
        var timeseries = me.timeseriesGraph.timeseries[0];

        var colsize = 11 * 24 * 36e5; // 10 days    Dekad
        if (me.timeseriesGraph.data_available){
            if (timeseries.frequency_id == 'e1day')
                colsize = 1 * 24 * 36e5; // 1 day
            if (timeseries.frequency_id == 'e1modis8day')
                colsize = 8 * 24 * 36e5; // 8 days
            if (timeseries.frequency_id == 'e1modis16day')
                colsize = 16 * 24 * 36e5; // 16 days
            if (timeseries.frequency_id == 'e1month')
                colsize = 30 * 24 * 36e5; // 30 days
            if (timeseries.frequency_id == 'e3month')
                colsize = 3*30 * 24 * 36e5; // 3*30 days
            if (timeseries.frequency_id == 'e6month')
                colsize = 6*30 * 24 * 36e5; // 6*30 days
            if (timeseries.frequency_id == 'e1dekad')
                colsize = 11 * 24 * 36e5; // 11 days
        }

        var series = [];
        if (me.timeseriesGraph.data_available) {
            series = [{
                name: timeseries.name,
                borderWidth: 0,
                borderColor: "#ffffff",
                nullColor: 'transparent',
                colsize: colsize,   // 2 * 24 * 36e5, // 11 days     // 30 * me.timeseriesGraph.yaxes[0].categories.length,  // (me.tsgraph.plotWidth / (timeseries.data.length / me.timeseriesGraph.categories.length)),    //
                data: timeseries.data
            }]
        }

        var colorAxis = me.timeseriesGraph.colorAxis;

        if (Ext.isDefined(colorAxis.stops)) {
            legend = {
                layout: 'horizontal',       // horizontal vertical
                align: 'center',            // center left right
                verticalAlign: 'bottom',    // bottom
                title: {
                    text: timeseries.name,
                    margin: 0,
                    padding: 0,
                    style: {
                        fontStyle: 'italic',
                        fontSize: me.graphProperties.legend_title_font_size + 'px'
                    }
                },
                // padding: 50,
                // width: 460,
                symbolWidth: 500
                // itemStyle: {
                //     "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                //     "fontWeight": 'bold',
                //     "fontSize": me.graphProperties.legend_title_font_size + 'px'
                // }
            };

            colorAxis.labels = {
                style: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px'
                },
                formatter: function () {
                    if (this.value % 1 === 0)
                        return this.value;
                    else
                        return this.value.toFixed(2);
                }
            }
        }
        else {
            legend = {
                layout: 'vertical',      // horizontal vertical
                align: 'right',          // center left right
                verticalAlign: 'top',    // bottom
                x: 0,
                y: 100,
                width: 100,
                margin: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px'
                },
                title: {
                    text: timeseries.name,
                    style: {
                        fontStyle: 'italic',
                        "fontSize": me.graphProperties.legend_title_font_size + 'px',
                        width: 100
                    }
                }
            };
        }

        var xAxisLabels = {
            enabled: 1,
            // autoRotationLimit: -40,
            y: 20,
            style: {
                color: me.graphProperties.xaxe_font_color,
                "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                "fontWeight": 'bold',
                "fontSize": me.graphProperties.xaxe_font_size + 'px',
                margin: '0 0 0 0'
            },
            format: '{value:%b}' // long month
            //formatter: function () {
            //    return Highcharts.dateFormat('%b', this.value);
            //}
        };

        var xAxis = [{
            type: 'datetime',
            reversed: false,
            ordinal: true,
            showEmpty: false,
            tickmarkPlacement: 'on',      // on between  - For categorized axes only!
            startOnTick: false,
            lineWidth: 1,
            labels: xAxisLabels
            ,tickInterval: 30 * 24 * 3600 * 1000    //   colsize  //
        }];

        //me.timeseriesGraph.timeseries.forEach(function (timeserie) {
        //    timeserie.data.forEach(function (dataItem){
        //        dataItem.color = esapp.Utils.convertRGBtoHex(dataItem.color);
        //    })
        //    timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        //});

        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            // if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
            //     opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min != null){
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max != null) {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                gridLineWidth: 1,
                startOnTick: false,
                endOnTick: false,
                offset: 10,
                labels: {
                    format: '{value} ',
                    // padding: 10,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    padding: 10,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                showEmpty: false,
                opposite: opposite
                ,min: min
                ,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }


        me.filename = timeseries_names + (me.graphtype == 'xy' ? esapp.Utils.getTranslation('PROFILE') : me.graphtype)
        if (esapp.Utils.objectExists(me.graphProperties.title)){
            me.filename += '_' + me.graphProperties.title.replace(' ', '_');
        }
        if (esapp.Utils.objectExists(me.graphProperties.subtitle)){
            me.filename += '_' + me.graphProperties.subtitle.toString().replace(' ', '_');
        }

        var spacingRight = 20;
        if (Ext.isDefined(colorAxis.stops)) {
           spacingRight = 30;
        }

        //Highcharts.theme = {
        //    colors: ['#90006F', '#3300CC', '#004AFF', '#00F5FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000', '#690000']    // me.timeseriesGraph.colors
        //}
        //
        //Highcharts.setOptions(Highcharts.theme);
        //
        //me.tsgraph = new Highcharts.Chart(Highcharts.merge(Highcharts.theme,{
        me.tsgraph = new Highcharts.Chart({

            chart: {
                type: 'heatmap',
                renderTo: 'tsgraph_' + me.id,
                className: 'chartfitlayout',
                spacingLeft: 10,
                spacingRight: spacingRight,
                plotBackgroundImage: plotBackgroundImage
            },

            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },

            credits: {
                enabled: false
            },

            title: {
                text: me.graphProperties.title,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_title_font_size + 'px'
                }
            },

            subtitle: {
                text: me.graphProperties.subtitle,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_subtitle_font_size + 'px'
                }
            },

            //plotOptions: {
                //heatmap: {
                //    //colorByPoint: true,
                //    colors: ['#90006F', '#3300CC', '#004AFF', '#00F5FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000', '#690000']    // me.timeseriesGraph.colors
                //}
                //series: {
                //    turboThreshold: 0
                //    point: {
                //        events: {
                //            mouseOver: function () {
                //                console.log(this);
                //                this.shapeArgs.width = 2;
                //            }
                //        }
                //    }
                //}
            //},

            series: series,
            xAxis: xAxis,
            yAxis: Yaxes,
            colorAxis: colorAxis,
            legend: legend,

            tooltip: {
                formatter: function () {
                    if (this.point.value == null){
                        return false;
                    }
                    else {
                        return '<b>' + Highcharts.dateFormat('%d %b', this.point.x) + ' ' + this.point.y +
                                //'</b> Year: <br><b>' + this.point.y + '</b>' +
                            '<br>' + this.point.value
                            ;
                    }
                    //return '<b>Date:' + this.series.xAxis.categories[this.point.x] + '</b> Value: <br><b>' +
                    //    this.point.value + '</b> Year: <br><b>' + this.series.yAxis.categories[this.point.y] + '</b>';
                }
            }
        });
        //}));

        if (me.showObjects){
            var graphObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));
            graphObjectToggleBtn.toggle(true);
            me.getController().toggleObjects(graphObjectToggleBtn);
        }

        me.tsgraph.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tsgraph.redraw();
        //console.info(me.tsgraph);
    },

    createScatterChart: function(mecallback) {
        var me = mecallback;
        var plotBackgroundImage = '';
        var categories = [];
        var legend = {};

        if (!me.timeseriesGraph.data_available) {
            plotBackgroundImage = 'resources/img/no_data.gif';
        }
        var timeseries = me.timeseriesGraph.timeseries[0];

        var colsize = 11 * 24 * 36e5; // 10 days    Dekad
        if (me.timeseriesGraph.data_available){
            if (timeseries.frequency_id == 'e1day')
                colsize = 1 * 24 * 36e5; // 1 day
            if (timeseries.frequency_id == 'e1modis8day')
                colsize = 8 * 24 * 36e5; // 8 days
            if (timeseries.frequency_id == 'e1modis16day')
                colsize = 16 * 24 * 36e5; // 16 days
            if (timeseries.frequency_id == 'e1month')
                colsize = 30 * 24 * 36e5; // 30 days
            if (timeseries.frequency_id == 'e3month')
                colsize = 3*30 * 24 * 36e5; // 3*30 days
            if (timeseries.frequency_id == 'e6month')
                colsize = 6*30 * 24 * 36e5; // 6*30 days
            if (timeseries.frequency_id == 'e1dekad')
                colsize = 11 * 24 * 36e5; // 11 days
        }

        var series = [];
        if (me.timeseriesGraph.data_available) {
            series = [{
                name: timeseries.name,
                borderWidth: 0,
                borderColor: "#ffffff",
                nullColor: 'transparent',
                colsize: colsize,   // 2 * 24 * 36e5, // 11 days     // 30 * me.timeseriesGraph.yaxes[0].categories.length,  // (me.tsgraph.plotWidth / (timeseries.data.length / me.timeseriesGraph.categories.length)),    //
                data: timeseries.data
            }]
        }

        var colorAxis = me.timeseriesGraph.colorAxis;

        if (Ext.isDefined(colorAxis.stops)) {
            legend = {
                layout: 'horizontal',       // horizontal vertical
                align: 'center',            // center left right
                verticalAlign: 'bottom',    // bottom
                title: {
                    text: timeseries.name,
                    margin: 0,
                    padding: 0,
                    style: {
                        fontStyle: 'italic',
                        fontSize: me.graphProperties.legend_title_font_size + 'px'
                    }
                },
                // padding: 50,
                // width: 460,
                symbolWidth: 500
                // itemStyle: {
                //     "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                //     "fontWeight": 'bold',
                //     "fontSize": me.graphProperties.legend_title_font_size + 'px'
                // }
            };

            colorAxis.labels = {
                style: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px'
                },
                formatter: function () {
                    if (this.value % 1 === 0)
                        return this.value;
                    else
                        return this.value.toFixed(2);
                }
            }
        }
        else {
            legend = {
                layout: 'vertical',      // horizontal vertical
                align: 'right',          // center left right
                verticalAlign: 'top',    // bottom
                x: 0,
                y: 100,
                width: 100,
                margin: 10,
                itemStyle: {
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.legend_title_font_size + 'px'
                },
                title: {
                    text: timeseries.name,
                    style: {
                        fontStyle: 'italic',
                        "fontSize": me.graphProperties.legend_title_font_size + 'px',
                        width: 100
                    }
                }
            };
        }

        var xAxisLabels = {
            enabled: 1,
            // autoRotationLimit: -40,
            y: 20,
            style: {
                color: me.graphProperties.xaxe_font_color,
                "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                "fontWeight": 'bold',
                "fontSize": me.graphProperties.xaxe_font_size + 'px',
                margin: '0 0 0 0'
            },
            format: '{value:%b}' // long month
            //formatter: function () {
            //    return Highcharts.dateFormat('%b', this.value);
            //}
        };

        var xAxis = [{
            type: 'datetime',
            reversed: false,
            ordinal: true,
            showEmpty: false,
            tickmarkPlacement: 'on',      // on between  - For categorized axes only!
            startOnTick: false,
            lineWidth: 1,
            labels: xAxisLabels
            ,tickInterval: 30 * 24 * 3600 * 1000    //   colsize  //
        }];

        //me.timeseriesGraph.timeseries.forEach(function (timeserie) {
        //    timeserie.data.forEach(function (dataItem){
        //        dataItem.color = esapp.Utils.convertRGBtoHex(dataItem.color);
        //    })
        //    timeserie.color = esapp.Utils.convertRGBtoHex(timeserie.color);
        //});

        var Yaxes = [];
        var timeseries_names = '';
        for (var yaxescount = 0; yaxescount < me.timeseriesGraph.yaxes.length; yaxescount++) {
            var opposite = false;
            // if (me.timeseriesGraph.yaxes[yaxescount].opposite === 'true' ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == true ||
            //     me.timeseriesGraph.yaxes[yaxescount].opposite == 'true')
            //     opposite = true;

            var unit = me.timeseriesGraph.yaxes[yaxescount].unit;
            if (unit == null || unit.trim() == '')
                unit = ''
            else unit = ' (' + unit + ')'

            var min = me.timeseriesGraph.yaxes[yaxescount].min;
            if (min != null){
                min =  parseFloat(me.timeseriesGraph.yaxes[yaxescount].min)
            }
            var max = me.timeseriesGraph.yaxes[yaxescount].max;
            if (max != null) {
                max = parseFloat(me.timeseriesGraph.yaxes[yaxescount].max)
            }

            me.timeseriesGraph.yaxes[yaxescount].title_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[yaxescount].title_color);

            var yaxe = {
                id: me.timeseriesGraph.yaxes[yaxescount].id,
                gridLineWidth: 1,
                startOnTick: false,
                endOnTick: false,
                offset: 10,
                labels: {
                    format: '{value} ',
                    // padding: 10,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                title: {
                    text: me.timeseriesGraph.yaxes[yaxescount].title + unit,
                    padding: 10,
                    style: {
                        color: me.timeseriesGraph.yaxes[yaxescount].title_color,  // Highcharts.getOptions().colors[yaxescount],
                        "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                        "fontWeight": 'bold',
                        "fontSize": me.timeseriesGraph.yaxes[yaxescount].title_font_size + 'px'
                    }
                },
                showEmpty:false,
                opposite: opposite
                ,min: min
                ,max: max
            };
            Yaxes.push(yaxe);
            timeseries_names += me.timeseriesGraph.yaxes[yaxescount].title.replace(' ', '_') + '_';
        }


        me.filename = timeseries_names + (me.graphtype == 'xy' ? esapp.Utils.getTranslation('PROFILE') : me.graphtype)
        if (esapp.Utils.objectExists(me.graphProperties.title)){
            me.filename += '_' + me.graphProperties.title.replace(' ', '_');
        }
        if (esapp.Utils.objectExists(me.graphProperties.subtitle)){
            me.filename += '_' + me.graphProperties.subtitle.toString().replace(' ', '_');
        }

        var spacingRight = 20;
        if (Ext.isDefined(colorAxis.stops)) {
           spacingRight = 30;
        }

        //Highcharts.theme = {
        //    colors: ['#90006F', '#3300CC', '#004AFF', '#00F5FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000', '#690000']    // me.timeseriesGraph.colors
        //}
        //
        //Highcharts.setOptions(Highcharts.theme);
        //
        //me.tsgraph = new Highcharts.Chart(Highcharts.merge(Highcharts.theme,{
        me.tsgraph = new Highcharts.Chart({

            chart: {
                type: 'heatmap',
                renderTo: 'tsgraph_' + me.id,
                className: 'chartfitlayout',
                spacingLeft: 10,
                spacingRight: spacingRight,
                plotBackgroundImage: plotBackgroundImage
            },

            exporting: {
                enabled: false,
                buttons: {
                    exportButton: {
                        enabled: false
                    },
                    printButton: {
                        enabled: false
                    }

                }
            },

            credits: {
                enabled: false
            },

            title: {
                text: me.graphProperties.title,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_title_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_title_font_size + 'px'
                }
            },

            subtitle: {
                text: me.graphProperties.subtitle,
                align: 'center',
                style: {
                    color: me.graphProperties.graph_subtitle_font_color,
                    "font-family": 'Arial, Verdana, Helvetica, sans-serif',
                    "fontWeight": 'bold',
                    "fontSize": me.graphProperties.graph_subtitle_font_size + 'px'
                }
            },

            //plotOptions: {
                //heatmap: {
                //    //colorByPoint: true,
                //    colors: ['#90006F', '#3300CC', '#004AFF', '#00F5FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000', '#690000']    // me.timeseriesGraph.colors
                //}
                //series: {
                //    turboThreshold: 0
                //    point: {
                //        events: {
                //            mouseOver: function () {
                //                console.log(this);
                //                this.shapeArgs.width = 2;
                //            }
                //        }
                //    }
                //}
            //},

            series: series,
            xAxis: xAxis,
            yAxis: Yaxes,
            colorAxis: colorAxis,
            legend: legend,

            tooltip: {
                formatter: function () {
                    if (this.point.value == null){
                        return false;
                    }
                    else {
                        return '<b>' + Highcharts.dateFormat('%d %b', this.point.x) + ' ' + this.point.y +
                                //'</b> Year: <br><b>' + this.point.y + '</b>' +
                            '<br>' + this.point.value
                            ;
                    }
                    //return '<b>Date:' + this.series.xAxis.categories[this.point.x] + '</b> Value: <br><b>' +
                    //    this.point.value + '</b> Year: <br><b>' + this.series.yAxis.categories[this.point.y] + '</b>';
                }
            }
        });
        //}));

        if (me.showObjects){
            var graphObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_'));
            graphObjectToggleBtn.toggle(true);
            me.getController().toggleObjects(graphObjectToggleBtn);
        }

        me.tsgraph.setSize(document.getElementById(me.id + "-body").offsetWidth, document.getElementById(me.id + "-body").offsetHeight);
        me.tsgraph.redraw();
        //console.info(me.tsgraph);
    },

    generateChart: function(){
        var me = this.getView();
        var user = esapp.getUser();
        var graphpropertiesStore = this.getStore('graphproperties');

        me.tsFromSeason =  me.tsFromSeason instanceof Date ? Ext.Date.format(me.tsFromSeason, 'm-d') : me.tsFromSeason;          // !(me.tsFromSeason instanceof Date)
        me.tsToSeason = me.tsToSeason instanceof Date ? Ext.Date.format(me.tsToSeason, 'm-d') : me.tsToSeason;
        me.tsFromPeriod = me.tsFromPeriod instanceof Date ? Ext.Date.format(me.tsFromPeriod, 'Y-m-d') : me.tsFromPeriod;
        me.tsToPeriod = me.tsToPeriod instanceof Date ? Ext.Date.format(me.tsToPeriod, 'Y-m-d') : me.tsToPeriod;

        if (user != 'undefined' && user != null){
            Ext.fly('graphview_title_templatename_' + me.id).dom.innerHTML = me.isTemplate ? me.graph_tpl_name : '';
            // me.selectedregionname = me.isTemplate ? me.selectedregionname : me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('selectedregionname').getValue();
        }
        // else {
        //     me.selectedregionname = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).lookupReference('selectedregionname').getValue();
        // }

        if (me.graphtype == 'cumulative'){
            // me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('CUMULATIVE')+ ' ' + esapp.Utils.getTranslation('GRAPH')+ ' - ' + Ext.getCmp('selectedregionname').getValue() +'</span>');
            Ext.fly('graphview_title_' + me.id).dom.innerHTML = esapp.Utils.getTranslation('CUMULATIVE');
                                                                // + ' ' + esapp.Utils.getTranslation('GRAPH');
                                                                // me.selectedregionname;
        }
        else if (me.graphtype == 'ranking'){
            // me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('RANKING_ZSCORE')+ ' ' + esapp.Utils.getTranslation('GRAPH')+ ' - ' + Ext.getCmp('selectedregionname').getValue() +'</span>');
            Ext.fly('graphview_title_' + me.id).dom.innerHTML = esapp.Utils.getTranslation('RANKING_ZSCORE');
                                                                // + ' ' + esapp.Utils.getTranslation('GRAPH');
                                                                // me.selectedregionname;
        }
        else if (me.graphtype == 'matrix'){
            // me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('MATRIX')+ ' ' + esapp.Utils.getTranslation('GRAPH')+ ' - ' + Ext.getCmp('selectedregionname').getValue() +'</span>');
            Ext.fly('graphview_title_' + me.id).dom.innerHTML = esapp.Utils.getTranslation('MATRIX');
                                                                // + ' ' + esapp.Utils.getTranslation('GRAPH');
                                                                // me.selectedregionname;
        }
        else if (me.graphtype == 'scatter'){
            // me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('SCATTER')+ ' ' + esapp.Utils.getTranslation('GRAPH')+ ' - ' + Ext.getCmp('selectedregionname').getValue() +'</span>');
            Ext.fly('graphview_title_' + me.id).dom.innerHTML = esapp.Utils.getTranslation('SCATTER');
                                                                // + ' ' + esapp.Utils.getTranslation('GRAPH');
                                                                // me.selectedregionname;
        }
        else {
            // me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('PROFILE')+ ' ' + esapp.Utils.getTranslation('GRAPH')+ ' - ' + Ext.getCmp('selectedregionname').getValue() +'</span>');
            Ext.fly('graphview_title_' + me.id).dom.innerHTML = esapp.Utils.getTranslation('PROFILE');
                                                                // + ' ' + esapp.Utils.getTranslation('GRAPH');
                                                                // me.selectedregionname;
        }

        var storeparams = {
                graphtype: me.graphtype
            }
        if (user != 'undefined' && user != null){
            storeparams.userid = user.userid;
            storeparams.graph_tpl_id = esapp.Utils.objectExists(me.graph_tpl_id) ? me.graph_tpl_id : -1;
            storeparams.graph_tpl_name = me.isTemplate ? me.graph_tpl_name : 'default';
        }
        me.lookupReference('tbar_'+me.id).disable();
        graphpropertiesStore.load({
            params: storeparams,
            callback:function(){
                if (me.graphtype == 'scatter'){
                    me.getController().getTimeseries(me.getController().createScatterChart);
                }
                else {
                    me.getController().setGraphProperties();
                    // graphpropertiesStore.each(function(graphproperties) {
                    //     var height = parseInt(graphproperties.get('graph_height'));
                    //     if (height > Ext.getBody().getViewSize().height-80){
                    //         height = Ext.getBody().getViewSize().height-80
                    //     }
                    //     me.setSize(parseInt(graphproperties.get('graph_width')), height);
                    // });
                    if (me.graphtype == 'ranking'){
                        me.getController().getTimeseries(me.getController().createRankingChart);
                    }
                    else if (me.graphtype == 'matrix'){
                        me.getController().getTimeseries(me.getController().createMatrixChart);
                    }
                    else {
                        me.getController().getTimeseries(me.getController().createDefaultChart);
                    }
                }
            }
        });
    },

    refreshChart: function(){
        var me = this.getView();
        // var graphpropertiesStore = this.getStore('graphproperties');
        // var timeseriesselections = null;

        var selectedProductsAndTimeFramePanel = Ext.getCmp(me.getId()+'-select_products_timeframe');
        me.tsdrawprops = selectedProductsAndTimeFramePanel.down('timeseriesproductselection').getController().getSelectedTSDrawProperties();

        // var chartdrawpropertiespanel = this.lookupReference('chart_draw_properties_' + me.id);
        // if (chartdrawpropertiespanel != null){
        //     chartdrawpropertiespanel.destroy();
        // }

        // if (!me.isTemplate){
        //     timeseriesselections = me.workspace.lookupReference('timeserieschartselection'+me.workspace.id).getController().getTimeseriesSelections(me.graphtype);
        //     if (timeseriesselections != null) {
        //         //console.info(timeseriesselections);
        //         me.selectedTimeseries = timeseriesselections.selectedTimeseries;
        //         me.yearTS = timeseriesselections.yearTS;
        //         me.tsFromPeriod = timeseriesselections.tsFromPeriod;
        //         me.tsToPeriod = timeseriesselections.tsToPeriod;
        //         me.yearsToCompare = timeseriesselections.yearsToCompare;
        //         me.tsFromSeason = timeseriesselections.tsFromSeason;
        //         me.tsToSeason = timeseriesselections.tsToSeason;
        //         me.wkt_geom = timeseriesselections.wkt_geom;
        //     }
        // }
        if( me.tsgraph instanceof Highcharts.Chart) {
            me.tsgraph.destroy();
        }
        me.tsgraph = null;

        me.lookupReference('tbar_'+me.id).disable();
        me.getController().setGraphProperties();
        me.graphProperties.localRefresh = false;
        if (me.graphtype == 'ranking') {
            // me.getController().createRankingChart(me);
            me.getController().getTimeseries(me.getController().createRankingChart);

        }
        else if (me.graphtype == 'matrix') {
            // me.getController().createMatrixChart(me);
            me.getController().getTimeseries(me.getController().createMatrixChart);
        }
        else {
            // me.getController().createDefaultChart(me);
            me.getController().getTimeseries(me.getController().createDefaultChart);
        }
        // this.generateChart();
    },

    openChartProperties: function() {
        var me = this.getView(),
            thiscontroller = this,
            source = {},
            yaxe1 = {},
            yaxe2 = {},
            yaxe3 = {}

        var chartDrawPropertiesPanel = Ext.getCmp('chart_draw_properties_'+me.id);
        me.lookupReference('tbar_'+me.id).disable();

        if (!chartDrawPropertiesPanel) {
            var crenderer = function (color) {
                renderTpl = color;

                if (color.trim() == '') {
                    renderTpl = 'transparent';
                }
                else {
                    renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
                }
                return renderTpl;
            };

            var fontsizes = Ext.create('Ext.data.Store', {      // [8,9,10,11,12,14,16,18,20,22,24,26,28,30,32,34,36,48,72]
                fields: ['fontsize'],
                data: [
                    {'fontsize': 8},
                    {'fontsize': 9},
                    {'fontsize': 10},
                    {'fontsize': 11},
                    {'fontsize': 12},
                    {'fontsize': 14},
                    {'fontsize': 16},
                    {'fontsize': 18},
                    {'fontsize': 20},
                    {'fontsize': 22},
                    {'fontsize': 24},
                    {'fontsize': 26},
                    {'fontsize': 28},
                    {'fontsize': 30},
                    {'fontsize': 32},
                    {'fontsize': 34},
                    {'fontsize': 36},
                    {'fontsize': 48},
                    {'fontsize': 72}
                ]
            });

            var fontsizesCombo = {
                xtype: 'combobox',
                store: fontsizes,
                queryMode: 'local',
                displayField: 'fontsize',
                valueField: 'fontsize',
                forceSelection: true,
                triggerAction: 'all',
                allowBlank: false,
                editable: false
            };

            var aggregationTypeStoreYaxe1 = ['mean', 'count', 'percent'];
            var aggregationTypeStoreYaxe2 = ['mean', 'count', 'percent'];
            var aggregationTypeStoreYaxe3 = ['mean', 'count', 'percent'];
            var aggregationTypeStoreYaxe4 = ['mean', 'count', 'percent'];

            source = {
                // graph_width: me.graphProperties.width,
                // graph_height: me.graphProperties.height,

                graph_title: me.graphProperties.title,
                graph_title_font_color: esapp.Utils.convertRGBtoHex(me.graphProperties.graph_title_font_color),
                graph_title_font_size: me.graphProperties.graph_title_font_size,

                graph_subtitle: me.graphProperties.subtitle,
                graph_subtitle_font_color: esapp.Utils.convertRGBtoHex(me.graphProperties.graph_subtitle_font_color),
                graph_subtitle_font_size: me.graphProperties.graph_subtitle_font_size,

                legend_font_size: me.graphProperties.legend_title_font_size,
                legend_font_color: esapp.Utils.convertRGBtoHex(me.graphProperties.legend_title_font_color),

                xaxe_font_size: me.graphProperties.xaxe_font_size,
                xaxe_font_color: esapp.Utils.convertRGBtoHex(me.graphProperties.xaxe_font_color)
            }

            source.yaxe1_id = me.timeseriesGraph.yaxes[0].id;
            source.yaxe1_title = me.timeseriesGraph.yaxes[0].title;
            // source.yaxe1_font_size = me.graphProperties.yaxe1_font_size;    // from TABLE!
            source.yaxe1_font_size = me.timeseriesGraph.yaxes[0].title_font_size;    // from TABLE!
            source.yaxe1_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[0].title_color);
            source.yaxe1_min = me.timeseriesGraph.yaxes[0].min;
            source.yaxe1_max = me.timeseriesGraph.yaxes[0].max;
            source.yaxe1_opposite = me.timeseriesGraph.yaxes[0].opposite;
            source.yaxe1_unit = me.timeseriesGraph.yaxes[0].unit;
            source.yaxe1_aggregation_type = me.timeseriesGraph.yaxes[0].aggregation_type;
            source.yaxe1_aggregation_min = me.timeseriesGraph.yaxes[0].aggregation_min;
            source.yaxe1_aggregation_max = me.timeseriesGraph.yaxes[0].aggregation_max;
            // console.info(me.timeseriesGraph.yaxes[0].id);
            if (me.timeseriesGraph.yaxes[0].id.includes("rain")){
                aggregationTypeStoreYaxe1 = ['mean', 'percent', 'precip'];
            }
            else if (me.timeseriesGraph.yaxes[0].id.includes("WBD"))  {       // "inlandwater"
                aggregationTypeStoreYaxe1 = ['percent', 'surface'];
            }
            else if (me.timeseriesGraph.yaxes[0].id.includes("fire")){
                aggregationTypeStoreYaxe1 = ['mean', 'count', 'percent', 'cumulate'];
            }
            else if (me.timeseriesGraph.yaxes[0].id.includes("ba")){
                aggregationTypeStoreYaxe1 = ['percent', 'surface','count'];
            }

            if (me.timeseriesGraph.yaxes.length > 1) {
                source.yaxe2_id = me.timeseriesGraph.yaxes[1].id;
                source.yaxe2_title = me.timeseriesGraph.yaxes[1].title;
                // source.yaxe2_font_size = me.graphProperties.yaxe2_font_size;    // from TABLE!
                source.yaxe2_font_size = me.timeseriesGraph.yaxes[1].title_font_size;    // from TABLE!
                source.yaxe2_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[1].title_color);
                source.yaxe2_min = me.timeseriesGraph.yaxes[1].min;
                source.yaxe2_max = me.timeseriesGraph.yaxes[1].max;
                source.yaxe2_opposite = me.timeseriesGraph.yaxes[1].opposite;
                source.yaxe2_unit = me.timeseriesGraph.yaxes[1].unit;
                source.yaxe2_aggregation_type = me.timeseriesGraph.yaxes[1].aggregation_type;
                source.yaxe2_aggregation_min = me.timeseriesGraph.yaxes[1].aggregation_min;
                source.yaxe2_aggregation_max = me.timeseriesGraph.yaxes[1].aggregation_max;

                // console.info(me.timeseriesGraph.yaxes[1].id);
                if (me.timeseriesGraph.yaxes[1].id.includes("rain")){
                    aggregationTypeStoreYaxe2 = ['mean', 'percent', 'precip'];
                }
                else if (me.timeseriesGraph.yaxes[1].id.includes("WBD"))  {       // "inlandwater"
                    aggregationTypeStoreYaxe2 = ['percent', 'surface'];
                }
                else if (me.timeseriesGraph.yaxes[1].id.includes("fire")){
                    aggregationTypeStoreYaxe2 = ['mean', 'count', 'percent', 'cumulate'];
                }
                else if (me.timeseriesGraph.yaxes[1].id.includes("ba")){
                    aggregationTypeStoreYaxe2 = ['percent', 'surface','count'];
                }
            }
            if (me.timeseriesGraph.yaxes.length > 2) {
                source.yaxe3_id = me.timeseriesGraph.yaxes[2].id;
                source.yaxe3_title = me.timeseriesGraph.yaxes[2].title;
                // source.yaxe3_font_size = me.graphProperties.yaxe3_font_size;    // from TABLE!
                source.yaxe3_font_size = me.timeseriesGraph.yaxes[2].title_font_size;    // from TABLE!
                source.yaxe3_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[2].title_color);
                source.yaxe3_min = me.timeseriesGraph.yaxes[2].min;
                source.yaxe3_max = me.timeseriesGraph.yaxes[2].max;
                source.yaxe3_opposite = me.timeseriesGraph.yaxes[2].opposite;
                source.yaxe3_unit = me.timeseriesGraph.yaxes[2].unit;
                source.yaxe3_aggregation_type = me.timeseriesGraph.yaxes[2].aggregation_type;
                source.yaxe3_aggregation_min = me.timeseriesGraph.yaxes[2].aggregation_min;
                source.yaxe3_aggregation_max = me.timeseriesGraph.yaxes[2].aggregation_max;

                if (me.timeseriesGraph.yaxes[2].id.includes("rain")){
                    aggregationTypeStoreYaxe3 = ['mean', 'percent', 'precip'];
                }
                else if (me.timeseriesGraph.yaxes[2].id.includes("WBD"))  {       // "inlandwater"
                    aggregationTypeStoreYaxe3 = ['percent', 'surface'];
                }
                else if (me.timeseriesGraph.yaxes[2].id.includes("fire")){
                    aggregationTypeStoreYaxe3 = ['mean', 'count', 'percent', 'cumulate'];
                }
                else if (me.timeseriesGraph.yaxes[2].id.includes("ba")){
                    aggregationTypeStoreYaxe3 = ['percent', 'surface','count'];
                }
            }
            if (me.timeseriesGraph.yaxes.length > 3) {
                source.yaxe4_id = me.timeseriesGraph.yaxes[3].id;
                source.yaxe4_title = me.timeseriesGraph.yaxes[3].title;
                // source.yaxe4_font_size = me.graphProperties.yaxe4_font_size;    // from TABLE!
                source.yaxe4_font_size = me.timeseriesGraph.yaxes[3].title_font_size;    // from TABLE!
                source.yaxe4_color = esapp.Utils.convertRGBtoHex(me.timeseriesGraph.yaxes[3].title_color);
                source.yaxe4_min = me.timeseriesGraph.yaxes[3].min;
                source.yaxe4_max = me.timeseriesGraph.yaxes[3].max;
                source.yaxe4_opposite = me.timeseriesGraph.yaxes[3].opposite;
                source.yaxe4_unit = me.timeseriesGraph.yaxes[3].unit;
                source.yaxe4_aggregation_type = me.timeseriesGraph.yaxes[3].aggregation_type;
                source.yaxe4_aggregation_min = me.timeseriesGraph.yaxes[3].aggregation_min;
                source.yaxe4_aggregation_max = me.timeseriesGraph.yaxes[3].aggregation_max;

                if (me.timeseriesGraph.yaxes[3].id.includes("rain")){
                    aggregationTypeStoreYaxe4 = ['mean', 'percent', 'precip'];
                }
                else if (me.timeseriesGraph.yaxes[3].id.includes("WBD"))  {       // "inlandwater"
                    aggregationTypeStoreYaxe4 = ['percent', 'surface'];
                }
                else if (me.timeseriesGraph.yaxes[3].id.includes("fire")){
                    aggregationTypeStoreYaxe4 = ['mean', 'count', 'percent', 'cumulate'];
                }
                else if (me.timeseriesGraph.yaxes[3].id.includes("ba")){
                    aggregationTypeStoreYaxe4 = ['percent', 'surface','count'];
                }
            }

            chartDrawPropertiesPanel = Ext.create('Ext.panel.Panel', {
                title: esapp.Utils.getTranslation('graph_properties'),     // 'Graph properties',
                id: 'chart_draw_properties_' + me.id,
                reference: 'chart_draw_properties_' + me.id,
                width: 400,
                maxHeight: document.getElementById(me.id + "-body").offsetHeight - 3,
                autoHeight: true,
                margin: '0 0 10 0',
                maximizable: false,
                collapsible: true,
                resizable: true,
                layout: 'fit',
                hidden: true,
                floating: true,
                defaultAlign: 'tl-tl',
                closable: true,
                closeAction: 'hide',
                draggable: true,
                constrain: true,
                alwaysOnTop: true,
                autoShow: false,
                frame: false,
                frameHeader: false,
                border: false,
                shadow: false,
                componentCls: 'newpanelstyle',
                listeners: {
                    close : function (){
                        me.lookupReference('tbar_'+me.id).enable();
                    },
                    focusleave: function(){
                        this.close();
                    }
                },
                items: [
                    {
                        text: esapp.Utils.getTranslation('Chart draw properties'),
                        xtype: 'propertygrid',
                        nameColumnWidth: 180,
                        sortableColumns: false,
                        source: source,
                        sourceConfig: {
                            // graph_width: {
                            //     displayName: esapp.Utils.getTranslation('chartwidth'),   // 'graph width (in px)',
                            //     //type: 'number',
                            //     editor: {
                            //         xtype: 'numberfield',
                            //         selectOnFocus:true
                            //     }
                            // },
                            // graph_height: {
                            //     displayName: esapp.Utils.getTranslation('chartheight'),   // 'graph height (in px)',
                            //     //type: 'number',
                            //     editor: {
                            //         xtype: 'numberfield',
                            //         selectOnFocus:true
                            //     }
                            // },
                            graph_title: {
                                displayName: esapp.Utils.getTranslation('title'),   // 'Title',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            graph_title_font_color: {
                                displayName: esapp.Utils.getTranslation('titlecolor'),   // 'Title color',
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            graph_title_font_size: {
                                displayName: esapp.Utils.getTranslation('titlefontsize'),   // 'Title font size',
                                editor: fontsizesCombo
                            },
                            graph_subtitle: {
                                displayName: esapp.Utils.getTranslation('subtitle'),   // 'Sub title',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            graph_subtitle_font_color: {
                                displayName: esapp.Utils.getTranslation('subtitlecolor'),   // 'Sub title color',
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                    //,floating: false
                                }
                                , renderer: crenderer
                            },
                            graph_subtitle_font_size: {
                                displayName: esapp.Utils.getTranslation('subtitlefontsize'),   // 'Sub title font size',
                                editor: fontsizesCombo
                            },
                            legend_font_size: {
                                displayName: esapp.Utils.getTranslation('legendfontsize'),   // 'Legend font size',
                                editor: fontsizesCombo
                            },
                            legend_font_color: {
                                displayName: esapp.Utils.getTranslation('legendfontcolor'),   // 'Legend font colour',
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            xaxe_font_size: {
                                displayName: esapp.Utils.getTranslation('xaxefontsize'),   // 'xAxe font size',
                                editor: fontsizesCombo
                            },
                            xaxe_font_color: {
                                displayName: esapp.Utils.getTranslation('xaxefontcolor'),   // 'xAxe font color',
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },


                            yaxe1_id: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('id')
                                //type: null
                                //editor: null,
                                //editable: false,
                                //disabled: true,
                                //cls: 'highlightYaxe',
                                //style: {
                                //    "background-color": '#C1DDF1'
                                //},
                                //listener: {
                                //    afterrender: function(field, eOpts){ console.info('id field rendered'); field.setEditable(false);}
                                //}
                            },
                            yaxe1_title: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('title'),
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe1_font_size: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('fontsize'),
                                editor: fontsizesCombo
                            },
                            yaxe1_color: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('color'),
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            yaxe1_min: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('min'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe1_max: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('max'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe1_opposite: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                                type: 'boolean'
                            },
                            yaxe1_unit: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe1_aggregation_type: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                                editor: {
                                    xtype: 'combobox',
                                    store: aggregationTypeStoreYaxe1,
                                    forceSelection: true
                                }
                            },
                            yaxe1_aggregation_min: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                                type: 'number'
                            },
                            yaxe1_aggregation_max: {
                                displayName: 'yAxe 1 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                                type: 'number'
                            },


                            yaxe2_id: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('id'),
                                editor: {}
                            },
                            yaxe2_title: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('title'),
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe2_font_size: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('fontsize'),
                                editor: fontsizesCombo
                            },
                            yaxe2_color: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('color'),
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            yaxe2_min: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('min'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe2_max: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('max'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe2_opposite: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                                type: 'boolean'
                            },
                            yaxe2_unit: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe2_aggregation_type: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                                editor: {
                                    xtype: 'combobox',
                                    store: aggregationTypeStoreYaxe2,
                                    forceSelection: true
                                }
                            },
                            yaxe2_aggregation_min: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                                type: 'number'
                            },
                            yaxe2_aggregation_max: {
                                displayName: 'yAxe 2 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                                type: 'number'
                            },


                            yaxe3_id: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('id'),
                                editor: {}
                            },
                            yaxe3_title: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('title'),
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe3_font_size: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('fontsize'),
                                editor: fontsizesCombo
                            },
                            yaxe3_color: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('color'),
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            yaxe3_min: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('min'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe3_max: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('max'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe3_opposite: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                                type: 'boolean'
                            },
                            yaxe3_unit: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe3_aggregation_type: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                                editor: {
                                    xtype: 'combobox',
                                    store: aggregationTypeStoreYaxe3,
                                    forceSelection: true
                                }
                            },
                            yaxe3_aggregation_min: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                                type: 'number'
                            },
                            yaxe3_aggregation_max: {
                                displayName: 'yAxe 3 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                                type: 'number'
                            },


                            yaxe4_id: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('id'),
                                editor: {}
                            },
                            yaxe4_title: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('title'),
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe4_font_size: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('fontsize'),
                                editor: fontsizesCombo
                            },
                            yaxe4_color: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('color'),
                                editor: {
                                    xtype: 'mycolorselector'    // 'mycolorpicker'
                                }
                                , renderer: crenderer
                            },
                            yaxe4_min: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('min'),
                                //type: 'number',
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe4_max: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('max'),
                                editor: {
                                    xtype: 'numberfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe4_opposite: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('opposite'),   // 'Opposite',
                                type: 'boolean'
                            },
                            yaxe4_unit: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('unit'),   // 'Unit',
                                editor: {
                                    xtype: 'textfield',
                                    selectOnFocus: true
                                }
                            },
                            yaxe4_aggregation_type: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('aggregation_type'),   // 'Aggregation type',
                                editor: {
                                    xtype: 'combobox',
                                    store: aggregationTypeStoreYaxe4,
                                    forceSelection: true
                                }
                            },
                            yaxe4_aggregation_min: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('aggregation_min'),   // 'Aggregation min',
                                type: 'number'
                            },
                            yaxe4_aggregation_max: {
                                displayName: 'yAxe 4 ' + esapp.Utils.getTranslation('aggregation_max'),   // 'Aggregation max',
                                type: 'number'
                            }
                        },

                        listeners: {
                            propertychange: function (source, recordId, value, oldValue, eOpts) {

                                function saveGraphProperty(property, newvalue) {
                                    var user = esapp.getUser();
                                    var extraParams = {
                                        userid: '',
                                        istemplate: false,
                                        graph_tpl_id: -1,
                                        graph_tpl_name: ''
                                    };
                                    var graphpropertiesStore = thiscontroller.getStore('graphproperties');

                                    if (user != 'undefined' && user != null) {
                                        extraParams.userid = user.userid;
                                        extraParams.istemplate = me.isTemplate;
                                        extraParams.graph_tpl_id = me.isTemplate ? me.parent_tpl_id : -1;
                                        extraParams.graph_tpl_name = me.isTemplate ? me.graph_tpl_name : 'default';
                                        graphpropertiesStore.proxy.extraParams = extraParams;

                                        graphpropertiesStore.each(function (graphproperties) {
                                            if (graphproperties.get('graph_type') == me.graphtype) {
                                                if (graphproperties.data.hasOwnProperty(property)) {
                                                    //console.info('Property "' + property + '" exists in record!');
                                                    graphproperties.set(property, newvalue);
                                                }
                                            }
                                        });
                                    }
                                }

                                // function saveYaxeProperty(yaxe) {
                                //     var user = esapp.getUser();
                                //
                                //     if (user != 'undefined' && user != null) {
                                //         yaxe.userid = user.userid;
                                //         yaxe.istemplate = me.isTemplate;
                                //         yaxe.graph_tpl_id = me.isTemplate ? me.parent_tpl_id : -1;
                                //         yaxe.graph_tpl_name = me.isTemplate ? me.graph_tpl_name : 'default';
                                //         yaxe.graphtype = me.graphtype;
                                //
                                //         // Save yaxe changes!
                                //         Ext.Ajax.request({
                                //             url: "analysis/updateyaxe",
                                //             timeout: 300000,
                                //             params: yaxe,
                                //             method: 'POST',
                                //             success: function (result, request) {
                                //                 //console.info(Ext.util.JSON.decode(result.responseText));
                                //             },
                                //             failure: function (result, request) {
                                //             }
                                //         });
                                //     }
                                // }

                                if (value != oldValue) {
                                    var graph_settings_fields = [
                                        'graph_width',
                                        'graph_height',
                                        'graph_title',
                                        'graph_title_font_color',
                                        'graph_title_font_size',
                                        'graph_subtitle',
                                        'graph_subtitle_font_color',
                                        'graph_subtitle_font_size',
                                        'legend_font_size',
                                        'legend_font_color',
                                        'xaxe_font_size',
                                        'xaxe_font_color'
                                    ]

                                    me.graphProperties.localRefresh = true;

                                    if (Ext.Array.contains(graph_settings_fields, recordId)) {
                                        if (recordId == 'graph_width') {
                                            me.graphProperties.width = value;
                                            me.setSize(parseInt(me.graphProperties.width), parseInt(me.graphProperties.height));
                                        }
                                        if (recordId == 'graph_height') {
                                            me.graphProperties.height = value;
                                            me.setSize(parseInt(me.graphProperties.width), parseInt(me.graphProperties.height));
                                        }
                                        if (recordId == 'graph_title') me.graphProperties.title = value;
                                        if (recordId == 'graph_title_font_color') me.graphProperties.graph_title_font_color = value;
                                        if (recordId == 'graph_title_font_size') me.graphProperties.graph_title_font_size = value;

                                        if (recordId == 'graph_subtitle') me.graphProperties.subtitle = value;
                                        if (recordId == 'graph_subtitle_font_color') me.graphProperties.graph_subtitle_font_color = value;
                                        if (recordId == 'graph_subtitle_font_size') me.graphProperties.graph_subtitle_font_size = value;

                                        if (recordId == 'legend_font_size') me.graphProperties.legend_title_font_size = value;
                                        if (recordId == 'legend_font_color') me.graphProperties.legend_title_font_color = value;

                                        if (recordId == 'xaxe_font_size') me.graphProperties.xaxe_font_size = value;
                                        if (recordId == 'xaxe_font_color') me.graphProperties.xaxe_font_color = value;

                                        saveGraphProperty(recordId, value);
                                    }
                                    else {
                                        if (recordId == 'yaxe1_title') {
                                            me.timeseriesGraph.yaxes[0].title = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        // if (recordId == 'yaxe1_font_size')  me.timeseriesGraph.yaxes[0].title_font_size = value;    // from TABLE!
                                        if (recordId == 'yaxe1_font_size') {
                                            me.timeseriesGraph.yaxes[0].title_font_size = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_color') {
                                            me.timeseriesGraph.yaxes[0].title_color = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_min') {
                                            me.timeseriesGraph.yaxes[0].min = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_max') {
                                            me.timeseriesGraph.yaxes[0].max = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_opposite') {
                                            me.timeseriesGraph.yaxes[0].opposite = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_unit') {
                                            me.timeseriesGraph.yaxes[0].unit = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_aggregation_type') {
                                            me.timeseriesGraph.yaxes[0].aggregation_type = value;
                                            me.graphProperties.localRefresh = false;

                                            if (value == 'mean') me.timeseriesGraph.yaxes[0].unit = me.timeseriesGraph.yaxes[0].unit_orig;
                                            if (value == 'count') me.timeseriesGraph.yaxes[0].unit = 'nr';
                                            if (value == 'percent') me.timeseriesGraph.yaxes[0].unit = '%';
                                            if (value == 'cumulate') me.timeseriesGraph.yaxes[0].unit = 'nr';
                                            if (value == 'surface') me.timeseriesGraph.yaxes[0].unit = 'km2';
                                            if (value == 'precip') me.timeseriesGraph.yaxes[0].unit = 'm3';
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_aggregation_min') {
                                            me.timeseriesGraph.yaxes[0].aggregation_min = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }
                                        if (recordId == 'yaxe1_aggregation_max') {
                                            me.timeseriesGraph.yaxes[0].aggregation_max = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[0]);
                                        }


                                        if (recordId == 'yaxe2_title') {
                                            me.timeseriesGraph.yaxes[1].title = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        // if (recordId == 'yaxe2_font_size')  me.timeseriesGraph.yaxes[1].title_font_size;     // from TABLE!
                                        if (recordId == 'yaxe2_font_size') {
                                            me.timeseriesGraph.yaxes[1].title_font_size = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_color') {
                                            me.timeseriesGraph.yaxes[1].title_color = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_min') {
                                            me.timeseriesGraph.yaxes[1].min = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_max') {
                                            me.timeseriesGraph.yaxes[1].max = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_opposite') {
                                            me.timeseriesGraph.yaxes[1].opposite = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_unit') {
                                            me.timeseriesGraph.yaxes[1].unit = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_aggregation_type') {
                                            me.timeseriesGraph.yaxes[1].aggregation_type = value;
                                            me.graphProperties.localRefresh = false;

                                            if (value == 'mean') me.timeseriesGraph.yaxes[1].unit = me.timeseriesGraph.yaxes[1].unit_orig;
                                            if (value == 'count') me.timeseriesGraph.yaxes[1].unit = 'nr';
                                            if (value == 'percent') me.timeseriesGraph.yaxes[1].unit = '%';
                                            if (value == 'cumulate') me.timeseriesGraph.yaxes[1].unit = 'nr';
                                            if (value == 'surface') me.timeseriesGraph.yaxes[1].unit = 'km2';
                                            if (value == 'precip') me.timeseriesGraph.yaxes[1].unit = 'm3';
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_aggregation_min') {
                                            me.timeseriesGraph.yaxes[1].aggregation_min = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }
                                        if (recordId == 'yaxe2_aggregation_max') {
                                            me.timeseriesGraph.yaxes[1].aggregation_max = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[1]);
                                        }


                                        if (recordId == 'yaxe3_title') {
                                            me.timeseriesGraph.yaxes[2].title = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        // if (recordId == 'yaxe3_font_size')  me.timeseriesGraph.yaxes[2].title_font_size;   // from TABLE!
                                        if (recordId == 'yaxe3_font_size') {
                                            me.timeseriesGraph.yaxes[2].title_font_size = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_color') {
                                            me.timeseriesGraph.yaxes[2].title_color = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_min') {
                                            me.timeseriesGraph.yaxes[2].min = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_max') {
                                            me.timeseriesGraph.yaxes[2].max = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_opposite') {
                                            me.timeseriesGraph.yaxes[2].opposite = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_unit') {
                                            me.timeseriesGraph.yaxes[2].unit = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_aggregation_type') {
                                            me.timeseriesGraph.yaxes[2].aggregation_type = value;
                                            me.graphProperties.localRefresh = false;

                                            if (value == 'mean') me.timeseriesGraph.yaxes[2].unit = me.timeseriesGraph.yaxes[2].unit_orig;
                                            if (value == 'count') me.timeseriesGraph.yaxes[2].unit = 'nr';
                                            if (value == 'percent') me.timeseriesGraph.yaxes[2].unit = '%';
                                            if (value == 'cumulate') me.timeseriesGraph.yaxes[2].unit = 'nr';
                                            if (value == 'surface') me.timeseriesGraph.yaxes[2].unit = 'km2';
                                            if (value == 'precip') me.timeseriesGraph.yaxes[2].unit = 'm3';
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_aggregation_min') {
                                            me.timeseriesGraph.yaxes[2].aggregation_min = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }
                                        if (recordId == 'yaxe3_aggregation_max') {
                                            me.timeseriesGraph.yaxes[2].aggregation_max = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[2]);
                                        }

                                        if (recordId == 'yaxe4_title') {
                                            me.timeseriesGraph.yaxes[3].title = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        // if (recordId == 'yaxe4_font_size')  me.timeseriesGraph.yaxes[3].title_font_size;    // from TABLE!
                                        if (recordId == 'yaxe4_font_size') {
                                            me.timeseriesGraph.yaxes[3].title_font_size = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_color') {
                                            me.timeseriesGraph.yaxes[3].title_color = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_min') {
                                            me.timeseriesGraph.yaxes[3].min = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_max') {
                                            me.timeseriesGraph.yaxes[3].max = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_opposite') {
                                            me.timeseriesGraph.yaxes[3].opposite = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_unit') {
                                            me.timeseriesGraph.yaxes[3].unit = value;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_aggregation_type') {
                                            me.timeseriesGraph.yaxes[3].aggregation_type = value;
                                            me.graphProperties.localRefresh = false;

                                            if (value == 'mean') me.timeseriesGraph.yaxes[3].unit = me.timeseriesGraph.yaxes[3].unit_orig;
                                            if (value == 'count') me.timeseriesGraph.yaxes[3].unit = 'nr';
                                            if (value == 'percent') me.timeseriesGraph.yaxes[3].unit = '%';
                                            if (value == 'cumulate') me.timeseriesGraph.yaxes[3].unit = 'nr';
                                            if (value == 'surface') me.timeseriesGraph.yaxes[3].unit = 'km2';
                                            if (value == 'precip') me.timeseriesGraph.yaxes[3].unit = 'm3';
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_aggregation_min') {
                                            me.timeseriesGraph.yaxes[3].aggregation_min = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                        if (recordId == 'yaxe4_aggregation_max') {
                                            me.timeseriesGraph.yaxes[3].aggregation_max = value;
                                            me.graphProperties.localRefresh = false;
                                            // saveYaxeProperty(me.timeseriesGraph.yaxes[3]);
                                        }
                                    }

                                    if (me.graphProperties.localRefresh){
                                        if (me.graphtype == 'ranking') {
                                            me.getController().createRankingChart(me);
                                        }
                                        else if (me.graphtype == 'matrix') {
                                            me.getController().createMatrixChart(me);
                                        }
                                        else {
                                            me.getController().createDefaultChart(me);
                                        }
                                    }
                                    else {
                                        chartDrawPropertiesPanel.hide();
                                        me.getController().refreshChart();
                                    }
                                }
                            },
                            beforeedit: function (editor, e, opts) {
                                //console.info(e.record.get( 'name' ));
                                if (e.record.get('name') == 'yaxe1_id' || e.record.get('name') == 'yaxe2_id' || e.record.get('name') == 'yaxe3_id' || e.record.get('name') == 'yaxe4_id') {
                                    return false;
                                }
                            }
                        }
                    }
                ]
            });

            me.add(chartDrawPropertiesPanel);
        }
        chartDrawPropertiesPanel.show();
        chartDrawPropertiesPanel.doConstrain();
    },

    saveChartAsPNG: function() {

        //function saveImageAs (imgOrURL) {
        //    if (typeof imgOrURL == 'object')
        //      imgOrURL = imgOrURL.src;
        //    window.win = open (imgOrURL);
        //    setTimeout('win.document.execCommand("SaveAs")', 500);
        //}

        function download(data, filename) {
          var a = document.createElement('a');
          a.download = filename;
          a.href = data;
          document.body.appendChild(a);
          a.click();
          a.remove();
        }

        var EXPORT_WIDTH = 1200;
        var me = this.getView();
        var chart = me.tsgraph,
            ObjectToggleBtn = me.lookupReference('objectsbtn_'+me.id.replace(/-/g,'_')),
            disclaimerObj = me.lookupReference('disclaimer_obj_' + me.id),
            logosObj = me.lookupReference('logo_obj_' + me.id),
            disclaimerObjPosition = [],
            logosObjPosition = [];

        if (ObjectToggleBtn.pressed) {
            disclaimerObjPosition = disclaimerObj.getPosition(true);
            logosObjPosition = logosObj.getPosition(true);
        }

        // Get the cart's SVG code          getSVGForLocalExport() if using modules/offline-exporting.js
        var svg = chart.getSVG({
            exporting: {
              sourceWidth: chart.chartWidth,
              sourceHeight: chart.chartHeight
            }
        });

        // var render_width = EXPORT_WIDTH;
        // var render_height = render_width * chart.chartHeight / chart.chartWidth;
        var render_width = chart.chartWidth;
        var render_height = chart.chartHeight;
        // Create a canvas
        var canvas = document.createElement('canvas'),
            context = canvas.getContext('2d');
        canvas.height =  render_height;
        canvas.width = render_width;
        //document.body.appendChild(canvas);

        // Create an image and draw the SVG onto the canvas
        var image = new Image;
        image.onload = function() {
            context.drawImage(this, 0, 0, render_width, render_height);

            if (ObjectToggleBtn.pressed) {
                context.drawImage(disclaimerObj.disclaimer_ImageObj, disclaimerObjPosition[0], disclaimerObjPosition[1]);
                context.drawImage(logosObj.logos_ImageObj, logosObjPosition[0], logosObjPosition[1]);
            }
            var data = canvas.toDataURL("image/png");
            download(data, me.filename + '.png');
        };
        //image.src = 'data:image/svg+xml;base64,' + window.btoa(svg);
        image.src = 'data:image/svg+xml;base64,' + window.btoa(unescape(encodeURIComponent(svg)));


        //console.info(data);
        // data = data.replace(/^data:image\/(png|jpg);base64,/, "");
        //download(data, me.filename + '.png');

        // console.info(image);
        // saveImageAs(image);
    },

    tsDownload: function() {

        var chart = this.getView().tsgraph;
        var type = Highcharts.exporting.MIME_TYPES.XLS;
        chart.exportChartLocal({ type: type, filename: this.getView().filename});
    }

    //,_saveChart: function() {
    //    // FROM : http://willkoehler.net/2014/11/07/client-side-solution-for-downloading-highcharts-charts-as-images.html
    //
    //    function download(canvas, filename) {
    //        download_in_ie(canvas, filename) || download_with_link(canvas, filename);
    //    }
    //
    //    // Works in IE10 and newer
    //    function download_in_ie(canvas, filename) {
    //        return(navigator.msSaveOrOpenBlob && navigator.msSaveOrOpenBlob(canvas.msToBlob(), filename));
    //    }
    //
    //    // Works in Chrome and FF. Safari just opens image in current window, since .download attribute is not supported
    //    function download_with_link(canvas, filename) {
    //        var a = document.createElement('a')
    //        a.download = filename
    //        a.href = canvas.toDataURL("image/png")
    //        document.body.appendChild(a);
    //        a.click();
    //        a.remove();
    //    }
    //
    //    var chart = this.getView().tsgraph;
    //
    //    var render_width = 1000;
    //    var render_height = render_width * chart.chartHeight / chart.chartWidth;
    //
    //    var svg = chart.getSVG({
    //        exporting: {
    //            sourceWidth: chart.chartWidth,
    //            sourceHeight: chart.chartHeight
    //        }
    //    });
    //
    //    var canvas = document.createElement('canvas');
    //    canvas.height = render_height;
    //    canvas.width = render_width;
    //
    //    canvg(canvas, svg, {
    //        scaleWidth: render_width,
    //        scaleHeight: render_height,
    //        ignoreDimensions: true
    //    });
    //
    //    download(canvas, this.getView().filename + '.png');
    //
    //}
});
