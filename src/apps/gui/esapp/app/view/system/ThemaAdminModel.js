Ext.define('esapp.view.system.ThemaAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-themaadmin',

    stores: {
        themas: {
            model: 'esapp.model.Themas',
            session: true
        }
    }

});
