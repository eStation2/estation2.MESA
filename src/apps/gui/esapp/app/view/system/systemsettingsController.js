Ext.define('esapp.view.system.systemsettingsController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-systemsettings',

    execServiceTask: function(menuitem, ev) {
        var me = this,
            running = false,
            runner = new Ext.util.TaskRunner();

        var checkstatus = runner.newTask({     //  newTask
            run: function () {
                Ext.Ajax.request({
                    method: 'POST',
                    params: {
                        service: 'ingestarchive',
                        task: 'status'
                    },
                    url: 'systemsettings/ingestarchive',
                    success: function (response, opts) {
                        var result = Ext.JSON.decode(response.responseText);
                        if (result.success) {
                            //console.info(result);
                            if (result.running == 'true') {
                                me.getView().down('button[name=ingestarchivebtn]').setIconCls('fa fa-spin fa-spinner');
                                //me.getView().down('button[name=ingestarchivebtn]').setStyle('color','white');
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=run_ingestarchive]').setDisabled(true);
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=stop_ingestarchive]').setDisabled(false);
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=restart_ingestarchive]').setDisabled(false);
                            } else {
                                me.getView().down('button[name=ingestarchivebtn]').setIconCls('');
                                //me.getView().down('button[name=ingestarchivebtn]').setIconCls('fa fa-spinner');
                                //me.getView().down('button[name=ingestarchivebtn]').setStyle('color','gray');
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=run_ingestarchive]').setDisabled(false);
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=stop_ingestarchive]').setDisabled(true);
                                me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=restart_ingestarchive]').setDisabled(true);
                                checkstatus.stop();     // Stop checking the status when Ingest Archive finished running.
                            }
                            //if (result.running == 'true') {
                            //    Ext.toast({
                            //        html: 'Ingest archive running...',
                            //        title: 'Ingest archive',
                            //        width: 250,
                            //        align: 't'
                            //    });
                            //    btn.setIconCls('fa fa-spin fa-spinner');
                            //}
                            //else {
                            //    btn.setIconCls('');
                            //    task.stop();
                            //    //Ext.util.TaskRunner.destroy(task);
                            //}
                        }
                    },
                    failure: function (response, opts) {
                        console.info(response.status);
                        me.getView().down('button[name=ingestarchivebtn]').setIconCls('');
                        checkstatus.stop();
                    }
                });
            },
            interval:5000 // Check status every 5 seconds.
        });

        // AJAX call to run/start a specified task of the service "ingestarchive" (specified through the menuitem task).
        Ext.Ajax.request({
            method: 'POST',
            url: 'systemsettings/ingestarchive',
            // extraParams: {task: menuitem.name},
            params: {
                service: menuitem.service,
                task: menuitem.task
            },
            success: function (response, opts) {
                var result = Ext.JSON.decode(response.responseText);
                if (result.running == 'true') {
                    running = true;
                    checkstatus.start();
                    me.getView().down('button[name=ingestarchivebtn]').setIconCls('fa fa-spin fa-spinner');
                    //me.getView().down('button[name=ingestarchivebtn]').setStyle('color','white');
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=run_ingestarchive]').setDisabled(true);
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=stop_ingestarchive]').setDisabled(false);
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=restart_ingestarchive]').setDisabled(false);
                } else {
                    me.getView().down('button[name=ingestarchivebtn]').setIconCls('');
                    //me.getView().down('button[name=ingestarchivebtn]').setIconCls('fa fa-spinner');
                    //me.getView().down('button[name=ingestarchivebtn]').setStyle('color','gray');
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=run_ingestarchive]').setDisabled(false);
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=stop_ingestarchive]').setDisabled(true);
                    me.getView().down('button[name=ingestarchivebtn]').down('menuitem[name=restart_ingestarchive]').setDisabled(true);
                }
                if (result.success) {
                    if (menuitem.task == 'restart') {
                        var message = esapp.Utils.getTranslation(menuitem.service) + ' ' + esapp.Utils.getTranslation('restarted');
                        Ext.toast({
                            html: message,
                            title: message,
                            width: 200,
                            align: 't'
                        });
                    }
                }
            },
            failure: function (response, opts) {
                console.info(response.status);
            }
        });

    },

    viewLogFile: function (menuitem) {
        var logViewWin = new esapp.view.acquisition.logviewer.LogView({
            params: {
                logtype: 'service',
                record: menuitem.service
            }
        });
        logViewWin.show();
    }
});
