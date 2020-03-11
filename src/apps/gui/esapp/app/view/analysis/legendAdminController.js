Ext.define('esapp.view.analysis.legendAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-legendadmin'

    ,onClose: function(win, ev) {
        var me = this.getView();
        if (me.assign){
            var legendsstore  = Ext.data.StoreManager.lookup('LegendsStore');
            var filters = legendsstore.getFilters();

            var selecteddataset = me.productNavigatorObj.lookupReference('mapset-dataset-grid').getSelectionModel().getSelected().items[0];
            me.productNavigatorObj.getController().mapsetDataSetGridRowClick(this, selecteddataset);

            filters.removeAll();
        }
       // Ext.getCmp('analysismain').lookupReference('analysismain_legendsbtn').enable();
    }

    ,loadLegendsStore: function(win, ev) {
        var me = this.getView();
        var legendsgridstore  = Ext.data.StoreManager.lookup('LegendsStore');
        // var legendsgridstore  = me.lookupReference('legendsGrid').getStore('legends');
        //console.info(me.view);
        if (legendsgridstore.isStore) {
            legendsgridstore.load({
                callback: function(response, options, success) {
                    // console.info(response); // for error handling -  capture status code 500 and 400
                    me.lookupReference('legendsGrid').updateLayout();
                    me.updateLayout();
                }
            });
        }
        // me.lookupReference('legendsGrid').updateLayout();
        // me.updateLayout();
    }

    ,copyLegend: function(){
        var me = this.getView();
        var selrec = me.lookupReference('legendsGrid').getSelectionModel().getSelected();
        var legendStore = me.lookupReference('legendsGrid').getStore();

        if (!esapp.Utils.objectExists(selrec)){
            Ext.toast({html: esapp.Utils.getTranslation('nolegend_selected'), title: esapp.Utils.getTranslation('copy_legend'), width: 200, align: 't'});   // 'Copy legend', 'No legend selected!'
        }
        else {
            Ext.Ajax.request({
               url:'legends/copylegend',
               params:{
                   legendid:selrec.items[0].get('legendid'),
                   legend_descriptive_name:selrec.items[0].get('legend_descriptive_name')
               },
               method: 'POST',
               scope:this,
               success: function(result, request) {
                   // The success handler is called if the XHR request actually
                   // made it to the server and a response of some kind occurs.
                   var returnData = Ext.util.JSON.decode(result.responseText);
                   if (returnData.success){
                       //  var defaultData = {
                       //      legendid: returnData.legendid,
                       //      colourscheme: selrec.items[0].get('colorscheme'),
                       //      legendname: selrec.items[0].get('legendname'),
                       //      minvalue: selrec.items[0].get('minvalue'),
                       //      maxvalue: selrec.items[0].get('maxvalue'),
                       //      legend_descriptive_name: returnData.legend_descriptive_name
                       //  };
                       // var newrecord = new esapp.model.Legend(defaultData);
                       // legendStore.add(newrecord);
                       this.loadLegendsStore();

                       Ext.toast({html: esapp.Utils.getTranslation('legend_name')+': <b>'+returnData.legend_descriptive_name+'</b>', title: esapp.Utils.getTranslation('legend_copied'), width: 200, align: 't'});

                   } else if(!returnData.success){
                       esapp.Utils.showError(returnData.message || result.responseText);
                   }
               }, // eo function onSuccess
               failure: function(result, request) {
                   // The failure handler is called if there's some sort of network error,
                   // like you've unplugged your ethernet cable, the server is down, etc.
                   var returnData = Ext.util.JSON.decode(result.responseText);
                   esapp.Utils.showError(returnData.message || result.responseText);
               } // eo function onFailure
            });
        }
    }

    ,importLegend: function(){

    }

    ,exportLegend: function(grid, rowIndex){
        // var selrec = this.getSelectionModel().getSelected();
        var selrec = grid.getStore().getAt(rowIndex);
        console.info(selrec);

        if (!Ext.fly('frmExportDummy')) {
            var frm = document.createElement('form');
            frm.id = 'frmExportDummy';
            frm.name = frm.id;
            frm.className = 'x-hidden';
            document.body.appendChild(frm);
        }
        Ext.Ajax.request({
           url:'legends/exportlegend',
           params:{
               task:'exportLegend',
               legendid:selrec.data.legendid,
               legendname:selrec.data.legend_descriptive_name
           },
           method: 'POST',
           isUpload: true,
           form: Ext.fly('frmExportDummy'),
           scope:this,
           success: function(result, request) {
               // var result = Ext.JSON.decode(response.responseText);
               // if (!result.success){
               //     console.info(response.status);
               // }
           }, // eo function onSuccess
           failure: function(result, request) {
               // console.info(response.status);
           } // eo function onFailure
        });
    }

    ,newLegend: function(){
        var user = esapp.getUser();
        // var me = this.getView();
        // var legendsgridstore  = Ext.data.StoreManager.lookup('LegendsStore');

        var defaultData = {
            legendid: -1,
            colourscheme: null,
            legendname: null,
            minvalue: null,
            maxvalue: null,
            defined_by: (esapp.Utils.objectExists(user) && user.userlevel == 1) ? 'JRC' : 'USER',
            legend_descriptive_name: null
        };
        var newrecord = new esapp.model.Legend(defaultData);

        var newLegendWin = new esapp.view.analysis.addEditLegend({
            params: {
                new: true,
                edit: false,
                view: false,
                legendrecord: newrecord
            }
        });
        newLegendWin.show();
    }

    ,editLegend: function(grid, rowIndex){
        var user = esapp.getUser();
        var record = grid.getStore().getAt(rowIndex);

        // if(!isNaN(record)) {    // record is the rowIndex so get the record from the store through the rowIndex
        //     record = grid.getStore().getAt(rowIndex);
        // }

        var edit = false;
        var view = true;
        if (record.get('defined_by') != 'JRC' || (esapp.Utils.objectExists(user) && user.userlevel == 1)){
            edit = true;
            view = false;
        }

        //if (record.get('defined_by') != 'JRC') {
            var editLegendWin = new esapp.view.analysis.addEditLegend({
                params: {
                    new: false,
                    edit: edit,
                    view: view,
                    legendrecord: record
                }
            });
            editLegendWin.show();
        //}
    }

    ,deleteLegend: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        // if (record.get('deletable')){
            Ext.Msg.show({
                title: esapp.Utils.getTranslation('deletelegendquestion'),     // 'Delete legend definition?',
                message: esapp.Utils.getTranslation('deletelegendquestion') + ' "' + record.get('legend_descriptive_name') + '"?',
                buttons: Ext.Msg.OKCANCEL,
                icon: Ext.Msg.QUESTION,
                fn: function(btn) {
                    if (btn === 'ok') {
                        grid.getStore().remove(record);
                    }
                }
            });
        // }
    }
});
