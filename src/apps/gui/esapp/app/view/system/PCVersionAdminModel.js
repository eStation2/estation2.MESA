Ext.define('esapp.view.system.PCVersionAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.system-pcversionadmin',

    stores: {
        versions: {
            model: 'esapp.model.Versions',
            session: true
        }
    }
});
