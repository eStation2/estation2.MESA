Ext.define('esapp.view.system.PCModeAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pcmodeadmin'

    ,changeMode: function() {
        var me = this.getView(),
            permitChangeMode = false,
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

        console.info("current mode:" + currentmode);
        console.info("new mode:" + newmode);
        console.info("other pc mode:" + otherPCMode);

        if (currentmode == 'nominal' && newmode == 'recovery'){

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

        if (currentmode == 'maintenance' && newmode == 'recovery'){

            permitChangeMode = true
        }

        console.info("permit change mode:" + newmode);
        if (permitChangeMode){
            console.info(me.getController());
            me.getController().setMode(newmode)
        }
        else {
            Ext.Msg.alert('Mode can NOT be changed!',
                'Mode can NOT be changed to ' + esapp.Utils.getTranslation(newmode) + ' because the other PC is still reachable and in ' + esapp.Utils.getTranslation(otherPCMode) + ' Mode!');
        }

    },

    setMode: function(newmode) {
        var me = this;

        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changemode',
            params: {
                mode: newmode
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                //console.info(result);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('systemmodesetto') + " " + newmode,
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
