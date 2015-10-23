Ext.define('esapp.store.SystemSettingsStore', {
     extend  : 'Ext.data.Store'
    ,alias: 'store.systemsettings'

    ,requires : [
        'esapp.model.SystemSetting'
    ]
    ,model: 'esapp.model.SystemSetting'

    ,storeId : 'SystemSettingsStore'

});
