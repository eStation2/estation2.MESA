Ext.define('esapp.view.analysis.graphTemplateAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-graphtemplateadmin'

    ,openGraphTemplates: function(){
        var me = this.getView();
        var selectedGraphTemplates = me.getSelectionModel().getSelection();
        // var analysisMain = Ext.getCmp('analysismain');
        var workspace = me.owner.up().up();

        for (var i = 0; i < selectedGraphTemplates.length; i++) {
           // console.info(selectedGraphTemplates[i]);

            var graphTemplate = {
                workspace: workspace,
                isTemplate: true,
                isNewTemplate: false,
                workspaceid: selectedGraphTemplates[i].data.workspaceid,
                userid: selectedGraphTemplates[i].data.userid,
                graph_tpl_id: selectedGraphTemplates[i].data.graph_tpl_id,
                parent_tpl_id: selectedGraphTemplates[i].data.parent_tpl_id,
                graph_tpl_name: selectedGraphTemplates[i].data.graph_tpl_name,
                istemplate: selectedGraphTemplates[i].data.istemplate,
                graphviewposition: selectedGraphTemplates[i].data.graphviewposition.split(",").map(function(x){return parseInt(x)}),      // .filter(Boolean)
                graphviewsize: selectedGraphTemplates[i].data.graphviewsize.split(",").map(function(x){return parseInt(x)}),
                graphtype: selectedGraphTemplates[i].data.graph_type,
                selectedTimeseries: selectedGraphTemplates[i].data.selectedtimeseries,
                yearTS: selectedGraphTemplates[i].data.yearts,
                tsFromPeriod: selectedGraphTemplates[i].data.tsfromperiod,
                tsToPeriod: selectedGraphTemplates[i].data.tstoperiod,
                yearsToCompare: selectedGraphTemplates[i].data.yearstocompare != '' ? Ext.decode(selectedGraphTemplates[i].data.yearstocompare) : '',
                tsFromSeason: selectedGraphTemplates[i].data.tsfromseason,
                tsToSeason: selectedGraphTemplates[i].data.tstoseason,
                wkt_geom: selectedGraphTemplates[i].data.wkt_geom,
                selectedregionname: selectedGraphTemplates[i].data.selectedregionname,
                disclaimerObjPosition: selectedGraphTemplates[i].data.disclaimerobjposition != null ? selectedGraphTemplates[i].data.disclaimerobjposition.split(",").map(function(x){return parseInt(x)}) : [0,611],
                disclaimerObjContent: selectedGraphTemplates[i].data.disclaimerobjcontent,
                logosObjPosition: selectedGraphTemplates[i].data.logosobjposition != null ? selectedGraphTemplates[i].data.logosobjposition.split(",").map(function(x){return parseInt(x)}) : [434, 583],
                logosObjContent: selectedGraphTemplates[i].data.logosobjcontent != '' ? Ext.decode(selectedGraphTemplates[i].data.logosobjcontent) : null,
                showObjects: selectedGraphTemplates[i].data.showobjects,
                showtoolbar: selectedGraphTemplates[i].data.showtoolbar,
                auto_open: selectedGraphTemplates[i].data.auto_open
            };
            // console.info(graphTemplate);
            var newGraphViewWin = new esapp.view.analysis.timeseriesChartView(graphTemplate);

            workspace.add(newGraphViewWin);
            newGraphViewWin.show();
        }
    }


    ,deleteGraphTemplate: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        grid.getStore().remove(record);
    }
});
