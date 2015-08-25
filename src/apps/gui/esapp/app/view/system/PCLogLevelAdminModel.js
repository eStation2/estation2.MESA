Ext.define('esapp.view.system.PCLogLevelAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-pclogleveladmin',

    stores: {
        loglevels:{
            fields: ['loglevel'],
            data: [
                {loglevel: 'DEBUG'},
                {loglevel: 'INFO'},
                {loglevel: 'WARNING'},
                {loglevel: 'ERROR'},
                {loglevel: 'FATAL'}
            ]
        }
    }
});
