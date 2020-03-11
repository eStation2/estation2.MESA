Ext.define('esapp.view.system.PCModeAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pcmodeadmin'

    ,changeMode: function() {
        var me = this.getView(),
            permitChangeMode = false,
            waitForFullSync = false,
            otherPCMode = '',
            currentmode = me.params.currentmode,
            newmode = Ext.getCmp('modesradiogroup').getValue().mode,
            dashboard = Ext.getCmp('dashboard-panel');

        Ext.getCmp('dashboard-panel').getController().setupDashboard();

        if (dashboard.activePC == 'pc2')
            otherPCMode = dashboard.PC3_mode;
        else if (dashboard.activePC == 'pc3'){
            otherPCMode = dashboard.PC2_mode;
        }

        if (currentmode == 'nominal' && newmode == 'recovery'){

            if (dashboard.PC23_connection) {
                if (otherPCMode == 'nominal') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'recovery') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'maintenance') {
                    permitChangeMode = true
                }
            }
            else {
                permitChangeMode = true
            }
        }

        if (currentmode == 'nominal' && newmode == 'maintenance'){

            permitChangeMode = true
        }


        if (currentmode == 'recovery' && newmode == 'nominal'){

            if (dashboard.PC23_connection) {
                if (otherPCMode == 'nominal') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'recovery') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'maintenance') {
                    permitChangeMode = true
                    waitForFullSync = true
                }
            }
            else {
                permitChangeMode = false
            }
        }

        if (currentmode == 'recovery' && newmode == 'maintenance'){

            permitChangeMode = false
        }

        if (currentmode == 'maintenance' && newmode == 'nominal'){

            if (dashboard.PC23_connection) {
                if (otherPCMode == 'nominal') {
                    permitChangeMode = true
                }
                if (otherPCMode == 'recovery') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'maintenance') {
                    permitChangeMode = false
                }
            }
            else {
                permitChangeMode = true
            }
        }

        if (currentmode == 'maintenance' && newmode == 'recovery'){

            permitChangeMode = false
        }

        if (permitChangeMode){
            me.getController().setMode(newmode, waitForFullSync)
        }
        else {
            Ext.Msg.alert('Mode can NOT be changed!',
                'You cannot change to ' + esapp.Utils.getTranslation(newmode) + ' while the other PC is in ' + esapp.Utils.getTranslation(otherPCMode) + '!');
        }

    },

    setMode: function(newmode, waitForFullSync) {
        var me = this;

        if (waitForFullSync){
            var myMask = new Ext.LoadMask({
                msg    : 'Syncing Data and Settings to the other PC. This may take a while, please be patient.',
                target : Ext.getCmp('systemsettingsview')
            });
            me.getView().hide();
            myMask.show();
        }
        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changemode',
            params: {
                mode: newmode
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                //console.info(result);
                if (waitForFullSync) {
                    myMask.hide();
                    me.getView().show();
                }
                if (result.success){
                    Ext.Msg.alert(esapp.Utils.getTranslation('modechanged'), result.message);
                    //Ext.toast({ html: esapp.Utils.getTranslation('systemmodesetto') + " " + newmode,
                    //            title: esapp.Utils.getTranslation('modechanged'),
                    //            width: 200, align: 't' });

                    var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
                    var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                        scope: me,
                        failure: function(record, operation) {
                            //console.info('failure');
                        },
                        success: function(record, operation) {
                            var systemsettingview = Ext.getCmp('systemsettingsview');

                            systemsettingview.loadRecord(systemsettingsrecord);
                            systemsettingview.updateRecord();

                            //Ext.getCmp('dashboard-panel').getController().setupDashboard();

                            me.closeView();
                        }
                    });
                }
                else {
                    Ext.Msg.alert('Mode can NOT be changed!', 'Mode can NOT be changed to Recovery because the other PC is still reachable and in Nominal Mode!');
                    //Ext.toast({ html: "Mode can NOT be changed to Recovery because the other PC is still reachable and in Nominal Mode!",
                    //            title: "Mode NOT changed!",
                    //            width: 200, align: 't' });
                }
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
});
