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
                var ingestarchives_chkbox = Ext.getCmp('ingest_archives_from_eumetcast');
                //console.info(ingestarchives_chkbox);
                //ingestarchives_chkbox.suspendEvents(false);
                ingestarchives_chkbox.setRawValue(services.ingest_archive_eum);
                //ingestarchives_chkbox.resumeEvents();
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    },


    setIngestArchivesFromEumetcast: function(chkbox, ev){

        // AJAX call to run/start a specified service (specified through the menuitem name).
        Ext.Ajax.request({
            method: 'GET',
            url: 'acquisition/setingestarchives',
            params: {
                setingestarchives: chkbox.value
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                var message = esapp.Utils.getTranslation('turnedoff');     // 'turned off'
                if (chkbox.value) {
                    message = esapp.Utils.getTranslation('turnedon');  // 'turned on'
                }
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('ingest_archives_from_eumetcast') + ' ' + message, title: esapp.Utils.getTranslation('ingest_archives_from_eumetcast'), width: 350, align: 't' });
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }


    ,selectProduct: function(btn, event) {
        var selectProductWin = new esapp.view.acquisition.product.selectProduct();
        // selectProductWin.down('grid').getStore().load();
        selectProductWin.show();
    }

    ,openProductAdmin: function(btn, event) {
        var ProductAdminWin = new esapp.view.acquisition.product.ProductAdmin();
        // selectProductWin.down('grid').getStore().load();
        ProductAdminWin.show();
    }

    ,editProduct: function(grid, rowIndex, row){
        var record = grid.getStore().getAt(rowIndex);
        if (record.get('defined_by') != 'JRC') {
            var editProductWin = new esapp.view.acquisition.product.editProduct({
                params: {
                    edit: true,
                    product: record,
                    orig_productcode: record.get('productcode'),
                    orig_version: record.get('version')
                }
            });
            editProductWin.show();
        }
    }


    //,renderHiddenColumnsWhenUnlocked: function(){
        //var dataacquisitiongrids = Ext.ComponentQuery.query('dataacquisitiongrid');
        //var ingestiongrids = Ext.ComponentQuery.query('ingestiongrid');
        //
        //if (Ext.getCmp('lockunlock').pressed) {
        //    //console.info('unlock status: ' + Ext.getCmp('lockunlock').pressed);
        //
        //    Ext.Object.each(dataacquisitiongrids, function(id, dataacquisitiongrid, myself) {
        //        dataacquisitiongrid.columns[1].show();      // Edit Data Source
        //        //dataacquisitiongrid.columns[1].updateLayout();
        //        dataacquisitiongrid.columns[2].show();      // Store Native
        //        //dataacquisitiongrid.columns[2].updateLayout();
        //        //dataacquisitiongrid.columns[2].show();   // Last executed
        //        //dataacquisitiongrid.columns[3].show();   // Store Native
        //        //dataacquisitiongrid.updateLayout();
        //    });
        //
        //    Ext.Object.each(ingestiongrids, function(id, ingestiongrid, myself) {
        //        ingestiongrid.columns[0].show();    // Add Mapset
        //        //ingestiongrid.columns[0].updateLayout();
        //        ingestiongrid.columns[3].show();    // Delete Mapset
        //        //ingestiongrid.columns[3].updateLayout();
        //        //ingestiongrid.updateLayout();
        //    });
        //}
        //else {
        //    Ext.Object.each(dataacquisitiongrids, function(id, dataacquisitiongrid, myself) {
        //        dataacquisitiongrid.columns[1].hide();  // Edit Data Source
        //        dataacquisitiongrid.columns[2].hide();  // Store Native
        //        //dataacquisitiongrid.columns[3].hide();
        //        //dataacquisitiongrid.updateLayout();
        //    });
        //    Ext.Object.each(ingestiongrids, function(id, ingestiongrid, myself) {
        //        ingestiongrid.columns[0].hide();    // Add Mapset
        //        ingestiongrid.columns[3].hide();    // Delete Mapset
        //        //ingestiongrid.updateLayout();
        //    });
        //}
    //}
    //
    //
    //,onAddClick: function(){
    //
    //    win = Ext.create('esapp.view.acquisition.product.editProduct', {
    //        product : "",
    //        module: true
    //    });
    //
    //    win.show();
    //
    //    if (!win) {
    //        win = Ext.create('esapp.view.acquisition.product.editProduct', {
    //            product : "",
    //            module: true
    //        });
    //    }
    //
    //    if (win.isVisible()) {
    //        win.hide(me, function() {
    //
    //        });
    //    } else {
    //        win.show(me, function() {
    //
    //        });
    //    }
    //
    //    // Create a model instance
    //    var rec = new esapp.model.ProductAcquisition({
    //        productcode: 'newproductcode',
    //        version: 'undefined',
    //        activated: false,
    //        category_id: 'fire',
    //        descriptive_name: false,
    //        order_index:1
    //    });
    //
    //    me.getStore().insert(0, rec);
    //    me.cellEditing.startEditByPosition({
    //        row: 0,
    //        column: 0
    //    });
    //}

});
