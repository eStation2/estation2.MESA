Ext.define('esapp.view.dashboard.DashboardModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.dashboard-dashboard',

    stores: {
        dashboard: {
            model: 'esapp.model.Dashboard',
            session: true
        }
    }
});
