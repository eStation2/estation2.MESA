Ext.define('esapp.view.analysis.mapTemplateAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-maptemplateadmin'

    ,openMapTemplates: function(){
        var me = this.getView();
        var selectedMapTemplates = me.getSelectionModel().getSelection();
        // var analysisMain = Ext.getCmp('analysismain');
        var workspace = me.owner.up().up();

        for (var i = 0; i < selectedMapTemplates.length; i++) {
            var mapTemplate = {
                workspace : me.owner.up().up(),
                isTemplate: true,
                isNewTemplate: false,
                userid: selectedMapTemplates[i].data.userid,
                map_tpl_id: selectedMapTemplates[i].data.map_tpl_id,
                parent_tpl_id: selectedMapTemplates[i].data.parent_tpl_id,
                templatename: selectedMapTemplates[i].data.map_tpl_name,
                mapviewPosition: selectedMapTemplates[i].data.mapviewposition.split(",").map(function(x){return parseInt(x)}),      // .filter(Boolean)
                mapviewSize: selectedMapTemplates[i].data.mapviewsize.split(",").map(function(x){return parseInt(x)}),
                productcode: selectedMapTemplates[i].data.productcode,
                subproductcode: selectedMapTemplates[i].data.subproductcode,
                productversion: selectedMapTemplates[i].data.productversion,
                mapsetcode: selectedMapTemplates[i].data.mapsetcode,
                productdate: selectedMapTemplates[i].data.productdate,
                legendid: selectedMapTemplates[i].data.legendid,
                legendlayout: selectedMapTemplates[i].data.legendlayout,
                legendObjPosition: selectedMapTemplates[i].data.legendobjposition.split(",").map(function(x){return parseInt(x)}),
                showlegend: selectedMapTemplates[i].data.showlegend,
                titleObjPosition: selectedMapTemplates[i].data.titleobjposition.split(",").map(function(x){return parseInt(x)}),
                titleObjContent: selectedMapTemplates[i].data.titleobjcontent,
                disclaimerObjPosition: selectedMapTemplates[i].data.disclaimerobjposition.split(",").map(function(x){return parseInt(x)}),
                disclaimerObjContent: selectedMapTemplates[i].data.disclaimerobjcontent,
                logosObjPosition: selectedMapTemplates[i].data.logosobjposition.split(",").map(function(x){return parseInt(x)}),
                logosObjContent: Ext.decode(selectedMapTemplates[i].data.logosobjcontent),
                showObjects: selectedMapTemplates[i].data.showobjects,
                showtoolbar: selectedMapTemplates[i].data.showtoolbar,
                showgraticule: selectedMapTemplates[i].data.showgraticule,
                showtimeline: selectedMapTemplates[i].data.showtimeline,
                nozoom: false,  // true = Opening a real map template and not a workspace template will not zoom to saved zoomextent
                scalelineObjPosition: selectedMapTemplates[i].data.scalelineobjposition.split(",").map(function(x){return parseInt(x)}),
                vectorLayers: selectedMapTemplates[i].data.vectorlayers,
                outmask: selectedMapTemplates[i].data.outmask,
                outmaskFeature: selectedMapTemplates[i].data.outmaskfeature,
                zoomextent: selectedMapTemplates[i].data.zoomextent,
                mapsize: selectedMapTemplates[i].data.mapsize,
                mapcenter: selectedMapTemplates[i].data.mapcenter
            };

            var newMapViewWin = new esapp.view.analysis.mapView(mapTemplate);

            workspace.add(newMapViewWin);
            newMapViewWin.show();
        }
    }


    ,deleteMapTemplate: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        grid.getStore().remove(record);
        //Ext.Msg.show({
        //    title: esapp.Utils.getTranslation('Delete Map Template?'),     // 'Delete layer definition?',
        //    message: esapp.Utils.getTranslation('Delete Map Template?') + ' "' + record.get('templatename') + '"?',
        //    buttons: Ext.Msg.OKCANCEL,
        //    icon: Ext.Msg.QUESTION,
        //    fn: function(btn) {
        //        if (btn === 'ok') {
        //            grid.getStore().remove(record);
        //        }
        //    }
        //});
    }
});
