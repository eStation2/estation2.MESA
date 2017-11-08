Ext.define('esapp.view.analysis.legendAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-legendadmin',

    stores: {
        legends: {
            source:'LegendsStore'
        }
    }
});
