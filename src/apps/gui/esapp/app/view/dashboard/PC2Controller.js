Ext.define('esapp.view.dashboard.PC2Controller', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.dashboard-pc2',

    checkStatusServices: function(splitbtn, ev){
        // Ext.toast({ html: 'checkStatusServices', title: 'checkStatusServices', width: 200, align: 't' });
        // AJAX call to check the status of all 3 services
        Ext.Ajax.request({
            method: 'POST',
            url: 'services/checkstatusall',
            success: function(response, opts){
                var services = Ext.JSON.decode(response.responseText);
                if (services.eumetcast){
                    splitbtn.up().down('button[name=eumetcastbtn]').setStyle('color','green');
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=runeumetcast]').setDisabled(true);
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=stopeumetcast]').setDisabled(false);
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=restarteumetcast]').setDisabled(false);
                } else {
                    splitbtn.up().down('button[name=eumetcastbtn]').setStyle('color','red');
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=runeumetcast]').setDisabled(false);
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=stopeumetcast]').setDisabled(true);
                    splitbtn.up().down('button[name=eumetcastbtn]').down('menuitem[name=restarteumetcast]').setDisabled(true);
                }
                if (services.internet){
                    splitbtn.up().down('button[name=internetbtn]').setStyle('color','green');
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=runinternet]').setDisabled(true);
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=stopinternet]').setDisabled(false);
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=restartinternet]').setDisabled(false);
                } else {
                    splitbtn.up().down('button[name=internetbtn]').setStyle('color','red');
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=runinternet]').setDisabled(false);
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=stopinternet]').setDisabled(true);
                    splitbtn.up().down('button[name=internetbtn]').down('menuitem[name=restartinternet]').setDisabled(true);
                }
                if (services.ingest){
                    splitbtn.up().down('button[name=ingestbtn]').setStyle('color','green');
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=runingest]').setDisabled(true);
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=stopingest]').setDisabled(false);
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=restartingest]').setDisabled(false);
                } else {
                    splitbtn.up().down('button[name=ingestbtn]').setStyle('color','red');
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=runingest]').setDisabled(false);
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=stopingest]').setDisabled(true);
                    splitbtn.up().down('button[name=ingestbtn]').down('menuitem[name=restartingest]').setDisabled(true);
                }
                if (services.processing){
                    splitbtn.up().down('button[name=processingbtn]').setStyle('color','green');
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(true);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(false);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(false);
                } else {
                    splitbtn.up().down('button[name=processingbtn]').setStyle('color','red');
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=runprocessing]').setDisabled(false);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=stopprocessing]').setDisabled(true);
                    splitbtn.up().down('button[name=processingbtn]').down('menuitem[name=restartprocessing]').setDisabled(true);
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
    //
    //
    //execServiceTask: function(menuitem, ev){
    //    var me = this;
    //
    //    // AJAX call to run/start a specified service (specified through the menuitem name).
    //    // Ext.Ajax.extraParams = {task: menuitem.name};
    //    Ext.Ajax.request({
    //        method: 'POST',
    //        url: 'services/execservicetask',
    //        // extraParams: {task: menuitem.name},
    //        params: {
    //            service: menuitem.service,
    //            task: menuitem.task
    //        },
    //        success: function(response, opts){
    //            var runresult = Ext.JSON.decode(response.responseText);
    //            if (runresult.success){
    //                Ext.toast({ html: 'Execute Service ' + menuitem.service + 'is ' + menuitem.task + 'ed', title: 'Service Task Executed', width: 200, align: 't' });
    //                // menuitem.up().up().fireEvent('click', this);
    //                me.getView().getController('acquisition').checkStatusServices(menuitem.up().up());
    //            }
    //        },
    //        failure: function(response, opts) {
    //            console.info(response.status);
    //        }
    //    });
    //}
    
});
