Ext.define('esapp.view.acquisition.AcquisitionController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.acquisition',


    checkStatusServices: function(){
        var me = this;

        // AJAX call to check the status of all 3 services
        Ext.Ajax.request({
            method: 'POST',
            url: 'services/checkstatusall',
            success: function(response, opts){
                var services = Ext.JSON.decode(response.responseText);
                if (services.eumetcast){
                    me.getView().down('button[name=eumetcastbtn]').setStyle('color','green');
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=runeumetcast]').setDisabled(true);
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=stopeumetcast]').setDisabled(false);
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=restarteumetcast]').setDisabled(false);
                } else {
                    me.getView().down('button[name=eumetcastbtn]').setStyle('color','red');
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=runeumetcast]').setDisabled(false);
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=stopeumetcast]').setDisabled(true);
                    me.getView().down('button[name=eumetcastbtn]').down('menuitem[name=restarteumetcast]').setDisabled(true);
                }
                if (services.internet){
                    me.getView().down('button[name=internetbtn]').setStyle('color','green');
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=runinternet]').setDisabled(true);
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=stopinternet]').setDisabled(false);
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=restartinternet]').setDisabled(false);
                } else {
                    me.getView().down('button[name=internetbtn]').setStyle('color','red');
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=runinternet]').setDisabled(false);
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=stopinternet]').setDisabled(true);
                    me.getView().down('button[name=internetbtn]').down('menuitem[name=restartinternet]').setDisabled(true);
                }
                if (services.ingest){
                    me.getView().down('button[name=ingestbtn]').setStyle('color','green');
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=runingest]').setDisabled(true);
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=stopingest]').setDisabled(false);
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=restartingest]').setDisabled(false);
                } else {
                    me.getView().down('button[name=ingestbtn]').setStyle('color','red');
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=runingest]').setDisabled(false);
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=stopingest]').setDisabled(true);
                    me.getView().down('button[name=ingestbtn]').down('menuitem[name=restartingest]').setDisabled(true);
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }


    //execServiceTask: function(menuitem, ev){
    //    var me = me;
    //
    //    // AJAX call to run/start a specified service (specified through the menuitem name).
    //    Ext.Ajax.request({
    //        method: 'POST',
    //        url: 'services/execservicetask',
    //        // extraParams: {task: menuitem.name},
    //        params: {
    //            task: menuitem.name
    //        },
    //        success: function(response, opts){
    //            var runresult = Ext.JSON.decode(response.responseText);
    //            if (runresult.success){
    //                Ext.toast({ html: 'Execute Service Task' + menuitem.name, title: 'Execute Service Task', width: 200, align: 't' });
    //                // menuitem.up().up().fireEvent('click', me);
    //                me.getView().getController('acquisition').checkStatusServices(menuitem.up().up());
    //            }
    //        },
    //        failure: function(response, opts) {
    //            console.info(response.status);
    //        }
    //    });
    //}


    ,selectProduct: function(btn, event) {
        var selectProductWin = new esapp.view.acquisition.product.selectProduct();
        selectProductWin.down().getStore().load();
        selectProductWin.show();
    }


    ,editProduct: function(grid, rowIndex, row){
        var editProductWin = new esapp.view.acquisition.product.editProduct();
        editProductWin.show();

//        win = Ext.create('esapp.view.acquisition.product.editProduct', {
//            product : "",
//            module: true
//        });
//
//        win.show();
//
//        if (!win) {
//            win = Ext.create('esapp.view.acquisition.product.editProduct', {
//                product : "",
//                module: true
//            });
//        }
//
//        if (win.isVisible()) {
//            win.hide(me, function() {
//
//            });
//        } else {
//            win.show(me, function() {
//
//            });
//        }
    }

    ,onAddClick: function(){
        // Create a model instance
        //var rec = new esapp.model.ProductAcquisition({
        //    productcode: 'newproductcode',
        //    version: 'undefined',
        //    activated: false,
        //    category_id: 'fire',
        //    descriptive_name: false,
        //    order_index:1
        //});
        //
        //me.getStore().insert(0, rec);
        //me.cellEditing.startEditByPosition({
        //    row: 0,
        //    column: 0
        //});
    }

});
