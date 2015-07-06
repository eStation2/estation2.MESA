Ext.define('esapp.view.system.PCLogLevelAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-pclogleveladmin',

    stores: {
        loglevels:{
            fields: ['loglevel'],
            data: [
                {loglevel: 'INFO'},
                {loglevel: 'DEBUG'},
                {loglevel: 'WARNING'},
                {loglevel: 'ERROR'},
                {loglevel: 'FATAL'}
            ]
        }
    }
});
