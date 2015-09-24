Ext.define('esapp.view.system.PCModeAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pcmodeadmin'

    ,changeMode: function() {
        var me = this,
            permitChangeMode = false,
            otherPCMode = '',
            newmode = Ext.getCmp('modesradiogroup').getValue(),
            dashboard = Ext.getCmp('dashboard-panel');

        Ext.getCmp('dashboard-panel').getController().setupDashboard();

        if (dashboard.activePC == 'pc2')
            otherPCMode = dashboard.PC3_mode;
        else if (dashboard.activePC == 'pc3'){
            otherPCMode = dashboard.PC2_mode;
        }

        if (me.params.currentmode == 'nominal' && newmode == 'recovery'){

            if (dashboard.PC23_connection) {
                if (otherPCMode == 'nominal') {
                    //Ext.Msg.alert('Mode can NOT be changed!', 'Mode can NOT be changed to Recovery because the other PC is still reachable and in Nominal Mode!');
                    permitChangeMode = false
                }
                if (otherPCMode == 'recovery') {
                    //Ext.Msg.alert('Mode can NOT be changed!', 'Mode can NOT be changed to Recovery because the other PC is still reachable and in Recovery Mode!');
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

        if (me.params.currentmode == 'recovery' && newmode == 'nominal'){

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
                permitChangeMode = false
            }
        }

        if (me.params.currentmode == 'nominal' && newmode == 'maintenance'){

            permitChangeMode = true
        }

        if (me.params.currentmode == 'maintenance' && newmode == 'nominal'){

            if (dashboard.PC23_connection) {
                if (otherPCMode == 'nominal') {
                    permitChangeMode = false
                }
                if (otherPCMode == 'recovery') {
                    permitChangeMode = true
                }
                if (otherPCMode == 'maintenance') {
                    permitChangeMode = false
                }
            }
            else {
                permitChangeMode = false
            }
        }

        if (permitChangeMode){
            me.getController().setMode(newmode)
        }
        else {
            Ext.Msg.alert('Mode can NOT be changed!',
                'Mode can NOT be changed to ' + esapp.Utils.getTranslation(newmode) + ' because the other PC is still reachable and in ' + esapp.Utils.getTranslation(otherPCMode) + ' Mode!');
        }

    },

    setMode: function(newmode) {
        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changemode',
            params: {
                mode: newmode.mode
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                //console.info(result);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('systemmodesetto') + " " + newmode.mode,
                                title: esapp.Utils.getTranslation('modechanged'),
                                width: 200, align: 't' });

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

                            Ext.getCmp('dashboard-panel').getController().setupDashboard();

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
