Ext.define('esapp.store.IPSettingsStore', {
     extend  : 'Ext.data.Store'
    ,alias: 'store.ipsettings'

    ,requires : [
        'esapp.model.IPSetting'
    ]
    ,model: 'esapp.model.IPSetting'

    ,storeId : 'IPSettingsStore'

});
