Ext.define('esapp.view.analysis.mapTemplateAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-maptemplateadmin'

    ,openMapTemplates: function(){
        var me = this.getView();
        var selectedMapTemplates = me.getSelectionModel().getSelection();
        var analysisMain = Ext.getCmp('analysismain');

        console.info(me.getSelectionModel().getSelection());
        //console.info(Ext.getCmp('analysismain'));

        //analysisMain.getController().openSelectedMapTemplate(selections);

       for (var i = 0; i < selectedMapTemplates.length; i++) {
            var mapTemplate = {
                isTemplate: true,
                isNewTemplate: false,
                userid: selectedMapTemplates[i].data.userid,
                templatename: selectedMapTemplates[i].data.templatename,
                mapviewPosition: selectedMapTemplates[i].data.mapviewposition.split(",").map(function(x){return parseInt(x)}),      // .filter(Boolean)
                mapviewSize: selectedMapTemplates[i].data.mapviewsize.split(",").map(function(x){return parseInt(x)}),
                productcode: selectedMapTemplates[i].data.productcode,
                subproductcode: selectedMapTemplates[i].data.subproductcode,
                productversion: selectedMapTemplates[i].data.productversion,
                mapsetcode: selectedMapTemplates[i].data.mapsetcode,
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
                //logosObjContent: '',
                showObjects: selectedMapTemplates[i].data.showobjects,
                scalelineObjPosition: selectedMapTemplates[i].data.scalelineobjposition.split(",").map(function(x){return parseInt(x)}),
                vectorLayers: selectedMapTemplates[i].data.vectorlayers,
                outmask: selectedMapTemplates[i].data.outmask,
                outmaskFeature: selectedMapTemplates[i].data.outmaskfeature
            };

            //mapTemplate = {
            //    userid: 'jurvtk',
            //    isTemplate: true,
            //    templatename: '',
            //    mapviewPosition: [10, 5],
            //    mapviewSize: [1000, 900],
            //    productcode: 'vgt-fapar',
            //    subproductcode: 'fapar',
            //    productversion: 'V2.0',
            //    mapsetcode: 'SPOTV-Africa-1km',
            //    legendid: 99,
            //    legendlayout: 'vertical',
            //    legendObjPosition: [5, 210],
            //    showlegend: true,
            //    titleObjPosition: [35, 20],
            //    titleObjContent: '<font size="3" style="color: rgb(0, 0, 0);"><b>{selected_area}</b></font><div><font size="3" style="color: rgb(0, 0, 0);"><b>{product_name}&nbsp;</b></font><div><font size="3"><b>Decade of <font color="#3366ff">{product_date}</font></b></font></div></div>',
            //    disclaimerObjPosition: [330, 695],
            //    disclaimerObjContent: '<font size="1">​Geographical map, WGS 84 - Resolution 5km</font><div><font size="1">Sources: 1) Image NDVI &nbsp;2) Vectors FAO GAUL 2015</font></div>',
            //    logosObjPosition: [585, 677],
            //    logosObjContent: [
            //        { src:'resources/img/logo/MESA_logo.png', width:'65', height:'50' },
            //        { src:'resources/img/logo/AfricanUnion_logo.jpg', width:'65', height:'50' },
            //        { src:'resources/img/logo/logo_en.gif', width:'65', height:'50' }
            //    ],
            //    showObjects: true,
            //    scalelineObjPosition: [0, 710],
            //    vectorLayers: '',
            //    outmask: false,
            //    outmaskFeature: ''
            //}

            //console.info(mapTemplate);
            var newMapViewWin = new esapp.view.analysis.mapView(mapTemplate);

            analysisMain.add(newMapViewWin);
            newMapViewWin.show();
        }

       //me.hide();
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
