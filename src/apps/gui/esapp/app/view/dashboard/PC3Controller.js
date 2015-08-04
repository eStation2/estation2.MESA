Ext.define('esapp.view.dashboard.PC3Controller', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.dashboard-pc3',

    checkStatusServices: function(splitbtn, ev){
        var me = this;
        //console.info('Start checkStatusServices for PC3');

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
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
    
});
