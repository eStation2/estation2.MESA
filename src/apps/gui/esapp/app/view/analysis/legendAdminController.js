Ext.define('esapp.view.analysis.legendAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-legendadmin'

    ,onClose: function(win, ev) {
        Ext.getCmp('analysismain').lookupReference('analysismain_legendsbtn').enable();
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

    ,exportLegend: function(){
//         var selrec = this.getSelectionModel().getSelected();
//         if (!objectExists(selrec)){
//             Ext.ux.Toast.msg(EMMA.getTranslation('toast_title_export_legend'), EMMA.getTranslation('toast_text_nolegend_selected') );   // 'Export legend'  'No legend selected!'
//         }
//         else {
//             if (!Ext.fly('frmExportDummy')) {
//                 var frm = document.createElement('form');
//                 frm.id = 'frmExportDummy';
//                 frm.name = id;
//                 frm.className = 'x-hidden';
//                 document.body.appendChild(frm);
//             }
//             Ext.Ajax.request({
//                url:this.url,
//                params:{
//                    task:'exportLegend',
//                    legendid:selrec.data.legend_id,
//                    legendname:selrec.data.legend_name
//                },
//                method: 'POST',
//                form: Ext.fly('frmExportDummy'),
//                waitMsg:EMMA.getTranslation('Msg_wait_exporting_legend'), // 'Exporting legend...',
//                scope:this,
//                success: function(result, request) {
//                    // The success handler is called if the XHR request actually
//                    // made it to the server and a response of some kind occurs.
// //                               var returnData = Ext.util.JSON.decode(result.responseText);
// //                               if (returnData.success){
// //                                   Ext.ux.Toast.msg('Legend exported', 'Legend Exported'+': <b>{0}</b>', returnData.legendname);
// //
// //                               } else if(!returnData.success){
// //                                   this.showError(returnData.error || result.responseText);
// //                               }
//                }, // eo function onSuccess
//                failure: function(result, request) {
//                    // The failure handler is called if there's some sort of network error,
//                    // like you've unplugged your ethernet cable, the server is down, etc.
//                }, // eo function onFailure
//                callback:function(callinfo,responseOK,response ){
//                    //refresh legend list
//                }
//                ,isUpload: true
//             });
//         }
    }

    ,newLegend: function(){
        // var me = this.getView();
        // var legendsgridstore  = Ext.data.StoreManager.lookup('LegendsStore');

        var defaultData = {
            legendid: -1,
            colourscheme: null,
            legendname: null,
            minvalue: null,
            maxvalue: null,
            legend_descriptive_name: null
        };
        var newrecord = new esapp.model.Legend(defaultData);

        var newLegendWin = new esapp.view.analysis.addEditLegend({
            params: {
                edit: false,
                legendrecord: newrecord
            }
        });
        newLegendWin.show();
    }

    ,editLegend: function(grid, record, element, rowIndex, e, eOpts){
        if(!isNaN(record)) {    // record is the rowIndex so get the record from the store through the rowIndex
            record = grid.getStore().getAt(record);
        }
        //if (record.get('defined_by') != 'JRC') {
            var editLegendWin = new esapp.view.analysis.addEditLegend({
                params: {
                    edit: true,
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
