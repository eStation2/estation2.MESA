Ext.define('esapp.view.dashboard.PC2Controller', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.dashboard-pc2',

    viewLogFile: function (menuitem) {
        var logViewWin = new esapp.view.acquisition.logviewer.LogView({
            params: {
                logtype: 'service',
                record: menuitem.service
            }
        });
        logViewWin.show();
    },

    execEnableDisableAutoSync: function(chkbox, ev) {
        var me = this;
        //console.info(chkbox);
        Ext.Ajax.request({
            method: 'POST',
            url: 'dashboard/setdataautosync',
            params:{
                dataautosync: chkbox.checked
            },
            success: function(response, opts){
                var responseText = Ext.JSON.decode(response.responseText);
                // ToDO: Set checkbox text to enable or disable and show a toast message!
//                console.info(responseText);
            },
            failure: function(response, opts) {
//                console.info(response.status);
            }
        });
    },
    execManualDataSync: function(menuitem, ev) {
        var me = this;
        Ext.Ajax.request({
            method: 'POST',
            url: 'dashboard/rundatasync',
            success: function(response, opts){
                var responseText = Ext.JSON.decode(response.responseText);
                // ToDO: Show a toast message with the result of the manual data sync!
//                console.info(responseText);
            },
            failure: function(response, opts) {
//                console.info(response.status);
            }
        });
    },
    execEnableDisableAutoDBSync: function(chkbox, ev) {
        var me = this;
//        console.info(chkbox);
        Ext.Ajax.request({
            method: 'POST',
            url: 'dashboard/setdbautosync',
            params:{
                dbautosync: chkbox.checked
            },
            success: function(response, opts){
                var responseText = Ext.JSON.decode(response.responseText);
                // ToDO: Set checkbox text to enable or disable and show a toast message!
//                console.info(responseText);
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    },
    execManualDBSync: function(menuitem, ev) {
        var me = this;
        Ext.Ajax.request({
            method: 'POST',
            url: 'dashboard/rundbsync',
            success: function(response, opts){
                var responseText = Ext.JSON.decode(response.responseText);
                // ToDO: Show a toast message with the result of the manual DB sync!
//                console.info(responseText);
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    },
    checkStatusServices: function(splitbtn, ev){
        var me = this;
        //console.info('Start checkStatusServices for PC2');

        // Ext.toast({ html: 'checkStatusServices', title: 'checkStatusServices', width: 200, align: 't' });
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
                if (services.processing){
                    me.getView().down('button[name=processingbtn]').setStyle('color','green');
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(true);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(false);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(false);
                } else {
                    me.getView().down('button[name=processingbtn]').setStyle('color','red');
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(false);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(true);
                    me.getView().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(true);
                }
                if (services.system){
                    me.getView().down('button[name=systembtn]').setStyle('color','green');
                    me.getView().down('button[name=systembtn]').down('menuitem[name=runsystem]').setDisabled(true);
                    me.getView().down('button[name=systembtn]').down('menuitem[name=stopsystem]').setDisabled(false);
                    me.getView().down('button[name=systembtn]').down('menuitem[name=restartsystem]').setDisabled(false);
                } else {
                    me.getView().down('button[name=systembtn]').setStyle('color','red');
                    me.getView().down('button[name=systembtn]').down('menuitem[name=runsystem]').setDisabled(false);
                    me.getView().down('button[name=systembtn]').down('menuitem[name=stopsystem]').setDisabled(true);
                    me.getView().down('button[name=systembtn]').down('menuitem[name=restartsystem]').setDisabled(true);
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
    
});
