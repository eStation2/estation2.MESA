Ext.define('esapp.view.system.PCModeAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.system-pcmodeadmin'

    ,changeMode: function() {
        var me = this,
            newmode = Ext.getCmp('modesradiogroup').getValue();

        Ext.Ajax.request({
            method: 'GET',
            url: 'systemsettings/changemode',
            params: {
                mode: newmode.mode
            },
            success: function(response, opts){
                var result = Ext.JSON.decode(response.responseText);
                if (result.success){
                    Ext.toast({ html: esapp.Utils.getTranslation('systemmodesetto') + " " + newmode.mode,
                                title: esapp.Utils.getTranslation('modechanged'),
                                width: 200, align: 't' });
                }
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
            },
            failure: function(response, opts) {
                console.info(response.status);
            }
        });
    }
});
