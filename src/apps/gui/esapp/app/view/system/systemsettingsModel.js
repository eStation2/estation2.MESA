Ext.define('esapp.view.system.systemsettingsModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-systemsettings'

    ,links: {
        system_setting: {
            reference: 'esapp.model.SystemSetting',
//            type: 'SystemSetting',
            id: 0
            ,listeners: {
                update: function () {
                    Ext.Msg.alert('Message', 'System settings updated!');
                }
            }
        }
    }
});
