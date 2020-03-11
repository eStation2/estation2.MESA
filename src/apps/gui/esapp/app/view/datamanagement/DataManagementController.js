Ext.define('esapp.view.datamanagement.DataManagementController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-datamanagement'

    ,showRequestsAdmin: function(btn){
        btn.requestsAdminPanel.show();
    }
});